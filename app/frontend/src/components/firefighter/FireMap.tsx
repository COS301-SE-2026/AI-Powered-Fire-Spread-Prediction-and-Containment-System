'use client';

import 'mapbox-gl/dist/mapbox-gl.css'
import circle from '@turf/circle';
import React, { useEffect, useState, useRef, useMemo } from 'react';
import { Map, Marker, Popup, Layer, Source } from 'react-map-gl/mapbox';
import MapboxDraw from '@mapbox/mapbox-gl-draw'
import { Prediction } from '../../hooks/useSimulation';
import type { FirefighterReportTable } from '../../types/FirefighterReports';
import { useFirefighterReports } from '../../hooks/useFirefighterReports';

interface MapProps{
    lat: number;
    lng: number;
    drawMode: boolean;
    onDrawComplete: (line: string) => void;
    clearDrawings: number;
    burnGrid?: number[] | null;
    burnGridH?: number;
    burnGridW?: number;
    predictions?: Prediction[];
    currentTick?: number;
    selectedFireId?: string | null;
    onSelectFire?: (ref: string) => void;
}

export function FireMap({lat, lng, drawMode, onDrawComplete, clearDrawings, burnGridH, burnGridW, predictions, currentTick=0, selectedFireId, onSelectFire}: MapProps) {

    const mapRef = useRef<any>(null);
    const drawRef = useRef<any>(null);

    const { reports: fires } = useFirefighterReports(''); // no search — just the full nearby fires list for the map
    const [viewState, setViewState] = useState({longitude: lng, latitude: lat, zoom: 12});
    const [selectedFire, setSelectedFire] = useState<FirefighterReportTable | null>(null);

    const handleDrawCreate = (e: any) => {
        const line = e.features[0];
        const coords = line.geometry.coordinates;
        const wkt = `LINESTRING(${coords.map((c: number[]) => `${c[0]} ${c[1]}`).join(', ')})`;
        onDrawComplete(wkt);
    }

    useEffect(() => {
        if(!mapRef.current){
            return;
        }
        const map = mapRef.current.getMap();

        if(drawMode){
            if(!drawRef.current){
                drawRef.current = new MapboxDraw({
                    displayControlsDefault: false,
                    modes: {...MapboxDraw.modes},
                });
                map.addControl(drawRef.current);
            }
            drawRef.current.changeMode('draw_line_string')

            map.off('draw.create', handleDrawCreate);
            map.on('draw.create', handleDrawCreate);
        }else if(drawRef.current){
                drawRef.current.changeMode('simple_select');
            }
    }, [drawMode]);

    useEffect(() => {
        if(!drawRef.current) return;
        drawRef.current.deleteAll();
    }, [clearDrawings])

    useEffect(() => {
        setViewState(v => ({...v, longitude: lng, latitude:lat}));
    },[lat,lng]);

    const circleFeatures = useMemo(() => fires.filter(f => f.size != null && f.size > 0).map(f => circle([f.lng, f.lat], f.size, {
            steps: 64,
            units: 'kilometers',
            properties: {ref: f.ref}
        })), [fires])

    useEffect(() => {
        if(!selectedFireId) return;
        const fire = fires.find(f => f.ref === selectedFireId);
        if(!fire) return;
        setViewState(v => ({...v, longitude: fire.lng, latitude: fire.lat, zoom: Math.max(v.zoom, 13)}))
    }, [selectedFireId, fires])

    const EXTENT_DEG = 0.05;

    const girdFeautures = useMemo(() => {
        if(!predictions?.length || !burnGridH || !burnGridW) return [];
        
        const features = [];
        const cellLonSize = EXTENT_DEG / burnGridW;
        const cellLatSize = EXTENT_DEG / burnGridH;

        for (const p of predictions){
            const grid = p.history[currentTick]
            if(!grid) continue;

            const minLon = p.lng - EXTENT_DEG / 2;
            const maxLat = p.lat + EXTENT_DEG / 2;

            for(let row = 0; row < burnGridH; row++){
                for(let col = 0; col < burnGridW; col++){
                    const state = grid[row * burnGridW + col];
                    if(state === 0) continue;

                    const cellMinLon = minLon + col * cellLonSize;
                    const cellMaxLat = maxLat - row * cellLatSize;

                    features.push({
                        type: 'Feature',
                        properties: { ref: p.ref, state},
                        geometry: {
                            type: 'Polygon',
                            coordinates: [[
                                [cellMinLon, cellMaxLat - cellLatSize],
                                [cellMinLon + cellLonSize, cellMaxLat - cellLatSize],
                                [cellMinLon + cellLonSize, cellMaxLat],
                                [cellMinLon, cellMaxLat],
                                [cellMinLon, cellMaxLat - cellLatSize],
                            ]],
                        }
                    });
                }
            }
        }
        return features;
    }, [predictions, currentTick, burnGridH, burnGridW])

    return (
        <Map
            ref={mapRef}
            mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
            {...viewState}
            onMove={evt => setViewState(evt.viewState)}
            style={{ width: '100%', height: '100%' }}
            mapStyle='mapbox://styles/mapbox/navigation-night-v1'
        >
           {fires.map((fire) => (
                <Marker key={fire.ref} longitude={fire.lng} latitude={fire.lat} anchor='center' onClick={(e) => {e.originalEvent.stopPropagation(); setSelectedFire(fire); onSelectFire?.(fire.ref); }}>
                    <div className='relative flex items-center justify-center size-6'>
                        {/* The radar ping animation effect */}
                        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75 ${fire.ref === selectedFireId ? '' : 'hidden'}`} />
                        {/* The solid core so the marker remains visible */}
                        <span className={`relative inline-flex rounded-full size-3 bg-accent shadow-lg shadow-black ${fire.ref === selectedFireId ? 'bg-flare ring-2 ring-white' : 'bg-accent'}`} />
                    </div>
                </Marker>
            ))}

            {/* Circles around markers */}
            {circleFeatures.length>0 &&(
              <Source
                  id ='fire-circles'
                  type='geojson'
                  data={{
                      type:'FeatureCollection',
                      features:circleFeatures
                  }}
                  >
                      <Layer
                          id='fire-radius-fill'
                          type='fill'
                          paint={{
                            'fill-color': '#fcba3e',
                            'fill-opacity': 0.3,
                          }}
                      />

                      <Layer
                          id='fire-radius-outline'
                          type='line'
                          paint={{
                            'line-color': '#fcba3e',
                            'line-width': 1,
                          }}
                      />
                  </Source>

          )}

          {girdFeautures.length > 0 && (
            <Source id='burn-grid' type='geojson' data={{type: 'FeatureCollection', features: girdFeautures}}>
                <Layer
                    id='burn-grid-fill'
                    type='fill'
                    paint={{
                        'fill-color': ['match', ['get', 'state'], 1, '#ff6b1a', 2, '#46201d', '#000000'], // swap with ignite and torch vals
                        'fill-opacity': ['match', ['get', 'state'], 1, 0.75, 2, 0.55, 0],
                        'fill-antialias': true
                    }}
                 />

                <Layer
                    id='simulation-outline'
                    type='line'
                    paint={{
                        'line-color': '#000000',
                        'line-opacity': 0.15,
                        'line-width': 0.5,
                    }}
                 />
            </Source>
          )}

            {selectedFire && (
                <Popup longitude={selectedFire.lng} latitude={selectedFire.lat} onClose={() => setSelectedFire(null)} className='carbon-popup'>
                    <div className='p-1'>
                        <h3 className='font-display font-bold text-sm uppercase tracking-wide text-ignite'>
                            {selectedFire.location}
                        </h3>
                        <p className='text-xs text-text-muted mt-1'>
                            Status: <span className='text-neutral-content'>{selectedFire.status}</span>
                        </p>
                        <p className='text-xs text-text-muted'>
                            Submitted: <span className='text-neutral-content'>{new Date(selectedFire.reported).toLocaleString()}</span>
                        </p>
                        {selectedFire.size && (
                            <p className='text-xs text-text-muted'>
                                Radius: <span className='text-neutral-content'>{selectedFire.size} km</span>
                            </p>
                        )}
                    </div>
                </Popup>
            )}
        </Map>
    );
}
