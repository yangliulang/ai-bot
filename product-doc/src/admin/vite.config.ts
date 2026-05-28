import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { skillSpecBffPlugin } from "./dev/skillSpecBffPlugin";

const adminRoot = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(adminRoot, "../..");

export default defineConfig({
  plugins: [react(), ...(process.env.VITEST ? [] : [skillSpecBffPlugin()])],
  resolve: {
    alias: {
      "@skill-specs": path.join(repoRoot, "specs/requirements/skill-specs"),
    },
  },
  server: {
    port: 5174,
    fs: { allow: [repoRoot] },
  },
});
