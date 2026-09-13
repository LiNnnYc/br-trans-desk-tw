---
term_en: "Authorization Domain Name"
abbreviation: "ADN"
recommended_zh: "經授權網域名稱"
recommended_definition: |
  係指用以對指定之完全吻合網域名稱（FQDN）或萬用網域名稱（Wildcard Domain Name）執行網域授權或控管權驗證之 FQDN。
  （v2.3.0 起，ADN 的推導方式改由《基本要求》§3.2.2.4 的選取流程規範，不再寫在定義裡。）
recommended_source: "BR"
sources:
  - source: "BR"
    version: "v2.3.0"
    term_zh: "經授權網域名稱"
    definition: |
      係指用以對指定之完全吻合網域名稱（FQDN）或萬用網域名稱（Wildcard Domain Name）執行網域授權或控管權驗證之 FQDN。
      （v2.3.0 起，ADN 的推導方式改由《基本要求》§3.2.2.4 的選取流程規範，不再寫在定義裡。）
    ref: "/server-cert-br/1-6-1/"
  - source: "HiPKICA"
    version: "v1.1"
    term_zh: "經授權網域名稱"
    definition: |
      用於取得對某一個特定完全吻合網域名稱之憑證簽發的授權之網域名稱。
      憑證機構可使用網域名稱服務別名紀錄查詢服務（DNS CNAME lookup）所回覆之 FQDN 當作 FQDN，用來達到網域驗證的目的。如果 FQDN 包含萬用字元，則憑證機構必須從被請求之 FQDN 的最左邊移除所有萬用字元。憑證機構可從左至右刪除零個或多個標籤（label）直到遇到基礎網域名稱，也可使用任何在這個過程中的值來達到網域驗證的目的。
    ref: "HiPKICA CP/CPS v1.1 附錄 2"
tags: []
---
