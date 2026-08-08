import { useFetch } from './useFetch';
import { useAuthHeaders } from './useAuthHeaders';
import type { FireReportDetailResponse } from '../types/Report';

export function useFireReport(reportRef: string) {
    const headers = useAuthHeaders();
    const { data, loading, error, refetch } = useFetch<FireReportDetailResponse>(
        `/api/admin/reported-fires/${reportRef}`,
        { headers }
    );
    return { report: data, loading, error, refetch };
}