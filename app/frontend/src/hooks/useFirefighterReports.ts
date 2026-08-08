import { useFetch } from './useFetch';
import { useAuthHeaders } from './useAuthHeaders';
import { useDebounce } from './useDebounce';
import type { ReportList } from '../types/FirefighterReports';

export function useFirefighterReports(searchKey: string) {
    const headers = useAuthHeaders();
    const debouncedSearch = useDebounce(searchKey, 600); // waits until the user stops typing before firing a request

    const url = debouncedSearch
        ? `/api/firefighter/reported-fires/search?key=${encodeURIComponent(debouncedSearch)}`
        : `/api/firefighter/reported-fires`;

    const { data, loading, error, refetch } = useFetch<ReportList>(url, { headers });

    return {
        reports: data?.data ?? [],
        total: data?.total ?? 0,
        loading,
        error,
        refetch,
    };
}