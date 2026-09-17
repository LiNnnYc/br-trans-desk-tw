// 章節編號的共用工具：排序與「顯示標籤」。
//
// section_id 是**機器識別碼**——它決定永久網址與檔名（CLAUDE.md 的 IA 慣例），
// 所以附錄一律用 `appendix-<letter>` 前綴，子節接點分數字：
//
//   appendix-a       → /server-cert-br/appendix-a/
//   appendix-a.1.1   → /server-cert-br/appendix-a-1-1/
//
// 但這串前綴不是原文的章節號。凡是要給人看的地方（麵包屑、標題列、側邊欄、
// 錨點導覽、引用卡）都必須改走 sectionIdToLabel()，才會顯示成原文的
// 「附錄 A」／「A.1.1」。正文的數字編號不受影響，原樣輸出。

/** `appendix-a`、`appendix-a.1.1` → ['a', [1, 1]]；正文回傳 null。 */
function parseAppendix(id: string): { letter: string; nums: number[] } | null {
  const m = /^appendix-([a-z])((?:\.\d+)*)$/.exec(id);
  if (!m) return null;
  const nums = m[2] ? m[2].slice(1).split('.').map(Number) : [];
  return { letter: m[1], nums };
}

/**
 * 排序鍵：正文在前（群組 0）、附錄在後（群組 1，再依字母與子節編號）。
 * 之所以要展開成數字陣列而不是字串比大小，是因為 localeCompare 會把
 * `.10` 排在 `.2` 前面；而直接 Number() 整串 id 則會讓附錄變成 NaN。
 */
function sortKey(id: string): number[] {
  const app = parseAppendix(id);
  if (app) return [1, app.letter.charCodeAt(0), ...app.nums];
  return [0, ...id.split('.').map(Number)];
}

/** br collection 的 section_id 自然排序（正文數字序，附錄殿後）。 */
export function compareSectionId(a: string, b: string): number {
  const ak = sortKey(a);
  const bk = sortKey(b);
  const n = Math.max(ak.length, bk.length);
  for (let i = 0; i < n; i++) {
    const av = ak[i] ?? -1;
    const bv = bk[i] ?? -1;
    if (av !== bv) return av - bv;
  }
  return 0;
}

/**
 * 顯示標籤：把機器識別碼還原成原文的章節號。
 *
 *   appendix-a      → 附錄 A
 *   appendix-a.1.1  → A.1.1
 *   3.2.2.4         → 3.2.2.4（原樣）
 */
export function sectionIdToLabel(id: string): string {
  const app = parseAppendix(id);
  if (!app) return id;
  const letter = app.letter.toUpperCase();
  return app.nums.length === 0 ? `附錄 ${letter}` : `${letter}.${app.nums.join('.')}`;
}

/** 階層深度（頂層為 0）：3.2.2 → 2、appendix-a → 0、appendix-a.1.1 → 2。 */
export function sectionIdDepth(id: string): number {
  return id.split('.').length - 1;
}

/**
 * glossary／acronyms 來源的 `ref` → 給人看的出處標籤。
 *
 * BR 來源存的是本站章節頁的路徑（`/server-cert-br/1-6-1/`），拿來當顯示文字
 * 既不好讀、也看不出那是本站的翻譯而非 CA/Browser Forum 原文，所以一律轉成
 * 「本站 BR 翻譯 §1.6.1」。其餘 ref（外部文件的描述字串、非章節的站內路徑）
 * 原樣回傳——連結與否由呼叫端決定。
 */
export function sourceRefLabel(ref: string): string {
  const m = /^\/server-cert-br\/(\d+(?:-\d+)*)\/$/.exec(ref);
  return m ? `本站 BR 翻譯 §${m[1].replace(/-/g, '.')}` : ref;
}
