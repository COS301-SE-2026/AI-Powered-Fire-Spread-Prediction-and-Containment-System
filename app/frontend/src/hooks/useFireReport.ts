import { useFetch } from './useFetch';
import type { FireReportDetailResponse } from '../types/Report';

export function useFireReport(reportRef: string) {
  const safeRef = /^FR-\d{4}-[A-Z0-9]{3,}$/i.test(reportRef) ? encodeURIComponent(reportRef) : '';
  const { data, loading, error, refetch } = useFetch<FireReportDetailResponse>(
    safeRef ? `/api/admin/reported-fires/${safeRef}` : ''
  );
  return { report: data, loading, error, refetch };
}
