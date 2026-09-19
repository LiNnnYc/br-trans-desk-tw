// 章節編號 → 網址片段（3.2.2.4 → 3-2-2-4）。
//
// 本檔原本還含 spec §4.3 的引用卡輸出格式 buildCitation()；「複製引用」功能已於
// 2026-09-19 依使用者指示廢除，該函式與 CitationInput 型別一併移除。
// ⚠️ spec §4.3、PRD §4.4 與 CLAUDE.md 仍記載該輸出格式為必要規範，尚未同步；
// 要復原可從 git 歷史取回本檔的前一版。

export function sectionIdToPath(sectionId: string): string {
  return sectionId.replaceAll('.', '-');
}
