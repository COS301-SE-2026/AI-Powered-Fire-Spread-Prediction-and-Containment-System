import { useFetch } from './useFetch';
import type { FireReportDetailResponse } from '../types/Report';

export function useFireReport(reportRef: string) {
  const { data, loading, error, refetch } = useFetch<FireReportDetailResponse>(
    `/api/admin/reported-fires/${reportRef}`
  );
  return { report: data, loading, error, refetch };
}
