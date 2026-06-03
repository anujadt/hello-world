import { NextRequest, NextResponse } from "next/server";
import {
  COOKIE_NAME,
  SESSION_TTL_SECONDS,
  readSession,
  signSession,
  verifyPasswordForProject,
} from "@/lib/auth";
import { projectBySlug } from "@/lib/projects";
import {
  checkLockout,
  clearFailures,
  getClientIp,
  mandatoryDelay,
  registerFailure,
} from "@/lib/rate-limit";

// Node runtime so the in-memory rate-limit Map persists across invocations.
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Server-side diagnostic: emits a SHA-256 of the submitted password to the
// Vercel function log (NOT the response body). The hash is one-way so this
// doesn't expose the password to anyone reading logs; it lets me compare
// against the known SHA-256 of the correct password to confirm what was
// actually typed/pasted. Safe because the password itself is already known
// to the legitimate user.
async function logSubmitDiagnostic(slug: string, submitted: string, ok: boolean) {
  try {
    const bytes = new TextEncoder().encode(submitted);
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    const hex = Array.from(new Uint8Array(digest))
      .map((b) => b.toString(16).padStart(2, "0")).join("");
    console.log(
      `[login] project=${slug} length=${submitted.length} sha256=${hex} verified=${ok}`,
    );
  } catch (e) {
    console.log(`[login] diagnostic-error project=${slug} verified=${ok} err=${e}`);
  }
}

export async function POST(req: NextRequest) {
  const ip = getClientIp(req, req.headers);

  let body: { project?: string; password?: string } = {};
  try {
    body = await req.json();
  } catch {
    // ignore
  }
  const slug = (body.project ?? "").toString();
  const project = projectBySlug(slug);
  if (!project || project.status !== "protected") {
    await mandatoryDelay();
    return NextResponse.json({ error: "Unknown project." }, { status: 400 });
  }

  // Lockout per (ip, project).
  const lockKey = `${ip}|${slug}`;
  const lock = checkLockout(lockKey);
  if (lock.locked) {
    await mandatoryDelay();
    return NextResponse.json(
      {
        error: "Too many failed attempts. Try again later.",
        retryAfterSeconds: Math.ceil(lock.retryAfterMs / 1000),
      },
      { status: 429, headers: { "Retry-After": String(Math.ceil(lock.retryAfterMs / 1000)) } },
    );
  }

  // Mandatory delay every attempt.
  await mandatoryDelay();

  const submitted = body.password ?? "";
  const ok = await verifyPasswordForProject(slug, submitted);
  await logSubmitDiagnostic(slug, submitted, ok);
  if (!ok) {
    const { lockedNow, backoffMs } = registerFailure(lockKey);
    return NextResponse.json(
      {
        error: lockedNow ? "Locked out. Try again in 5 minutes." : "Invalid password.",
        backoffSeconds: Math.ceil(backoffMs / 1000),
      },
      { status: lockedNow ? 429 : 401 },
    );
  }

  clearFailures(lockKey);

  // Add the slug to the existing session's unlocked list, or start a fresh session.
  const existing = await readSession(req.cookies.get(COOKIE_NAME)?.value);
  const unlocked = new Set(existing?.unlocked ?? []);
  unlocked.add(slug);
  const exp = Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS;
  const token = await signSession({ exp, unlocked: Array.from(unlocked) });

  const res = NextResponse.json({ ok: true });
  res.cookies.set(COOKIE_NAME, token, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_TTL_SECONDS,
  });
  return res;
}
