import React, { useEffect, useState } from "react";
import { X, Check } from 'lucide-react';
import { GPUWorker } from "../../types/GPUWorkers";

const START_COMMAND = 'docker start fireaway-worker';

function CommandBox({ command }: { command : string }){
    const [copied, setCopied] = useState(false);
    const copy = async () => {
        try {
            await navigator.clipboard.writeText(command);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch {
            {/* user can still select all */}
        }
    };

    return (
        <div className='relative rounded-sm border border-border-carbon-stroke bg-carbon-input p-3'>{command}
            <pre className='font-mono text-xs text-text-primary whitespace-pre-wrap break-all pr-16 select-all'>{command}</pre>
            <button
                type='button'
                onClick={copy}
                className='absolute right-3 top-3 rounded-box border border-carbon-stroke bg-[#1a2030] hover:bg-smoke-hover py-1 text-xs font-medium text-text-primary transition-colors'            
            >
                {copied ? <span className='flex items-center gap-1 text-humidity'><Check className='size-3.5'/> Copied</span>: 'Copy'}
            </button>
        </div>
    );
}

export function WorkerCommandModal({worker, onClose}: {worker: GPUWorker, onClose: () => void}) {
    const [runCommand, setRunCommand] = useState('');
    const [resetCommand, setResetCommand] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [resetting, setResetting] = useState(false);

    useEffect(() => {
        fetch(`/api/v1/workers/${worker.id}/command`, { credentials: 'include'})
        .then((res) => (res.ok ? res.json() : Promise.reject(new Error('Could not load command'))))
        .then((data) => setRunCommand(data.docker_command))
        .catch((err: Error) => setError(err.message));
    }, [worker.id])

    const handleReset = async () => {
        setResetting(true);
        setError(null);

        try {
            const res = await fetch(`/api/v1/workers/${worker.id}/reset-key`, { method: 'POST', credentials: 'include'});

            if(!res.ok) throw new Error('Could not reset credentials');
            const data = await res.json();
            setResetCommand(data.docker_command);
        } catch (err){
            setError(err instanceof Error ? err.message : 'Could not reset credentials');
        } finally {
            setResetting(false);
        }
    };

    return (
        <div className='fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 font-body backdrop-blur-xs'>
            <div className='relative w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-box border border-carbon-stroke bg-carbon-card p-6 shadow-2xl text-text-primary space-y-4'>
                <button
                    type='button'
                    onClick={onClose}
                    aria-label='Close modal'
                    className='absolute right-4 top-4 text-text-muted hover:text-text-primary'
                >
                    <X className='size-5'/>
                </button>
                <h2 className='text-xl font-bold font-display tracking-wide'>{worker.label}</h2>
                <p className='text-sm text-text-muted'>{worker.gpu_name}</p>
            </div>

            {error && <div className='rounded-sm bg-danger/10 border border-danger/40 p-2.5 text-xs text-flare font-mono'>{error}</div>}

            <div>
                <p className='text-sm font-semibold mb-1.5'>Start it again</p>
                <p className='text-xs text-text-muted mb-2'>If your computer was off or the worker stopped, run this:</p>
                <CommandBox command={START_COMMAND} />
            </div>

            {runCommand && (
                <div>
                    <p className='text-sm font-semibold mb-1.5'>Recreate the container</p>
                    <p className='text-xs text-text-muted mb-2'>If the container was deleted, run this. It reconnects using the credentials saved on your machine.</p>
                    <CommandBox command={runCommand} />
                </div>
            )}

            <div className='pt-4 border-t border-carbon-stroke'>
                <p className='text-sm font-semibold mb-1.5'>Still can't connect?</p>
                {resetCommand ? (
                    <>
                        <p className='text-xs text-text-muted mb-2'>
                            Remove the old container with <code className='font-mono'>docker rm -f fireaway-worker</code>, then run this new command. It works once and expires in 7 days.
                        </p>
                        <CommandBox command={resetCommand}/>                    
                    </>
                ) : (
                    <>
                        <p className='text-xs text-text-muted mb-2'>
                            Reset this machine's credentials to get a new setup command. The old credentials stop working.
                        </p>
                        <button
                            type='button'
                            onClick={handleReset}
                            disabled={resetting}
                            className='btn btn-sm btn-outline border-error/60 rounded-xl text-error hover:bg-error/10'
                        >
                            {resetting ? 'Resetting...' : 'Reset Credentials'}
                        </button>
                    </>
                )
            }
            </div>
        </div>
    );
}