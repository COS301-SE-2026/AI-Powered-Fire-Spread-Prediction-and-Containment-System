import React from 'react';
import type { AppProps } from 'next/app';
import '../styles/globals.css';
import '../styles/brand_style.css';

function MyApp({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}

export default MyApp;