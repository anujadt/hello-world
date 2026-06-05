import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import tsconfigPaths from "vite-tsconfig-paths";

// Plain Vite + React 19 SPA. No SSR, no Cloudflare, no Lovable wrapper.
// Tailwind v4 is driven entirely from src/styles.css (@theme), so there is
// no tailwind.config.js. The `@/*` alias is read from tsconfig.json.
export default defineConfig({
  plugins: [react(), tailwindcss(), tsconfigPaths()],
});
