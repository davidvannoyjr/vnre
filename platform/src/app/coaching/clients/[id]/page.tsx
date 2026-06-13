import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { format } from "date-fns";
import { auth } from "@/lib/auth";
import { dbEnabled } from "@/lib/db";
import { getClientForCoach, STAGES } from "@/lib/coaching";
import { StageTasks } from "@/components/coaching/stage-tasks";
import { CheckoutLinkButton } from "@/components/coaching/checkout-link-button";
import { savePlan, addNote, toggleNoteShare, addTask } from "../../actions";

export const metadata = { title: "Client" };

export default async function CoachClientPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const session = await auth();
  if (!session?.user?.id) redirect("/login");
  if (session.user.role !== "coach" || !dbEnabled) redirect("/coaching");

  const c = await getClientForCoach(session.user.id, id);
  if (!c) notFound();

  return (
    <div className="mx-auto max-w-3xl px-4 py-16">
      <Link href="/coaching/clients" className="text-sm text-accent hover:underline">← All clients</Link>
      <h1 className="mt-3 text-3xl font-bold tracking-tight">{c.client.name ?? c.client.email}</h1>
      <p className="mt-1 text-steel/60">{c.client.email}</p>

      {/* Billing */}
      <section className="mt-8 rounded-lg border border-band p-5">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-semibold">Billing</div>
            <div className="text-xs text-steel/60">
              {c.client.tier === "coaching" ? "Active — $1,000/mo" : "Not billing yet"}
              {c.client.stripeCurrentPeriodEnd &&
                ` · renews ${format(new Date(c.client.stripeCurrentPeriodEnd), "MMM d, yyyy")}`}
            </div>
          </div>
        </div>
        <div className="mt-3">
          <CheckoutLinkButton profileId={c.id} />
        </div>
      </section>

      {/* Tasks */}
      <section className="mt-10">
        <h2 className="text-xl font-bold">Coaching outline</h2>
        <div className="mt-3">
          <StageTasks tasks={c.tasks} />
        </div>
        <form action={addTask} className="mt-5 space-y-2 rounded-lg border border-band p-4">
          <input type="hidden" name="profileId" value={c.id} />
          <div className="flex flex-wrap gap-2">
            <select name="stage" className="rounded-md border border-band px-2 py-2 text-sm">
              {STAGES.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
            <input name="title" required placeholder="Task title" className="flex-1 rounded-md border border-band px-3 py-2 text-sm" />
            <input name="dueDate" type="date" className="rounded-md border border-band px-2 py-2 text-sm" />
          </div>
          <input name="detail" placeholder="Detail (optional)" className="w-full rounded-md border border-band px-3 py-2 text-sm" />
          <button className="rounded-md bg-steel px-4 py-2 text-sm font-medium text-white hover:opacity-90">Add task</button>
        </form>
      </section>

      {/* Business plan */}
      <section className="mt-12">
        <h2 className="text-xl font-bold">Business plan</h2>
        <form action={savePlan} className="mt-3 space-y-3">
          <input type="hidden" name="profileId" value={c.id} />
          <textarea
            name="content"
            defaultValue={c.plan?.content ?? ""}
            rows={12}
            className="w-full rounded-md border border-band p-3 font-mono text-sm"
          />
          <button className="rounded-md bg-steel px-4 py-2 text-sm font-medium text-white hover:opacity-90">Save plan</button>
        </form>
      </section>

      {/* Notes */}
      <section className="mt-12">
        <h2 className="text-xl font-bold">Coaching notes</h2>
        <p className="mt-1 text-sm text-steel/60">Private to you unless you share a note.</p>
        <form action={addNote} className="mt-3 space-y-2">
          <input type="hidden" name="profileId" value={c.id} />
          <textarea name="body" required rows={3} placeholder="New note…" className="w-full rounded-md border border-band p-3 text-sm" />
          <label className="flex items-center gap-2 text-sm text-steel/70">
            <input type="checkbox" name="share" /> Share this note with the client
          </label>
          <button className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:opacity-90">Add note</button>
        </form>

        <ul className="mt-5 space-y-3">
          {c.notes.length === 0 && <li className="text-sm text-steel/60">No notes yet.</li>}
          {c.notes.map((n) => (
            <li key={n.id} className="rounded-md border border-band p-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-steel/50">{format(new Date(n.createdAt), "MMM d, yyyy")}</span>
                <form action={toggleNoteShare}>
                  <input type="hidden" name="noteId" value={n.id} />
                  <button className={`text-xs ${n.sharedWithClient ? "text-accent" : "text-steel/50"} hover:underline`}>
                    {n.sharedWithClient ? "Shared — make private" : "Private — share"}
                  </button>
                </form>
              </div>
              <div className="mt-1 whitespace-pre-wrap text-sm">{n.body}</div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
