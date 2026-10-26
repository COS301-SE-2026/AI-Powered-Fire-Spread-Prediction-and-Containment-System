import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/router';
import { isSectionRoute } from '@/lib/skeletonRoutes';
import { RouteSkeleton } from './skeleton/RouteSkeleton';

const SHOW_AFTER_MS = 150;

export function RouteTransitionSkeleton() {
    const router = useRouter();
    const [targetUrl, setTargetUrl] = useState<string | null>(null);
    const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

    useEffect(() => {
        const clear = () => {
            if (timer.current) clearTimeout(timer.current);
            timer.current = null;
        };

        const start = (url: string) => {
            clear();
            timer.current = setTimeout(() => setTargetUrl(url), SHOW_AFTER_MS);
        };

        const stop = () => {
            clear();
            setTargetUrl(null);
        };

        router.events.on('routeChangeStart', start);
        router.events.on('routeChangeComplete', stop);
        router.events.on('routeChangeError', stop);
        return () => {
            clear();
            router.events.off('routeChangeStart', start);
            router.events.off('routeChangeComplete', stop);
            router.events.off('routeChangeError', stop);
        };
    }, [router.events]);

    if (!targetUrl) return null;

    const withSidebar = isSectionRoute(targetUrl);

    return (
        <div className={`fixed z-30 bg-carbon-bg overflow-y-auto inset-x-0 bottom-0 ${withSidebar ? 'top-18 lg:top-0 lg:left-23' : 'top-0'}`}>
            <RouteSkeleton url={targetUrl} />
        </div>
    );
}