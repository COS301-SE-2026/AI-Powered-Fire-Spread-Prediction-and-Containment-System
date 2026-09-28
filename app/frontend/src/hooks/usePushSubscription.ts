import { useEffect } from 'react';
import { useAuth } from './useAuth';
import { subscribeToPush } from '@/lib/push';

export function usePushSubscription(): void {
    const { isAuth, isLoading } = useAuth();

    useEffect(() => {
        if (isLoading || !isAuth) return;

        subscribeToPush().catch((err) => {
            console.warn('Push subscription failed', err);
        });
    }, [isAuth, isLoading]);
}
