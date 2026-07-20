import dynamic from 'next/dynamic';
import React, { useState,useEffect } from 'react';
import { NearbyFire, NearbyReports } from '../../components/users/nearbyReports';
import { SidebarLayout } from '../../components/users/sidebar';
import { PageHeader } from '../../components/pageHeader';
import { MapPanel } from '../../components/users/mapPanel';
import { SidePanelRight } from '../../components/users/sidePanelRight';

const FireMap = dynamic(
    () => import('../../components/reportfire/Firemap').then((mod) => mod.FireMap),
    {
        ssr: false,
        loading: () => (
            <div className="flex-1 flex items-center justify-center bg-carbon-side/20 animate-pulse h-full w-full">
                <span className="text-neutral/40 font-display tracking-widest text-sm uppercase">
                    Initializing Map
                </span>
            </div>
        )
    }
);

export default function RegisteredUserDashboard (){
    const default_location = { lat: -25.7479, lng: 28.2293}; // Pretoria
    const [userLocation, setUserLocation] = useState(default_location);
    const [nearbyFires, setNearbyFires] = useState<NearbyFire[]>([]);

    useEffect (() => {
        if(!navigator.geolocation){ // if user does not allow location return default location on map
            return;
        }
    
        // if users location permissions accepted set lat and lng to users location 
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
                    return;
                }
                const data = await resp.json();
                setNearbyFires(data.nearby_fires?.data ?? []);
            } catch(error){
                if(error.name === 'AbortError') return; // this request is superseded by a newer request
                console.error("Was unable to find/retrieve nearby fires", error);
                setNearbyFires([]);
            }
        };
        fetchRequest();
        return () => fetchController.abort(); // this will cancel the fetch if the users location again changes before it is resolved
    }, [userLocation]);

    return(
        <SidebarLayout>
            <div className="flex flex-col p-6">

                <PageHeader
                    title="Welcome"
                    subtitle="Public Fire Map View"
                />

                <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 xl:grid-rows-1">
                    <MapPanel colSpan={8} height='lg'>
                        <FireMap externalPin={{ lng: userLocation.lng, lat: userLocation.lat }}/>
                    </MapPanel>

                    <SidePanelRight title="Nearby Reports" colSpan={4} maxHeight="calc(480px + 2rem + 197px)">
                        <NearbyReports nearby_fires={nearbyFires}/>
                    </SidePanelRight>
                </div>
            </div>
        </SidebarLayout>
        
    );
   
}