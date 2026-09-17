---
term_en: "Certification Authority Authorization"
abbreviation: "CAA"
recommended_zh: "授權憑證機構簽發憑證"
recommended_definition: |
  《基本要求》第 1.6.2 節縮寫表所列，全稱為「Certification Authority Authorization」。
recommended_source: "BR"
first_seen_at: "/server-cert-br/3-2-2-8/"
sources:
  - source: "BR"
    version: "v2.2.7"
    term_zh: "授權憑證機構簽發憑證"
    definition: |
      《基本要求》第 1.6.2 節縮寫表所列，全稱為「Certification Authority Authorization」。
    ref: "/server-cert-br/1-6-2/"
  - source: "HiPKICA"
    version: "v1.2"
    term_zh: "授權憑證機構簽發憑證"
    definition: |
      CAA 網域名稱系統資源紀錄（DNS Resource Record）允許網域名稱系統之網域名稱擁有者指定憑證機構（一個或多個）取得授權幫該網域名稱簽發憑證。發布 CAA DNS Resource Record 允許公眾信賴之憑證機構實施額外之控制降低非預期之憑證誤發的風險。[RFC 8659]
    ref: "HiPKICA CP/CPS v1.2 附錄 2"
  - source: "TWCA"
    version: "v3.2"
    term_zh: "授權憑證機構簽發"
    definition: |
      是一種 DNS 資源紀錄，它允許網站所有者指定哪些 CA 有權為其網域發行 TLS 憑證。透過設定 CAA 紀錄，網站管理者可以限制憑證的發行權限，有效防止未經授權的 CA 意外或惡意地為其網域頒發憑證，從而增強網域憑證的安全性。
    ref: "TWCA Global CPS v3.2 附錄一"
tags: []
---
