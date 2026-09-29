import { useFetch } from './useFetch';
import type { FireReportDetailResponse } from '../types/Report';

export function useMyFireReport(reportRef: string) {
  const safeRef = /^FR-\d{4}-\d{3,}$/.test(reportRef) ? encodeURIComponent(reportRef) : '';
  const { data, loading, error, refetch } = useFetch<FireReportDetailResponse>(
    safeRef ? `/api/users/me/reported-fires/${safeRef}` : ''
  );
  return { report: data, loading, error, refetch };
}
