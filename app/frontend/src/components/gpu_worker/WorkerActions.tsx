import React from 'react';
import type { GPUWorker } from '../../types/GPUWorkers';

interface WorkerActionsProps {
  worker: GPUWorker;
  onActivate: (id: string) => void;
  onDeactivate: (id: string) => void;
  onRemove: (worker: GPUWorker) => void;
}

export function WorkerActions({ worker, onActivate, onDeactivate, onRemove }: WorkerActionsProps) {
  if (worker.status === 'removed'){
    return <span className='text-xs text-text-muted'>No actions</span>
  }
  const removeButton = (
    <button type='button' onClick={() => onRemove(worker)} className='text-xs font-semibold btn btn-sm btn-outline border-error/60 rounded-xl text-error hover:bg-error/10 hover:text-error transition-colors'>
      Remove
    </button>
  );
  if (worker.status === 'deactivated'){
    return (
      <div className='flex gap-2'>
        <button type='button' onClick={() => onActivate(worker.id)} className='text-xs font-semibold btn btn-sm btn-outline border-text-primary rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors w-21'>
          Activate
        </button>
        {removeButton}
      </div>
    );
  }
  if (worker.status === 'quarantined' || worker.status === 'offline' || worker.status === 'rejected'){
    return (
        <div className='flex gap-2'>
            <button type='button' onClick={() => onActivate(worker.id)} className='text-xs font-semibold btn btn-sm btn-outline border-text-primary rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors invisible pointer-events-none'>
                Deactivate
            </button>
            {removeButton}
        </div>
    );
  }
  return (
    <div className='flex gap-2'>
      <button type='button' onClick={() => onDeactivate(worker.id)} className='text-xs font-semibold btn btn-sm btn-outline border-text-primary rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors'>
        Deactivate
      </button>
      {removeButton}
    </div>
  );
}