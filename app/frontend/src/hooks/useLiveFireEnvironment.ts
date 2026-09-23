import { useEffect, useState } from 'react';
import { apiCall } from '../lib/api';
import type { EnvironmentVariables } from '@/types/FirefighterDashboard';
import type { FireEnvironment } from '@/lib/fireGrowth';

// Weather doesn't need to be refetched as often as the simulation ticks.
// Every couple mins if fine and keeps from hammering Open-Meteo call in firefighter dashboard

const REFRESH_MS = 2 * 60 * 1000;

function toFireEnvironment(env: EnvironmentVariables): FireEnvironment {
    return {
        windKph: env.wind,
        windDirDeg: env.wind_dir,
        temperatureC: env.temperature,
        humidityPct: env.humidity,
    };
}

// round to ~1km so small GPS jitter on a moving device doesn't trigger a refetch
function roundCoord(n: number): number {
    return Math.round(n * 100) / 100;
}

export function useLiveFireEnvironment(lat: number, lng: number, enabled = true): FireEnvironment | null {
    const [env, setEnv] = useState<FireEnvironment | null>(null);
    const roundedLat = Number.isFinite(lat) ? roundCoord(lat) : null;
    const roundedLng = Number.isFinite(lng) ? roundCoord(lng) : null;

    useEffect(() => {
        if (roundedLat == null || roundedLng == null) return undefined;
        let cancelled = false;

        const fetchEnv = async () => {
            try {
                const data = await apiCall(`/api/firefighter/dashboard?lat=${roundedLat}&lng=${roundedLng}`);
                if (!cancelled && data?.environment_variables) {
                    setEnv(toFireEnvironment(data.environment_variables));
                }
            } catch (err) {
                console.error('Unable to fetch live environment for fire growth', err);
            }
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
