import { useCallback } from 'react';
import { useFetch } from './useFetch';
import type { RoleRequestList, RoleRequestCreate } from '../types/RoleRequest';
import { apiCall } from '../lib/api';

export function useMyRoleRequests() {
  const { data, loading, error, refetch } = useFetch<RoleRequestList>('/api/users/role-requests/me');
  
  const requestRole = useCallback(async (payload: RoleRequestCreate) => {
    await apiCall('/api/users/role-requests', 'POST', payload);
    await refetch();
  }, [refetch]);

  const cancelRequest = useCallback(async () => {
    await apiCall('/api/users/role-requests/me', 'DELETE');
    await refetch();
  }, [refetch]);

  return {
    requests: data?.data ?? [],
    total: data?.total ?? 0,
    loading,
    requestRole,
    cancelRequest,
    refetch,
  };
}
