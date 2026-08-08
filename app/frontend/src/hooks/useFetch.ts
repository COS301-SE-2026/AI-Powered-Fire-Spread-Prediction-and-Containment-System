import { useState, useEffect, useCallback, useRef } from 'react';

export function useFetch<T>(url: string) {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const refetchIndex = useRef(0);

    const refetch = useCallback(() => {
        refetchIndex.current += 1;
        setLoading(true); // trigger immediately so refetch() calls feel responsive
    }, []);

    useEffect(() => {
        const controller = new AbortController();

        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                const resp = await fetch(url, { signal: controller.signal });
                if (!resp.ok) {
                    throw new Error(`Request failed: ${resp.status}`);
                }
                const json: T = await resp.json();
                setData(json);
            } catch (err) {
                if (err instanceof Error && err.name === 'AbortError') {
                    return;
                }
                console.error(`Failed to fetch ${url}`, err);
                setError(err instanceof Error ? err.message : 'Unknown error');
                setData(null);
            } finally {
                if (!controller.signal.aborted) {
                    setLoading(false);
                }
            }
        };

        fetchData();

        return () => controller.abort();
    }, [url, refetchIndex.current]);

    return { data, loading, error, refetch };
}