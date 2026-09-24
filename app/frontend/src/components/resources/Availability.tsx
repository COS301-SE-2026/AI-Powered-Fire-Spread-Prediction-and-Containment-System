'use client';

import React from 'react';
import { Alert } from '../shared/Alerts';

interface Availibility {
    readonly availableFrom: string;
    readonly availableUntil: string;
}

interface AvailibilityProps {
    readonly value: Availibility;
    readonly error?: string;
    readonly onChange: (value: Availibility) => void;
}

function todayISO(): string {
    return new Date().toLocaleDateString('en-CA');
}

export function Availability({ value, error = '', onChange }: AvailibilityProps) {
    const availableFrom = value.availableFrom || todayISO();
    const isIndefinite = value.availableUntil === '';

    function handleIndefiniteToggle(e: React.ChangeEvent<HTMLInputElement>) {
        if (e.target.checked) {
            onChange({ availableFrom, availableUntil: '' });
        } else {
            onChange({ availableFrom, availableUntil: availableFrom });
        }
    }

    function handleFromChange(e: React.ChangeEvent<HTMLInputElement>){
        onChange({ ...value, availableFrom: e.target.value });
    }

    function handleUntilChange(e: React.ChangeEvent<HTMLInputElement>){
        onChange({ ...value, availableUntil: e.target.value })
    }

    return (
        <div className="w-full">
            <div className="flex items-center justify-between">
                <h4 className='p-1 mb-2'>Availability</h4>
                <label className="label cursor-pointer">
                    <span className="text-text-muted label-text text-xs">Infinity</span>
                    <input type="checkbox" className="toggle toggle-primary toggle-sm rounded-full before:rounded-full" checked={isIndefinite} onChange={handleIndefiniteToggle} />
                </label>
            </div>
            <div className="flex flex-col sm:flex-row gap-2">
                <div className='flex-1'>
                    <span className='label-text text-xs text-text-muted mb-1 block'>From</span>
                    <input type="date" value={availableFrom} onChange={handleFromChange} className='input input-bordered w-full bg-surface-input border-carbon-stroke focus:outline-ignite focus:border-none h-11' />
                </div>
                <div className='flex-1'>
                    <span className='label-text text-xs text-text-muted mb-1 block'>Until (optional)</span>
                    <input type='date' value={value.availableUntil} onChange={handleUntilChange} min={availableFrom || undefined} className="input input-bordered w-full bg-surface-input border-carbon-stroke focus:outline-ignite focus:border-none h-11" />
                </div>
            </div>
            {error && <Alert variant="error" message={error} id="resource-availability-error" />}
        </div>
    );
}