> **1. What are the CA/Browser Forum Baseline Requirements (BR) and how did they come about?**

**1. 什麼是 CA/Browser Forum《基本要求》（Baseline Requirements，BR）？它是如何形成的？**

> The widespread use of the Internet for online transactions, the need to secure them, the proliferation of Certification Authorities (CA), and the varying criteria used by browsers to determine whether to embed CAs as trust anchors in software has driven the critical need for a standard baseline on SSL business operations and authentication processes to ensure the continued success and viability of the trust model. During the course of several years, CAs and Browsers worked to develop stricter and more uniform standards for the management of CAs and issuance of SSL Certificates. Baseline Requirements 1.0 went into effect on July 1, 2012. They were designed to strengthen the security around authentication processes and SSL issuance operations. The requirements include identity vetting, certificate content and profiles, CA security, certificate revocation mechanisms, use of algorithms and key sizes, audit requirements, liability, privacy and confidentiality, and delegation of authority.

隨著網際網路廣泛應用於線上交易，確保交易安全的需求日益增加，而憑證機構（CA）數量的快速增加，以及各瀏覽器用以決定是否將 CA 植入軟體信賴根源（Trust Anchor）的判斷標準不一，使得制定「SSL 業務作業與主體鑑別流程的共同基本標準」成為迫切需求，以確保此一信任模型得以持續成功運作與維持可行性。歷經數年，CA 與瀏覽器業者共同發展出一套更為嚴格且一致的標準，以規範 CA 之管理及 SSL 憑證之簽發。《基本要求》1.0 版於 2012 年 7 月 1 日起生效，其設計目的在於強化主體鑑別流程與 SSL 簽發作業的安全性。其要求規定涵蓋身分驗證、憑證內容與剖繪、CA 的安全防護、憑證廢止機制、演算法與金鑰長度之使用、稽核要求、業務責任、隱私與保密，以及職權之委託。

> **2. What are in the Baseline Requirements?**

**2.《基本要求》包含哪些內容？**

> Examples of practices covered in the Baseline Requirements include:
>
> - Differentiation between Domain Validated (DV) and Organizational Validated (OV) certificates that are compliant to the CA/B Baseline Requirements, a practice similar to Extended Validation (EV) certificates.
> - Validity period for certificates issued after July 1, 2012 must not exceed 60 months and issued after April 1, 2015 must not exceed 39 months.
> - Each entry for Subject Alternative Name (SAN) extension must contain a Fully-Qualified Domain Name (FQDN) or the IP address of a server that belongs to the organization.
> - Certificates with a SAN or Common Name (CN) field containing a Reserved IP Address or Internal Server Name are being phased out and such certificates will no longer be valid after October 2016.

《基本要求》所涵蓋之作業實務，舉例如下：

- 區隔符合 CA/B《基本要求》規定的網域驗證型（Domain Validated，DV）憑證與組織驗證型（Organization Validated，OV）憑證之辨識，作法類似延伸驗證型（Extended Validation，EV）憑證。
- 2012 年 7 月 1 日後簽發的憑證，其有效期不得超過 60 個月；2015 年 4 月 1 日後簽發的憑證不得超過 39 個月。
- 主體別名（Subject Alternative Name，SAN）擴充欄位的每一項目，均須包含屬於該組織伺服器的完全吻合網域名稱（FQDN）或 IP 位址。
- SAN 或通用名稱（Common Name，CN）欄位包含保留 IP 位址（Reserved IP Address）或內部伺服器名稱（Internal Server Name）之憑證正逐步淘汰，此類憑證於 2016 年 10 月後將不再有效。

**編按**：上列第 2、4 點為 2013 年撰寫本頁時之規定，**現行《基本要求》規定已大幅變更**。現行憑證有效期規定於[第 6.3.2 節](#632-certificate-operational-periods-and-key-pair-usage-periods)。內部名稱（Internal Name）與保留 IP 位址的淘汰期限亦早已屆至，現行規定見[第 7.1.4.2 節](#7142-subject-attribute-encoding)。引用時請以現行《基本要求》規定為準。

> The Baseline Requirements can be reviewed by clicking the Baseline Requirements link above, or the one here: [CA/B Forum Baseline Requirements](https://cabforum.org/working-groups/server/baseline-requirements/).

《基本要求》全文可透過上方的 Baseline Requirements 連結查閱，或點選此處：[CA/B Forum Baseline Requirements](https://cabforum.org/working-groups/server/baseline-requirements/)。本站亦提供[《基本要求》全文繁體中文翻譯](/server-cert-br/)。

> **3. Why are the Baseline Requirements important?**

**3. 為什麼《基本要求》很重要？**

> Baseline Requirements are important to both CA service providers and consumers. CA service providers will have a clear understanding of the standards that they need to adhere to when providing SSL and authentication services. In turn, auditors will use the criteria to measure whether the CA meets industry minimum expectations. A CA with an audit indicating that it is compliant with the Baseline Requirements will have less risk of being rejected by the leading browsers (i.e. their certificates will be more widely accepted). Consumers will be assured of a certain level of security when they encounter SSL certificates offered by CAs that have adopted the CA/B Baseline Requirements. The Baseline Requirements will lead to more frequent use of SSL to secure websites with stronger encryption and fewer certificate-related vulnerabilities.

《基本要求》對 CA 服務供應商與消費者雙方都很重要。CA 服務供應商可清楚理解其提供 SSL 與主體鑑別服務時所須遵循之標準。相對地，稽核業者則以這些標準評估該 CA 是否符合業界最低預期。稽核結果顯示遵循《基本要求》規定之 CA，被主流瀏覽器拒絕的風險也較低（亦即其憑證會被更廣泛地接受）。消費者若遇到採行 CA/B《基本要求》標準之 CA 所提供的 SSL 憑證時，亦可獲得一定程度的安全保障。《基本要求》將促使 SSL 更普遍地用於保護網站，並帶來更強的加密與更少的憑證相關弱點。

> **4. With the issuance of Baseline Requirements, does it mean that all CAs have the same security standards?**

**4. 《基本要求》發布後，是否代表所有 CA 都具有相同的安全標準？**

> Baseline Requirements provide a minimal standard for CAs with regards to their SSL operations and business processes. However, CAs are encouraged to go beyond the baseline standards to provide stringent authentication practices and high standards which makes for stronger security for organizations and users. In summary, users and consumers sharing and transacting on the Internet will have better protection and visibility into the trust level of the websites they visit.

《基本要求》針對 CA 的 SSL 作業與業務流程提供一套**最低**標準。然而，我們鼓勵 CA 超越此基本標準，採行更嚴格的主體鑑別實務與更高的標準，為組織與使用者帶來更強的安全性。總而言之，在網際網路上分享資訊與進行交易的使用者及消費者，將獲得更好的保護，也更清楚明瞭其所造訪網站的信任程度。

> **5. How can I tell if a certificate is compliant to the Baseline Requirements?**

**5. 我如何判斷一張憑證是否遵循《基本要求》？**

> Section 9.3.4 of the Baseline Requirements states that the CA must disclose that Certificates it issues containing its specified Baseline Requirements policy identifier are managed in accordance with these Requirements. The CA must include a statement in its Certificate Policy or Certification Practices Statements that it complies with Baseline Requirements, and the audit criteria of all major audit schemes check whether the CA performs in accordance with such disclosed practices. The CA can identify those certificates issued in compliance with the Baseline Requirements by using the CA/Browser Forum certificate policy object identifier (CP OID). The CP OID is typically in the Details tab and one can get there by clicking on the padlock and "View certificates" link, then scroll down to Certificate Policies. CP OIDs are displayed in the certificate similar to the example below from Internet Explorer.

《基本要求》第 9.3.4 節載明，CA 須揭露其所簽發、且包含《基本要求》所指定之政策識別碼（policy identifier）的憑證，均依本文件要求規定管理。CA 須於其憑證政策（CP）或憑證實務作業基準（CPS）中聲明其遵循《基本要求》規定；此外，各主要稽核架構的稽核準則均會查核該 CA 是否依其所揭露之實務作業執行。CA 可使用 CA/Browser Forum 提供的憑證政策物件識別碼（CP OID），標示其依《基本要求》簽發之憑證。CP OID 通常位於憑證的「詳細資料」分頁，可點選網址列的鎖頭圖示與「檢視憑證」連結後，向下捲動至「憑證原則（Certificate Policies）」查看。CP OID 在憑證中的顯示方式，與下方取自 Internet Explorer 的範例類似。

**編按**：本段所引之**第 9.3.4 節在現行《基本要求》（v2.2.7）中已不存在**（第 9.3 節僅有 9.3.1–9.3.3）；保留憑證政策識別碼之規定見[第 7.1.6.1 節](#7161-reserved-certificate-policy-identifiers)。原文所稱「下方取自 Internet Explorer 的範例」為原頁面的圖片，本翻譯未收錄；Internet Explorer 亦已終止支援，實際操作請參考所使用瀏覽器的憑證檢視介面。

> **6. How do I know the Baseline Requirements CP OID for a particular CA?**

**6. 我如何得知特定 CA 所用的《基本要求》CP OID？**

> A CA can use one of the generic CP OIDs provided by the Baseline Requirements:
>
> - 2.23.140.1.2   (Certificate issued in compliance with the Baseline Requirements)
> - 2.23.140.1.2.1 (Compliant with Baseline Requirements – No entity identity asserted)
> - 2.23.140.1.2.2 (Compliant with Baseline Requirements – Entity identity asserted)

CA 得使用《基本要求》所提供的通用 CP OID 之一：

- 2.23.140.1.2　　（遵循《基本要求》所簽發之憑證）
- 2.23.140.1.2.1（遵循《基本要求》——未表明個體身分）
- 2.23.140.1.2.2（遵循《基本要求》——已表明個體身分）

**編按**：現行《基本要求》另定有 **2.23.140.1.2.3**（個人驗證，individual-validated）；完整清單見[第 7.1.6.1 節](#7161-reserved-certificate-policy-identifiers)。

> Only certificates from CAs that comply with the Baseline Requirements can display the CA/Browser Forum OIDs above, but most commercial CAs maintain their own CP OIDs. If a CA has created its own proprietary CP OIDs when to assert compliance with the BRs, they will list them in their CP or CPS, or the CA/Browser Forum also maintains a list of these OIDs here, in the CA/Browser Forum's own [Object Registry](https://cabforum.org/resources/object-registry/).

只有遵循《基本要求》的 CA 所簽發之憑證，才能標示上述 CA/Browser Forum OID；然而，多數商業 CA 均有其自訂的 CP OID。若 CA 在宣告其遵循《基本要求》規範時，已建立自己的 CP OID，則會將這些 OID 同步列於其 CP 或 CPS 之中；CA/Browser Forum 亦於其[物件登錄表（Object Registry）](https://cabforum.org/resources/object-registry/)中維護此類 OID 的清單。
