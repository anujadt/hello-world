import { NextRequest, NextResponse } from "next/server";
import { COOKIE_NAME, isProjectUnlocked, readSession } from "@/lib/auth";
import { pickProjectForPath } from "@/lib/projects";

// Run on every path except the login flow and static assets.
export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|login|api/login|api/logout|data).*)"],
};

export async function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname;
  const project = pickProjectForPath(path);
  // Outside any project namespace (landing, about, etc.) or project is public: pass.
  if (!project || project.status === "public") return NextResponse.next();

  const session = await readSession(req.cookies.get(COOKIE_NAME)?.value);
  if (isProjectUnlocked(session, project.slug)) return NextResponse.next();

  const loginUrl = new URL("/login", req.url);
  loginUrl.searchParams.set("project", project.slug);
  loginUrl.searchParams.set("next", path);
  return NextResponse.redirect(loginUrl);
}
