import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { FirefighterSideBar } from '../../components/firefighter/firefighterSidebar';
import { QuickActions } from '../../components/firefighter/quickActions';
import { NearbyReports, useNearbyFires } from '../../components/nearbyReports';
import { EnvironmentWidgets } from '../../components/firefighter/weatherStats';
import { MapStatsOverlay } from '../../components/firefighter/mapStat';
import { FireMap } from '../../components/DynamicFirefighterMap';
import { useContainmentLine } from '../../components/firefighter/useContainmentLine';

export default function FirefighterDashboard() {
    const [drawMode, setDrawMode] = useState(false);
    const [clearDrawings, setClearDrawings] = useState(0);
    const { userLocation, nearbyFires, environmentVariables }=useNearbyFires();

    const handleDrawComplete = useContainmentLine(() => setDrawMode(false));

    return(
        <FirefighterSideBar hideLoginRegister>
            <div className="flex flex-col p-6">
                <header className="mb-4 flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-display font-bold tracking-wider text-text-primary uppercase">Firefighter Dashboard</h1>
                        <p className="text-sm text-text-primary/50 font-medium">Tshwane District • Real-time Monitoring</p>
                    </div>
                </header>

                {/* Main Grid container */}
                <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 xl:grid-rows-1">

                    <div className="xl:col-span-8 flex flex-col gap-4">
                        {/* Map */}
                        <div className="rounded-2xl bg-carbon-side/40 border border-carbon-stroke backdrop-blur-sm flex flex-col overflow-hidden relative shadow-2xl shadow-black/20 h-[480px]">
                            <div className="p-4 border-b border-carbon-card bg-carbon-bg/50 backdrop-blur-md absolute top-0 w-full z-10 flex justify-between items-center border-l-2 border-l-ignite/60">
                                <span className="font-bold text-m tracking-wide text-text-primary/80">LIVE FIRE MAP</span>
                                <button type="button" onClick={() => setClearDrawings(c => c + 1)} className="text-xs font-medium text-text-primary/60 hover:text-ignite transition-colors">Clear Lines</button>
                            </div>
                            <div className="flex-1 w-full h-full pt-[53px]">
                                <FireMap lat={userLocation.lat} lng={userLocation.lng}  drawMode={drawMode} onDrawComplete={handleDrawComplete} clearDrawings={clearDrawings}/>
                            </div>
                            <MapStatsOverlay nearby_fires={nearbyFires}/>
                        </div>
                        <div className="grid grid-cols-2 gap-2 shrink-0">
                            <div className="flex flex-col">
                                <h2 className="text-xs font-bold tracking-widest text-text-primary/50 uppercase mb-3">
                                    Environment Variables
                                </h2>
                                <EnvironmentWidgets variables={environmentVariables}/>
                            </div>
                            <div className="flex flex-col">
                                <h2 className="text-xs font-bold tracking-widest text-text-primary/50 uppercase mb-3">
                                    Quick Actions
                                </h2>
                                <QuickActions onStartDraw={() => setDrawMode(true)}/>
                            </div>
                        </div>
                    </div>

                    {/* Right Column */}
                    <div className="xl:col-span-4 flex flex-col gap-3" style={{ maxHeight: '100%' }}>
                        <h2 className="text-xs font-bold tracking-widest text-text-primary/50 uppercase shrink-0">
                            Nearby Reports
                        </h2>
                        <div className="rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card overflow-y-auto" style={{ maxHeight: 'calc(480px + 2rem + 220px)' }}>
                            <NearbyReports nearby_fires={nearbyFires}/>
                        </div>
                    </div>
                </div>
            </div>
        </FirefighterSideBar>
    );
}