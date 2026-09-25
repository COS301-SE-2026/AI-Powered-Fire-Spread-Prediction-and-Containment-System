import React, { useState } from 'react';
import { useGPUWorkers } from '../../hooks/useGPUWorkers';
import { GpuWorkersTable } from './GPUTable';
import type { Status } from '../../types/GPUWorkers';
import { PageHeader } from '../layout/pageHeader';
import { StatusFilter } from '../shared/Filter';
import { SearchBar } from '../shared/Searchbar';

type WorkerFilter = 'All' | Status;
const WORKER_FILTERS: readonly WorkerFilter[] = ['All', 'active', 'busy', 'offline', 'quarantined', 'deactivated', 'rejected', 'removed',];

export default function GpuWorkersPage() {
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState<WorkerFilter>('All');
    const { workers, loading, error, refetch, activate, deactivate, remove } = useGPUWorkers(search);

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
           <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2 mb-4">
                <SearchBar value={search} placeholder="Search GPU workers" onChange={setSearch} />
                <StatusFilter<WorkerFilter> options={WORKER_FILTERS} filter={filter} onChange={setFilter} />
            </div>
            {loading && <p className='text-sm'>Loading...</p>}
            {!loading && (
                <GpuWorkersTable workers={workers} filter={filter} variant="admin" onActivate={activate} onDeactivate={deactivate} onRemove={remove} />
            )}
        </div>
    );
}