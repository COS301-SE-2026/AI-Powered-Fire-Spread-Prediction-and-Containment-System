import { useFetch } from './useFetch';
import { useState } from 'react';
import type { GPUWorker, Status } from '../types/GPUWorkers';
import { mockGpuWorkers } from '../mockData/GPUWorkers';

export function useGPUWorkers() {
    // TODO: uncomment once GET /api/admin/gpu-workers is ready, delete the mock block below
    // const { data, loading, error, refetch } = useFetch<GPUWorker[]>(
    //   '/api/admin/gpu-workers'
    // );

    const [data, setData] = useState<GPUWorker[]>(mockGpuWorkers);
    const loading = false;
    const error = null;
    const refetch = () => {};

    function updateLocal(id: string, patch: Partial<GPUWorker>) {
        setData((prev) => prev.map((w) => (w.id === id ? { ...w, ...patch } : w)));
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

    async function remove(id: string) {
        // TODO: replace with a real mutation call, e.g.
        // await fetch(`/api/admin/gpu-workers/${id}/remove`, { method: 'POST' });
        // refetch();
        updateLocal(id, { status: 'removed' as Status, removed_at: new Date().toISOString() });
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
