/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['coinmarketcap.com', 's2.coinmarketcap.com', 's3.coinmarketcap.com'],
  },
}

module.exports = nextConfig
