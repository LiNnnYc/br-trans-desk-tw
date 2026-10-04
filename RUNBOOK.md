# RUNBOOK — BR 翻譯小站維運手冊

> 本檔對應 milestone **M1-13**，內容為「常做的事」與「出狀況時怎麼辦」。
> 譯名與排版慣例請看 [`TRANSLATION_CONVENTIONS.md`](./TRANSLATION_CONVENTIONS.md)。

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
- 中英對照 toggle 為 client-side script，dev 與 build 皆可運作。
- 若改了 `src/config/site.ts` 的 `siteUrl`，術語表詳細頁的結構化資料網址會跟著變；正式部署前確認此值對齊實際網域。

---

## 2. 內容操作

### 2.1 新增 BR 章節翻譯

1. 在 `src/content/br/` 建立 `<section-id-dashed>.md`（例：`3-2-2-4.md`）。
2. 前置欄位依 [`src/content.config.ts`](./src/content.config.ts) 的 Zod schema 填入：必填 `section_id`、`original_url`、`original_version`、`status`、`translator`、`last_updated`、`order` 等。
3. 譯稿格式、術語譯名、RFC 2119 規範詞加粗、表格／清單寫法等慣例見 [`TRANSLATION_CONVENTIONS.md`](./TRANSLATION_CONVENTIONS.md)。
4. `npm run check` 確認 schema 通過。
5. `npm run build && npm run preview` 確認頁面渲染、中英對照、Pagefind 搜尋命中。
6. commit；翻譯主文件穩定前**只做本地 commit**，不 push 不建 remote（見 memory `feedback_local_only_until_content_ready`）。

### 2.2 新增術語

1. 在 `src/content/glossary/` 新增 `.md`，欄位見 schema：`term_en`、`term_zh`、`definition`，可選 `abbreviation`、`first_seen_at`、`source`。
2. 譯名來源優先順序：HiPKICA CP/CPS v1.2 附錄 1/2 → TWCA Global CPS v3.2 附錄一 → 數位發展部主管法規（電子簽章法、數位簽章憑證實務作業基準應載明事項）→ 自行擬定（並於 `source` 註明）。
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
| 上游最新版（落後時顯示） | build 時讀 `upstream/BR.md` 的 `subtitle: Version X` |

兩個版本號不同時，徽章自動變成「上游 vX.Y.Z」，`/changelog/` 也會出現提醒。
**上游版本永遠不會被拿來當本站版本顯示**——否則客服會誤以為站上已是新版。

#### 升版流程（v2.2.7 → 下一版）

> **順序很重要：先封存舊版，再換原文。** `upstream/BR.md` 檔名不帶版本號
> （上游 cabforum 每一版都叫 BR.md），一旦覆蓋掉，比對基準就沒了。所以**步驟 0
> 必須在動 BR.md 之前完成**——不要像早期版本的 SOP 那樣把打 tag 排到最後，
> 那會逼你事後回頭指認「該版最後一個 commit」，指錯就前功盡棄。

**步驟 0：封存現行版（動 BR.md 之前）**

```sh
git status                       # 必須乾淨——存檔要對應得上 commit
```

1. `src/config/br-versions.ts` 現行版那列補上 `gitTag: 'br-v<舊版>'`
   （`archive` 在該版還是最新版時就已填好）。
2. 封存英文原文（**檔名帶版本號，方便人找**）：

   ```sh
   cp upstream/BR.md upstream/BR_archive/BR-v<舊版>.md
   ```

3. 確認中文下載檔與現行內容一致（該版當最新版時已由 `node scripts/build_downloads.mjs` 產生）：

   ```sh
   python scripts/lint_downloads.py   # exit 0 就不用重出；不一致就先重跑 build_downloads.mjs 再 commit
   ```

   > 2026-09-25 之前的做法是在這一步用 `export_chapters_html.mjs` 另外匯出離線存檔（v2.2.7 就是這樣做的）；
   > 現在下載檔隨最新版維護，封存時只需確認。

4. commit 上述兩項（＋重出的下載檔，若有），然後對**該 commit** 打 tag：

   ```sh
   git tag -a br-v<舊版> -m "TLS BR v<舊版> 繁體中文翻譯（全文審閱完成）"
   ```

**步驟 1：換上新版原文**

```sh
# 從 cabforum/servercert main 分支取得新的 BR.md
```

此時版本徽章立刻顯示「上游 vX.Y.Z」、`/changelog/` 出現落後提醒，而站上內容仍標
舊版——**這是正確狀態**，不要急著改 `br-versions.ts`。

**步驟 2：比對出哪些章節真的變了**

```sh
python scripts/diff_br_versions.py
```

自動拿 `BR_archive/` 最新的封存版（或 `br-v*` tag）跟新的 BR.md 逐節比對，列出
內容變動／新增／刪除各幾節、對應到哪些 `src/content/br/*.md`。
看單節差異：`--show-diff 6.3.2`。要把變動章節一次標記成待重譯：

```sh
python scripts/diff_br_versions.py --mark-outdated --write
```

**步驟 3：重譯變動章節**

把該檔 `original_version` 改為新版、`status` 改回 `translated`。
**這段期間全庫會混版，是正常的**；本地 commit 不受影響，但 `git push` 會被
pre-push hook 擋下。

**步驟 4：宣告新版**

1. **內容未變動的章節也要把 `original_version` 改為新版**——`lint_version_consistency.py`
   要求全庫一致。改之前先確認這些節在新舊原文間真的一字未變
   （v2.3.0 升版時是 391 節，逐節比對 `BR_archive/BR-v<舊版>.md` 與 `BR.md` 後才批次改）。
   只改該行，`last_updated` 不動（譯文沒變）。
2. 若升版有**新增章節**，`order` 依 `section_id` 自然排序（同 `src/lib/section.ts` 的
   `compareSectionId`）**從 1 起**重新連號。`order` 目前沒有程式讀取（排序走 `section_id`），
   但維持連號可避免日後誤用；新節插在中間時編號必然整片位移，建議與譯文分開 commit。
3. `src/config/br-versions.ts` **最上面加一列**新版（`date` 從新的 BR.md 標頭抄過來），
   `archive` 填 `BR_v<新版>_zh-TW`（最新版也提供下載，`lint_downloads.py` 要求第一列必須有）。
   `gitTag` 先不填——**要到下一次升版的步驟 0 封存時才補**。

**步驟 5：確認可發布**

```sh
python scripts/lint_version_consistency.py   # 要 exit 0
```

接著：

1. `node scripts/build_downloads.mjs` 產生新版下載檔，`public/archive/` 與 `src/config/downloads-stamp.json` 一起 commit。
2. `README.md` 的全文下載連結寫死了版本號，改成新版。
3. `/news/` 視需要新增「原文動態」「翻譯更新」（`src/content/news/`）。
4. push 時連同步驟 0 的 tag：`git push origin main br-v<舊版>`。

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
- 應隱藏：頁首 banner/nav、深底 footer、sidebar、搜尋 modal、中英對照 toggle。
- 應保留：麵包屑、章節標題、版本／Ballot 資訊、章節內文、譯者資訊、免責聲明。

### 5.4 確認術語一致性（M1-10 CI 上線前的人工流程）

1. `npm run check` 過。
2. `npm run build`、開 `/glossary/` 確認新增術語有出現在正確字母分組。
3. 章節新譯文中若引用了術語，第一次出現處需可由 `GlossaryTooltip` 顯示英文原文（M2 階段全面套用）。

---

## 6. 已知雷區

- **不要 `--no-verify` 跳過 git hooks**：上游若新增 lint hook（M1-10），跳過會讓不一致內容進 main。
- **不要刪 `upstream/BR.md`**：建置時 `src/lib/version.ts` 會讀它取得上游版本與日期，刪掉會建置失敗。
- **改 remark／rehype plugin 後 build 沒變化 → 是 content layer 快取**：Astro 把章節檔的 render 結果存在 `node_modules/.astro/data-store.json`（另有 `.astro/data-store.json`），失效條件只看 markdown 內容與 `astro.config.mjs`，**不看 `scripts/*.mjs`**。改 plugin 後請先刪這兩個檔再 build：

  ```sh
  rm -f node_modules/.astro/data-store.json .astro/data-store.json
  npm run build
  ```
