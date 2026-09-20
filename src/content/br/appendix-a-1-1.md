---
title: "CAA contactemail 屬性標籤"
section_id: "appendix-a.1.1"
parent: "appendix-a.1"
order: 420
original_url: "https://cabforum.org/working-groups/server/baseline-requirements/requirements/#a11-caa-contactemail-property"
original_version: "2.3.0"
ballot_refs: []
translator: "Claude (Sonnet) 初譯 + ChatGPT (Instant) 潤稿 + LiNnnYc 審閱"
last_updated: 2026-09-20
status: translated
tags: []
---

> **CAA contactemail Property**

> SYNTAX: `contactemail <rfc6532emailaddress>`

語法：`contactemail <rfc6532emailaddress>`

> The CAA contactemail property takes an email address as its parameter. The entire parameter value MUST be a valid email address as defined in [RFC 6532, Section 3.2](https://datatracker.ietf.org/doc/html/rfc6532#section-3.2), with no additional padding or structure, or it cannot be used.

CAA `contactemail` 屬性接受電子郵件地址作為其參數。整個參數值**應（MUST）**為 [RFC 6532 第 3.2 節](https://datatracker.ietf.org/doc/html/rfc6532#section-3.2) 所定義的有效電子郵件地址，且不得包含任何額外字元或結構，否則不得使用。

> The following is an example where the holder of the domain specified the contact property using an email address.

以下為網域名稱持有人使用電子郵件地址指定聯絡屬性之範例。

```DNSZone
$ORIGIN example.com .
CAA 0 contactemail "domainowner@example.com"
```

> The contactemail property MAY be critical, if the domain owner does not want CAs who do not understand it to issue certificates for the domain.

若網域名稱擁有者不希望無法解析 `contactemail` 屬性的憑證機構（CA）對該網域名稱簽發憑證，`contactemail` 屬性**得（MAY）**設為關鍵（critical）。
