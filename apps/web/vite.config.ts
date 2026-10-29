import { defineConfig } from 'vite'

export default defineConfig({
    server: {
        host: '0.0.0.0',
        port: 5173,
        watch: { usePolling: true },
        // /api/notes -> <API_URL>/notes;
        // in compose the api is http://notes:8000
        proxy: {
            '/api': {
                target: process.env.API_URL ?? 'http://localhost:8000',
                rewrite: path => path.replace(/^\/api/, ''),
            },
        },
        headers: {
            'Cross-Origin-Opener-Policy': 'same-origin',
            'Cross-Origin-Embedder-Policy': 'require-corp',
        },
    },
})
