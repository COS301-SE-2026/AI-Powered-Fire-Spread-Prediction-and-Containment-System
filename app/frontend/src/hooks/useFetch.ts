import { useState, useEffect, useCallback, useRef } from 'react';

export function useFetch<T>(url: string, options?: RequestInit) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<number | null>(null);
  const [refetchIndex, setRefetchIndex] = useState(0);

  const optionsRef = useRef(options);

  useEffect(() => {
    optionsRef.current = options;
  });

  const refetch = useCallback(() => {
    setRefetchIndex((i) => i + 1);
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    let cancelled = false;

    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const resp = await fetch(url, {
          ...optionsRef.current,
          credentials: 'include',
          signal: controller.signal,
        });
        if (cancelled) return;
        setStatus(resp.status);

        if (!resp.ok) {
          const body = await resp.json().catch(() => null);
          if (cancelled) return;
          throw new Error(body?.detail || `Request failed: ${resp.status}`);
        }
        const json: T = await resp.json();
        if (cancelled) return;
        setData(json);
      } catch (err) {
        if (cancelled) return;
        if (err instanceof Error && err.name === 'AbortError') {
          return;
        }
        console.error(`Failed to fetch ${url}`, err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setData(null);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [url, refetchIndex]);

  return { data, loading, error, status, refetch };
}
