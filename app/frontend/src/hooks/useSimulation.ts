// All API communication and playback state for fire simulation
import { useState, useRef, useCallback, useEffect } from 'react';

export interface Prediction {
    ref: string;
    lat: number;
    lng: number;
    history: number[][];
    burned_cells: number;
    radius_m: number;
    truncated: boolean;
    lat_extent_deg: number;
    lon_extent_deg: number;
    grid_h: number;
    grid_w: number;
    cell_size_m: number;
}

export interface SimulationResult {
    predictions: Prediction[];
    n_steps_run: number;
}

export type SimulationStatus = 'idle' | 'loading' | 'playing' | 'paused' | 'error';


const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
const PLAYBACK_INTERVAL_MS = 300; // ms between ticks during autoplay

// Hook
export function useSimulation() {
  const [status, setStatus] = useState<SimulationStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [currentTick, setCurrentTick] = useState(0); // Tick user is currently viewing (drives map overlay and stats panel)

  const playTimeRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Auto-play ticker
  const stopAutoPlay = useCallback(() => {
    if (playTimeRef.current !== null) {
      clearInterval(playTimeRef.current);
      playTimeRef.current = null;
    }
  }, []);

    const startAutoPlay = useCallback((totalTicks: number) => {
        stopAutoPlay();
        setStatus('playing');

        playTimeRef.current = setInterval(() => {
            setCurrentTick((t) => {
                const next = t + 1;

                if (next >= totalTicks-1) {
                    return totalTicks - 1;
                }
                return next
            });
        }, PLAYBACK_INTERVAL_MS);
        setStatus('playing');
    },
    [stopAutoPlay]
  );

  useEffect(
    () => () => {
      stopAutoPlay();
      abortRef.current?.abort();
    },
    [stopAutoPlay]
  );

    // API call
    const runSimulation = useCallback(
        async (fireId: string | null = null, nSteps = 288) => {
            abortRef.current?.abort();
            const controller = new AbortController();
            abortRef.current = controller;

            setStatus('loading');
            setError(null);
            setCurrentTick(0);
            stopAutoPlay();
            
            try {
                let data: SimulationResult;

                if(fireId) {
                    const resp = await fetch(`${API_BASE}/api/simulate/fire/${fireId}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json'},
                        body: JSON.stringify({n_steps : nSteps}),
                        signal: controller.signal,
                    });

                    if(!resp.ok) {
                        const detail = await resp.text();
                        throw new Error(`Simulation failed ${resp.status}: ${detail}`);
                    }

                    const prediction: Prediction = await resp.json();
                    data = {predictions: [prediction], n_steps_run: prediction.history.length}
                } else{
                    const resp = await fetch(`${API_BASE}/api/simulate`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json' },
                        signal: controller.signal,
                    });
                    
                    if (!resp.ok) {
                      const detail = await resp.text()
                      throw new Error(`Simulation failed ${resp.status}: ${detail}`)
                    }

                    data = await resp.json();
                }

                setResult(data);
                startAutoPlay(data.n_steps_run);
            } catch (err) {
                if (err instanceof Error && err.name === 'AbortError') return;
                const msg = err instanceof Error ? err.message : String(err);
                setError(msg);
                setStatus('error');
            }
        },
        [startAutoPlay, stopAutoPlay]
    );

  const stopRunning = useCallback(() => {
    stopAutoPlay();
    if(abortRef.current){
      abortRef.current.abort();
      abortRef.current = null;
    }
    setStatus((prev) => (prev === 'loading' ? 'idle' : 'paused'));
  }, [stopAutoPlay])

  const clearMap = useCallback(() => {
    stopAutoPlay();
    if(abortRef.current){
      abortRef.current.abort();
    }
    setResult(null);
    setCurrentTick(0);
    setError(null);
    setStatus('idle')
  }, [stopAutoPlay])

  // Playback controls
  const pause = useCallback(() => {
    stopAutoPlay();
    setStatus('paused');
  }, [stopAutoPlay]);

  const play = useCallback(() => {
    if (!result) return;
    if (currentTick >= result.n_steps_run - 1) {
      setCurrentTick(0);
    }
    startAutoPlay(result.n_steps_run);
  }, [result, currentTick, startAutoPlay]);

  const seekToTick = useCallback(
    (tick: number) => {
      if (!result) return;
      const clamped = Math.max(0, Math.min(tick, result.n_steps_run - 1));
      setCurrentTick(clamped);
      // seeking while playing keeps playback running from new position
    },
    [result]
  );

  return {
    status,
    error,
    runSimulation,
    predictions: result?.predictions ?? [],
    currentTick,
    seekToTick,
    play,
    pause,
    stopRunning,
    clearMap,
    totalTicks: result?.n_steps_run ?? 0,
  };
}