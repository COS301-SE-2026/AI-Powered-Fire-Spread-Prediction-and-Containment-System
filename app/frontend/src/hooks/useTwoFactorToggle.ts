import { useEffect, useState } from 'react'; 
import { apiCall } from '../lib/api';

interface TwoFactorStatusProps {
    readonly enabled: boolean; readonly loading: boolean;
    readonly setEnabled: (value: boolean) => void;
}

export function useTwoFactorStatus(): TwoFactorStatusProps {
    const [enabled, setEnabled] = useState(false);
    const [loading, setLoading] = useState(true);
    
    useEffect (() => {
        let isMounted = true;
        
        async function fetchStatus(): Promise<void> {
            try {
                const data: { enabled: boolean } = await apiCall('/api/auth/2fa/status');
                if (isMounted) {
                    setEnabled (data.enabled);
                }
            } catch {
            // not authenticated
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        }
        fetchStatus();
        
        return () => {
            isMounted = false;
        };
    }, []);
    return { enabled, loading, setEnabled };
}