import { NextRequest, NextResponse } from "next/server";
import { projectBySlug } from "@/lib/projects";

export const runtime = "nodejs";

export async function GET(req: NextRequest) {
  const slug = req.nextUrl.searchParams.get("slug") ?? "";
  const project = projectBySlug(slug);
  if (!project) return NextResponse.json({ error: "Unknown project" }, { status: 404 });
  return NextResponse.json({
    slug: project.slug,
    title: project.title,
    protected: project.status === "protected",
  });
}
