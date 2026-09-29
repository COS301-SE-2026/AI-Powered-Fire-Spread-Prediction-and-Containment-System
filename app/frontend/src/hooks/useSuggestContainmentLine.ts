import { useState, useCallback } from "react";
import type {
    SuggestedContainmentLine,
    SuggestedContainmentLinesList,
} from '../types/ContainmentLines';

import { apiCall } from '../lib/api';

export function useSuggestContainmentLine() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [suggestion, setSuggestion] = useState<SuggestedContainmentLine | null>(null);

    const fetchSuggestion = useCallback(
        async (fireRef: string): Promise<SuggestedContainmentLine | null> => {
            setLoading(true);
            setError(null);

            try {
                const resp: SuggestedContainmentLinesList = await apiCall(
                    `/api/firefighter/suggest-containment-line/${encodeURIComponent(fireRef)}`
                );
                const first = resp?.data?.[0] ?? null;
                setSuggestion(first);
                if (!first) {
                    setError('No feasible containment line found for the current forecast.');
                }
                return first;
            } catch (err) {
                const message = err instanceof Error ? err.message : 'unknown error';
                console.error('Failed to fetch suggested containment line', err);
                setError(message);
                setSuggestion(null);
                return null;
            } finally {
                setLoading(false);
            }
        },
        []
    );
    const clearSuggestion = useCallback(() => {
        setSuggestion(null);
        setError(null);
    },[]);
    return {suggestion, loading, error, fetchSuggestion, clearSuggestion}
}
