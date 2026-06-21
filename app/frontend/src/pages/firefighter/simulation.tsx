import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { SideBarLayout } from '../../components/demoSidebar';
import { Simulation_Results } from '../../components/firefighter/simulationResult';

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



export default function ReportTable() {
    return (
        <SideBarLayout>
            <div className="p-4 flex flex-col h-full w-full gap-y-3">

                {/*Page header and subtitle*/}
                <header className="mb-6">
                    <h1 className="text-page-title font-display font-bold tracking-wider text-neutral uppercase">Fire Simulation</h1>
                    <p className="font-body text-body text-neutral/50">Simulate fire spread and prevention methods</p>
                </header>

                {/* Page contents map + simulation results*/}
                <div className="flex flex-row gap-4">
                    {/* Fire Map */}
                    <div className="basis-3/4 rounded-2xl bg-carbon-side/80 border border-carbon-stroke backdrop-blur-sm shadow-2xl shadow-black/20 h-[70vh] overflow-hidden relative">
                        <div className="p-4 border-b border-carbon-card bg-carbon-bg/50 backdrop-blur-md absolute top-0 w-full z-10 flex justify-between items-center border-l-2 border-l-ignite/60">
                            <span className="font-bold text-lg tracking-wide text-neutral/80 uppercase">LIVE FIRE MAP</span>
                        </div>
                        <div className="w-full h-full"> 
                                <FireMap />
                        </div>

                    </div>

                    {/* Simulation results */}
                    <div className="basis-1/4 rounded-2xl bg-carbon-side border border-carbon-stroke overflow-hidden">
                        <Simulation_Results/>
                    </div>
                </div>

                {/* simulation params */}

            </div>  
        </SideBarLayout>
    );
}