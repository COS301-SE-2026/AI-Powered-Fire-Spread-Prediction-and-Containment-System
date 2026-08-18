// All API communication and playback state for fire simulation

import { useState, useRef, useCallback, useEffect } from 'react';

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
  n_steps?: number;
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

// Defaults
export const DEFAULT_WEATHER: WeatherParams = {
  wind_u: 3.0,
  wind_v: 1.0,
  rel_humidity: 35.0,
  temperature: 28.0,
};

export const DEFAULT_STATIC: StaticParams = {
  elevation: 0,
  slope: 0,
  aspect_sin: 0,
  aspect_cos: 1,
  fuel_load: 0.5,
  dryness: 0.5,
};

export const DEFAULT_DCA: DCAParams = {
  a: 0.1,
  p_h: 0.4,
  c_1: 0.1,
  c_2: 0.1,
  p_continue: 0.6,
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
const PLAYBACK_INTERVAL_MS = 300; // ms between ticks during autoplay

// Hook
export function useSimulation() {
  const [status, setStatus] = useState<SimulationStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SimulationResult | null>(null);

  const [currentTick, setCurrentTick] = useState(0); // Tick user is currently viewing (drives map overlay and stats panel)
  const [autoplay, setAutoPlay] = useState(true);

  // Weather/static/dca params - user can edit via sidebar controls
  const [weather, setWeather] = useState<WeatherParams>(DEFAULT_WEATHER);
  const [staticParams, setStaticParams] = useState<StaticParams>(DEFAULT_STATIC);
  const [dcaParams, setDcaParams] = useState<DCAParams>(DEFAULT_DCA);

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
        async (lat: number, lng: number, n_steps = 288, fireId: string | null = null) => {
            abortRef.current?.abort();
            const controller = new AbortController();  // ← declared here
            abortRef.current = controller;

            setStatus('loading');
            setError(null);
            setResult(null);
            setCurrentTick(0);
            stopAutoPlay();
            
            try {
                let data: SimulationResult;

                if(fireId) {
                    const resp = await fetch(`${API_BASE}/api/simulate/fire/${fireId}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json'},
                        body: JSON.stringify({n_steps, dca: dcaParams}),
                        signal: controller.signal,
                    });

                    if(!resp.ok) {
                        const detail = await resp.text();
                        throw new Error(`INternal server error ${resp.status}: ${detail}`);
                    }

                    const prediction: Prediction = await resp.json();
                    data = {predictions: [prediction], n_steps_run: prediction.history.length}
                } else{
                    const body: SimulationRequest = {
                        lat,
                        lng,
                        fire_id: null,
                        grid_h: 30,
                        grid_w: 30,
                        n_steps,
                        n_ignition_points: 1,
                        weather,
                        static: staticParams,
                        dca: dcaParams,
                    }

                    const res = await fetch(`${API_BASE}/api/simulate`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json' },
                        body: JSON.stringify(body),
                        signal: controller.signal,
                    });

                    data = await res.json();
                }
                setResult(data);

                if(autoplay){
                  startAutoPlay(data.n_steps_run);
                }else{
                  setStatus('paused')
                }
            
            } catch (err) {
                if (err instanceof Error && err.name === 'AbortError') return;
                const msg = err instanceof Error ? err.message : String(err);
                setError(msg);
                setStatus('error');
            }
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

  // Derived data for current tick
  const currentGrids = result
    ? Object.fromEntries(result.predictions.map((p) => [p.ref, p.history[currentTick]]))
    : {};

    return {
        status,
        error,
        runSimulation,
        predictions: result?.predictions ?? [],
        currentTick,
        seekToTick,
        play,
        pause,
        autoplay,
        setAutoPlay,
        totalTicks: result?.n_steps_run ?? 0,
        weather,
        setWeather,
        staticParams,
        setStaticParams,
        dcaParams,
        setDcaParams,
    };
}
