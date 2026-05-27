/**
 * Remark plugin：為表格儲存格自動加 `nowrap` class。
 *
 * 規則：cell 內文（trim 後）沒有空白字元、且長度 ≤ 16，視為原子 token
 * （日期 2025-01-15、版號 1.2.3、章節編號 3.2.2.4、Ballot 編號 SC080v3、
 *   破折號 --、N/A 等），加上 .nowrap class 由 CSS 套 white-space: nowrap。
 *
 * 設計考量：
 *   - 不寫死正則：用「無空白＋短長度」一條規則即可涵蓋所有目前的欄位類型，
 *     未來新增表格欄位類型無須改 plugin。
 *   - 連 link 算進去：cell 含 [3.2.2.4](#anchor) 時，textContent = "3.2.2.4"，
 *     仍符合條件，會 nowrap。
 *   - 上限 16 字元防止把長英文字串（如 "Subscriber" 也算進來但無 link 結構）
 *     誤判為 token。實務上會 wrap 的欄位本來就含空白，這條只是保險。
 */
import { visit } from 'unist-util-visit';

function nodeText(node) {
  if (!node) return '';
  if (typeof node.value === 'string' && (node.type === 'text' || node.type === 'inlineCode')) {
    return node.value;
  }
  if (Array.isArray(node.children)) {
    return node.children.map(nodeText).join('');
  }
  return '';
}

// 章節參照 pattern：整個 cell 內容為「第 X.Y.Z 節」或「Section X.Y.Z」，
// 允許前綴「參見 / See 」。這類 cell 不應在 X 與 Y 之間或編號中間斷行。
const SECTION_REF_RE =
  /^(?:參見)?第\s+\d+(?:\.\d+)*\s+節$|^(?:See\s+)?Section\s+\d+(?:\.\d+)*$/;

function shouldNowrap(text) {
  const t = text.trim();
  if (!t) return false;
  // 短 token：無空白 + ≤16 字元
  if (!/\s/.test(t) && t.length <= 16) return true;
  // 章節參照
  if (SECTION_REF_RE.test(t)) return true;
  return false;
}

function addClass(node, cls) {
  node.data = node.data || {};
  const hProps = node.data.hProperties || {};
  const existing = hProps.className;
  let arr;
  if (Array.isArray(existing)) arr = [...existing];
  else if (typeof existing === 'string') arr = existing.split(/\s+/).filter(Boolean);
  else arr = [];
  if (!arr.includes(cls)) arr.push(cls);
  hProps.className = arr;
  node.data.hProperties = hProps;
}

export function remarkTableNowrap() {
  return (tree) => {
    visit(tree, 'table', (table) => {
      const rows = (table.children || []).filter((c) => c.type === 'tableRow');
      if (rows.length < 2) return;
      const headerRow = rows[0];
      const bodyRows = rows.slice(1);

      // Step 1：per-cell — 凡 body 中的短 token cell 都加 .nowrap（white-space: nowrap）
      bodyRows.forEach((row) => {
        (row.children || []).forEach((cell) => {
          if (shouldNowrap(nodeText(cell))) addClass(cell, 'nowrap');
        });
      });

      // Step 2：per-column — 只有「全欄 body cells 都是短 token」時才加 .col-shrink
      // （width: 1%）。避免某欄混有長文字 row + 單字元 `-` row 時，瀏覽器
      // 取最小 hint 把整欄擠到 1 字元寬。
      const colCount = Math.max(
        ...rows.map((r) => (r.children || []).length),
        0,
      );
      for (let c = 0; c < colCount; c++) {
        const allShrink = bodyRows.every((row) => {
          const cell = (row.children || [])[c];
          if (!cell) return false;
          return shouldNowrap(nodeText(cell));
        });
        if (!allShrink) continue;
        bodyRows.forEach((row) => {
          const cell = (row.children || [])[c];
          if (cell) addClass(cell, 'col-shrink');
        });
        const hCell = (headerRow.children || [])[c];
        if (hCell) addClass(hCell, 'col-shrink');
      }
    });
  };
}

export default remarkTableNowrap;
