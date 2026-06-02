// In-memory brute-force protection per IP.
//
// Caveat: Vercel serverless functions are stateless across cold starts and may run in
// multiple regions, so this Map is best-effort. The 32-character password plus
// PBKDF2 (~80 ms per verify) plus a 300 ms mandatory delay make brute-force
// economically infeasible regardless of this rate limit. For production-grade
// global tracking, swap this for Vercel KV / Upstash Ratelimit.

type Entry = {
  attempts: number;
  windowStart: number;
  lockedUntil: number;
};

const WINDOW_MS = 15 * 60 * 1000;       // 15 minutes
const MAX_ATTEMPTS_IN_WINDOW = 10;       // after the 10th failure, lock
const LOCK_MS = 60 * 60 * 1000;          // 1 hour lockout
const MIN_DELAY_MS = 300;                // every attempt waits at least this long

const store = new Map<string, Entry>();

export function getClientIp(req: Request, headers: Headers): string {
  // Trust Vercel's forwarded headers in production.
  const fwd = headers.get("x-forwarded-for");
  if (fwd) return fwd.split(",")[0].trim();
  const real = headers.get("x-real-ip");
  if (real) return real;
  return "unknown";
}

export function checkLockout(ip: string): { locked: boolean; retryAfterMs: number } {
  const e = store.get(ip);
  const now = Date.now();
  if (!e) return { locked: false, retryAfterMs: 0 };
  if (e.lockedUntil > now) {
    return { locked: true, retryAfterMs: e.lockedUntil - now };
  }
  // Reset window if expired.
  if (now - e.windowStart > WINDOW_MS) {
    store.delete(ip);
    return { locked: false, retryAfterMs: 0 };
  }
  return { locked: false, retryAfterMs: 0 };
}

export function registerFailure(ip: string): { lockedNow: boolean; backoffMs: number } {
  const now = Date.now();
  const existing = store.get(ip);
  let entry: Entry;
  if (!existing || now - existing.windowStart > WINDOW_MS) {
    entry = { attempts: 1, windowStart: now, lockedUntil: 0 };
  } else {
    entry = { ...existing, attempts: existing.attempts + 1 };
  }
  if (entry.attempts >= MAX_ATTEMPTS_IN_WINDOW) {
    entry.lockedUntil = now + LOCK_MS;
  }
  store.set(ip, entry);
  // Exponential backoff for the next retry, capped at 30 s.
  const backoffMs = Math.min(30_000, MIN_DELAY_MS * Math.pow(2, Math.max(0, entry.attempts - 1)));
  return { lockedNow: entry.lockedUntil > now, backoffMs };
}

export function clearFailures(ip: string): void {
  store.delete(ip);
}

export async function mandatoryDelay(): Promise<void> {
  await new Promise((r) => setTimeout(r, MIN_DELAY_MS));
}

export const RATE_LIMIT_CONFIG = {
  WINDOW_MS,
  MAX_ATTEMPTS_IN_WINDOW,
  LOCK_MS,
  MIN_DELAY_MS,
};
