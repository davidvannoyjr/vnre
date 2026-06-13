import { signIn, auth } from "@/lib/auth";
import { redirect } from "next/navigation";

export const metadata = { title: "Log in" };

export default async function LoginPage() {
  const session = await auth();
  if (session?.user) redirect("/dashboard");

  const hasEmail = !!process.env.AUTH_EMAIL_SERVER;
  const hasGoogle = !!process.env.AUTH_GOOGLE_ID;

  return (
    <div className="mx-auto max-w-md px-4 py-24">
      <h1 className="text-2xl font-bold tracking-tight">Log in</h1>
      <p className="mt-2 text-steel/70">Members get the magic link — no passwords.</p>

      {!hasEmail && !hasGoogle && (
        <div className="mt-6 rounded-md border border-band bg-strip p-4 text-sm text-steel/70">
          Auth providers aren&apos;t configured yet. Set <code className="font-mono">AUTH_EMAIL_SERVER</code>{" "}
          or Google credentials in <code className="font-mono">.env.local</code> to enable sign-in.
        </div>
      )}

      {hasEmail && (
        <form
          action={async (formData) => {
            "use server";
            await signIn("nodemailer", { email: formData.get("email") as string, redirectTo: "/dashboard" });
          }}
          className="mt-6 space-y-3"
        >
          <input
            type="email"
            name="email"
            required
            placeholder="you@brokerage.com"
            className="w-full rounded-md border border-band px-3 py-2"
          />
          <button className="w-full rounded-md bg-accent px-4 py-2 font-medium text-white">
            Email me a login link
          </button>
        </form>
      )}

      {hasGoogle && (
        <form
          action={async () => {
            "use server";
            await signIn("google", { redirectTo: "/dashboard" });
          }}
          className="mt-3"
        >
          <button className="w-full rounded-md border border-steel px-4 py-2 font-medium hover:bg-strip">
            Continue with Google
          </button>
        </form>
      )}
    </div>
  );
}
