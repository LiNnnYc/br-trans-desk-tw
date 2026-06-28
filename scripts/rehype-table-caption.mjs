/**
 * Rehype plugin：把表格上方的 Pandoc 風格 `Table:` / `表：` 段落轉成
 * 真正的 <caption> 元素，置於 <table> 內第一個子節點，由 CSS
 * `caption-side: bottom` 顯示在表格底端（對齊 cabforum.org 經 Pandoc 渲染的行為）。
 *
 * 來源標記由 scripts/restore_table_captions.py 回填，格式為「緊鄰表格上方」：
 *   英文（blockquote 內）         中文（一般流）
 *   > Table: <caption>           表：<caption>
 *   >                            （空白行）
 *   > | header |                 | header |
 *   > | ---    |                 | ---    |
 *
 * 經 remark→rehype 後，blockquote 內為 <p>Table: …</p> + <table>，
 * 一般流為 <p>表：…</p> + <table>；本 plugin 找出緊鄰 <table> 前的 caption
 * 段落，去掉前綴後搬進 <caption>。
 *
 * 必須在 rehype（hast）階段做：<caption> 是 <table> 的子元素，mdast 階段
 * 無對應節點型別，且 remark-rehype 會自行生成 thead/tbody，難以插入。
 */
import { visit } from 'unist-util-visit';

const EN_RE = /^Table:\s*/;
const CN_RE = /^表[:：]\s*/;

function textOf(node) {
  if (!node) return '';
  if (node.type === 'text') return node.value;
  if (Array.isArray(node.children)) return node.children.map(textOf).join('');
  return '';
}

// 複製 caption 段落的 inline 子節點，並去掉開頭的「Table: 」/「表：」前綴。
function stripPrefix(children, re) {
  const out = children.slice();
  for (let i = 0; i < out.length; i++) {
    if (out[i].type === 'text') {
      const v = out[i].value.replace(re, '');
      if (v === '') out.splice(i, 1);
      else out[i] = { ...out[i], value: v };
      break;
    }
  }
  return out;
}

export function rehypeTableCaption() {
  return (tree) => {
    const ops = [];
    visit(tree, { type: 'element', tagName: 'table' }, (table, index, parent) => {
      if (!parent || index == null) return;
      // 往前找最近的「非空白」兄弟節點
      let i = index - 1;
      while (i >= 0) {
        const sib = parent.children[i];
        if (sib.type === 'text' && sib.value.trim() === '') { i--; continue; }
        break;
      }
      if (i < 0) return;
      const sib = parent.children[i];
      if (!sib || sib.type !== 'element' || sib.tagName !== 'p') return;
      const txt = textOf(sib);
      let isEn;
      if (EN_RE.test(txt)) isEn = true;
      else if (CN_RE.test(txt)) isEn = false;
      else return;
      ops.push({ table, parent, p: sib, isEn });
    });

    for (const { table, parent, p, isEn } of ops) {
      const inline = stripPrefix(p.children, isEn ? EN_RE : CN_RE);
      const caption = {
        type: 'element',
        tagName: 'caption',
        properties: { className: ['table-caption', isEn ? 'caption-en' : 'caption-cn'] },
        children: inline,
      };
      const pi = parent.children.indexOf(p);
      if (pi !== -1) parent.children.splice(pi, 1);
      table.children.unshift(caption);
    }

    // 第二趟：把每個 <table> 包進 <div class="table-wrap">，讓寬表水平捲動，
    // 同時 <table> 維持 display:table，使 caption-side: bottom 在窄螢幕（全文頁
    // 原本對 table 設 display:block）也能正確顯示於底端。
    visit(tree, { type: 'element', tagName: 'table' }, (table, index, parent) => {
      if (!parent || index == null) return;
      if (parent.type === 'element' && parent.tagName === 'div'
          && (parent.properties?.className || []).includes('table-wrap')) {
        return; // 已包過
      }
      const wrapper = {
        type: 'element',
        tagName: 'div',
        properties: { className: ['table-wrap'] },
        children: [table],
      };
      parent.children[index] = wrapper;
    });
  };
}

export default rehypeTableCaption;
