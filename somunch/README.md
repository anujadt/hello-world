# So Munch — landing page

The "So Munch" waitlist landing page, decoupled from Lovable into a plain
**Vite + React 19 SPA** styled with **Tailwind v4** + **shadcn/ui**, backed by
**Supabase** (a single `waitlist_signups` table with an RLS insert policy).

## Local development

```bash
cd somunch
cp .env.example .env.local   # then fill in your Supabase values
npm install
npm run dev                  # http://localhost:5173
```

## Build

```bash
npm run build                # outputs static files to dist/
npm run preview              # serve the production build locally
```

## Environment variables

| Variable                        | Description                                               |
| ------------------------------- | --------------------------------------------------------- |
| `VITE_SUPABASE_URL`             | Supabase project URL                                      |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Supabase publishable/anon key (safe to expose; RLS-gated) |

Set these in `.env.local` for local dev and in the Vercel project settings
(Production + Preview) for deploys.

## Deploy (Vercel)

This folder is a self-contained Vite app. On Vercel, create a project from the
`anujadt/hello-world` repo and set **Root Directory = `somunch`**. Vercel
auto-detects the Vite preset (build `vite build`, output `dist`). Add the two
environment variables above. Pushes to the tracked branch then auto-deploy.

## Notes

- No SSR/server code: the page is fully client-rendered and talks to Supabase
  directly from the browser. No Cloudflare/TanStack Start/Lovable runtime.
- Tailwind v4 is configured entirely in `src/styles.css` (`@theme`); there is no
  `tailwind.config.js`.
- `NotifyDialog` / `FinalCTA` / `WaitlistForm` / `Footer` in `src/App.tsx` are
  ported but not mounted (matching the live page), ready to enable later.
