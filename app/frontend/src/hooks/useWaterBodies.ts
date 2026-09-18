'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import area from '@turf/area';
import type { MapRef } from 'react-map-gl/mapbox';
import type {
    Feature,
    FeatureCollection,
    Geometry,
    LineString,
    MultiLineString,
    MultiPolygon,
    Polygon,
} from 'geojson';

export interface WaterBody {
    id: string;
    name?: string;
    areaM2: number;
    areaHa: number;
    geometry: Polygon | MultiPolygon;
}

export interface River {
    id: string;
    name?: string;
    geometry: LineString | MultiLineString;
}

interface UseWaterBodiesOptions {
    minAreaM2?: number;
    riverClasses?: string[];
    sourceId?: string;
}

const EMPTY_POLYGONS: FeatureCollection = { type: 'FeatureCollection', features: [] };
const EMPTY_LINES: FeatureCollection = { type: 'FeatureCollection', features: []};

export function useWaterBodies(
    mapRef: React.RefObject<MapRef | null>,
    {
        minAreaM2 = 20000,
        riverClasses = ['river'],
        sourceId = 'composite',
    } : UseWaterBodiesOptions = {}
) {
    const [waterBodies, setWaterBodies] = useState<WaterBody[]>([]);
    const [rivers, setRivers] = useState<River[]>([]);
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    const detect = useCallback(() => {
        const map = mapRef.current?.getMap();
        if (!map || !map.isStyleLoaded()) return;

        // Large water polygon
        let waterFeatures: Array<Feature<Geometry>> = [];
        try {
            waterFeatures = map.querySourceFeatures(sourceId, {
                sourceLayer: 'water',
            }) as Array<Feature<Geometry>>;
        } catch {

        }

        const seenWater = new Map<string, WaterBody>();
        for (const f of waterFeatures) {
            if (!f.geometry || (f.geometry.type !== 'Polygon' && f.geometry.type !== 'MultiPolygon')){
                continue;
            }
            const a = area(f as Feature<Polygon | MultiPolygon>);
            if (a < minAreaM2) continue;

            const name = (f.properties?.name as string | undefined) ?? undefined;
            const key = `${name ?? 'unnamed'}-${Math.round(a / 5000)}`;
            const existing = seenWater.get(key);
            if (!existing || a > existing.areaM2) {
                seenWater.set(key, {
                    id: key,
                    name,
                    areaM2: a,
                    areaHa: a / 1000,
                    geometry: f.geometry as Polygon | MultiPolygon,
                });
            }
        }

        // Rivers
        let waterwayFeatures: Array<Feature<Geometry>> = [];
        try {
            waterwayFeatures = map.querySourceFeatures(sourceId, {
                sourceLayer: 'waterway',
                filter: ['in', ['get', 'class'], ['literal', riverClasses]],
            }) as Array<Feature<Geometry>>;
        } catch {
            // ignore
        }

        const seenRivers = new Map<string, River>();
        for (const f of waterwayFeatures) {
            if (!f.geometry || (f.geometry.type !== 'LineString' && f.geometry.type !== 'MultiLineString')){
                continue;
            }
            const name = (f.properties?.name as string | undefined) ?? undefined;
            const key = `${name ?? 'unnamed'}-${f.id ?? Math.random()}`;
            seenRivers.set(key, { id: key, name, geometry: f.geometry as LineString | MultiLineString });
        }

        setWaterBodies(Array.from(seenWater.values()));
        setRivers(Array.from(seenRivers.values()));
    }, [mapRef, minAreaM2, riverClasses, sourceId]);

    useEffect(() => {
        const map = mapRef.current?.getMap();
        if (!map) return undefined;

        const scheduleDetect = () => {
            if (debounceRef.current) clearTimeout(debounceRef.current);
            debounceRef.current = setTimeout(detect, 300);
        };

        map.on('idle', scheduleDetect);
        scheduleDetect();

        return () => {
            map.off('idle', scheduleDetect);
            if (debounceRef.current) clearTimeout(debounceRef.current);
        };
    }, [mapRef, detect]);

    const waterFeatureCollection: FeatureCollection = waterBodies.length === 0 ? EMPTY_POLYGONS : {
        type: 'FeatureCollection',
        features: waterBodies.map((wb) => ({
            type: 'Feature',
            properties: {
                id: wb.id,
                name: wb.name ?? null,
                areaHa: Math.round(wb.areaHa * 10) / 10,
            },
            geometry: wb.geometry,
        })),
    };

    const riverFeatureCollection: FeatureCollection = rivers.length === 0 ? EMPTY_LINES : {
        type: 'FeatureCollection',
        features: rivers.map((r) => ({
            type: 'Feature',
            properties: { id: r.id, name: r.name ?? null },
            geometry: r.geometry,
        })),
    };

    return {
        waterBodies,
        rivers,
        waterFeatureCollection,
        riverFeatureCollection,
    };
}