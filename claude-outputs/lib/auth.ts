// Password verification and signed-cookie session.
//
// Secrets resolve in this order:
//   1. SITE_PASSWORD env var (plaintext). If set, its PBKDF2 hash is used for verification.
//   2. PBKDF2_HASH_HEX constant below (build-time hash of the original password).
//
// SITE_SECRET env var overrides SIGNING_SECRET_HEX for session cookie signing.
//
// If the repo is PUBLIC, you MUST set SITE_PASSWORD and SITE_SECRET in Vercel env vars,
// otherwise the password hash and signing secret are readable in source.
// If the repo is PRIVATE, the in-source constants are acceptable and no env vars are needed.

const PBKDF2_ITERATIONS = 210_000;
const PBKDF2_SALT_HEX = "e9f7c3116538b0777f3becf20dcd4c1c";
const PBKDF2_HASH_HEX = "09dc71d8ac6acf12ec52aa1cc1074235a1a94d35901d75e2ebd3b9d0d6791a76";
const SIGNING_SECRET_HEX = "cb54244d895ea5346095d520d40223c22d627e4b583981d2b75e4cf08761619c";

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

async function pbkdf2Bits(password: string, saltBytes: Uint8Array): Promise<Uint8Array> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(password),
    { name: "PBKDF2" },
    false,
    ["deriveBits"],
  );
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", hash: "SHA-256", salt: saltBytes, iterations: PBKDF2_ITERATIONS },
    key,
    32 * 8,
  );
  return new Uint8Array(bits);
}

// Cache the env-derived hash; only recompute if SITE_PASSWORD value changes.
let envHashCache: Uint8Array | null = null;
let envHashCachedFor: string | null = null;

async function expectedHash(): Promise<Uint8Array> {
  const envPw = process.env.SITE_PASSWORD;
  if (envPw && envPw.length > 0) {
    if (envHashCache && envHashCachedFor === envPw) return envHashCache;
    envHashCache = await pbkdf2Bits(envPw, hexToBytes(PBKDF2_SALT_HEX));
    envHashCachedFor = envPw;
    return envHashCache;
  }
  return hexToBytes(PBKDF2_HASH_HEX);
}

function signingKeyBytes(): Uint8Array {
  const envSecret = process.env.SITE_SECRET;
  if (envSecret && /^[0-9a-fA-F]{32,}$/.test(envSecret)) return hexToBytes(envSecret);
  return hexToBytes(SIGNING_SECRET_HEX);
}

export async function verifyPassword(submitted: string): Promise<boolean> {
  if (typeof submitted !== "string" || submitted.length === 0 || submitted.length > 256) {
    return false;
  }
  const derived = await pbkdf2Bits(submitted, hexToBytes(PBKDF2_SALT_HEX));
  const expected = await expectedHash();
  return timingSafeEqual(derived, expected);
}

export async function signSession(payload: object): Promise<string> {
  const payloadJson = JSON.stringify(payload);
  const payloadB64 = base64UrlEncode(new TextEncoder().encode(payloadJson));
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

export async function verifySession(token: string | undefined): Promise<boolean> {
  if (!token || typeof token !== "string") return false;
  const parts = token.split(".");
  if (parts.length !== 2) return false;
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
    if (!valid) return false;
    const payload = JSON.parse(new TextDecoder().decode(base64UrlDecode(payloadB64))) as {
      exp?: number;
    };
    if (!payload.exp || Date.now() / 1000 > payload.exp) return false;
    return true;
  } catch {
    return false;
  }
}
