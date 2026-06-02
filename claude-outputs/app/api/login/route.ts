import { NextRequest, NextResponse } from "next/server";
import { COOKIE_NAME, SESSION_TTL_SECONDS, signSession, verifyPassword } from "@/lib/auth";
import {
  checkLockout,
  clearFailures,
  getClientIp,
  mandatoryDelay,
  registerFailure,
} from "@/lib/rate-limit";

// Force Node runtime so the in-memory rate-limit Map persists across invocations
// within the same instance (Edge runtime resets state more aggressively).
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const ip = getClientIp(req, req.headers);

  // Lockout gate.
  const lock = checkLockout(ip);
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

  // Constant-overhead delay on every attempt to slow brute-force.
  await mandatoryDelay();

  let body: { password?: string } = {};
  try {
    body = await req.json();
  } catch {
    // ignore; treated as wrong
  }
  const submitted = body.password ?? "";
  const ok = await verifyPassword(submitted);
  if (!ok) {
    const { lockedNow, backoffMs } = registerFailure(ip);
    return NextResponse.json(
      {
        error: lockedNow
          ? "Locked out. Try again in 60 minutes."
          : "Invalid password.",
        backoffSeconds: Math.ceil(backoffMs / 1000),
      },
      { status: lockedNow ? 429 : 401 },
    );
  }

  clearFailures(ip);
  const exp = Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS;
  const token = await signSession({ exp });
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
