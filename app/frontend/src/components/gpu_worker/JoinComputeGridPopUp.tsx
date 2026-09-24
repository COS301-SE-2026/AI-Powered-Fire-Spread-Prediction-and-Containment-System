import React, { useState } from 'react';
import { X } from 'lucide-react';
import { useDeviceCapability } from '../../hooks/useDeviceCapability';

interface JoinComputeGridPopUpProps {
    isOpen: boolean;
    onClose: () => void;
    onKeyGenerated?: (keyData: { registrationKey: string; dockerCommand: string }) => void;
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

    if (!isOpen) return null;

    const platformDisplay = osName ? `${osName} (desktop)` : 'Detecting platform...';

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
                    gpu_name: gpuName,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Failed to issue setup key');
            }

            const data = await response.json();
            if (onKeyGenerated) {
                onKeyGenerated({
                    registrationKey: data.registration_key,
                    dockerCommand: data.docker_command,
                }); 
            }
            onClose();
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Error generating key');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className='fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 font-body backdrop-blur-xs'>
            <div className='relative w-full max-w-md rounded-box border border-carbon-stroke bg-carbon-card p-6 shadow-2xl text-text-primary'>
                <button type="button" onClick={onClose} aria-label="Close dialog"
                    className='absolute right-4 top-4 text-text-muted hover:text-text-primary transition-colors'
                >
                    <X className='size-5'/>
                </button>

                <h2 className='text-xl font-bold font-display tracking-wide text-text-primary mb-1'>
                    Join the compute grid!
                </h2>
                <p className='text-sm text-text-muted mb-5'>
                    Set up this computer as a volunteer worker.
                </p>

                {error && (
                    <div className='mb-4 rounded-sm bg-danger/10 border border-danger/40 p-2.5 text-xs text-flare font-mono'>
                        {error}
                    </div>
                )}

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
                        <input type="text" placeholder='e.g. Home desktop' value={machineLabel} onChange={(e) => setMachineLabel(e.target.value)}
                            className='w-full rounded-sm border border-carbon-stroke bg-carbon-input px-3.5 py-2.5 text-sm text-texxt-primary placeholder:text-text-disabled focus:border-ignite focus:outline-none transition-colors'
                        />
                    </div>

                    <div className='flex items-center justify-end gap-3 pt-4 border-t border-carbon-stroke'>
                        <button type="button" onClick={onClose}
                            className='min-h-[44px] px-4 py-2 rounded-sm bg-ignite hover:bg-flare active:bg-ember text-sm font-bold tracking-wide uppercase font-display text-white transition-colors disabled:opacity-50'
                        >
                            {loading ? 'Generating...' : 'Get setup key'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};