import { useCallback, useRef } from "react";

const MIN_DELTA_DEG = 0.0005;

export function useUpdateUserLocation(onSynced? : () => void){
    const lastSent = useRef<{ lat: number; lng: number } | null>(null);

    return useCallback((lat: number, lng: number) => {
        const last = lastSent.current;
        if (last && Math.abs(last.lat - lat) < MIN_DELTA_DEG && Math.abs(last.lng - lng) < MIN_DELTA_DEG) {
            return;
        }
        lastSent.current = { lat, lng };

        fetch('/api/users/me/location', {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ latitude: lat, longitude: lng }),
        }).then((res) => {
            if (!res.ok) {
                console.warn('Location sync returned an error status', res.status);
                return;
            }

            onSynced?.();
        }).catch((err) => {
            console.warn('Failed to sync user location');
        });
    }, [onSynced]);
}