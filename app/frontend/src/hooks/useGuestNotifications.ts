import { useCallback, useRef } from 'react';
import type { FireNotification } from '@/types/Notifications';

const MIN_DELTA_DEG = 0.0005;

export function useGuestNotifications(showToast: (notification: FireNotification) => void) {
  const lastSent = useRef<{ lat: number; lng: number } | null>(null);
  const seenFireIdsRef = useRef<Set<string>>(new Set());

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

      lastSent.current = { lat, lng };

      fetch('/api/guests/nearby-fires', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: lat, longitude: lng }),
      })
        .then((res) => {
          if (!res.ok) {
            console.warn('Guest nearby-fires check returned an error status', res.status);
            return null;
          }
          return res.json();
        })
        .then((results: FireNotification[] | null) => {
          if (!results) return;

          const unseen = results.filter((n) => !seenFireIdsRef.current.has(n.fireId));
          unseen.forEach((n) => seenFireIdsRef.current.add(n.fireId));

          // Only one toast can show at a time
          // Surface just the first unseen one rather than queuing.
          if (unseen.length > 0) {
            showToast(unseen[0]);
          }
        })
        .catch(() => {
          console.warn('Failed to check nearby fires for guest');
        });
    },
    [showToast]
  );
}
