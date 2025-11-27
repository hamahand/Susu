import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path';

export default defineConfig({
  base: '/app/',
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'logo.svg', 'apple-touch-icon.svg'],
      manifest: {
        name: 'SusuSave - Modern ROSCA Platform',
        short_name: 'SusuSave',
        description: 'Save together, grow together. Ghana\'s first hybrid ROSCA platform with automated Mobile Money integration.',
        theme_color: '#2E7D32',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait-primary',
        start_url: '/app/',
        scope: '/app/',
        icons: [
          {
            src: '/assets/favicon-16x16.svg',
            sizes: '16x16',
            type: 'image/svg+xml'
          },
          {
            src: '/assets/favicon-32x32.svg',
            sizes: '32x32',
            type: 'image/svg+xml'
          },
          {
            src: '/assets/logo-icon.svg',
            sizes: '192x192',
            type: 'image/svg+xml',
            purpose: 'any maskable'
          },
          {
            src: '/assets/apple-touch-icon.svg',
            sizes: '512x512',
            type: 'image/svg+xml'
          }
        ],
        shortcuts: [
          {
            name: 'My Groups',
            short_name: 'Groups',
            description: 'View your savings groups',
            url: '/app/dashboard',
            icons: [{ src: '/assets/logo-icon.svg', sizes: '96x96' }]
          },
          {
            name: 'Join Group',
            short_name: 'Join',
            description: 'Join a new group',
            url: '/app/groups/join',
            icons: [{ src: '/assets/logo-icon.svg', sizes: '96x96' }]
          }
        ],
        categories: ['finance', 'productivity']
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.sususave\.com\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 // 1 hour
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'utils': ['axios', 'date-fns']
        }
      }
    }
  }
});

