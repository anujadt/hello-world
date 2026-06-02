"use client";
import { useState, FormEvent, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const next = params.get("next") || "/";
  const [pw, setPw] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      const r = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: pw }),
      });
      if (r.ok) {
        router.replace(next);
      } else {
        const j = await r.json().catch(() => ({}));
        setErr(j.error || `Login failed (${r.status})`);
      }
    } catch {
      setErr("Network error.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950 text-zinc-100 p-6">
      <form
        onSubmit={onSubmit}
        className="w-full max-w-sm space-y-4 bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-xl"
      >
        <div>
          <h1 className="text-lg font-semibold">claude-outputs</h1>
          <p className="text-sm text-zinc-400 mt-1">Private dashboard. Enter the password.</p>
        </div>
        <input
          type="password"
          autoFocus
          autoComplete="current-password"
          value={pw}
          onChange={(e) => setPw(e.target.value)}
          className="w-full px-3 py-2 rounded-md bg-zinc-950 border border-zinc-800 focus:border-zinc-600 focus:outline-none"
          placeholder="Password"
        />
        {err && <div className="text-sm text-red-400">{err}</div>}
        <button
          type="submit"
          disabled={busy || pw.length === 0}
          className="w-full py-2 rounded-md bg-zinc-100 text-zinc-900 font-medium disabled:opacity-50"
        >
          {busy ? "Verifying..." : "Enter"}
        </button>
        <p className="text-xs text-zinc-500">
          Rate-limited. After 10 failed attempts, this IP is locked for 60 minutes.
        </p>
      </form>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <LoginForm />
    </Suspense>
  );
}
