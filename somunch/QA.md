# So Munch — QA report

_Validated 2026-06-04 against the decoupled Vite SPA in `somunch/` + Supabase project `nyrtpuqrruwjculuneme`._

Legend: ✅ pass.

## A. Build, types, lint

| ID  | Test                                             | Expected                          | Result |
| --- | ------------------------------------------------ | --------------------------------- | ------ |
| A1  | `npm install`                                    | clean, no errors                  | ✅ 348 pkgs |
| A2  | `npm run build`                                  | succeeds, emits `dist/`           | ✅ ~3.1s |
| A3  | `npx tsc --noEmit`                               | 0 type errors                     | ✅ exit 0 |
| A4  | `npm run lint`                                   | 0 errors                          | ✅ 0 errors (6 benign react-refresh warnings in stock shadcn ui) |
| A5  | `npm run format` idempotent                      | code prettier-clean               | ✅ |

## B. Frontend / UI (rendered at 1280px desktop + 390px mobile)

| ID  | Test                                             | Expected                                                | Result |
| --- | ------------------------------------------------ | ------------------------------------------------------- | ------ |
| B1  | Hero mascot                                      | original art (lips-frog + "I LOVE CAKES SO MUNCH!"), wiggle | ✅ |
| B2  | Wordmark                                         | "SO MUNCH" (Bowlby One), peach on plum                  | ✅ |
| B3  | Tagline                                          | two clean lines, breaks at the `·` point                | ✅ |
| B4  | Fonts load                                       | Bowlby One / DM Sans / Instrument Serif via Google      | ✅ |
| B5  | Colors / palette                                 | plum bg, peach text, pink-hot accents (Tailwind v4 tokens) | ✅ |
| B6  | Name/email pill inputs + NOTIFY ME button        | present, styled, focus ring                             | ✅ |
| B7  | "Launching online soon · UAE 🇦🇪" badge           | present                                                 | ✅ |
| B8  | 60s / 99 / 13g stats                             | present with dividers                                   | ✅ |
| B9  | Responsive (mobile 390px)                        | layout intact, no horizontal overflow                   | ✅ |
| B10 | Favicon                                          | mascot-derived favicon served                           | ✅ |

## C. Supabase data layer & RLS security

Tested by assuming the `anon` role in Postgres (identical to the browser's publishable-key path).

| ID  | Test                                                          | Expected                | Result |
| --- | ------------------------------------------------------------- | ----------------------- | ------ |
| C1  | Project status                                                | ACTIVE_HEALTHY          | ✅ |
| C2  | Table schema `waitlist_signups`                               | matches (8 cols, pk id) | ✅ |
| C3  | RLS enabled                                                   | true                    | ✅ |
| C4  | Policies                                                      | single INSERT policy for anon/authenticated with validation | ✅ |
| C5  | INSERT email-only (`inline-notify`)                           | accepted                | ✅ |
| C6  | INSERT phone-only (`landing`)                                 | accepted                | ✅ |
| C7  | INSERT neither phone nor email                                | REJECTED (RLS 42501)    | ✅ |
| C8  | INSERT invalid email                                          | REJECTED                | ✅ |
| C9  | INSERT non-digit phone                                        | REJECTED                | ✅ |
| C10 | anon SELECT                                                   | 0 rows (data not publicly readable) | ✅ |
| C11 | anon UPDATE                                                   | 0 rows affected         | ✅ |
| C12 | anon DELETE                                                   | 0 rows affected         | ✅ |
| C13 | Security advisors                                             | 0 lints                 | ✅ |
| C14 | Performance advisors                                          | 0 lints                 | ✅ |
| C15 | Test rows cleaned up                                          | table = 0 rows          | ✅ |

## D. Decoupling / hygiene (built `dist/`)

| ID  | Test                                                          | Expected            | Result |
| --- | ------------------------------------------------------------- | ------------------- | ------ |
| D1  | No Lovable telemetry/badge/CDN refs (`lovable`,`_flock`,`__l5e`,`gpteng`,`tinybird`) | none | ✅ |
| D2  | Supabase URL + publishable key inlined                        | present             | ✅ |
| D3  | No service-role / secret in bundle (`service_role`,`sb_secret`) | none              | ✅ |
| D4  | `index.html` meta/title/fonts                                 | correct, no lovable-badge | ✅ |
| D5  | `.env.local` git-ignored (only `.env.example` committed)      | yes                 | ✅ |
| D6  | Hero asset weight                                             | 8.3MB → 203KB (downscaled) | ✅ |

## Notes / non-blocking
- 6 react-refresh lint warnings originate from unmodified shadcn `ui/*` (e.g. `sidebar.tsx`, `toggle.tsx`) that export helpers alongside components — cosmetic, no runtime impact.
- JS bundle ~557KB (gzip ~158KB): React + Supabase + dialog/toaster. Acceptable for a single landing page; can code-split later if more pages are added.
- OG/social preview image intentionally omitted; add a 1200×630 image when desired.
