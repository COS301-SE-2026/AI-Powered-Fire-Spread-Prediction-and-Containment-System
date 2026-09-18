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
    readonly onChange: (value: Resource) => void;
    readonly onChangeOther: (value: string) => void;
    readonly error?: string;
}

export function ResourceDropdown({ value, other, onChange, onChangeOther, error }: ResourceDropdownProps) {
    return (
        <>
            <Dropdown id="resource-type" value={value} options={RESOURCE_TYPES} onChange={onChange} error={error} />
            {value === 'other' && (
                <input type="text" placeholder='Describe the resource' className='input w-full bg-carbon-input border-carbon-stroke mt-2' value={other} onChange={(e) => onChangeOther(e.target.value)} />
            )}
        </>
    );
}