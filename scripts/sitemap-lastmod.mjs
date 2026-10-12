// @astrojs/sitemap 的 lastmod 來源：網址 → 最後更新日（yyyy-mm-dd）。
//
// 兩種日期來源：
// 1. 內容 md 的 front-matter（astro.config 階段用不到 astro:content，這裡直接讀；只認單行
//    `key: value`，與 src/content.config.ts 的欄位對應）：
//      /server-cert-br/<id>/    ← br 的 last_updated
//      /quick-reference/<slug>/ ← quick-reference 的 last_updated
//      /news/<slug>/            ← news 的 date
// 2. 非動態的 .astro 頁面：該檔（＋它 import 的本機 .md ＋ PAGE_DEPS 列的資料檔）在 git 的最後 commit 日；
//    工作區有未提交修改時算今天（本機 build 用；CI 一定是已提交狀態）。
//    ⚠️ CI 的 actions/checkout 必須 fetch-depth: 0，淺 clone 下每個檔都會拿到 HEAD 的日期。
// 列表頁取兩者的最大值（例：章節目錄＝max(各章節 last_updated, table-of-contents.astro)）。
// 術語表各詞條頁（/glossary/<slug>/）刻意不給 lastmod——給錯日期比不給更糟。

import { execFileSync } from 'node:child_process';
import { readdirSync, readFileSync } from 'node:fs';
import { join, posix } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = fileURLToPath(new URL('../', import.meta.url));
const CONTENT = join(ROOT, 'src/content');

// 頁面內容主要來自其他檔案時，一併納入 git 日期的計算
const PAGE_DEPS = {
  '/changelog/': ['src/config/br-versions.ts'],
  '/glossary/': ['src/content/glossary', 'src/content/acronyms'],
  '/glossary/cert-fields/': ['src/config/cert-field-mappings.ts'],
};

const git = (...args) => execFileSync('git', args, { cwd: ROOT, encoding: 'utf8' }).trim();

function today() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

/** 這些路徑在 git 的最後修改日；有未提交修改則為今天；從未提交過則為 undefined */
function gitDate(paths) {
  if (git('status', '--porcelain', '--', ...paths)) return today();
  return git('log', '-1', '--format=%cs', '--', ...paths) || undefined;
}

/** src/pages 底下非動態、非 404 的 .astro → [網址, 原始檔] */
function staticPages() {
  const pages = join(ROOT, 'src/pages');
  return readdirSync(pages, { recursive: true })
    .map((f) => f.replaceAll('\\', '/'))
    .filter((f) => f.endsWith('.astro') && !f.includes('[') && f !== '404.astro')
    .map((f) => {
      const route = f.replace(/\.astro$/, '').replace(/(^|\/)index$/, '');
      return [route ? `/${route}/` : '/', `src/pages/${f}`];
    });
}

/** 頁面 import 的本機 .md（例：src/md/about-base-req.md，正文在那裡而不在 .astro） */
function importedMd(file) {
  const src = readFileSync(join(ROOT, file), 'utf8');
  return [...src.matchAll(/from\s+['"](\.{1,2}\/[^'"]+\.md)['"]/g)].map((m) =>
    posix.join(posix.dirname(file), m[1]),
  );
}

function readFrontMatter(dir) {
  const base = join(CONTENT, dir);
  return readdirSync(base)
    .filter((f) => f.endsWith('.md'))
    .map((f) => {
      const text = readFileSync(join(base, f), 'utf8');
      const fm = text.match(/^---\r?\n([\s\S]*?)\r?\n---/)?.[1] ?? '';
      const get = (key) =>
        fm.match(new RegExp(`^${key}:\\s*["']?([^"'\\r\\n]+?)["']?\\s*$`, 'm'))?.[1];
      return get;
    });
}

function toDate(value, where) {
  if (!value || !/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    throw new Error(`sitemap-lastmod：${where} 的日期格式不是 yyyy-mm-dd（${value}）`);
  }
  return value;
}

const max = (dates) => dates.reduce((a, b) => (b > a ? b : a));

export function buildLastmodMap(site) {
  const map = new Map();
  const set = (path, date) => map.set(new URL(path, site).href, date);

  const br = readFrontMatter('br').map((get) => {
    const id = get('section_id');
    return { path: `/server-cert-br/${id.replaceAll('.', '-')}/`, date: toDate(get('last_updated'), `br ${id}`) };
  });
  const qr = readFrontMatter('quick-reference').map((get) => ({
    path: `/quick-reference/${get('slug')}/`,
    date: toDate(get('last_updated'), `quick-reference ${get('slug')}`),
  }));
  const news = readFrontMatter('news').map((get) => ({
    path: `/news/${get('slug')}/`,
    date: toDate(get('date'), `news ${get('slug')}`),
  }));

  for (const e of [...br, ...qr, ...news]) set(e.path, e.date);

  // 列表頁的內容來自其下各頁
  const brMax = max(br.map((e) => e.date));
  const newsMax = max(news.map((e) => e.date));
  const listed = {
    '/server-cert-br/': brMax,
    '/server-cert-br/table-of-contents/': brMax,
    '/quick-reference/': max(qr.map((e) => e.date)),
    '/news/': newsMax,
    '/': newsMax, // 首頁主要的變動區塊是最新消息
  };

  for (const [path, file] of staticPages()) {
    const sources = [file, ...importedMd(file), ...(PAGE_DEPS[path] ?? [])];
    const dates = [gitDate(sources), listed[path]].filter(Boolean);
    if (dates.length) set(path, max(dates));
  }
  return map;
}
