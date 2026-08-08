import { useState, useEffect, useCallback, useRef } from 'react';

export function useFetch<T>(url: string, options?: RequestInit) {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [status, setStatus] = useState<number | null>(null);
    const [refetchIndex, setRefetchIndex] = useState(0);

    const optionsRef = useRef(options);
    optionsRef.current = options;

    const refetch = useCallback(() => {
        setRefetchIndex((i) => i + 1);
    }, []);

    useEffect(() => {
        const controller = new AbortController();

        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                const resp = await fetch(url, { ...optionsRef.current, credentials: 'include', signal: controller.signal });
                setStatus(resp.status);

                if (!resp.ok) {
                    const body = await resp.json().catch(() => null);
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
    }, [url, refetchIndex]);

    return { data, loading, error, status, refetch };
}