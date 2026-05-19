import React from 'react';
import dynamic from 'next/dynamic';
import { SidebarLayout } from '../components/firefighter/sidebar';
import { QuickActions } from '../components/firefighter/quickActions';
import { NearbyReports } from '../components/firefighter/nearbyReports';

const FireMap = dynamic(
    () => import('../components/firefighter/FireMap').then((mod) => mod.FireMap),
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
    return(
        <SidebarLayout>
            <div className="flex flex-col h-full">
                <header className="mb-8 flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-display font-bold tracking-wider text-neutral uppercase">Firefighter Dashboard</h1>
                        <p className="text-sm text-neutral/50 font-medium">Tshwane District • Real-time Monitoring</p>
                    </div>
                </header>                

                {/* Main Grid container */}
                <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 flex-1 min-h-0">

                    <div className="xl:col-span-8 flex flex-col gap-4 min-h-0">
                        {/* Map */}
                        <div className="rounded-2xl bg-carbon-side/40 border border-carbon-card backdrop-blur-sm flex flex-col overflow-hidden relative shadow-2xl shadow-black/20 min-h-[500px]">
                            <div className="p-4 border-b border-carbon-card bg-carbon-bg/50 backdrop-blur-md absolute top-0 w-full z-10 flex justify-between items-center">
                                <span className="font-bold text-m tracking-wide text-neutral/80">LIVE FIRE MAP</span>
                            </div>
                            <div className="flex-1 w-full h-full pt-[53px]"> 
                                <FireMap />
                            </div>
                        </div>
                        <div className="grid grid-cols-2 xl-gird-cols-6 gap-2 flex-1 min-h-0">
                            <div>
                                <h2 className="text-xs font-bold tracking-widest text-neutral/50 uppercase mb-3">
                                    Weather Statistics
                                </h2>

                            </div>
                            <div>
                                <h2 className="text-xs font-bold tracking-widest text-neutral/50 uppercase mb-3">
                                    Quick Actions
                                </h2>
                                <QuickActions />
                            </div>
                        </div>
                        

                    </div>

                    {/* Right Column */}
                    <div className="xl:col-span-4 flex flex-col gap-4 overflow-y-auto">
                        <NearbyReports/>
                    </div>
                </div>
            </div> 
        </SidebarLayout>
    );
}