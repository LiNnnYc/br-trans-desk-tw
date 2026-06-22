---
term_en: "Authorization Domain Name"
abbreviation: "ADN"
recommended_zh: "經授權網域名稱"
recommended_source: "BR"
sources:
  - source: "BR"
    term_zh: "經授權網域名稱"
    definition: |
      係指用以證明有權將指定完全吻合網域名稱（FQDN）納入憑證之 FQDN。憑證機構（CA）可將 DNS CNAME 查詢所回覆之 FQDN 作為網域驗證目的之 FQDN。若擬將萬用網域名稱（Wildcard Domain Name）納入憑證內容，則 CA **應（MUST）**移除萬用網域名稱最左端之「*.」，以產生符合規定之 FQDN。CA 可自左至右刪除該 FQDN 之零個或多個網域標籤（Domain Labels），直至遇到基礎網域名稱（Base Domain Name）為止，也可使用刪除過程中所產生之任一值（包括基礎網域名稱本身）作為網域驗證之用。
    ref: "/server-cert-br/1-6-1/"
  - source: "HiPKICA"
    term_zh: "經授權網域名稱"
    definition: |
      用於取得對某一個特定完全吻合網域名稱之憑證簽發的授權之網域名稱。
      憑證機構可使用網域名稱服務別名紀錄查詢服務（DNS CNAME lookup）所回覆之 FQDN 當作 FQDN，用來達到網域驗證的目的。如果 FQDN 包含萬用字元，則憑證機構必須從被請求之 FQDN 的最左邊移除所有萬用字元。憑證機構可從左至右刪除零個或多個標籤（label）直到遇到基礎網域名稱，也可使用任何在這個過程中的值來達到網域驗證的目的。
    ref: "HiPKICA CP/CPS v1.1 附錄 2"
tags: []
---
