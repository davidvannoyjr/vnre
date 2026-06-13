"use client";

import { useState } from "react";

/** Coach control: mint a private monthly checkout link to send to a client. */
export function CheckoutLinkButton({ profileId }: { profileId: string }) {
  const [url, setUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function generate() {
    setLoading(true);
    try {
      const res = await fetch("/api/coaching/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profileId })
      });
      const data = await res.json();
      if (data.url) setUrl(data.url);
      else alert(data.error ?? "Could not create link.");
    } catch {
      alert("Could not create link.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-2">
      <button
        onClick={generate}
        disabled={loading}
        className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-60"
      >
        {loading ? "Generating…" : "Generate monthly checkout link"}
      </button>
      {url && (
        <div className="rounded-md border border-band bg-strip p-3 text-sm">
          <div className="mb-1 text-xs text-steel/60">Send this to your client:</div>
          <input
            readOnly
            value={url}
            onFocus={(e) => e.currentTarget.select()}
            className="w-full rounded border border-band px-2 py-1 font-mono text-xs"
          />
        </div>
      )}
    </div>
  );
}
