import type { SimProgress } from "@/hooks/useSimulationProgress";

const STAGES = [
    {stage: 'queued', label: 'Finding an available GPU', pct: 5},
    {stage: 'dispatched', label: 'Sending job to a volunteer GPU', pct: 10},
    {stage: 'received', label: 'Job picked up', pct: 15},
    {stage: 'fetching_weather', label: 'Fetching weather data', pct: 25},
    {stage: 'fetching_terrain', label: 'Fetching terrain and satellite data', pct: 45},
    {stage: 'running_model', label: 'Running fire spread model', pct: 80},
    {stage: 'packaging', label: 'Sending results', pct: 95},
] as const;

export function SimulationProgress({ progress }: {progress: SimProgress | null}) {
    const isCloud = progress?.stage === 'cloud';
    const index = STAGES.findIndex((s) => s.stage === progress?.stage);
    const current = index >= 0 ? STAGES[index] : null;
    const pct = isCloud ? 50 : current?.pct ?? 2;
    const label = isCloud ? 'Running on the cloud worker' : current?.label ?? 'Starting simulation';

    return (
        <div className='w-full max-w-sm flex flex-col gap-3 px-6'>
            <div className='flex items-baseline justify-between gap-3'>
                <span className='text-sm font-semibold text-text-primary'>{label}</span>
                <span className='text-sm font-mono text-text-muted'>{pct}%</span>
            </div>

            <div className='h-2 w-full rounded-full bg-carbon-stroke overflow-hidden'>
                <div
                    className={`h-full rounded-full bg-ignite transition-all duration-700 ease-out ${isCloud ? 'animate-pulse' : ''}`}
                    style={{ width: `${pct}%`}}
                />
            </div>

            {!isCloud && (
                <ol className='flex flex-col gap-1'>
                    {STAGES.map((s, i) => (
                        <li
                            key={s.stage}
                            className={`text-xs font-mono ${
                                i < index ? ' text-text-muted line-through decoration-ignite/30' : i === index ? 'text-ignite' : 'text-text-disabled'
                            }`}
                        >
                            {s.label}
                        </li>
                    ))}
                </ol>
            )}
        </div>  
    )
}