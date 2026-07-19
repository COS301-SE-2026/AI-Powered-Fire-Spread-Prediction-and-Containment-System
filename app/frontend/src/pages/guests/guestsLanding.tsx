'use client';
import React, { useEffect, useState, useRef , useCallback} from 'react';
import { SideBarLayout } from '../../components/demoSidebar';
import { GuestEnvironment } from '../../components/guest/GuestEnvironment';
import GuestMap,{ GuestMapHandle } from '../../components/guest/GuestMap';
import { GuestReports } from '../../components/guest/GuestReports';
import { GuestActions } from '../../components/guest/GuestActions';

export default function GuestPublicDashboard() {
  const defaultLocation = { lat: -25.7479, lng: 28.2293 };
  const [location, setLocation] = useState(defaultLocation);
  const [envData, setEnvData] = useState(null);
  const [reports, setReports] = useState([]);
  const [drawMode, setDrawMode] = useState(false);
//  const [clearDrawings, setClearDrawings] = useState(0);
//  const [drawingCount, setDrawingCount] = useState(0);
  const [isClient, setIsClient] = useState(false);
  const mapRef = useRef<GuestMapHandle>(null);
  useEffect(() => {
    setIsClient(true);
  }, []);
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
  
    const handleDrawComplete = useCallback((wkt: string) => {
      console.log('Drawn WKT', wkt);
      setDrawMode(false);
    }, []);
    const handleToggleDraw=()=>{
      console.log('Draw mode changed')
      setDrawMode(!drawMode);
    };
    const handleUndo = () => {
      console.log('Undo called, mapRef.current:', mapRef.current);
      mapRef.current?.undoDraw();
    };
    const handleClear = () => {
      console.log('Clear called, mapRef.current:', mapRef.current);
      mapRef.current?.clearDraw();
    };
    const handleRecenter = () => {
      console.log('Recenter called, mapRef.current:', mapRef.current);
      if (mapRef.current && location) {
        mapRef.current.recenter(location.lat, location.lng);
      }
    };
    const handleDrawingsChange = useCallback((count: number) => {
      console.log('drawing count changed:', count);
      //setDrawingCount(count);
    }, []);
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
                            {isClient ? (
                <GuestMap
                  ref={mapRef}
                  reports={reports}
                  centerLat={location.lat}
                  centerLng={location.lng}
                  user_location={location}
                  drawMode={drawMode}
                  onDrawComplete={handleDrawComplete}
                  //clearDrawings={clearDrawings}
                  onDrawingsChange={handleDrawingsChange}
                />
              ) : (
                <div className="flex-1 flex items-center justify-center bg-carbon-side/20 animate-pulse h-full w-full">
                  <span className="text-neutral/40 font-display tracking-widest text-sm uppercase">
                    Initializing Map
                  </span>
                </div>
              )}
            </div>
            <div className="grid grid-cols-2 gap-2">
              <GuestEnvironment data={envData} />
              <GuestActions
                isDrawMode={drawMode}
                onToggleDraw={handleToggleDraw}
                //onUndo={handleUndo}
                //onClear={handleClear}
                onRecenter={handleRecenter}
                //canUndo={drawingCount > 0}
                //canClear={drawingCount > 0}
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