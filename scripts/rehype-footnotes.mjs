/**
 * Rehype plugin：把 GFM 產生的註腳（footnotes）整理成本站的形式。
 *
 * 原生（remark-gfm + remark-rehype）輸出的問題：
 *   1. id 全域固定為 `user-content-fn-<label>` / `user-content-fnref-<label>`。
 *      全文頁 /server-cert-br/ 會把 408 個 entry 串在同一頁，同一個 label
 *      （如 `eku_ca` 有 5 個章節各自定義一份）會產生重複 id，錨點只會跳到
 *      第一個出現的地方 → 跨章節時跳錯位置。
 *   2. 標題是英文 `Footnotes` 且為 sr-only，視覺上沒有「這裡是註腳區」的分界。
 *   3. 第一個引用的 id 沒有 `-1` 後綴（`fnref-x`、`fnref-x-2`、`fnref-x-3`），
 *      要後製時得處理兩種形式。
 *
 * 本 plugin 的輸出（每個章節檔各自成立）：
 *   引用：<sup><a class="fn-ref" href="#fn-<sec>-<label>" id="fnref-<sec>-<label>-<n>"
 *              data-fn-label="<label>" data-fn-sec="<section_id>"
 *              [data-fn-en]>（數字）</a></sup>
 *         data-fn-en 表示該引用位於英文原文 blockquote 內（全文頁隱藏英文，
 *         故全文頁的註腳回鏈只認中文側的引用）。
 *   註腳區：<section class="clause-footnotes" data-fn-section="<section_id>">
 *             <h2 class="clause-footnotes-title" id="fn-title-<sec>">註腳</h2>
 *             <ol><li id="fn-<sec>-<label>" data-fn-label="<label>">…
 *                   <a class="fn-backref" href="#fnref-<sec>-<label>-<n>">↩</a></li></ol>
 *           </section>
 *
 * 單章節頁 /server-cert-br/[slug]/ 直接沿用這份輸出：註腳落在該節內文最下方，
 * 只含該節用到的註腳。全文頁再由 src/pages/server-cert-br/index.astro 把各節的
 * 註腳區抽出、依 label 合併成整份文件末尾的單一註腳清單（比照 cabforum.org
 * 原文把註腳放在文件最下方的作法）；該處的字串處理依賴本 plugin 產出的
 * `class="clause-footnotes"`、`data-fn-label`、`class="fn-backref"` 等標記，
 * 修改本檔的輸出格式時務必同步檢查該頁。
 */
import { visit } from 'unist-util-visit';

const FN_PREFIX = 'user-content-fn-';
const FNREF_PREFIX = 'user-content-fnref-';
const EN_SUFFIX = '_en';

/** `eku_ca_en` → `eku_ca`；中英兩條註腳共用同一個編號（比照 Style A 對照） */
function baseLabelOf(label) {
  return label.endsWith(EN_SUFFIX) ? label.slice(0, -EN_SUFFIX.length) : label;
}

/** `7.1.2.2.3` → `7-1-2-2-3`（附錄的 section_id 本身已是 `appendix-a`） */
function toSlug(sectionId) {
  return String(sectionId).replace(/\./g, '-');
}

/** 從 vfile 取 section_id；取不到時退回檔名（拆檔檔名即 slug）。 */
function sectionIdOf(file) {
  const fm = file?.data?.astro?.frontmatter;
  if (fm && typeof fm.section_id === 'string' && fm.section_id) return fm.section_id;
  const path = file?.history?.[0] ?? file?.path ?? '';
  const base = String(path).split(/[\\/]/).pop() ?? '';
  return base.replace(/\.md$/, '') || 'unknown';
}

/** `user-content-fnref-eku_ca-3` → { label: 'eku_ca', n: 3 }（無後綴視為第 1 個） */
function parseRefId(id) {
  const rest = id.slice(FNREF_PREFIX.length);
  const m = /^(.+?)-(\d+)$/.exec(rest);
  return m ? { label: m[1], n: Number(m[2]) } : { label: rest, n: 1 };
}

export function rehypeFootnotes() {
  return (tree, file) => {
    const sectionId = sectionIdOf(file);
    const slug = toSlug(sectionId);
    const titleId = `fn-title-${slug}`;

    // ── 1. 引用（<a data-footnote-ref>）───────────────────────────────────
    // blockquote 內＝英文原文側，另外標記，供全文頁排除。
    /** label → [{ n, inQuote }]，供下方回鏈判斷哪些引用是英文側 */
    const refsByLabel = new Map();
    /** 基底 label → 顯示編號；中英兩條（`x` 與 `x_en`）共用，依首次引用順序 */
    const numberOf = new Map();
    const markRefs = (node, inQuote) => {
      if (node.type === 'element') {
        if (node.tagName === 'blockquote') inQuote = true;
        const props = node.properties ?? {};
        if (node.tagName === 'a' && props.dataFootnoteRef !== undefined) {
          const label = String(props.href ?? '').slice(('#' + FN_PREFIX).length);
          const { n } = parseRefId(String(props.id ?? ''));
          if (!refsByLabel.has(label)) refsByLabel.set(label, []);
          refsByLabel.get(label).push({ n, inQuote });
          const base = baseLabelOf(label);
          if (!numberOf.has(base)) numberOf.set(base, numberOf.size + 1);
          // GFM 的編號把中英兩條各算一項（1、2、3、4…），改成兩條共用一個編號
          node.children = [{ type: 'text', value: String(numberOf.get(base)) }];
          node.properties = {
            className: ['fn-ref'],
            href: `#fn-${slug}-${label}`,
            id: `fnref-${slug}-${label}-${n}`,
            'data-fn-label': label,
            'data-fn-sec': sectionId,
            ...(inQuote ? { 'data-fn-en': '' } : {}),
            'aria-describedby': titleId,
          };
        }
      }
      for (const child of node.children ?? []) markRefs(child, inQuote);
    };
    markRefs(tree, false);

    // ── 2. 註腳區（<section data-footnotes>）──────────────────────────────
    visit(tree, { type: 'element', tagName: 'section' }, (section) => {
      const props = section.properties ?? {};
      if (props.dataFootnotes === undefined) return;

      section.properties = {
        className: ['clause-footnotes'],
        'data-fn-section': sectionId,
        'aria-labelledby': titleId,
      };

      // 英文 sr-only 標題 → 可見的中文標題
      const heading = (section.children ?? []).find(
        (c) => c.type === 'element' && /^h[1-6]$/.test(c.tagName)
      );
      if (heading) {
        heading.tagName = 'h2';
        heading.properties = { className: ['clause-footnotes-title'], id: titleId };
        heading.children = [{ type: 'text', value: '註腳' }];
      }

      // 定義項目與回鏈
      visit(section, { type: 'element', tagName: 'li' }, (li) => {
        const id = String(li.properties?.id ?? '');
        if (!id.startsWith(FN_PREFIX)) return;
        const label = id.slice(FN_PREFIX.length);
        li.properties = {
          id: `fn-${slug}-${label}`,
          'data-fn-label': label,
          // 中英兩條共用同一編號，<ol> 的自動編號要用 value 蓋掉
          value: numberOf.get(baseLabelOf(label)),
          // 英文那條（`<label>_en`）：單章節頁與英文 blockquote 一樣常駐顯示，
          // 只以灰階區分；全文頁（純中文）由 index.astro 合併時排除。
          ...(label.endsWith(EN_SUFFIX) ? { className: ['fn-item-en'] } : {}),
        };

        // 回鏈：中英兩側各自照序編號（↩、↩2…）。指向英文側引用者另加
        // .fn-backref-en，供全文頁那類「只顯示中文」的情境一併隱藏，避免
        // 「點了跳到看不見的地方」。
        const refs = refsByLabel.get(label) ?? [];
        let cnCount = 0;
        let enCount = 0;
        visit(li, { type: 'element', tagName: 'a' }, (a) => {
          const ap = a.properties ?? {};
          if (ap.dataFootnoteBackref === undefined) return;
          const href = String(ap.href ?? '');
          const { n } = parseRefId(href.slice(1)); // 去掉開頭的 #
          const isEn = refs.find((r) => r.n === n)?.inQuote === true;
          const seq = isEn ? ++enCount : ++cnCount;
          a.properties = {
            className: isEn ? ['fn-backref', 'fn-backref-en'] : ['fn-backref'],
            href: `#fnref-${slug}-${label}-${n}`,
            'data-fn-backref': '',
            'aria-label': isEn
              ? `回到英文原文第 ${seq} 處引用`
              : `回到內文第 ${seq} 處引用`,
          };
          a.children = [
            { type: 'text', value: '↩' },
            ...(seq > 1
              ? [{ type: 'element', tagName: 'sup', properties: {}, children: [{ type: 'text', value: String(seq) }] }]
              : []),
          ];
        });
      });
    });

    // ── 3. 清掉英文註腳定義留下的空 blockquote ────────────────────────────
    // `> [^x_en]: …` 的定義會被 remark 抽走（統一收進註腳區），原地留下一個空的
    // <blockquote>，在單章節頁會顯示成一條孤立的藍色左框。
    const dropEmptyQuotes = (node) => {
      if (!Array.isArray(node.children)) return;
      node.children = node.children.filter((c) => {
        if (c.type !== 'element' || c.tagName !== 'blockquote') return true;
        return (c.children ?? []).some(
          (g) => g.type === 'element' || (g.type === 'text' && g.value.trim() !== '')
        );
      });
      node.children.forEach(dropEmptyQuotes);
    };
    dropEmptyQuotes(tree);
  };
}

export default rehypeFootnotes;
