"use client";

import { useState } from "react";
import type { Tier } from "@/lib/tiers";

export function CheckoutButton({ tier, highlight }: { tier: Tier; highlight?: boolean }) {
  const [loading, setLoading] = useState(false);

  async function start() {
    setLoading(true);
    try {
      const res = await fetch("/api/stripe/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tier })
      });
      const data = await res.json();
      if (data.url) window.location.href = data.url;
      else alert(data.error ?? "Checkout is not configured yet.");
    } catch {
      alert("Could not start checkout.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      onClick={start}
      disabled={loading}
      className={`block w-full rounded-md px-4 py-2 text-center font-medium text-white disabled:opacity-60 ${
        highlight ? "bg-accent" : "bg-steel"
      } hover:opacity-90`}
    >
      {loading ? "Starting…" : "Subscribe"}
    </button>
  );
}
