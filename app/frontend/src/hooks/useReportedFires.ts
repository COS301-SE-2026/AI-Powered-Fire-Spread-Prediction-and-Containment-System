import { useFetch } from './useFetch';
import { useAuthHeaders } from './useAuthHeaders';
import type { FireReportMapResponse } from '../types/Report';

export function useReportedFires() {
    const headers = useAuthHeaders();
    const { data, loading, error, refetch } = useFetch<FireReportMapResponse[]>(
        '/api/admin/reported-fires',
        { headers }
    );

    return {
        reports: data ?? [],
        loading,
        error,
        refetch,
    };
}