import { useEffect, useState } from 'react';
import { apiCall } from '../lib/api';
import type { EnvironmentVariables } from '@/types/FirefighterDashboard';
import type { FireEnvironment } from '@/lib/fireGrowth';

// Weather doesn't need to be refetched as often as the simulation ticks.
// Every couple mins if fine and keeps from hammering Open-Meteo call in firefighter dashboard

const REFRESH_MS = 2 * 60 * 1000;

// round to ~1km so small GPS jitter on a moving device doesn't trigger a refetch
function roundCoord(n: number): number {
    return Math.round(n * 100) / 100;
}

export function useLiveFireEnvironment(lat: number, lng: number, enabled = true): FireEnvironment | null {
    const [env, setEnv] = useState<FireEnvironment | null>(null);
    const roundedLat = Number.isFinite(lat) ? roundCoord(lat) : null;
    const roundedLng = Number.isFinite(lng) ? roundCoord(lng) : null;

    useEffect(() => {
        if (!enabled || roundedLat == null || roundedLng == null) return undefined;
        let cancelled = false;

        const fetchEnv = async () => {
            const [dashboardResult, fuelConditionsResult] = await Promise.allSettled([
                apiCall(`/api/firefighter/dashboard?lat=${roundedLat}&lng=${roundedLng}`),
                apiCall(`/api/firefighter/fuel-conditions?lat=${roundedLat}&lng=${roundedLng}`),
            ]);

            if (cancelled) return;
            
            if (dashboardResult.status === 'rejected') {
                console.error('Unable to fetch live environment for fire growth', dashboardResult.reason);
                return;
            }

            const envVars = dashboardResult.value?.environment_variables as EnvironmentVariables | undefined;
            if (!envVars) return;

            // dryness_grass optional, buildFirePolygon falls back to a cruder
            // temp/humidity estimate when missing so failed/slow
            // fuel-conditions call degrades gracefully rather than blocking growth
            const drynessGrass =
                fuelConditionsResult.status === 'fulfilled' ? fuelConditionsResult.value?.dryness_grass : undefined;
            if (fuelConditionsResult.status === 'rejected') {
                console.error('Unable to fetch fuel conditions for fire growth', fuelConditionsResult.reason);
            }

            setEnv({
                windKph: envVars.wind,
                windDirDeg: envVars.wind_dir,
                temperatureC: envVars.temperature,
                humidityPct: envVars.humidity,
                drynessGrass,
            });
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
