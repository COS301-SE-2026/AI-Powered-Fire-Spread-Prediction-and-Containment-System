// Lightweight, client-side live fire perimeter model.
// Uses all pure maths functions. No GPUs required and not using DCA and ConvLSTM logic

import destination from '@turf/destination';
import { polygon as turfPolygon, featureCollection } from '@turf/helpers';
import union from '@turf/union';
import booleanIntersects from '@turf/boolean-intersects';
import type { Feature, FeatureCollection, MultiPolygon, Polygon } from 'geojson';

export interface FireEnvironment {
    windKph: number;
    windDirDeg: number;
    temperatureC: number;
    humidityPct: number;
    drynessGrass?: number;
}

export interface DirectionalBias {
    bearing_deg: number;
    factor: number;
}

export interface GrowableFire {
    id: string;
    ref: string;
    lat: number;
    lng: number;
    initialRadiusKm: number;    // verified radius (km) at report time. Used as fire's starting size, not current size
    ignitedAtMs: number;    // when fire was first verified in epoch ms
}

const PERIMETER_POINTS = 64;
const BASE_ROS_KM_PER_MIN = 0.0015;
const EASE_IN_MINS = 8;

function hashedSeed(id: string): number {
    let h = 0;
    for (let i = 0; i < id.length; i++) {
        h = (h * 31 + id.charCodeAt(i)) | 0;
    }
    return ((h % 1000) / 1000) * Math.PI * 2;
}

// mirrors wind banding already used server-side in fuel_conditions.py
function windSpeedFactor(windKph: number): number {
    if (windKph <= 5) return 1.0;
    if (windKph <= 15) return 1.1;
    if (windKph <= 25) return 1.25;
    if (windKph <= 40) return 1.4;
    return 1.5;
}

function crudeDryFactor(humidityPct: number, temperatureC: number): number {
    const humidityTerm = Math.max(0, (70 - humidityPct) / 70);
    const tempTerm = Math.max(0, (temperatureC - 15) / 25);
    return 0.4 + 1.2 * Math.min(1, 0.5 * humidityTerm + 0.5 * tempTerm);
}

function drynessFactor(env: FireEnvironment): number {
    if (env.drynessGrass != null) {
        return 0.4 + 1.2 * Math.max(0, Math.min(1, env.drynessGrass));
    }
    return crudeDryFactor(env.humidityPct, env.temperatureC);
}

function lengthToBreadth(windKph: number): number {
    return 1 + (windKph * windKph) / 8500;
}

export function headRateOfSpreadKmPerMin(env: FireEnvironment): number {
    return BASE_ROS_KM_PER_MIN * windSpeedFactor(env.windKph) * drynessFactor(env);
}

function easeIn(elapsedMin: number): number {
    return 1 - Math.exp(-elapsedMin / EASE_IN_MINS);
}

// angularly interpolates nearest two /terrain-bias samples for an arbitrary bearing
function terrainFactorAt(bearingDeg: number, bias: DirectionalBias[] | undefined): number {
    if (!bias || bias.length === 0) return 1;
    const n = bias.length;
    const step = 360 / n;
    const idx = ((bearingDeg / step) % n + n) % n;
    const i0 = Math.floor(idx)
    const i1 = (i0 + 1) % n;
    const t = idx - i0;
    return bias[i0].factor * (1 - t) + bias[i1].factor * t;
}

export function buildFirePolygon(fire: GrowableFire, env: FireEnvironment, nowMs: number, terrainBias?: DirectionalBias[]): Feature<Polygon> {
    const elapsedMin = Math.max(0, (nowMs - fire.ignitedAtMs) / 60000);
    const growth = easeIn(elapsedMin);
    const headROS = headRateOfSpreadKmPerMin(env);
    const headDistKm = fire.initialRadiusKm + headROS * elapsedMin * growth;
    const backDistKm = fire.initialRadiusKm + (headDistKm - fire.initialRadiusKm) * 0.15;

    const lbr = lengthToBreadth(env.windKph);
    const seed = hashedSeed(fire.id);
    const downwindRad = ((env.windDirDeg + 180) * Math.PI / 180);

    const coords: number[][] = [];
    for (let i = 0; i <= PERIMETER_POINTS; i++) {
        const bearingDeg = (360 / PERIMETER_POINTS) * i;
        const bearingRad = (bearingDeg * Math.PI) / 180;

        const downwindness = Math.cos(bearingRad - downwindRad);
        const t = (downwindness + 1) / 2;
        const windShapedRadiusKm = backDistKm + (headDistKm - backDistKm) * Math.pow(t, 1 / Math.max(1, lbr * 0.5));
        const baseRadiusKm = windShapedRadiusKm * terrainFactorAt(bearingDeg, terrainBias);

        const noise =
            1 + 
            0.15 * Math.sin(bearingRad * 3 + seed) +
            0.08 * Math.sin(bearingRad * 7 + seed * 1.7 + elapsedMin * 0.02);

        const radiusKm = Math.max(0.02, baseRadiusKm * noise);
        const point = destination([fire.lng, fire.lat], radiusKm, bearingDeg, { units: 'kilometers'});
        coords.push(point.geometry.coordinates);
    }
    coords.push(coords[0]);

    return turfPolygon([coords], { ref: fire.ref, id: fire.id });
}

export function mergeOverlappingFires(polygons: Feature<Polygon>[]): Feature<Polygon | MultiPolygon>[] {
    const groups: Feature<Polygon>[][] = [];

    for (const poly of polygons) {
        const touchingGroup = groups.find((group) => group.some((p) => booleanIntersects(p, poly)));
        if (touchingGroup) {
            touchingGroup.push(poly);
        } else {
            groups.push([poly]);
        }
    }

    return groups.map((group) => {
        if (group.length === 1) return group[0];
        return group.reduce<Feature<Polygon | MultiPolygon>>((merged, next) => {
            const result = union(featureCollection([merged, next]));
            return (result ?? merged) as Feature<Polygon | MultiPolygon>;
        }, group[0]);
    });
}

export function buildFireFeatureCollection(
    fires: GrowableFire[],
    env: FireEnvironment,
    nowMs: number,
    terrainBiasByFireId?: Map<string, DirectionalBias[]>
): FeatureCollection {
    const polygons = fires.filter((f) => f.initialRadiusKm > 0).map((f) => buildFirePolygon(f, env, nowMs));
    const merged = mergeOverlappingFires(polygons);
    return featureCollection(merged);
}