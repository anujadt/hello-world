// Project-aware auth. One signed session cookie lists every project the visitor
// has unlocked. The middleware checks `unlocked.includes(slug)` for protected projects.
//
// Each project carries its own PBKDF2 hash and signing secret in lib/projects.ts.
// Env vars override per-project: <ENV_PREFIX>PASSWORD and <ENV_PREFIX>SECRET.

import { PROJECTS, Project, projectBySlug } from "./projects";

export const COOKIE_NAME = "cdo-auth";
export const SESSION_TTL_SECONDS = 60 * 60 * 24 * 7;

function hexToBytes(hex: string): Uint8Array {
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(hex.substr(i * 2, 2), 16);
  return out;
}
function bytesToHex(bytes: Uint8Array): string {
  return Array.from(bytes).map((b) => b.toString(16).padStart(2, "0")).join("");
}
function base64UrlEncode(bytes: Uint8Array): string {
  const b64 = btoa(String.fromCharCode(...bytes));
  return b64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function base64UrlDecode(s: string): Uint8Array {
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  const bin = atob(s);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}
function timingSafeEqual(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a[i] ^ b[i];
  return diff === 0;
}

async function pbkdf2Bits(
  password: string,
  saltBytes: Uint8Array,
  iterations: number,
): Promise<Uint8Array> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(password),
    { name: "PBKDF2" },
    false,
    ["deriveBits"],
  );
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", hash: "SHA-256", salt: saltBytes, iterations },
    key,
    32 * 8,
  );
  return new Uint8Array(bits);
}

// All projects share one signed cookie, so they share one signing key. We pick the first
// protected project's secret (env-overridable). For public-only deployments, sessions are
// unused, so the placeholder key never matters.
function signingKeyBytes(): Uint8Array {
  const firstProtected = PROJECTS.find((p) => p.status === "protected");
  if (!firstProtected || !firstProtected.auth) {
    return new TextEncoder().encode("placeholder-signing-key-must-not-be-used".padEnd(32, "0"));
  }
  const envName = `${firstProtected.envVarPrefix ?? ""}SECRET`;
  const env = process.env[envName];
  if (env && /^[0-9a-fA-F]{32,}$/.test(env)) return hexToBytes(env);
  return hexToBytes(firstProtected.auth.signingSecretHex);
}

const envHashCache = new Map<string, { for: string; bytes: Uint8Array }>();

async function expectedHashForProject(project: Project): Promise<Uint8Array> {
  if (!project.auth) throw new Error(`Project ${project.slug} has no auth config`);
  const envName = `${project.envVarPrefix ?? ""}PASSWORD`;
  const envPw = process.env[envName];
  if (envPw && envPw.length > 0) {
    const cached = envHashCache.get(project.slug);
    if (cached && cached.for === envPw) return cached.bytes;
    const bytes = await pbkdf2Bits(
      envPw,
      hexToBytes(project.auth.saltHex),
      project.auth.iterations,
    );
    envHashCache.set(project.slug, { for: envPw, bytes });
    return bytes;
  }
  return hexToBytes(project.auth.hashHex);
}

export async function verifyPasswordForProject(slug: string, submitted: string): Promise<boolean> {
  const project = projectBySlug(slug);
  if (!project || project.status !== "protected" || !project.auth) return false;
  if (typeof submitted !== "string" || submitted.length === 0 || submitted.length > 256) return false;
  const derived = await pbkdf2Bits(
    submitted,
    hexToBytes(project.auth.saltHex),
    project.auth.iterations,
  );
  const expected = await expectedHashForProject(project);
  return timingSafeEqual(derived, expected);
}

export type SessionPayload = { exp: number; unlocked: string[] };

export async function signSession(payload: SessionPayload): Promise<string> {
  const payloadB64 = base64UrlEncode(new TextEncoder().encode(JSON.stringify(payload)));
  const key = await crypto.subtle.importKey(
    "raw",
    signingKeyBytes(),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = new Uint8Array(
    await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(payloadB64)),
  );
  return `${payloadB64}.${bytesToHex(sig)}`;
}

export async function readSession(token: string | undefined): Promise<SessionPayload | null> {
  if (!token || typeof token !== "string") return null;
  const parts = token.split(".");
  if (parts.length !== 2) return null;
  const [payloadB64, sigHex] = parts;
  try {
    const key = await crypto.subtle.importKey(
      "raw",
      signingKeyBytes(),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["verify"],
    );
    const valid = await crypto.subtle.verify(
      "HMAC",
      key,
      hexToBytes(sigHex),
      new TextEncoder().encode(payloadB64),
    );
    if (!valid) return null;
    const payload = JSON.parse(new TextDecoder().decode(base64UrlDecode(payloadB64))) as SessionPayload;
    if (!payload.exp || Date.now() / 1000 > payload.exp) return null;
    if (!Array.isArray(payload.unlocked)) return null;
    return payload;
  } catch {
    return null;
  }
}

export function isProjectUnlocked(session: SessionPayload | null, slug: string): boolean {
  if (!session) return false;
  return session.unlocked.includes(slug);
}
