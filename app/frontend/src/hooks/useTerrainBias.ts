import { useEffect, useState } from 'react';
import { apiCall } from '../lib/api';
import type { DirectionalBias } from '../lib/fireGrowth';

const cache = new Map<string, DirectionalBias[]>();
const inflight = new Map<string, Promise<DirectionalBias[] | null>>();

function cacheKey(lat: number, lng: number): string {
    return `${lat.toFixed(2)},${lng.toFixed(2)}`;
}

// cached, de-duplicated fetch of real terrain-driven directional bias for one location
export async function fetchTerrainBias(lat: number, lng: number): Promise<DirectionalBias[] | null> {
    const key = cacheKey(lat, lng);
    const cached = cache.get(key);
    if (cached) return cached

    let pending = inflight.get(key);
    if (!pending) {
        pending = (async () => {
            try {
                const data = await apiCall(`/api/firefighter/terrain-bias?lat=${lat}&lng${lng}`);
                return (data?.bias as DirectionalBias[] | undefined) ?? null;
            } catch (err) {
                console.error('Unable to fetch terrain bias for fire growth', err);
                return null;
            }
        })();
        inflight.set(key, pending);
    }

    const result = await pending;
    inflight.delete(key);
    if (result) cache.set(key, result);
    return result;
}

interface BiasTarget {
    id: string;
    lat: number;
    lng: number;
}

// fetches and caches real terrain bias for list of fires, returning a fireId -> bias map that fills
// in as each fetch resolves. Only fetches ids not already resolved in map so growing/shrinking
// fires  list doesn't re-fetch fires already seen
export function useTerrainBiasMap(fires: BiasTarget[], enabled = true): Map<string, DirectionalBias[]> {
    const [biasMap, setBiasMap] = useState<Map<string, DirectionalBias[]>>(new Map());

    useEffect(() => {
        if (!enabled) return;
        const missing = fires.filter((f) => Number.isFinite(f.lat) && Number.isFinite(f.lng) && !biasMap.has(f.id));
        if (missing.length === 0) return;

        let cancelled = false;
        Promise.all(
            missing.map(async (f) => {
                const bias = await fetchTerrainBias(f.lat, f.lng);
                return { id: f.id, bias };
            })
        ).then((results) => {
            if (cancelled) return;
            setBiasMap((prev) => {
                const next = new Map(prev);
                for (const { id, bias } of results) {
                    if (bias) next.set(id, bias);
                }
                return next;
            });
        });

        return () => {
            cancelled = true;
        };
        // fires' id changes each render so key off a stable signature id ids
        // rather than array ref itself.
    }, [fires.map((f) => f.id).join(','), enabled]);

    return biasMap;
}
