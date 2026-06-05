# So Munch — deployment repo handover

This repository is the **deployment home** for the "So Munch" waitlist landing page
(a UAE high-protein 1-minute cake mix). The app lives at the **root** of this repo.

It was decoupled from a Lovable export into a plain **Vite + React 19 SPA** (Tailwind v4 +
shadcn/ui) with a **Supabase** waitlist backend, then exported here from
`anujadt/hello-world` (branch `claude/keen-johnson-byRwy`, originally under `somunch/`,
see PR #3). UI/UX is pixel-faithful to the original Lovable page and has passed QA.

---

## What this repo is

- **Stack:** Vite 7 + React 19, Tailwind v4 (config lives in `src/styles.css` via `@theme`,
  no `tailwind.config.js`), shadcn/ui, `@supabase/supabase-js`, `zod`, `sonner`.
- **Single landing page** rendered client-side: wiggling mascot + "I LOVE CAKES SO MUNCH!"
  bubble, giant "SO MUNCH" wordmark, tagline (two lines), name/email waitlist form,
  "Launching online soon · UAE 🇦🇪" badge, and 60s/99/13g stats.
- **No SSR / no Cloudflare / no Lovable runtime, telemetry, or badge.** The form talks to
  Supabase directly from the browser via the publishable (anon) key; security is enforced by
  Postgres Row Level Security.
- Key files: `index.html`, `src/main.tsx`, `src/App.tsx`, `src/styles.css`,
  `src/integrations/supabase/{client.ts,types.ts}`, `src/assets/so-munch-frog.png` (the real
  mascot, downscaled), `vercel.json`. See also `STATUS.md` and `QA.md`.

## Supabase (already provisioned + QA-passed — do NOT recreate)

- Project: **`so-munch`** · ref **`nyrtpuqrruwjculuneme`** · region `eu-central-1` ·
  org `itqbhkumjgpnrvyinbdz` · free tier.
- URL: `https://nyrtpuqrruwjculuneme.supabase.co`
- Publishable (anon) key: `sb_publishable_sAy05iaz7H4v-gVMJvHjVQ_WE0w2pNK`
  (public-safe — RLS-gated; **never** add the service-role key to this app).
- Table `public.waitlist_signups` (id, phone, country_code default `+971`, name, source,
  user_agent, created_at, email). RLS **on**, single INSERT policy: anon may insert a row
  that has a phone OR email (validated); anon **cannot** read/update/delete. Verified.

## Environment variables (set these in Vercel: Production + Preview)

| Variable | Value |
| --- | --- |
| `VITE_SUPABASE_URL` | `https://nyrtpuqrruwjculuneme.supabase.co` |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | `sb_publishable_sAy05iaz7H4v-gVMJvHjVQ_WE0w2pNK` |

For local dev, create `.env.local` (git-ignored) with the same two lines, then
`npm install && npm run dev` → http://localhost:5173.

## Open tasks

1. **Deploy to Vercel** (team `anujtwp-1602's projects`):
   - Import this repo. Framework preset **Vite** (auto). **Root Directory = repo root** (the
     app is at root now — NOT a subfolder). Build `vite build`, output `dist`, install `npm install`.
   - Add the two env vars above (Production + Preview).
   - Deploy, then smoke-test: open the URL, submit the form, confirm a row landed in
     `waitlist_signups` (then delete the test row). Free **Hobby** tier is fine for a static
     site (commercial-ToS note: Pro is the strictly-correct tier for a commercial brand).
2. **Custom domain (GoDaddy)** — keep GoDaddy as registrar, just point DNS at Vercel:
   - Vercel → Project → Settings → Domains → add `yourdomain.com` (+ `www`).
   - At GoDaddy DNS: **A** `@` → `76.76.21.21`; **CNAME** `www` → `cname.vercel-dns-0.com`
     (use the exact value Vercel shows). Remove GoDaddy parking record + turn off Domain
     Forwarding. SSL auto-issues. If the domain is used for **email**, keep this A+CNAME method
     (do NOT switch nameservers, or you'll have to recreate MX records).
3. Optional: add a 1200×630 OG/social preview image (currently omitted); enable the ported-but-
   unmounted `FinalCTA`/`Footer` sections in `src/App.tsx` if desired.

## Guardrails

- Keep the UI **pixel-faithful**; the hero mascot is the original art at
  `src/assets/so-munch-frog.png` — don't replace it.
- `npm run build` must stay green; `tsc --noEmit` is clean; `npm run lint` has 0 errors
  (a few benign react-refresh warnings from stock shadcn components).

## How this repo was populated (for reference / re-sync)

Exported from `anujadt/hello-world` with `git subtree split --prefix=somunch` so the app sits
at the repo root with its commit history.
