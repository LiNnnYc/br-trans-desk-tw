// spec §4.3 — 引用卡輸出格式。
// 此格式為 CLAUDE.md 明示「不可更動」之輸出規範，包含免責聲明。
// 修改任何欄位順序、emoji、標點都會破壞下游 CA 客服窗口的引用模板。

export interface CitationInput {
  /** 章節編號，如 "3.2.2.4" */
  sectionId: string;
  /** 中文章節標題（不含編號） */
  title: string;
  /** 整節摘要或單段段落文字 */
  body: string;
  /** 對應原文 URL */
  originalUrl: string;
  /** 對應原文版本，如 "v2.1.5" */
  originalVersion: string;
  /** 站台絕對網址，不含 trailing slash */
  siteUrl: string;
}

export function sectionIdToPath(sectionId: string): string {
  return sectionId.replaceAll('.', '-');
}

export function buildCitation(input: CitationInput): string {
  const siteUrl = input.siteUrl.replace(/\/+$/, '');
  const sectionPath = sectionIdToPath(input.sectionId);

  return [
    `【${input.sectionId} ${input.title}】`,
    input.body,
    '',
    `📎 繁中翻譯：${siteUrl}/server-cert-br/${sectionPath}/`,
    `📎 原文：${input.originalUrl}`,
    `📌 對應原文版本：${input.originalVersion}`,
    '',
    '⚠️ 本翻譯為非官方翻譯，發生爭議時以 CA/Browser Forum 英文原文為準。',
  ].join('\n');
}
