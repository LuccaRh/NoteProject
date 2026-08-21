import { defineConfig } from 'vite'

const DAEMON = process.env.NOTESD_URL ?? 'http://127.0.0.1:8787'

export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: { usePolling: true },
    headers: {
      'Cross-Origin-Opener-Policy': 'same-origin',
      'Cross-Origin-Embedder-Policy': 'require-corp',
    },
    // O front chama /api/... na propria origem e o Vite repassa ao daemon.
    // Sem isso o COEP acima teria de negociar CORS com outra porta.
    proxy: {
      '/api': { target: DAEMON, changeOrigin: true, rewrite: p => p.replace(/^\/api/, '') },
    },
  },
})
