---
term_en: "OCSP Stapling"
term_zh: "線上憑證狀態協定裝訂"
definition: |
  一種 TLS 憑證狀態請求擴展欄位（TLS Certificate Status Request extension），可替代線上憑證狀態協定（OCSP）成為另一種檢查 X.509 憑證狀態的方法。
  本方法在運作上，網站會事先向 OCSP 回應伺服器取得有「時間限制（例如兩小時）」的 OCSP Response 並暫存；接下來，在每一次的 TLS Handshake 的初始過程中，網站會將此暫存的 OCSP Response 傳送給用戶（通常為瀏覽器），用戶只需驗證該 OCSP Response 的有效性而不用再向 CA 發送 OCSP 請求，如此可避免用戶每次連結高流量 TLS 網站都需要向 CA 詢問其 TLS 憑證狀態，因此減輕 CA 的負擔。
source: "HiPKICA CP/CPS v1.1 附錄 2"
---
