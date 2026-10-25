'use client';

import React, { useEffect, useState } from 'react'; 
import { apiCall } from '../../lib/api';
import { useTwoFactorStatus } from '../../hooks/useTwoFactorToggle';
import { Alert } from '../shared/Alerts';

export function TwoFactorToggle() {
    const { enabled, loading, setEnabled } = useTwoFactorStatus();
    const [busy, setBusy] = useState (false);
    const [error, setError] = useState('');
    const [notice, setNotice] = useState('');
   
    useEffect(() => {
        if (!notice) {
            return;
        }
        const timer = setTimeout(() => setNotice(''), 4000);
        return () => clearTimeout(timer);
    }, [notice]) ;

    async function handleToggle() {
        const next = !enabled;
        setBusy (true) ; 
        setError ('');
        setNotice('');
        try {
            await apiCall('/api/auth/2fa/toggle', 'POST', { enabled: next }); setEnabled (next);
            setEnabled(next);
            if (next){
                setNotice ('Two-factor authentication enabled.');
            } else {
                setNotice('Two-factor authentication disabled.');
            }
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError (err.message);
            } else {
                setError ('Could not update two-factor authentication');
            }
        } finally {
            setBusy(false);
        }
    }
    let status = 'Off';
    if (enabled) {
        status = 'On';
    }
    return (
        <div className='ml-auto flex flex-col items-end gap-2'>
            <p className='uppercase text-text-muted font-bold text-sm'>Two-factor authentication</p>
            <div className='flex items-center gap-3'>
                <p className='text-text-primary font-semibold'>{status}</p>
                <input
                    type='checkbox'
                    className='toggle toggle-sm rounded-full before:rounded-full text-white border-white checked:bg-white/20 checked:border-white'
                    checked={enabled}
                    disabled={loading || busy}
                    onChange={handleToggle}
                    aria-label='Toggle two-factor authentication'
                />
            </div>
            {notice && <Alert variant='success' message={notice} />}
            {error && <Alert variant='error' message={error} />}
        </div>
    );
}