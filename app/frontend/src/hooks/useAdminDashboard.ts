import { useFetch } from './useFetch';
import type { DashboardSummaryResponse } from '../types/AdminDashboard';
import { useAuthHeaders } from './useAuthHeaders';

export function useAdminDashboard() {
    const headers = useAuthHeaders();
    const token = localStorage.getItem('access_token');
    const { data, loading, error, status, refetch } = useFetch<DashboardSummaryResponse>('api/admin/dashboard/summary',
        { headers }
    );
    const isForbidden = status === 401 || status === 403;

    return {
        topMetrics: data?.top_metrics ?? null,
        activityLog: data?.activity_log ?? [],
        weeklyIncidents: data?.weekly_incidents ?? [],
        systemMetrics: data?.system_metrics ?? null,
        loading,
        error,
        isForbidden,
        refetch,
    };
}