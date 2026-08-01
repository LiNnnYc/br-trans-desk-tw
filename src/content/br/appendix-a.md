---
title: "CAA 聯絡標籤"
section_id: "appendix-a"
order: 406
original_url: "https://cabforum.org/working-groups/server/baseline-requirements/requirements/#appendix-a-caa-contact-tag"
original_version: "2.2.7"
ballot_refs: []
translator: "免費 AI 初譯 + Claude (Opus) 潤稿"
last_updated: 2026-05-24
status: draft
tags: []
---

> **CAA Contact Tag**

> These methods allow domain owners to publish contact information in DNS for the purpose of validating domain control.

這些方法允許網域名稱（Domain Name）擁有者在 DNS 中發布聯絡資訊，以供網域控管驗證之用。

## A.1. CAA 方法

### A.1.1. CAA contactemail 屬性

> SYNTAX: `contactemail <rfc6532emailaddress>`

語法：`contactemail <rfc6532emailaddress>`

> The CAA contactemail property takes an email address as its parameter. The entire parameter value MUST be a valid email address as defined in [RFC 6532, Section 3.2](https://datatracker.ietf.org/doc/html/rfc6532#section-3.2), with no additional padding or structure, or it cannot be used.

CAA `contactemail` 屬性以電子郵件地址作為參數。整個參數值**應（MUST）**為 RFC 6532 第 3.2 節所定義的有效電子郵件地址，不得附加任何填充或結構，否則不得使用。

> The following is an example where the holder of the domain specified the contact property using an email address.

以下為網域名稱持有人以電子郵件地址指定聯絡屬性的範例。

```DNSZone
$ORIGIN example.com .
CAA 0 contactemail "domainowner@example.com"
```

> The contactemail property MAY be critical, if the domain owner does not want CAs who do not understand it to issue certificates for the domain.

若網域名稱擁有者不希望不瞭解此屬性的 CA 為該網域名稱簽發憑證，`contactemail` 屬性**得（MAY）**設為 critical。

### A.1.2. CAA contactphone 屬性

> SYNTAX: `contactphone <rfc3966 Global Number>`

語法：`contactphone <rfc3966 Global Number>`

> The CAA contactphone property takes a phone number as its parameter. The entire parameter value MUST be a valid Global Number as defined in [RFC 3966, Section 5.1.4](https://datatracker.ietf.org/doc/html/rfc3966#section-5.1.4), or it cannot be used. Global Numbers MUST have a preceding + and a country code and MAY contain spaces as visual separators.

CAA `contactphone` 屬性以電話號碼作為參數。整個參數值**應（MUST）**為 RFC 3966 第 5.1.4 節所定義的有效 Global Number，否則不得使用。Global Number **應（MUST）**以 + 開頭並含有國碼，且**得（MAY）**包含空格作為視覺分隔符號。

> The following is an example where the holder of the domain specified the contact property using a phone number.

以下為網域名稱持有人以電話號碼指定聯絡屬性的範例。

```DNSZone
$ORIGIN example.com .
CAA 0 contactphone "+1 555 123 4567"
```

> The contactphone property MAY be critical if the domain owner does not want CAs who do not understand it to issue certificates for the domain.

若網域名稱擁有者不希望不瞭解此屬性的 CA 為該網域名稱簽發憑證，`contactphone` 屬性**得（MAY）**設為 critical。

## A.2. DNS TXT 方法

### A.2.1. DNS TXT 紀錄電子郵件聯絡

> The DNS TXT record MUST be placed on the "`_validation-contactemail`" subdomain of the domain being validated. The entire RDATA value of this TXT record MUST be a valid email address as defined in [RFC 6532, Section 3.2](https://datatracker.ietf.org/doc/html/rfc6532#section-3.2), with no additional padding or structure, or it cannot be used.

DNS TXT 紀錄**應（MUST）**置於待驗證網域名稱的「`_validation-contactemail`」子網域上。此 TXT 紀錄的整個 RDATA 值**應（MUST）**為 RFC 6532 第 3.2 節所定義的有效電子郵件地址，不得附加任何填充或結構，否則不得使用。

### A.2.2. DNS TXT 紀錄電話聯絡

> The DNS TXT record MUST be placed on the "`_validation-contactphone`" subdomain of the domain being validated. The entire RDATA value of this TXT record MUST be a valid Global Number as defined in [RFC 3966, Section 5.1.4](https://datatracker.ietf.org/doc/html/rfc3966#section-5.1.4), or it cannot be used.

DNS TXT 紀錄**應（MUST）**置於待驗證網域名稱的「`_validation-contactphone`」子網域上。此 TXT 紀錄的整個 RDATA 值**應（MUST）**為 RFC 3966 第 5.1.4 節所定義的有效 Global Number，否則不得使用。
