import React, { useEffect } from 'react';
import type { AppProps } from 'next/app';
import '../styles/globals.css';
import 'mapbox-gl/dist/mapbox-gl.css';
import { NotificationsProvider, useNotifications } from '../hooks/useNotification';
import { NotificationToast } from '../components/notification/NotificationToast';
import { offlineStore } from '../lib/offlineStore';
import { probeHealth } from '../lib/offline/shared';
import { OfflineBar } from '../components/shared/OfflineBar';

function GlobalToast() {
  const { activeToast, dismissToast } = useNotifications();
  if (!activeToast) return null;
  return (
    <div className="toast toast-top toast-end z-100">
      <NotificationToast notification={activeToast} onDismiss={dismissToast} />
    </div>
  );
}

function MyApp({ Component, pageProps }: AppProps) {
  useEffect(() => {
    // Only register in prod

    if (
      process.env.NODE_ENV === 'production' &&
      typeof window !== 'undefined' &&
      'serviceWorker' in navigator
    ) {
      navigator.serviceWorker.register('/service_worker.js').catch(() => {
        // service worker registration fallback
      });
    }

    offlineStore.init();

    const handleReconnection = async () => {
      const isReachable = await probeHealth();
      if (isReachable) {
        const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
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
      <Component {...pageProps} />
      <GlobalToast />
      <OfflineBar />
    </NotificationsProvider>
  );
}

export default MyApp;
