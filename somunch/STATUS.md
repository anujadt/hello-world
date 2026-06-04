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
- [x] **Real mascot** — user uploaded the original 7200px PNG via GitHub; downscaled to 1200px
      (203 KB, transparency intact) → `src/assets/so-munch-frog.png`; favicon regenerated. SVG stand-in removed.
- [x] `npm install` (348 packages, clean)
- [x] `npm run build` (clean production build, ~3.8s)
- [x] Run locally (vite preview :4173) + screenshot desktop & mobile → **shown to user**
- [x] Real mascot wired in + tagline clean two-line break (user requests)
- [x] Verify DB write path: anon email-only insert ACCEPTED; no-contact insert REJECTED by RLS; table cleaned
- [x] **Full QA pass — see `QA.md`** (build · tsc 0 · lint 0 err · UI · RLS security · hygiene), all ✅
- [x] Commit & push to branch `claude/keen-johnson-byRwy`
- [ ] Vercel: create project (Root Directory = `somunch`) + env vars → deploy ← **awaiting user go-ahead**
- [ ] Post-deploy smoke test (open URL, submit form, confirm row)

## Key facts

- Supabase project: `so-munch` / ref `nyrtpuqrruwjculuneme` / region eu-central-1 / **$0 free tier**
- Supabase URL: `https://nyrtpuqrruwjculuneme.supabase.co`
- Branch: `claude/keen-johnson-byRwy` in `anujadt/hello-world`, app under `somunch/`
- Vercel team: `anujtwp-1602's projects`
- Deploy gate: **user reviews local build before any Vercel deploy**

## Open items / decisions

- Mascot: original art wired in (downscaled 8.3MB→203KB). ✅
- OG/social preview image: currently omitted; can add a 1200×630 image later.
- Vercel deploy: pending user go-ahead.
