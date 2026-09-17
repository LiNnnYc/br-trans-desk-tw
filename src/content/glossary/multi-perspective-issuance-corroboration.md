---
term_en: "Multi-Perspective Issuance Corroboration"
abbreviation: "MPIC"
recommended_zh: "多視角簽發佐證"
recommended_definition: |
  於憑證簽發前，由其他網路視角（Network Perspectives）佐證主要網路視角（Primary Network Perspective）在網域驗證及 CAA 檢查時所做判定之流程。
recommended_source: "BR"
sources:
  - source: "BR"
    version: "v2.2.7"
    term_zh: "多視角簽發佐證"
    definition: |
      於憑證簽發前，由其他網路視角（Network Perspectives）佐證主要網路視角（Primary Network Perspective）在網域驗證及 CAA 檢查時所做判定之流程。
    ref: "/server-cert-br/1-6-1/"
  - source: "TWCA"
    version: "v3.2"
    term_zh: "多視角驗證"
    definition: |
      多視角驗證要求 CA 在核發憑證前，必須由多個地理位置分散的驗證節點交叉確認 DNS 記錄與網域驗證結果是否一致，以降低因 BGP 劫持、DNS 汙染或區域性網路攻擊所導致的錯誤驗證風險。在 MPIC 架構中，驗證流程包含兩種視角：
      
      主視角驗證（Primary Perspective）：
      由 CA 的主要驗證節點執行，負責取得 DNS、CAA、HTTP-01 或 TLS-ALPN-01 等基礎驗證資料，作為後續比對的基準。主視角主要用於確認申請端是否具備基本且可被正常觀測的驗證配置。
      
      遠端視角驗證（Remote Perspective）：
      由分布於不同於主視角之地理區域、不同網路路徑的節點執行。這些節點必須能取得與主視角一致的驗證資訊，以確認該網域的設定在全球皆呈現一致狀態，並排除僅發生在 CA 主視角附近的路由或 DNS 欺騙情形。

      CA 只有在主視角與所有遠端視角均取得一致結果時，方可視該網域驗證為有效，並據以簽發憑證；若任一視角觀測不一致，驗證即視為失敗。
    ref: "TWCA Global CPS v3.2 附錄一"
tags: []
---
