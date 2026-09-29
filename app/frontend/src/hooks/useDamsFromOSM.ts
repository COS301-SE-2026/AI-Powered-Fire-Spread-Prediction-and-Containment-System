'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { MapRef } from 'react-map-gl/mapbox';
import type { Feature, FeatureCollection, Geometry } from 'geojson';
import { apiCall } from '../lib/api';

// Used to fill the gaps left by useWaterBodies

interface UseDamsFromOSMOptions {
    minAreaM2?: number;
    minMoveFraction?: number;
}

const EMPTY: FeatureCollection = { type: 'FeatureCollection', features: [] };

export function useDamsFromOSM(
    mapRef: React.RefObject<MapRef | null>,
    { minAreaM2 = 2000, minMoveFraction = 0.3 }: UseDamsFromOSMOptions = {}
) {
    const [osmWater, setOsmWater] = useState<FeatureCollection>(EMPTY);
    const [isLoading, setIsLoading] = useState(false);
    const lastQueriedBounds = useRef<{ minLat: number; minLng: number; maxLat: number; maxLng: number } | null>(null);
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const requestIdRef = useRef(0);

    const maybeFetch = useCallback(async () => {
        const map = mapRef.current?.getMap();
        if (!map) return;

        const bounds = map.getBounds();
        if (!bounds) return;

        const minLat = bounds.getSouth();
        const minLng = bounds.getWest();
        const maxLat = bounds.getNorth();
        const maxLng = bounds.getEast();

        const prev = lastQueriedBounds.current;
        if (prev) {
            const latSpan = maxLat - minLat;
            const lngSpan = maxLng - minLng;
            const moved = 
                Math.abs(minLat - prev.minLat) > latSpan * minMoveFraction ||
                Math.abs(maxLat - prev.maxLat) > latSpan * minMoveFraction ||
                Math.abs(minLng - prev.minLng) > lngSpan * minMoveFraction ||
                Math.abs(maxLng - prev.maxLng) > lngSpan * minMoveFraction;
            if (!moved) return; // still within the area we already fetched, skip round-trip
        }

        const requestId = ++requestIdRef.current;
        setIsLoading(true);
        try {
            const params = new URLSearchParams({
                min_lat: String(minLat),
                min_lng: String(minLng),
                max_lat: String(maxLat),
                max_lng: String(maxLng),
                min_area_m2: String(minAreaM2),
            });
            const data = (await apiCall(`/api/geo/water-bodies?${params.toString()}`)) as FeatureCollection<Geometry> | null;

            if (requestId !== requestIdRef.current) return; // newer request superseded this one

            lastQueriedBounds.current = { minLat, minLng, maxLat, maxLng};
            setOsmWater(data ?? EMPTY);
        } catch (err) {
            // non-fatal. Mapbox's own water layer still renders via useWaterBodies, this is a best-efforst supplement
            console.warn('Failed to fetch OSM water bodies:', err);
        } finally {
            if (requestId === requestIdRef.current) setIsLoading(false);
        }
    }, [mapRef, minAreaM2, minMoveFraction]);

    useEffect(() => {
        const map = mapRef.current?.getMap();
        if (!map) return undefined;

        const scheduleFetch = () => {
            if (debounceRef.current) clearTimeout(debounceRef.current);
            debounceRef.current = setTimeout(maybeFetch, 600);
        };

        map.on('moveend', scheduleFetch);
        scheduleFetch();

        return () => {
            map.off('moveend', scheduleFetch);
            if (debounceRef.current) clearTimeout(debounceRef.current);
        };
    }, [mapRef, maybeFetch]);

    return { osmWaterFeatureCollection: osmWater, isLoading };
}

// Combines Mapbox-detected water polygons with OSM-detected dams/resevoirs, de-duplicating 
// roughly by name so a dam that both sources happen to detect don't get double highlighted.
export function mergeWaterFeatureCollections(
    mapboxWater: FeatureCollection,
    osmWater: FeatureCollection
): FeatureCollection {
    const seenNames = new Set(
        mapboxWater.features
        .map((f:Feature) => (f.properties?.name as string | undefined)?.toLowerCase())
        .filter((n): n is string => Boolean(n))
    );

    const dedupedOsmFeatures = osmWater.features.filter((f: Feature) => {
        const name = (f.properties?.name as string | undefined)?.toLowerCase();
        return !name || !seenNames.has(name);
    });

    return {
        type: 'FeatureCollection',
        features: [...mapboxWater.features, ...dedupedOsmFeatures],
    };
}