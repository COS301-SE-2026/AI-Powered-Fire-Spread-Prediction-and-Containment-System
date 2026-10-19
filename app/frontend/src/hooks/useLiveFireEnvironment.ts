import { useEffect, useRef, useState } from 'react';
import type { FuelConditions } from '@/types/FuelConditions';
import type { FireEnvironment } from '@/lib/fireGrowth';
import { apiCall } from '../lib/api';

// Weather doesn't need to be refetched as often as the simulation ticks.
// Every couple mins if fine and keeps from hammering Open-Meteo call in firefighter dashboard

const REFRESH_MS = 2 * 60 * 1000;

// calm moderate baseline used only until first real fetch succeeds
const DEFAULT_ENVIRONMENT: FireEnvironment = {
    windKph: 10,
    windDirDeg: 0,
    temperatureC: 20,
    humidityPct: 50,
};

const STALE_WARNING_MS = 15 * 60 * 1000;

// round to ~1km so small GPS jitter on a moving device doesn't trigger a refetch
function roundCoord(n: number): number {
    return Math.round(n * 100) / 100;
}

export function useLiveFireEnvironment(lat: number, lng: number, enabled = true): FireEnvironment | null {
    const [env, setEnv] = useState<FireEnvironment | null>(enabled ? DEFAULT_ENVIRONMENT : null);
    const roundedLat = Number.isFinite(lat) ? roundCoord(lat) : null;
    const roundedLng = Number.isFinite(lng) ? roundCoord(lng) : null;
    const lastSuccessAtRef = useRef<number | null>(null);
    const warnedStaleRef = useRef(false);

    useEffect(() => {
        if (!enabled || roundedLat == null || roundedLng == null) return undefined;
        let cancelled = false;

        const fetchEnv = async () => {
            let fc: FuelConditions | null = null;
            try{
                fc = await apiCall(`/api/firefighter/fuel-conditions?lat=${roundedLat}&lng=${roundedLng}`);
            } catch (err){
                if(cancelled) return;
                console.warn('Unable to fetch live environment for fire growth', err);
                const sinceSuccessMs = lastSuccessAtRef.current == null ? Infinity : Date.now() - lastSuccessAtRef.current;
                if (sinceSuccessMs > STALE_WARNING_MS && !warnedStaleRef.current){
                    warnedStaleRef.current = true;
                    console.warn(`Fire growth has been running on stale/default weather for over ${Math.round(STALE_WARNING_MS / 60000)} minutes.`);
                }
                return;
            }
            if (cancelled || !fc) return;

            lastSuccessAtRef.current = Date.now();
            warnedStaleRef.current = false;

            const next: FireEnvironment = {
                windKph: fc.wind_speed,
                windDirDeg: fc.wind_direction,
                temperatureC: fc.temperature,
                humidityPct: fc.humidity,
                drynessGrass: fc.dryness_grass,
            };

            setEnv((prev) => 
                prev &&
                prev.windKph === next.windKph &&
                prev.windDirDeg === next.windDirDeg &&
                prev.temperatureC === next.temperatureC &&
                prev.humidityPct === next.humidityPct &&
                prev.drynessGrass === next.drynessGrass 
                    ? prev : next
            );
        };
        fetchEnv();
        const id = setInterval(fetchEnv, REFRESH_MS);
        return () => {
            cancelled = true;
            clearInterval(id);
        };
    }, [roundedLat, roundedLng, enabled]);

    return env;
}
