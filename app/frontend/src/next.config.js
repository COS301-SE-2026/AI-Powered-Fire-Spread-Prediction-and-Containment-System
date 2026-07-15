/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    transpilePackages: ['mapbox-gl', 'react-map-gl'],
      eslint: {
        ignoreDuringBuilds: true,
    },
    async rewrites() {
        const backend_url = process.env.BACKEND_INTERNAL_URL || 'http://python-backend:8000' //NOSONAR - internal Docker service
        console.log('[next.config.js] Proxying /api/* to:', backend_url)
        return[
            {
                source: '/api/:path*',
                destination: `${backend_url}/api/:path*`,
            }
        ]
    }
}

module.exports = nextConfig