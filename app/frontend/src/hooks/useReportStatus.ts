import { useCallback, useState } from 'react';
import { useAuthHeaders } from './useAuthHeaders';
import type { ReportStatus, FireReportDetailResponse } from '../types/Report';

export function useReportStatus() {
    const headers = useAuthHeaders();
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const updateStatus = useCallback(async (
        reportRef: string,
        newStatus: ReportStatus
    ): Promise<FireReportDetailResponse | null> => {
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch(
                `/api/admin/reported-fires/${reportRef}/status?status=${newStatus}`,
                { method: 'PATCH', headers }
            );
            if (!resp.ok) {
                throw new Error('Failed to update status');
            }
            const updated: FireReportDetailResponse = await resp.json();
            return updated;
        } catch (err) {
            console.error('Error updating report status', err);
            setError(err instanceof Error ? err.message : 'Unknown error');
            return null;
        } finally {
            setLoading(false);
        }
    }, [headers]);

    return { updateStatus, loading, error };
}