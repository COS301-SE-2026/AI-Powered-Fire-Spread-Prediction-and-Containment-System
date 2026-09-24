import { useState, useEffect, useCallback } from 'react';
import type { GPUWorker } from '../types/GPUWorkers';

interface UseGPUWorkersReturn {
    workers: GPUWorker[];
    loading: boolean;
    error: string | null;
    refetch: () => Promise<void>;
    activate: (id: string) => Promise<void>;
    deactivate: (id: string) => Promise<void>;
    remove: (id: string, reason?: string) => Promise<void>;
}

export function useGPUWorkers(): UseGPUWorkersReturn {
    const [workers, setWorkers] = useState<GPUWorker[]>([]);
    const [loading, setLoading] = useState(true); 
    const [error, setError] = useState<string | null>(null);

    const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || '';
    
    const fetchWorkers = useCallback(async (): Promise<void> => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${apiBaseUrl}/api/v1/workers`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`Failed to load workers (status: ${response.statusText})`);
            }

            const data = await response.json();
            setWorkers(Array.isArray(data) ? data : []);
        } catch (err: unknown) {
            const message = err instanceof Error ? err.message : 'Error fetching workers';
            setError(message);
            setWorkers([]);
        } finally {
            setLoading(false);
        }
    }, [apiBaseUrl]);

    const activate = useCallback(
        async (id: string): Promise<void> => {
            try {
                const response = await fetch(`${apiBaseUrl}/api/v1/workers/${id}/activate`, {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    throw new Error(`Failed to activate worker: ${response.statusText}`);
                }
            
                const updateNode: GPUWorker = await response.json();
                    setWorkers((prev: GPUWorker[]) => prev.map((worker: GPUWorker) => (worker.id === id ? updateNode : worker)));
            } catch (err: unknown) {
                const message = err instanceof Error ? err.message : 'Error activating worker';
                setError(message);
            }
        }, 
        [apiBaseUrl]
    );

    const deactivate = useCallback(
        async (id: string): Promise<void> => {
            try {
                const response = await fetch(`${apiBaseUrl}/api/v1/workers/${id}/deactivate`, {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    throw new Error(`Failed to deactivate worker: ${response.statusText}`);
                }
            
                const updateNode: GPUWorker = await response.json();
                setWorkers((prev: GPUWorker[]) => prev.map((worker: GPUWorker) => (worker.id === id ? updateNode : worker)));
            } catch (err: unknown) {
                const message = err instanceof Error ? err.message : 'Error deactivating worker';
                setError(message);
            }
        },
        [apiBaseUrl]
    );

    const remove = useCallback(
        async (id: string, reason?: string): Promise<void> => {
            try {
                const response = await fetch(`${apiBaseUrl}/api/v1/workers/${id}/remove`,  {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ reason: reason || '' }),
                });

                if (!response.ok) {
                    throw new Error(`Failed to remove worker: ${response.statusText}`);
                }

                const updateNode: GPUWorker = await response.json();
                setWorkers((prev: GPUWorker[]) => prev.map((worker: GPUWorker) => (worker.id === id ? updateNode : worker))); 
            } catch (err: unknown) {
                const message = err instanceof Error ? err.message : 'Error removing worker';
                setError(message);
            }
        },
        [apiBaseUrl]
    );

    useEffect(() => {
        fetchWorkers();
    }, [fetchWorkers]);

    return {
        workers,
        loading,
        error,
        refetch: fetchWorkers,
        activate,
        deactivate,
        remove,
    };
}
