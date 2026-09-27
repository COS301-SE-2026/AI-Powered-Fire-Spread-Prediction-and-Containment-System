import { apiCall } from '../lib/api';
import { useCallback, useRef } from 'react';

const MIN_DELTA_DEG = 0.0005;

export function useUpdateUserLocation(onSynced?: () => void) {
  const lastSent = useRef<{ lat: number; lng: number } | null>(null);

  return useCallback(
    (lat: number, lng: number) => {
      const last = lastSent.current;
      if (
        last &&
        Math.abs(last.lat - lat) < MIN_DELTA_DEG &&
        Math.abs(last.lng - lng) < MIN_DELTA_DEG
      ) {
        return;
      }
      apiCall('/api/users/me/location', 'PATCH', {latitude: lat, longitude: lng})
      .then(() => {
        lastSent.current = {lat, lng};
        onSynced?.();
      })
        .catch((err) => {
          console.warn('Failed to sync user location', err);
        });
    },
    [onSynced]
  );
}
