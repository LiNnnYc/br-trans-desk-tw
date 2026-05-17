// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  // 站台 URL 之後接到 GitHub Pages 時再補上 site/base
  i18n: {
    defaultLocale: 'zh-TW',
    locales: ['zh-TW'],
    routing: {
      prefixDefaultLocale: false,
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
