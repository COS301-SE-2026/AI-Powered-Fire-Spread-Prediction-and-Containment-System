'use client';
import React, { useEffect, useState, useRef } from 'react';
import dynamic from 'next/dynamic';
import { SideBarLayout } from '../../components/demoSidebar';
import { GuestEnvironment } from '../../components/guest/GuestEnvironment';
import { GuestMapHandle, GuestMapProps } from '../../components/guest/GuestMap';
import { GuestReports } from '../../components/guest/GuestReports';
import { GuestActions } from '../../components/guest/GuestActions';

const GuestMapDynamic = (dynamic as any)(
  () => import('../../components/guest/GuestMap').then(mod => mod.default),
  {
    ssr: false,
    loading: () => (
      <div className="flex-1 flex items-center justify-center bg-carbon-side/20 animate-pulse h-full w-full">
        <span className="text-neutral/40 font-display tracking-widest text-sm uppercase">
          Initializing Map
        </span>
      </div>
    )
  }
) as React.ForwardRefExoticComponent<GuestMapProps & { ref?: React.Ref<GuestMapHandle> }>;

export default function GuestPublicDashboard() {
  const defaultLocation = { lat: -25.7479, lng: 28.2293 };
  const [location, setLocation] = useState(defaultLocation);
  const [envData, setEnvData] = useState(null);
  const [reports, setReports] = useState([]);
  const [drawMode, setDrawMode] = useState(false);
  const [clearDrawings, setClearDrawings] = useState(0);
  const mapRef = useRef<GuestMapHandle>(null);

    //get user location
    useEffect(() => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                pos => setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
                () => {}
            );
        }
    }, []);
    //fetch dashboard data
    useEffect(()=>{
        const fetchData= async () =>{
            try{
                const resp = await fetch(`/api/guests/dashboard?lat=${location.lat}&lng=${location.lng}&radius_km=20`);
                if(!resp.ok) throw new Error("Failed to fetch dashboard data");
                const data= await resp.json();
                setEnvData(data.environment_variables);
                setReports(data.nearby_reports);
            }catch(err){
                console.error("Dashboard fetch error", err);
            }  
        };
        fetchData();
    },[location]);
  
    const handleDrawComplete=(wkt:string)=>{
      console.log('Drawn WKT', wkt);
      setDrawMode(false);
    };
    const handleToggleDraw=()=>{
      setDrawMode(!drawMode);
    };
    const handleUndo=()=>{
      if(mapRef.current){
        mapRef.current.undoDraw();
      }
    };
    const handleClear=()=>{
      if(mapRef.current){
        mapRef.current.clearDraw();
      }
    };
    const handleRecenter=()=>{
      if (mapRef.current && location) {
        mapRef.current.recenter(location.lat, location.lng);
      }
    };
  return (
    <SideBarLayout hideLogout>
      <div className="flex flex-col p-6">
        {/* Header */}
        <header className="mb-4 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-display font-bold tracking-wider text-neutral uppercase">
              Incident Map
            </h1>
            <p className="text-sm text-neutral/50 font-medium">Public Fire Map View</p>
          </div>
        </header>

        {/* Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
          {/* Left column */}
          <div className="xl:col-span-7 flex flex-col gap-6">
            <div className="relative rounded-2xl overflow-hidden border border-carbon-card h-[33rem] w-full shadow-md">
              <GuestMapDynamic
                ref={mapRef}
                reports={reports}
                centerLat={location.lat}
                centerLng={location.lng}
                user_location={location}
                drawMode={drawMode}
                onDrawComplete={handleDrawComplete}
                clearDrawings={clearDrawings}
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <GuestEnvironment data={envData} />
              <GuestActions
                isDrawMode={drawMode}
                onToggleDraw={handleToggleDraw}
                onUndo={handleUndo}
                onClear={handleClear}
                onRecenter={handleRecenter}
                canUndo={mapRef.current?.hasDrawings?.() ?? false}
                canClear={mapRef.current?.hasDrawings?.() ?? false}
              />
              </div>
          </div>

          {/* Right column – Nearby Reports */}
          <div className="xl:col-span-4 flex flex-col gap-3">
            <h2 className="text-xs font-bold tracking-widest text-neutral/50 uppercase">Nearby Reports</h2>
            <div
              className="rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card overflow-y-auto"
              style={{ maxHeight: 'calc(480px + 2rem + 140px)' }}
            >
              <GuestReports reports={reports} />
            </div>
          </div>
        </div>
      </div>
    </SideBarLayout>
  );
}