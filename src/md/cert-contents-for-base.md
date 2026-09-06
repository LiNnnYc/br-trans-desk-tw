> **Baseline Requirements for Contents of Publicly Trusted SSL/TLS Certificates**

> Certificates conforming to the Baseline Requirements must comply with sections 9.1 and 9.2 of the Baseline Requirements as well as Appendices A and B. Here are the general requirements found in those parts of the Baseline Requirements:

遵循《基本要求》之憑證，須符合《基本要求》第 9.1 節、第 9.2 節以及附錄 A 與附錄 B 之規定。以下為《基本要求》上述部分所載之一般性要求：

**編按**：本段所引條號為 2013 年撰寫本頁時的《基本要求》1.0 版編號。現行《基本要求》（v2.2.7）已改採 RFC 3647 架構，**第 9.1 節為「費用」、第 9.2 節為「財務責任」，與憑證內容無關**；憑證剖繪現規定於[第 7.1 節](#71-certificate-profile)（憑證剖繪）、[第 7.2 節](#72-crl-profile)（CRL 剖繪）與[第 7.3 節](#73-ocsp-profile)（OCSP 剖繪）。附錄 A 現為「CAA 聯絡標籤」、附錄 B 現為「為 Onion 網域名稱簽發憑證」。

> **CA Certificates**

## 憑證機構（CA）憑證

> Recommended key strengths are at least 2048-bit RSA using SHA-256, SHA-384 or SHA-512 or Elliptic Curve using NIST P-256, P-384, or P-521.

建議之金鑰強度為至少 2048 位元 RSA 搭配 SHA-256、SHA-384 或 SHA-512，或使用 NIST P-256、P-384、P-521 之橢圓曲線（Elliptic Curve）。

> No MD5, and 1024-bit RSA and SHA1 are grandfathered. — SHA-1 MAY be used with RSA keys until SHA-256 is supported widely by browsers used by a substantial portion of relying-parties worldwide, and a Root CA Certificate issued prior to 31 Dec. 2010 with an RSA key size less than 2048 bits may still serve as a trust anchor for Subscriber Certificates.

不得使用 MD5；1024 位元 RSA 與 SHA-1 則適用既存保留（grandfathered）。在全球相當比例之信賴憑證者所使用的瀏覽器廣泛支援 SHA-256 之前，SHA-1 **得（MAY）**與 RSA 金鑰搭配使用；且於 2010 年 12 月 31 日前簽發、RSA 金鑰長度小於 2048 位元之根憑證機構憑證，仍得作為用戶憑證之信賴根源（Trust Anchor）。

**編按**：本段所述之過渡安排早已失效。現行金鑰長度規定見[第 6.1.5 節](#615-key-sizes)，簽章演算法規定見[第 7.1.3.2 節](#7132-signature-algorithmidentifier)——SHA-1 僅在極有限的既有憑證情形下、且於 2026-09-15 前始得使用。

> - **basicConstraints**
>
>   This extension MUST be present and MUST be marked critical. The cA field MUST be set true. The pathLenConstraint field MAY be present.
>
> - **keyUsage**
>
>   This extension MUST be present and MUST be marked critical. Bit positions for keyCertSign and cRLSign MUST be set. If the Private Key is used for signing OCSP responses, then the digitalSignature bit MUST be set.

- **`basicConstraints`**

  此擴充欄位**應（MUST）**存在，且**應（MUST）**標記為關鍵（critical）。`cA` 欄位**應（MUST）**設為 true。`pathLenConstraint` 欄位**得（MAY）**存在。

- **`keyUsage`**

  此擴充欄位**應（MUST）**存在，且**應（MUST）**標記為關鍵（critical）。`keyCertSign` 與 `cRLSign` 之位元位置**應（MUST）**設定。若該私密金鑰用於簽署 OCSP 回應，則 `digitalSignature` 位元**應（MUST）**設定。

> **All Certificates**

## 所有憑證

> CA shall not issue Certificates containing a keyUsage flag, extendedKeyUsage value, Certificate extension, or other data not specified unless the CA is aware of a reason for including the data in the Certificate. CAs SHALL NOT issue a Certificate with:
>
> - (a) Extensions that do not apply in the context of the public Internet (such as an extendedKeyUsage value for a service that is only valid in the context of a privately managed network), unless:
>   - i. such value falls within an OID arc for which the Applicant demonstrates ownership, or
>   - ii. the Applicant can otherwise demonstrate the right to assert the data in a public context; or
> - (b) semantics that, if included, will mislead a Relying Party about the certificate information verified by the CA (such as including extendedKeyUsage value for a smart card, where the CA is not able to verify that the corresponding Private Key is confined to such hardware due to remote issuance).

除非 CA 知悉將該資料納入憑證之理由，否則 CA 不應簽發含有未經規定之 `keyUsage` 旗標、`extendedKeyUsage` 值、憑證擴充欄位或其他資料之憑證。CA **不得（SHALL NOT）**簽發具有下列情形之憑證：

- （a）不適用於公眾網際網路情境之擴充欄位（例如僅在私有管理網路情境下方為有效之服務所使用的 `extendedKeyUsage` 值），但下列情形不在此限：
  - i. 該值落於申請者能證明其所有權之 OID arc 內；或
  - ii. 申請者能以其他方式證明其有權於公開情境中主張該資料；或
- （b）若納入將使信賴憑證者對 CA 所查核之憑證資訊產生誤解之語意（例如納入智慧卡專用之 `extendedKeyUsage` 值，而 CA 因採遠端簽發而無法查核對應之私密金鑰確實受限於該硬體之中）。

> **Subscriber Certificates**

## 用戶憑證

> - **certificatePolicies**
>
>   This extension MUST be present and SHOULD NOT be marked critical. certificatePolicies:policyIdentifier (Required)
>
>   - A Policy Identifier, defined by the issuing CA, that indicates a Certificate Policy asserting the issuing CA's adherence to and compliance with these Requirements.
>
>   The following extensions MAY be present: certificatePolicies:policyQualifiers:policyQualifierId (Recommended)
>
>   - id-qt 1 \[RFC 5280\].
>
>   certificatePolicies:policyQualifiers:qualifier:cPSuri (Optional)
>
>   - HTTP URL for the Subordinate CA's Certification Practice Statement, Relying Party Agreement or other pointer to online information provided by the CA.

- **`certificatePolicies`**

  此擴充欄位**應（MUST）**存在，且**不宜（SHOULD NOT）**標記為關鍵。`certificatePolicies:policyIdentifier`（必要）

  - 由簽發 CA 所定義之政策識別碼，用以表明簽發 CA 遵守並遵循本要求規定之憑證政策。

  下列擴充欄位**得（MAY）**存在：`certificatePolicies:policyQualifiers:policyQualifierId`（建議）

  - id-qt 1 \[RFC 5280\]。

  `certificatePolicies:policyQualifiers:qualifier:cPSuri`（選用）

  - 下屬 CA 之憑證實務作業基準（CPS）、信賴憑證者合約（Relying Party Agreement）之 HTTP URL，或 CA 所提供之其他線上資訊指標。

> - **cRLDistributionPoints**
>
>   This extension MAY be present. If present, it MUST NOT be marked critical, and it MUST contain the HTTP URL of the CA's CRL service. See Section 13.2.1 for details.

- **`cRLDistributionPoints`**

  此擴充欄位**得（MAY）**存在。若存在，則**不得（MUST NOT）**標記為關鍵，且**應（MUST）**包含該 CA 之 CRL 服務 HTTP URL。詳見第 13.2.1 節。

> - **authorityInformationAccess**
>
>   With the exception of stapling, which is noted below, this extension MUST be present. It MUST NOT be marked critical, and it MUST contain the HTTP URL of the Issuing CA's OCSP responder (accessMethod = 1.3.6.1.5.5.7.48.1). It SHOULD also contain the HTTP URL of the Issuing CA's certificate (accessMethod = 1.3.6.1.5.5.7.48.2). See Section 13.2.1 for details. The HTTP URL of the Issuing CA's OCSP responder MAY be omitted provided that the Subscriber "staples" OCSP responses for the Certificate in its TLS handshakes \[RFC4366\].

- **`authorityInformationAccess`**

  除下述 stapling 之情形外，此擴充欄位**應（MUST）**存在。它**不得（MUST NOT）**標記為關鍵，且**應（MUST）**包含簽發 CA 之 OCSP 回應伺服器 HTTP URL（accessMethod = 1.3.6.1.5.5.7.48.1）。它亦**宜（SHOULD）**包含簽發 CA 憑證之 HTTP URL（accessMethod = 1.3.6.1.5.5.7.48.2）。詳見第 13.2.1 節。若用戶於其 TLS 交握中對該憑證「stapling」OCSP 回應 \[RFC4366\]，則簽發 CA 之 OCSP 回應伺服器 HTTP URL **得（MAY）**省略。

**編按**：上兩段的「第 13.2.1 節」為《基本要求》1.0 版編號，**現行版本並無第 13 章**（最高為第 9 章）。另外，現行[第 7.1.2.7.7 節](#71277-subscriber-certificate-authority-information-access)已將 `id-ad-ocsp`（OCSP 回應伺服器 URL）改為**得（MAY）**，不再是必要欄位；CRL 與 OCSP 之簽發與可用性規定見[第 4.9.7 節](#497-crl-issuance-frequency)與[第 4.9.9 節](#499-on-line-revocationstatus-checking-availability)。`certificatePolicies` 之現行規定見[第 7.1.2.7.9 節](#71279-subscriber-certificate-certificate-policies)。

> - **basicConstraints (optional)**
>
>   If present, the cA field MUST be set false.
>
> - **keyUsage (optional)**
>
>   If present, bit positions for keyCertSign and cRLSign MUST NOT be set.
>
> - **extKeyUsage (required)**
>
>   Either the value id-kp-serverAuth \[RFC5280\] or id-kp-clientAuth \[RFC5280\] or both values MUST be present. id-kp-emailProtection \[RFC5280\] MAY be present. Other values SHOULD NOT be present.

- **`basicConstraints`（選用）**

  若存在，`cA` 欄位**應（MUST）**設為 false。

- **`keyUsage`（選用）**

  若存在，`keyCertSign` 與 `cRLSign` 之位元位置**不得（MUST NOT）**設定。

- **`extKeyUsage`（必要）**

  `id-kp-serverAuth` \[RFC5280\] 或 `id-kp-clientAuth` \[RFC5280\] 二者之一，或兩者，**應（MUST）**存在。`id-kp-emailProtection` \[RFC5280\] **得（MAY）**存在。其他值則**不宜（SHOULD NOT）**存在。

**編按**：`extKeyUsage` 的規定已變更。依現行[第 7.1.2.7.10 節](#712710-subscriber-certificate-extended-key-usage)，用戶憑證中 `id-kp-emailProtection` 為**不得（MUST NOT）**存在，與本頁所述「得存在」相反。引用時請以《基本要求》本文為準。
