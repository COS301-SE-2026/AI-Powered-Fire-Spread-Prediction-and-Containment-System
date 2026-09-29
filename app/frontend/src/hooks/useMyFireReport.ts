import { useFetch } from './useFetch';
import type { FireReportDetailResponse } from '../types/Report';

export function useMyFireReport(reportRef: string) {
  const { data, loading, error, refetch } = useFetch<FireReportDetailResponse>(
    `/api/users/me/reported-fires/${reportRef}`
  );
  return { report: data, loading, error, refetch };
}
