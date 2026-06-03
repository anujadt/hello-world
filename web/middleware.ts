import { NextRequest, NextResponse } from "next/server";
import { COOKIE_NAME, isProjectUnlocked, readSession } from "./lib/auth";
import { pickProjectForPath, projectBySlug } from "./lib/projects";

// Run on every path except the login flow and Next.js internals.
// IMPORTANT: /data is NOT exempted. Files under public/data/<slug>/* are gated by the
// same project auth as their owning /<slug> route. Otherwise anyone could curl the raw
// CSVs and memos without authenticating.
export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|login|api/login|api/logout|api/project).*)"],
};

// Map a request path to its owning project slug, including /data/<slug>/* asset paths.
function projectForPath(pathname: string) {
  if (pathname.startsWith("/data/")) {
    const seg = pathname.split("/")[2];
    return seg ? projectBySlug(seg) : undefined;
  }
  return pickProjectForPath(pathname);
}

export async function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname;
  const project = projectForPath(path);
  // Outside any project namespace (landing, about, /data root etc.) or project is public: pass.
  if (!project || project.status === "public") return NextResponse.next();

  const session = await readSession(req.cookies.get(COOKIE_NAME)?.value);
  if (isProjectUnlocked(session, project.slug)) return NextResponse.next();

  const loginUrl = new URL("/login", req.url);
  loginUrl.searchParams.set("project", project.slug);
  // For raw-asset URLs, redirect to the project landing after login, not back to the asset.
  loginUrl.searchParams.set("next", path.startsWith("/data/") ? `/${project.slug}` : path);
  return NextResponse.redirect(loginUrl);
}
