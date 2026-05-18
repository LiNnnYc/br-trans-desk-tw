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
    // tailwind 4.3 的 vite plugin 與 Astro 內建 vite 型別有 skew，build 正常；
    // 用 any 繞過 `npm run check` 的型別錯誤，待上游對齊後可移除
    plugins: [/** @type {any} */ (tailwindcss())],
  },
});
