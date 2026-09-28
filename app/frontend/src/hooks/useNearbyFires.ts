import { useState, useEffect, useMemo } from 'react';
import { apiCall } from '../lib/api';
import type { NearbyFire, EnvironmentVariables } from '../types/FirefighterDashboard';

const DEFAULT_LOCATION = { lat: -25.7479, lng: 28.2293 }; // Pretoria

export function useNearbyFires() {
  const [userLocation, setUserLocation] = useState<{lat: number; lng: number} | null>(null);
  const [locationResolved, setLocationResolved] = useState(false);
  const searchLocation = useMemo(() => userLocation ?? DEFAULT_LOCATION, [userLocation])
  const [nearbyFires, setNearbyFires] = useState<NearbyFire[]>([]);
  const [environmentVariables, setEnvironmentVariables] = useState<EnvironmentVariables | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!navigator.geolocation) {
      setLocationResolved(true);
      return;
    }

    // if users location permissions accepted set lat and lng to users location
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
        setLocationResolved(true);
      },
      () => setLocationResolved(true),
      {timeout: 10000, maximumAge: 60000}
    );
  }, []);

  useEffect(() => {
    if(!locationResolved) return;
    let cancelled = false;
    const fetchRequest = async () => {
      setLoading(true);
      setError(null);

      const url = `/api/firefighter/dashboard?lat=${searchLocation.lat}&lng=${searchLocation.lng}`;
      try {
        const data = await apiCall(url);
        if (cancelled) return;
        setNearbyFires(data.nearby_fires?.data ?? []);
        setEnvironmentVariables(data.environment_variables ?? null);
      } catch (err: unknown) {
        if (cancelled) return;
        console.error('Was unable to find/retrieve dashboard data', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setNearbyFires([]);
        setEnvironmentVariables(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    fetchRequest();
    return () => {
      cancelled = true;
    };
  }, [locationResolved, searchLocation]);
  return { userLocation, searchLocation, nearbyFires, environmentVariables, loading, error };
}
