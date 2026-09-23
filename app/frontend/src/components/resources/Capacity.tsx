'use client';

import React, { useState } from 'react';
import { Alert } from '../shared/Alerts';

interface CapacityProps {
    readonly value: number;
    readonly unit: string;
    readonly min: number;
    readonly max: number;
    readonly step?: number;
    readonly label?: string;
    readonly helperText?: string;
    readonly error?: string;
    readonly onChange: (value: number) => void;
}

export function Capacity({ value, unit, min, max, step=1, label='Capacity', helperText = '', error = '', onChange, }: CapacityProps){
    const tickCount = 5;
    const ticks: number[] = [];
    for (let i = 0; i < tickCount; i++) {
        ticks.push(min + ((max - min) / (tickCount - 1)) * i);
    }

    const clamp = (n: number): number => Math.min(Math.max(n, min), max);
    const [draft, setDraft] = useState<string | null>(null);

    const commitDraft = (): void => {
        if (draft !== null) {
            onChange(Math.min(Math.max(Number(draft), min), max));
        }
        setDraft(null);
    }

    return (
        <div className='w-full'>
            <div className='flex items-baseline justify-between mb-2'>
                <h4>{label}</h4>
                <label className='flex items-center gap-2'>
                    <input type='number' inputMode='numeric' min={min} max={max} step={step} value={draft ?? value} onChange={(e) => setDraft(e.target.value)} onBlur={commitDraft} onKeyDown={(e) => { if (e.key === 'Enter') e.currentTarget.blur(); }} aria-label={`${label} in ${unit}`} className='input input-bordered bg-surface-input border-carbon-stroke input-xs w-24 text-left text-primary font-semibold focus:outline-primary text-lg'/>
                        <span className='text-primary font-bold text-lg'>{unit}</span>
                </label>
            </div>
            <input type='range' min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} className='range range-primary range-xs w-full' />

            <div className="flex w-full justify-between px-1 mt-1">
                {ticks.map((tick) => (
                        <span key={tick} className="text-[10px] text-text-muted">
                            {Math.round(tick).toLocaleString()}
                        </span>
                    ))}
            </div>

            {helperText && !error && (
                <p id="resource-capacity-helper" className="text-xs text-text-muted mt-2">
                    {helperText}
                </p>
            )}
            {error && <Alert variant="error" message={error} id="resource-capacity-error" />}
        </div>
    );
}