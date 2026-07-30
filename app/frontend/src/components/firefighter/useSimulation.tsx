// All API communication and playback state for fire simulation

import { useState, useRef, useCallback, useEffect } from "react";
import { SimulationResults } from "./simulationResult"

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
    grid_h?: number;
    grid_w?: number;
    n_steps?: number;
    n_ignition_points?: number;
    weather?: Partial<WeatherParams>;
    static?: Partial<StaticParams>;
    dca?: Partial<DCAParams>;
}

export interface TickStats {
    tick: number;
    burning: number;
    burned: number;
    total_cells: number;
}

export interface SimulationResult {
    history: number[][];    //[tick][H*W] flat burn-state arrays
    grid_h: number;
    grid_w: number;
    tick_stats: TickStats[];
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

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const PLAYBACK_INTERVAL_MS = 300; // ms between ticks during autoplay

// Hook
export function useSimulation() {
    const [status, setStatus] = useState<SimulationStatus>('idle');
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<SimulationResult | null>(null);

    const [currentTick, setCurrentTick] = useState(0);  // Tick user is currently viewing (drives map overlay and stats panel)
    const [autoplay, setAutoPlay] = useState(true);

    // Weather/static/dca params - user can edit via sidebar controls
    const [weather, setWeather] = useState<WeatherParams>(DEFAULT_WEATHER);
    const [staticParams, setStaticParams] = useState<StaticParams>(DEFAULT_STATIC);
    const [dcaParams, setDcaParams] = useState<DCAParams>(DEFAULT_DCA);

    const playTimeRef = useRef<ReturnType<typeof setInterval> | null>(null);

    // Auto-play ticker
    const stopAutoPlay = useCallback(() => {
        if (playTimeRef.current !== null) {
            clearInterval(playTimeRef.current);
            playTimeRef.current = null;
        }
    }, []);

    const startAutoPlay = useCallback((totalTicks: number) => {
        stopAutoPlay();
        playTimeRef.current = setInterval(() => {
            setCurrentTick((t) => {
                if (t >= totalTicks-1) {
                    return t;
                }
                return t+1;
            });
            const next = totalTicks + 1;
    
        }, PLAYBACK_INTERVAL_MS);
        setStatus('playing');
    },
    [stopAutoPlay]
    );

    useEffect(() => () => stopAutoPlay(), [stopAutoPlay]);

    // API call
    const runSimulation = useCallback(
        async (lat: number, lng: number, n_steps = 48) => {
            setStatus('loading');
            setError(null);
            setResult(null);
            setCurrentTick(0);
            stopAutoPlay();

            const body: SimulationRequest = {
                lat,
                lng,
                grid_h: 30,
                grid_w: 30,
                n_steps,
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
                const msg = err instanceof Error ? err.message : String(err);
                setError(msg);
                setStatus('error');
            }
        },
        [weather, staticParams, dcaParams, autoplay, startAutoPlay, startAutoPlay]
    );

    // Playback controls
    const pause = useCallback(() => {
        stopAutoPlay();
        setStatus('paused');
    }, [stopAutoPlay, status, result, stopAutoPlay]);

    const play = useCallback(() => {
        if (!result) return;
        if (currentTick >= result.n_steps_run-1) {
            setCurrentTick(0);
        }
        startAutoPlay(result.n_steps_run);
    }, [result, currentTick, startAutoPlay]);

    const seekToTick = useCallback((tick: number) => {
        if (!result) return;
        const clamped = Math.max(0, Math.min(tick, result.n_steps_run-1));
        setCurrentTick(clamped);
        // seeking while playing keeps playback running from new position
    },
    [result]
    );

    // Derived data for current tick
    const currentGrid = result ? result.history[currentTick] : null;
    const currentStats = result ? result.tick_stats[currentTick] : null;

    return {
        status,
        error,
        runSimulation,
        currentTick,
        seekToTick,
        play,
        pause,
        autoplay,
        setAutoPlay,
        totalTicks: result?.n_steps_run ?? 0,
        currentGrid,
        currentStats,
        gridH: result?.grid_h ?? 30,
        gridW: result?.grid_w ?? 30,
        allStats: result?.tick_stats ?? [],
        weather, 
        setWeather,
        staticParams,
        setStaticParams,
        dcaParams,
        setDcaParams,
    };
}
