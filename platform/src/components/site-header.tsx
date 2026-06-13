import Link from "next/link";
import { siteConfig } from "../../site.config";

const NAV = [
  { href: "/tutorials", label: "Tutorials" },
  { href: "/blog", label: "Blog & Updates" },
  { href: "/pricing", label: "Pricing" }
];

export function SiteHeader() {
  return (
    <header className="border-b border-band bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <Link href="/" className="font-bold tracking-tight text-lg">
          {siteConfig.name}
          <span className="ml-2 hidden text-xs font-normal text-steel/50 sm:inline">
            {siteConfig.tagline}
          </span>
        </Link>
        <nav className="flex items-center gap-6 text-sm font-medium">
          {NAV.map((item) => (
            <Link key={item.href} href={item.href} className="hidden hover:text-accent sm:inline">
              {item.label}
            </Link>
          ))}
          <form action="/search" className="hidden md:block">
            <input
              type="search"
              name="q"
              placeholder="Search…"
              aria-label="Search"
              className="w-36 rounded-md border border-band px-3 py-1.5 text-sm"
            />
          </form>
          <Link href="/login" className="hover:text-accent">
            Log in
          </Link>
          <Link
            href="/pricing"
            className="rounded-md bg-accent px-3 py-1.5 text-white hover:opacity-90"
          >
            Join
          </Link>
        </nav>
      </div>
    </header>
  );
}
