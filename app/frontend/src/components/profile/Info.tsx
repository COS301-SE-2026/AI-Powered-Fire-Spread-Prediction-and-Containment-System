'use client';

import React, { useState } from "react";
import type { UserResponse, UserUpdate } from "../../types/User";
import { useUpdateProfile } from "../../hooks/useUpdateProfile";

interface InfoProps {
    readonly user: UserResponse;
    readonly onUpdated: (user:UserResponse) => void;
}

function formatDate(createdAt: string): string{
    const date = new Date(createdAt);
    return date.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric'});
}

export function Info({ user, onUpdated }: InfoProps) {
    const { updateProfile } = useUpdateProfile();
    const [editing, setEditing] = useState(false);
    const [name, setName] = useState(user.name);
    const [surname, setSurname] = useState(user.surname);
    const [email, setEmail] = useState(user.email);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    function startEdit() {
        setName(user.name);
        setSurname(user.surname);
        setEmail(user.email);
        setError('');
        setEditing(true);
    }

    function cancelEdit() {
        setEditing(false);
        setError('');
    }

    async function handleSave() {
        setSaving(true);
        setError('');
        const payload: UserUpdate = { name, surname, email };
        try {
            const updated = await updateProfile(payload);
            onUpdated(updated);
            setEditing(false);
        } catch {
            setError('Failed to update profile');
        } finally {
            setSaving(false);
        }
    }

        if (!editing) {
            return (
                <div className="w-full rounded-2xl border border-carbon-stroke p-6 flex flex-col">
                    <h2 className='uppercase mb-3'>
                        Account Info
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-y-6 gap-x-8 mb-4">
                        <div>
                            <p className="uppercase text-text-muted font-bold text-sm">Full name</p>
                            <p className="text-text-primary font-semibold">{user.name} {user.surname}</p>
                        </div>
                        <div>
                            <p className="uppercase text-text-muted font-bold text-sm">Email</p>
                            <p className="text-text-primary font-semibold">{user.email}</p>
                        </div>
                        <div>
                            <p className="uppercase text-text-muted font-bold text-sm">Role</p>
                            <p className="text-text-primary font-semibold">{user.role}</p>
                        </div>
                        <div>
                            <p className="uppercase text-text-muted font-bold text-sm">Member since</p>
                            <p className="text-text-primary font-semibold">{formatDate(user.created_at)}</p>
                        </div>
                    </div>
                    <button type='button' onClick={startEdit} className="self-start text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors">Edit Info</button>
                </div>
            );
        }
        return (
            <div className="w-full rounded-2xl border border-carbon-stroke p-6 flex flex-col">
                <h2 className='uppercase mb-4'>Account Info</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                        <label className="block uppercase text-text-muted font-bold text-sm mb-2" htmlFor="account-name">Name</label>
                        <input id='account-name' className='input input-bordered w-full bg-surface-input border-carbon-stroke focus:outline-primary' value={name} onChange={(e) => setName(e.target.value)} />
                    </div>
                    <div>
                        <label className="block uppercase text-text-muted font-bold text-sm mb-2" htmlFor="account-name">Surname</label>
                        <input id='account-name' className='input input-bordered w-full bg-surface-input border-carbon-stroke focus:outline-primary' value={surname} onChange={(e) => setSurname(e.target.value)} />
                    </div>
                    <div className="md:col-span-2">
                        <label className="block uppercase text-text-muted font-bold text-sm mb-2" htmlFor="account-name">Email</label>
                        <input id='account-name' className='input input-bordered w-full bg-surface-input border-carbon-stroke focus:outline-primary' value={email} onChange={(e) => setEmail(e.target.value)} />
                    </div>
                </div>
                {error ? <p className="text-error text-xs mb-3">{error}</p> : null}
                <div className="flex gap-2">
                    <button type="button" onClick={handleSave} disabled={saving} className="text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors">{saving ? 'Saving...' : 'Save'}</button>
                    <button type="button" onClick={cancelEdit} disabled={saving} className="text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors">Cancel</button>
                </div>
            </div>
        );

}