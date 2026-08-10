import { useCallback } from 'react';
import { useFetch } from './useFetch';
import type { RoleRequestList, RoleAction } from '../types/RoleRequest';
import { apiCall } from '../lib/api';

export function useRoleRequests() {
    const { data, loading, error, refetch } = useFetch<RoleRequestList>('/api/admin/role-requests');

    const updateStatus = useCallback(async (requestId: string, action: RoleAction) => {
        try {
            await apiCall(`/api/admin/role-requests/${requestId}/${action}`, 'PUT');
            await refetch();
        } catch (err: unknown) {
            console.error(`Error on ${action} request`, err);
        }
    }, [refetch]);
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
