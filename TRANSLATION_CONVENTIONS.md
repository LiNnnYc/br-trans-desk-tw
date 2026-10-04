# TRANSLATION_CONVENTIONS — 譯稿格式與用語慣例

> 給未來版本（v2.2.8、v2.3.0…）的翻譯者／審閱者依循。本檔為長期約定，與
> 一次性的 `TRANSLATION_BRIEF.md`（gitignored、特定版次的潤稿提示）分工不同。
> 對應 `RUNBOOK.md` §2.1 新增章節流程。

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

**例外**：§1.6.1 定義條目雖屬「術語表」性質，仍採 Style A（每條 `> **Term**: 英文釋義` + 中文 `**中譯**：釋義`）；中文行粗體只放中譯（無中文名者如 `Linting`／`WHOIS`／`P-Label`／`XN-Label`／`Requirements` 保留英文粗體）。此區由 `scripts/add_en_to_definitions_1_6_1.py` 從 BR.md 一次性產生（見 §11）。§1.6.2 縮寫表同樣補了英文 quoted 表對照。

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

### 2.2 表格 caption：保留並緊鄰表格上方

BR.md 原文使用 **Pandoc 風格** 的表格 caption，Pandoc 會渲染成表格底端的 `<caption>`：

```markdown
Table: My caption

| col1 | col2 |
| ---- | ---- |
```

本站以 **`scripts/rehype-table-caption.mjs`**（rehype plugin）支援之：把緊鄰 `<table>` 上方的 `Table:`／`表：` 段落轉成 `<caption>` 並置於表格內，由 `global.css` 的 `caption-side: bottom` 顯示在表格底端，對齊 cabforum.org（Pandoc）的渲染。

> **沿革**：早期（commit `69b7baf`）因 remark 不認 Pandoc caption、`Table:` 被當純文字而**整批移除**；2026-06 改為「保留＋plugin 轉 `<caption>`」（本節即新慣例），caption 由 `scripts/restore_table_captions.py` 從 BR.md（英文）＋ git `69b7baf^`（已譯中文）回填。

**做法**（plugin 依賴的格式，務必遵守）：caption 段落須**緊鄰**其表格的上方（中間僅一個空白行），中英各自貼著自己的表格：

```markdown
> Table: My caption
>
> | EN col | ... |
> | ----   | --- |

表：我的表格說明

| 中文欄 | ... |
| ----   | --- |
```

- 英文 caption 寫在 blockquote 內（`> Table: ...` 後接 `>` 空行再接表格），與英文表同屬一個 blockquote。
- 中文 caption 寫 `表：...`（全形冒號）後接一個空白行再接中文表。
- caption 內可含 inline `` `code` ``（如 `` `policyQualifiers` ``），plugin 會保留。
- 每個 `<table>` 另會被 plugin 包進 `<div class="table-wrap">`（水平捲動），表格維持 `display:table` 以確保 `caption-side: bottom` 在全文頁也生效。

### 2.3 欄位階層縮排（U+2007）

BR.md 以前導空白表示欄位從屬關係（`    revokedCertificates` 隸屬於 `tbsCertList`）。HTML 會摺疊一般空白，故 `scripts/preserve_table_indent.py` 把它轉成 **U+2007 FIGURE SPACE**（數字寬空白，不會被摺疊）寫在儲存格開頭：

```markdown
|     `revokedCertificates` | * | 若 CA 已簽發… |
```

- **層級對應**：目前語料用 2／4／8 個 U+2007（4＝一層、8＝兩層；2 是 §7.1.2.10.8 的半層）。沿用即可，不要改成一般空白或 `&nbsp;`。
- **render 時會被搬到 CSS padding**：`scripts/rehype-table-indent.mjs` 在 build 時把前導 U+2007 從文字拿掉，改成 `<td class="cell-indent" style="--cell-indent:4">`。
  原因：縮排若留在文字流裡，會被 `overflow-wrap: anywhere`（讓長識別碼不撐爆欄寬的規則）視為斷行點，該儲存格的 min-content 只剩識別碼寬度；同列其他欄一長、第一欄被壓到最小寬度時，縮排就留在上一行、識別碼貼齊左緣，看起來完全沒縮排（實例：§7.2「CRL 欄位」表的 `revokedCertificates`）。改成 padding 後縮排不參與換行、且計入欄寬下限，任何寬度都不會失效。
- 因此**譯稿只管照原文寫 U+2007**，排版問題由 plugin 處理，不需要為了視覺效果調整字數或改用別的字元。
- **不要混用半形空白**：`|    ␣␣␣`base`` 這種「U+2007 + 半形空白」寫法，半形部分會被 HTML 摺疊，第二層就跟第一層一樣寬、階層整個消失（實例：§7.1.2.10.8 的中文表曾把第一層寫成 4 個 U+2007、第二層寫成 4 個 U+2007＋3 個半形空白，兩層看起來一樣）。加深一層就是**再加一組 U+2007**。
- **中英兩表層級要一致**：同一個識別碼在英文表與中文表的縮排數必須相同。以上兩點由 `scripts/lint_table_indent.py` 機械檢查。

### 2.4 長識別碼不會被從中間切斷

`global.css` 對 `td` 設了 `overflow-wrap: anywhere`（避免長識別碼撐爆欄寬），代價是瀏覽器可以在**任意字元間**斷行。為了不讓 `cessationOfOperation` 這種語意單元被切成兩半，`scripts/remark-table-nowrap.mjs` 會把「原子 token」儲存格標成 `nowrap`：

- 無空白且 ≤16 字元（日期、版號、章節編號…），或
- 無空白、≤40 字元且**內容全為 ASCII**（ASN.1 欄位名 `authorityInformationAccess`、OID `0.9.2342.19200300.100.1.25`、CRLReason `cessationOfOperation`、時間戳 `2025-06-15T12:00:00Z`）。

**為什麼限定 ASCII**：中文句子本來就沒有空白，若只看「無空白」，整句中文會被判成原子 token 而 `nowrap`，直接撐爆版面。

整欄 body 都是原子 token 時另加 `col-shrink`（`width: 1%`），欄寬收到內容寬度、把空間讓給說明欄。反面案例：§7.2.2 CRLReasons 表第一欄原本因為 `affiliationChanged`（18 字元）超過舊的 16 字元上限而未標 nowrap，欄位被說明欄擠窄後，識別碼就從中間斷成兩行。

inline `` `code` `` 另有 `.clause-body td code { white-space: nowrap }` 保護；**未加反引號的純文字識別碼**（BR.md 原文有些表格就是這樣寫）則靠上述規則。

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

**表格儲存格也一樣加粗**（2026-10-04 定版）：憑證剖繪等表的「必要性」欄（`**應（MUST）**`、`**不建議（NOT RECOMMENDED）**`…）、
§1.2.1 版本表的 Ballot 名稱等，只要原文是全大寫關鍵字就加粗，與內文同一規則。只加粗關鍵字本身，前後的符號不包進去
（`**應（MUST）**／**得（MAY）**`）。英文 blockquote 側照抄原文，不加粗。第 7 章原本有 250 處未加粗、240 處已加粗，已一次補齊。

### 3.2 小寫 = 描述性，不加粗

原文若是小寫 `shall` / `may` / `must` / `should` / `optional` 等，**屬於一般描述用詞**（如 "shall be interpreted"、"this method may only be used"、"CAA checking is optional"），中譯只用「應／得／必須」等普通動詞，**不加粗**、**不括註英文**。

歷史誤判修補：§1.5、§1.6.4、§2.4、§3.2.2.4、§3.2.2.4.12、§3.2.2.8 共修過 9 處。2026-06-21 以 `scripts/lint_rfc2119.py` 全文對照，再修 8 處 over-bold（小寫 `shall`/`may`/`must`/`required` 被誤標，含 §1.5.2、§3.2.2.4.16/.17、§3.2.2.9、§7.1.4.1、§7.1.4.3、§7.1.2.11.2 等）。2026-07-12 再修 §5.7.1.1 一處：小寫 `shall`（"CA organizations shall have…"）被誤標 `**應（shall）**`，改回一般動詞「應」（不加粗、不括註）。

### 3.3 大寫動詞形也是關鍵字

`RECOMMENDS` / `RECOMMEND`（如 "This Profile RECOMMENDS that…"、"These Baseline Requirements RECOMMEND…"）是 `RECOMMENDED` 的大寫動詞形，**仍屬規範詞**，中譯標 `**建議（RECOMMENDED）**`（用標準關鍵字形）。`REQUIRES` 同理對應 `**必要（REQUIRED）**`。

### 3.4 「大寫關鍵字 + 小寫 not」：否定來自大寫詞，不另標 NOT 變體

原文若為 `SHALL not use` / `MUST respect … and not issue`（大寫 `SHALL`/`MUST` 統轄一個小寫 `not`），否定的規範力來自前面那個大寫詞，**不要**把它標成完整的 `**不得（SHALL NOT）**` / `**不得（MUST NOT）**`（那會無中生有一個原文沒有的全大寫關鍵字）。

- `… SHALL not use …` → `**應（SHALL）**……不再使用`（或保留「不得」但不加 NOT 括註）
- `… MUST respect … and not issue …` → `**應（MUST）**遵守……且……不簽發`（單一 MUST 分配到兩個動詞）

歷史修補：§3.2.2.8（2026-06-21 改）。§3.2.2.4.7／§3.2.2.5.1 的 `SHALL not use` 暫保留「不得（SHALL NOT）」（語意忠實），如日後求嚴謹再依此規則調整。

### 3.5 非 RFC 2119 的同形詞，不加粗

下列情境的字詞與 RFC 2119 關鍵字同形，但**不是**規範詞，保留原文純文字、不加粗：

- **ASN.1 關鍵字**：`OPTIONAL` 欄位、`DEFAULT` 值（如 §7.1.2.8.4 "DEFAULT values within OPTIONAL fields"）——屬 ASN.1 語法，非規範動詞。
- §1.6.4 列舉關鍵字本身（"the key words MUST, SHALL, … are to be interpreted"）為定義引用，非該句的規範語氣。

### 3.6 每個規範詞出現都標英文括註

同一段落內相同關鍵字重複出現時，**每一次**都標完整 `**應（SHALL）**` / `**得（MAY）**`，**不省略**英文括註。

> 沿革：2026-07-12 前的慣例為「首次標英文、其餘同詞僅加粗 `**得**`」；因審閱時 bare 形式易被誤認為漏標、且對照不便，改為「每次都標」。既有的 bare 形式已補齊（如 §4.1.2 `**得**`→`**得（MAY）**`）。

唯一例外：並列「A 得 X，或 Y」結構中，`得` 可分配到「或」之後而不重複出現粗體（此時英文側 MAY 數會多於中文括註數，屬 under-bold 雜訊，如 §9.6.3）。

> `scripts/lint_rfc2119.py` 的「bare 粗體」檢查會抓出任何無括註的 `**應**`／`**得**` 等，一律視為漏標須補。

### 3.7 機械校驗：`scripts/lint_rfc2119.py`

對照 `src/content/br/*.md` 各檔的英文 blockquote 大寫關鍵字數與中文括註數：

- **over-bold**（中文 > 英文）＝原文無大寫關鍵字卻被誤標，**須逐處核對修正**（本檔 §3.2 之主要用途）。
- **under-bold**（英文 > 中文）＝參考用，多為 §3.5 同形詞或 §3.6 例外（`得`分配於「或」），須人工確認是否真漏標。
- **bare 粗體**（2026-07-12 新增，逐 span 掃描）＝無括註的 `**應**`／`**得**` 等，依 §3.6「每次都標」一律須補英文括註。
- **畸形括註**（2026-07-12 新增）＝括號內非標準全大寫關鍵字（如 `**應（shall）**` 用了小寫，或拼錯），須逐處核對——多半是原文小寫（§3.2 應去標）或大小寫誤植。

腳本已知限制：不解析註腳（`[^x]:`，無英文對照、已跳過）、不處理 §3.4 的「大寫詞 + 小寫 not」（會同時出現在 over/under 兩側）；bare／畸形括註掃描僅比對粗體 span 文字本身，不查該處英文語境。BR 版本升級後可重跑做回歸對照。

---

## 4. 術語譯名

### 4.1 優先順序

1. **HiPKICA CP/CPS v1.2 附錄 1／附錄 2**（附錄 1 的 4 筆仍依 v1.1）— 最高優先
2. **TWCA Global CPS v3.2 附錄一**— HiPKICA 未覆蓋時補入
3. **數位發展部主管法規**（電子簽章法〔華總一義字第11300039241號〕、數位簽章憑證實務作業基準應載明事項〔數授產經字第1134000891號〕）— 法規用語，前兩者未覆蓋時補入；已收錄者一律以 `sources` 併列保留，供爭議時引用
4. **既有 `src/content/glossary/` 條目**
5. 自行擬定（記得 commit 到 glossary，並於 `source` 註明）

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
| No stipulation（空白章節標記） | **不作規定** | 無規定、未作規定 |

#### 4.2.1 v2.3.0（SC-101v2）ADN 相關定版

以下由 §3.2.2.4 人工審閱定案（2026-09-09），§4.2.2.1 家族審閱再補（2026-09-10），
**§3.2.2.4 全家族、§4.2.2 全家族與附錄 B 一律沿用**：

| 英文 | 中譯 | 不要用 |
|---|---|---|
| Authorization Domain Name（內文首次） | **經授權網域名稱（Authorization Domain Name，ADN）** | 經授權網域名稱（ADN, Authorization Domain Name） |
| Authorization Domain Name（內文後續） | **經授權網域名稱（ADN）**——**同一句重複多次也不裸寫** | 裸寫 `ADN` |
| Prune（§3.2.2.4 對照表欄名） | **刪減（Prune）** | 刪除（Prune）、修剪 |
| prune（動詞，句中） | **刪除**（刪除最左側網域標籤） | 刪減、修剪 |
| Wildcard（§3.2.2.4 對照表欄名） | **萬用網域（Wildcard）** | 萬用（Wildcard） |
| Method（§3.2.2.4 對照表欄名） | **驗證方法** | 方法 |
| has a check in the X column | **於下表「X」欄中標示「✔」** | 於下表「X」欄標示為 ✔ |
| applied-for（FQDN） | **所申請的** | 申請的 |
| given（FQDN） | **指定之** | 給定之、所指之 |
| Initialize `A` to … | **將 `A` 設為…** | 將 `A` 初始化為… |
| validation of domain authorization or control | **網域授權或控管權驗證** | 網域授權或控制驗證 |
| CAA record lookup(s) | **CAA 紀錄檢查** | CAA 紀錄查詢 |
| CAA check / CAA checking | **CAA 檢查** | CAA 查核 |
| IANA ACME Validation Methods registry | **保留原文不譯** | IANA ACME 驗證方法登錄簿 |
| ACME Account URL | **保留原文不譯** | ACME 帳戶網址 |
| URI scheme | **保留原文不譯**（如「acct」URI scheme） | URI 協定、URI 配置 |
| account | **帳號** | 帳戶 |
| subsection | **小節** | 子節 |
| bind / binding | **繫結** | 綁定、連結 |
| register / registered | **登記** | 登錄 |
| Effective `<date>`（句首時間狀語） | **自 `<date>` 起，…** | 自 `<date>` 起生效，… |
| DNS TXT Record | **DNS TXT 紀錄** | DNS TXT Record（中文側照抄英文） |
| DNS TXT Record Phone Contact／Email Contact | **DNS TXT 紀錄電話聯絡人／電子郵件聯絡人**，檔內首次加英文括註 | DNS TXT Record 電話聯絡人 |
| DNS CAA Phone Contact／Email Contact | **DNS CAA 電話聯絡人／電子郵件聯絡人**，檔內首次加英文括註 | DNS CAA 電子郵件聯絡地址 |
| EV Guidelines | **《EV 指引》** | EV Guidelines（中文側照抄英文） |
| underscore（character） | **底線**（字元） | 下底線 |
| Section `N`（中文句中引用他份文件的節號） | **第 `N` 節** | Section `N` |
| Automated Certificate Management Environment | **自動憑證更新環境（ACME）** | 自動化憑證管理環境 |
| Account URI | **保留原文不譯** | 帳號 URI |
| ADN selection algorithm（§3.2.2.5.3 等） | **選擇經授權網域名稱（ADN）的判斷流程** | ADN 選取演算法 |
| (ADNs must be) derived | **決定** | 推導 |
| Clarify …（Ballot 名稱，§1.2.1） | **明定…** | 釐清…、明訂… |
| Clarification（名詞，Ballot 名稱） | **釐清** | |

**縮寫括註的兩套格式，不要混用**：

- **§1.6.1 定義條目**：`中譯（縮寫, English Full Name）`，半形逗號。
  例：`憑證廢止清冊（CRL, Certificate Revocation List）`、
  `經授權網域名稱（ADN, Authorization Domain Name）`。這是定義章自己的格式。
- **一般內文**：`中譯（English Full Name，縮寫）`，全形逗號；同一檔後續出現簡化為
  `中譯（縮寫）`。例：`完全吻合網域名稱（Fully-Qualified Domain Name，FQDN）`、
  `經授權網域名稱（Authorization Domain Name，ADN）` → 後續 `經授權網域名稱（ADN）`。

**節標題的「之」**：`X of Y`／`Y requirements` 這類標題，中譯用「之」連接，不要省略。

| 英文節標題 | 中譯 |
|---|---|
| Validation of Domain Authorization or Control | 網域授權或控管權**之**驗證 |
| CAA record processing | 授權憑證機構簽發憑證（CAA）紀錄**之**處理 |
| DNSSEC Validation Requirements | DNSSEC 驗證**之**要求 |
| DNS Resolver Requirements | DNS 解析器**之**要求 |

**CAA 節標題一律用全稱**「授權憑證機構簽發憑證（CAA）…」，**子節也不例外**：

| 節 | 標題 |
|---|---|
| §3.2.2.8 | 授權憑證機構簽發憑證（CAA）紀錄 |
| §4.2.2.1 | 授權憑證機構簽發憑證（CAA）紀錄**之**處理 |
| §4.2.2.1.1 | 授權憑證機構簽發憑證（CAA）**之**多視角簽發佐證 |
| §4.2.2.1.2 | 授權憑證機構簽發憑證（CAA）**之**參數 |

> **沿革**：2026-09-10 曾誤記為「子節用簡稱 CAA」（當時 §4.2.2.1.1／.1.2 的初稿是簡稱），
> 2026-09-12 審閱把兩節都改為全稱，**規則是一律全稱**。
> 目前唯一例外是 §3.2.2.8.1「CAA 紀錄的 DNSSEC 驗證」——舊標題，本次未一併改。

**IANA 的登錄簿／資料庫等專有名稱保留英文**，不譯、不加中文括註——比照 §1.6.1 對
`IANA Root Zone Database` 的既有處理。實例：§4.2.2.1.2 的連結文字寫
`[IANA ACME Validation Methods registry](…)`。
（`IANA DNSSEC root trust anchor` 是例外：既有譯文作「IANA DNSSEC 信賴根源
（IANA DNSSEC root trust anchor）」，已審閱定稿，維持不動。）

> **ADN 重複時的寫法已定案（2026-09-13）**：§3.2.2.4.16／.17 原本的「首次全稱、後續裸寫 ADN」
> 已由審閱全部改成「經授權網域名稱（ADN）」，即使一句話出現三次也照寫。
> 全庫殘留 1 處：`5-4-1.md` 第 74 行「所使用之 ADN 與所申請的 FQDN 不相同」。

> **「自動憑證更新環境」不是誤譯**（2026-09-13 審閱者說明）：`Management` 字面是「管理」，
> 但台灣兩大 CA 都稱 ACME 為「自動憑證更新環境」——業界對 ACME 的認知就是憑證自動更新，
> 而非管理整個憑證生命週期。glossary `automated-certificate-management-environment.md`
> 早已收錄（來源 TWCA Global CPS v3.2 附錄一）。**依 §4.1 優先順序，國內 CA 既有譯名優先於字面直譯**，
> 質疑譯名前先查 glossary。

> **附錄 B 有一處本站補充的括號說明**（2026-09-13 審閱加入）：v2.3.0 附錄 B.2.a 引用
> 「This method allows Onion Domain Name issuance」，但 §3.2.2.4 底下沒有任何方法寫這句
> （上游改用對照表的 Onion 欄後漏改）。中文在該處補「（指第 3.2.2.4 節表格中 Onion 欄位標示「✔」的方法）」。
> **這段括號是刻意加的，英文側沒有對應文字，不要當成多譯刪掉。**上游若修正此句，再回頭拿掉。

**以下是審閱時出現、但全庫未一致的潤飾——不是定版，勿逕行全站 sweep**（除非審閱者明說）：

| 審閱改法 | 全庫現況 | 判斷 |
|---|---|---|
| 「之所有」→「的所有」 | 仍有 16 檔 19 處 | 局部潤飾 |
| 「遵從其 CPS」→「遵從其憑證實務作業基準（CPS）」 | 中文側裸寫 CPS 仍有 8 檔 10 處 | 局部潤飾 |
| `delegate`（動作）：「委派」／「委任」→「委託」（§3.2.2.4.7、附錄 B） | 「委託」全庫已 10 處／6 檔；「委任」40 處多為固定詞「受委任第三方（Delegated Third Party）」；「委派」剩 3 處（§1.3.2 一處、DNSSEC Delegation Signer、ICANN delegated gTLD） | 一般 delegate 動作傾向「委託」；**「受委任第三方」為定版不動**；其餘依語境 |
| 「該經授權網域名稱（ADN）」刪「該」 | 同節內仍有保留「該」者 | 依語境，無規則 |

### 4.3 使用者面向用詞

| 用 | 不用 |
|---|---|
| 翻譯 | 中譯 |
| 章節細項 | 條款 |
| 本翻譯為非官方翻譯，發生爭議時以 CA/Browser Forum 英文原文為準 | 本中譯為非官方… |

免責文字**逐字硬編碼**於 `src/components/SiteFooter.astro`（每頁頁尾），**不可改寫**。
（原本另有一份硬編碼在引用卡 `CitationCard.astro` 的輸出格式中；「複製引用」功能已於 2026-09-19 廢除，
該元件連同 `src/lib/citation.ts` 的 `buildCitation()` 一併移除。）

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

**字母（`a.` `b.`）／羅馬數字（`i.` `ii.` `iii.`）子清單**：直接照 BR.md 的 Pandoc 寫法寫即可，`scripts/remark-fancy-lists.mjs` 會在 build 時重建成 `<ol type="a">` / `<ol type="i">`（對齊 cabforum.org）。規則：

- 一律從 `a.` 或 `i.` 起算；巢狀關係由標記類型推斷（字母為上層、其後羅馬數字為其子層，最深兩層）。
- **同一份清單的所有項目要連續寫在同一個語言區塊內**——英文 a/b/c/d 全放進同一個 `> ` blockquote，中文 a/b/c/d 全放進緊接的段落。**不要**逐項交錯（EN-a, CN-a, EN-b, CN-b…），否則同語言的項目不相鄰，plugin 會拆成多個 `<ol start=N>` 碎片。歷史上 §3.2.2.3／§3.2.2.5.1／§3.2.2.9 曾因此 bug 修補過。

不要把英文與中文逐項交錯（同表格規則）。

### 6.1 長清單項的區塊級交錯：英文 blockquote 必須縮排

上面禁止的是**逐 bullet 交錯**（短項目排在同一份 flat 清單裡）。但有些清單項本身是
一整個區塊——底下帶自己的段落、子清單、程式碼區塊（如附錄 B 的 `（a）`／`（b）`）——
這種情形仍可維持「該項英文 → 該項中文」的區塊級交錯，方便對照。

**但英文 blockquote 一定要縮排到該清單項的內容欄，不可寫在第 0 欄。**
CommonMark 規定第 0 欄的 blockquote 會把整個上層清單關掉，其後的
`   2. …`（3 格）就變成**新的頂層清單**，於是該項的縮排少一層：

```markdown
2. CA **應（MUST）**使用下列至少一種方法…：
   1. **（a）** …
      - **（i）** …

   >    2. **(b)** The CA MAY verify …    ← 縮排 3 格：留在上層清單項內 ✅
   >       - **(i)** …

   2. **（b）** …                          ← 正確落在第 2 層
      - **（i）** …
```

若上面那段 blockquote 寫成 `> 2. **(b)** …`（第 0 欄），`（b）` 會掉到第 1 層、
與 `（a）` 不同層。附錄 B 曾如此，2026-09-06 修正。

> 辨識法：畫面上同一組的 `（a）`／`（b）` 縮排不一樣 → 先看兩者之間的英文
> blockquote 是不是寫在第 0 欄，或直接跑 `python scripts/lint_list_nesting.py`。

### 6.2 上游把子項寫在第 0 欄時：英文照抄，中文縮排成巢狀

BR.md 偶爾會把語意上的子條件寫在第 0 欄，導致 CommonMark／Pandoc 把它解讀成
「中斷項目清單、另起一個編號清單」，渲染成並列而非巢狀。實例（§4.2.2.1.2，v2.3.0）：

```markdown
- For certificate requests made using the ACME protocol, … all of the following:
1. The CA maintains an internal, auditable mapping …      ← 第 0 欄，語意上是子條件
2. The CA has cryptographically or administratively verified …
3. The CA retains audit logs …
- If the CA supports domain validation methods …
```

**處理原則（2026-09-10 定案）**：

- **英文 blockquote 逐字照抄，連縮排都不要動**——它必須與 BR.md 逐行相同，
  才通得過「英文引用側機械核對」。渲染成 `ul → ol → ul` 三個並列清單是預期結果，
  cabforum.org（Pandoc）呈現的也一樣。
- **中文縮排成正確的巢狀**（子項縮 2 格對齊 `- ` 的內容欄）。
  讀者理解優先，中英兩側的清單結構因此**刻意不一致**。

> 這是 §1「中英結構對稱」的**唯一例外**，且僅適用於「上游 markdown 明顯寫錯層級」的情形。
> 一般情況仍須兩側結構一致。遇到時在對照檔記一筆，讓審閱者知道差異是刻意的。

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
- `pending-review` → **譯完但還沒人工審**（站上顯示紫色「待審閱」徽章）。
  2026-09-08 為 v2.3.0 升版新增；**不列入 `lint_version_consistency.py` 的
  `PUBLISHABLE_STATUS`，會擋 push**。
- `translated` → 譯者本人或他人通讀過，視為可用
- `reviewed` → 至少兩人交叉 review 完成（含術語一致性、規範性語義正確性）
- `outdated` → 上游 Ballot 已改動此節但譯稿尚未跟上

目錄頁 `/server-cert-br/table-of-contents/` 會自動統計各狀態數量。

### 8.1 升版重譯的 `translator` 欄

重譯期間分兩階段寫，**不要保留舊的初譯／潤稿／審閱鏈**：

| 階段 | `status` | `translator` |
|---|---|---|
| 重譯完成、待人工審 | `pending-review` | `Claude (Opus)` |
| 人工審閱完成 | `translated` | `Claude (Opus) + LiNnnYc 審閱` |
| 審閱前經另一個模型潤稿 | `translated` | `Claude (Opus) + ChatGPT (Instant) 潤稿 + LiNnnYc 審閱` |

`last_updated` 在第二階段改為**實際審閱日**（可能與重譯日不同天）。

審閱者若在送審前另用其他模型潤稿，就把該階段插在鏈中間（第三列）——
這是全站既有寫法，第 7～9 章與附錄多數檔案都是這個形式。**不要自行填寫潤稿階段**，
由審閱者補；重譯時一律只寫 `Claude (Opus)`。

> ⚠️ 新增含連字號的 `status` 值時，先 `grep -rn 'status:' scripts/*.py` 掃一遍——
> `\w+` 不吃連字號，會安靜截斷；`diff_br_versions.py` 甚至會把截斷結果**寫回檔案**
> （`pending-review` 曾被寫成 `outdated-review`）。兩支腳本已改 `[\w-]+`。

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

1. 更新 `upstream/BR.md` 為新版本原文（從 [`cabforum/servercert`](https://github.com/cabforum/servercert) 抓 main 分支）。
2. 跑 **`scripts/diff_br_versions.py`** 看哪些章節變動（自動取 `BR_archive/` 的封存版或 `br-v*` tag 當基準）。
3. 把改動的章節 `status` 改為 `outdated`，重新翻譯後再升回 `translated`。
4. ~~更新 `src/config/site.ts` 的 `upstream.version` 與 `lastSyncedAt`。~~
   → 改為在 **`src/config/br-versions.ts` 最上面加一列**（`date` 抄自新版 BR.md 標頭的
   `date:`）；`site.ts` 已改為自動推導，不再手動維護。舊版那列補上 `gitTag` 與 `archive`。
   完整流程見 `RUNBOOK.md` §2.4。
5. 補 §1.2.1 新增的 Ballot 列、§1.2.2 新增的合規日期列。
6. 全站 `last_updated` 仍維持各檔自己的最後潤稿日期，**不要全檔批量改**。

---

## 11. 工具腳本參考

常駐 remark／rehype plugins（`astro.config.mjs` 掛載，每次 build 自動生效）：

- `scripts/remark-code-figure.mjs` — 為 code block 加語言標籤（複製按鈕已於 2026-09-19 廢除）
- `scripts/remark-table-nowrap.mjs` — 表格原子 token（短 token、長的純 ASCII 識別碼／OID、章節參照）nowrap、整欄收緊（col-shrink）
- `scripts/remark-fancy-lists.mjs` — 字母（`a.`）／羅馬數字（`i.`）子清單重建成 `<ol type>`（見 §6）
- `scripts/rehype-table-caption.mjs` — 把表格上方 `Table:`／`表：` 段落轉成表格底端 `<caption>`，並把每個 `<table>` 包進 `.table-wrap`（見 §2.2）
- `scripts/rehype-footnotes.mjs` — 註腳 id 加章節前綴、標題改中文「註腳」、標記英文側引用（見 §13）
- `scripts/rehype-table-indent.mjs` — 表格儲存格前導 U+2007 縮排改成 cell padding（見 §2.3）
- `scripts/rehype-section-links.mjs` — 章節交叉參照改指向本站全文頁：`#7121-…` → `/server-cert-br/#7121-…`。**譯稿維持原文的錨點寫法**（好與 BR.md 逐字對照），錨點名與 cabforum.org 相同，網域對調即可落到同一節。以「各檔 `original_url` fragment」為白名單，註腳的 `#fn-…` 不受影響。⚠️ 之後若替 `astro.config.mjs` 設了 `base`，plugin 內的 `FULL_TEXT_PATH` 要一併加前綴

> ⚠️ **改 plugin 後要清 content layer 快取**：Astro 把每個章節檔的 render 結果存在 `node_modules/.astro/data-store.json`（另有 `.astro/data-store.json`），快取只看 markdown 內容與 `astro.config.mjs`，**不看 plugin 檔本身**。只改 `scripts/*.mjs` 而不動 config 的話，`npm run build` 會沿用舊 HTML、看起來像改動沒生效。刪掉這兩個檔再 build 即可。

校驗 lint（手動執行，`python scripts/<name>.py`）：

- `scripts/lint_rfc2119.py` — RFC 2119 加粗對照：英文 blockquote 大寫關鍵字 vs 中文 `（關鍵字）` 括註（見 §3.7）；另含 bare 粗體與畸形括註檢查
- `scripts/lint_term_consistency.py` — 譯名一致性：以 §1.6.1/§1.6.2 定版掃 chapter ≥ 3 的 `變體（English）` 分歧
- `scripts/lint_version_consistency.py` — **發布前把關**：全庫 `original_version` 是否一致、是否等於 `br-versions.ts` 宣告的發布版、是否還有 `draft`／`outdated`、`upstream/BR.md` 是否不低於發布版（上游較新只提示，較舊則報錯）。升版做到一半必然混版，故不擋 build／commit，只由 `.githooks/pre-push` 在 `git push` 前擋（安裝：`git config core.hooksPath .githooks`）
- `scripts/lint_table_indent.py` — 表格欄位階層縮排檢查：抓「U+2007 混半形空白」與「中英表層級不一致」（見 §2.3）
- `scripts/lint_list_nesting.py` — 巢狀清單掉層檢查：抓「縮排清單項前面隔著第 0 欄 blockquote」導致 render 少一層縮排（見 §6.1）。中英兩側各自判定；只在該項確實有上層清單項時才報，故 `  a.` `  b.` 這種前面只有散文引言、縮排純屬排版的頂層清單不會誤報。純掃 markdown，不需先 build
- `scripts/lint_translation_style.py` — 翻譯風格 lint（審閱加速器 Phase A）：以 §1.6/glossary/CURATED 為基準掃 chapter ≥ 4 的譯名分歧與機翻 artifact；報告寫 `web-spec-doc/翻譯工作區/風格審查_PhaseA報告.md`。逐節語意審查（Phase B）由 Claude 對照英文執行，產出 `PhaseB_ch<N>_worklist.md`

- `scripts/diff_br_versions.py` — 上游兩版 BR.md 的逐節比對：列出內容變動／新增／刪除各幾節並對應到本站檔名。舊版原文自動取自 `upstream/BR_archive/BR-v*.md`（升版前封存，檔名帶版本號）或 `br-v*` git tag，兩者都不必手動保存。`--show-diff <節號>` 看單節差異，`--mark-outdated --write` 把變動章節標記為待重譯

一次性轉換腳本：

- `scripts/unify_headings.py` — 統一三波翻譯的標題格式為 Style A
- `scripts/split_to_collection.py` — 把潤稿主檔拆成單節 `.md`
- `scripts/interleave_wave1_paragraphs.py` — 把全 EN→全 CN 改為逐段交錯
- `scripts/preserve_table_indent.py` — 把 BR.md 表格儲存格前導空白轉成 U+2007 對齊縮排
- `scripts/add_en_to_definitions_1_6_1.py` — 從 BR.md 把 §1.6.1 定義改成 Style A（補英文原文）；BR 版本升級時若 §1.6.1 定義有增減，調整後可重跑（會重寫整個 `1-6-1.md`）
- `scripts/add_en_footnote_defs.py` — 把註腳補成中英對照：英文側引用改用 `<label>_en`、從 BR.md 補上英文定義（見 §13）。可重跑（已補過的會跳過）；BR 升版若註腳有增減可再跑一次。`--write` 才實際寫入；`--doc <路徑>` 產出「改註腳翻譯要動哪些檔」的審閱清單（含各副本位置與不一致警示），已產出 `web-spec-doc/翻譯工作區/註腳翻譯修改清單.md`。
- `scripts/restore_table_captions.py` — 把 BR.md 的 `Table:` caption（英文）與 git `69b7baf^` 的「表：」（中文）以「緊鄰表格上方」格式回填各章節檔，供 `rehype-table-caption.mjs` 轉 `<caption>`（見 §2.2）。以表格內容簽章比對、idempotent，BR 升版後可重跑；`--write` 才實際寫入。

不在 repo 中的 hot-fix 腳本（補英文表 blockquote 等）已在歷史 commit 訊息中說明做法，未來如需重做可參考 commit `54eee2b`、`2185aba`、本檔對應的整理 commit。

---

## 12. 為何不採 Pandoc（targeted-plugin 策略）

cabforum.org 用 Pandoc 渲染 BR 原文，並為此調整過 markdown 語法。本站**刻意不改用 Pandoc**，而是維持 Astro 的 remark/CommonMark 流程 + 針對性 plugin。決策理由：

1. **技術上沒有「Pandoc 模式」可切。** Astro content collection 一律走 unified/remark。要「用 Pandoc」只能：(a) 先用 Pandoc 把整份文件渲染成 HTML 再嵌入 → 會失去每節 frontmatter／模板、中英對照 toggle、引用卡、Pagefind 子章節命中、Shiki 高亮、`.clause-body` 樣式鉤子（大倒退）；或 (b) 保留 remark、針對每個 Pandoc 功能加 plugin → **這正是現行做法**。
2. **本站原始檔不是 Pandoc 文件。** `src/content/br/*.md` 是重構過的「每節一檔 + Style A 中英對照」自訂方言，與 Pandoc 的唯一接觸點是逐字複製 BR.md 的英文片段。
3. **實際缺口幾乎是零。** BR.md 用到的 Pandoc 專屬語法很少，且已全部覆蓋：

| Pandoc 構件 | BR.md 用量 | 本站對應 |
|---|---|---|
| fancy lists（`a.`／`i.`） | 55 | `remark-fancy-lists.mjs`（§6） |
| `Table:` caption | 41 | `rehype-table-caption.mjs` → 底端 `<caption>`（§2.2） |
| 表格儲存格縮排 | 多處 | `preserve_table_indent.py`（U+2007）+ `rehype-table-indent.mjs`（§2.3） |
| footnotes `[^x]` | 22 | `remark-gfm` + `rehype-footnotes.mjs`（§13） |
| pipe tables | 大量 | `remark-gfm` |
| grid tables `+---+` | 0 | — |
| definition lists（`: 釋義`） | 0 | — |
| attribute blocks `{.class}` `{#id}` | 0 | — |
| fenced div `:::` | 0 | — |

**結論**：「支援 Pandoc」在 remark 生態裡的正確翻譯，就是「針對用到的 Pandoc 功能加 plugin」——而這已是現行策略。撞到新的 Pandoc-ism 時，加一支對應 plugin 即可，不需整體改造。

**可選的中間路線（backlog，暫不做）**：Pandoc definition list（`<dl><dt><dd>`）語意上最適合 §1.6.1／glossary，無障礙性較佳，可用 `remark-definition-list`。但 §1.6.1 剛統一為 Style A、與全站一致，為語意再翻一次不划算；等 a11y 或術語表體驗有實際需求再評估。

---

## 13. 註腳（footnotes）

### 13.1 譯稿寫法（中英對照）

註腳比照 Style A 做中英對照：**英文側用 `<label>_en`、中文側用原 label**，兩份定義都放在該章節檔最下方，英文在上、中文在下：

```markdown
> | `extKeyUsage` | SHOULD[^eku_ca_en] | N | … |

| `extKeyUsage` | 宜（SHOULD）[^eku_ca] | N | … |

> [^eku_ca_en]: While [RFC 5280, Section 4.2.1.12](…) notes that…（照抄 BR.md）

[^eku_ca]: 雖然 RFC 5280 第 4.2.1.12 節指出…（中文譯文）
```

- **label 沿用原文的英文 label**（`eku_ca`、`name_constraints`…），不要改名或改成數字：拆檔後同一個 label 會出現在多個章節檔，靠 label 相同才能在全文頁合併成同一條註腳。英文那份固定加 `_en` 後綴。
- 英文定義寫成 `> ` blockquote 形式（與其他英文原文一致）。markdown 的註腳定義不論寫在哪都會被抽到註腳區，blockquote 只是原地留一個空框——由 `rehype-footnotes.mjs` 自動清掉。
- **每個引用該註腳的章節檔都要自帶中英兩份定義**（拆檔時由 `split_to_collection.py` 複製中文那份；英文那份由 `add_en_footnote_defs.py` 從 BR.md 補），否則該節單獨頁的註腳會變成純文字 `[^eku_ca]`。
- 同一 label 在不同章節檔的定義文字**必須完全一致**；全文頁合併時以首次出現者為準，內容不同會被吃掉。

### 13.2 呈現方式（`scripts/rehype-footnotes.mjs` + 全文頁合併）

| 位置 | 註腳出現在哪 | 中英 | 編號 | 錨點 |
|---|---|---|---|---|
| 單章節頁 `/server-cert-br/<slug>/` | 該節內文最下方，只含該節用到的註腳 | 英文條目（灰字）+ 中文條目並列 | 該節內 1、2…，中英兩條**共用**同一號（`<li value>`） | `#fn-<節slug>-<label>` ↔ `#fnref-<節slug>-<label>-<n>` |
| 全文頁 `/server-cert-br/` | **全文最下方**單一清單（比照 cabforum.org 原文） | 只有中文 | 全文首次出現順序 1…N | `#fn-<label>` ↔ 各節的 `#fnref-…` |

- 引用（上標數字）**帶底線**（比照 cabforum.org）：BR 內文本身就有 `2¹⁵⁹` 這類真正的指數，而註腳引用常緊接在數字後面（如 §7.1.4.2 的 `64`+註腳 → 「64¹」），沒有底線會被誤讀成指數。底線同時也是「可點」的提示。
- 引用（上標數字）點下去跳到對應註腳；註腳的回鏈跳回內文標記處。全文頁的回鏈以「§節號」列出所有引用該註腳的章節（同節多次引用時附上標 2、3…）。
- 英文條目與英文側引用在全文頁不出現（英文 blockquote 本來就隱藏），其回鏈另有 `.fn-backref-en` 供一併隱藏，避免點了跳到看不見的位置。
- 匯出腳本 `export_chapters_html.mjs` 會一併帶出全文頁的註腳區，並濾掉回鏈落在匯出範圍外的註腳（保留原編號，以 `<li value>` 固定）。（`<dl><dt><dd>`）語意上最適合 §1.6.1／glossary，無障礙性較佳，可用 `remark-definition-list`。但 §1.6.1 剛統一為 Style A、與全站一致，為語意再翻一次不划算；等 a11y 或術語表體驗有實際需求再評估。
