"use client";
import { useEffect, useRef, useState, FormEvent, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

type ProjectInfo = { slug: string; title: string; protected: boolean };

function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const next = params.get("next") || "/";
  const slug = params.get("project") || "";
  const [project, setProject] = useState<ProjectInfo | null>(null);
  const [pw, setPw] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [shake, setShake] = useState(false);
  const [attempts, setAttempts] = useState(0);
  const [lockedFor, setLockedFor] = useState(0); // seconds; only set on a real lockout (429)
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!slug) return;
    fetch(`/api/project?slug=${encodeURIComponent(slug)}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => j && setProject(j))
      .catch(() => undefined);
  }, [slug]);

  // Lockout countdown tick (only runs when actually locked out).
  useEffect(() => {
    if (lockedFor <= 0) return;
    const id = setInterval(() => setLockedFor((c) => Math.max(0, c - 1)), 1000);
    return () => clearInterval(id);
  }, [lockedFor]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (busy || lockedFor > 0 || pw.length === 0) return;
    setBusy(true);
    setErr(null);
    try {
      const r = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project: slug, password: pw }),
      });
      if (r.ok) {
        router.replace(next);
        return;
      }
      const j = (await r.json().catch(() => ({}))) as {
        error?: string;
        retryAfterSeconds?: number;
      };
      const nextAttempts = attempts + 1;
      setAttempts(nextAttempts);

      if (r.status === 429) {
        // Genuine lockout: honor the server's wait window.
        const wait = j.retryAfterSeconds ?? 3600;
        setLockedFor(wait);
        setErr(j.error ?? "Too many attempts. Take a short break and try again.");
      } else {
        // Plain wrong password: friendly, immediate retry allowed. Nudge after a few misses.
        const base = "That password did not work.";
        const hint =
          nextAttempts >= 3
            ? " Double-check for stray spaces or a missed character; the field is case-sensitive."
            : "";
        setErr(base + hint);
      }
      // Shake + clear + refocus, but do NOT force a wait for a simple typo.
      setShake(true);
      setTimeout(() => setShake(false), 400);
      setPw("");
      requestAnimationFrame(() => inputRef.current?.focus());
    } catch {
      setErr("Network hiccup. Give it a moment and try again.");
    } finally {
      setBusy(false);
    }
  }

  const title = project?.title ?? (slug || "Locked");
  const locked = lockedFor > 0;
  const disabled = busy || pw.length === 0 || !slug || locked;
  const buttonLabel = locked
    ? `Locked, retry in ${formatDuration(lockedFor)}`
    : busy
      ? "Checking..."
      : "Enter";

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950 text-zinc-100 p-6">
      <form
        onSubmit={onSubmit}
        className={`w-full max-w-sm space-y-4 bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-xl ${
          shake ? "cdo-shake" : ""
        }`}
      >
        <div>
          <div className="text-xs text-zinc-500 uppercase tracking-wide">Locked project</div>
          <h1 className="text-lg font-semibold mt-1">{title}</h1>
          <p className="text-sm text-zinc-400 mt-1">Enter the project password.</p>
        </div>
        <input
          ref={inputRef}
          type="password"
          autoFocus
          autoComplete="current-password"
          value={pw}
          onChange={(e) => {
            setPw(e.target.value);
            if (err) setErr(null);
          }}
          disabled={locked}
          className={`w-full px-3 py-2 rounded-md bg-zinc-950 border focus:outline-none transition-colors ${
            err ? "border-amber-700/60 focus:border-amber-600" : "border-zinc-800 focus:border-zinc-600"
          } ${locked ? "opacity-50 cursor-not-allowed" : ""}`}
          placeholder="Password"
        />
        {err && (
          <div className="text-sm text-amber-300/90 bg-amber-950/30 border border-amber-900/40 rounded-md px-3 py-2">
            {err}
          </div>
        )}
        <button
          type="submit"
          disabled={disabled}
          className="w-full py-2 rounded-md bg-zinc-100 text-zinc-900 font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
        >
          {buttonLabel}
        </button>
        <p className="text-xs text-zinc-500">
          You can retry immediately. After 10 rapid failed attempts this IP pauses for a while as a
          brute-force guard.
        </p>
        <p className="text-xs text-zinc-600">
          <a href="/" className="hover:text-zinc-400">Back to projects</a>
        </p>
      </form>
    </div>
  );
}

function formatDuration(sec: number): string {
  if (sec >= 60) {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return s ? `${m}m ${s}s` : `${m}m`;
  }
  return `${sec}s`;
}

export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <LoginForm />
    </Suspense>
  );
}
