"use client";

import React, { useCallback, useEffect, useRef, useState } from 'react';
import type { Feature, Polygon } from 'geojson';
import mapboxgl from 'mapbox-gl';
const { default: Map, Source, Layer } = require('react-map-gl/mapbox');
import 'mapbox-gl/dist/mapbox-gl.css';

interface FireMapProps {
  onLocationSelect?: (loc: { lat: number; lng: number; address: string }) => void;
  onBoundarySizeChange?: (radiusKm: number) => void;
  /** When set, the map flies here and drops a pin (from form search) */
  externalPin?: { lng: number; lat: number } | null;
}

function makeCircle(centerLng: number, centerLat: number, radiusKm: number, steps = 80): Feature<Polygon> {
  const coords: [number, number][] = [];
  const latRadius = radiusKm / 111;
  const lngRadius = radiusKm / (111 * Math.cos((centerLat * Math.PI) / 180));
  for (let i = 0; i <= steps; i++) {
    const angle = (i / steps) * 2 * Math.PI;
    coords.push([centerLng + lngRadius * Math.cos(angle), centerLat + latRadius * Math.sin(angle)]);
  }
  return { type: "Feature", properties: {}, geometry: { type: "Polygon", coordinates: [coords] } };
}

function getRimHandlePos(centerLng: number, centerLat: number, radiusKm: number) {
  const lngRadius = radiusKm / (111 * Math.cos((centerLat * Math.PI) / 180));
  return { lng: centerLng + lngRadius, lat: centerLat };
}

function haversineKm(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.asin(Math.sqrt(a));
}

function formatRadius(km: number): string {
  return km < 1 ? `${Math.round(km * 1000)} m` : `${km.toFixed(1)} km`;
}

const INITIAL_RADIUS_KM = 0.2;
const INITIAL_ZOOM = 15.5;

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

  // ── EXTERNAL PIN (from form search) ──────────────────────────
  useEffect(() => {
    if (!externalPin) return;
    const { lng, lat } = externalPin;
    setMarkerPos({ lng, lat });
    setRadiusKm(INITIAL_RADIUS_KM);
    radiusKmRef.current = INITIAL_RADIUS_KM;
    onBoundarySizeChange?.(INITIAL_RADIUS_KM);
    mapRef.current?.flyTo({ center: [lng, lat], zoom: INITIAL_ZOOM, duration: 900, essential: true });
  }, [externalPin]);

  // ── PIN MARKER ────────────────────────────────────────────────
  useEffect(() => {
    if (!markerPos || !mapRef.current) return;
    pinMarkerRef.current?.remove();

    const el = document.createElement('div');
    el.style.cssText = 'display:flex;flex-direction:column;align-items:center;pointer-events:none;';
    el.innerHTML = `
      <div style="width:28px;height:28px;border-radius:50%;background:#E84500;border:3px solid white;box-shadow:0 0 20px rgba(232,69,0,0.9);display:flex;align-items:center;justify-content:center;">
        <div style="width:10px;height:10px;border-radius:50%;background:white;"></div>
      </div>
      <div style="width:3px;height:20px;background:linear-gradient(to bottom,#E84500 60%,transparent);"></div>
      <div style="width:5px;height:5px;border-radius:50%;background:#E84500;"></div>
    `;

    pinMarkerRef.current = new mapboxgl.Marker({ element: el, anchor: 'bottom' })
      .setLngLat([markerPos.lng, markerPos.lat])
      .addTo(mapRef.current.getMap());

    return () => { pinMarkerRef.current?.remove(); };
  }, [markerPos]);

  // ── RIM HANDLE MARKER ─────────────────────────────────────────
  useEffect(() => {
    if (!markerPos || !mapRef.current) return;
    rimMarkerRef.current?.remove();

    const rimPos = getRimHandlePos(markerPos.lng, markerPos.lat, radiusKmRef.current);
    const el = document.createElement('div');
    el.style.cssText = 'display:flex;flex-direction:column;align-items:center;gap:4px;cursor:grab;';

    const label = document.createElement('div');
    label.style.cssText = 'padding:3px 10px;border-radius:999px;background:rgba(0,0,0,0.85);border:1px solid rgba(232,69,0,0.5);color:#fff;font-size:11px;font-family:monospace;white-space:nowrap;pointer-events:none;margin-bottom:4px;';
    label.textContent = formatRadius(radiusKmRef.current);

    const btn = document.createElement('div');
    btn.style.cssText = 'width:40px;height:40px;border-radius:50%;background:rgba(10,10,10,0.9);border:2.5px solid #E84500;color:#E84500;font-size:26px;font-weight:700;display:flex;align-items:center;justify-content:center;box-shadow:0 0 16px rgba(232,69,0,0.6);user-select:none;line-height:1;';
    btn.textContent = '+';

    el.appendChild(label);
    el.appendChild(btn);

    const rimMarker = new mapboxgl.Marker({ element: el, anchor: 'center', draggable: true })
      .setLngLat([rimPos.lng, rimPos.lat])
      .addTo(mapRef.current.getMap());

    rimMarker.on('dragstart', () => { isDragging.current = true; });

    rimMarker.on('drag', () => {
      const pos = markerPosRef.current;
      if (!pos) return;
      const rawLngLat = rimMarker.getLngLat();
      const deltaLng = rawLngLat.lng - pos.lng;
      const deltaLat = rawLngLat.lat - pos.lat;
      const theta = Math.atan2(deltaLat, deltaLng);
      const rawRadius = haversineKm(pos.lat, pos.lng, rawLngLat.lat, rawLngLat.lng);
      const newRadius = Math.max(0.2, Math.min(rawRadius, 25));
      const latRadius = newRadius / 111;
      const lngRadius = newRadius / (111 * Math.cos((pos.lat * Math.PI) / 180));
      const lockedLng = pos.lng + lngRadius * Math.cos(theta);
      const lockedLat = pos.lat + latRadius * Math.sin(theta);
      rimMarker.setLngLat([lockedLng, lockedLat]);
      const source = mapRef.current?.getMap()?.getSource('boundary') as mapboxgl.GeoJSONSource | undefined;
      source?.setData(makeCircle(pos.lng, pos.lat, newRadius));
      label.textContent = formatRadius(newRadius);
      radiusKmRef.current = newRadius;
      onBoundarySizeChange?.(newRadius);
    });

    rimMarker.on('dragend', () => {
      setRadiusKm(radiusKmRef.current);
      isDragging.current = false;
      dragEndTime.current = Date.now();
    });

    rimMarkerRef.current = rimMarker;
    return () => { rimMarkerRef.current?.remove(); };
  }, [markerPos]);

  // ── MAP CLICK ─────────────────────────────────────────────────
  const handleMapClick = useCallback(async (e: any) => {
    if (isDragging.current) return;
    if (Date.now() - dragEndTime.current < 300) return;

    const { lng, lat } = e.lngLat;
    setMarkerPos({ lng, lat });
    setRadiusKm(INITIAL_RADIUS_KM);
    radiusKmRef.current = INITIAL_RADIUS_KM;
    onBoundarySizeChange?.(INITIAL_RADIUS_KM);
    mapRef.current?.flyTo({ center: [lng, lat], zoom: INITIAL_ZOOM, duration: 900, essential: true });

    try {
      const res = await fetch(
        `https://api.mapbox.com/geocoding/v5/mapbox.places/${lng},${lat}.json` +
        `?access_token=${process.env.NEXT_PUBLIC_MAPBOX_TOKEN}&types=address,place&limit=1`
      );
      const json = await res.json();
      const address = json.features?.[0]?.place_name ?? `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
      onLocationSelect?.({ lat, lng, address });
    } catch {
      onLocationSelect?.({ lat, lng, address: `${lat.toFixed(5)}, ${lng.toFixed(5)}` });
    }
  }, [onLocationSelect, onBoundarySizeChange]);

  // ── RENDER ────────────────────────────────────────────────────
  const circleData = markerPos ? makeCircle(markerPos.lng, markerPos.lat, radiusKm) : null;

  return (
    <Map
      ref={mapRef}
      mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
      initialViewState={{ longitude: 28.0473, latitude: -26.2041, zoom: 12 }}
      style={{ width: '100%', height: '100%', pointerEvents: 'auto' }}
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