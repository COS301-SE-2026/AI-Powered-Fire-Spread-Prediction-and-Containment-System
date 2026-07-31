import React, { useEffect, useState } from 'react';
import { EnvironmentVariables, EnvironmentWidgets } from '../../components/firefighter/weatherStats';
import { LoggedContainmentLine } from './containmentLineCard';
import { Prediction, SimulationStatus } from './useSimulation';

interface SimulationResultsProps {
    predictions?: Prediction[];
    currentTick?: number;
    status?: SimulationStatus;
}

function countStates(grid: number[] | undefined) {
    if (!grid) return {burning: 0, burned: 0, unburned: 0, total: 0}
    let burning = 0, burned = 0;
    for (const cell of grid){
        if (cell == 1) burning++;
        else if(cell == 2) burned++;
    }
    return { burning, burned, unburned: grid.length - burning - burned, total: grid.length};
}


export function SimulationResults ({predictions = [], currentTick = 0,status='idle'}: SimulationResultsProps) {

    const default_location = { lat: -25.7479, lng: 28.2293}; // Pretoria
    const [userLocation, setUserLocation] = useState(default_location);
    const [environmentVariables, setEnvironmentVariables] = useState<EnvironmentVariables | null>(null);

    useEffect (() => {
            if(!navigator.geolocation){ // if user does not allow location return default location on map
                return;
            }
    
            // if users location permissions accepted set lat and lng to users location 
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    setUserLocation({
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                    });
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
                        
                        setEnvironmentVariables(null);
                        return;
                    }
                    const data = await resp.json();
                    setEnvironmentVariables(data.environment_variables ?? null);
                } catch(error){
                    if(error.name === 'AbortError') return; // this request is superseded by a newer request
                    console.error("Was unable to find/retrieve dashboard data", error);
                    setEnvironmentVariables(null);
                }
            };
            fetchRequest();
            return () => fetchController.abort(); // this will cancel the fetch if the users location again changes before it is resolved
        }, [userLocation]);

    const totals = predictions.reduce(
        (acc, p) => {
            const c = countStates(p.history[currentTick]);
            return{
                burning: acc.burning + c.burning,
                burned: acc.burned + c.burned,
                unburned: acc.unburned + c.unburned,
            }
        },
        {burning: 0, burned: 0, unburned: 0}
    );

    const hasResult = predictions.length > 0;
    const maxBurned = Math.max(...predictions.map(p => p.burned_cells), 1);

    return (
        <div className="w-full shrink-0 flex flex-col gap-3 px-2 py-3 overflow-auto">
            {/* Simulation header */}
            <div>
                <h3 className="text-xs uppercase tracking-widest text-text-muted font-semibold">
                    Simulation - time area
                </h3>
                <p className="text-xs text-text-disabled">
                    {status === 'idle' && 'Not yet run'}
                    {status === 'loading' && 'Running simulation...'}  
                    {status === 'playing' && `Tick ${currentTick} - Playing`}
                    {status === 'paused' && `Tick ${currentTick} - Paused`}
                    {status === 'error' && 'Simulation failed'}
                </p>
            </div>

            {/* Live burn stats for current tick */}
            {hasResult && (
                <div className='flex gap-3'>
                    <div className='flex flex-col'>
                        <span className='text-xs text-text-muted uppercase'>Burning</span>
                        <span className='text-sm font-semibold text-ignite'>
                            {totals.burning}
                                cells
                        </span>
                    </div>
                    <div className='flex flex-col'>
                        <span className='text-xs text-text-muted uppercase'>Burning</span>
                        <span className='text-sm font-semibold text-green-500/70'>
                            {totals.burned}
                                cells
                        </span>
                    </div>
                    <div className='flex flex-col'>
                        <span className='text-xs text-text-muted uppercase'>Unburned</span>
                        <span className='text-sm font-semibold text-green-500/70'>
                            {totals.unburned}
                                cells
                        </span>
                    </div>
                </div>
            )}

            {/* Weather conditions */}
            <div>
                <p className="text-sm uppercase py-2">weather inputs</p>
                <EnvironmentWidgets variables={environmentVariables}/>
            </div>

            {/* simulation results */}
            <div>
                <p className="text-sm uppercase py-2">predicted spread area</p>
                {!hasResult ? (
                    <p className='text-xs text-text-disabled'>Run the simulation to see spread data</p>
                ) : (
                    <div className="flex flex-col gap-2">
                    {predictions.map((p) => ( 
                        <div key={p.ref} className="flex items-center gap-2">
                            <span className="text-xs text-text-muted w-8 shrink-0">{p.ref.slice(0.8)}</span>
                            <div className='flex-1 h-2 rounded-full bg-carbon-stroke overflow-hidden'>
                                <div className="h-full rounded-full bg-ignite" style={{width: `${(p.burned_cells / maxBurned) * 100}%` }}/> {/* bar for results calculated by dividing max hectar from predicted fire by current times hectar estimate */}
                            </div>
                            <span className="text-xs text-text-primary shrink-0">{(p.radius_m / 1000).toFixed(1)} km</span>
                        </div>
                    ))}
                </div>
                )}
                
            </div>

            {/* logged containment lines */}
            <div>
                <p className="text-sm uppercase py-2">containment lines logged</p>
                <LoggedContainmentLine/>
            </div>
        </div>
    );
}