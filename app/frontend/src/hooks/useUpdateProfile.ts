import { useCallback } from 'react';
import type { UserUpdate} from '../types/User';

export function useUpdateProfile() {
  const updateProfile = useCallback(async (payload: UserUpdate) => {
    const res = await fetch(`/api/users/me`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });

    if (!res.ok) {
        throw new Error('Failed to update profile');
    }

    return res.json();
  }, []);
  return { updateProfile };
}
