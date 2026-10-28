'use client';

import React, { useEffect, useState } from "react";
import type { UserResponse, UserUpdate } from "../../types/User";
import { useUpdateProfile } from "../../hooks/useUpdateProfile";
import { useEditPassword } from "../../hooks/useEditPassword";
import PasswordInput from "../shared/PasswordInput";
import { Alert } from "../shared/Alerts";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

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
    const { editPassword } = useEditPassword();
    const [editing, setEditing] = useState(false);
    const [name, setName] = useState(user.name);
    const [surname, setSurname] = useState(user.surname);
    const [email, setEmail] = useState(user.email);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    const [changingPassword, setChangingPassword] = useState(false);
    const [current, setCurrent] = useState('');
    const [next, setNext] = useState('');
    const [confirm, setConfirm] = useState('');
    const [pwError, setPwError] = useState('');
    const [pwSaving, setPwSaving] = useState(false);
    const [pwDone, setPwDone] = useState(false);
    const [infoDone, setInfoDone] = useState(false);

    useEffect(() => {
        if (!pwDone) {
            return;
        }
        const timer = setTimeout(() => setPwDone(false), 4000);
        return () => clearTimeout(timer);
    }, [pwDone]);

    useEffect(() => {
        if (!infoDone) {
            return;
        }
        const timer = setTimeout(() => setInfoDone(false), 4000);
        return () => clearTimeout(timer);
    }, [infoDone]);

    function startEdit() {
        setName(user.name);
        setSurname(user.surname);
        setEmail(user.email);
        setError('');
        setPwDone(false);
        setEditing(true);
    }

    function cancelEdit() {
        setEditing(false);
        setError('');
    }

    function openPassword() {
        setPwDone(false);
        setInfoDone(false);
        setChangingPassword(true);
    }

    function closePassword(){
        setChangingPassword(false);
        setCurrent('');
        setNext('');
        setConfirm('');
        setPwError('');
    }

    async function handleSave() {
        if (!name.trim() || !surname.trim()) {
            setError('Name and surname are required');
            return;
        }

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            setError('Enter a valid email address');
            return;
        }

        setError('');
        setSaving(true);
        const payload: UserUpdate = { name, surname, email };
        try {
            const updated = await updateProfile(payload);
            onUpdated(updated);
            setEditing(false);
            setInfoDone(true);
        } catch {
            setError('Failed to update profile');
        } finally {
            setSaving(false);
        }
    }

    async function handlePasswordSave() {
        setPwSaving(true) ;
        setPwError ('');
        try {
            await editPassword(current, next, confirm); 
            closePassword() ;
            setPwDone(true) ;
        } catch (err: unknown) {
            if (err instanceof Error) {
                setPwError(err.message);
            } else {
                setPwError ('Could not change password');
            }
        } finally {
            setPwSaving(false) ;
        }
    }
        
    if (changingPassword) 
        return (
            <div className="w-full rounded-2xl border border-carbon-stroke flex flex-col p-10">
                <h2 className='uppercase mb-4'>Change Password</h2>
                <div className="space-y-4 mb-4">
                    <div>
                        <label className='block uppercase text-text-muted font-bold text-sm mb-2' htmlFor="current-password">Current password</label>
                        <PasswordInput id='current-password' value={current} onChange={(e) => setCurrent(e.target.value)} placeholder='Current password' autoComplete='current-password' />
                    </div>
                    <div>
                        <label className='block uppercase text-text-muted font-bold text-sm mb-2' htmlFor="new-password">New password</label>
                        <PasswordInput id='new-password' name='new-password' value={next} onChange={(e) => setNext(e.target.value)} placeholder='New password' autoComplete='new-password' />
                    </div>
                    <div>
                        <label className='block uppercase text-text-muted font-bold text-sm mb-2' htmlFor="confirm-new-password">Confirm new password</label>
                        <PasswordInput id='confirm-new-password' value={confirm} onChange={(e) => setConfirm(e.target.value)} placeholder='Repeat new password' autoComplete='new-password' />
                    </div>
                </div>
                {pwError && (
                    <div className="mb-3">
                        <Alert variant="error" message={pwError} />
                    </div>
                )}
                <div className="flex gap-2">
                    <button type="button" onClick={handlePasswordSave} disabled={pwSaving} className='text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors'>Save</button>
                    <button type="button" onClick={closePassword} disabled={pwSaving} className='text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors'>Cancel</button>
                </div>
            </div>
        );

        if (!editing) {
            return (
                <div className="w-full rounded-2xl border border-carbon-stroke p-10 flex flex-col">
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
                    {infoDone && (
                        <div className="mb-3">
                            <Alert variant="success" message="Profile updated successfully." />
                        </div>
                    )}
                    {pwDone && (
                        <div className="mb-3">
                            <Alert variant="success" message="Password changed successfully." />
                        </div>
                    )}
                    <div className="flex gap-2">
                        <button type='button' onClick={startEdit} className='text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors'>Edit Info</button>
                        <button type='button' onClick={openPassword} className='text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors'>Change Password</button>
                    </div>
                </div>
            );
        }
        return (
            <div className="w-full rounded-2xl border border-carbon-stroke flex flex-col p-10">
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
                {error && (
                <div className="mb-3">
                    <Alert variant="error" message={error} />
                </div>
                )}
                <div className="flex gap-2">
                    <button type="button" onClick={handleSave} disabled={saving} className="text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors">{saving ? 'Saving...' : 'Save'}</button>
                    <button type="button" onClick={cancelEdit} disabled={saving} className="text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors">Cancel</button>
                </div>
            </div>
        );

}