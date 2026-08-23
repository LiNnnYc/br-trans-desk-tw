---
aliases:
- /baseline-requirements-certificate-contents/
date: 2013-09-04 03:30:54
title: 基準要求 SSL 憑證內容
---

# 公眾信任 SSL/TLS 憑證內容之基準要求 {#Baseline_Requirements_for_Contents_of_Publicly_Trusted_SSL.2BAC8-TLS_Certificates}

符合基準要求之憑證，須遵循基準要求第 9.1 節及第 9.2 節，以及附錄 A 與附錄 B 之規定。以下為該等章節所載之一般性要求：

## CA 憑證 {#CA_Certificates}

建議之金鑰強度為：至少 2048 位元 RSA，搭配 SHA-256、SHA-384 或 SHA-512；或採用 NIST P-256、P-384 或 P-521 之橢圓曲線（Elliptic Curve）演算法。

不得使用 MD5，1024 位元 RSA 及 SHA1 則予以沿用（grandfathered）——在 SHA-256 尚未被全球絕大多數依賴方（relying-parties）所使用之瀏覽器廣泛支援前，SHA-1 得與 RSA 金鑰併用；而於 2010 年 12 月 31 日前核發、RSA 金鑰長度未達 2048 位元之根 CA 憑證，仍得作為訂閱者憑證之信任錨點（trust anchor）。

- **basicConstraints**

本擴充欄位必須存在，且必須標記為關鍵（critical）。cA 欄位必須設為 true。pathLenConstraint 欄位得選擇性存在。

- **keyUsage**

本擴充欄位必須存在，且必須標記為關鍵。keyCertSign 及 cRLSign 之位元位置必須設定。若私密金鑰用於簽署 OCSP 回應，則 digitalSignature 位元必須設定。

## 所有憑證 {#All_Certificates}

除非 CA 知悉將特定資料納入憑證之理由，否則不得核發含有未經指定之 keyUsage 旗標、extendedKeyUsage 值、憑證擴充欄位或其他資料之憑證。CA 不得核發具有下列內容之憑證：(a) 於公開網際網路情境下不適用之擴充欄位（例如僅適用於私有管理網路情境之服務的 extendedKeyUsage 值），除非：i. 該值屬於申請人得證明其擁有權之 OID 分支範圍內，或 ii. 申請人得以其他方式證明其於公開情境中主張該資料之權利；或 (b) 若納入將使依賴方對 CA 所驗證之憑證資訊產生誤解之語義內容（例如針對智慧卡納入 extendedKeyUsage 值，惟因採遠端核發方式，CA 實際上無法驗證對應之私密金鑰確實侷限於該硬體內）。

## 訂閱者憑證 {#Subscriber_Certificates}

- **certificatePolicies**

本擴充欄位必須存在，且不應（SHOULD NOT）標記為關鍵。certificatePolicies:policyIdentifier（必要）

- 由核發 CA 定義之政策識別碼（Policy Identifier），用以表明核發 CA 遵循並符合本要求之憑證政策。

下列擴充欄位得選擇性存在：certificatePolicies:policyQualifiers:policyQualifierId（建議）

- id-qt 1 \[RFC 5280\]。

certificatePolicies:policyQualifiers:qualifier:cPSuri（選用）

- 次級 CA 之憑證實務作業聲明（Certification Practice Statement）、依賴方協議（Relying Party Agreement），或由 CA 提供之其他線上資訊指向連結之 HTTP URL。

- **cRLDistributionPoints**

本擴充欄位得選擇性存在。若存在，則不得標記為關鍵，且必須包含該 CA 憑證撤銷清單（CRL）服務之 HTTP URL。詳見第 13.2.1 節。

- **authorityInformationAccess**

除下述憑證裝訂（stapling）之情形外，本擴充欄位必須存在。其不得標記為關鍵，且必須包含核發 CA 之 OCSP 回應器之 HTTP URL（accessMethod = 1.3.6.1.5.5.7.48.1）。並應（SHOULD）包含核發 CA 憑證之 HTTP URL（accessMethod = 1.3.6.1.5.5.7.48.2）。詳見第 13.2.1 節。若訂閱者於其 TLS 交握（handshake）過程中對該憑證採用 OCSP 回應「裝訂」（staples）方式 \[RFC4366\]，則核發 CA 之 OCSP 回應器 HTTP URL 得予省略。

- **basicConstraints（選用）**

若存在，cA 欄位必須設為 false。

- **keyUsage（選用）**

若存在，keyCertSign 及 cRLSign 之位元位置不得設定。

- **extKeyUsage（必要）**

id-kp-serverAuth \[RFC5280\] 或 id-kp-clientAuth \[RFC5280\] 之值，二者至少須存在其一，或兩者皆存在。id-kp-emailProtection \[RFC5280\] 得選擇性存在。其他值則不應（SHOULD NOT）存在。
