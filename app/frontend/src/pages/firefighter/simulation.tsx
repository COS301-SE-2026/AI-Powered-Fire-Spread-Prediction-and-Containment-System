import { useState } from 'react';
import { FirefighterSideBar } from '../../components/firefighter/firefighterSidebar';
import { SimulationResults } from '../../components/firefighter/simulationResult';
import { Pencil,CirclePlay, Pause, RotateCcw, AlertTriangle, Loader2 } from 'lucide-react';
import { FireMap } from '../../components/DynamicFiremap';
import { useContainmentLine } from '../../components/firefighter/useContainmentLine';
import { useSimulation } from '../../components/firefighter/useSimulation';

export default function ReportTable() {
    const [timeline, setTimeline] = useState(0);
    const default_location = { lat: -25.7479, lng: 28.2293}; // Pretoria
    const [drawMode, setDrawMode] = useState(false);
    const [userLocation] = useState(default_location);
    const [clearDrawings] = useState(0);
    const handleDrawComplete = useContainmentLine(() => setDrawMode(false));
    const {
        status,
        error,
        runSimulation,
        predictions,
        currentTick,
        seekToTick,
        play,
        pause,
        autoplay,
        setAutoPlay,
        totalTicks,
        gridH,
        gridW,
        weather,
        setWeather,
        staticParams, 
        setStaticParams,
        dcaParams,
        setDcaParams,
    } = useSimulation();

    const isLoading = status === 'loading';
    const isPlaying = status === 'playing';
    const hasResult = totalTicks > 0;

    function handleRun() {
        runSimulation(userLocation.lat, userLocation.lng, 48);  // n_steps = 2 ticks per hour x 24h
    }

    function handleReset(){
        seekToTick(0);
        pause();
    }

    const maxSlider = Math.max(totalTicks-1, 1);    // Timeline slider tracks currentTick when simulation is running. Manual drag seeks to specific task

    return (
        <FirefighterSideBar>
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

                                {/* Live tick badge */}
                                {hasResult && (
                                    <span className='text-xs font-mono text-ignite/80 bg-ignite/10 border border-ignite/30 px-2 py-1 rounded-md'>
                                        TICK {currentTick} / {totalTicks-1}
                                    </span>
                                )}
                            </div>

                            {/* Loading overlay */}
                            {isLoading && (
                                <div className='absolute inset-0 z-20 flex flex-col items-center justify-center bg-carbon-bg/70 backdrop-blur-sm gap-3'>
                                    <Loader2 className='animate-spin text-ignite' size={40} />
                                    <span className='text-neutral/70 text-sm font-mono uppercase tracking-widest'>
                                        Running Simulation...
                                    </span>
                                </div>
                            )}

                            {/* Error overlay */}
                            {status === 'error' && (
                                <div className='absolute inset-0 z-20 flex flex-col items-center justify-center bg-carbon-bg/80 backdrop-blur-sm gap-3 p-6'>
                                    <AlertTriangle className='text-red-400' size={36} />
                                    <p className='text-red-400 text-sm font-mono text-center max-w-xs'>
                                        {error ?? 'Simulation failed. Check the backend is running'}
                                    </p>
                                    <button 
                                        onClick={handleRun}
                                        className='btn btn-sm btn-outline text-neutral/70 mt-2'>
                                            Retry
                                    </button>
                                </div>
                            )}

                            <div className="w-full h-full"> 
                                <FireMap 
                                    lat={userLocation.lat} 
                                    lng={userLocation.lng}  
                                    drawMode={drawMode}
                                    onDrawComplete={handleDrawComplete} 
                                    clearDrawings={clearDrawings}
                                    burnGridH={gridH}
                                    burnGridW={gridW}
                                    predictions={predictions}
                                    currentTick={currentTick}/>
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

                                {/* Run/pause/resume button */}
                                {!hasResult || status === 'idle' || status === 'error' ? (
                                     <button
                                        onClick={handleRun}
                                        disabled={isLoading}
                                        className='btn btn-accent rounded-lg btn-outline btn-wide btn-xl p-2 flex-1 disabled-opacity-50'>
                                            {isLoading ? <Loader2 className='animate-spin' size={24} /> : <CirclePlay size={24} />}
                                            {isLoading ? 'Running...' : 'RUN'}
                                    </button>
                                ) : isPlaying ? (
                                    <button onClick={pause} className='btn btn-accent rounded-lg btn-outline btn-wide btn-xl p-2 flex-1'>
                                        <Pause size={24} />
                                        Pause
                                    </button>
                                ) : (
                                    <div className='flex gap-2 flex-1'>
                                        <button onClick={play} className='btn btn-accent rounded-lg btn-outline btn-xl p-2 flex-1'>
                                            <CirclePlay size={22} />
                                            Resume
                                        </button>
                                        <button onClick={handleRun} className='btn btn-outline rounded-lg btn-xl p-2 flex-1 text-neutral/60' title='Re-run simulation'>
                                            <RotateCcw size={18} />
                                        </button>
                                    </div>
                                )}
                               

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
                                                <span className="text-sm text-text-muted p-1">
                                                    {hasResult ? `Tick ${currentTick} of ${totalTicks-1}` : 'Not yet run'}
                                                </span>
                                                {/* Auto Update Checkbox */}
                                                <label className="flex gap-1 p-2">
                                                    <span className="text-sm text-text-muted">Auto Play:</span>
                                                    <input type="checkbox" checked={autoplay} onChange={(e) => setAutoPlay(e.target.checked)} className="checkbox checkbox-sm rounded-lg" />
                                                </label>
                                            </div>
                                        
                                        <div className="w-full">
                                            <input 
                                                type="range" 
                                                min={0} 
                                                max="sliderMax"
                                                step={1}
                                                className="range range-xs w-full disabled:opacity-30" 
                                                value={currentTick} 
                                                disabled={!hasResult}
                                                onChange={(e) => seekToTick(Number(e.target.value))}/>

                                            <div className="flex justify-between px-2.5 mt-2 text-sm">
                                                <span>{Math.round(maxSlider/4)}h</span>
                                                <span>{Math.round(maxSlider/2)}h</span>
                                                <span>{Math.round(maxSlider*3/4)}h</span>
                                                <span>{maxSlider}h</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Weather inputs */}
                                    <div className='border-t border-carbon-stroke/40 pt-3'>
                                        <p className='text-xs uppercase tracking-wide text-text-muted/60 font-semibold mb-2'>
                                            Weather Params
                                        </p>
                                        <div className='grid grid-cols-2 gap-2'>
                                            <label className='flex flex-col gap-1'>
                                                <span className='text-xs text-text-muted'> Wind U (m/s)</span>
                                                <input 
                                                    type='number'
                                                    step={0.5}
                                                    value={weather.wind_u}
                                                    onChange={(e) => setWeather({ ...weather, wind_u: Number(e.target.value)})}
                                                    className='input input-sm input-bordered rounded-lg bg-carbon-bg text-neutral w-full' />
                                            </label>
                                            <label className='flex flex-col gap-1'>
                                                <span className='text-xs text-text-muted'>Wind V (m/s)</span>
                                                <input 
                                                    type='number'
                                                    step={0.5}
                                                    value={weather.wind_v}
                                                    onChange={(e) => setWeather({ ...weather, wind_v: Number(e.target.value)})}
                                                    className='input input-sm input-boardered rounded-lg bg-carbon-bg text-neutral w-full'/>
                                            </label>
                                            <label className='flex flex-col gap-1'>
                                                <span className='text-xs text-text-muted'>Humidity (%)</span>
                                                <input
                                                    type='number'
                                                    step={1}
                                                    min={0}
                                                    max={100}
                                                    value={weather.rel_humidity}
                                                    onChange={(e) => setWeather({ ...weather, rel_humidity: Number(e.target.value)})}
                                                    className='input input-sm input-boardered rounded-lg bg-carbon-bg rext-neutral w-full' />
                                            </label>
                                            <label className='flex flex-col gap-1'>
                                                <span className='text-xs text-text-muted'>Temp (degrees celcius)</span>
                                                <input 
                                                    type='number'
                                                    step={1}
                                                    value={weather.temperature}
                                                    onChange={(e) => setWeather({ ...weather, temperature: Number(e.target.value)})}
                                                    className='input input-sm input-boardered rounded-lg bg-carbon-bg text-netral w-full' />
                                            </label>
                                        </div>
                                    </div>

                                    {/* Fuel Params */}
                                    <div className='border-t boarder-carbon-stroke/40 pt-3'>
                                        <p className='text-xs uppercase tracking-wide text-text-muted/60 font-semibold mb-2'>
                                            fuel Conditions
                                        </p>
                                        <div className='grid grid-col-2 gap-2'>
                                            <label className='flex flex-col gap-1'>
                                                <span className='text-xs text-text-muted'>
                                                    Fuel Load: {staticParams.fuel_load.toFixed(2)}
                                                </span>
                                                <input 
                                                    type='range'
                                                    min={0}
                                                    max={1}
                                                    step={0.05}
                                                    value={staticParams.fuel_load}
                                                    onChange={(e) => setStaticParams({ ...staticParams, fuel_load: Number(e.target.value)})}
                                                    className='range range-xs w-full' />
                                            </label>
                                            <label className='flex flex-col gap-1'>
                                                <span className='text-xs text-text-muted'>
                                                    Dryness: {staticParams.dryness.toFixed(2)}
                                                </span>
                                                <input 
                                                    type='range'
                                                    min={0}
                                                    max={1}
                                                    step={0.05}
                                                    value={staticParams.dryness}
                                                    onChange={(e) => setStaticParams({ ...staticParams, dryness: Number(e.target.value)})}
                                                    className='range range-xs w-full' />
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Simulation results */}
                    <div className="basis-1/4 rounded-2xl bg-carbon-side border border-carbon-stroke overflow-y-auto">
                        <SimulationResults
                        // Pass live stats so panel can show burning/burned counts per tick
                        predictions={predictions}
                        currentTick={currentTick}
                        status={status}/>
                    </div>
                </div>
            </div>  
        </FirefighterSideBar>
    );
}