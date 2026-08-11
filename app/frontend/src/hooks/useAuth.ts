import { useState, useEffect } from 'react';
import { apiCall } from '../lib/api';

interface AuthProps {
    readonly isAuth: boolean;
    readonly role: string | null;
    readonly isLoading: boolean;
}

export function useAuth(): AuthProps {
    const [isAuth, setIsAuth] = useState(false);
    const [role, setRole] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        let isMounted = true;

        async function checkAuth(): Promise<void> {
            try {
                const data = await apiCall('/api/auth/me');
                if (isMounted) {
                    setIsAuth(true);
                    setRole(data.role);
                }
            } catch {

            } finally {
                if (isMounted) {
                    setIsLoading(false);
                }
            }
        }
        checkAuth();

        return () => {
            isMounted = false;
        };
    }, []);
    return {isAuth, role, isLoading};
}