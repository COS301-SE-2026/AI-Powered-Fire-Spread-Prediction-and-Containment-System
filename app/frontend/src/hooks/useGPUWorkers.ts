import { useState, useEffect, useCallback } from 'react';
import type { GPUWorker } from '../types/GPUWorkers';
import { useDebounce } from './useDebounce';
import { apiCall } from '@/lib/api';

interface UseGPUWorkersReturn {
    workers: GPUWorker[];
    loading: boolean;
    error: string | null;
    actionError: string | null;
    refetch: () => Promise<void>;
    activate: (id: string) => Promise<void>;
    deactivate: (id: string) => Promise<void>;
    remove: (id: string, reason?: string) => Promise<void>;
}

export function useGPUWorkers(searchKey: string = ''): UseGPUWorkersReturn {
    const [workers, setWorkers] = useState<GPUWorker[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [actionError, setActionError] = useState<string | null>(null);

    const debouncedSearch = useDebounce(searchKey, 600);
    // const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || '';

    const fetchWorkers = useCallback(async (): Promise<void> => {
        setLoading(true);
        setError(null);

        const key = debouncedSearch.trim();
        const endpoint = key
            ? `/api/v1/workers?key=${encodeURIComponent(key)}`
            : '/api/v1/workers';

        try{
            const data = await apiCall(endpoint);
            setWorkers(Array.isArray(data) ? data : []);
        }catch(err: unknown){
            setError(err instanceof Error ? err.message : 'Error fetching workers');
            setWorkers([]);
        }finally{
            setLoading(false);
        }
        
    }, [debouncedSearch]);

    const runAction = useCallback(
        async (id: string, action: 'activate' | 'deactivate' | 'remove', body?: unknown): Promise<void> => {
            setActionError(null);
            try{
                const updated: GPUWorker = await apiCall(`/api/v1/workers/${id}/${action}`, 'POST', body ?? null);
                setWorkers((prev) => prev.map((w) => (w.id == id ? updated : w)));
            }catch(err: unknown){
                setActionError(err instanceof Error ? err.message : `Failed to ${action} worker` );
            }
        }, []
    );

    const activate = useCallback((id: string) => runAction(id, 'activate'), [runAction]);
    const deactivate = useCallback((id: string) => runAction(id, 'deactivate'), [runAction]);
    const remove = useCallback((id: string, reason?: string) => runAction(id, 'remove', { reason: reason?.trim() || null}), [runAction]);

    useEffect(() => {
        fetchWorkers();
    }, [fetchWorkers]);

    return {
        workers,
        loading,
        error,
        actionError,
        refetch: fetchWorkers,
        activate,
        deactivate,
        remove,
    };
}
