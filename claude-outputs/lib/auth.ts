// Password verification and signed-cookie session.
// PBKDF2-SHA256 hash of the site password is embedded here as a constant.
// Repo must remain PRIVATE; treat these constants as secrets that gate everything.

const PBKDF2_ITERATIONS = 210_000;
const PBKDF2_SALT_HEX = "e9f7c3116538b0777f3becf20dcd4c1c";
const PBKDF2_HASH_HEX = "09dc71d8ac6acf12ec52aa1cc1074235a1a94d35901d75e2ebd3b9d0d6791a76";
const SIGNING_SECRET_HEX = "cb54244d895ea5346095d520d40223c22d627e4b583981d2b75e4cf08761619c";

export const COOKIE_NAME = "cdo-auth";
export const SESSION_TTL_SECONDS = 60 * 60 * 24 * 7; // 7 days

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

// Constant-time byte comparison.
function timingSafeEqual(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a[i] ^ b[i];
  return diff === 0;
}

export async function verifyPassword(submitted: string): Promise<boolean> {
  if (typeof submitted !== "string" || submitted.length === 0 || submitted.length > 256) {
    return false;
  }
  const enc = new TextEncoder().encode(submitted);
  const key = await crypto.subtle.importKey("raw", enc, { name: "PBKDF2" }, false, ["deriveBits"]);
  const derivedBuf = await crypto.subtle.deriveBits(
    {
      name: "PBKDF2",
      hash: "SHA-256",
      salt: hexToBytes(PBKDF2_SALT_HEX),
      iterations: PBKDF2_ITERATIONS,
    },
    key,
    32 * 8,
  );
  const derived = new Uint8Array(derivedBuf);
  return timingSafeEqual(derived, hexToBytes(PBKDF2_HASH_HEX));
}

// Signed session token. Payload is base64url(JSON), signature is HMAC-SHA256(payload, secret).
// Cookie value: <payload>.<sig>
export async function signSession(payload: object): Promise<string> {
  const payloadJson = JSON.stringify(payload);
  const payloadBytes = new TextEncoder().encode(payloadJson);
  const payloadB64 = base64UrlEncode(payloadBytes);
  const key = await crypto.subtle.importKey(
    "raw",
    hexToBytes(SIGNING_SECRET_HEX),
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
      hexToBytes(SIGNING_SECRET_HEX),
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
