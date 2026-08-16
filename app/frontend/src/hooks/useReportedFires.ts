import { useFetch } from './useFetch';
import type { FireReportMapResponse } from '../types/Report';

export function useReportedFires() {
  const { data, loading, error, refetch } = useFetch<FireReportMapResponse[]>(
    '/api/admin/reported-fires'
  );

  return {
    reports: data ?? [],
    loading,
    error,
    refetch,
  };
}
