import { useCallback, useState } from 'react';
import type { ReportStatus, FireReportDetailResponse } from '../types/Report';
import { apiCall } from '../lib/api';

export function useReportStatus() {
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const updateStatus = useCallback(async (
        reportRef: string,
        newStatus: ReportStatus
    ): Promise<FireReportDetailResponse | null> => {
        setLoading(true);
        setError(null);
        try {
            const updated = await apiCall(
                `/api/admin/reported-fires/${reportRef}/status?status=${newStatus}`,'PATCH'
            );
            return updated;
        } catch (err: unknown) {
            console.error('Error updating report status', err);
            setError(err instanceof Error ? err.message : 'Unknown error');
            return null;
        } finally {
            setLoading(false);
        }
    },[]);

    return { updateStatus, loading, error };
}