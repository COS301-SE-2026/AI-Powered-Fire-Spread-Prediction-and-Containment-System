import React from 'react';
import type { AppProps } from 'next/app';
import '../styles/globals.css';
import 'mapbox-gl/dist/mapbox-gl.css'
import { NotificationsProvider, useNotifications } from "../hooks/useNotification";
import { NotificationToast } from '../components/notification/NotificationToast';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <NotificationsProvider>
      <Component {...pageProps} />
      <GlobalToast />
    </NotificationsProvider>
  );
}

function GlobalToast() {
  const { activeToast, dismissToast } = useNotifications();
  if (!activeToast) return null;
  return (
    <div className="toast toast-top toast-end z-100">
      <NotificationToast notification={activeToast} onDismiss={dismissToast} />
    </div>
  );
}

export default MyApp;
