import { NextRequest, NextResponse } from "next/server";
import {
  COOKIE_NAME,
  SESSION_TTL_SECONDS,
  readSession,
  signSession,
} from "@/lib/auth";

export const runtime = "nodejs";

export async function GET(req: NextRequest) {
  const slug = req.nextUrl.searchParams.get("project");
  const session = await readSession(req.cookies.get(COOKIE_NAME)?.value);

  // Per-project signout: remove just that slug from unlocked array, keep cookie.
  if (slug && session) {
    const remaining = session.unlocked.filter((s) => s !== slug);
    const redirectTo = remaining.length ? "/" : "/";
    const res = NextResponse.redirect(new URL(redirectTo, req.url));
    if (remaining.length === 0) {
      res.cookies.set(COOKIE_NAME, "", {
        path: "/",
        maxAge: 0,
        httpOnly: true,
        secure: true,
        sameSite: "lax",
      });
    } else {
      const exp = Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS;
      const token = await signSession({ exp, unlocked: remaining });
      res.cookies.set(COOKIE_NAME, token, {
        path: "/",
        maxAge: SESSION_TTL_SECONDS,
        httpOnly: true,
        secure: true,
        sameSite: "lax",
      });
    }
    return res;
  }

  // No slug: sign out of everything.
  const res = NextResponse.redirect(new URL("/", req.url));
  res.cookies.set(COOKIE_NAME, "", {
    path: "/",
    maxAge: 0,
    httpOnly: true,
    secure: true,
    sameSite: "lax",
  });
  return res;
}
