import { RotateCw, X } from 'lucide-react';

interface RotateHintProps {
    readonly show: boolean;
    readonly onDismiss: () => void;
}

export function RotateHint({ show, onDismiss }: RotateHintProps){
    if (!show){
        return null;
    }
    return (
        <div className='z-40 md:hidden'>
            <div className='bg-info/15 border border-info/50 rounded-xl px-4 py-3 flex items-center justify-start gap-3'>
                <RotateCw className='w-5 h-5 text-info rotate-90 shrink-0' />
                <span className='text-xs text-info flex-1'>
                    Rotate device
                </span>
                <button type='button' onClick={onDismiss} className='text-info shrink-0'>
                    <X className='w-4 h-4' />
                </button>
            </div>
        </div>
    );
}
