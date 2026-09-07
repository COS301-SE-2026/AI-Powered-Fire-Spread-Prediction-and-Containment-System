const withSerwistInit = require("@serwist/next").default;

const withSerwist = withSerwistInit({
  swSrc: "src/service-worker/index.ts",
  swDest: "public/sw.js",
  reloadOnOnline: true,
  disable: process.env.NODE_ENV === "development",
  additionalPrecacheEntries: [
    { url: "/admin/live-map", revision: "1" },
    { url: "/users/live-map", revision: "1" },
    { url: "/guests/live-map", revision: "1" },
    { url: "/firefighter/dashboard", revision: "1" },
  ],
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  transpilePackages: ['mapbox-gl', 'react-map-gl'],
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: process.env.MINIO_PROTOCOL ||'http',
        hostname: process.env.MINIO_PUBLIC_HOSTNAME || 'localhost',
        port: process.env.MINIO_PUBLIC_PORT || '9000',
        pathname: '/fire-reports/**',
      },
    ],
  },
  async rewrites() {
    if (process.env.NODE_ENV === 'production') return [];
    const backend_url = process.env.BACKEND_INTERNAL_URL || process.env.BACKEND_URL || "http://127.0.0.1:8000"; // NOSONAR - internal Docker service
    console.log('[next.config.js] Proxying /api/* to:', backend_url);
    return [
      {
        source: '/api/:path*',
        destination: `${backend_url}/api/:path*`,
      },
    ];
  },
};

module.exports = withSerwist(nextConfig);
