---
title: "DNS TXT 紀錄電話聯絡人（DNS TXT Record Phone Contact）"
section_id: "appendix-a.2.2"
parent: "appendix-a.2"
order: 412
original_url: "https://cabforum.org/working-groups/server/baseline-requirements/requirements/#a22-dns-txt-record-phone-contact"
original_version: "2.2.7"
ballot_refs: []
translator: "Claude (Sonnet) 初譯 + ChatGPT (Instant) 潤稿 + LiNnnYc 審閱"
last_updated: 2026-09-12
status: translated
tags: []
---

> **DNS TXT Record Phone Contact**

> The DNS TXT record MUST be placed on the "`_validation-contactphone`" subdomain of the domain being validated. The entire RDATA value of this TXT record MUST be a valid Global Number as defined in [RFC 3966, Section 5.1.4](https://datatracker.ietf.org/doc/html/rfc3966#section-5.1.4), or it cannot be used.

DNS TXT 紀錄**應（MUST）**置於待驗證網域名稱的「`_validation-contactphone`」子網域上。此 TXT 紀錄的整個 RDATA 值**應（MUST）**為 [RFC 3966 第 5.1.4 節](https://datatracker.ietf.org/doc/html/rfc3966#section-5.1.4) 所定義的有效全球號碼（Global Number），否則不得使用。
