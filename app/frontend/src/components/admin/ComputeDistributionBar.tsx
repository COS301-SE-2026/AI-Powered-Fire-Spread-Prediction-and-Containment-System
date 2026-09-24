import React, { useEffect, useState } from 'react';


export interface ComputeDistributionData {
    active: number;
    busy: number;
    quarantined: number;
    offline: number;
    total: number;
}


interface ComputeDistributionProps {
    initialData: ComputeDistributionData;
    refreshIntervalMs?: number;
}


export const ComputeDistribution: React.FC<ComputeDistributionProps> = ({
    initialData,
    refreshIntervalMs = 10000,
}) => {
    const [data, setData] = useState<ComputeDistributionData>(
        initialData || {active: 30, busy: 30, quarantined: 5, offline: 7, total: 72,}
    );
    const [loading, setLoading] = useState<boolean>(!initialData);

    useEffect(() => {
        let isMounted = true;

        const fetchDistribution = async () => {
            try {
                const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;

                const res = await fetch(
                    `${apiBaseUrl}/api/v1/workers/calculate-distribution`,
                    {
                        method: 'GET',
                        credentials: 'include',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    }
                );

                if (res.ok) {
                    const json: ComputeDistributionData = await res.json();
                    if (isMounted) {
                        setData(json);
                        setLoading(false);
                    }
                }
            } catch {
                // keeps the last state it was in if something wrong
            }
        };

        fetchDistribution().catch(() => {});
        const interval = setInterval(fetchDistribution, refreshIntervalMs);

        return () => {
            isMounted = false;
            clearInterval(interval);
        };
    }, [refreshIntervalMs]);

    const total = data.total > 0 ? data.total : 1;
    const activeP = (data.active / total) * 100;
    const busyP = (data.busy / total) * 100;
    const quarantinedP = (data.quarantined / total) * 100;
    const offlineP = (data.offline / total) * 100;
    
    return (
        <section className='w-full rounded-box bg-base-200 border border-carbon-stroke p-6 text-base-content font-sans'>
            <h2 className='text-xl font-bold font-display tracking-tight text-white mb-4'>
                Computational Distribution
            </h2>

            <div className='w-full h-3 rounded-full bg-base-300 overflow-hidden flex items-center mb-6'>
                {data.total === 0 ? (
                    <div className='w-full h-full bg-base-100' />
                ) : (
                    <>
                        <div style={{ width: `${activeP}%` }} className='h-full bg-humidity transition-all duration-500 ease-out' title={`Active (Standby): ${data.active}`} />
                        <div style={{ width: `${busyP}%` }} className='h-full bg-wind transition-all duration-500 ease-out' title={`Busy (Computing): ${data.busy}`} />
                        <div style={{ width: `${quarantinedP}%` }} className='h-full bg-accent transition-all duration-500 ease-out' title={`Active (Standby): ${data.quarantined}`} />
                        <div style={{ width: `${offlineP}%` }} className='h-full bg-text-disabled transition-all duration-500 ease-out' title={`Active (Standby): ${data.offline}`} />
                    </>
                )}
            </div>

            <div className='flex flex-wrap items-start gap-8 sm:gap-12'>

                <div className='flex flex-col'>
                    <span className='text-3xl font-extrabold font-mono text-white leading-none'>
                        {loading ? '': data.active}
                    </span>
                    <div className='flex items-center gap-2 mt-2'>
                        <span className='w-2.5 h-2.5 rounded-full bg-humidity' />
                        <span className='text-sm font-medium text-text-muted'>
                            Active (Standby)
                        </span>
                    </div>
                </div>

                <div className='flex flex-col'>
                    <span className='text-3xl font-extrabold font-mono text-white leading-none'>
                        {loading ? '': data.busy}
                    </span>
                    <div className='flex items-center gap-2 mt-2'>
                        <span className='w-2.5 h-2.5 rounded-full bg-wind' />
                        <span className='text-sm font-medium text-text-muted'>
                            Busy (Computing)
                        </span>
                    </div>
                </div>

                <div className='flex flex-col'>
                    <span className='text-3xl font-extrabold font-mono text-white leading-none'>
                        {loading ? '': data.quarantined}
                    </span>
                    <div className='flex items-center gap-2 mt-2'>
                        <span className='w-2.5 h-2.5 rounded-full bg-accent' />
                        <span className='text-sm font-medium text-text-muted'>
                            Quarantined
                        </span>
                    </div>
                </div>

                <div className='flex flex-col'>
                    <span className='text-3xl font-extrabold font-mono text-white leading-none'>
                        {loading ? '': data.offline}
                    </span>
                    <div className='flex items-center gap-2 mt-2'>
                        <span className='w-2.5 h-2.5 rounded-full bg-text-disabled' />
                        <span className='text-sm font-medium text-text-muted'>
                            Offline
                        </span>
                    </div>
                </div>


            </div>
        </section>
    )
}