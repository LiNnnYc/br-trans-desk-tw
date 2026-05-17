# CA/Browser BR 中文化（zh-TW）

CA/Browser Forum **Server Certificate Baseline Requirements** 的非官方繁體中文翻譯，由社群維護。

> ⚠️ 本翻譯為非官方翻譯，發生爭議時以 [CA/Browser Forum 英文原文](https://cabforum.org/working-groups/server/baseline-requirements/requirements/)為準。本翻譯不構成法律意見。

## 專案宗旨

長期以來 CA/Browser Forum 的 Server Certificate Baseline Requirements 沒有公開的繁體中文版本。本站讓台灣 CA 從業人員、購買憑證的企業窗口，以及資安／法務人員，在面對「為什麼申請憑證需要驗證」、「為什麼憑證效期越來越短」這類問題時，能有可引用的中文翻譯內容。

完整背景與目標請見 [`web-spec-doc/PRD.md`](./web-spec-doc/PRD.md)。

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
- **分析**：GoatCounter（隱私友善、無 cookie）

詳見 [`web-spec-doc/spec.md`](./web-spec-doc/spec.md) §6。

## 本地開發

```sh
npm install
npm run dev      # 開發 server：http://localhost:4321/
npm run build    # 靜態產出至 dist/
npm run preview  # 預覽 build 結果
npm run check    # Astro / TypeScript 檢查
```

需要 Node.js ≥ 20。

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

## 維護狀態與死人開關

本專案目前由單一維護者推進。

> 若本 repository 連續 **6 個月未更新**（無 commit、無 Issue 回覆、無 PR 處理），視為**停止維護**。
> 本翻譯採 CC BY 4.0 授權，任何人皆可 fork 接手繼續維護，無須額外授權。

這是刻意設計的「死人開關」聲明：避免站點僵在過時狀態卻沒有人能正當地接手。

## 相關文件

- [`web-spec-doc/PRD.md`](./web-spec-doc/PRD.md) — 產品需求（What & Why）
- [`web-spec-doc/spec.md`](./web-spec-doc/spec.md) — 技術規格（How）
- [`web-spec-doc/milestones.md`](./web-spec-doc/milestones.md) — 里程碑與 Issue 拆解
- [`CLAUDE.md`](./CLAUDE.md) — 給 AI 協作工具的專案上下文
