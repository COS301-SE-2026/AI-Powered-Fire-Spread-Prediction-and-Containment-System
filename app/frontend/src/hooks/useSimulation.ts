// All API communication and playback state for fire simulation
import { useState, useRef, useCallback, useEffect } from 'react';
import { offlineStore, OfflinePredictionOverlay } from '../lib/offlineStore';
import { probeHealth } from '../lib/offline/shared';

export interface WeatherParams {
  wind_u: number;
  wind_v: number;
  rel_humidity: number;
  temperature: number;
}

export interface StaticParams {
  elevation: number;
  slope: number;
  aspect_sin: number;
  aspect_cos: number;
  fuel_load: number;
  dryness: number;
}

export interface DCAParams {
  a: number;
  p_h: number;
  c_1: number;
  c_2: number;
  p_continue: number;
}

export interface SimulationRequest {
  lat: number;
  lng: number;
  fire_id?: string | null;
  grid_h?: number;
  grid_w?: number;
  nSteps?: number;
  n_ignition_points?: number;
  weather?: Partial<WeatherParams>;
  static?: Partial<StaticParams>;
  dca?: Partial<DCAParams>;
}

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
      setResult(null);
      setCurrentTick(0);
      stopAutoPlay();

      const isOnline = await probeHealth(API_BASE);

      if (isOnline) {
        const body: SimulationRequest = {
          lat,
          lng,
          fire_id: fireId,
          grid_h: 30,
          grid_w: 30,
          nSteps,
          n_ignition_points: 1,
          weather,
          static: staticParams,
          dca: dcaParams,
        };

        try {
          const res = await fetch(`${API_BASE}/api/simulate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
            signal: controller.signal,
          });

          if (!res.ok) {
            const detail = await res.text();
            throw new Error(`Server error ${res.status}: ${detail}`);
          }

          const data: SimulationResult = await res.json();
          setResult(data);

          if (autoplay) {
            startAutoPlay(data.n_steps_run);
          } else {
            setStatus('paused');
          }
        } catch (err) {
          if (err instanceof Error && err.name === 'AbortError') return;
          const msg = err instanceof Error ? err.message : String(err);
          setError(msg);
          setStatus('error');
        }
      }

      if (fireId) {
        const cachedOverlay = await offlineStore.getCachedPredictionOverlay(fireId);
        if (cachedOverlay) {
          const fallbackResult: SimulationResult = {
            predictions: [
              {
                ref: fireId,
                lat,
                lng,
                history: [],
                burned_cells: 0,
                radius_m: 200,
              },
            ],
            grid_h: 30,
            grid_w: 30,
            n_steps_run: 1,
          };
          setResult(fallbackResult);
          setStatus('paused');
          return;
        }
      }

      setError('No offline simulation data available for this incident.');
      setStatus('error');
    },
    [weather, staticParams, dcaParams, autoplay, startAutoPlay, stopAutoPlay]
  );

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
