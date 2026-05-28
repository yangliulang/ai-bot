import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss(), vueDevTools()],
  server: {
    port: 5174,
    strictPort: false,
    // Vite 6+：公网隧道 Host 不在白名单会 403（含 /webhook 代理前的请求）。
    allowedHosts: ['.ngrok-free.dev', '.ngrok-free.app', '.ngrok.app', '.ngrok.io'],
    proxy: {
      '/api': { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/webhook': { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/health': { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/docs': { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/openapi.json': { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/redoc': { target: 'http://127.0.0.1:8080', changeOrigin: true },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
