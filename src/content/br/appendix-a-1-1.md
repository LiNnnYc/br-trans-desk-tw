---
title: "CAA contactemail 屬性"
section_id: "appendix-a.1.1"
parent: "appendix-a.1"
order: 408
original_url: "https://cabforum.org/working-groups/server/baseline-requirements/requirements/#a11-caa-contactemail-property"
original_version: "2.2.7"
ballot_refs: []
translator: "免費 AI 初譯 + Claude (Opus) 潤稿"
last_updated: 2026-05-24
status: draft
tags: []
---

> **CAA contactemail Property**

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
