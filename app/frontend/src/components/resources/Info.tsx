'use client';

import React from 'react';
import { Alert } from '../shared/Alerts';

interface InfoProps {
    name: string;
    contact: string;
    nameError?: string;
    contactError?: string;
    onNameChange: (value: string) => void;
    onContactChange: (value: string) => void;
}

export function Info({ name, contact, nameError = '', contactError = '', onNameChange, onContactChange }: InfoProps){
    return (
        <div className="grid grid-cols-2 gap-3 w-full mb-1">
            <div className="w-full">
                <h4 className="p-1">Resource Name</h4>
                <input type="text" placeholder="e.g. Botha water trailer" className="input input-bordered w-full bg-surface-input border-carbon-stroke focus:outline-primary" value={name} onChange={(e) => onNameChange(e.target.value)} />
                {nameError && <Alert variant="error" message={nameError} id="resource-name-error" />}
            </div>
            <div className="w-full">
                <h4 className="p-1">Contact Number</h4>
                <input type="tel" value={contact} placeholder="e.g. 082 000 0000" className="input input-bordered w-full bg-surface-input border-carbon-stroke focus:outline-primary" onChange={(e) => onContactChange(e.target.value)} />
                {contactError && <Alert variant="error" message={contactError} id="resource-contact-error" />}
            </div>
        </div>
    );
}