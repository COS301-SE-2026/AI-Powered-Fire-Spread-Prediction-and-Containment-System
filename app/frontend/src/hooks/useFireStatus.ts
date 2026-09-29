import { useCallback, useState } from 'react';
import type { FireStatus, FireReportDetailResponse } from '@/types/Report';
import { apiCall } from '../lib/api';

export function useFireStatus() {
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const updateFireStatus = useCallback(
        async (
            reportRef: string,
            newStatus: FireStatus,
            containmentPercent?: number
        ): Promise<FireReportDetailResponse | null> => {
            setLoading(true);
            setError(null);
            try {
                const params = new URLSearchParams({ fire_status: newStatus });
                if (containmentPercent != null) {
                    params.set('containment_percent', String(containmentPercent));
                }
                const updated = await apiCall(
                    `/api/admin/reported-fires/${reportRef}/fire-status?${params.toString()}`,
                    'PATCH'
                );
                return updated;
            } catch (err: unknown) {
                console.error('Error updating fire status', err);
                setError(err instanceof Error ? err.message : 'Unknown error');
                return null;
            } finally {
                setLoading(false);
            }
        },
        []
    );

    return { updateFireStatus, loading, error };

}