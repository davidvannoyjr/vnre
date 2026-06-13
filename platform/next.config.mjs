/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Content is file-based MDX compiled at request/build time via next-mdx-remote.
  // No external CMS — the repo is the CMS.
  experimental: {
    serverActions: {
      bodySizeLimit: "2mb"
    }
  }
};

export default nextConfig;
