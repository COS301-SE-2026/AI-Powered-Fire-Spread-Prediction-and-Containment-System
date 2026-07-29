"use client";

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { makeCircle, getRimPos, realKm, output } from '../../lib/geo';
import mapboxgl from 'mapbox-gl';
const { default: Map, Source, Layer } = require('react-map-gl/mapbox');
import 'mapbox-gl/dist/mapbox-gl.css';

interface FireMapProps {
  onLocationSelect?: (loc: { lat: number; lng: number; address: string }) => void;
  onBoundarySizeChange?: (radiusKm: number) => void;
  externalPin?: { lng: number; lat: number } | null;

}

const INITIAL_RADIUS_KM = 0.2;
const INITIAL_ZOOM = 15.5;

  function resetBoundary(
    lng: number,
    lat: number,
    setMarkerPos: (pos: { lng: number; lat: number }) => void,
    setRadius: (r: number) => void,
    onBoundarySizeChange?: (r: number) => void
  ) {
    setMarkerPos({ lng, lat });
    setRadius(INITIAL_RADIUS_KM);
    onBoundarySizeChange?.(INITIAL_RADIUS_KM);
  }
    function toLocation(mapRef: React.RefObject<any>, lng: number, lat: number) {
    mapRef.current?.flyTo({ center: [lng, lat], zoom: INITIAL_ZOOM, duration: 900, essential: true });
  }

  function createPinElement(): HTMLDivElement {
    const el = document.createElement('div');
    el.className = "flex flex-col items-center pointer-events-none";
    el.innerHTML = `
      <div class="w-7 h-7 rounded-full bg-ignite border-2 border-white shadow-lg flex items-center justify-center">
        <div class="w-2.5 h-2.5 rounded-full bg-white"><div/>
      </div>
      <div class="w-1 h-5 bg-ignite/40"></div>
      <div class="w-1 h-1 rounded-full bg-ignite"></div>
    `;
    return el;
  }

  function createRimElement(radiusKm: number): { el: HTMLDivElement; label: HTMLDivElement } {
    const el = document.createElement('div');
    el.className = "flex flex.col items-center gap-1 cursor-grab";

    const label = document.createElement('div');
    label.className = "absolute left-full ml-2 text-white text-xs font-mono whitespace-nowrap pointer-events-none";
    label.textContent = output(radiusKm);

    const btn = document.createElement('div');
    btn.className = "w-8 h-8 rounded-full bg-white border-2 border-ignite text-ignite font-bold text-lg flex items-center justify-center select-none leading-none shadow-lg";
    btn.textContent = "+";

    el.append(label, btn);
    return { el, label };
  }

  function handleRimDrag(
    rimMarker: mapboxgl.Marker,
    label: HTMLDivElement,
    markerPosRef: React.RefObject<{lng: number; lat: number }|null>,
    radiusKmRef: React.MutableRefObject<number>,
    mapRef: React.RefObject<any>,
    onBoundarySizeChange?: (r: number) => void
  ) {
    const pos = markerPosRef.current;
    if (!pos) return;

    const rawLngLat = rimMarker.getLngLat();
    const deltaLng = rawLngLat.lng - pos.lng;
    const deltaLat = rawLngLat.lat - pos.lat;
    const theta = Math.atan2(deltaLat, deltaLng);
    const rawRadius = realKm(pos.lat, pos.lng, rawLngLat.lat, rawLngLat.lng);
    const newRadius = Math.max(0.2, Math.min(rawRadius, 25));
    const latRadius = newRadius / 111.32;
    const lngRadius = newRadius / (111.32 * Math.cos((pos.lat * Math.PI) / 180));
    const lockedLng = pos.lng + lngRadius * Math.cos(theta);
    const lockedLat = pos.lat + latRadius * Math.sin(theta);
    rimMarker.setLngLat([lockedLng, lockedLat]);
    const source = mapRef.current?.getMap()?.getSource('boundary') as mapboxgl.GeoJSONSource | undefined;
    source?.setData(makeCircle(pos.lng, pos.lat, newRadius));
    label.textContent = output(newRadius);
    radiusKmRef.current = newRadius;
    onBoundarySizeChange?.(newRadius);
  }

export function FireMap({ onLocationSelect, onBoundarySizeChange, externalPin }: FireMapProps) {
  const mapRef = useRef<any>(null);
  const [markerPos, setMarkerPos] = useState<{ lng: number; lat: number } | null>(null);
  const [radiusKm, setRadiusKm] = useState(INITIAL_RADIUS_KM);
  const markerPosRef = useRef(markerPos);
  const radiusKmRef = useRef(radiusKm);
  const isDragging = useRef(false);
  const dragEndTime = useRef(0);
  const pinMarkerRef = useRef<mapboxgl.Marker | null>(null);
  const rimMarkerRef = useRef<mapboxgl.Marker | null>(null);

  useEffect(() => { markerPosRef.current = markerPos; }, [markerPos]);
  useEffect(() => { radiusKmRef.current = radiusKm; }, [radiusKm]);

  const setRadius = useCallback((r: number) => {
    setRadiusKm(r);
    radiusKmRef.current = r;
  }, []);

  //pin from search
  useEffect(() => {
    if (!externalPin) return;
    resetBoundary(externalPin.lng, externalPin.lat, setMarkerPos, setRadius, onBoundarySizeChange);
    toLocation(mapRef, externalPin.lng, externalPin.lat);
  }, [externalPin?.lng, externalPin?.lat]);

  useEffect(() => {
    if (!markerPos || !mapRef.current) return;
    pinMarkerRef.current?.remove();

    pinMarkerRef.current = new mapboxgl.Marker({ element: createPinElement(), anchor: 'bottom' })
      .setLngLat([markerPos.lng, markerPos.lat])
      .addTo(mapRef.current.getMap());

    return () => { pinMarkerRef.current?.remove(); };
  }, [markerPos]);

  //rim marker
  useEffect(() => {
    if (!markerPos || !mapRef.current) return;
    rimMarkerRef.current?.remove();

    const rimPos = getRimPos(markerPos.lng, markerPos.lat, radiusKmRef.current);
    const { el, label } = createRimElement(radiusKmRef.current);

    const rimMarker = new mapboxgl.Marker({ element: el, anchor: 'center', draggable: true })
      .setLngLat([rimPos.lng, rimPos.lat])
      .addTo(mapRef.current.getMap());

    rimMarker.on('dragstart', () => { isDragging.current = true; });

    rimMarker.on('drag', () => handleRimDrag(rimMarker, label, markerPosRef, radiusKmRef, mapRef, onBoundarySizeChange));

    rimMarker.on('dragend', () => {
      setRadiusKm(radiusKmRef.current);
      isDragging.current = false;
      dragEndTime.current = Date.now();
    });

    rimMarkerRef.current = rimMarker;
    return () => { rimMarkerRef.current?.remove(); };
  }, [markerPos]);

  async function reverseGeocode(lng: number, lat: number): Promise<string> {
     try {
      const res = await fetch(`https://api.mapbox.com/geocoding/v5/mapbox.places/${lng},${lat}.json?access_token=${process.env.NEXT_PUBLIC_MAPBOX_TOKEN}&types=address,place&limit=1`);
      const json = await res.json();
      return json.features?.[0]?.place_name ?? `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
    } catch {
      return `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
    }
  }

  //map click
  const handleMapClick = useCallback(async (e: any) => {
    if (isDragging.current) return;
    if (Date.now() - dragEndTime.current < 300) return;

    const { lng, lat } = e.lngLat;
    resetBoundary(lng, lat, setMarkerPos, setRadius, onBoundarySizeChange);
    toLocation(mapRef, lng, lat);

    const address = await reverseGeocode(lng, lat);
    onLocationSelect?.({ lat, lng, address });
  }, [onLocationSelect, onBoundarySizeChange]);

  const circleData = markerPos ? makeCircle(markerPos.lng, markerPos.lat, radiusKm) : null;

  return (
    <Map
      ref={mapRef}
      mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
      initialViewState={{ longitude: 28.0473, latitude: -26.2041, zoom: 12 }}
      className="w-full h-full"
      mapStyle="mapbox://styles/mapbox/navigation-night-v1"
      onClick={handleMapClick}
      cursor="crosshair"
    >
      {circleData && (
        <Source id="boundary" type="geojson" data={circleData}>
          <Layer id="boundary-fill" type="fill" paint={{ "fill-color": "#E84500", "fill-opacity": 0.10 }} />
          <Layer id="boundary-stroke" type="line" paint={{ "line-color": "#E84500", "line-width": 2.5, "line-opacity": 0.9 }} />
        </Source>
      )}
    </Map>
  );
}