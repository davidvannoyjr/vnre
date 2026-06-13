import Link from "next/link";
import { siteConfig } from "../../site.config";

export function SiteFooter() {
  return (
    <footer className="border-t border-band bg-strip">
      <div className="mx-auto max-w-6xl px-4 py-8 text-sm text-steel/70">
        <div className="flex flex-col justify-between gap-4 sm:flex-row">
          <div>
            <div className="font-bold text-steel">{siteConfig.name}</div>
            <div>{siteConfig.tagline}</div>
          </div>
          <nav className="flex flex-wrap gap-6">
            <Link href="/tutorials" className="hover:text-accent">Tutorials</Link>
            <Link href="/blog" className="hover:text-accent">Blog</Link>
            <Link href="/pricing" className="hover:text-accent">Pricing</Link>
            <Link href="/about" className="hover:text-accent">About &amp; FAQ</Link>
            <a href="/feed.xml" className="hover:text-accent">RSS</a>
          </nav>
        </div>
        <div className="mt-6 text-xs text-steel/50">
          © {new Date().getFullYear()} {siteConfig.author} · DVN Coaching. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
