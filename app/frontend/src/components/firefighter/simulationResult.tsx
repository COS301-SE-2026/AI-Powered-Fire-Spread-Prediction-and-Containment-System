import React, { useEffect, useState } from 'react';
import { EnvironmentVariables, EnvironmentWidgets } from '../../components/firefighter/weatherStats';
import { LoggedContainmentLine } from './containmentLineCard';
import { TickStats, SimulationStatus } from './useSimulation';

interface SimulationResultsProps {
    currentStats?: TickStats | null;
    allStats?: TickStats[];
    status?: SimulationStatus;
}



export function SimulationResults ({currentStats, allStats = [], status='idle'}: SimulationResultsProps) {

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

    const spreadSample = allStats.filter((_, i) => i % 6 === 0);
    const maxBurning = Math.max(...spreadSample.map(s => s.burning), 1);

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
                    {status === 'playing' && `Tick ${currentStats?.tick ?? 0} - Playing`}
                    {status === 'paused' && `Tick ${currentStats?.tick ?? 0} - Paused`}
                    {status === 'error' && 'Simulation failed'}
                </p>
            </div>

            {/* Live burn stats for current tick */}
            {currentStats && (
                <div className='flex gap-3'>
                    <div className='flex flex-col'>
                        <span className='text-xs text-text-muted uppercase'>Burning</span>
                        <span className='text-sm font-semibold text-ignite'>
                            {currentStats.burning}
                                cells
                        </span>
                    </div>
                    <div className='flex flex-col'>
                        <span className='text-xs text-text-muted uppercase'>Buring</span>
                        <span className='text-sm font-semibold text-green-500/70'>
                            {currentStats.burned}
                                cells
                        </span>
                    </div>
                    <div className='flex flex-col'>
                        <span className='text-xs text-text-muted uppercase'>Unburned</span>
                        <span className='text-sm font-semibold text-green-500/70'>
                            {currentStats.total_cells - currentStats.burning - currentStats.burned}
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
                {allStats.length === 0 ? (
                    <p className='text-xs text-text-disabled'>Run the simulation to see spread data</p>
                ) : (
                    <div className="flex flex-col gap-2">
                    {spreadSample.map((data) => ( 
                        <div key={data.tick} className="flex items-center gap-2">
                            <span className="text-xs text-text-muted w-8 shrink-0">{data.tick}</span>
                            <div className='flex-1 h-2 rounded-full bg-carbon-stroke overflow-hidden'>
                                <div className="h-full rounded-full bg-ignite" style={{width: `${(data.burning/maxBurning) * 100}%` }}/> {/* bar for results calculated by dividing max hectar from predicted fire by current times hectar estimate */}
                            </div>
                            <span className="text-xs text-text-primary shrink-0">{data.burning} cells</span>
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