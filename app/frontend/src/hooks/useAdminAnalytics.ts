import { useFetch } from './useFetch';
import type { AnalyticsData } from '../types/Analytics';
import { useAuthHeaders } from './useAuthHeaders';

export function useAdminAnalytics() {
    const headers = useAuthHeaders();
    const { data, loading, error, refetch } = useFetch<AnalyticsData>('/api/admin/analytics/overview', { headers });

    return {
        kpis: data?.kpis ?? null,
        pendingRequests: data?.pending_requests ?? [],
        loading,
        error,
        refetch,
    };
}