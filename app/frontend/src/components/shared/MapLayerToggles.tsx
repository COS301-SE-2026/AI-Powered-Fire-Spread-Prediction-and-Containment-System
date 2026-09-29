import { useEffect, useRef, useState } from 'react';
import { Layers, ChevronDown } from 'lucide-react';
import { LayerSwitch } from './LayerSwitch';

interface MapLayerTogglesProps {
    readonly showWater: boolean;
    readonly onToggleWater: () => void;
    readonly showResources: boolean;
    readonly onToggleResources: () => void;
    readonly pill?: boolean;
}

export function MapLayerToggles({
    showWater,
    onToggleWater,
    showResources,
    onToggleResources,
    pill = false,
}: MapLayerTogglesProps) {
    const [open, setOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const onPointerDown = (e: PointerEvent) => {
            if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
        };
        const onKey = (e: KeyboardEvent) => {
            if (e.key === 'Escape') setOpen(false);
        };
        document.addEventListener('pointerdown', onPointerDown);
        document.addEventListener('keydown', onKey);
        return () => {
            document.removeEventListener('pointerdown', onPointerDown);
            document.removeEventListener('keydown', onKey);
        };
    }, []);

    const pillClass = pill
        ? 'bg-carbon-bg/90 border border-carbon-card rounded-full px-3 py-1.5 shadow-lg backdrop-blur-sm'
        : '';

        return (
            <>
            {/* desktop: inline toggles */}
            <div className='hidden md:flex items-center gap-4'>
                <LayerSwitch label='Show Water' checked={showWater} onChange={onToggleWater} className={pillClass}/>
                <LayerSwitch label='Show Resources' checked={showResources} onChange={onToggleResources} className={pillClass} />
            </div>
            
            {/* Mobile/PWA: dropdown */}
            <div ref={ref} className='relative md:hidden'>
                <button
                    type='button'
                    aria-haspopup='true'
                    aria-expanded={open}
                    onClick={() => setOpen((o) => !o)}
                    className='flex items-center gap-1.5 rounded-full border border-carbon-card bg-carbon-bg/90 px-3 py-1.5 text-sm font-medium text-text-muted shadow-lg backdrop-blur-sm active:scale-95 transition'
                >
                    <Layers className='w-4 h-4' />
                    Layers
                    <ChevronDown className={`w-4 h-4 transition-transform ${open ? 'rotate-180' : ''}`}/>
                </button>

                {open && (
                    <div className='absolute right-0 top-full z-30 mt-2 flex w-52 flex-col gap-3 rounded-xl border border-carbon-card bg-carbon-side/95 p-3 shadow-2xl backdrop-blur-md'>
                        <LayerSwitch label='Show Water' checked={showWater} onChange={onToggleWater} className='justify-between' />
                        <LayerSwitch  label='Show Resources' checked={showResources} onChange={onToggleResources} className='justify-between'/>
                    </div>
                )}
            </div>
            </>
        );
}