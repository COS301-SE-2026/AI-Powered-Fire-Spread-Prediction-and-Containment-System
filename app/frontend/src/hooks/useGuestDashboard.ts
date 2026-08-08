import { useState, useEffect } from 'react';
import type { EnvironmentVariables, NearbyFire } from '../types/FirefighterDashboard';

interface GuestReport {
    // fill in with the real shape once you have the backend schema for /api/guests/dashboard
    [key: string]: unknown;
}

const DEFAULT_LOCATION = { lat: -25.7479, lng: 28.2293 };

export function useGuestDashboard(radiusKm = 20) {
    const [location, setLocation] = useState(DEFAULT_LOCATION);
    const [environmentVariables, setEnvironmentVariables] = useState<EnvironmentVariables | null>(null);
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
        const controller = new AbortController();

        const fetchDashboard = async () => {
            setLoading(true);
            setError(null);
            try {
                const resp = await fetch(
                    `/api/guests/dashboard?lat=${location.lat}&lng=${location.lng}&radius_km=${radiusKm}`,
                    { signal: controller.signal }
                );
                if (!resp.ok) throw new Error('Failed to fetch dashboard data');
                const data = await resp.json();
                setEnvironmentVariables(data.environment_variables ?? null);
                setReports(data.nearby_reports ?? []);
            } catch (err) {
                if (err instanceof Error && err.name === 'AbortError') return;
                console.error('Dashboard fetch error', err);
                setError(err instanceof Error ? err.message : 'Unknown error');
            } finally {
                if (!controller.signal.aborted) setLoading(false);
            }
        };

        fetchDashboard();
        return () => controller.abort();
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