import { STAGES } from "@/lib/coaching";
import { toggleTask } from "@/app/coaching/actions";
import { format } from "date-fns";

type Task = {
  id: string;
  stage: string;
  title: string;
  detail: string;
  status: string;
  dueDate: Date | null;
};

/**
 * Tasks grouped by the five-stage outline, each with a done/undone toggle.
 * Used by both the client portal and the coach view (server component; the
 * checkbox is a server-action form, no client JS needed).
 */
export function StageTasks({ tasks }: { tasks: Task[] }) {
  return (
    <div className="space-y-6">
      {STAGES.map((stage) => {
        const items = tasks.filter((t) => t.stage === stage.id);
        if (items.length === 0) return null;
        const done = items.filter((t) => t.status === "done").length;
        return (
          <div key={stage.id}>
            <div className="flex items-baseline justify-between border-b border-band pb-1">
              <h3 className="font-semibold">
                {stage.name} <span className="font-normal text-steel/50">· {stage.blurb}</span>
              </h3>
              <span className="text-xs text-steel/50">{done}/{items.length} done</span>
            </div>
            <ul className="mt-2 space-y-1.5">
              {items.map((t) => (
                <li key={t.id} className="flex items-start gap-3">
                  <form action={toggleTask}>
                    <input type="hidden" name="taskId" value={t.id} />
                    <button
                      type="submit"
                      aria-label={t.status === "done" ? "Mark not done" : "Mark done"}
                      className={`mt-0.5 flex h-5 w-5 items-center justify-center rounded border ${
                        t.status === "done" ? "border-accent bg-accent text-white" : "border-steel/40"
                      }`}
                    >
                      {t.status === "done" ? "✓" : ""}
                    </button>
                  </form>
                  <div className={t.status === "done" ? "text-steel/40 line-through" : ""}>
                    <div className="text-sm font-medium">{t.title}</div>
                    {t.detail && <div className="text-xs text-steel/60">{t.detail}</div>}
                    {t.dueDate && (
                      <div className="text-xs text-steel/50">due {format(new Date(t.dueDate), "MMM d")}</div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        );
      })}
      {tasks.length === 0 && <p className="text-sm text-steel/60">No tasks yet.</p>}
    </div>
  );
}
