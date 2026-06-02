import { promises as fs } from "node:fs";
import path from "node:path";
import { parse } from "csv-parse/sync";

const DATA = path.join(process.cwd(), "public", "data");

export async function readMarkdown(name: string): Promise<string> {
  return fs.readFile(path.join(DATA, name), "utf8");
}

export async function readCsv(name: string): Promise<Record<string, string>[]> {
  const raw = await fs.readFile(path.join(DATA, "csvs", name), "utf8");
  return parse(raw, { columns: true, skip_empty_lines: true });
}

export async function listCharts(): Promise<string[]> {
  const dir = path.join(DATA, "charts");
  const files = await fs.readdir(dir);
  return files.filter((f) => f.toLowerCase().endsWith(".png")).sort();
}

export async function listCsvs(): Promise<string[]> {
  const dir = path.join(DATA, "csvs");
  const files = await fs.readdir(dir);
  return files.filter((f) => f.toLowerCase().endsWith(".csv")).sort();
}
