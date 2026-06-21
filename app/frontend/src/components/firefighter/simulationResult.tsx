import { EnvironmentWidgets } from '../../components/firefighter/weatherStats';
import { LoggedContainmentLine } from './containmentLineCard';


export function SimulationResults () {
    const mockSpreadData = [
        {label: "1h", hectares: 6.2},
        {label: "3h", hectares: 11.4},
        {label: "6h", hectares: 16.1},
        {label: "12h", hectares: 18.1},
        {label: "24h", hectares: 38.2},
    ];

    

    const maxHectar = Math.max(...mockSpreadData.map(mx => mx.hectares));

    return (
        <div className="w-full shrink-0 flex flex-col gap-3 px-2 py-3 overflow-auto">
            {/* Simulation header */}
            <div>
                <h3 className="text-xs uppercase tracking-widest text-text-muted font-semibold">
                    Simulation - time area
                </h3>
                <p className="text-xs text-text-disabled">Last run 2 min ago · Auto Update</p>
            </div>

            {/* Weather conditions */}
            <div>
                <p className="text-sm uppercase py-2">weather inputs</p>
                <EnvironmentWidgets/>
            </div>

            {/* simulation results */}
            <div>
                <p className="text-sm uppercase py-2">predicted spread area</p>
                <div className="flex flex-col gap-2">
                    {mockSpreadData.map((data) => ( 
                        <div key={data.label} className="flex items-center gap-2">
                            <span className="text-xs text-text-muted w-8 shrink-0">{data.label}</span>
                            <div className='flex-1 h-2 rounded-full bg-carbon-stroke overflow-hidden'>
                                <div className="h-full rounded-full bg-ignite" style={{width: `${(data.hectares/maxHectar) * 100}%` }}/> {/* bar for results calculated by dividing max hectar from predicted fire by current times hectar estimate */}
                            </div>
                            <span className="text-xs text-text-primary shrink-0">{data.hectares} ha</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* logged containment lines */}
            <div>
                <p className="text-sm uppercase py-2">containment lines logged</p>
                <LoggedContainmentLine/>
            </div>
        </div>
    );
}