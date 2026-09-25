/**
 * export_pdf.mjs — 用 headless Chrome（或 Edge）把離線存檔 HTML 印成 PDF。
 *
 * 輸入是 export_chapters_html.mjs 產出的自足 HTML（樣式已內嵌），所以 PDF 與離線存檔同版面、
 * 同樣只有中文。列印前在暫存副本裡補一段列印樣式：
 *   - A4 版面與邊界（Chrome CLI 沒有紙張大小參數，只能靠 @page）
 *   - 表格外層 .table-wrap 與 <pre> 在螢幕上是 overflow-x:auto，印出來會被**裁掉**，
 *     列印時改成 visible 並讓程式碼換行
 *   - 標題不與下一段分頁、表格列不從中間斷開
 *   - 站台列印樣式造成的副作用（藏掉免責聲明、展開網址），見 PRINT_CSS 上方註解
 * 原始 HTML 不動。
 *
 * 瀏覽器路徑：先看環境變數 CHROME_PATH，再找 Windows／macOS／Linux 常見位置。
 * 用獨立的 --user-data-dir，避免和正在開著的 Chrome 搶同一個設定檔。
 *
 * 用法：
 *   node scripts/export_pdf.mjs --in public/archive/BR_v2.3.0_zh-TW.html --out public/archive/BR_v2.3.0_zh-TW.pdf
 */
import { readFileSync, writeFileSync, existsSync, mkdtempSync, rmSync, statSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const argv = process.argv.slice(2);
function arg(name, fallback) {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : fallback;
}
const inArg = arg('in', null);
const outArg = arg('out', null);
if (!inArg || !outArg) {
  console.error('用法：node scripts/export_pdf.mjs --in <html> --out <pdf>');
  process.exit(1);
}
const inPath = resolve(ROOT, inArg);
const outPath = resolve(ROOT, outArg);
if (!existsSync(inPath)) {
  console.error(`找不到 ${inPath}`);
  process.exit(1);
}

const CANDIDATES = [
  process.env.CHROME_PATH,
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
].filter(Boolean);
const browser = CANDIDATES.find((p) => existsSync(p));
if (!browser) {
  console.error('找不到 Chrome／Edge；請以環境變數 CHROME_PATH 指定瀏覽器執行檔');
  process.exit(1);
}

// ⚠️ 站台 global.css 的 @media print 會隱藏所有 header／footer（為了藏導覽列），
// 存檔的標題區與頁尾**免責聲明**會跟著消失——免責聲明不得移除（CLAUDE.md），所以這裡強制顯示。
// 同一份樣式還會把外部連結展開成「 <網址>」尾註，並印出各節標題旁的「原文 ↗」與錨點圖示，
// 在整本 PDF 裡只是雜訊，一併關掉。
const PRINT_CSS = `<style>
  @page { size: A4; margin: 16mm 14mm; }
  @media print {
    .export-card > header, .export-card > footer.export-foot { display: block !important; }
    a[href]::after { content: none !important; }
    a[title="cabforum.org 原文"], a[title="本節錨點連結"] { display: none !important; }
    .export-wrap { max-width: none; padding: 0; }
    .clause-body .table-wrap, .clause-body pre, .clause-body .code-figure { overflow: visible !important; }
    .clause-body pre { white-space: pre-wrap; word-break: break-all; }
    h1, h2, h3, h4, h5, h6 { break-after: avoid; }
    tr, .code-figure { break-inside: avoid; }
  }
</style>`;

const tmp = mkdtempSync(join(tmpdir(), 'br-pdf-'));
try {
  const html = readFileSync(inPath, 'utf8');
  if (!html.includes('</head>')) throw new Error('HTML 缺 </head>，無法注入列印樣式');
  const tmpHtml = join(tmp, 'print.html');
  writeFileSync(tmpHtml, html.replace('</head>', `${PRINT_CSS}\n</head>`), 'utf8');
  // 先刪舊檔，否則瀏覽器失敗時下面的「檔案存在」檢查會被舊 PDF 騙過
  rmSync(outPath, { force: true });

  const res = spawnSync(
    browser,
    [
      '--headless=new',
      '--disable-gpu',
      '--no-first-run',
      '--no-default-browser-check',
      `--user-data-dir=${join(tmp, 'profile')}`,
      '--no-pdf-header-footer',
      `--print-to-pdf=${outPath}`,
      pathToFileURL(tmpHtml).href,
    ],
    { encoding: 'utf8', timeout: 180_000 },
  );
  if (res.error) throw res.error;
  if (!existsSync(outPath) || statSync(outPath).size === 0) {
    console.error(res.stderr);
    throw new Error('瀏覽器沒有產出 PDF');
  }
  console.log(`✔ 已匯出 ${outPath}（${(statSync(outPath).size / 1024 / 1024).toFixed(1)} MB）`);
  console.log(`  瀏覽器：${browser}`);
} finally {
  rmSync(tmp, { recursive: true, force: true });
}
