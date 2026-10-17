'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { MapRef } from 'react-map-gl/mapbox';
import type { Feature, FeatureCollection, Geometry } from 'geojson';
import { apiCall } from '../lib/api';

// Used to fill the gaps left by useWaterBodies

interface UseDamsFromOSMOptions {
    minAreaM2?: number;
    mapReady?: boolean;
}

const EMPTY: FeatureCollection = { type: 'FeatureCollection', features: [] };
const MAX_HALF_SPAN_DEG = 0.4;
const MIN_HALF_SPAN_DEG = 0.15;
const SNAP_DEG = 0.05;
const snapDown = (v: number) => Math.floor(v / SNAP_DEG) * SNAP_DEG;
const snapUp = (v: number) => Math.ceil(v / SNAP_DEG) * SNAP_DEG;

export function useDamsFromOSM(
    mapRef: React.RefObject<MapRef | null>,
    { minAreaM2 = 2000, mapReady = true}: UseDamsFromOSMOptions = {}
) {
    const [osmWater, setOsmWater] = useState<FeatureCollection>(EMPTY);
    const [isLoading, setIsLoading] = useState(false);
    const lastQueriedBounds = useRef<{ minLat: number; minLng: number; maxLat: number; maxLng: number } | null>(null);
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const requestIdRef = useRef(0);
    const lastSigRef = useRef('');

    const maybeFetch = useCallback(async () => {
        const map = mapRef.current?.getMap();
        if (!map) return;
        if(map.getZoom() < 10) return;

        const bounds = map.getBounds();
        if (!bounds) return;

        const prev = lastQueriedBounds.current;
        if (prev &&
            bounds.getSouth() >= prev.minLat && bounds.getNorth() <= prev.maxLat &&
            bounds.getWest() >= prev.minLng && bounds.getEast() <= prev.maxLng) {
                return; // viewport
        }

        const c = map.getCenter();
        const clampHalf = (span: number) => 
            Math.min(MAX_HALF_SPAN_DEG, Math.max(MIN_HALF_SPAN_DEG, span/2));
        const halfLat = clampHalf(bounds.getNorth() - bounds.getSouth());
        const halfLng = clampHalf(bounds.getEast() - bounds.getWest());
        const minLat = snapDown(c.lat - halfLat);
        const maxLat = snapUp(c.lat + halfLat);
        const minLng = snapDown(c.lng - halfLng);
        const maxLng = snapUp(c.lng + halfLng);

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
            const next = data ?? EMPTY;
            const sig = next.features.map((f) => f.properties?.id).join('|');
            if (sig !== lastSigRef.current) {
                lastSigRef.current = sig;
                setOsmWater(next);
            }
        } catch (err) {
            // non-fatal. Mapbox's own water layer still renders via useWaterBodies, this is a best-efforst supplement
            console.warn('Failed to fetch OSM water bodies:', err);
        } finally {
            if (requestId === requestIdRef.current) setIsLoading(false);
        }
    }, [mapRef, minAreaM2]);

    useEffect(() => {
        if (!mapReady) return undefined;
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
    }, [mapRef, maybeFetch, mapReady]);

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