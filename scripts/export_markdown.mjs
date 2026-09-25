/**
 * export_markdown.mjs — 把 br 章節檔串成單一 Markdown 檔（**只有中文**），供下載。
 *
 * 與 export_chapters_html.mjs 同一套取捨：
 *   - 英文原文一律是 blockquote（Style A），整段刪掉；中文段落原樣保留。
 *   - 每節標題前掛 `<a id="<原文錨點>">`（取自 front-matter 的 original_url），
 *     譯稿內沿用原文寫法的交叉參照 `(#7121-…)` 因此在同一份檔內可以互跳。
 *   - 註腳：同一 label 在多節各定義一份、內容相同（如 eku_ca），合併後統一放到檔尾。
 *   - 字母／羅馬數字清單（a. b.／i. ii.）是本站靠 remark-fancy-lists 才排得出來的，
 *     一般 Markdown 檢視器會把它們併成一行；這裡在前一行行尾補 `\`（CommonMark 硬換行），
 *     至少保住逐行顯示。
 *
 * 讀原始 md 而不是 dist，所以不需要先 build；`--src` 可指向從 git tag 取出的舊版章節檔。
 *
 * 用法：
 *   node scripts/export_markdown.mjs --out public/archive/BR_v2.3.0_zh-TW.md
 *   node scripts/export_markdown.mjs --src <某目錄> --version 2.2.7 --out public/archive/BR_v2.2.7_zh-TW.md
 */
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const argv = process.argv.slice(2);
function arg(name, fallback) {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : fallback;
}
const srcDir = resolve(ROOT, arg('src', 'src/content/br'));
const outArg = arg('out', null);
if (!outArg) {
  console.error('請以 --out 指定輸出檔');
  process.exit(1);
}
const outPath = resolve(ROOT, outArg);

// 版本：未指定時取 br-versions.ts 第一列（同 export_chapters_html.mjs，匹配不到就拋錯）
let version = arg('version', null);
if (!version) {
  const ts = readFileSync(join(ROOT, 'src/config/br-versions.ts'), 'utf8');
  version = /^\s*version:\s*'([^']+)'/m.exec(ts.slice(ts.indexOf('export const brVersions')))?.[1];
  if (!version) throw new Error('src/config/br-versions.ts 讀不到 brVersions[0].version');
}

// ---- 章節編號工具（同 src/lib/section.ts；那邊是 TS，node 直接 import 不了）----------
function parseAppendix(id) {
  const m = /^appendix-([a-z])((?:\.\d+)*)$/.exec(id);
  if (!m) return null;
  return { letter: m[1], nums: m[2] ? m[2].slice(1).split('.').map(Number) : [] };
}
function sortKey(id) {
  const app = parseAppendix(id);
  if (app) return [1, app.letter.charCodeAt(0), ...app.nums];
  return [0, ...id.split('.').map(Number)];
}
function compareSectionId(a, b) {
  const ak = sortKey(a);
  const bk = sortKey(b);
  for (let i = 0; i < Math.max(ak.length, bk.length); i++) {
    const av = ak[i] ?? -1;
    const bv = bk[i] ?? -1;
    if (av !== bv) return av - bv;
  }
  return 0;
}
function sectionIdToLabel(id) {
  const app = parseAppendix(id);
  if (!app) return id;
  const letter = app.letter.toUpperCase();
  return app.nums.length === 0 ? `附錄 ${letter}` : `${letter}.${app.nums.join('.')}`;
}

// ---- 讀章節檔 ----------------------------------------------------------------
function frontMatterField(fm, name) {
  const m = new RegExp(`^${name}:\\s*(.*)$`, 'm').exec(fm);
  if (!m) return null;
  return m[1].trim().replace(/^"(.*)"$/, '$1').replace(/\\"/g, '"');
}

const sections = readdirSync(srcDir)
  .filter((f) => f.endsWith('.md'))
  .map((f) => {
    const raw = readFileSync(join(srcDir, f), 'utf8').replace(/\r\n/g, '\n');
    const m = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/.exec(raw);
    if (!m) throw new Error(`${f}：找不到 front-matter`);
    const [, fm, body] = m;
    const id = frontMatterField(fm, 'section_id');
    const title = frontMatterField(fm, 'title');
    const url = frontMatterField(fm, 'original_url');
    if (!id || !title || !url) throw new Error(`${f}：front-matter 缺 section_id／title／original_url`);
    return { file: f, id, title, anchor: url.split('#')[1] ?? null, body };
  })
  .sort((a, b) => compareSectionId(a.id, b.id));

// ---- 內文處理 ----------------------------------------------------------------
const FENCE_RE = /^\s*(```|~~~)/;
const QUOTE_RE = /^\s*>/;
const FN_DEF_RE = /^\[\^([^\]]+)\]:\s?(.*)$/;
const FANCY_RE = /^\s*(?:[a-z]|[ivxlcdm]+)\.\s/;

const footnotes = new Map(); // label → 定義文字（首次出現者）
let removedQuoteLines = 0;
let hardBreaks = 0;

function processBody(body, file) {
  const out = [];
  let inFence = false;
  const lines = body.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    // 英文側的 fence 也以 `>` 開頭，會在下一個條件被整行刪掉，不影響中文側的 fence 狀態
    if (!QUOTE_RE.test(line) && FENCE_RE.test(line)) {
      inFence = !inFence;
      out.push(line);
      continue;
    }
    if (inFence) {
      out.push(line);
      continue;
    }
    if (QUOTE_RE.test(line)) {
      removedQuoteLines++;
      continue;
    }
    const fn = FN_DEF_RE.exec(line);
    if (fn) {
      // 定義的續行（縮排 4 格）一併收下
      let text = fn[2];
      while (i + 1 < lines.length && /^ {4}\S/.test(lines[i + 1])) text += `\n    ${lines[++i].trim()}`;
      const prev = footnotes.get(fn[1]);
      if (prev === undefined) footnotes.set(fn[1], text);
      else if (prev !== text) console.warn(`⚠️ 註腳 [^${fn[1]}] 在 ${file} 的定義與先前不同，沿用第一份`);
      continue;
    }
    out.push(line);
  }
  // 字母／羅馬數字清單：前一行非空白時補硬換行
  for (let i = 0; i < out.length - 1; i++) {
    if (FANCY_RE.test(out[i + 1]) && out[i].trim() !== '' && !out[i].endsWith('\\')) {
      out[i] += '\\';
      hardBreaks++;
    }
  }
  return out.join('\n').replace(/\n{3,}/g, '\n\n').trim();
}

const headingLevel = (id) => Math.min(id.split('.').length + 1, 6);
const cleanTitle = (t) => t.replace(/^\s*\d+(?:\.\d+)*\s*[、：:.\-—]?\s*/, '').trim() || t;

const blocks = sections.map((s) => {
  const heading = `${'#'.repeat(headingLevel(s.id))} ${sectionIdToLabel(s.id)} ${cleanTitle(s.title)}`;
  const body = processBody(s.body, s.file);
  return [s.anchor ? `<a id="${s.anchor}"></a>\n\n${heading}` : heading, body].filter(Boolean).join('\n\n');
});

// ---- 組檔 --------------------------------------------------------------------
const today = new Date().toLocaleDateString('sv-SE'); // 本地日期 yyyy-mm-dd（理由見 export_chapters_html.mjs）

// 與 src/components/SiteFooter.astro 同一套文案
const DISCLAIMER =
  '本站為 Web PKI 相關文件的非官方繁體中文翻譯，由社群維護。發生爭議時以原文內容為準。本網站內容不構成法律意見。';

const toc = sections
  .filter((s) => s.id.split('.').length <= 2)
  .map((s) => {
    const indent = s.id.split('.').length === 2 ? '  ' : '';
    const text = `${sectionIdToLabel(s.id)} ${cleanTitle(s.title)}`;
    return `${indent}- ${s.anchor ? `[${text}](#${s.anchor})` : text}`;
  })
  .join('\n');

const md = `# CA/Browser Forum《Baseline Requirements for the Issuance and Management of Publicly-Trusted TLS Server Certificates》非官方繁體中文翻譯

對應原文版本 \`${version}\` · 匯出日期 ${today} · 本檔僅含中文翻譯，未附英文原文。

⚠️ ${DISCLAIMER}
本檔為參考用途，非 CA/Browser Forum 官方文件；原文請見 <https://cabforum.org/working-groups/server/baseline-requirements/documents/>。

## 目錄

${toc}

${blocks.join('\n\n')}
${
  footnotes.size > 0
    ? `\n## 註腳\n\n${[...footnotes].map(([label, text]) => `[^${label}]: ${text}`).join('\n\n')}\n`
    : ''
}
---

⚠️ ${DISCLAIMER}

本檔由「BR 翻譯小站」原始碼於 ${today} 匯出。翻譯狀態與後續修訂以站台版本為準。
`;

writeFileSync(outPath, md, 'utf8');
console.log(`✔ 已匯出 ${outPath}`);
console.log(`  章節：${sections.length} 節（v${version}）`);
console.log(`  移除英文 blockquote 行：${removedQuoteLines}；字母／羅馬數字清單補硬換行：${hardBreaks}`);
console.log(`  註腳：${footnotes.size} 條（已合併重複定義）`);
