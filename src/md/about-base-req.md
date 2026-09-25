> **About the Baseline Requirements**

**關於《基本要求》**

> The Baseline Requirements for the Issuance and Management of Publicly-Trusted Certificates describe a subset of the requirements that a certification authority must meet in order to issue digital certificates for SSL/TLS servers to be publicly trusted by browsers. Except where explicitly stated otherwise, the requirements apply only to events that occur on or after the requirement's effective date.

《公開信賴憑證簽發與管理之基本要求》（Baseline Requirements for the Issuance and Management of Publicly-Trusted Certificates）描述憑證機構（Certification Authority，CA）簽發受瀏覽器公開信賴的 SSL/TLS 伺服器數位憑證時，所應符合之要求的一部分內容。除非另有明確說明，否則本文件要求規定僅適用於該要求生效日或之後發生的相關事件。

> The requirements do not address all of the issues relevant to the issuance and management of publicly-trusted certificates, and the CA/Browser Forum may update the requirements to address both existing and emerging threats to online security.

本文件並未涵蓋簽發與管理公開信賴憑證過程中所涉及的全部議題；CA/Browser Forum 得不定期更新本文件要求規定，以因應現有及新興的網路安全（online security）威脅。

> The current version of the requirements only addresses certificates used for authenticating servers accessible through the Internet. Similar requirements for code signing, S/MIME, time-stamping, VoIP, IM, Web services, etc. may be covered in future versions.

現行版本僅針對用於鑑別（authenticating）可透過網際網路（Internet）存取之伺服器的憑證（Certificates）。針對程式碼簽章（code signing）、S/MIME、時戳（time-stamping）、VoIP、IM、Web 服務（Web services）等類似要求，可能會在未來版本中涵蓋。

> The requirements also do not address the issuance, or management of certificates by enterprises that operate their own Public Key Infrastructure for internal purposes only and where the root certificate is not distributed by browsers.

本文件要求規定亦不涉及企業（enterprises）僅供內部用途（internal purposes）而自行營運的公開金鑰基礎建設（Public Key Infrastructure，PKI），及其所進行的憑證簽發或管理，且其根憑證未經瀏覽器配發。

> **Vetting of Certificate Applicants pursuant to the Baseline Requirements**

**依《基本要求》辦理憑證申請者之審驗**

> The Baseline Requirements require CAs to verify all contents of a certificate, except information contained in the organizational unit field, to a minimum degree of diligence. For certificates issued to domain names only, the CA confirms that, as of the date the Certificate was issued, the applicant either is the registrant of the domain name or has control over the FQDN. This can be done through an automated, challenge-response email. A similar requirement applies for verifying the assignment or control of IP addresses. Certification Authorities issuing organizationally-vetted certificates (certificates with subject identity information) verify the name and address of the applicant using reliable information sources, such as a government agency in the jurisdiction of the Applicant's legal creation, existence, or recognition or a reliable third party database. The CA also confirms the authenticity of the certificate request through some means of reliable communication with the organization (i.e. they verify that the certificate requester is an authorized employee/agent within the subscribing organization). For certificates issued to individuals, the CA verifies the individual's identity using a government-issued photo ID that is inspected for indication of alteration or falsification.

《基本要求》要求憑證機構（CA）應盡最低程度的盡職調查（a minimum degree of diligence），驗證憑證中的所有內容，但組織單位（organizational unit）欄位所含之資訊除外。對於簽發僅網域名稱之憑證，CA 應確認於憑證簽發之日，申請者（Applicant）為該網域名稱之註冊人（Registrant），或對該完全吻合網域名稱（FQDN）具有控管權。此項確認可透過自動化之挑戰－回應（challenge-response）電子郵件方式完成。對於指配 IP 位址或控管權的驗證，亦適用類似要求。CA 簽發經組織驗證的憑證（載有主體識別資訊之憑證），應使用可靠資訊來源（reliable information sources）驗證申請者的身分與地址，例如申請者合法設立、存續或獲得認許之所在地主管機關，或者可靠的第三方資料庫。CA 亦應透過可靠通訊方式（reliable communication）與該組織聯繫，確認憑證申請的真實性（亦即，驗證憑證申請者是否為用戶組織內獲授權之員工或代理人）。對於簽發予個人之憑證，CA 應使用政府核發之附照片身分證明文件驗證個人身分，並檢查該身分證明文件是否有遭竄改或偽造的跡象。

> Since 2012, the Baseline Requirements have been incorporated by reference into, and form part of, the CA/Browser Forum's [Extended Validation Guidelines](https://cabforum.org/working-groups/server/extended-validation/).

自 2012 年起，《基本要求》即以引用方式被納入 CA/Browser Forum 的[《EV 指引》（Extended Validation Guidelines）](https://cabforum.org/working-groups/server/extended-validation/)，並構成該指引之一部分。
