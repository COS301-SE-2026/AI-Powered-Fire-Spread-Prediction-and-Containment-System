'use client';

import React, { useState } from 'react';
import type { Status } from '../../types/Resource';
import { Dropdown } from '../ui/Dropdown';

const STATUS_OPTIONS: Array<{ value: Status; label: string }> = [
  { value: 'available', label: 'Available' },
  { value: 'dispatched', label: 'Dispatched' },
  { value: 'unavailable', label: 'Unavailable' },
];

interface ResourceDropdownProps{
    readonly id: string;
    readonly status: Status;
    readonly onStatusChange: (id: string, status: Status) => void;
}

export function ResourceDropdown({id, status, onStatusChange, }: ResourceDropdownProps) {
    const [pending, setPending] = useState(false);
    const [error, setError] = useState('');

    async function handleChange(next: Status) {
        setPending(true);
        setError('');
        try {
            await onStatusChange(id, next);
        } finally {
            setPending(false);
        }
    }    
    return (
        <Dropdown<Status> id={`resource-status-${id}`} value={status} options={STATUS_OPTIONS} onChange={handleChange} error={error} />
    );
}