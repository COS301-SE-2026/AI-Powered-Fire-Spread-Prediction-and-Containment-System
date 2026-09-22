import React from 'react';
import { GpuWorkersTable } from './GPUTable';
import type { Status } from '../../types/GPUWorkers';
import { useGPUWorkers } from '@/hooks/useGPUWorkers';
import { PageHeader } from '../layout/pageHeader';

export default function VolunteerPage() {
    const { workers, loading, error, refetch, activate, deactivate, remove } = useGPUWorkers();
    const filter: 'All' | Status = 'All';

    if (loading) {
        return (
            <div className='p-6'>
                <PageHeader title="Your machines" subtitle="Lend your NVIDIA GPU to the compute grid while it is idle. Machines you add appear here." showIcons />
                <p className='text-error text-sm'>Loading...</p>
            </div>
        );
    }
    if (error) {
        return (
            <div className='p-6'>
                <PageHeader title="Your machines" subtitle="Lend your NVIDIA GPU to the compute grid while it is idle. Machines you add appear here." showIcons />
                <p className='text-error text-sm'>Failed to load GPU workers.</p>
            </div>
        );
    }
    return (
        <div className='p-6'>
            <PageHeader title="Your machines" subtitle="Lend your NVIDIA GPU to the compute grid while it is idle. Machines you add appear here." showIcons />
            <GpuWorkersTable workers={workers} filter={filter} variant="volunteer" onActivate={activate} onDeactivate={deactivate} onRemove={remove} />
        </div>
    );
}