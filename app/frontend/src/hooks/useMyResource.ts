import { useFetch } from './useFetch';
import type { ResourceList, ResourceTable } from '../types/Resource';

export function useMyResource(id: string) {
  const { data, loading, error, refetch } = useFetch<ResourceTable>(
    `/api/users/resources/${id}`
  );
  return { resource: data, loading, error, refetch };
}

export function useMyResources() {
  const { data, loading, error, refetch } = useFetch<ResourceList>('/api/users/resources/mine');
  return {
    resources: data?.data ?? [],
    total: data?.total ?? 0,
    loading,
    error,
    refetch,
  };
}