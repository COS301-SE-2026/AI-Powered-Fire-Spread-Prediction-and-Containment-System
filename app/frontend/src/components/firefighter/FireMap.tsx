"use client";

import React, { useEffect, useState } from 'react';
const { default: Map, Marker } = require('react-map-gl/mapbox');

interface FireReport{
    reference_number: string;
    location_text: string;
    status: string
    latitude: number;
    longitude: number;
}

interface MapProps{
    lat: number;
    lng: number;
    drawMode: boolean;
    onDrawComplete: (line: string) => void;
}

export function FireMap({lat, lng, drawMode, onDrawComplete}: MapProps) {
    const [fires, setFires] = useState<FireReport[]>([]);

    useEffect(() => {
        const fetchRequest = async() => {
            const url = `/api/firefighter/reported-fires`

            try{
                const resp = await fetch(url);
                if(!resp.ok){
                    setFires([]);
                    return;
                }
                const data = await resp.json();
                setFires(data.data ?? []);
            }catch(error){
                console.error("failed to find fires", error)
                setFires([]);
            }
        };
        fetchRequest();
    }, [])

    return (
        <Map
            mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
            initialViewState={{
                longitude: lng,
                latitude: lat,
                zoom: 12
            }}
            style={{ width: '100%', height: '100%' }}
            mapStyle="mapbox://styles/mapbox/navigation-night-v1"
        >
            {fires.map((fire) => (
                <Marker key={fire.reference_number} longitude={fire.longitude} latitude={fire.latitude} anchor="center">
                    <div className="relative flex items-center justify-center size-6">
                        {/* The radar ping animation effect */}
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-ignite opacity-75" />
                        {/* The solid core so the marker remains visible */}
                        <span className="relative inline-flex rounded-full size-3 bg-ignite shadow-lg shadow-black" />
                    </div>
                </Marker>
            ))}
            
        </Map>
    );
}