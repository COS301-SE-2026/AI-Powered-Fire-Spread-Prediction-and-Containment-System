/** @type {import('next').NextConfig} */
const nextConfig = {
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
    const backend_url = process.env.BACKEND_INTERNAL_URL || 'http://backend:8000'; // NOSONAR - internal Docker service
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
