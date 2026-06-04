# So Munch — decouple & deploy: STATUS

_Live progress tracker. Last updated: 2026-06-04._

**Goal:** Decouple the Lovable "So Munch" landing page → plain Vite + React SPA in `somunch/`,
backed by a new Supabase project, deployed on Vercel. UI/UX kept pixel-identical.

## Checklist
- [x] Explore Lovable export & confirm exact UI (TanStack Start → SPA)
- [x] Create new Supabase project `so-munch` (`nyrtpuqrruwjculuneme`, eu-central-1, free tier)
- [x] Apply DB schema (waitlist_signups + RLS insert policy + email column)
- [x] Generate Supabase TypeScript types
- [x] Scaffold Vite SPA (`somunch/`): package.json, vite/ts config, index.html, main.tsx, App.tsx
- [x] Port UI verbatim: styles.css, shadcn `components/ui/*`, hooks, lib, assets
- [x] Wire Supabase browser client (publishable key, RLS)
- [x] Local `.env.local` set with new Supabase URL + publishable key
- [ ] **Real mascot PNG** — blocked: env network policy blocks lovable.app. Using a temporary
      stand-in. Need `so-much-sweetness.lovable.app` allowlisted (or attach the PNG file).
- [x] `npm install` (348 packages, clean)
- [x] `npm run build` (clean production build, ~3.8s)
- [x] Run locally (vite preview :4173) + screenshot desktop & mobile → **shown to user**
- [ ] **Awaiting user OK on local build** before deploy
- [x] Verify DB write path: anon email-only insert ACCEPTED; no-contact insert REJECTED by RLS; table cleaned
- [x] Commit & push to branch `claude/keen-johnson-byRwy` (commit 74f423c)
- [ ] Vercel: create project (Root Directory = `somunch`) + env vars → deploy  ← **awaiting user go-ahead**
- [ ] Post-deploy smoke test (open URL, submit form, confirm row)

## Key facts
- Supabase project: `so-munch` / ref `nyrtpuqrruwjculuneme` / region eu-central-1 / **$0 free tier**
- Supabase URL: `https://nyrtpuqrruwjculuneme.supabase.co`
- Branch: `claude/keen-johnson-byRwy` in `anujadt/hello-world`, app under `somunch/`
- Vercel team: `anujtwp-1602's projects`
- Deploy gate: **user reviews local build before any Vercel deploy**

## Open items / decisions
- Mascot art: swap the temporary stand-in for the real `so-munch-frog.png` once
  the host is allowlisted or the file is attached.
- OG/social preview image: currently omitted; can add a 1200×630 image later.
