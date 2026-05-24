// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import remarkCjkFriendly from 'remark-cjk-friendly';
import { remarkCodeFigure } from './scripts/remark-code-figure.mjs';

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
  markdown: {
    // remark-cjk-friendly：修正 CJK + 全形括號 + **bold** 在原生 CommonMark 不被
    // 認定為 right-flanking 的問題（例：**應（MUST）**符合 原本不會渲染粗體）。
    // remarkCodeFigure：在 mdast 階段把 fenced code block 包進 <figure>（含語言
    // 標籤＋複製按鈕）；必須在 remark 階段而非 Shiki transformer 完成，因 Astro
    // 會在 Shiki 處理前把未知語言（如 ASN.1）改成 plaintext，transformer 內已抓
    // 不到原始 fence 標籤。複製按鈕的點擊行為由章節頁 client-side script 接管。
    remarkPlugins: [remarkCjkFriendly, remarkCodeFigure],
  },
  vite: {
    // tailwind 4.3 的 vite plugin 與 Astro 內建 vite 型別有 skew，build 正常；
    // 用 any 繞過 `npm run check` 的型別錯誤，待上游對齊後可移除
    plugins: [/** @type {any} */ (tailwindcss())],
  },
});
