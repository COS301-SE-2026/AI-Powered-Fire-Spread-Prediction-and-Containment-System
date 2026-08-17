'use client';

import React, { useState, useEffect, useRef, forwardRef, useImperativeHandle } from 'react';
import { Map, Marker, Popup, Layer, Source, MapRef } from 'react-map-gl/mapbox';
import 'mapbox-gl/dist/mapbox-gl.css';

interface Report {
  id: string;
  lat: number;
  lng: number;
  location_text: string;
  status: string;
  boundary_radius?: number; // will probably change later on
  // future fields
}
export interface GuestMapProps {
  reports: Report[];
  centerLat: number;
  centerLng: number;
  userLocation?: { lat: number; lng: number };
}

export interface GuestMapHandle {
  recenter: (lat: number, lng: number) => void;
}

const GuestMap = forwardRef<GuestMapHandle, GuestMapProps>(
  ({ reports, centerLat, centerLng, userLocation = undefined }, ref) => {
    const [selected, setSelected] = useState<Report | null>(null);
    const [viewport, setViewport] = useState({
      longitude: centerLng,
      latitude: centerLat,
      zoom: 12,
    });
    const mapRef = useRef<MapRef>(null);

    useEffect(() => {
      setViewport((v) => ({ ...v, longitude: centerLng, latitude: centerLat }));
    }, [centerLat, centerLng]);

    useImperativeHandle(ref, () => ({
      recenter: (lat: number, lng: number) => {
        if (mapRef.current) {
          const map = mapRef.current.getMap();
          map.flyTo({ center: [lng, lat], zoom: 14, essential: true });
        }
      },
    }));

    const circleFeatures = reports
      .filter((r) => r.boundary_radius && r.boundary_radius > 0)
      .map((r) => ({
        type: 'Feature' as const,
        geometry: { type: 'Point' as const, coordinates: [r.lng, r.lat] },
        properties: { radius: r.boundary_radius * 1000 },
      }));

    return (
      <Map
        ref={mapRef}
        mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
        {...viewport}
        onMove={(evt) => setViewport(evt.viewState)}
        style={{ width: '100%', height: '100%' }}
        mapStyle="mapbox://styles/mapbox/navigation-night-v1"
      >
        {/* Markers */}
        {reports.map((report) => (
          <Marker
            key={report.id}
            longitude={report.lng}
            latitude={report.lat}
            anchor="center"
            onClick={() => setSelected(report)}
          >
            <div className="relative flex items-center justify-center size-6">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-ignite opacity-75" />
              <span className="relative inline-flex rounded-full size-4 bg-ignite shadow-lg shadow-black" />
            </div>
          </Marker>
        ))}
        {/* Circles around fire markers */}
        {circleFeatures.length >= 0 && (
          <Source
            id="guest-fire-circles"
            type="geojson"
            data={{
              type: 'FeatureCollection' as const,
              features: circleFeatures.map((f) => ({
                ...f,
                properties: {
                  radius_m: f.properties.radius,
                },
              })),
            }}
          >
            <Layer
              id="guest-fire-radius"
              type="circle"
              paint={{
                'circle-color': '#ff4501',
                'circle-opacity': 0.24,
                'circle-stroke-color': '#ff4501',
                'circle-stroke-width': 1.1,
                'circle-radius': [
                  'interpolate',
                  ['linear'],
                  ['zoom'],
                  0,
                  0,
                  8,
                  ['*', ['get', 'radius_m'], 0.05],
                  12,
                  ['*', ['get', 'radius_m'], 0.1],
                  16,
                  ['*', ['get', 'radius_m'], 0.2],
                  20,
                  ['*', ['get', 'radius_m'], 0.5],
                ],
              }}
            />
          </Source>
        )}

        {/* Popup */}
        {selected && (
          <Popup longitude={selected.lng} latitude={selected.lat} onClose={() => setSelected(null)}>
            <div>
              <h3>{selected.location_text}</h3>
              <p>Status: {selected.status}</p>
              {selected.boundary_radius && <p>Radius: {selected.boundary_radius} km</p>}
            </div>
          </Popup>
        )}
      </Map>
    );
  }
);
GuestMap.displayName = 'GuestMap';
GuestMap.defaultProps = {
  userLocation: undefined,
};
export default GuestMap;
