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

- Next.js 15 (App Router) + React 19
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

Push to GitHub and connect to Vercel (or use the Vercel CLI / MCP tool).
No environment variables required: everything needed to gate the site is in source code, which
is fine because the repo is private.
