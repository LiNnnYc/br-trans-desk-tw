/**
 * Rehype plugin：把表格儲存格的前導 U+2007（FIGURE SPACE）縮排改成 cell padding。
 *
 * 背景：BR.md 原文以前導空白表示欄位階層（`    revokedCertificates` 屬於
 * `tbsCertList` 之下），`scripts/preserve_table_indent.py` 把它轉成 U+2007
 * 保留對齊（一般空白在 HTML 會被摺疊）。
 *
 * 問題：U+2007 留在文字流裡時，縮排本身也是可換行的內容。`global.css` 對
 * `td` 設了 `overflow-wrap: anywhere`（讓長識別碼不撐爆欄寬），於是縮排與
 * 識別碼之間成了斷行點，且該儲存格的 min-content 只剩「識別碼寬度」——當同列
 * 其他欄很長、table 演算法把第一欄壓到最小寬度時，瀏覽器就把縮排留在上一行、
 * 識別碼掉到第二行貼齊左緣，看起來完全沒縮排。欄位名越長越容易中招
 * （實例：§7.2「CRL 欄位」表的 `revokedCertificates`）。
 *
 * 做法：build 時把前導 U+2007 從文字拿掉，改成 `<td class="cell-indent"
 * style="--cell-indent:4">`，由 global.css 換算成 padding-left。padding 不參與
 * 換行，又會計入欄寬下限，因此任何欄寬下縮排都不會失效，換行時也自然形成
 * 首行與續行對齊的 hanging indent。
 *
 * 譯稿檔維持寫 U+2007（審閱者讀原始 markdown 時仍看得到階層），不需改內容。
 */
import { visit } from 'unist-util-visit';

const FIGURE_SPACE = String.fromCharCode(0x2007); // 以碼位書寫，避免被誤改成一般空白
const LEADING_INDENT = new RegExp(`^[ \t]*(${FIGURE_SPACE}+)[ \t]*`);

export function rehypeTableIndent() {
  return (tree) => {
    visit(tree, { type: 'element' }, (node) => {
      if (node.tagName !== 'td' && node.tagName !== 'th') return;
      const first = node.children?.[0];
      if (!first || first.type !== 'text') return;
      const m = LEADING_INDENT.exec(first.value);
      if (!m) return;

      const level = m[1].length; // U+2007 個數，BR.md 目前用 2 / 4 / 8
      first.value = first.value.slice(m[0].length);
      if (first.value === '') node.children.shift();

      const props = (node.properties ??= {});
      const className = Array.isArray(props.className)
        ? props.className
        : props.className
          ? [props.className]
          : [];
      props.className = [...className, 'cell-indent'];
      props.style = props.style
        ? `${props.style};--cell-indent:${level}`
        : `--cell-indent:${level}`;
    });
  };
}

export default rehypeTableIndent;
