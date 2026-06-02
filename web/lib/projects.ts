// Project manifest. Adding a new project means:
//   1. Drop assets in web/public/data/<slug>/
//   2. Add routes under web/app/<slug>/...
//   3. Add an entry below
//
// To gate a project with a password:
//   - Generate hash + signing-secret locally:
//       node -e "
//         const c=require('crypto'); const s=c.randomBytes(16);
//         const h=c.pbkdf2Sync('YOUR_PASSWORD', s, 210000, 32, 'sha256');
//         console.log('saltHex=' + s.toString('hex'));
//         console.log('hashHex=' + h.toString('hex'));
//         console.log('secretHex=' + c.randomBytes(32).toString('hex'));
//       "
//   - Set protected: true and embed the values, OR set env vars per .env.example.
//   - The middleware reads this manifest at every request and gates accordingly.

export type ProjectPage = {
  href: string;
  label: string;
};

export type ProjectAuth = {
  iterations: number;
  saltHex: string;
  hashHex: string;
  signingSecretHex: string;
};

export type Project = {
  slug: string;                   // URL segment, e.g. "real-estate"
  title: string;                  // Display name
  blurb: string;                  // 1-2 sentence pitch on landing page
  tags: string[];                 // For landing-page filtering later
  status: "public" | "protected"; // Public = open. Protected = password gate.
  auth?: ProjectAuth;             // Required when status === "protected"
  envVarPrefix?: string;          // Optional, e.g. "RE_" allows RE_PASSWORD / RE_SECRET overrides
  pages: ProjectPage[];           // Sub-nav inside the project
  accent?: string;                // Optional tailwind text-color class for card accent
};

export const PROJECTS: Project[] = [
  {
    slug: "real-estate",
    title: "Abu Dhabi Real Estate Investor Memo",
    blurb:
      "Investor-grade analysis of the Abu Dhabi residential market built from 114k DARI transactions, triangulated against ADREC, Bayut, and Cushman published reports.",
    tags: ["data", "finance", "real estate"],
    status: "protected",
    envVarPrefix: "RE_",
    auth: {
      iterations: 210_000,
      saltHex: "e9f7c3116538b0777f3becf20dcd4c1c",
      hashHex: "09dc71d8ac6acf12ec52aa1cc1074235a1a94d35901d75e2ebd3b9d0d6791a76",
      signingSecretHex: "cb54244d895ea5346095d520d40223c22d627e4b583981d2b75e4cf08761619c",
    },
    pages: [
      { href: "/real-estate", label: "Overview" },
      { href: "/real-estate/memo", label: "Insight memo" },
      { href: "/real-estate/scorecard", label: "Scorecard" },
      { href: "/real-estate/shortlist", label: "Shortlist" },
      { href: "/real-estate/triangulation", label: "Triangulation" },
      { href: "/real-estate/charts", label: "Charts" },
    ],
    accent: "text-emerald-400",
  },
];

export function projectBySlug(slug: string): Project | undefined {
  return PROJECTS.find((p) => p.slug === slug);
}

export function pickProjectForPath(pathname: string): Project | undefined {
  // /real-estate or /real-estate/anything matches the "real-estate" project.
  const seg = pathname.split("/").filter(Boolean)[0];
  if (!seg) return undefined;
  return projectBySlug(seg);
}
