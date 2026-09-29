'use client';

import React, { useState } from 'react';
import { FireExtinguisher, ShieldCheck, User } from 'lucide-react';
import type { UserResponse, UserRole } from '../../types/User';
import { useMyRoleRequests } from '../../hooks/useMyRoleRequests';
import { RoleActions } from './RoleActions';
import { RoleRow } from './RoleRow';

interface RoleProps {
    user: UserResponse;
}

export function RoleRequests({ user }: RoleProps){
    const { requests, loading, requestRole, cancelRequest } = useMyRoleRequests();
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState('');
    const pending = requests.find((request) => request.status === 'pending');

    async function run(action: () => Promise<void>){
        setBusy(true);
        setError('');
        try {
            await action();
        } catch {
            setError('Something went wrong. Please try again.');
        } finally {
            setBusy(false);
        }
    }

    return (
        <div className='w-full rounded-2xl border border-carbon-stroke p-10 flex flex-col'>
            <h2 className='uppercase mb-3'>Role &amp; Requests</h2>
            {user.role === 'user' && (
                <RoleRow icon={<User size={20} />} title="Registered User" actions={<RoleActions userRole="user" user={user} pending={pending} loading={loading} busy={busy} run={run} requestRole={requestRole} cancelRequest={cancelRequest}/> } />
            )}
            {user.role !== 'admin' && (
                <RoleRow icon={<FireExtinguisher size={20} />} title="Firefighter" actions={<RoleActions userRole="firefighter" user={user} pending={pending} loading={loading} busy={busy} run={run} requestRole={requestRole} cancelRequest={cancelRequest}/>} />
            )}
            <RoleRow icon={<ShieldCheck size={20} />} title="Admin" actions={<RoleActions userRole="admin" user={user} pending={pending} loading={loading} busy={busy} run={run} requestRole={requestRole} cancelRequest={cancelRequest}/>} />
            {error && <p className='text-error text-xs mt-3'>{error}</p>}
        </div>
    );
}