import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    // Vite 5's dev server rejects requests whose Host header it doesn't
    // recognize (DNS-rebinding protection) — needed so the site works when
    // reached through the production nginx reverse proxy on arss.uz.
    allowedHosts: ['arss.uz', 'www.arss.uz', 'localhost', '127.0.0.1'],
    watch: {
      usePolling: true,
    },
  }
})