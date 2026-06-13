import type { MetadataRoute } from "next";
import { siteConfig } from "../../site.config";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      // Members-only and API surfaces don't belong in the index.
      disallow: ["/dashboard", "/coaching", "/api/"]
    },
    sitemap: `${siteConfig.url}/sitemap.xml`
  };
}
