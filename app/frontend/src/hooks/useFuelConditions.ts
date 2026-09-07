import { useEffect, useState } from "react";
import { apiCall } from '../lib/api';
import { FuelConditions } from "@/types/FuelConditions";

export function useFuelConditions(lat: number| null, lng: number | null) {
    const [conditions, setConditions] = useState<FuelConditions | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if(lat == null || lng == null){
            return;
        }

        let cancelled = false;
        setLoading(true);
        setError(null);

        apiCall(`/api/firefighter/fuel-conditions?lat=${lat.toFixed(3)}&lng=${lng.toFixed(3)}`).then(data => {
            if (cancelled) return;
            setConditions(data);
        }).catch(err => {
            if (cancelled) return;
            console.error('Failed to load fuel conditions', err);
            setError(err instanceof Error ? err.message : 'Unkown error');
            setConditions(null);
        }).finally(() => {
            if (!cancelled) setLoading(false);
        })

        return () => {cancelled = true};
    }, [lat, lng]);

    return { conditions, loading, error };
}
