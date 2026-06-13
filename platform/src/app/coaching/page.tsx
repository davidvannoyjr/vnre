import Link from "next/link";
import { redirect } from "next/navigation";
import { format } from "date-fns";
import { auth } from "@/lib/auth";
import { dbEnabled } from "@/lib/db";
import { getMyClientWorkspace } from "@/lib/coaching";
import { StageTasks } from "@/components/coaching/stage-tasks";
import { savePlan } from "./actions";
import { siteConfig } from "../../../site.config";

export const metadata = { title: "Coaching" };

export default async function CoachingPage() {
  const session = await auth();

  if (!session?.user?.id) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-24 text-center">
        <h1 className="text-2xl font-bold">1:1 Coaching</h1>
        <p className="mt-2 text-steel/70">Log in to reach your coaching workspace.</p>
        <Link href="/login" className="mt-6 inline-block rounded-md bg-accent px-5 py-2.5 text-white">Log in</Link>
      </div>
    );
  }

  // Coaches manage clients elsewhere.
  if (session.user.role === "coach") redirect("/coaching/clients");

  const workspace = dbEnabled ? await getMyClientWorkspace(session.user.id) : null;

  if (!workspace) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-24 text-center">
        <h1 className="text-2xl font-bold">You're not enrolled in 1:1 coaching.</h1>
        <p className="mt-3 text-steel/70">
          1:1 coaching with DVN is invite-only and capped. Want in? Reach out at{" "}
          <a href={`mailto:${siteConfig.contactEmail}`} className="text-accent underline">
            {siteConfig.contactEmail}
          </a>.
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-16">
      <h1 className="text-3xl font-bold tracking-tight">Your coaching workspace</h1>
      <p className="mt-2 text-steel/70">
        Coach: {workspace.coach.name ?? workspace.coach.email}. Work the plan; check off the tasks.
      </p>

      {/* Tasks by stage */}
      <section className="mt-10">
        <h2 className="text-xl font-bold">Your outline</h2>
        <p className="mt-1 text-sm text-steel/60">Forge → Conquer → Anchor → Architect → Own.</p>
        <div className="mt-4">
          <StageTasks tasks={workspace.tasks} />
        </div>
      </section>

      {/* Business plan (shared, editable) */}
      <section className="mt-12">
        <h2 className="text-xl font-bold">Your business plan</h2>
        <form action={savePlan} className="mt-3 space-y-3">
          <input type="hidden" name="profileId" value={workspace.id} />
          <textarea
            name="content"
            defaultValue={workspace.plan?.content ?? ""}
            rows={14}
            placeholder="Your living business plan — goals, numbers, strategy."
            className="w-full rounded-md border border-band p-3 font-mono text-sm"
          />
          <button className="rounded-md bg-steel px-4 py-2 text-sm font-medium text-white hover:opacity-90">
            Save plan
          </button>
          {workspace.plan?.updatedAt && (
            <span className="ml-3 text-xs text-steel/50">
              updated {format(new Date(workspace.plan.updatedAt), "MMM d, yyyy")}
            </span>
          )}
        </form>
      </section>

      {/* Notes shared by the coach */}
      <section className="mt-12">
        <h2 className="text-xl font-bold">Notes from your coach</h2>
        <ul className="mt-3 space-y-3">
          {workspace.notes.length === 0 && (
            <li className="text-sm text-steel/60">No shared notes yet.</li>
          )}
          {workspace.notes.map((n) => (
            <li key={n.id} className="rounded-md border border-band bg-strip p-3">
              <div className="text-xs text-steel/50">{format(new Date(n.createdAt), "MMM d, yyyy")}</div>
              <div className="mt-1 whitespace-pre-wrap text-sm">{n.body}</div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
