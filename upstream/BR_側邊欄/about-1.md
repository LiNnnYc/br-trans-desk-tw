---
aliases:
- /about-the-baseline-requirements/
date: 2013-09-04 03:20:27
title: 關於基準要求 (Baseline Requirements)
---

**關於基準要求（Baseline Requirements）**

《公眾信任憑證核發與管理基準要求》（Baseline Requirements for the Issuance and Management of Publicly-Trusted Certificates）描述了憑證機構（Certification Authority, CA）若欲核發受瀏覽器公眾信任之 SSL/TLS 伺服器數位憑證，所須符合的部分要求。除非另有明確規定，本要求僅適用於該要求生效日期當日或之後發生的事件。

本要求並未涵蓋與公眾信任憑證核發及管理相關的所有議題，CA/Browser Forum 可能會更新本要求，以因應線上安全既有及新興的威脅。

現行版本的要求僅適用於用來驗證可透過網際網路存取之伺服器的憑證。未來版本可能會涵蓋程式碼簽章（code signing）、S/MIME、時間戳記（time-stamping）、VoIP、即時通訊（IM）、Web 服務等類似要求。

本要求亦不適用於企業僅為內部用途而自行架設公開金鑰基礎建設（Public Key Infrastructure, PKI），且其根憑證未由瀏覽器所發佈之情況下的憑證核發或管理。

**依基準要求對憑證申請人進行審查**

基準要求規定 CA 須以最低程度之審慎注意，驗證憑證內容之各項資訊，惟組織單位（organizational unit）欄位所載資訊不在此限。就僅核發予網域名稱之憑證而言，CA 須確認於憑證核發當日，申請人為該網域名稱之註冊人，或對該完全合格網域名稱（FQDN）具有控制權；此項確認可透過自動化之挑戰－回應（challenge-response）電子郵件方式完成。就 IP 位址之指派或控制之驗證，亦適用類似之要求。核發組織審查型憑證（即含主體身分資訊之憑證）之憑證機構，須運用可靠之資訊來源──例如申請人依法設立、存在或受承認所在轄區之政府機關,或可靠之第三方資料庫──驗證申請人之名稱與地址。CA 亦須透過某種可靠之聯繫方式確認憑證申請之真實性（亦即確認憑證申請人係該訂閱組織內經授權之員工或代理人）。就核發予個人之憑證而言，CA 須以政府核發之附照片身分證件驗證申請人身分，並檢查該證件有無變造或偽造之跡象。

自 2012 年起，基準要求已以引用方式納入 CA/Browser Forum 之[延伸驗證準則（Extended Validation Guidelines）][1]，並構成其一部分。

[1]: /?page_id=90 "Extended Validation"
