import { useCallback } from 'react';
import type { Status} from '../types/Resource';

export function useUpdateResourceStatus() {
  const updateStatus = useCallback(async (id: string, status: Status) => {
    const res = await fetch(`/api/users/resources/${id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
    });

    if (!res.ok) {
        throw new Error('Failed to update resource status');
    }

    return res.json();
  }, []);
  return { updateStatus };
}
