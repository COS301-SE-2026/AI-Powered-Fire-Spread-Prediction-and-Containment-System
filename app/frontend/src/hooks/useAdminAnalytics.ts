import { useFetch } from './useFetch';
import type { AnalyticsData } from '../types/Analytics';

export function useAdminAnalytics() {
    const { data, loading, error, refetch } = useFetch<AnalyticsData>('/api/admin/analytics/overview');

    return {
        kpis: data?.kpis ?? null,
        pendingRequests: data?.pending_requests ?? [],
        loading,
        error,
        refetch,
    };
}