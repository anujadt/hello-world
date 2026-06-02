# hello-world web

Public portfolio of projects built with Claude Code. Each project lives at its own URL with
its own data and (optionally) its own password gate. Adding a new project is two changes:

1. Drop assets into `public/data/<slug>/`.
2. Add an entry to `lib/projects.ts`. Pages live under `app/<slug>/`.

## Current projects

- `/real-estate` — Abu Dhabi DARI residential market analysis. Password-protected.
  Backed by `public/data/real-estate/` (insight memo, charts, scorecards, triangulation).

## Per-project password protection

Per-project: each entry in `lib/projects.ts` declares `status: "public" | "protected"`.
Protected projects ship with PBKDF2-SHA256 hash, salt, and a session signing secret in source.
Env vars (per-project) override the in-source values when set:

- `<PREFIX>PASSWORD` — plaintext, overrides the embedded hash.
- `<PREFIX>SECRET` — 32+ byte hex, overrides the session signing secret.

`real-estate` uses prefix `RE_` (see `.env.example`).

Brute-force protection (`lib/rate-limit.ts`):

- 300 ms mandatory delay per attempt.
- After 10 failed attempts in 15 minutes on a given (IP, project), that pair is locked for 60 min.
- PBKDF2 verify adds another ~80 ms.
- Sessions: signed HMAC-SHA256 cookies, HttpOnly + Secure + SameSite=Lax, 7-day TTL.

Cookie payload lists all projects the visitor has unlocked, so logging into one project does not
log you into others.

## Stack

Next.js 14 App Router, React 18, Tailwind, TypeScript, react-markdown, csv-parse, Web Crypto
(PBKDF2 + HMAC) in middleware and API routes.

## Run locally

```bash
npm install
npm run dev
```

## Deploy

In Vercel, set Project Root Directory to `web/` and deploy from `master` (or whichever branch).
If the repo is public, set `RE_PASSWORD` and `RE_SECRET` env vars in Vercel for the real-estate
project. If private, no env vars needed.

## Adding a new project (template)

1. Pick a slug, e.g. `mlb-pitch-quality`.
2. Drop assets in `public/data/mlb-pitch-quality/` (charts/, csvs/, markdown).
3. Create routes in `app/mlb-pitch-quality/` (a `page.tsx`, optional sub-pages).
4. Add to `lib/projects.ts`:

```ts
{
  slug: "mlb-pitch-quality",
  title: "MLB Pitch-quality Model",
  blurb: "Short pitch.",
  tags: ["baseball", "ml"],
  status: "public",
  pages: [
    { href: "/mlb-pitch-quality", label: "Overview" },
    // ...
  ],
}
```

5. Build, commit, push. The landing page picks it up automatically.
