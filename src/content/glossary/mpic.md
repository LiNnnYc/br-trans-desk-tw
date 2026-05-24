---
term_en: "Multi-Perspective Issuance Corroboration"
term_zh: "多視角簽發佐證"
abbreviation: "MPIC"
definition: "多視角簽發佐證要求 CA 在核發憑證前，必須由多個地理位置分散的驗證節點交叉確認 DNS 記錄與網域驗證結果是否一致，以降低因 BGP 劫持、DNS 汙染或區域性網路攻擊所導致的錯誤驗證風險。在 MPIC 架構中，驗證流程包含兩種視角：主要網路視角（Primary Network Perspective）由 CA 的主要驗證節點執行，負責取得 DNS、CAA、HTTP-01 或 TLS-ALPN-01 等基礎驗證資料，作為後續比對的基準；遠端網路視角（Remote Network Perspective）由分布於不同地理區域、不同網路路徑的節點執行，必須能取得與主要網路視角一致的驗證資訊。CA 只有在主要網路視角與所有遠端網路視角均取得一致結果時，方可視該網域驗證為有效。"
source: "TWCA Global CPS v3.1 附錄一（譯名依 BR §3.2.2.9 修正為「多視角簽發佐證」）"
---
