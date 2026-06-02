# claude-outputs

Private dashboard for visualizing Claude Code analysis outputs. First payload is the Abu Dhabi
DARI residential market analysis (2019 to 2026): insight memo, scorecard, opportunity shortlist,
triangulation against external sources, and chart gallery.

## Security

Password-protected at the application level via Next.js middleware. The site password is hashed
with PBKDF2-SHA256 (210k iterations) and the hash plus a session-signing secret are embedded as
constants in `lib/auth.ts`. The repo is **private** by design; treat these constants as gating
secrets.

Brute-force protection (`lib/rate-limit.ts`):

- Mandatory 300 ms delay on every login attempt.
- After 10 failed attempts within a 15-minute window, the IP is locked out for 60 minutes.
- PBKDF2 verify itself costs another ~80 ms per attempt.
- Constant-time HMAC comparison on session cookies; HttpOnly + Secure + SameSite=Lax.

Caveat: Vercel serverless instances are stateless across cold starts, so rate-limit state is
best-effort per region. For production-grade rate limiting, swap to Vercel KV / Upstash Ratelimit.
The combination of strong password + PBKDF2 + 300 ms delay makes brute-force impractical anyway.

## Stack

- Next.js 14 (App Router) + React 18
- Tailwind CSS
- TypeScript
- react-markdown for the memo, csv-parse for tables
- Auth via Web Crypto (PBKDF2 + HMAC) in middleware and API route
- Deploys to Vercel

## Run locally

```bash
npm install
npm run dev
```

Then visit http://localhost:3000 and enter the password.

## Deploy

This app lives at `claude-outputs/` inside the `anujadt/hello-world` repo on the `dashboard` branch.

In Vercel:

1. New Project, import `anujadt/hello-world`.
2. Production Branch: `dashboard` (set in Project Settings > Git after first import if needed).
3. Root Directory: `claude-outputs`.
4. Framework Preset: Next.js (auto-detected).
5. Deploy.

### Important security note

The password hash and session-signing secret live in `lib/auth.ts` as constants. That is only
safe if the repo is **private**. Two options:

- **Option A (recommended)**: keep `anujadt/hello-world` private. No env vars needed.
- **Option B**: set `SITE_PASSWORD` (plaintext) and `SITE_SECRET` (32+ byte hex) as Vercel env
  vars. The app prefers env vars over the in-source constants when present, so this is safe even
  if the repo is public.

See `.env.example` for variable names.
