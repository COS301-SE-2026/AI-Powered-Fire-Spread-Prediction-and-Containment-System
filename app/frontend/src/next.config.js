/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    transpilePackages: ['mapbox-gl', 'react-map-gl'],
      eslint: {
        ignoreDuringBuilds: true,
    },
    async rewrites() {
        return[
            {
                source: '/api/:path*',
                destination: 'http://backend:8000/api/:path*',
            }
        ]
    }
}

module.exports = nextConfig