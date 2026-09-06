> **About the Baseline Requirements**

> The Baseline Requirements for the Issuance and Management of Publicly-Trusted Certificates describe a subset of the requirements that a certification authority must meet in order to issue digital certificates for SSL/TLS servers to be publicly trusted by browsers. Except where explicitly stated otherwise, the requirements apply only to events that occur on or after the requirement's effective date.

《公開信賴憑證之簽發及管理基本要求》（Baseline Requirements for the Issuance and Management of Publicly-Trusted Certificates）說明憑證機構（Certification Authority，CA）欲簽發受瀏覽器公開信賴之 SSL/TLS 伺服器數位憑證時，所必須符合的部分要求。除另有明文規定外，這些要求僅適用於該要求生效日當日或之後所發生之事件。

> The requirements do not address all of the issues relevant to the issuance and management of publicly-trusted certificates, and the CA/Browser Forum may update the requirements to address both existing and emerging threats to online security.

本要求規定並未涵蓋與公開信賴憑證之簽發及管理相關的所有議題；CA/Browser Forum 得不定期更新本要求規定，以因應現有及新興的網路安全（online security）威脅。

> The current version of the requirements only addresses certificates used for authenticating servers accessible through the Internet. Similar requirements for code signing, S/MIME, time-stamping, VoIP, IM, Web services, etc. may be covered in future versions.

現行版本的要求規定僅涵蓋用於鑑別可透過網際網路存取之伺服器的憑證。程式碼簽章（code signing）、S/MIME、時間戳記（time-stamping）、網路電話（VoIP）、即時通訊（IM）、Web 服務等類似要求，可能於未來版本中納入。

> The requirements also do not address the issuance, or management of certificates by enterprises that operate their own Public Key Infrastructure for internal purposes only and where the root certificate is not distributed by browsers.

本要求規定亦不涵蓋下列情形之憑證簽發或管理：企業純為內部用途自行維運公開金鑰基礎建設（Public Key Infrastructure，PKI），且其根憑證並未由瀏覽器配發。

> **Vetting of Certificate Applicants pursuant to the Baseline Requirements**

> The Baseline Requirements require CAs to verify all contents of a certificate, except information contained in the organizational unit field, to a minimum degree of diligence. For certificates issued to domain names only, the CA confirms that, as of the date the Certificate was issued, the applicant either is the registrant of the domain name or has control over the FQDN. This can be done through an automated, challenge-response email. A similar requirement applies for verifying the assignment or control of IP addresses. Certification Authorities issuing organizationally-vetted certificates (certificates with subject identity information) verify the name and address of the applicant using reliable information sources, such as a government agency in the jurisdiction of the Applicant's legal creation, existence, or recognition or a reliable third party database. The CA also confirms the authenticity of the certificate request through some means of reliable communication with the organization (i.e. they verify that the certificate requester is an authorized employee/agent within the subscribing organization). For certificates issued to individuals, the CA verifies the individual's identity using a government-issued photo ID that is inspected for indication of alteration or falsification.

《基本要求》要求 CA 以最低程度之審慎注意（minimum degree of diligence）查核憑證之所有內容，但組織單位（organizational unit）欄位所含資訊除外。對於僅簽發予網域名稱之憑證，CA 應確認截至該憑證簽發日為止，申請者（Applicant）為該網域名稱之註冊人（Registrant），或對該 FQDN 具有控管權；此項確認得以自動化之挑戰／回應（challenge-response）電子郵件完成。驗證 IP 位址之指派或控管權時亦適用類似要求。簽發經組織查核之憑證（即載有主體識別資訊之憑證）的 CA，會運用可靠資訊來源查核申請者之名稱與地址——例如申請者依法設立、存續或獲得認可之管轄區內的政府機關，或可靠之第三方資料庫。CA 亦會透過與該組織之某種可靠通訊方式，確認該憑證申請之真實性（亦即查核提出憑證申請者確為該用戶組織內獲授權之員工／代理人）。對於簽發予個人之憑證，CA 則以政府核發之附相片身分證件查核該個人之身分，並檢視該證件有無遭變造或偽造之跡象。

> Since 2012, the Baseline Requirements have been incorporated by reference into, and form part of, the CA/Browser Forum's [Extended Validation Guidelines](https://cabforum.org/working-groups/server/extended-validation/).

自 2012 年起，《基本要求》已以引用方式納入 CA/Browser Forum 的 [EV 指引（Extended Validation Guidelines）](https://cabforum.org/working-groups/server/extended-validation/)，並構成其一部分。
