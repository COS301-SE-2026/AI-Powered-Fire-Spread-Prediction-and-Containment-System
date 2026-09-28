'use client';

import React, { useState } from 'react';
import type { UserResponse, UserRole } from '../../types/User';
import { useMyRoleRequests } from '../../hooks/useMyRoleRequests';
import { FireExtinguisher, Ambulance, ShieldCheck, User } from 'lucide-react';

interface RoleProps {
    user: UserResponse;
}

interface RoleRowProps {
    icon: React.ReactNode;
    title: string;
    actions: React.ReactNode;
}

const ROLES: Record<UserRole, number> = {
    user: 0,
    firefighter: 1,
    admin: 2
};

function RoleRow({ icon, title, actions }: RoleRowProps){
    return (
        <div className='flex items-center justify-between gap-4 py-4 border-b border-carbon-stroke last:border-b-0'>
            <div className="flex items-center gap-3">
                <span className="text-text-muted">{icon}</span>
                <p className='text-text-primary font-semibold'>{title}</p>
            </div>
            {actions}
        </div>
    );
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

    function Actions(role: UserRole){
        if (user.role === role){
            return <span className='uppercase text-success font-bold text-sm'>Current</span>;
        }
        const isPending = pending?.requested_role === role;

        return (
            <button type="button" className='text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors' disabled={loading || busy || (!isPending && pending !== undefined)} onClick={() => run(isPending ? cancelRequest : () => requestRole({ requested_role: role }))}>
                {isPending ? 'Cancel request' : 'Request'}
            </button>
        );
    }
    return (
        <div className='w-full rounded-2xl border border-carbon-stroke p-10 flex flex-col'>
            <h2 className='uppercase mb-3'>Role &amp; Requests</h2>
            {user.role === 'user' && (
                <RoleRow icon={<User size={20} />} title="Registered User" actions={Actions('user')}/> 
            )}
            {user.role !== 'admin' && (
                <RoleRow icon={<FireExtinguisher size={20} />} title="Firefighter" actions={Actions('firefighter')}/> 
            )}
            <RoleRow icon={<ShieldCheck size={20} />} title="Admin" actions={Actions('admin')}/> 
            {error && <p className='text-error text-xs mt-3'>{error}</p>}
        </div>
    );
}