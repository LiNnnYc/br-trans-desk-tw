// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import remarkCjkFriendly from 'remark-cjk-friendly';
import { remarkCodeFigure } from './scripts/remark-code-figure.mjs';
import { remarkTableNowrap } from './scripts/remark-table-nowrap.mjs';
import { remarkFancyLists } from './scripts/remark-fancy-lists.mjs';
import { rehypeTableCaption } from './scripts/rehype-table-caption.mjs';

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
    // remarkFancyLists：補上 CommonMark 不支援的字母（a. b.）／羅馬數字（i. ii.）
    // 巢狀清單，使排版對齊 cabforum.org 的 <ol type="a"> / <ol type="i">。
    remarkPlugins: [remarkCjkFriendly, remarkCodeFigure, remarkTableNowrap, remarkFancyLists],
    // rehypeTableCaption：把表格上方的 `Table:`／`表：` 段落（由
    // scripts/restore_table_captions.py 回填）轉成表格內 <caption>，
    // 搭配 global.css `caption-side: bottom` 顯示於表格底端。
    rehypePlugins: [rehypeTableCaption],
  },
  vite: {
    // tailwind 4.3 的 vite plugin 與 Astro 內建 vite 型別有 skew，build 正常；
    // 用 any 繞過 `npm run check` 的型別錯誤，待上游對齊後可移除
    plugins: [/** @type {any} */ (tailwindcss())],
  },
});
