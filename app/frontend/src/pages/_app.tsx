import React from 'react';
import type { AppProps } from 'next/app';
import '../styles/globals.css';
import 'mapbox-gl/dist/mapbox-gl.css'
import { NotificationsProvider } from "../hooks/useNotification";

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <NotificationsProvider>
      <Component {...pageProps} />
    </NotificationsProvider>
  );
}

export default MyApp;