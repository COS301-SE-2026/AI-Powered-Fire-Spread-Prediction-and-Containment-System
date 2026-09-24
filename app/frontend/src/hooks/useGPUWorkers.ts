import { useState , useCallback } from 'react';
import { useFetch } from './useFetch';
import { apiCall } from '../lib/api';
import type { GPUWorker, Status } from '../types/GPUWorkers';
import { mockGpuWorkers } from '../mockData/GPUWorkers';
import { useDebounce } from './useDebounce';

export function useGPUWorkers(searchKey: string = '') {
    const debouncedSearch = useDebounce(searchKey, 600);
    // TODO: uncomment once the endpoints are ready, delete the mock block below
    // let url = '/api/admin/gpu-workers';
    // if (debouncedSearch) {
    //     url = `/api/admin/gpu-workers/search?key=${encodeURIComponent(debouncedSearch)}`;
    // }
    // const { data, loading, error, refetch } = useFetch<GPUWorker[]>(url);


    const [mockData, setMockData] = useState<GPUWorker[]>(mockGpuWorkers);
    const loading = false;
    const error = null;
    const refetch = () => {};

    const needle = debouncedSearch.trim().toLowerCase();
    const data = mockData.filter((w) =>
        `${w.label} ${w.gpu_name} ${w.id}`.toLowerCase().includes(needle)
    );

    function updateLocal(id: string, patch: Partial<GPUWorker>) {
        setMockData((prev) => prev.map((w) => (w.id === id ? { ...w, ...patch } : w)));
    }

    async function activate(id: string) {
        // TODO: replace with a real mutation call, e.g.
        // await fetch(`/api/admin/gpu-workers/${id}/activate`, { method: 'POST' });
        // refetch();
        updateLocal(id, { status: 'active' as Status, deactivated_at: null });
    }

    async function deactivate(id: string) {
        // TODO: replace with a real mutation call, e.g.
        // await fetch(`/api/admin/gpu-workers/${id}/deactivate`, { method: 'POST' });
        // refetch();
        updateLocal(id, { status: 'deactivated' as Status, deactivated_at: new Date().toISOString() });
    }

    async function remove(id: string, reason: string) {
        // await apiCall(`/api/admin/gpu-workers/${id}/remove`, 'PUT', { reason });
        // await refetch();
        let removalReason: string | null = null;
        if (reason.length > 0) {
            removalReason = reason;
        }
        updateLocal(id, {status: 'removed' as Status, removed_at: new Date().toISOString(), removal_reason: removalReason,});
    }

  return {
    workers: data ?? [],
    loading,
    error,
    refetch,
    activate,
    deactivate,
    remove,
  };
}
