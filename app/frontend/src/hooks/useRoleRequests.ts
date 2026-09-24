import { useCallback } from 'react';
import { useFetch } from './useFetch';
import type { RoleRequestList, RoleAction } from '../types/RoleRequest';
import { apiCall } from '../lib/api';
import { useDebounce } from './useDebounce';

export function useRoleRequests(searchKey: string) {
  const debounceedSearch = useDebounce(searchKey, 600);

  let url = '/api/admin/role-requests';
  if (debounceedSearch) {
    url = `/api/admin/role-requests/search?key=${encodeURIComponent(debounceedSearch)}`;
  }
  const { data, loading, error, refetch } = useFetch<RoleRequestList>(url);

  const updateStatus = useCallback(
    async (requestId: string, action: RoleAction) => {
      try {
        await apiCall(`/api/admin/role-requests/${requestId}/${action}`, 'PUT');
        await refetch();
      } catch (err: unknown) {
        console.error(`Error on ${action} request`, err);
      }
    },
    [refetch]
  );
  return {
    requests: data?.data ?? [],
    total: data?.total ?? 0,
    loading,
    error,
    approveRequest: (id: string) => updateStatus(id, 'approve'),
    rejectRequest: (id: string) => updateStatus(id, 'reject'),
    revokeRequest: (id: string) => updateStatus(id, 'revoke'),
    refetch,
  };
}
