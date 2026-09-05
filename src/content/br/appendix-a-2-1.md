---
title: "DNS TXT 紀錄電子郵件聯絡"
section_id: "appendix-a.2.1"
parent: "appendix-a.2"
order: 411
original_url: "https://cabforum.org/working-groups/server/baseline-requirements/requirements/#a21-dns-txt-record-email-contact"
original_version: "2.2.7"
ballot_refs: []
translator: "免費 AI 初譯 + Claude (Opus) 潤稿"
last_updated: 2026-05-24
status: draft
tags: []
---

> **DNS TXT Record Email Contact**

> The DNS TXT record MUST be placed on the "`_validation-contactemail`" subdomain of the domain being validated. The entire RDATA value of this TXT record MUST be a valid email address as defined in [RFC 6532, Section 3.2](https://datatracker.ietf.org/doc/html/rfc6532#section-3.2), with no additional padding or structure, or it cannot be used.

DNS TXT 紀錄**應（MUST）**置於待驗證網域名稱的「`_validation-contactemail`」子網域上。此 TXT 紀錄的整個 RDATA 值**應（MUST）**為 RFC 6532 第 3.2 節所定義的有效電子郵件地址，不得附加任何填充或結構，否則不得使用。
