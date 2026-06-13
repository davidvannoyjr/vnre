import Link from "next/link";
import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { dbEnabled } from "@/lib/db";
import { listCoachClients } from "@/lib/coaching";
import { inviteClient } from "../actions";

export const metadata = { title: "Coaching clients" };

export default async function CoachClientsPage() {
  const session = await auth();
  if (!session?.user?.id) redirect("/login");
  if (session.user.role !== "coach") redirect("/coaching");

  if (!dbEnabled) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-24 text-center text-steel/70">
        Set <code className="font-mono">DATABASE_URL</code> to manage coaching clients.
      </div>
    );
  }

  const clients = await listCoachClients(session.user.id);

  return (
    <div className="mx-auto max-w-4xl px-4 py-16">
      <h1 className="text-3xl font-bold tracking-tight">Coaching clients</h1>
      <p className="mt-2 text-steel/70">Your 1:1 roster. Capacity is yours to cap (~10–12).</p>

      {/* Onboard a client */}
      <form action={inviteClient} className="mt-8 flex flex-wrap items-end gap-3 rounded-lg border border-band p-4">
        <div>
          <label className="block text-xs font-medium text-steel/60">Client name</label>
          <input name="name" placeholder="Jane Agent" className="mt-1 rounded-md border border-band px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="block text-xs font-medium text-steel/60">Client email</label>
          <input name="email" type="email" required placeholder="jane@brokerage.com" className="mt-1 rounded-md border border-band px-3 py-2 text-sm" />
        </div>
        <button className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:opacity-90">
          Add client
        </button>
      </form>

      <ul className="mt-8 divide-y divide-band">
        {clients.length === 0 && <li className="py-6 text-steel/60">No clients yet. Add one above.</li>}
        {clients.map((c) => {
          const open = c.tasks.filter((t) => t.status !== "done").length;
          const billing = c.client.tier === "coaching" ? "Active" : "Not billing";
          return (
            <li key={c.id} className="py-4">
              <Link href={`/coaching/clients/${c.id}`} className="group flex items-center justify-between">
                <div>
                  <div className="font-semibold group-hover:text-accent">
                    {c.client.name ?? c.client.email}
                  </div>
                  <div className="text-xs text-steel/50">{c.client.email}</div>
                </div>
                <div className="flex items-center gap-4 text-xs text-steel/60">
                  <span>{open} open task{open === 1 ? "" : "s"}</span>
                  <span className={c.client.tier === "coaching" ? "text-accent" : "text-steel/50"}>{billing}</span>
                </div>
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
