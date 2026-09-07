import { useState, useEffect } from 'react';
import { apiCall } from '../lib/api';
import type { UserRole } from '../types/User';

interface AuthProps {
  readonly isAuth: boolean;
  readonly role: UserRole | null;
  readonly isLoading: boolean;
}

export function useAuth(): AuthProps {
  const [isAuth, setIsAuth] = useState(false);
  const [role, setRole] = useState<UserRole | null>(null);
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
        // not authenticated
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
  return { isAuth, role, isLoading };
}
