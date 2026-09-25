// 本站發布過的 TLS BR 版本歷程。**每次升版譯完後，在陣列最上面加一列。**
//
// 這是全站唯一需要人工維護的版本資料；其餘（上游最新版、是否落後、章節頁顯示的
// 版本）都由程式推導：
//   - 上游最新版與日期 → 讀 `web-spec-doc/BR.md` 的 front-matter（見 src/lib/version.ts）
//   - 本站實際發布版本 → 讀 `src/content/br/*.md` 的 `original_version`
//
// `date` 一律取自**該版原文 BR.md 標頭的 `date:` 欄位**（cabforum 在 GitHub 釋出的
// 值，如 `19-May-2026`），轉成 ISO。升版時 BR.md 標頭會換成新版的日期，所以舊版
// 日期要在當下記進這張表，之後就查不到了。

export interface BrVersionEntry {
  /** 上游版本號，如 "2.2.7" */
  version: string;
  /** 該版原文發布日（ISO yyyy-mm-dd），取自該版 BR.md 標頭的 date */
  date: string;
  /** 通過該版的投票案編號 */
  ballot?: string;
  /** 本站完成該版翻譯與審閱的日期（ISO） */
  translatedAt?: string;
  /** git tag 名稱（嚴封該版全文） */
  gitTag?: string;
  /**
   * 下載檔的檔名主體（不含副檔名，相對於 public/archive/）。同名的 `.html`／`.pdf`／`.md`
   * 三個檔都要在（全文、只有中文），由 `node scripts/build_downloads.mjs` 產生；
   * pre-push 以 scripts/lint_downloads.py 檢查齊全與否、最新版是否跟得上內容。
   * 讓客服不必 checkout git 也能離線查閱或轉寄。
   */
  archive?: string;
}

/** 最新的排在最前面；`[0]` 即本站目前發布的版本。 */
export const brVersions: BrVersionEntry[] = [
  {
    version: '2.3.0',
    date: '2026-09-07',
    ballot: 'SC100',
    translatedAt: '2026-09-13',
    archive: 'BR_v2.3.0_zh-TW',
  },
  {
    version: '2.2.7',
    date: '2026-05-19',
    ballot: 'SC099',
    translatedAt: '2026-09-06',
    gitTag: 'br-v2.2.7',
    archive: 'BR_v2.2.7_zh-TW',
  },
];
