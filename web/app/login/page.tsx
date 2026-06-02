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
  const [cooldown, setCooldown] = useState(0);
  const [locked, setLocked] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!slug) return;
    fetch(`/api/project?slug=${encodeURIComponent(slug)}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => j && setProject(j))
      .catch(() => undefined);
  }, [slug]);

  // Cooldown tick.
  useEffect(() => {
    if (cooldown <= 0) return;
    const id = setInterval(() => setCooldown((c) => Math.max(0, c - 1)), 1000);
    return () => clearInterval(id);
  }, [cooldown]);

  // When cooldown finishes after a lockout, allow retry by clearing the locked flag.
  useEffect(() => {
    if (locked && cooldown === 0) setLocked(false);
  }, [cooldown, locked]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (busy || locked || cooldown > 0) return;
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
        backoffSeconds?: number;
        retryAfterSeconds?: number;
      };
      if (r.status === 429) {
        // Locked out for a longer window.
        const wait = j.retryAfterSeconds ?? 3600;
        setLocked(true);
        setCooldown(wait);
        setErr(j.error ?? "Too many attempts. Try again later.");
      } else {
        setErr(j.error ?? "That password did not work.");
        setCooldown(j.backoffSeconds ?? 1);
      }
      setShake(true);
      setTimeout(() => setShake(false), 380);
      setPw("");
      requestAnimationFrame(() => inputRef.current?.focus());
    } catch {
      setErr("Network hiccup. Try again in a moment.");
    } finally {
      setBusy(false);
    }
  }

  const title = project?.title ?? (slug || "Locked");
  const disabled = busy || pw.length === 0 || !slug || locked || cooldown > 0;
  const buttonLabel = locked
    ? `Locked, retry in ${formatDuration(cooldown)}`
    : cooldown > 0
      ? `Wait ${cooldown}s`
      : busy
        ? "Verifying..."
        : "Enter";

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950 text-zinc-100 p-6">
      <form
        onSubmit={onSubmit}
        className={`w-full max-w-sm space-y-4 bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-xl transition-transform ${
          shake ? "animate-[shake_360ms_ease-out]" : ""
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
          onChange={(e) => setPw(e.target.value)}
          disabled={locked}
          className={`w-full px-3 py-2 rounded-md bg-zinc-950 border focus:outline-none ${
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
          Rate-limited. 10 failed attempts in 15 minutes locks this IP for 60 minutes.
        </p>
        <p className="text-xs text-zinc-600">
          <a href="/" className="hover:text-zinc-400">Back to projects</a>
        </p>
      </form>

      <style jsx>{`
        @keyframes shake {
          0%   { transform: translateX(0); }
          15%  { transform: translateX(-8px); }
          30%  { transform: translateX(7px); }
          45%  { transform: translateX(-5px); }
          60%  { transform: translateX(4px); }
          75%  { transform: translateX(-2px); }
          100% { transform: translateX(0); }
        }
      `}</style>
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
