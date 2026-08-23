/**
 * export_chapters_html.mjs — 把 /server-cert-br/ 全文頁的指定章節匯出成
 * 單一自足（self-contained）HTML 檔，供站外分享／離線參考。
 *
 * 特性：
 *   - 只保留中文：移除所有英文對照 blockquote 節點（不是靠 CSS 隱藏，是真的刪掉，
 *     複製文字不會夾帶英文）。
 *   - CSS 內嵌：把 build 產出的樣式表 inline 進 <style>，單檔即可開啟。
 *   - 站內連結（詳細頁）移除，cabforum.org 原文外連保留。
 *   - 附章節目錄 + 免責聲明（CLAUDE.md：免責文字為 load-bearing，不得移除）。
 *
 * 前置：先跑 `npm run build`（本腳本讀 dist/，不自行 build）。
 *
 * 用法：
 *   node scripts/export_chapters_html.mjs --chapters 1-6 --out "web-spec-doc/翻譯工作區/BR_ch1-6_zh-TW.html"
 */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as parse5 from 'parse5';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

// ---- 參數 -----------------------------------------------------------------
const argv = process.argv.slice(2);
function arg(name, fallback) {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : fallback;
}
const chapterSpec = arg('chapters', '1-6');
const outPath = resolve(ROOT, arg('out', `web-spec-doc/翻譯工作區/BR_ch${chapterSpec}_zh-TW.html`));

const [chFrom, chTo] = chapterSpec.includes('-')
  ? chapterSpec.split('-').map(Number)
  : [Number(chapterSpec), Number(chapterSpec)];

// ---- 讀取 build 產物 -------------------------------------------------------
const srcHtml = join(ROOT, 'dist/server-cert-br/index.html');
if (!existsSync(srcHtml)) {
  console.error(`找不到 ${srcHtml}，請先執行 npm run build`);
  process.exit(1);
}
const doc = parse5.parse(readFileSync(srcHtml, 'utf8'));

// ---- parse5 小工具 ---------------------------------------------------------
const attr = (node, name) => node.attrs?.find((a) => a.name === name)?.value ?? '';
const hasClass = (node, cls) => attr(node, 'class').split(/\s+/).includes(cls);
function* walk(node) {
  yield node;
  for (const child of node.childNodes ?? []) yield* walk(child);
}
function find(root, pred) {
  for (const n of walk(root)) if (n.nodeName !== '#text' && pred(n)) return n;
  return null;
}
function textOf(node) {
  let out = '';
  for (const n of walk(node)) if (n.nodeName === '#text') out += n.value;
  return out.trim().replace(/\s+/g, ' ');
}
/** 遞迴刪除符合 pred 的節點 */
function removeWhere(root, pred) {
  let removed = 0;
  const visit = (node) => {
    if (!node.childNodes) return;
    node.childNodes = node.childNodes.filter((c) => {
      if (c.nodeName !== '#text' && pred(c)) {
        removed++;
        return false;
      }
      return true;
    });
    node.childNodes.forEach(visit);
  };
  visit(root);
  return removed;
}
// ---- 取出全文 article、篩選章節 --------------------------------------------
const article = find(doc, (n) => n.tagName === 'article' && hasClass(n, 'full-text-only-cn'));
if (!article) {
  console.error('在全文頁找不到 <article class="full-text-only-cn">');
  process.exit(1);
}

const chapterOf = (secId) => {
  // sec-1-6-1 → 1；附錄（sec-appendix-a）回傳 NaN，不納入數字章節範圍
  const m = /^sec-(\d+)(?:-|$)/.exec(secId);
  return m ? Number(m[1]) : NaN;
};

const sections = (article.childNodes ?? []).filter(
  (n) => n.tagName === 'section' && hasClass(n, 'full-text-section')
);
const kept = sections.filter((s) => {
  const ch = chapterOf(attr(s, 'id'));
  return Number.isFinite(ch) && ch >= chFrom && ch <= chTo;
});
if (kept.length === 0) {
  console.error(`章節範圍 ${chapterSpec} 沒有匹配到任何 section`);
  process.exit(1);
}

// ---- 清理：刪英文 blockquote、刪站內連結 ------------------------------------
let removedQuotes = 0;
let removedLinks = 0;
for (const sec of kept) {
  removedQuotes += removeWhere(sec, (n) => n.tagName === 'blockquote');
  // 站外分享時「詳細頁」相對連結會失效，移除；cabforum.org 原文連結保留。
  removedLinks += removeWhere(sec, (n) => n.tagName === 'a' && attr(n, 'href').startsWith('/'));
}

// ---- 目錄（取 h2/h3 兩層，即 §X 與 §X.Y） ------------------------------------
const toc = [];
for (const sec of kept) {
  const id = attr(sec, 'id');
  const h = find(sec, (n) => /^h[2-6]$/.test(n.tagName ?? ''));
  if (!h) continue;
  const level = Number(h.tagName[1]);
  if (level > 3) continue;
  toc.push({ id, level, text: textOf(h).replace(/\s*原文\s*↗\s*$/, '').trim() });
}

// ---- CSS 內嵌 --------------------------------------------------------------
const head = find(doc, (n) => n.tagName === 'head');
const cssHrefs = [...walk(head)]
  .filter((n) => n.tagName === 'link' && attr(n, 'rel') === 'stylesheet')
  .map((n) => attr(n, 'href'));
const css = cssHrefs
  .map((href) => readFileSync(join(ROOT, 'dist', href.replace(/^\//, '')), 'utf8'))
  .join('\n');

// ---- 站台資訊 --------------------------------------------------------------
const siteTs = readFileSync(join(ROOT, 'src/config/site.ts'), 'utf8');
const version = /version:\s*'([^']+)'/.exec(siteTs)?.[1] ?? 'tbd';
const today = new Date().toISOString().slice(0, 10);

const chapterLabel = chFrom === chTo ? `第 ${chFrom} 章` : `第 ${chFrom}–${chTo} 章`;
const title = `CA/Browser Forum 基本要求 非官方繁體中文翻譯（${chapterLabel}）`;

const DISCLAIMER =
  '本翻譯為非官方翻譯，發生爭議時以 CA/Browser Forum 英文原文為準。';

const html = `<!doctype html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<style>
${css}
</style>
<style>
  body { background: #f1f5f9; }
  .export-wrap { max-width: 1000px; margin: 0 auto; padding: 1.5rem 1rem 4rem; }
  .export-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 0.375rem; padding: 1.75rem 1.5rem; }
  .export-notice { border: 1px solid #fcd34d; background: #fffbeb; color: #78350f;
    border-radius: 0.375rem; padding: 0.75rem 1rem; font-size: 0.875rem; line-height: 1.7; }
  .export-toc { margin-top: 1.5rem; border: 1px solid #e2e8f0; border-radius: 0.375rem; padding: 1rem 1.25rem; background: #f8fafc; }
  .export-toc ul { list-style: none; margin: 0.5rem 0 0; padding: 0; font-size: 0.9rem; }
  .export-toc li { margin: 0.15rem 0; }
  .export-toc li.lv3 { padding-left: 1.5rem; font-size: 0.85rem; }
  .export-toc a { color: #0d6efd; text-decoration: none; }
  .export-toc a:hover { text-decoration: underline; }
  .export-foot { margin-top: 2rem; font-size: 0.8rem; color: #64748b; line-height: 1.8; }
  @media print {
    body { background: #fff; }
    .export-card { border: 0; padding: 0; }
    .export-toc { break-after: page; }
  }
</style>
</head>
<body class="bg-slate-100 text-slate-900 antialiased">
<div class="export-wrap">
  <div class="export-card">
    <header style="border-bottom:1px solid #e2e8f0; padding-bottom:1rem; margin-bottom:1.25rem;">
      <h1 class="font-serif-tc" style="font-size:1.75rem; font-weight:700; line-height:1.3;">
        CA/Browser Forum<br>《Baseline Requirements for the Issuance and Management of Publicly-Trusted TLS Server Certificates》<br>非官方繁體中文翻譯 — ${chapterLabel}
      </h1>
      <p style="margin-top:0.75rem; font-size:0.875rem; color:#475569; line-height:1.8;">
        對應原文版本 <code>${version}</code>　·　匯出日期 ${today}　·　本檔僅含中文翻譯，未附英文原文。<br>
        內容範圍：${chapterLabel}（已完成人工審閱之章節）。
      </p>
      <p class="export-notice" style="margin-top:1rem;">
        ⚠️ ${DISCLAIMER}<br>
        本檔為參考用途，非 CA/Browser Forum 官方文件；原文請見
        <a href="https://cabforum.org/working-groups/server/baseline-requirements/documents/" target="_blank" rel="noopener noreferrer">cabforum.org</a>。
      </p>
    </header>

    <nav class="export-toc" aria-label="章節目錄">
      <strong style="font-size:0.9rem;">目錄</strong>
      <ul>
${toc.map((t) => `        <li class="lv${t.level}"><a href="#${t.id}">${t.text}</a></li>`).join('\n')}
      </ul>
    </nav>

    <article class="full-text-only-cn" style="margin-top:2rem;">
${kept.map((s) => parse5.serializeOuter(s)).join('\n')}
    </article>

    <footer class="export-foot">
      <p>⚠️ ${DISCLAIMER}</p>
      <p>本檔由「BRs 翻譯小站」原始碼於 ${today} 匯出，僅含${chapterLabel}。翻譯狀態、後續修訂與其餘章節以站台版本為準。</p>
    </footer>
  </div>
</div>
</body>
</html>
`;

writeFileSync(outPath, html, 'utf8');
console.log(`✔ 已匯出 ${outPath}`);
console.log(`  章節 section：${kept.length} 個（${chapterLabel}）`);
console.log(`  移除英文 blockquote：${removedQuotes} 個；移除站內連結：${removedLinks} 個`);
console.log(`  內嵌樣式表：${cssHrefs.join(', ')}`);
console.log(`  目錄項目：${toc.length}`);
