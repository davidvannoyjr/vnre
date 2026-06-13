"use client";

import { useState } from "react";

export function ManageBillingButton() {
  const [loading, setLoading] = useState(false);

  async function open() {
    setLoading(true);
    try {
      const res = await fetch("/api/stripe/portal", { method: "POST" });
      const data = await res.json();
      if (data.url) window.location.href = data.url;
      else alert(data.error ?? "Billing isn't available yet.");
    } catch {
      alert("Could not open billing.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <button onClick={open} disabled={loading} className="text-sm text-accent hover:underline disabled:opacity-60">
      {loading ? "Opening…" : "Manage billing"}
    </button>
  );
}
