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
        protocol: 'http',
        hostname: 'localhost',
        port: '9000',
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

module.exports = nextConfig;
