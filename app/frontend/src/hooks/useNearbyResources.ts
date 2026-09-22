import { useState, useEffect } from 'react';
// import { apiCall } from '../lib/api';
import { mockResources } from '../mockData/Resources';
import type { ResourceTable } from '../types/Resource';

export interface NearbyResource extends ResourceTable {
    distance: number;
}

function distance(lat1: number, lng1: number, lat2: number, lng2: number) {
    const lat = (lat2 -lat1)* 111.32;  // 111.32 km pr degree
    const lng = (lng2 - lng1)* 111.32 * Math.cos((lat1 * Math.PI)/180);
    return Math.hypot(lat, lng);
}

export function useNearbyResources(userLocation: { lat: number, lng: number }, radiusKm?: number) {
  const [nearbyResources, setNearbyResources] = useState<NearbyResource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const fetchRequest = async () => {
      setLoading(true);
      setError(null);

      try {
            // const data = await apiCall(url);
            // if (cancelled) return;
            // setNearbyResources(data.resources?.data ?? []);

            // MOCK: delete this block when backend is live
            const data: ResourceTable[] = mockResources;
            if (cancelled) return;
            setNearbyResources( data.map((r) => ({ ...r, distance: distance( userLocation.lat, userLocation.lng, r.externalPin.lat, r.externalPin.lng ),})).filter((r) => radiusKm == null || r.distance <= radiusKm).sort((a, b) => a.distance - b.distance));
      } catch (err: unknown) {
        if (cancelled) return;
        console.error('Was unable to find/retrieve dashboard data', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setNearbyResources([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    fetchRequest();
    return () => {
      cancelled = true;
    };
  }, [userLocation, radiusKm]);
  return { nearbyResources, loading, error };
}
