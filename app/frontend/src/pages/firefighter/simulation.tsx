import { useState } from 'react';
import dynamic from 'next/dynamic';
import { SideBarLayout } from '../../components/demoSidebar';
import { SimulationResults } from '../../components/firefighter/simulationResult';
import { Pencil,CirclePlay } from 'lucide-react';

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
    const [timeline, setTimeline] = useState(0);
    const default_location = { lat: -25.7479, lng: 28.2293}; // Pretoria
    const [drawMode, setDrawMode] = useState(false);
    const [userLocation, setUserLocation] = useState(default_location);
    const [clearDrawings, setClearDrawings] = useState(0);
    const [isDefaultLocation, setIsDefaultLocation] = useState(true);
    const [nearbyFires, setNearbyFires] = useState<any[]>([]);
    const [environmentVariables, setEnvironmentVariables] = useState<any | null>(null);
    
    const handleDrawComplete = async (wkt: string) => {
        setDrawMode(false);
        try{
            const resp = await fetch('/api/firefighter/containment-line', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({wkt})
            });
            if(!resp.ok) {
                const err = await resp.json();
                console.error("Failed to save the containment line", err.detail);
                return;
            } 
        }catch(error) {
            console.error("was unable to submit containment line", error);
        }
    };

    return (
        <SideBarLayout>
            <div className="p-4 flex flex-col h-full w-full gap-y-3">

                {/*Page header and subtitle*/}
                <header className="mb-6">
                    <h1 className="text-page-title font-display font-bold tracking-wider text-neutral uppercase">Fire Simulation</h1>
                    <p className="font-body text-body text-neutral/50">Simulate fire spread and prevention methods</p>
                </header>

                <div className="flex flex-row gap-4 min-w-0">

                    {/* left side of page: map + controls and buttons*/}
                    <div className="basis-3/4 flex flex-col gap-4">
                        {/* Fire Map */}
                        <div className="rounded-2xl bg-carbon-side/80 border border-carbon-stroke backdrop-blur-sm shadow-2xl shadow-black/20 h-[70vh] overflow-hidden relative">
                            <div className="p-4 border-b border-carbon-card bg-carbon-bg/50 backdrop-blur-md absolute top-0 w-full z-10 flex justify-between items-center border-l-2 border-l-ignite/60">
                                <span className="font-bold text-lg tracking-wide text-neutral/80 uppercase">LIVE FIRE MAP</span>
                            </div>
                            <div className="w-full h-full"> 
                                <FireMap lat={userLocation.lat} lng={userLocation.lng}  drawMode={drawMode} onDrawComplete={handleDrawComplete} clearDrawings={clearDrawings}/>
                            </div>
                        </div>

                        {/* simulation vars and buttons */}
                        <div className="flex gap-2 items-stretched">
                            {/* buttons to start simulation or draw page */}
                            <div className="flex flex-col gap-6 shrink-0 h-auto justify-between">
                                <button className="btn btn-accent rounded-lg btn-outline btn-wide btn-xl p-2 flex-1">
                                    <Pencil size={28}/> 
                                    Draw Containment
                                </button>
                                <button className="btn btn-accent rounded-lg btn-outline btn-wide btn-xl p-2 flex-1">
                                    <CirclePlay />
                                    RUN
                                </button>
                            </div>

                            {/* input variables */}
                            <div className="border border-carbon-stroke w-full rounded-2xl bg-carbon-side">
                                <div className="flex flex-col gap-3 p-2">
                                    <p className="text-sm uppercase tracking-wide text-text-muted font-semibold">Simulation Variables</p>

                                    <div className="grid grid-cols-3 gap-2">
                                        {/* Wind speed and direction */}
                                        <label className="flex gap-1 p-2">
                                            <span className="text-sm text-text-muted">Wind:</span>
                                            <input type="text" placeholder="wind speed" className="input input-accent input-xs w-full" />
                                            <select className="select select-xs select-accent w-full">
                                                <option>N</option>
                                                <option>W</option>
                                                <option>E</option>
                                                <option>S</option>
                                                <option>NW</option>
                                                <option>NE</option>
                                                <option>SE</option>
                                                <option>SW</option>
                                            </select>
                                        </label>
                                        {/* temperature */}
                                        <label className="flex gap-1 p-2">
                                            <span className="text-sm text-text-muted">Temperature:</span>
                                            <input type="text" placeholder="Temperature" className="input input-accent input-xs w-full" />
                                        </label>

                                        {/* humidity */}
                                        <label className="flex gap-1 p-2">
                                            <span className="text-sm text-text-muted">Humidity:</span>
                                            <input type="text" placeholder="Humidity" className="input input-accent input-xs w-full" />
                                        </label>

                                        {/* dryness */}
                                        <label className="flex gap-1 p-2">
                                            <span className="text-sm text-text-muted">Dryness:</span>
                                            <select className="select select-xs select-accent w-full">
                                                <option>Very High</option>
                                                <option>High</option>
                                                <option>Medium</option>
                                                <option>Low</option>
                                            </select>
                                        </label>
                                        
                                        {/* Auto Update Checkbox */}
                                        <label className="flex gap-1 p-2">
                                            <span className="text-sm text-text-muted">Auto Update:</span>
                                            <input type="checkbox" defaultChecked className="checkbox checkbox-sm rounded-lg" />
                                        </label>

                                        {/* Timeline slider */}
                                        <label className="flex flex-col gap-1 p-2 col-span-3">
                                            <span className="text-sm text-text-muted p-2">Timeline: {timeline} h</span>
                                            <div className="w-full">
                                                <input type="range" min={0} max="24" className="range range-xs w-full" step="0.5" value={timeline} onChange={(e) => setTimeline(Number(e.target.value))}/>
                                                <div className="flex justify-between px-2.5 mt-2 text-sm">
                                                    <span>0h</span>
                                                    <span>6h</span>
                                                    <span>12h</span>
                                                    <span>18h</span>
                                                    <span>24h</span>
                                                </div>
                                            </div>
                                        </label>

                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>

                    {/* Simulation results */}
                    <div className="basis-1/4 rounded-2xl bg-carbon-side border border-carbon-stroke overflow-y-auto">
                        <SimulationResults/>
                    </div>
                </div>
            </div>  
        </SideBarLayout>
    );
}