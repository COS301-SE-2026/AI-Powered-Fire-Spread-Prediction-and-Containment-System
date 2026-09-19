'use client';

import React from 'react';
import type { Resource } from '../../types/Resource';
import { Dropdown } from '../ui/Dropdown';

const RESOURCE_TYPES:{ value: Resource; label: string } [] = [
    { value: 'water_tank', label: 'Water Tank' },
    { value: 'borehole', label: 'Borehole' },
    { value: 'trailer', label: 'Trailer' },
    { value: 'dam', label: 'Dam' },
    { value: 'aircraft', label: 'Aircraft' },
    { value: 'crew', label: 'Crew' },
    { value: 'other', label: 'Other' },
];

interface ResourceDropdownProps{
    readonly value: Resource;
    readonly other: string;
    readonly otherCapacity: string;
    readonly onChange: (value: Resource) => void;
    readonly onChangeOther: (value: string) => void;
    readonly onChangeOtherCapacity: (value: string) => void;
    readonly error?: string;
}

export function ResourceDropdown({ value, other, otherCapacity, onChange, onChangeOther, onChangeOtherCapacity, error = ''}: ResourceDropdownProps) {
    return (
        <>
            <Dropdown id="resource-type" value={value} options={RESOURCE_TYPES} onChange={onChange} error={error} />
            {value === 'other' && (
                <div className='grid grid-cols-2 gap-3 w-full mb-1 mt-2'>
                    <div className='w-full'>
                        <h4 className='p-1'>Resource Name</h4>
                        <input type="text" placeholder='e.g. Diesel generator' className='input input-bordered w-full bg-surface-input border-carbon-stroke focus:outline-primary' value={other} onChange={(e) => onChangeOther(e.target.value)} />
                    </div>
                    <div className='w-full'>
                        <h4 className='p-1'>Capacity Unit</h4>
                        <input type="text" placeholder='e.g. liters, boxes, units' className='input input-bordered w-full bg-surface-input border-carbon-stroke focus:outline-primary' value={otherCapacity} onChange={(e) => onChangeOtherCapacity(e.target.value)} />
                    </div>
                </div>
            )}
        </>
    );
}