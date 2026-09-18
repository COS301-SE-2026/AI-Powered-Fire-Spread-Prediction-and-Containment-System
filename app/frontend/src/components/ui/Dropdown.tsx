'use client';

import React from 'react';
import { ChevronDown } from 'lucide-react';
import { useDropdown } from '../../hooks/useDropdown';

interface DropdownOption<T> {
    readonly value: T;
    readonly label: string;
};

interface DropdownProps<T> {
    readonly id: string;
    readonly value: T;
    readonly options: Array<DropdownOption<T>>;
    readonly onChange: (value: T) => void;
    readonly placeholder?: string;
    readonly error?: string;
}

export function Dropdown<T extends string>({ id, value, options, onChange, placeholder, error }: DropdownProps<T>) {
    const { open, setOpen, ref: containerRef } = useDropdown<HTMLDivElement>();
    const selected = options.find((opt) => opt.value === value);

    let buttonLabel: string;
    if (selected) {
        buttonLabel = selected.label;
    } else if (placeholder) {
        buttonLabel = placeholder;
    } else {
        buttonLabel = 'Select and option';
    }

    function handleSelect(opt: T){
        onChange(opt);
        setOpen(false);
    }

    return (
        <div ref={containerRef} className="form-control w-full relative">
            <div className={`dropdown w-full ${open ? 'dropdown-open' : ''}`}>
            <button type="button" id={id} className="btn w-full justify-between bg-carbon-input border-carbon-stroke font-normal"onClick={() => setOpen(!open)} aria-haspopup="listbox" aria-expanded={open}>
                {buttonLabel}
                <ChevronDown className={`w-4 h-4 text-text-muted transition-transform ${open ? 'rotate-180' : ''}`} />
            </button>
            { open && (
                <ul role="listbox" className="dropdown-content menu p-2 w-full mt-1 bg-carbon-elevated border border-carbon-stroke rounded-md shadow-lg z-50 block" style={{ display: 'block' }}>
                { options.map((opt) => (
                    <li key={opt.value} role="none">
                        <button type="button" role="option" aria-selected={opt.value === value} onClick={() => handleSelect(opt.value)} className={`w-full text-left p-2 rounded-md transition-colors ${opt.value === value ? 'bg-pimary text-primary-content' : 'hover:bg-carbon-stroke'}`}>
                            {opt.label}
                        </button>
                    </li>
                ))}
                </ul>
            )}
            </div>
            {error && <p className="text-error text-xs mt-1">{error}</p>}
        </div>
    );
}