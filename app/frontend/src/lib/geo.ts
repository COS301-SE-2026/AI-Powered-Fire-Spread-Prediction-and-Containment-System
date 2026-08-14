import type { Feature, Polygon } from 'geojson'

export function makeCircle(centerLng: number, centerLat: number, radiusKm: number, steps = 80): Feature<Polygon> {
  const coords: [number, number][] = [];
  
  // degrees = radius_in_km/111.32
  const latRadius = radiusKm / 111.32;
  const lngRadius = radiusKm / (111.32 * Math.cos((centerLat * Math.PI) / 180));
  for (let i = 0; i <= steps; i++) {
    const angle = (i / steps) * 2 * Math.PI;
    coords.push([centerLng + lngRadius * Math.cos(angle), centerLat + latRadius * Math.sin(angle)]);
  }
  return { type: "Feature", properties: {}, geometry: { type: "Polygon", coordinates: [coords] } };
}

export function getRimPos(centerLng: number, centerLat: number, radiusKm: number) {
  const lngRadius = radiusKm / (111.32 * Math.cos((centerLat * Math.PI) / 180));
  return { lng: centerLng + lngRadius, lat: centerLat };
}

// real world distances between lat and lng 
export function realKm(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6371; // earths average radius
  const differenceLat = (lat2 - lat1) * Math.PI / 180;
  const differenceLng = (lng2 - lng1) * Math.PI / 180;
  const a = Math.sin(differenceLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(differenceLng / 2) ** 2;
  return R * 2 * Math.asin(Math.sqrt(a));
}

export function output(km: number): string {
  if (km < 1) {
    return `${Math.round(km * 1000)} m`;
  } 
    return `${km.toFixed(1)} km`;
  
}