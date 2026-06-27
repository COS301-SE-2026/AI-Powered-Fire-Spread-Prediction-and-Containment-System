"use client";

import React from 'react';
const { default: FireMap } = require('react-map-gl/mapbox');

interface ReportMapProps {
    readonly lat: number;
    readonly lng: number;
}

export function ReportMap({ lat, lng }: ReportMapProps) {
    return (
        <div className="flex flex-col gap-2">   
            <h2>Fire Report Location</h2>  
            <div className="relative rounded-xl overflow-hidden h-64"> 
                <FireMap
                    mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
                    initialViewState={{ longitude: lng, latitude: lat, zoom: 13 }}
                    style={{ width: '100%', height: '100%' }}
                    mapStyle="mapbox://styles/mapbox/navigation-night-v1"
                />
                {/*replace with mapboxgl.Marker when connecting backend */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="relative flex items-center justify-center size-6">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-ignite opacity-75" />
                        <span className="relative inline-flex rounded-full size-3 bg-ignite shadow-lg shadow-black" />
                    </div>
                </div>
            </div>
        </div>
    );
}