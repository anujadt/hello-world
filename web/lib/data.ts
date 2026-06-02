import { promises as fs } from "node:fs";
import path from "node:path";
import { parse } from "csv-parse/sync";

const DATA = path.join(process.cwd(), "public", "data");

function projectRoot(slug: string): string {
  return path.join(DATA, slug);
}

export async function readMarkdown(slug: string, name: string): Promise<string> {
  return fs.readFile(path.join(projectRoot(slug), name), "utf8");
}

export async function readCsv(slug: string, name: string): Promise<Record<string, string>[]> {
  const raw = await fs.readFile(path.join(projectRoot(slug), "csvs", name), "utf8");
  return parse(raw, { columns: true, skip_empty_lines: true });
}

export async function listCharts(slug: string): Promise<string[]> {
  const dir = path.join(projectRoot(slug), "charts");
  const files = await fs.readdir(dir);
  return files.filter((f) => f.toLowerCase().endsWith(".png")).sort();
}

export async function listCsvs(slug: string): Promise<string[]> {
  const dir = path.join(projectRoot(slug), "csvs");
  const files = await fs.readdir(dir);
  return files.filter((f) => f.toLowerCase().endsWith(".csv")).sort();
}

export function chartUrl(slug: string, file: string): string {
  return `/data/${slug}/charts/${file}`;
}
