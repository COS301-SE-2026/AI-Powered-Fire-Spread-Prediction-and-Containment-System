"use client";

import React from 'react';
const { default: Map, Marker } = require('react-map-gl/mapbox');

export function FireMap() {
    return (
        <Map
            mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
            initialViewState={{
                longitude: 28.0473,
                latitude: -26.2041,
                zoom: 12
            }}
            style={{ width: '100%', height: '100%' }}
            mapStyle="mapbox://styles/mapbox/navigation-night-v1"
        >
            <Marker longitude={28.0473} latitude={-26.2041} anchor="center">
                <div className="relative flex items-center justify-center size-6">
                    {/* The radar ping animation effect */}
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-ignite opacity-75" />
                    {/* The solid core so the marker remains visible */}
                    <span className="relative inline-flex rounded-full size-3 bg-ignite shadow-lg shadow-black" />
                </div>
            </Marker>
        </Map>
    );
}