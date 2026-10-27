import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/router';
import { isSectionRoute } from '@/lib/skeletonRoutes';
import { RouteSkeleton } from './skeleton/RouteSkeleton';
import { clear } from 'node:console'

const SHOW_AFTER_MS = 150;

export function RouteTransitionSkeleton() {
    const router = useRouter();
    const [pendingUrl, setPendingUrl] = useState<string | null>(null);
    const [targetUrl, setTargetUrl] = useState<string | null>(null);

    useEffect(() => {
        const start = (url: string) => setPendingUrl(url);
        const stop = () => setPendingUrl(null);

        router.events.on('routeChangeStart', start);
        router.events.on('routeChangeComplete', stop);
        router.events.on('routeChangeError', stop);

        return () => {
            router.events.off('routeChangeStart', start);
            router.events.off('routeChangeComplete', stop);
            router.events.off('routeChangeError', stop);
        }
    }, [router.events]);

    useEffect(() => {
       if (!pendingUrl) {
            setTargetUrl(null);
            return undefined;
       }
       const timer = setTimeout(() => setTargetUrl(pendingUrl), SHOW_AFTER_MS);
       return () => clearTimeout(timer);
    }, [pendingUrl]);

    if (!targetUrl) return null;

    const withSidebar = isSectionRoute(targetUrl);

    return (
        <div className={`fixed z-30 bg-carbon-bg overflow-y-auto inset-x-0 bottom-0 ${withSidebar ? 'top-18 lg:top-0 lg:left-23' : 'top-0'}`}>
            {withSidebar ? (
                <main className='p-2 flex flex-col w-full max-w-450 mx-auto min-h-full'>
                    <RouteSkeleton url={targetUrl} />
                </main>
            ) : (
                <RouteSkeleton url={targetUrl} />
            )}
        </div>
    );
}