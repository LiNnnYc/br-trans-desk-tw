# RUNBOOK — CA/Browser BR 中譯站維運手冊

> 本檔對應 milestone **M1-13**，內容為「常做的事」與「出狀況時怎麼辦」。
> 長期約定請看 [`CLAUDE.md`](./CLAUDE.md) 與 [`web-spec-doc/`](./web-spec-doc/)；當前進度看 [`HANDOFF.md`](./HANDOFF.md)。

---

## 1. 本地開發

### 1.1 環境需求

- Node.js ≥ 20（Astro 5 要求）
- npm（隨 Node 附帶）
- Python 3（跑 `scripts/*.py` 的 lint）

**每個 clone 做一次**——啟用版控裡的 git hooks：

```sh
git config core.hooksPath .githooks
```

裝了之後 `git push` 前會自動跑版本一致性檢查（見 §2.4），擋下「升版做到一半」的
混版狀態被推出去。日常 build／dev／commit 不受影響。

### 1.2 常用指令

| 指令 | 用途 |
| --- | --- |
| `npm install` | 安裝相依套件（首次或 `package.json` 變動後執行） |
| `npm run dev` | 啟動本機開發伺服器，預設 <http://localhost:4321/> |
| `npm run check` | 跑 `astro check`：型別與 schema 檢查，**期望 0 errors** |
| `npm run build` | 產出 `dist/`（含 `dist/pagefind/` 索引） |
| `npm run preview` | 預覽完整 build（**這才能驗 Pagefind 搜尋與列印樣式**） |
| `npm run format` | Prettier 全檔格式化 |

### 1.3 注意事項

- **`dev` 模式下沒有 Pagefind 索引**：搜尋按鈕會顯示「dev 模式無索引」提示。要驗搜尋必須 `build` 後跑 `preview`。
- 中英對照 toggle 與 quotable 段落注入皆為 client-side script，dev 與 build 皆可運作。
- 若改了 `src/config/site.ts` 的 `siteUrl`，引用卡複製出的網址會跟著變；正式部署前確認此值對齊實際網域。

---

## 2. 內容操作

### 2.1 新增 BR 章節翻譯

1. 在 `src/content/br/` 建立 `<section-id-dashed>.md`（例：`3-2-2-4.md`）。
2. 前置欄位依 [`src/content.config.ts`](./src/content.config.ts) 的 Zod schema 填入：必填 `section_id`、`original_url`、`original_version`、`status`、`translator`、`last_updated`、`order` 等。
3. 譯稿格式、術語譯名、RFC 2119 規範詞加粗、表格／清單寫法等慣例見 [`TRANSLATION_CONVENTIONS.md`](./TRANSLATION_CONVENTIONS.md)。
4. `npm run check` 確認 schema 通過。
5. `npm run build && npm run preview` 確認頁面渲染、引用卡、段落 quotable、中英對照、Pagefind 搜尋命中。
6. commit；翻譯主文件穩定前**只做本地 commit**，不 push 不建 remote（見 memory `feedback_local_only_until_content_ready`）。

### 2.2 新增術語

1. 在 `src/content/glossary/` 新增 `.md`，欄位見 schema：`term_en`、`term_zh`、`definition`，可選 `abbreviation`、`first_seen_at`、`source`。
2. 譯名來源優先順序：HiPKICA CP/CPS v1.1 附錄 1/2 → TWCA Global CPS v3.1 附錄一 → 自行擬定（並於 `source` 註明）。
3. 大量匯入見 `scripts/generate_glossary_from_hipkica.py` 與 `scripts/generate_glossary_from_twca.py`。

### 2.3 新增客服爭議卡片

1. 在 `src/content/quick-reference/` 新增 `.md`，欄位見 schema：`slug`、`question`、`short_answer`、`related_sections`（須對應已存在的 BR section_id）、`last_updated`。
2. `/quick-reference/` 列表頁會自動以 `slug` 對應 placeholder 卡片並換成正式內容；不在 placeholder 清單中的新 slug 不會出現在預設網格中（如需擴充，編輯 `src/pages/quick-reference/index.astro` 的 `placeholders` 陣列）。

### 2.4 版本徽章與升版

**徽章資料不再手動維護**。`src/config/site.ts` 的 `upstream` 已改為由
`src/lib/version.ts` 推導：

| 顯示的東西 | 來源 |
|---|---|
| 本站發布版（徽章上的 `v2.2.7`） | `src/config/br-versions.ts` 的 `brVersions[0].version` |
| 原文發布日（徽章上的日期） | 同上 `.date`——取自**該版 BR.md 標頭的 `date:`**（cabforum 在 GitHub 釋出的值） |
| 上游最新版（落後時顯示） | build 時讀 `web-spec-doc/BR.md` 的 `subtitle: Version X` |

兩個版本號不同時，徽章自動變成「上游 vX.Y.Z」，`/changelog/` 也會出現提醒。
**上游版本永遠不會被拿來當本站版本顯示**——否則客服會誤以為站上已是新版。

#### 升版流程（v2.2.7 → 下一版）

1. 更新 `web-spec-doc/BR.md` 為新版原文（`cabforum/servercert` main 分支）。
   此時徽章立刻顯示「上游 vX.Y.Z」，站上內容仍標舊版——這是正確狀態。
2. 逐節比對、重譯變動章節，把該檔 `original_version` 改為新版、`status` 視情況調整。
   **這段期間全庫會混版，是正常的**；本地 commit 不受影響，但 `git push` 會被
   pre-push hook 擋下。
3. 全部更新完成後，在 `src/config/br-versions.ts` **最上面加一列**新版
   （`date` 從新的 BR.md 標頭抄過來），舊版那列補上 `gitTag` 與 `archive`。
4. 產出舊版離線存檔並打 tag：

   ```sh
   npm run build
   node scripts/export_chapters_html.mjs --chapters all      --out "public/archive/BR_v<舊版>_zh-TW.html"
   git tag br-v<舊版> <該版最後一個 commit>
   ```

5. 確認可發布：

   ```sh
   python scripts/lint_version_consistency.py   # 要 exit 0
   ```

`/changelog/` 會自動把舊版移到「已歸檔版本」並列出存檔下載連結，站上的章節頁
永遠只保留最新版（PRD §9：不做歷史版本翻譯，歷史以 git 與存檔留存）。

---

## 3. Ballot 跟進 SOP（spec §8）

原文版本生效後 **60 天內**完成中譯與上線。

1. **監測**（spec §8.1）：訂閱 CA/Browser Forum 公告郵件列表 + 監看 CABF GitHub repo。
2. **建立追蹤 Issue**：標題 `Ballot SC-XXX 跟進`，列出涉及的章節 `section_id`。
3. **Diff 原文**：以網路 archive 或 cabforum.org diff 工具識別影響的條款檔案。
4. **翻譯**：AI 初譯 → commit `[draft]` → 隔日重讀校稿 → commit `[review]`。
5. **更新 metadata**：每動到的 `.md` 同步更新 `original_version`、`last_updated`、`ballot_refs`、必要時改 `status`（若內容大改可標 `outdated` 等待重譯）。
6. **更新 changelog**：在 `src/pages/changelog.astro` 增列該 Ballot 的條目。
7. **更新 site config**：`siteConfig.upstream.version` / `lastSyncedAt` / `behindCount` 對齊新狀態。
8. **預覽合併**：`npm run build && npm run preview` 走過影響頁。
9. **發佈**（M0-3 啟用後）：push to main → GitHub Actions 自動部署 → 確認線上版可訪問。

---

## 4. 部署（M0-3 啟用後）

> 目前 local-only 階段尚未啟用部署管線；以下為 M0-3 開放後的操作預設值。

- 觸發：push to `main`，GitHub Actions workflow `.github/workflows/deploy.yml` 自動 build + 部署 GitHub Pages。
- 預覽：每個 PR 自動上傳 build artifact（M1-11）。
- **回滾**：在 Repo Settings → Pages 切回先前的 deployment；或 `git revert` 對應 commit 後重新 push。

---

## 5. 常見維運操作

### 5.1 重建 Pagefind 索引

Pagefind 索引在 `npm run build` 末段自動產生（`pagefind --site dist`，見 `package.json#scripts.build`）。若懷疑索引異常：

```sh
rm -rf dist/
npm run build
npm run preview
```

`zh-hant-tw` 不支援 stemming（CJK 共通）會在 CLI 顯示警告，可忽略；CJK 分詞由 Pagefind 內建處理。

### 5.2 樣式修改後驗證

- Tailwind v4（`@tailwindcss/vite`）會自動掃描 `src/` 內所有 class；新增 class 後 `npm run dev` 即可見效。
- **動態 client-side 注入的 class** 必須同時出現在某個 `.astro`／`.ts` 源碼中（例：段落 quotable 注入按鈕的 class 在 `Quotable.astro` 與 `[slug].astro` 的 script 內皆有），否則 JIT 不會產出對應規則。

### 5.3 列印測試

- Chromium 系：DevTools → ⋮ → More tools → Rendering → Emulate CSS media → `print`。
- 或直接 Ctrl/⌘+P 查看預覽。
- 應隱藏：頁首 banner/nav、深底 footer、sidebar、搜尋 modal、複製按鈕、中英對照 toggle。
- 應保留：麵包屑、章節標題、版本／Ballot 資訊、章節內文、譯者資訊、免責聲明。

### 5.4 確認術語一致性（M1-10 CI 上線前的人工流程）

1. `npm run check` 過。
2. `npm run build`、開 `/glossary/` 確認新增術語有出現在正確字母分組。
3. 章節新譯文中若引用了術語，第一次出現處需可由 `GlossaryTooltip` 顯示英文原文（M2 階段全面套用）。

---

## 6. 已知雷區

- **不要 `--no-verify` 跳過 git hooks**：上游若新增 lint hook（M1-10），跳過會讓不一致內容進 main。
- **不要動 `web-spec-doc/`**：那是使用者的規劃原稿。需要更新時請改 `HANDOFF.md` 與本檔。
- **`siteConfig.repoUrl` 為 `#TODO-github-repo`**：M0-1 建 repo 後再填入；目前 footer / contact 已做 placeholder 判斷。
- **`src/content/br/3-2-2-4.md`**：是模板驗證 fixture，不是正式翻譯。M2 啟動時先 `git rm` 或直接覆寫。
- **改 remark／rehype plugin 後 build 沒變化 → 是 content layer 快取**：Astro 把章節檔的 render 結果存在 `node_modules/.astro/data-store.json`（另有 `.astro/data-store.json`），失效條件只看 markdown 內容與 `astro.config.mjs`，**不看 `scripts/*.mjs`**。改 plugin 後請先刪這兩個檔再 build：

  ```sh
  rm -f node_modules/.astro/data-store.json .astro/data-store.json
  npm run build
  ```
