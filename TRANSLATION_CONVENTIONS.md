# TRANSLATION_CONVENTIONS — 譯稿格式與用語慣例

> 給未來版本（v2.2.8、v2.3.0…）的翻譯者／審閱者依循。本檔為長期約定，與
> 一次性的 `TRANSLATION_BRIEF.md`（gitignored、特定版次的潤稿提示）分工不同。
> 對應 `CLAUDE.md` 的「Language」原則與 `RUNBOOK.md` §2.1 新增章節流程。

---

## 1. 章節檔基本結構（Style A 雙語對照）

每個 `src/content/br/X-Y-Z.md` 採「**英文 quoted blockquote + 中文段落**」交錯：

```markdown
---
title: "中文標題"
section_id: "X.Y.Z"
parent: "X.Y"
order: <int>
original_url: "https://cabforum.org/.../#xyz-anchor"
original_version: "2.2.7"
ballot_refs: []
translator: "..."
last_updated: YYYY-MM-DD
status: draft | translated | reviewed | outdated
tags: []
---

> **English Section Title**

> English paragraph here.

中文翻譯段落。

> Next English paragraph.

下一個中文段落。
```

每個英文段落／清單／表格用 `> ` blockquote 引用，緊接著對應中文翻譯（不加 `> `）。

**例外**：定義條目（§1.6.1）、縮寫表（§1.6.2 內表格）等內容單元，英文行已直接嵌入中文版本（例如 `**Term（中譯）**：說明`），不再另做 quote 對照。

---

## 2. 表格

### 2.1 雙表格式

英文表完整 quoted，緊接中文表（中間僅單空行）：

```markdown
> | **English Header A** | **English Header B** |
> | -- | -- |
> | en-row1-a | en-row1-b |
> | en-row2-a | en-row2-b |

| **中文表頭 A** | **中文表頭 B** |
| -- | -- |
| 中文列 1-a | 中文列 1-b |
| 中文列 2-a | 中文列 2-b |
```

**禁止**：將 EN 列與 CN 列逐列交錯（會破壞 markdown 表格的「header → separator → row 連續」要求，渲染為純文字）。歷史上 §3.2.2.9、§4.2.1 曾發生此 bug。

### 2.2 不要寫 `Table:` caption

BR.md 原文使用 **Pandoc 風格** 的表格 caption：

```markdown
Table: My caption

| col1 | col2 |
| ---- | ---- |
```

Pandoc 會把 `Table:` 那行轉成 `<caption>` 元素。但 **Astro / remark 預設不支援此擴充**，會把 `Table: ...` 渲染為一般段落純文字，看起來像 bug。

**做法**：拆檔時把 BR.md 的 `Table: ...` 行（與翻譯的「表：...」行）一併移除。表頭的粗體標籤已足以說明用途。

若未來真有需要顯示 caption，請改用 remark plugin 或手動寫 `<figure><figcaption>...</figcaption><table>...</table></figure>`，不要保留裸 `Table:`。

---

## 3. RFC 2119 規範詞處理

### 3.1 加粗時機（嚴格規則）

只有原文**全大寫**的 RFC 2119 關鍵字才加粗並括註英文：

| 原文（ALL CAPS） | 中譯（加粗 + 括註） |
|---|---|
| `MUST` | `**應（MUST）**` |
| `MUST NOT` | `**不得（MUST NOT）**` |
| `REQUIRED` | `**必要（REQUIRED）**` |
| `SHALL` | `**應（SHALL）**` |
| `SHALL NOT` | `**不得（SHALL NOT）**` |
| `SHOULD` | `**宜（SHOULD）**` |
| `SHOULD NOT` | `**不宜（SHOULD NOT）**` |
| `RECOMMENDED` | `**建議（RECOMMENDED）**` |
| `NOT RECOMMENDED` | `**不建議（NOT RECOMMENDED）**` |
| `MAY` | `**得（MAY）**` |
| `OPTIONAL` | `**選用（OPTIONAL）**` |
| `NOT REQUIRED` | `**非必要（NOT REQUIRED）**` |

### 3.2 小寫 = 描述性，不加粗

原文若是小寫 `shall` / `may` / `must` / `should` / `optional` 等，**屬於一般描述用詞**（如 "shall be interpreted"、"this method may only be used"、"CAA checking is optional"），中譯只用「應／得／必須」等普通動詞，**不加粗**、**不括註英文**。

歷史誤判修補：§1.5、§1.6.4、§2.4、§3.2.2.4、§3.2.2.4.12、§3.2.2.8 共修過 9 處。

---

## 4. 術語譯名

### 4.1 優先順序

1. **HiPKICA CP/CPS v1.1 附錄 1／附錄 2**（`web-spec-doc/HiPKICA-CP_CPS_v1.1.pdf`）— 最高優先
2. **TWCA Global CPS v3.1 附錄一**（`web-spec-doc/TWCA-GLOBAL-CPS-V3.1.pdf`）— HiPKICA 未覆蓋時補入
3. **既有 `src/content/glossary/` 條目**
4. 自行擬定（記得 commit 到 glossary，並於 `source` 註明）

### 4.2 鎖定譯名（不可使用其他譯法）

| 英文 | 中譯 | 不要用 |
|---|---|---|
| Baseline Requirements（全稱） | **基本要求** | 基準、基準要求 |
| 指代 these Requirements / this document | **本文件**／**本文件要求**（依語境） | 本基準、本要求 |
| Subscriber | **用戶** | 訂閱者 |
| Certificate Revocation List | **憑證廢止清冊**（CRL） | 撤銷清單 |
| Publicly-Trusted | **公開信賴** | 公眾信任、公共可信 |
| CA/Browser Forum 文件名引用 | `《基本要求》`（中文加書名號簡稱） | 純英文書名 |
| Multi-Perspective Issuance Corroboration | **多視角簽發佐證**（MPIC） | 多視角驗證 |

### 4.3 使用者面向用詞

| 用 | 不用 |
|---|---|
| 翻譯 | 中譯 |
| 章節細項 | 條款 |
| 本翻譯為非官方翻譯，發生爭議時以 CA/Browser Forum 英文原文為準 | 本中譯為非官方… |

引用卡（CitationCard）的免責文字**逐字硬編碼**於 `src/components/CitationCard.astro`，**不可改寫**。

---

## 5. 書名格式（C 方案）

首次出現完整書名，採「中文書名（English Full Title，簡稱）」格式；後續一律用簡稱。

```markdown
《公開信賴 TLS 伺服器憑證簽發與管理之基本要求》（Baseline Requirements for the
Issuance and Management of Publicly-Trusted TLS Server Certificates，以下簡稱
《基本要求》）
```

後續引用：`《基本要求》`（含書名號）。

舊版引用（如 §7.2 引用 v1.8.7）應補充說明差異：「《公開信賴憑證簽發與管理之基本
要求》（**無 TLS Server**）第 1.8.7 版」。

WebTrust 等他家文件名（如「SSL Baseline」）**不加** 《》。

---

## 6. 巢狀／編號清單

英文清單整段 quoted，緊接中文清單：

```markdown
> 1. EN item one
> 2. EN item two
>    a. EN sub-item a
>    b. EN sub-item b

1. 中文項目一
2. 中文項目二
   a. 中文子項目 a
   b. 中文子項目 b
```

不要把英文與中文逐項交錯（同表格規則）。

---

## 7. 標題格式

雙行 Style A：

```markdown
> ##### English Heading Text
##### 中文標題文字
```

英文標題以 `> ` blockquote 引用（搭配既有的中英對照 toggle CSS），中文標題為實際 markdown heading（會出現在 TOC／anchor／sidebar）。

頂層章節保留尾句號：`## 1. 簡介`。附錄獨立格式：`> # Appendix A – CAA Contact Tag` + `# 附錄 A — CAA 聯絡標籤`。

---

## 8. 章節頁前置欄位 — `status` 升級流程

新增章節時預設 `status: draft`。經人工 review 後依下列順序升級：

- `draft` → 機器初譯／粗潤完成、未經人工驗收
- `translated` → 譯者本人或他人通讀過，視為可用
- `reviewed` → 至少兩人交叉 review 完成（含術語一致性、規範性語義正確性）
- `outdated` → 上游 Ballot 已改動此節但譯稿尚未跟上

目錄頁 `/server-cert-br/table-of-contents/` 會自動統計各狀態數量。

---

## 9. 程式碼區塊與 ASN.1

ASN.1 模組、shell 範例等程式碼區塊**不翻譯**，原樣保留於 fenced code block。註解（若有）可加中文。`remark-code-figure` plugin 會自動為其加上語言標籤與複製按鈕。

```asn1
SubjectPublicKeyInfo  ::=  SEQUENCE  {
  algorithm            AlgorithmIdentifier,
  subjectPublicKey     BIT STRING
}
```

---

## 10. 上游版本切換（v2.2.7 → 下一版）流程

1. 更新 `web-spec-doc/BR.md` 為新版本原文（從 [`cabforum/servercert`](https://github.com/cabforum/servercert) 抓 main 分支）。
2. 跑 `scripts/diff_br.py`（暫不存在，未來補）或人工 diff 看哪些章節變動。
3. 把改動的章節 `status` 改為 `outdated`，重新翻譯後再升回 `translated`。
4. 更新 `src/config/site.ts` 的 `upstream.version` 與 `lastSyncedAt`。
5. 補 §1.2.1 新增的 Ballot 列、§1.2.2 新增的合規日期列。
6. 全站 `last_updated` 仍維持各檔自己的最後潤稿日期，**不要全檔批量改**。

---

## 11. 工具腳本參考

- `scripts/unify_headings.py` — 統一三波翻譯的標題格式為 Style A
- `scripts/split_to_collection.py` — 把潤稿主檔拆成單節 `.md`
- `scripts/interleave_wave1_paragraphs.py` — 把全 EN→全 CN 改為逐段交錯
- `scripts/remark-code-figure.mjs` — Remark plugin，為 code block 加 toolbar

不在 repo 中的 hot-fix 腳本（補英文表 blockquote、移除 Pandoc `Table:` caption 等）已在歷史 commit 訊息中說明做法，未來如需重做可參考 commit `13558e3`、`17e34ed`、本檔對應的整理 commit。
