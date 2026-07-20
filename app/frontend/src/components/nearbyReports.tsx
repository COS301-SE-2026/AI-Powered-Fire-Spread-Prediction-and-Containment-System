import { useState, useEffect } from 'react';
import { ChevronRight } from "lucide-react";
import { statusBadge } from "./admin/statusBadge";
import type { EnvironmentVariables } from "./firefighter/weatherStats";

export interface NearbyFire{
    readonly ref: string;
    readonly location_text: string;
    readonly distance: number;
    readonly time_ago: string;
    readonly status: string;
}

const DEFAULT_LOCATION = { lat: -25.7479, lng: 28.2293 }; // Pretoria

export function useNearbyFires() {
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
            const url = `/api/firefighter/firefighter-dashboard?lat=${userLocation.lat}&lng=${userLocation.lng}`;
            try{
                const resp = await fetch(url, {signal: fetchController.signal});
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

interface NearbyFireReports{
    readonly nearby_fires: NearbyFire[];
}

export function NearbyReports({nearby_fires}: NearbyFireReports) {
    const fires = nearby_fires ?? [];

    if(fires.length === 0){
        return(
            <div className="h-full flex items-center justify-center p-4">
                <p className="text-xs opacity-50">No nearby fires</p>
            </div>
        )
    }
    return(
        <div className="h-full overflow-y-auto flex flex-col p-2">
        {fires.map((fire) => {
            const status= fire.status === 'received' ? 'pending' : fire.status; 
            const style = statusBadge[status] ?? statusBadge.none;
            return (
                <div key={fire.ref} className="flex items-center justify-between rounded-lg px-3 py-2.5 border border-carbon-stroke hover:border-ignite mb-2 hover:bg-carbon-card/50 cursor-pointer transition-colors">
                    <div>
                        <p className="font-semibold text-sm">{fire.location_text}</p>
                        <p className="text-xs opacity-50">{fire.distance} km · {fire.time_ago}</p>
                    </div>

                    <div className="flex items-center gap-2">
                        <span className={`badge px-3 py-1 rounded-full ${style.bg ?? ''} ${style.text ?? ''} ${style.border ?? ''}`}>
                            {status}
                        </span>
                        <ChevronRight className="size-4 opacity-30" />
                    </div>
            </div>
            )
        })}
        </div>
    );
}