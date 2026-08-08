import { useFetch } from './useFetch';
import type { FireReportMapResponse } from '../types/Report';

export function useUserReports() {
  const { data, loading, error, refetch } = useFetch<FireReportMapResponse[]>(
    '/api/users/reported-fires'
  );

  const sorted = [...(data ?? [])].sort(
    (a, b) => new Date(b.submitted_at).getTime() - new Date(a.submitted_at).getTime()
  );

  return { reports: sorted, loading, error, refetch };
}