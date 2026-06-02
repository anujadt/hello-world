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
  if (!ok) {
    const { lockedNow, backoffMs } = registerFailure(lockKey);
    return NextResponse.json(
      {
        error: lockedNow ? "Locked out. Try again in 60 minutes." : "Invalid password.",
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
