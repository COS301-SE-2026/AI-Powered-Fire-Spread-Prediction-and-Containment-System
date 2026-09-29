import { useCallback } from 'react';
import { useFetch } from './useFetch';
import type { SavedLocation, SavedLocationCreate, SavedLocationUpdate } from '../types/SavedLocation';
import { apiCall } from '../lib/api';

export function useSavedLocations() {
  const { data, loading, error, refetch } = useFetch<SavedLocation[]>('/api/users/saved-locations');
  
  const addLocation = useCallback(async (payload: SavedLocationCreate) => {
    await apiCall('/api/users/saved-locations', 'POST', payload);
    await refetch();
  }, [refetch]);

  const editLocation = useCallback(async (locationId: string, payload: SavedLocationUpdate) => {
    await apiCall(`/api/users/saved-locations/${locationId}`, 'PATCH', payload);
    await refetch();
  }, [refetch]);

  const removeLocation = useCallback(async (locationId: string) => {
    await apiCall(`/api/users/saved-locations/${locationId}`, 'DELETE');
    await refetch();
  }, [refetch]);

  return {
    locations: data ?? [],
    loading,
    error,
    addLocation,
    editLocation,
    removeLocation,
    refetch,
  };
}
