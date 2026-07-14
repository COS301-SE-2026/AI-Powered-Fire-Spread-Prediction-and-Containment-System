import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { SideBarLayout } from '../../components/demoSidebar';
import { QuickActions } from '../../components/firefighter/quickActions';
import { NearbyReports } from '../../components/firefighter/nearbyReports';
import { EnvironmentWidgets } from '../../components/firefighter/weatherStats';
import { MapStatsOverlay } from '../../components/firefighter/mapStat';

const FireMap = dynamic(
    () => import('../../components/firefighter/FireMap').then((mod) => mod.FireMap),
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
);

export default function FirefighterDashboard() {
    const default_location = { lat: -25.7479, lng: 28.2293}; // Pretoria
    const [drawMode, setDrawMode] = useState(false);
    const [userLocation, setUserLocation] = useState(default_location);
    const [clearDrawings, setClearDrawings] = useState(0);
    const [isDefaultLocation, setIsDefaultLocation] = useState(true);
    const [nearbyFires, setNearbyFires] = useState<any[]>([]);
    const [environmentVariables, setEnvironmentVariables] = useState<any | null>(null);

    useEffect (() => {
        if(!navigator.geolocation){ // if user does not allow location return default location on map
            return;
        }

        {/* if users location permissions accepted set lat and lng to users location */}
        navigator.geolocation.getCurrentPosition(
            (position) => {
                setUserLocation({
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                });
                setIsDefaultLocation(false);
            },
            () => {} // keeps default if there is failure retreiving users location
        )
    }, [])

    useEffect(() => {

        const fetchController = new AbortController();
        const fetchRequest = async () => {
            const url = `/api/firefighter/firefighter-dashboard?lat=${userLocation.lat}&lng=${userLocation.lng}`;
            try{
                const resp = await fetch(url, {signal: fetchController.signal});
                if (!resp.ok){
                    setNearbyFires([]);
                    setEnvironmentVariables(null);
                    return;
                }
                const data = await resp.json();
                setNearbyFires(data.nearby_fires?.data ?? []);
                setEnvironmentVariables(data.environment_variables ?? null);
            } catch(error){
                if(error.name === 'AbortError') return; // this request is superseded by a newer request
                console.error("Was unable to find/retrieve dashboard data", error);
                setNearbyFires([]);
                setEnvironmentVariables(null);
            }
        };
        fetchRequest();
        return () => fetchController.abort(); // this will cancel the fetch if the users location again changes before it is resolved
    }, [userLocation]);

    return(
        <SideBarLayout hideLoginRegister>
            <div className="flex flex-col p-6">
                <header className="mb-4 flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-display font-bold tracking-wider text-neutral uppercase">Firefighter Dashboard</h1>
                        <p className="text-sm text-neutral/50 font-medium">Tshwane District • Real-time Monitoring</p>
                    </div>
                </header>                

                {/* Main Grid container */}
                <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 xl:grid-rows-1">

                    <div className="xl:col-span-8 flex flex-col gap-4">
                        {/* Map */}
                        <div className="rounded-2xl bg-carbon-side/40 border border-carbon-stroke backdrop-blur-sm flex flex-col overflow-hidden relative shadow-2xl shadow-black/20 h-[480px]">
                            <div className="p-4 border-b border-carbon-card bg-carbon-bg/50 backdrop-blur-md absolute top-0 w-full z-10 flex justify-between items-center border-l-2 border-l-ignite/60">
                                <span className="font-bold text-m tracking-wide text-neutral/80">LIVE FIRE MAP</span>
                                <button onClick={() => setClearDrawings(c => c + 1)} className="text-xs font-medium text-neutral/60 hover:text-ignite transition-colors">Clear Lines</button>
                            </div>
                            <div className="flex-1 w-full h-full pt-[53px]"> 
                                <FireMap lat={userLocation.lat} lng={userLocation.lng}  drawMode={drawMode} onDrawComplete={(line) => {setDrawMode(false)}} clearDrawings={clearDrawings}/>
                            </div>
                            <MapStatsOverlay/>
                        </div>
                        <div className="grid grid-cols-2 gap-2 shrink-0">
                            <div className="flex flex-col">
                                <h2 className="text-xs font-bold tracking-widest text-neutral/50 uppercase mb-3">
                                    Environment Variables
                                </h2>
                                <EnvironmentWidgets variables={environmentVariables}/>
                            </div>
                            <div className="flex flex-col">
                                <h2 className="text-xs font-bold tracking-widest text-neutral/50 uppercase mb-3">
                                    Quick Actions
                                </h2>
                                <QuickActions onStartDraw={() => setDrawMode(true)}/>
                            </div>
                        </div>                  
                    </div>

                    {/* Right Column */}
                    <div className="xl:col-span-4 flex flex-col gap-3" style={{ maxHeight: '100%' }}>
                        <h2 className="text-xs font-bold tracking-widest text-neutral/50 uppercase shrink-0">
                            Nearby Reports
                        </h2>
                        <div className="rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card overflow-y-auto" style={{ maxHeight: 'calc(480px + 2rem + 220px)' }}>
                            <NearbyReports nearby_fires={nearbyFires}/>
                        </div>
                    </div>
                </div>
            </div> 
        </SideBarLayout>
    );
}