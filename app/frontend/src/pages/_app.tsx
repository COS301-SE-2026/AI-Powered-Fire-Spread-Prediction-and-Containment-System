import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import type { AppProps } from 'next/app';
import '../styles/globals.css';
import 'mapbox-gl/dist/mapbox-gl.css'
import Head from 'next/head';
import { NotificationsProvider, useNotifications } from '../hooks/useNotification';
import { NotificationToast } from '../components/notification/NotificationToast';
import { offlineStore } from '../lib/offlineStore';
import { probeHealth } from '../lib/offline/shared';
import { OfflineBar } from '../components/shared/OfflineBar';
import GpuNotification from '../components/gpu_worker/GpuNotification';

// function GlobalToast() {
//   const { activeToast, dismissToast } = useNotifications();
//   if (!activeToast) return null;
//   return (
//     <div className="toast toast-top toast-end z-100">
//       <NotificationToast notification={activeToast} onDismiss={dismissToast} />
//     </div>
//   );
// }

function MyApp({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const showGpuNotification = router.pathname.startsWith('/admin') || router.pathname.startsWith('/firefighter') || router.pathname.startsWith('/user');
  useEffect(() => {
    // Only register in prod

    // if (process.env.NODE_ENV === 'production' && typeof window !== 'undefined' && 'serviceWorker' in navigator) {
    //   navigator.serviceWorker.register('/service_worker.js').catch(() => {
    //     // service worker registration fallback
    //   });
    // }

    offlineStore.init();

    const handleReconnection = async () => {
      const isReachable = await probeHealth();
      if (isReachable) {
        const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || '';
        await offlineStore.syncQueuedActions(apiBaseUrl);
      }
    };

    window.addEventListener('online', handleReconnection);

    return () => {
      window.removeEventListener('online', handleReconnection);
    };
  }, []);

  return (
    <NotificationsProvider>
      <Head>
        <link rel='manifest' href='/manifest.json' />
        <meta name='theme-color' content='#ff4904' />
        <meta name='apple-mobile-web-app-title' content='Fireaway' />
      </Head>
      <Component {...pageProps} />
      {showGpuNotification && <GpuNotification />}
      <OfflineBar />
    </NotificationsProvider>
  );
}

export default MyApp;
