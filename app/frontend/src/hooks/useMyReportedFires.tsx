import { useFetch } from "./useFetch";
import type { FireReportMapResponse } from "../types/Report";

export function useMyReportedFires() {
    const { data, loading, error, refetch } = useFetch<FireReportMapResponse[]>('/api/users/me/reported-fires');
    return {
        reports: data ?? [],
        loading,
        error,
        refetch,
    };
}