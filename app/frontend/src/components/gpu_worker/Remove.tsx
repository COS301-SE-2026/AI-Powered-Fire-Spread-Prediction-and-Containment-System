import React, { useEffect, useRef, useState } from 'react';
import {X} from 'lucide-react';
import type { GPUWorker } from '../../types/GPUWorkers';

interface RemoveModalProps {
    readonly worker: GPUWorker;
    readonly variant: 'admin' | 'volunteer';
    readonly onClose: () => void;
    readonly onSubmit: (id: string, reason: string) => void;
}

export function RemoveModal({ worker, variant, onClose, onSubmit }: RemoveModalProps){
    const dialogRef = useRef<HTMLDialogElement>(null);
    const [reason, setReason] = useState('');
    const isRequired = variant === 'admin';
    const canSubmit = !isRequired || reason.trim().length > 0;

    useEffect(() => {
        dialogRef.current?.showModal();
    }, []);

    function handleClose() {
        dialogRef.current?.close();
    }

    function handleSubmit() {
        if (!canSubmit) {
            return;
        }
        onSubmit(worker.id, reason.trim());
        handleClose();
    }
    return (
        <dialog ref={dialogRef} data-testid='remove-worker-modal' onClose={onClose} className='modal'>
            <div className='modal-box bg-carbon-side border border-carbon-stroke rounded-lg p-4 max-w-md'>
                <div className='flex justify-between items-start mb-3'>
                    <h3 className='font-bold text-2xl text-text-primary'>
                        Remove {worker.label}
                    </h3>
                    <button type='button' onClick={handleClose} className='text-text-muted hover:text-text-primary'>
                        <X size={18}/>
                    </button>
                </div>
                <label className='text-base tracking-wide font-semibold text-text-primary mb-3' htmlFor='removal-reason'>
                    Reason for removal
                </label>
                <textarea id='removal-reason' value={reason} onChange={(e) => setReason(e.target.value)} rows={4} placeholder='Explain why this machine is being removed.' className='textarea w-full text-sm rounded-md border border-carbon-stroke bg-transparent placeholder:text-text-muted focus:border-primary focus:outline-none' />
                { isRequired ? (
                    <p className='text-sm text-text-muted mt-2'>Required before you can submit.</p>
                ):(
                    <p className='text-sm text-text-muted mt-2'>Optional.</p>
                )}
                <div className='mt-4 flex justify-end gap-2'>
                    <button type='button' onClick={handleClose} className='btn btn-sm btn-outline text-lg font-semibold rounded-md border-carbon-stroke text-text-muted hover:bg-smoke-hover'>
                        Cancel
                    </button>
                    <button type='button' disabled={!canSubmit} onClick={handleSubmit} className='btn btn-sm text-lg font-bold rounded-md bg-primary border-primary text-text-primary hover:bg-primary/90 disabled:opacity-40'>
                        Submit
                    </button>
                </div>
            </div>
        </dialog>
    );
}
