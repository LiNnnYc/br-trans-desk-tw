---
title: "CAA contactphone 屬性"
section_id: "appendix-a.1.2"
parent: "appendix-a.1"
order: 409
original_url: "https://cabforum.org/working-groups/server/baseline-requirements/requirements/#a12-caa-contactphone-property"
original_version: "2.2.7"
ballot_refs: []
translator: "免費 AI 初譯 + Claude (Opus) 潤稿"
last_updated: 2026-05-24
status: draft
tags: []
---

> **CAA contactphone Property**

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
