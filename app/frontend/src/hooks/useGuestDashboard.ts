import { useState, useEffect } from 'react';
import type { EnvironmentVariables, NearbyFire } from '../types/FirefighterDashboard';
import { apiCall } from '../lib/api';

const DEFAULT_LOCATION = { lat: -25.7479, lng: 28.2293 };

export function useGuestDashboard(radiusKm = 20) {
  const [location, setLocation] = useState(DEFAULT_LOCATION);
  const [environmentVariables, setEnvironmentVariables] = useState<EnvironmentVariables | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reports, setReports] = useState<NearbyFire[]>([]);

  useEffect(() => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => {}
    );
  }, []);

  useEffect(() => {
    let cancelled = false;

    const fetchDashboard = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiCall(
          `/api/guests/dashboard?lat=${location.lat}&lng=${location.lng}&radius_km=${radiusKm}`
        );
        if (cancelled) return;
        setEnvironmentVariables(data.environment_variables ?? null);
        setReports(data.nearby_reports ?? []);
      } catch (err: unknown) {
        if (cancelled) return;
        console.error('Dashboard fetch error', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchDashboard();
    return () => {
      cancelled = true;
    };
  }, [location, radiusKm]);

  const recenter = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => {}
      );
    } else {
      setLocation({ ...DEFAULT_LOCATION });
    }
  };

  return { location, environmentVariables, reports, loading, error, recenter };
}
