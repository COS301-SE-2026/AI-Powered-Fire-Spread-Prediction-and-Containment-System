import { useFetch } from './useFetch';
import type { DashboardSummaryResponse } from '../types/AdminDashboard';

export function useAdminDashboard() {
    const { data, loading, error, status, refetch } = useFetch<DashboardSummaryResponse>('/api/admin/dashboard/summary');
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