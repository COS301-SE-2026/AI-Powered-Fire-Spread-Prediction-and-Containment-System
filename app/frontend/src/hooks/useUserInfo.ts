import { useState, useEffect } from 'react';
import { apiCall } from '../lib/api';
import type { UserResponse } from '../types/User';

interface UserInfoProps {
  readonly isLoading: boolean;
  readonly user: UserResponse | null;
}

export function useUserInfo(): UserInfoProps {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function fetchUserInfo(): Promise<void> {
      try {
        const data = await apiCall('/api/users/me');
        if (isMounted) {
          setUser(data);
        }
      } catch {
        // not authenticated
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }
    fetchUserInfo();

    return () => {
      isMounted = false;
    };
  }, []);
  return { user, isLoading };
}
