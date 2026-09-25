import React, { useState } from 'react';
import { X, Check } from 'lucide-react';
import { useDeviceCapability } from '../../hooks/useDeviceCapability';

interface JoinComputeGridPopUpProps {
    isOpen: boolean;
    onClose: () => void;
    onKeyGenerated?: () => void;
}

export const JoinComputeGridPopUp: React.FC<JoinComputeGridPopUpProps> = ({
    isOpen,
    onClose,
    onKeyGenerated,
}) => {
    const { osName, gpuName } = useDeviceCapability();
    const [machineLabel, setMachineLabel] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [step, setStep] = useState<'form' | 'instructions'>('form');
    const [dockerCommand, setDockerCommand] = useState<string>('');
    const [copiedCommand, setCopiedCommand] = useState(false);

    if (!isOpen) return null;

    const platformDisplay = osName ? `${osName} (desktop)` : 'Detecting platform...';

    const handleClose = () => {
        setStep('form');
        setError(null);
        setMachineLabel('');
        setCopiedCommand(false);
        onClose();
    };

    const handleGetSetupKey = async () => {
        setLoading(true);
        setError(null);

        const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || '';

        try {
            const response = await fetch(`${apiBaseUrl}/api/v1/workers/keys`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    label: machineLabel.trim() || 'Home desktop',
                    gpu_name: gpuName || 'Unknown GPU',
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const detail = errorData.detail;
                const message = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail[0].msg : undefined;
                throw new Error(message || 'Failed to issue setup key');
            }

            const data = await response.json();
            setDockerCommand(data.docker_command);
            setStep('instructions');

            if (onKeyGenerated) {
                onKeyGenerated(); 
            }
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Error generating key');
        } finally {
            setLoading(false);
        }
    };

    const handleCopy = async () => {
        if(!dockerCommand) return;
        try{
            await navigator.clipboard.writeText(dockerCommand);
            setCopiedCommand(true);
            setTimeout(() => setCopiedCommand(false), 2000);
        }catch{
            setError('Could not automatically copy the command, please copy it manually.');
        }
    };

    return (
        <div className='fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 font-body backdrop-blur-xs'>
            <div className='relative w-full max-w-md rounded-box border border-carbon-stroke bg-carbon-card p-6 shadow-2xl text-text-primary'>
                <button type="button" onClick={handleClose} aria-label="Close dialog"
                    className='absolute right-4 top-4 text-text-muted hover:text-text-primary transition-colors'
                >
                    <X className='size-5'/>
                </button>

                <h2 className='text-xl font-bold font-display tracking-wide text-text-primary mb-1'>
                    Join the compute grid
                </h2>
                <p className='text-sm text-text-muted mb-5'>
                    Set up this computer as a volunteer worker.
                </p>

                {error && (
                    <div className='mb-4 rounded-sm bg-danger/10 border border-danger/40 p-2.5 text-xs text-flare font-mono'>
                        {error}
                    </div>
                )}

                {step === 'form' ? (
                    <div className='space-y-4'>
                        <div>
                            <label className='block text-sm font-semibold text-text-primary mb-1.5'>
                                Detected platform
                            </label>
                            <input type="text" readOnly value={platformDisplay} tabIndex={-1}
                                className='w-full rounded-sm border border-carbon-stroke bg-carbon-input px-3.5 py-2.5 text-sm text-text-muted cursor-not-allowed select-none focus:outline-none'
                            />
                        </div>

                        <div>
                            <label className='block text-sm font-semibold text-text-primary mb-1.5 font-display'>
                                GPU
                            </label>
                            <div tabIndex={-1} title={gpuName} 
                                className='w-full rounded-sm border border-carbon-stroke bg-carbon-input px-3.5 py-2.5 text-sm text-text-muted cursor-not-allowed select-none resize-none focus:outline-none leading-relaxed'
                            >
                                {gpuName || 'Detecting GPU...'}
                            </div>
                        </div>

                        <div>
                            <label className='block text-sm font-semibold text-text-primary mb-1.5'>
                                Machine label
                            </label>
                            <input type="text" placeholder='e.g. Home desktop' value={machineLabel} maxLength={100} onChange={(e) => setMachineLabel(e.target.value)}
                                className='w-full rounded-sm border border-carbon-stroke bg-carbon-input px-3.5 py-2.5 text-sm text-text-primary placeholder:text-text-disabled focus:border-ignite focus:outline-none transition-colors'
                            />
                        </div>

                        <div className='flex items-center justify-end gap-3 pt-4 border-t border-carbon-stroke'>
                            <button type="button" onClick={handleGetSetupKey} disabled={loading}
                                className='min-h-[44px] px-4 py-2 rounded-sm bg-ignite hover:bg-flare active:bg-ember text-sm font-bold tracking-wide uppercase font-display text-white transition-colors disabled:opacity-50 cursor-pointer'
                            >
                                {loading ? 'Generating...' : 'Get setup key'}
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className='space-y-4'>
                        <p className='text-xs text-text-muted leading-relaxed'>
                            This key works once and expires in 24 hours. Run the command below on your machine.
                            <span className='block mt-1 text-text-disabled font-mono text-[11px]'>*Docker necessary</span>
                        </p>

                        <div>
                            <label className='block text-sm font-semibold text-text-primary mb-1.5 font-display'>
                                Docker command
                            </label>
                            <div className='relative rounded-sm border border-carbon-stroke bg-carbon-input p-3'>
                                <pre className='font-mono text-xs text-text-primary whitespace-pre-wrap break-all pr-16 select-all'>
                                    {dockerCommand}
                                </pre>
                                <button type="button" onClick={handleCopy}
                                    className='absolute right-3 top-3 rounded-box border border-carbon-stroke bg-[#1a2030] hover:bg-smoke-hover px-3 py-1 text-xs font-medium text-text-primary transition-colors cursor-pointer shrink-0'
                                >
                                    {copiedCommand ? (
                                        <span className='flex items-center gap-1 text-humidity'>
                                            <Check className="size-3.5" /> Copied
                                        </span>
                                    ) : (
                                        'Copy'
                                    )}
                                </button>
                            </div>
                        </div>

                        <div className='flex justify-end pt-3'>
                            <button type="button" onClick={handleClose}
                                className='min-h-[44px] px-6 py-2 rounded-box bg-ignite hover:bg-flare active:bg-ember text-sm font-bold tracking-wide uppercase font-display text-display transition-colors cursor-pointer shadow-md'
                            >
                                Done
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};