import React from 'react';
import Button from '../components/Button';

interface SystemAlertsPanelProps {
    isOpen: boolean;
    onClose: () => void;
}

export const SystemAlertsPanel: React.FC<SystemAlertsPanelProps> = ({ isOpen, onClose}) => {
    return (
        <>
            {/*for mobile when panel open*/}
            { isOpen && (
                <div className='fixed inset-0 bg-black/50 z-40 md:hidden' onClick={onClose} />
            )}

            {/*sliding alerts */}
            <div className={`fixed inset-y-0 right-0 z-50 bg-carbon-side shadow-2xl border-l border-carbon-card transform transition-transform duration-300 ease-in-out w-full md:w-1/3 flex-col
            $ { isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
                <div className='p-6 flex items-center justify-between border-b border-carbon-card'>
                    <h2 className='text-xl font-bold tracking-widest text-neutral uppercase'>
                        System Alerts
                    </h2>
                    <button onClick={onClose} className='text-neutral/50 hover:text-neutral transition-colors'>
                        Close
                    </button>
                </div>

                <div className='p-6 overflow-y-auto flex-1 flex flex-col gap-4'>
                    {/*place for notifications*/}
                    <div className='bg-carbon-card p-4 rounded-xl border border-red-500/30'>
                        <h3 className='text-red-500 font-bold mb-1'>
                            Verified Fire Alert
                        </h3>
                        <p className='text-sm text-neutrak/70 mb-2'>
                            Location: ...
                        </p>
                        <p className='text-sm text-neutrak/70 mb-2'>
                            Distance: ...
                        </p>
                        <p className='text-sm text-neutrak/70 mb-2'>
                            Severity: ...
                        </p>
                        <Button className='w-full text-xs'>
                            View on Map
                        </Button>
                    </div>                
                </div>
            </div>
        </>
    );
};