"use client";
import 'mapbox-gl/dist/mapbox-gl.css'
import circle from '@turf/circle';
import React, { useEffect, useState, useRef, useMemo } from 'react';
import { Map, Marker, Popup, Layer, Source } from 'react-map-gl/mapbox';
import MapboxDraw from '@mapbox/mapbox-gl-draw'
import { Prediction } from './useSimulation';

interface FireReport{
    ref: string;
    location: string;
    status: string
    lat: number;
    lng: number;
    size?: number;
    reported: string;
    reporter?: string;
}

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
}

export function FireMap({lat, lng, drawMode, onDrawComplete, clearDrawings, burnGridH, burnGridW, predictions, currentTick=0}: MapProps) {

    const mapRef = useRef<any>(null);
    const drawRef = useRef<any>(null);

    const [fires, setFires] = useState<FireReport[]>([]);
    const [viewState, setViewState] = useState({longitude: lng, latitude: lat, zoom: 12});
    const [selectedFire, setSelectedFire] = useState<FireReport | null>(null);

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
        }else{
            if(drawRef.current){
                drawRef.current.changeMode('simple_select');
            }
        }
    }, [drawMode]);

    useEffect(() => {
        if(!drawRef.current) return;
        drawRef.current.deleteAll();
    }, [clearDrawings])

    useEffect(() => {
        setViewState(v => ({...v, longitude: lng, latitude:lat}));
    },[lat,lng]);

    const circleFeatures = useMemo(() => {
        return fires.filter(f => f.size != null && f.size > 0).map(f => circle([f.lng, f.lat], f.size, {
            steps: 64,
            units: 'kilometers',
            properties: {ref: f.ref}
        }));
    }, [fires])

    const simulationCircle = useMemo(() => {
        if (!predictions?.length) return [];

        // ~185 m cells: 0.05 degrees across a 30-cell grid
        const cellM = (0.05 / 30) * 111320;

        return predictions
            .map(p => {
                const grid = p.history[currentTick];
                if (!grid) return null;
                const cells = grid.filter(c => c === 1 || c === 2).length;
                if (cells === 0) return null;

                const radiusKm = Math.sqrt(cells * cellM * cellM / Math.PI) / 1000;
                return circle([p.lng, p.lat], radiusKm, {
                    steps: 64,
                    units: 'kilometers',
                    properties: { ref: p.ref },
                });
            })
            .filter(Boolean);
    }, [predictions, currentTick]);



    return (
        <Map
            ref={mapRef}
            mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
            {...viewState}
            onMove={evt => setViewState(evt.viewState)}
            style={{ width: '100%', height: '100%' }}
            mapStyle="mapbox://styles/mapbox/navigation-night-v1"
        >
           {fires.map((fire) => (
                <Marker key={fire.ref} longitude={fire.lng} latitude={fire.lat} anchor="center" onClick={() => setSelectedFire(fire)}>
                    <div className="relative flex items-center justify-center size-6">
                        {/* The radar ping animation effect */}
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-ignite opacity-75" />
                        {/* The solid core so the marker remains visible */}
                        <span className="relative inline-flex rounded-full size-3 bg-ignite shadow-lg shadow-black" />
                    </div>
                </Marker>
            ))}

            {/*Circles around markers*/}
            {circleFeatures.length>0 &&(
              <Source 
                  id ="fire-circles"
                  type="geojson"
                  data={{
                      type:'FeatureCollection',
                      features:circleFeatures
                  }}
                  >
                      <Layer 
                          id="fire-radius-fill"
                          type="fill"
                          paint={{
                            'fill-color': '#ff4500',
                            'fill-opacity': 0.25,
                          }}
                      />

                      <Layer 
                          id="fire-radius-outline"
                          type="line"
                          paint={{
                            'line-color': '#ff4500',
                            'line-width': 1,
                          }}
                      />
                  </Source>

          )}

          {simulationCircle.length > 0 && (
            <Source id="simulation-circle" type="geojson" data={{type: 'FeatureCollection', features: simulationCircle}}>
                <Layer
                    id="simulation-fill"
                    type="fill"
                    paint={{
                        'fill-color': '#ffd54f',
                        'fill-opacity': 0.18,
                    }}
                > 
                </Layer>

                <Layer
                    id="simulation-outline"
                    type="line"
                    paint={{
                        'line-color': '#ffc107',
                        'line-width': 1,
                        "line-dasharray": [2,2]
                    }}
                > 
                </Layer>
            </Source>
          )}

            {selectedFire && (
                <Popup longitude={selectedFire.lng} latitude={selectedFire.lat} onClose={() => setSelectedFire(null)}>
                    <div>
                        <h3>{selectedFire.location}</h3>
                        <p>Status: {selectedFire.status}</p>
                        <p>Submitted: {new Date(selectedFire.reported).toLocaleString()}</p>
                        {selectedFire.size && (
                            <p>Radius: {selectedFire.size} m</p>
                        )}
                    </div>
                </Popup>
            )}
        </Map>
    );
}
