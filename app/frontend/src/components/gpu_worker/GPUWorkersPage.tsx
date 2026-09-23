import React from 'react';
import { GpuWorkersTable } from './GPUTable';
import type { Status } from '../../types/GPUWorkers';
import { useGPUWorkers } from '@/hooks/useGPUWorkers';
import { PageHeader } from '../layout/pageHeader';

export default function GPUWorkersPage() {
    const { workers, loading, error, refetch, activate, deactivate, remove } = useGPUWorkers();
    const filter: 'All' | Status = 'All';

    if (loading) {
        return (
            <div className='p-6'>
                <PageHeader title="GPU workers" subtitle="Manage every machine currently connected to the compute grid." showIcons />
                <p className='text-error text-sm'>Loading...</p>
            </div>
        );
    }
    if (error) {
        return (
            <div className='p-6'>
                <PageHeader title="GPU workers" subtitle="Manage every machine currently connected to the compute grid." showIcons />
            </div>
        );
    }
    return (
        <div className='p-6'>
           <PageHeader title="GPU workers" subtitle="Manage every machine currently connected to the compute grid." showIcons />
            <GpuWorkersTable workers={workers} filter={filter} variant="admin" onActivate={activate} onDeactivate={deactivate} onRemove={remove} />
        </div>
    );
}