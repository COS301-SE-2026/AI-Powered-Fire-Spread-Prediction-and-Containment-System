import React, { useState } from 'react';
import { Plus } from 'lucide-react';
import { JoinComputeGridPopUp } from './JoinComputeGridPopUp';
import { useGPUWorkers } from '../../hooks/useGPUWorkers';
import { GpuWorkersTable } from './GPUTable';
import type { Status } from '../../types/GPUWorkers';
import { PageHeader } from '../layout/pageHeader';

export default function VolunteerPage() {
    const { workers, loading, error, refetch, activate, deactivate, remove } = useGPUWorkers();
    const [isAddModalGPUOpen, setIsAddGPUOpen] = useState(false);
    const filter: 'All' | Status = 'All';

    const handlCloseModal = () => {
        setIsAddGPUOpen(false);
        refetch()
    };

    if (loading) {
        return (
            <div className='p-6 font-body'>
                <PageHeader title="Your machines" subtitle="Lend your NVIDIA GPU to the compute grid while it is idle. Machines you add appear here." showIcons />
                <p className='text-error text-sm mt-4'>Loading...</p>
            </div>
        );
    }
    if (error) {
        return (
            <div className='p-6 font-body'>
                <PageHeader title="Your machines" subtitle="Lend your NVIDIA GPU to the compute grid while it is idle. Machines you add appear here." showIcons />
                <p className='text-error text-sm mt-4'>Failed to load GPU workers.</p>
            </div>
        );
    }

    return (
        <div className='p-6 font-body space-y-6'>
            <PageHeader title="Your machines" subtitle="Lend your NVIDIA GPU to the compute grid while it is idle. Machines you add appear here." showIcons />

            <div className='flex justify-end mb-6'>
                <button type="button" onClick={() => setIsAddGPUOpen(true)}
                    className='min-h-[44px] px-4 py-2 rounded-box bg-ignite hover:bg-flare active:bg-ember text-sm font-bold font-display uppercase tracking-wide text-white flex items-center gap-2 transition-colors cursor-pointer shrink-0 shadow-md'
                >
                    <Plus className='size-4' />
                    Add a machine
                </button>
            </div>

            <GpuWorkersTable workers={workers} filter={filter} variant="volunteer" onActivate={activate} onDeactivate={deactivate} onRemove={remove} />

            <JoinComputeGridPopUp isOpen={isAddModalGPUOpen} onClose={handlCloseModal} />
        </div>
    );
}