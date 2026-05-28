import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { meCommerceBffPlugin } from "./dev/meCommerceBffPlugin";

const rootDir = path.dirname(fileURLToPath(import.meta.url));

/** 开发/预览响应头：减轻浏览器与内置预览对已删除 chunk 的过期缓存导致的报错 */
const noStoreHeaders = { "Cache-Control": "no-store" } as const;

/** 用户侧页面原型；与后台 Demo `src/admin`（5174）错开端口 */
export default defineConfig({
  plugins: [react(), ...(process.env.VITEST ? [] : [meCommerceBffPlugin()])],
  server: {
    port: 5175,
    headers: noStoreHeaders,
  },
  preview: {
    headers: noStoreHeaders,
  },
  resolve: {
    alias: { "@": path.resolve(rootDir, "src") },
  },
});
