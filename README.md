# BR 翻譯小站（BR TRANS DESK）

提供 Web PKI 相關文件的非官方繁體中文翻譯。

> ⚠️ 所有文件皆為**非官方繁體中文翻譯**，由社群維護。發生爭議時以**原文內容為準**

## 專案宗旨

以 CA/Browser Forum 為主的 Web PKI 體系相關文件，長期以來一直缺乏繁體中文翻譯供相關從業人員參考。本站試著以社群維護的方式，提供 Web PKI 相關文件的非官方翻譯， 讓台灣 CA 從業人員、購買憑證的用戶、資安／法務人員在面對 Web PKI、PKIX 體系相關問題時，能有可參考的繁體中文翻譯內容。

## 目前已翻譯的文件

### CA/Browser Forum TLS BR 

以下皆為官網原文翻譯
1. Baseline Requirements for the Issuance and Management of Publicly-Trusted TLS Server Certificates（主文件）
2. About the Baseline Requirements
3. Certificate Contents for Baseline SSL
4. FAQ for Baseline Requirements

不翻譯：EV Guidelines、Code Signing BR、S/MIME BR、Baseline Requirements 歷史版本。

- 本站翻譯的 TLS BR 全文下載（v2.3.0）：[PDF](./public/archive/BR_v2.3.0_zh-TW.pdf)｜[Markdown](./public/archive/BR_v2.3.0_zh-TW.md)｜[HTML](./public/archive/BR_v2.3.0_zh-TW.html)（HTML 請下載後以瀏覽器開啟）
- 官方原文：[cabforum.org](https://cabforum.org/working-groups/server/baseline-requirements/requirements/)
- 發生爭議時**以原文內容為準**。本專案內容不構成法律意見。

## 參與貢獻

歡迎透過 GitHub Issue 回報勘誤或提出建議：

- **錯字／誤譯** → `bug-report` 模板
- **功能建議** → `feature-request` 模板
- **Ballot 跟進**（新通過的 CABF Ballot） → `ballot-followup` 模板

重大爭議走 Discussions。社群 PR 由維護者審核後合併。

## 聯絡方式

- 請參照 [聯絡方式](https://tls.brdesk.tw/contact/) 頁面
- GitHub Issues：見上方參與貢獻段落

## 授權

- **原文**採 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 授權（CA/Browser Forum）。
- **本翻譯**亦採 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 釋出，鼓勵引用；引用時請註明出處並附原文連結。

授權全文見 [`LICENSE`](./LICENSE)。

## 網站使用技術

- **靜態產生器**：Astro 5（TypeScript strict + Tailwind 4）
- **搜尋**：Pagefind
- **部署**：GitHub Pages（GitHub Actions）
- **分析**：GoatCounter（隱私友善、無 cookie；尚未啟用）

## 專案目錄結構

| 路徑 | 內容 |
|---|---|
| `src/content/br/` | 《基本要求》譯文，一節一檔（中英對照 markdown） |
| `src/content/glossary/`、`acronyms/`、`quick-reference/`、`news/` | 術語表、縮寫表、快速參考、更新消息 |
| `src/config/` | 版本表、憑證欄位譯名對照等資料 |
| `public/archive/` | 各版全文下載檔（HTML／PDF／Markdown），由 `scripts/build_downloads.mjs` 產生 |
| `scripts/` | remark／rehype plugin、lint、匯出與升版工具 |
| `upstream/BR.md` | 上游英文原文（現行版），**建置時會讀取**，不可刪除 |
| `upstream/BR_archive/` | 上游原文的歷史版本快照，升版比對用 |
| `upstream/BR_側邊欄/` | 側邊欄四頁的上游原文 |

## 專案無法繼續聲明（Dead man's switch）

本專案目前由單一維護者推進。

> 若本 repository 連續 **6 個月未更新**（無 commit、無 Issue 回覆、無 PR 處理），視為**停止維護**。
> 本翻譯採 CC BY 4.0 授權，任何人皆可 fork 接手繼續維護，無須額外授權。

這是刻意設計的「死人開關」聲明：避免網站翻譯文件持續處於過時狀態卻沒有人能正當地接手。

## 相關文件

- [`RUNBOOK.md`](./RUNBOOK.md) — 維運手冊（本地開發、升版流程、常見操作）
- [`TRANSLATION_CONVENTIONS.md`](./TRANSLATION_CONVENTIONS.md) — 譯名、排版與 lint 慣例
