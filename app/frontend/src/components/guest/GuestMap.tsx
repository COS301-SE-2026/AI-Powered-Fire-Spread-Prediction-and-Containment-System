'use client'
import React,{useState, useEffect, useRef, forwardRef, useImperativeHandle} from 'react';
import { Map, Marker, Popup, Layer, Source } from 'react-map-gl/mapbox';
import 'mapbox-gl/dist/mapbox-gl.css';
import MapboxDraw from '@mapbox/mapbox-gl-draw';   
interface Report{
    id: string;
    lat:number;
    lng:number;
    location_text:string;
    status:string;
    boundary_radius?:number;//will probably change later on
    //future fields
}
export interface GuestMapProps{
    reports:Report[];
    centerLat:number;
    centerLng:number;
    drawMode?:boolean;
    onDrawComplete?: (wkt:string) =>void ;
    clearDrawings?:number;
    user_location?: {lat:number, lng:number};
}

export interface GuestMapHandle{
    undoDraw:()=>void;
    clearDraw:()=>void;
    hasDrawings:()=>boolean;
    recenter:(lat:number, lng:number)=>void;
}


const GuestMap= forwardRef<GuestMapHandle, GuestMapProps>(({
    reports,
    centerLat,
    centerLng,
    user_location,
    drawMode,
    onDrawComplete,
    clearDrawings,
    }, ref)=>{
    const [selected, setSelected]= useState<Report |null>(null);
    const [viewport,  setViewport]= useState({
        longitude: centerLng,
        latitude: centerLat,
        zoom:12,
    });
    const mapRef=useRef<any>(null);
    const drawRef=useRef<any>(null);
    const [drawingCount, setDrawingCount]=useState(0)

    useEffect(()=>{
        setViewport(v =>({ ...v, longitude:centerLng, latitude:centerLat}));
    },[centerLat,centerLng]);


    useEffect(()=>{
        if(drawRef.current){
            drawRef.current.deleteAll();
            setDrawingCount(0);
        }
    },[clearDrawings]);

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
            const updateCount=()=>{
                if(drawRef.current){
                    const features =drawRef.current.getAll();
                    setDrawingCount(features.features.length);
                }
            };
            map.on('draw.create', updateCount);
            map.on('draw.delete', updateCount);
            map.on('draw.update', updateCount);
            (drawRef.current as any)._listeners= {updateCount};

            drawRef.current.changeMode('draw_line_string')


            const handleDrawCreate = (e: any) => {
                const line = e.features[0];
                const coords = line.geometry.coordinates;
                const wkt = `LINESTRING(${coords.map((c: number[]) => `${c[0]} ${c[1]}`).join(', ')})`;
                onDrawComplete(wkt);

                if(drawRef.current){
                    drawRef.current.changeMode('simple-select');
                }
            }
            map.on('draw.create', handleDrawCreate);
            (drawRef.current as any)._handleDrawCreate = handleDrawCreate;

        }else{
            if(drawRef.current){
                drawRef.current.changeMode('simple_select');
            }
        }
        return () => {
            if (map && drawRef.current) {
                const listeners = (drawRef.current as any)._listeners;
                if (listeners) {
                map.off('draw.create', listeners.updateCount);
                map.off('draw.delete', listeners.updateCount);
                map.off('draw.update', listeners.updateCount);
                }
                if ((drawRef.current as any)._handleDrawCreate) {
                map.off('draw.create', (drawRef.current as any)._handleDrawCreate);
                }
            }
        };
    }, [drawMode, onDrawComplete]);

useImperativeHandle(ref, () => ({
    undoDraw: () => {
      if (!drawRef.current) return;
      const features = drawRef.current.getAll();
      if (features.features.length === 0) return;
      const lastFeature = features.features[features.features.length - 1];
      drawRef.current.delete(lastFeature.id);
      setDrawingCount(features.features.length - 1);
    },
    clearDraw: () => {
      if (!drawRef.current) return;
      drawRef.current.deleteAll();
      setDrawingCount(0);
    },
    hasDrawings: () => drawingCount > 0,
    recenter: (lat: number, lng: number) => {
      if (mapRef.current) {
        const map = mapRef.current.getMap();
        map.flyTo({ center: [lng, lat], zoom: 14, essential: true });
      }
    },
  }));

    const circleFeatures = reports
    .filter(r => r.boundary_radius && r.boundary_radius > 0)
    .map(r => ({
      type: 'Feature' as const,
      geometry: { type: 'Point' as const, coordinates: [r.lng, r.lat] },
      properties: { radius: r.boundary_radius * 1000 },
    }));
    return (
        <Map
            ref={mapRef}
            mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
            {...viewport}
            onMove={evt=> setViewport(evt.viewState)}
            style={{width:'100%', height:'100%'}}
            mapStyle="mapbox://styles/mapbox/navigation-night-v1"
        >
        {/*Markers*/}
            {reports.map(report => (
                    <Marker key={report.id} longitude={report.lng} latitude={report.lat} anchor="center" onClick={() => setSelected(report)}>
                    <div className="relative flex items-center justify-center size-6">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-ignite opacity-75" />
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
                            id="fire-radius"
                            type="circle"
                            paint={{
                            'circle-color': '#ff4500',
                            'circle-opacity': 0.25,
                            'circle-stroke-color': '#ff4500',
                            'circle-stroke-width': 1,
                            'circle-radius': [
                                'interpolate',
                                ['linear'],
                                ['zoom'],
                                0, 0,
                                8, ['*', ['get', 'radius'], 0.05],
                                12, ['*', ['get', 'radius'], 0.1],
                                16, ['*', ['get', 'radius'], 0.2],
                                20, ['*', ['get', 'radius'], 0.5]
                            ]
                            }}
                        />
                </Source>

            )}
            
      {/* Popup */}
      {selected && (
        <Popup
          longitude={selected.lng}
          latitude={selected.lat}
          onClose={() => setSelected(null)}
        >
          <div>
            <h3>{selected.location_text}</h3>
            <p>Status: {selected.status}</p>
            {selected.boundary_radius && (
              <p>Radius: {selected.boundary_radius} km</p>
            )}
          </div>
        </Popup>
      )}
        </Map>
    );
});
GuestMap.displayName = 'GuestMap';
export default GuestMap;