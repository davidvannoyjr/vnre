import { MDXRemote } from "next-mdx-remote/rsc";

/**
 * Server-side MDX renderer. Content is trusted (authored in-repo by DVN / the
 * approved pipeline), so we render directly. Styling comes from .prose-vnre.
 */
export function Mdx({ source }: { source: string }) {
  return (
    <div className="prose-vnre">
      <MDXRemote source={source} />
    </div>
  );
}
