import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()],
  // In development the API runs on its own port. In production FastAPI serves both.
  server: { proxy: { '/api': 'http://localhost:8000' } },
  test: { environment: 'jsdom', setupFiles: './src/test/setup.ts' },
})
