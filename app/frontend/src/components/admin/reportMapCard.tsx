'use client';

import React, { useEffect, useState, useRef, useMemo, useCallback } from 'react';
import Map, { Marker } from 'react-map-gl/mapbox';
import 'mapbox-gl/dist/mapbox-gl.css';

interface ReportMapProps {
  readonly lat: number;
  readonly lng: number;
}

export function ReportMap({ lat, lng }: ReportMapProps) {
  const [showUserLocationTooltip, setShowUserLocationTooltip] = useState(false);
  return (
    <div className="flex flex-col gap-2 h-full">
      <h2>Fire Report Location</h2>
      <div className="relative rounded-xl overflow-hidden flex-1 min-h-100">
        <Map
          mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
          initialViewState={{ longitude: lng, latitude: lat, zoom: 13 }}
          style={{ width: '100%', height: '100%' }}
          mapStyle="mapbox://styles/mapbox/navigation-night-v1"
        >
          {lat != null && lng != null && (
            <Marker
              longitude={lng}
              latitude={lat}
              anchor="center"
              onClick={(e) => {
                e.originalEvent.stopPropagation();
                setShowUserLocationTooltip((prev) => !prev);
              }}
            >
              <div
                role="button"
                tabIndex={0}
                aria-label="Your location marker"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    setShowUserLocationTooltip((prev) => !prev);
                  }
                }}
                className='relative flex items-center justify-center w-11 h-11 cursor-pointer focus:outline-none'
              >
                {/*Click to show badge*/}
                {showUserLocationTooltip && (
                  <div className='absolute -top-7 left-1/2 -translate-x-1/2 flex items-center px-2 py-0.5 rounded bg-carbon-side/95
                  border border-carbon-stroke text-[11px] font-medium text-text-primary whitespace-nowrap shadow-lg z-20 pointer-events-none'>
                    Your location
                  </div>
                )}

                {/*pulse for marker*/}
                <span
                  className='animate-ping absolute inline-flex w-5 h-5 rounded-full opacity-75 pointer-events-none'
                  style={{ backgroundColor: 'var(--color-wind, #378add)' }}
                />

                {/*solid marker dot*/}
                <span
                  className='relative inline-flex rounded-full size-3 border-2 border-white shadow-md shadow-black pointer-events-none'
                  style={{ backgroundColor: 'var(--color-wind, #378add)' }}
                />
              </div>
            </Marker>
          )}
        </Map>
      </div>
    </div>
  );
}
