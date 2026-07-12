"use client";
import 'mapbox-gl/dist/mapbox-gl.css'
import React, { useState, useEffect } from 'react';
import Map, { Marker, Popup, Source, Layer } from 'react-map-gl/mapbox';

interface FireReport{
    id:string;
    reference_number:string;
    lat: number;
    lng: number;
    location_text:string;
    status:string;
    boundary_radius?:number;
    submitted_at:string;

}
export function FireMap() {
  
  const [reports, setReports]=useState<FireReport[]>([]);
  const [selectedReport, setSelectedReport]= useState<FireReport | null>(null);
  const [viewport, setViewport] = useState({
  longitude: 28.0473,
  latitude: -26.2041,
  zoom: 12,
});
  useEffect(()=>{
      fetch('/api/guests/reported-fires')
      .then(res=>res.json())
      .then(data => {setReports(data);})
      .catch(console.error);
  },[]);
  //build circle features
  const circleFeatures = reports
  .filter(r => r.boundary_radius != null && r.boundary_radius > 0)
  .map(r => ({
    type: 'Feature' as const,
    geometry: { type: 'Point' as const, coordinates: [r.lng, r.lat] },
    properties: { radius: r.boundary_radius*1000 }
  }));
const [mapLoaded, setMapLoaded] = useState(false);

  return (
    
      <Map
        {...viewport}
        onMove={evt => setViewport(evt.viewState)}
        mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
        mapStyle="mapbox://styles/mapbox/navigation-night-v1"
        style={{ width: '100%', height: '100%' }}
        onLoad={() => setMapLoaded(true)}
      >
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

    {/* Markers */}
    {mapLoaded&&reports.map(report => (
      <Marker
        key={report.id}
        longitude={report.lng}
        latitude={report.lat}
        onClick={() => setSelectedReport(report)}
      >
        <div className="relative flex items-center justify-center size-6">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-ignite opacity-75" />
          <span className="relative inline-flex rounded-full size-3 bg-ignite shadow-lg shadow-black" />
        </div>
      </Marker>
      
    ))}

    {selectedReport && (
      <Popup
        longitude={selectedReport.lng}
        latitude={selectedReport.lat}
        onClose={() => setSelectedReport(null)}
      >
        <div>
          <h3>{selectedReport.location_text}</h3>
          <p>Status: {selectedReport.status}</p>
          <p>Submitted: {new Date(selectedReport.submitted_at).toLocaleString()}</p>
          {selectedReport.boundary_radius && (
            <p>Radius: {selectedReport.boundary_radius} m</p>
          )}
        </div>
      </Popup>
    )}
    
  </Map>
  );
}