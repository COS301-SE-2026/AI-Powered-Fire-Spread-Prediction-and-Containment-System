import { useState } from 'react';
import { FirefighterSideBar } from '../../components/firefighter/firefighterSidebar';
import { SimulationResults } from '../../components/firefighter/simulationResult';
import { Pencil,CirclePlay } from 'lucide-react';
import { FireMap } from '../../components/DynamicFiremap';
import { useContainmentLine } from '../../components/firefighter/useContainmentLine';

export default function ReportTable() {
    const [timeline, setTimeline] = useState(0);
    const default_location = { lat: -25.7479, lng: 28.2293}; // Pretoria
    const [drawMode, setDrawMode] = useState(false);
    const [userLocation] = useState(default_location);
    const [clearDrawings] = useState(0);
    const handleDrawComplete = useContainmentLine(() => setDrawMode(false));

    return (
        <FirefighterSideBar>
            <div className="p-4 flex flex-col h-full w-full gap-y-3">

                {/*Page header and subtitle*/}
                <header className="mb-6">
                    <h1 className="text-page-title font-display font-bold tracking-wider text-text-primary uppercase">Fire Simulation</h1>
                    <p className="font-body text-body text-text-primary/50">Simulate fire spread and prevention methods</p>
                </header>

                <div className="flex flex-row gap-4 min-w-0">

                    {/* left side of page: map + controls and buttons*/}
                    <div className="basis-3/4 flex flex-col gap-4">
                        {/* Fire Map */}
                        <div className="rounded-2xl bg-carbon-side/80 border border-carbon-stroke backdrop-blur-sm shadow-2xl shadow-black/20 h-[70vh] overflow-hidden relative">
                            <div className="p-4 border-b border-carbon-card bg-carbon-bg/50 backdrop-blur-md absolute top-0 w-full z-10 flex justify-between items-center border-l-2 border-l-ignite/60">
                                <span className="font-bold text-lg tracking-wide text-text-primary/80 uppercase">LIVE FIRE MAP</span>
                            </div>
                            <div className="w-full h-full">
                                <FireMap lat={userLocation.lat} lng={userLocation.lng}  drawMode={drawMode} onDrawComplete={handleDrawComplete} clearDrawings={clearDrawings}/>
                            </div>
                        </div>

                        {/* simulation vars and buttons */}
                        <div className="flex gap-2 items-stretched">
                            {/* buttons to start simulation or draw page */}
                            <div className="flex flex-col gap-6 shrink-0 h-auto justify-between">
                                <button type="button" onClick={() => setDrawMode(true)} className="btn btn-accent rounded-lg btn-outline btn-wide btn-xl p-2 flex-1">
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
                                    <p className="text-sm uppercase tracking-wide text-text-muted font-semibold">Simulation Timeline</p>

                                        {/* Timeline slider */}
                                        <div className="flex flex-col gap-1 p-2">
                                            <div className="flex flex-row items-center justify-between">
                                                <span className="text-sm text-text-muted p-2">Timeline: {timeline} h</span>
                                                {/* Auto Update Checkbox */}
                                                <label className="flex gap-1 p-2">
                                                    <span className="text-sm text-text-muted">Auto Update:</span>
                                                    <input type="checkbox" defaultChecked className="checkbox checkbox-sm rounded-lg" />
                                                </label>
                                            </div>

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
        </FirefighterSideBar>
    );
}