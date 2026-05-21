/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    transpilePackages: ['mapbox-gl', 'react-map-gl'],
    async rewrites() {
        return[
            {
                source: '/api/:path*',
                destination: 'http://localhost:8000/api/:path*',
            }
        ]
    }
}

module.exports = nextConfig