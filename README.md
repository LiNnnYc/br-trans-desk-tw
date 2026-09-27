# BR 翻譯小站（BR TRANS DESK）

Web PKI 相關文件的非官方繁體中文翻譯，由社群維護。第一份是 CA/Browser Forum 的
**TLS Server Certificate Baseline Requirements**（《基本要求》）。

> ⚠️ 本站為 Web PKI 相關文件的**非官方繁體中文翻譯**，由社群維護。發生爭議時以**原文內容為準**
> （《基本要求》原文見 [cabforum.org](https://cabforum.org/working-groups/server/baseline-requirements/requirements/)）。本網站內容不構成法律意見。

## 專案宗旨

長期以來 CA/Browser Forum 的 Server Certificate Baseline Requirements 沒有公開的繁體中文版本。本站讓台灣 CA 從業人員、購買憑證的企業窗口，以及資安／法務人員，在面對「為什麼申請憑證需要驗證」、「為什麼憑證有效期越來越短」這類問題時，能有可引用的中文翻譯內容。

## 翻譯範圍

依優先序：

1. Baseline Requirements for the Issuance and Management of Publicly-Trusted TLS Server Certificates（主文件）
2. About the Baseline Requirements
3. Certificate Contents for Baseline SSL
4. FAQ for Baseline Requirements
5. 其他相關 BR 公告／指引

不翻譯：EV Guidelines、Code Signing BR、S/MIME BR、Baseline Requirements 歷史版本、簡體中文版本（詳見 PRD §9 Non-Goals）。

## 技術棧

- **靜態產生器**：Astro 5（TypeScript strict + Tailwind 4）
- **搜尋**：Pagefind
- **部署**：GitHub Pages（GitHub Actions）
- **分析**：GoatCounter（隱私友善、無 cookie；尚未啟用）

## 本地開發

```sh
npm install
npm run dev      # 開發 server：http://localhost:4321/
npm run build    # 靜態產出至 dist/（含 Pagefind 索引）
npm run preview  # 預覽 build 結果
npm run check    # Astro / TypeScript 檢查
```

需要 Node.js ≥ 20。`scripts/` 底下的 lint 與升版工具需要 Python 3。

clone 之後請安裝 pre-push hook（每個 clone 做一次），push 前會擋下「升版做到一半」與「下載檔沒重出」：

```sh
git config core.hooksPath .githooks
```

升版、重出下載檔等維運流程見 [`RUNBOOK.md`](./RUNBOOK.md)；譯名與排版慣例見
[`TRANSLATION_CONVENTIONS.md`](./TRANSLATION_CONVENTIONS.md)。

## 目錄結構

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

## 參與貢獻

歡迎透過 GitHub Issue 回報勘誤或提出建議：

- **錯字／誤譯** → `bug-report` 模板
- **功能建議** → `feature-request` 模板
- **Ballot 跟進**（新通過的 CABF Ballot） → `ballot-followup` 模板

重大爭議走 Discussions。社群 PR 由維護者審核後合併。

## 聯絡方式

- Email：[linnnyc5252@gmail.com](mailto:linnnyc5252@gmail.com)（僅用於回覆勘誤事宜，不轉售）
- GitHub Issues：見上方參與貢獻段落

## 授權

- **原文**採 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 授權（CA/Browser Forum）。
- **本翻譯**亦採 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 釋出，鼓勵引用；引用時請註明出處並附原文連結。

授權全文見 [`LICENSE`](./LICENSE)。

## 維護狀態與死人開關

本專案目前由單一維護者推進。

> 若本 repository 連續 **6 個月未更新**（無 commit、無 Issue 回覆、無 PR 處理），視為**停止維護**。
> 本翻譯採 CC BY 4.0 授權，任何人皆可 fork 接手繼續維護，無須額外授權。

這是刻意設計的「死人開關」聲明：避免站點僵在過時狀態卻沒有人能正當地接手。

## 相關文件

- [`RUNBOOK.md`](./RUNBOOK.md) — 維運手冊（本地開發、升版流程、常見操作）
- [`TRANSLATION_CONVENTIONS.md`](./TRANSLATION_CONVENTIONS.md) — 譯名、排版與 lint 慣例
