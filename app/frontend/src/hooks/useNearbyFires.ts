import { useState, useEffect } from 'react';
import { useAuthHeaders } from './useAuthHeaders';
import type { NearbyFire, EnvironmentVariables } from "../types/FirefighterDashboard";

const DEFAULT_LOCATION = { lat: -25.7479, lng: 28.2293 }; // Pretoria

export function useNearbyFires() {
    const headers = useAuthHeaders();
    const [userLocation, setUserLocation] = useState(DEFAULT_LOCATION);
    const [nearbyFires, setNearbyFires] = useState<NearbyFire[]>([]);
    const [environmentVariables, setEnvironmentVariables] = useState<EnvironmentVariables | null>(null);

    useEffect (() => {
        if(!navigator.geolocation){ // if user does not allow location return default location on map
            return;
        }

        //if users location permissions accepted set lat and lng to users location
        navigator.geolocation.getCurrentPosition(
            (position) => {
                setUserLocation({
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                });
            },
            () => {} // keeps default if there is failure retreiving users location
        )
    }, [])

    useEffect(() => {
        const fetchController = new AbortController();
        const fetchRequest = async () => {
            const url = `/api/firefighter/dashboard?lat=${userLocation.lat}&lng=${userLocation.lng}`;
            try{
                const resp = await fetch(url, { headers, signal: fetchController.signal});
                if (!resp.ok){
                    setNearbyFires([]);
                    setEnvironmentVariables(null);
                    return;
                }
                const data = await resp.json();
                setNearbyFires(data.nearby_fires?.data ?? []);
                setEnvironmentVariables(data.environment_variables ?? null);
            } catch(error){
                if(error.name === 'AbortError') return; // this request is superseded by a newer request
                console.error("Was unable to find/retrieve dashboard data", error);
                setNearbyFires([]);
                setEnvironmentVariables(null);
            }
        };
        fetchRequest();
        return () => fetchController.abort(); // this will cancel the fetch if the users location again changes before it is resolved
    }, [userLocation]);
    return { userLocation, nearbyFires, environmentVariables};
}
