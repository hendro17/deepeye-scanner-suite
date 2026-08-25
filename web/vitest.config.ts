import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      reportsDirectory: './coverage',
      include: ['src/**/*.{ts,js,vue}'],
      exclude: [
        'node_modules/**',
        'dist/**',
        'src/**/*.spec.{ts,js}',
        'src/**/*.test.{ts,js}',
        'src/vite-env.d.ts',
        'src/main.ts',
      ],
    },
  },
})
