/**
 * Rehype plugin：把譯稿內文的章節交叉參照改指向「本站全文頁的該章節錨點」。
 *
 * 背景：譯稿沿用 BR.md 原文的錨點寫法，例如
 *   [第 7.1.2.1 節](#7121-root-ca-certificate-profile)
 * 這在 cabforum.org 上有效（全文是一頁），但本站把 BR 拆成 414 個章節細項頁，
 * 這些純片段連結在**任何一頁都不存在**——詳細頁沒有這些 id，全文頁用的是
 * `sec-<節號>` 格式。稽核（2026-09-06）確認全庫 837 個站內錨點連結全是死連結。
 *
 * 做法：build 時把 `#<原文錨點>` 前面補上全文頁路徑 → `/server-cert-br/#<原文錨點>`，
 * 並由 `src/pages/server-cert-br/index.astro` 在全文頁各章節標題掛上同名 id。
 * 錨點名稱**與 cabforum.org 完全相同**，因此把網域對調即可在中英兩站落到同一節，
 * 對照原文時很方便。
 *
 * 譯稿檔維持原文寫法（好與 BR.md 逐字對照、升版時容易 diff），不需改內容檔。
 *
 * ## 只改章節錨點，白名單來自 front-matter
 *
 * 頁面上還有其他片段連結——註腳的 `#fn-…`／`#fnref-…`（`rehype-footnotes.mjs`
 * 產生）必須留在頁內，改成跨頁就壞了。因此這裡採**白名單**：只有出現在某個章節檔
 * `original_url` fragment 的錨點才改寫，其餘一律不動。黑名單（排除 `fn-` 開頭之類）
 * 會在日後新增其他產生式錨點時默默漏接。
 *
 * ## 之後接 GitHub Pages 時要注意
 *
 * `astro.config.mjs` 目前沒有設 `base`，故此處寫死站台根目錄下的 `/server-cert-br/`。
 * 若將來部署到子路徑而設了 `base`，這個常數要一併加上前綴。
 */
import { readdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { visit } from 'unist-util-visit';

/** 全文頁路徑；設了 astro base 之後要同步加前綴。 */
const FULL_TEXT_PATH = '/server-cert-br/';

const BR_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'content', 'br');
const ORIGINAL_URL_RE = /^original_url:\s*"[^"#]*#([^"]+)"/m;

/** 各章節檔 `original_url` 的 fragment＝該節在 cabforum.org 的錨點。 */
function loadSectionAnchors() {
  const anchors = new Set();
  for (const name of readdirSync(BR_DIR)) {
    if (!name.endsWith('.md')) continue;
    // front-matter 在檔首，讀前 1KB 足夠，不必整份載入
    const head = readFileSync(join(BR_DIR, name), 'utf8').slice(0, 1024);
    const m = ORIGINAL_URL_RE.exec(head);
    if (m) anchors.add(m[1]);
  }
  return anchors;
}

const SECTION_ANCHORS = loadSectionAnchors();

export function rehypeSectionLinks() {
  return (tree) => {
    visit(tree, { type: 'element' }, (node) => {
      if (node.tagName !== 'a') return;
      const href = node.properties?.href;
      if (typeof href !== 'string' || !href.startsWith('#')) return;
      const anchor = href.slice(1);
      if (!SECTION_ANCHORS.has(anchor)) return; // 註腳等其他片段連結維持頁內
      node.properties.href = `${FULL_TEXT_PATH}#${anchor}`;
    });
  };
}
