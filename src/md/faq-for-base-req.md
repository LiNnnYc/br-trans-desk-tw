> **1. What are the CA/Browser Forum Baseline Requirements (BR) and how did they come about?**

**1. 什麼是 CA/Browser Forum《基本要求》（Baseline Requirements，BR）？它是如何形成的？**

> The widespread use of the Internet for online transactions, the need to secure them, the proliferation of Certification Authorities (CA), and the varying criteria used by browsers to determine whether to embed CAs as trust anchors in software has driven the critical need for a standard baseline on SSL business operations and authentication processes to ensure the continued success and viability of the trust model. During the course of several years, CAs and Browsers worked to develop stricter and more uniform standards for the management of CAs and issuance of SSL Certificates. Baseline Requirements 1.0 went into effect on July 1, 2012. They were designed to strengthen the security around authentication processes and SSL issuance operations. The requirements include identity vetting, certificate content and profiles, CA security, certificate revocation mechanisms, use of algorithms and key sizes, audit requirements, liability, privacy and confidentiality, and delegation of authority.

網際網路廣泛用於線上交易、確保交易安全的需求、憑證機構（Certification Authority，CA）數量的增長，以及各瀏覽器在判斷是否將 CA 以信賴根源（Trust Anchor）形式內嵌於軟體時所採用的標準不一——這些因素使得「為 SSL 業務作業與鑑別流程訂定一套標準基準」成為維繫信任模型能否持續運作的關鍵需求。歷經數年，CA 與瀏覽器業者共同制定出更嚴格且更一致的標準，用於 CA 之管理與 SSL 憑證之簽發。《基本要求》1.0 版於 2012 年 7 月 1 日生效，其設計目的在於強化鑑別流程與 SSL 簽發作業的安全性。其要求規定涵蓋身分查核、憑證內容與剖繪、CA 安全、憑證廢止機制、演算法與金鑰長度之使用、稽核要求、責任、隱私與保密，以及職權之委任。

> **2. What are in the Baseline Requirements?**

**2.《基本要求》包含哪些內容？**

> Examples of practices covered in the Baseline Requirements include:
>
> - Differentiation between Domain Validated (DV) and Organizational Validated (OV) certificates that are compliant to the CA/B Baseline Requirements, a practice similar to Extended Validation (EV) certificates.
> - Validity period for certificates issued after July 1, 2012 must not exceed 60 months and issued after April 1, 2015 must not exceed 39 months.
> - Each entry for Subject Alternative Name (SAN) extension must contain a Fully-Qualified Domain Name (FQDN) or the IP address of a server that belongs to the organization.
> - Certificates with a SAN or Common Name (CN) field containing a Reserved IP Address or Internal Server Name are being phased out and such certificates will no longer be valid after October 2016.

《基本要求》所涵蓋之作業實務，舉例如下：

- 區分符合 CA/B《基本要求》之網域驗證（Domain Validated，DV）憑證與組織驗證（Organization Validated，OV）憑證，作法類似於延伸驗證（Extended Validation，EV）憑證。
- 2012 年 7 月 1 日後簽發之憑證，其有效期不得超過 60 個月；2015 年 4 月 1 日後簽發者不得超過 39 個月。
- 主體別名（Subject Alternative Name，SAN）擴充欄位之每一項目，均須包含屬於該組織之伺服器的完全吻合網域名稱（FQDN）或 IP 位址。
- SAN 或通用名稱（Common Name，CN）欄位含有保留 IP 位址（Reserved IP Address）或內部伺服器名稱（Internal Server Name）之憑證正逐步淘汰，此類憑證於 2016 年 10 月後將不再有效。

**編按**：上列第 2、4 點為 2013 年撰寫本頁時之規定，**現行《基本要求》已大幅變更**。憑證有效期現規定於[第 6.3.2 節](#632-certificate-operational-periods-and-key-pair-usage-periods)：2026-03-15 前簽發者不得超過 **398 日**、2026-03-15 起不得超過 **200 日**、2029-03-15 起不得超過 **47 日**。內部名稱（Internal Name）與保留 IP 位址之淘汰期限亦早已屆至，現行規定見[第 7.1.4.2 節](#7142-subject-attribute-encoding)。引用時請以《基本要求》本文為準。

> The Baseline Requirements can be reviewed by clicking the Baseline Requirements link above, or the one here: [CA/B Forum Baseline Requirements](https://cabforum.org/working-groups/server/baseline-requirements/).

《基本要求》全文可透過上方的 Baseline Requirements 連結查閱，或點選此處：[CA/B Forum Baseline Requirements](https://cabforum.org/working-groups/server/baseline-requirements/)。本站亦提供[《基本要求》全文繁體中文翻譯](/server-cert-br/)。

> **3. Why are the Baseline Requirements important?**

**3. 為什麼《基本要求》很重要？**

> Baseline Requirements are important to both CA service providers and consumers. CA service providers will have a clear understanding of the standards that they need to adhere to when providing SSL and authentication services. In turn, auditors will use the criteria to measure whether the CA meets industry minimum expectations. A CA with an audit indicating that it is compliant with the Baseline Requirements will have less risk of being rejected by the leading browsers (i.e. their certificates will be more widely accepted). Consumers will be assured of a certain level of security when they encounter SSL certificates offered by CAs that have adopted the CA/B Baseline Requirements. The Baseline Requirements will lead to more frequent use of SSL to secure websites with stronger encryption and fewer certificate-related vulnerabilities.

《基本要求》對 CA 服務提供者與消費者雙方都很重要。CA 服務提供者可清楚了解其提供 SSL 與鑑別服務時所須遵循的標準；稽核人員則以這些準則衡量該 CA 是否達到業界的最低期待。稽核結果顯示遵循《基本要求》之 CA，被主流瀏覽器拒絕的風險較低（亦即其憑證會被更廣泛地接受）。消費者遇到由已採行 CA/B《基本要求》之 CA 所提供的 SSL 憑證時，亦可獲得一定程度的安全保障。《基本要求》將促使 SSL 更普遍地用於保護網站，並帶來更強的加密與更少的憑證相關弱點。

> **4. With the issuance of Baseline Requirements, does it mean that all CAs have the same security standards?**

**4.《基本要求》發布後，是否代表所有 CA 都具有相同的安全標準？**

> Baseline Requirements provide a minimal standard for CAs with regards to their SSL operations and business processes. However, CAs are encouraged to go beyond the baseline standards to provide stringent authentication practices and high standards which makes for stronger security for organizations and users. In summary, users and consumers sharing and transacting on the Internet will have better protection and visibility into the trust level of the websites they visit.

《基本要求》就 CA 之 SSL 作業與業務流程提供一套**最低**標準。不過，我們鼓勵 CA 超越此基準標準，採行更嚴謹的鑑別實務與更高的標準，為組織與使用者帶來更強的安全性。總而言之，在網際網路上分享資訊與進行交易的使用者及消費者，將獲得更好的保護，也更能看清所造訪網站的信任程度。

> **5. How can I tell if a certificate is compliant to the Baseline Requirements?**

**5. 我如何判斷一張憑證是否遵循《基本要求》？**

> Section 9.3.4 of the Baseline Requirements states that the CA must disclose that Certificates it issues containing its specified Baseline Requirements policy identifier are managed in accordance with these Requirements. The CA must include a statement in its Certificate Policy or Certification Practices Statements that it complies with Baseline Requirements, and the audit criteria of all major audit schemes check whether the CA performs in accordance with such disclosed practices. The CA can identify those certificates issued in compliance with the Baseline Requirements by using the CA/Browser Forum certificate policy object identifier (CP OID). The CP OID is typically in the Details tab and one can get there by clicking on the padlock and "View certificates" link, then scroll down to Certificate Policies. CP OIDs are displayed in the certificate similar to the example below from Internet Explorer.

《基本要求》第 9.3.4 節載明，CA 須揭露其所簽發、含有該 CA 指定之《基本要求》政策識別碼的憑證，均依本要求規定管理。CA 須於其憑證政策（CP）或憑證實務作業基準（CPS）中載明其遵循《基本要求》，而各主要稽核制度的稽核準則會檢查該 CA 是否依其所揭露之實務作業執行。CA 可透過 CA/Browser Forum 的憑證政策物件識別碼（CP OID）標示哪些憑證係遵循《基本要求》所簽發。CP OID 通常位於憑證的「詳細資料」分頁，可點選網址列的鎖頭圖示與「檢視憑證」連結後，向下捲動至「憑證原則」查看。CP OID 在憑證中的顯示方式，與下方取自 Internet Explorer 的範例類似。

**編按**：本段所引之**第 9.3.4 節在現行《基本要求》（v2.2.7）中已不存在**（第 9.3 節僅有 9.3.1–9.3.3）；保留憑證政策識別碼之規定現見[第 7.1.6.1 節](#7161-reserved-certificate-policy-identifiers)。原文所稱「下方取自 Internet Explorer 的範例」為原頁面的圖片，本翻譯未收錄；Internet Explorer 亦已終止支援，實際操作請參考所使用瀏覽器的憑證檢視介面。

> **6. How do I know the Baseline Requirements CP OID for a particular CA?**

**6. 我如何得知特定 CA 的《基本要求》CP OID？**

> A CA can use one of the generic CP OIDs provided by the Baseline Requirements:
>
> - 2.23.140.1.2   (Certificate issued in compliance with the Baseline Requirements)
> - 2.23.140.1.2.1 (Compliant with Baseline Requirements – No entity identity asserted)
> - 2.23.140.1.2.2 (Compliant with Baseline Requirements – Entity identity asserted)

CA 得使用《基本要求》所提供的通用 CP OID 之一：

- 2.23.140.1.2　　（遵循《基本要求》所簽發之憑證）
- 2.23.140.1.2.1（遵循《基本要求》——未主張實體身分）
- 2.23.140.1.2.2（遵循《基本要求》——已主張實體身分）

**編按**：現行《基本要求》另定有 **2.23.140.1.2.3**（個人驗證，individual-validated）；完整清單見[第 7.1.6.1 節](#7161-reserved-certificate-policy-identifiers)。

> Only certificates from CAs that comply with the Baseline Requirements can display the CA/Browser Forum OIDs above, but most commercial CAs maintain their own CP OIDs. If a CA has created its own proprietary CP OIDs when to assert compliance with the BRs, they will list them in their CP or CPS, or the CA/Browser Forum also maintains a list of these OIDs here, in the CA/Browser Forum's own [Object Registry](https://cabforum.org/resources/object-registry/).

只有遵循《基本要求》之 CA 所簽發的憑證，才能標示上述 CA/Browser Forum OID；不過多數商業 CA 另有自訂的 CP OID。若某 CA 自行建立專屬 CP OID 以主張其遵循 BR，該 CA 會將這些 OID 列於其 CP 或 CPS 之中；CA/Browser Forum 亦於其[物件登錄表（Object Registry）](https://cabforum.org/resources/object-registry/)維護此類 OID 的清單。
