import React,{useState, useEffect, useRef} from 'react';
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
interface GuestMapProps{
    reports:Report[];
    centerLat:number;
    centerLng:number;
    drawMode?:boolean;
    onDrawComplete?: (wkt:string) =>void ;
    clearDrawings?:number;


}


export function GuestMap({
    reports,
    centerLat,
    centerLng,
    drawMode=false,
    onDrawComplete,
    clearDrawings=0,
    }: GuestMapProps){
    const [selected, setSelected]= useState<Report |null>(null);
    const [viewport,  setViewport]= useState({
        longitude: centerLng,
        latitude: centerLat,
        zoom:12,
    });
    const mapRef=useRef<any>(null);
    const drawRef=useRef<any>(null);

    useEffect(()=>{
        setViewport(v =>({ ...v, longitude:centerLng, latitude:centerLat}));
    },[centerLat,centerLng]);

//drawing logic from /firefighter/FireMap
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
}