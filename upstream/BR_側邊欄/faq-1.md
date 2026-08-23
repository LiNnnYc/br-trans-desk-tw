---
aliases:
- /faq-about-the-baseline-requirements/
date: 2013-09-04 03:33:24
title: 基準要求常見問答 (FAQ)
---

# 基準要求常見問答 {#Frequently_Asked_Questions_about_the_Baseline_Requirements}

**1. 何謂 CA/Browser Forum 基準要求（BR）？其緣起為何？**

網際網路廣泛用於線上交易、確保交易安全之需求、憑證機構（Certification Authority, CA）數量激增，以及各瀏覽器對於是否將 CA 內嵌為軟體信任錨點（trust anchor）所採用的標準不一，種種因素驅使業界迫切需要一套 SSL 業務運作及身分驗證程序的標準基準，以確保此信任模型能持續成功並具可行性。歷經數年，CA 與瀏覽器業者共同致力於為 CA 管理及 SSL 憑證核發制定更嚴格且更一致的標準。基準要求 1.0 版於 2012 年 7 月 1 日生效，旨在強化身分驗證程序及 SSL 憑證核發作業之安全性。其內容涵蓋身分審查、憑證內容與格式、CA 安全性、憑證撤銷機制、演算法與金鑰長度之使用、稽核要求、責任歸屬、隱私與保密，以及授權之委任。

**2. 基準要求規範了哪些內容？**

基準要求涵蓋之作業實務範例包括：符合 CA/B 基準要求之網域驗證型（Domain Validated, DV）與組織驗證型（Organizational Validated, OV）憑證之區別，此作法與延伸驗證（Extended Validation, EV）憑證類似；於 2012 年 7 月 1 日後核發之憑證，有效期限不得超過 60 個月，於 2015 年 4 月 1 日後核發者，則不得超過 39 個月；主體別名（Subject Alternative Name, SAN）擴充欄位之每一筆項目，皆須載明屬於該組織之伺服器的完全合格網域名稱（FQDN）或 IP 位址；SAN 或通用名稱（Common Name, CN）欄位含有保留 IP 位址（Reserved IP Address）或內部伺服器名稱（Internal Server Name）之憑證正逐步淘汰，此類憑證於 2016 年 10 月後將不再有效。

如欲檢視基準要求全文，可點選上方之基準要求連結，或此連結：[CA/B Forum 基準要求][1]。

**3. 為何基準要求十分重要？**

基準要求對 CA 服務提供者與消費者而言皆十分重要。CA 服務提供者能清楚了解其提供 SSL 及身分驗證服務時須遵循之標準；稽核人員則據此標準衡量該 CA 是否符合業界最低要求。稽核結果顯示符合基準要求之 CA，其憑證遭主要瀏覽器拒絕之風險較低（即其憑證能獲得更廣泛之接受）。消費者於使用採行 CA/B 基準要求之 CA 所提供之 SSL 憑證時，亦能對安全程度有一定之保障。基準要求將促使網站更頻繁採用具更強加密之 SSL 以確保安全，並減少與憑證相關之漏洞。

**4. 基準要求發布後，是否代表所有 CA 皆採相同之安全標準？**

基準要求為 CA 於 SSL 作業及業務流程方面提供最低標準；然而，業界仍鼓勵 CA 超越此基準標準，採行更嚴謹之身分驗證作業與更高標準，以強化組織與使用者之安全性。簡言之，於網路上進行分享及交易之使用者及消費者，將獲得更佳之保障，並能更清楚了解所造訪網站之信任等級。

**5. 我該如何得知某張憑證是否符合基準要求？**

基準要求第 9.3.4 節規定，CA 須揭露其所核發、含有其指定基準要求政策識別碼（policy identifier）之憑證，係依本要求進行管理。CA 須於其憑證政策（Certificate Policy）或憑證實務作業聲明（Certification Practices Statement）中載明其遵循基準要求之聲明，且各主要稽核機制之稽核標準，皆會檢核該 CA 是否確依其所揭露之作業方式執行。CA 可運用 CA/Browser Forum 之憑證政策物件識別碼（Certificate Policy Object Identifier, CP OID），標示依基準要求核發之憑證。CP OID 通常可於「詳細資料」（Details）分頁中查看，作法為點選憑證鎖頭圖示並選擇「檢視憑證」（View certificates）連結，再向下捲動至「憑證政策」（Certificate Policies）區塊即可查看。CP OID 於憑證中之顯示方式，可參考以下 Internet Explorer 之範例畫面。

**6. 我該如何得知特定 CA 之基準要求 CP OID？**

CA 可採用基準要求所提供之下列通用 CP OID 之一：

- 2.23.140.1.2   （憑證依基準要求核發）
- 2.23.140.1.2.1 （符合基準要求──未主張任何實體身分）
- 2.23.140.1.2.2 （符合基準要求──已主張實體身分）

僅有符合基準要求之 CA 所核發之憑證，方可顯示上述 CA/Browser Forum OID，惟大多數商業 CA 皆維護其自有之 CP OID。若某 CA 為主張其符合 BR 而建立自有之專屬 CP OID，該 CA 將於其 CP 或 CPS 中列出；此外，CA/Browser Forum 亦於其[物件登錄庫（Object Registry）][2]中維護此類 OID 之清單。

[1]: /working-groups/server/baseline-requirements/ "Baseline Requirements"
[2]: /resources/object-registry/ "Object Registry"
