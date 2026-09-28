import { useEffect } from 'react';
import { subscribeToPush } from '@/lib/push';
import { useAuth } from './useAuth';

export function usePushSubscription(): void {
    const { isAuth, isLoading } = useAuth();

    useEffect(() => {
        if (isLoading || !isAuth) return;

        subscribeToPush().catch((err) => {
            console.warn('Push subscription failed', err);
        });
    }, [isAuth, isLoading]);
}
