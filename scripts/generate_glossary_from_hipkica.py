"""
一次性匯入腳本：依 HiPKICA CP/CPS v1.1 附錄 1（縮寫及定義）與附錄 2（名詞解釋）
產生 src/content/glossary/*.md。

執行：
    python scripts/generate_glossary_from_hipkica.py

每筆 entry 標註 source: 'HiPKICA CP/CPS v1.1 附錄 X'，方便未來辨識。
"""
from __future__ import annotations
import os
from pathlib import Path

# (slug, term_en, term_zh, abbreviation, definition, first_seen_at, source)
# slug = 檔名（kebab-case）；first_seen_at 可為 None。
# definition 可含換行（會以 YAML literal block 寫入）。
ENTRIES: list[tuple[str, str, str, str | None, str, str | None, str]] = [
    # ─── 附錄 1 中可直接視為 BR 名詞的縮寫（其餘附錄 2 已詳述者，會以附錄 2 為準）─
    (
        "aia", "Authority Information Access", "憑證機構資訊存取", "AIA",
        "記載有關存取憑證機構資訊的擴充欄位，內容可包含：線上憑證狀態協定（OCSP）回應伺服器的服務位址，以及憑證簽發機構之憑證驗證路徑的下載位址等。微軟之視窗作業系統中文版將此名詞翻譯為「授權存取資訊」。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "ca", "Certification Authority", "憑證機構", "CA",
        "（1）簽發憑證之機關、法人。[電子簽章法第 2 條第 5 款]\n（2）為使用者所信任之權威機構，其業務為簽發並管理 ITU-T X.509 格式之公開金鑰憑證及憑證廢止清冊。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "caa", "Certification Authority Authorization", "授權憑證機構簽發憑證", "CAA",
        "CAA 網域名稱系統資源紀錄（DNS Resource Record）允許網域名稱系統之網域名稱擁有者指定憑證機構（一個或多個）取得授權幫該網域名稱簽發憑證。發布 CAA DNS Resource Record 允許公眾信賴之憑證機構實施額外之控制降低非預期之憑證誤發的風險。[RFC 8659]",
        "/server-cert-br/3-2-2-8/", "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "cpa", "Chartered Professional Accountants Canada", "加拿大會計師公會", "CPA",
        "與美國會計師公會共同訂頒 The Trust Services Principles and Criteria for Security, Availability, Processing Integrity, Confidentiality and Privacy 系列標準之單位，並為 WebTrust for CA、SSL Baseline Requirement & Network Security 標章之管理單位。加拿大會計師公會之前英文名稱為 Canadian Institute of Chartered Accountants，縮寫為 CICA。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "cp-oid", "CP Object Identifier", "憑證政策物件識別碼", "CP OID",
        "憑證政策物件識別碼，用以唯一識別憑證政策。",
        None, "HiPKICA CP/CPS v1.1 附錄 1",
    ),
    (
        "cps", "Certification Practice Statement", "憑證實務作業基準", "CPS",
        "（1）由憑證機構對外公告，用以陳述憑證機構據以簽發憑證及處理其他認證業務之作業準則。[電子簽章法第 2 條第 7 款]\n（2）宣告某憑證機構對憑證之作業程序（包括簽發、停用、廢止及存取等）符合特定需求（需求載明於憑證政策或其他服務契約中）之聲明。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "crl", "Certificate Revocation List", "憑證廢止清冊", "CRL",
        "（1）憑證機構以數位方式簽章，並可供信賴憑證者使用之已廢止憑證表列。[憑證實務作業基準應載明事項準則第 1 章第 2 條第 8 項]\n（2）由憑證機構維護之清單，清單中記載由此憑證機構所簽發且在到期日之前被廢止之憑證。",
        "/server-cert-br/4-9-7/", "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "dn", "Distinguished Name", "唯一識別名稱", "DN",
        "X.500 命名規範下唯一識別某個目錄項目的名稱結構。",
        None, "HiPKICA CP/CPS v1.1 附錄 1",
    ),
    (
        "dns", "Domain Name System", "網域名稱系統", "DNS",
        "用來自動轉換 IP 位址與網域名稱的分散式資料庫。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "ee", "End Entity", "終端個體", "EE",
        "在本基礎建設中包括以下兩類個體：\n（1）負責保管及應用憑證的私密金鑰擁有者。\n（2）信賴本基礎建設憑證機構所簽發憑證的第三者（不是私密金鑰擁有者，也不是憑證機構），亦即終端個體為用戶及信賴憑證者，包括人員、組織、客戶（Account）、裝置或站台（Site）。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "fips", "Federal Information Processing Standard", "聯邦資訊處理標準", "FIPS",
        "為美國聯邦政府制定除軍事機構外，所有政府機構及政府承包商所引用之資訊處理標準。其中密碼模組安全需求標準為 FIPS 第 140 號標準（簡稱 FIPS 140），FIPS 140-2 將密碼模組區分為 11 類安全需求，每一個安全需求類別再分成 4 個安全等級。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "fqdn", "Fully Qualified Domain Name", "完全吻合網域名稱", "FQDN",
        "一種用於指定電腦在網域階層中確切位置的明確網域名稱。完全吻合網域名稱包含主機名稱（服務名稱）與網域名稱兩部分。以 ourserver.ourdomain.com.tw 為例，ourserver 是主機名稱，ourdomain.com.tw 是網域名稱，其中 ourdomain 是第 3 層網域名稱，com 則是次級網域名稱（Second-Level Domain），tw 則是國碼頂級網域名稱（Country Code Top-Level Domain, ccTLD）。完全吻合網域名稱的開頭一定是主機名稱。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "iana", "Internet Assigned Numbers Authority", "網際網路號碼分配機構", "IANA",
        "負責管理國際網際網路中使用的 IP 位址、網域名稱及許多其它參數之組織。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "idn", "Internationalized Domain Name", "國際化域名", "IDN",
        "一種網際網路網域名稱，至少包含一個特定語言的腳本（Script）或字母字元（Alphabetic Character），然後以 punycode 編碼，用於只接受 ASCII 字符串的網域名稱服務。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "ietf", "Internet Engineering Task Force", "網際網路工程任務小組", "IETF",
        "負責網際網路標準的開發和推動。官方網站位於 https://www.ietf.org/，其願景是藉由產製高品質之技術文件影響人類設計、使用與管理網際網路，使得網際網路運作更順暢。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "nist", "National Institute of Standards and Technology", "（美國）國家標準和技術研究院", "NIST",
        "美國商務部下屬的非監管機構，負責制訂資訊安全相關標準（如 FIPS 系列）。",
        None, "HiPKICA CP/CPS v1.1 附錄 1",
    ),
    (
        "ocsp", "Online Certificate Status Protocol", "線上憑證狀態協定", "OCSP",
        "線上憑證狀態協定（Online Certificate Status Protocol）是一種線上憑證檢查協定，使信賴憑證者應用軟體可決定某張憑證之狀態（例如已廢止、有效等）。",
        "/server-cert-br/4-9-9/", "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "oid", "Object Identifier", "物件識別碼", "OID",
        "（1）一種以字母或數字組成之唯一識別碼，該識別碼必須依國際標準組織所訂定之註冊標準加以註冊，並可被用以識別唯一與之對應之憑證政策。\n（2）向國際標準化組織（ISO）註冊的特別形式的數碼，當提及某物件或物件類別時，可以引用此唯一的數碼做辨識。例如在公開金鑰基礎架構中，可以此數碼來指明使用的憑證政策及使用的密碼演算法。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "ov", "Organization Validation", "組織驗證", "OV",
        "TLS 憑證簽發過程中，除了識別與鑑別用戶之網域名稱控制權外並且依照憑證的保證等級識別與鑑別用戶之組織身分。故連結安裝組織驗證型 TLS 憑證之網站，可提供 TLS 加密通道，知道該網站之擁有者是誰並確保傳遞資料之完整性。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "pin", "Personal Identification Number", "個人識別碼", "PIN",
        "用於辨識個人身分的數字密碼。",
        None, "HiPKICA CP/CPS v1.1 附錄 1",
    ),
    (
        "pkcs", "Public-Key Cryptography Standard", "公開金鑰密碼學標準", "PKCS",
        "RSA 資訊安全公司旗下的 RSA 實驗室為促進公開金鑰技術的使用，所發展一系列的公開金鑰密碼編譯標準，廣為業界採用。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "pki", "Public Key Infrastructure", "公開金鑰基礎建設", "PKI",
        "由法律、政策、規範、人員、設備、設施、技術、流程、稽核和服務之集合，在廣泛尺度上發展與管理非對稱式密碼學及公鑰憑證。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "qgis", "Qualified Government Information Source", "合格的政府資訊來源", "QGIS",
        "定期更新且現行公眾可取得、為了準確提供可被諮詢且一般被公認為可信賴的資料庫而設計且由政府機關維護，例如經濟部全國商工登記資料庫。資料的報告是根據法律規定，且虛假或誤導性的報告將被處以刑事或民事處罰。CA/Browser Forum 之 Guidelines For The Issuance and Management of Extended Validation Certificates 不禁止使用第三方供應商從政府機關取得的資訊，如果這些第三方供應商是從政府機關直接取得資訊。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "qtis", "Qualified Government Tax Information Source", "合格的政府稅收資訊來源", "QTIS",
        "合格的政府資訊來源，須具體包含與私人組織、其他商業團體或個人相關的稅收資訊。例如我國的財稅資料中心、美國的國稅局（IRS）。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "ra", "Registration Authority", "註冊中心", "RA",
        "（1）負責確認憑證申請者之身分或其他屬性，但不簽發憑證亦不管理憑證。註冊中心是否需為其行為負責及其應負責任之範圍，依所適用之憑證政策或協議訂之。\n（2）一個體，負責對憑證主體做身分識別及鑑別，但不做憑證簽發。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "rfc", "Request for Comments", "徵求修正意見書", "RFC",
        "由網際網路工程任務小組（IETF）發行的一系列備忘錄。包含網際網路、UNIX 和網際網路社群的規範、協定、流程等的標準檔案，以編號排定。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "ssl", "Secure Sockets Layer", "安全插座層", "SSL",
        "由網景公司（Netscape）推出 Web 瀏覽器時所提出的協定，可於傳輸層對網路通信進行加密，並確保傳送資料之完整性以及對於伺服器端與用戶端進行身分鑑別。\n安全插座層協定的優勢在於它與應用層協定獨立無關。高層的應用層協定（例如：HTTP、FTP、Telnet 等）能透通地建立於 SSL 協定之上。SSL 協定在應用層協定通信之前就已經完成加密演算法、通信密鑰的協商以及伺服器認證工作。此協定之繼任者是 TLS（Transport Layer Security）協定。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "tls", "Transport Layer Security", "傳輸層安全", "TLS",
        "由 IETF 將 SSL 3.0 協定制訂為 RFC 2246，並將其稱為 TLS 1.0 協定，後續於 RFC 5246 及 RFC 6176 更新版本，亦即 TLS 1.2 協定。2018 年 IETF 公告最新版本 RFC 8446，即 TLS 1.3 協定。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "ups", "Uninterrupted Power System", "不斷電系統", "UPS",
        "在電力異常（如停電、干擾或電湧）的情況下不間斷地提供負載設備後備電源，以維持諸如伺服器或交換機等關鍵設備或精密儀器的不間斷運作，防止運算數據遺失，通信網路中斷或儀器失去控制。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),

    # ─── 附錄 2 中之名詞（不含縮寫，按英文字母順序）─────────────────────
    (
        "access", "Access", "存取", None,
        "運用系統資源處理資訊的能力。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "access-control", "Access Control", "存取控制", None,
        "對於授權的使用者、程式、程序或其他系統給予資訊系統資源存取權限的處理過程。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "activation-data", "Activation Data", "啟動資料", None,
        "在存取密碼模組時（例如用來開啟私密金鑰以進行簽章或解密），除金鑰外所需及應受保護之隱密資料。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "applicant", "Applicant", "申請者", None,
        "向憑證機構申請憑證，而尚未完成憑證簽發作業程序的用戶。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "archive", "Archive", "歸檔", None,
        "實體上（與主要資料存放處）分隔的長期資料儲存處，可用來支援稽核服務、可用性服務或完整性服務等用途。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "assurance", "Assurance", "保證", None,
        "據以信賴該個體已符合特定安全要件之基礎。[憑證實務作業基準應載明事項準則第 1 章第 2 條第 1 項]",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "assurance-level", "Assurance Level", "保證等級", None,
        "具相對性保證層級中之某 1 級數。[憑證實務作業基準應載明事項準則第 1 章第 2 條第 2 項]",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "audit", "Audit", "稽核", None,
        "評估系統控制的是否恰當、確保符合既定的政策及營運程序、並對現有的控制、政策及程序建議必要的改善而進行的獨立檢閱及調查。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "audit-data", "Audit Data", "稽核紀錄", None,
        "依照發生時間順序之系統活動紀錄，可用以重建或調查事件發生的順序及某個事件中的變化。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "authenticate", "Authenticate", "鑑別", None,
        "（1）驗證某個聲稱的身分是合法的且屬於提出此聲稱者的程序。[A Guide to Understanding Identification and Authentication in Trusted Systems, National Computer Security Center]\n（2）當某個體出示身分時，確認其身分之正確性。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "authentication", "Authentication", "鑑別程序", None,
        "（1）建立使用者或資訊系統身分信賴程度的程序。[NIST.SP.800-63-2 Electronic Authentication Guideline]\n（2）用以建立資料傳送、訊息、來源者之安全措施，或是驗證個人接收特定種類資訊權限之方法。\n（3）鑑別是識別的證明。[A Guide to Understanding Identification and Authentication in Trusted Systems]\n所謂的相互鑑別（Mutual Authentication）是指發生在進行通訊活動的兩方彼此進行鑑別。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "authorization-domain-name", "Authorization Domain Name", "經授權網域名稱", None,
        "用於取得對某一個特定完全吻合網域名稱之憑證簽發的授權之網域名稱。\n憑證機構可使用網域名稱服務別名紀錄查詢服務（DNS CNAME lookup）所回覆之 FQDN 當作 FQDN，用來達到網域驗證的目的。如果 FQDN 包含萬用字元，則憑證機構必須從被請求之 FQDN 的最左邊移除所有萬用字元。憑證機構可從左至右刪除零個或多個標籤（label）直到遇到基礎網域名稱，也可使用任何在這個過程中的值來達到網域驗證的目的。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "backup", "Backup", "備份", None,
        "將資料或程式複製，必要時可供復原之用。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "base-domain-name", "Base Domain Name", "基礎網域名稱", None,
        "申請的完全吻合網域名稱（FQDN）之一部分，是註冊表控制（registry-controlled）或公開字尾（public suffix）左邊第一個網域名稱節點加上註冊表控制或公開字尾（例如「example.co.uk」或「example.com」）。完全吻合網域名稱（FQDN）最右邊之網域名稱節點（domain name node），在其註冊協議（registry agreement）有 ICANN 規格 13（ICANN Specification 13）的通用頂級網域名稱（gTLD），則通用頂級網域名稱本身可以當做基礎網域名稱。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "baseline-requirements", "Baseline Requirements", "基本要求", None,
        "由 CA/Browser Forum 所發行的 The Baseline Requirements for the Issuance and Management of Publicly-Trusted Certificates 以及對這份文件所作的任何修訂。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "binding", "Binding", "連結、繫結", None,
        "將兩個相關的資訊元素做連結（結合）的過程。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "ca-certificate", "CA Certificate", "憑證機構憑證", None,
        "簽發給憑證機構的憑證。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "ca-key-pair", "CA Key Pair", "憑證機構金鑰對", None,
        "其公開金鑰資訊被記載於一個或多個根憑證機構憑證與／或下屬憑證機構憑證之主體公開金鑰欄位的金鑰對。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "certificate", "Certificate", "憑證", None,
        "（1）指載有簽章驗證資料，用以確認簽署人身分、資格之電子形式證明。[電子簽章法第 2 條第 6 款]\n（2）資訊之數位呈現，內容包括：A. 簽發的憑證機構；B. 用戶之名稱或身分；C. 用戶的公開金鑰；D. 憑證之有效期間；E. 憑證機構數位簽章。\n在本文件中所提及的「憑證」特別指其格式為 ITU-T X.509 v.3，且在其「憑證政策」欄位中明確地引用憑證政策物件識別碼的憑證。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "certificate-policy", "Certificate Policy", "憑證政策", "CP",
        "（1）某 1 憑證所適用之對象或情況所列舉之 1 套規則，該對象或情況可為特定之社群或具共同安全需求之應用。[憑證實務作業基準應載明事項準則第 1 章第 2 條第 3 項]\n（2）憑證政策係為透過憑證管理執行的電子交易所訂定之具專門格式的管理政策。憑證政策中包括與數位憑證相關之生成、產製、傳送、稽核、被破解後的復原以及其管理等各項議題。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "certificate-profile", "Certificate Profile", "憑證格式剖繪", None,
        "一組文件或檔案，其根據 Baseline Requirements 的第 7 章定義了對憑證內容與憑證擴充欄位的要求。例如，憑證實務作業基準中的某一章節內容或憑證機構軟體所使用的憑證模板文件。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "certificate-problem-reports", "Certificate Problem Reports", "憑證問題報告", None,
        "疑似金鑰遭破解、憑證遭誤用（misuse）或其他種類的詐騙、破解、濫用或與憑證相關的不當行為之投訴。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "compromise", "Compromise", "破解", None,
        "資訊洩漏給未經授權的人士或違反資訊安全政策造成物件未經授權蓄意、非蓄意的洩漏、修改、毀壞或遺失。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "confidentiality", "Confidentiality", "機密性", None,
        "資訊不會遭受未經授權的個體或程序獲知或取用。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "cross-certificate", "Cross-Certificate", "交互憑證", None,
        "在兩個憑證根憑證機構（Root CA）之間建立信賴關係的一種憑證，屬於一種憑證機構憑證，而非用戶憑證。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "cryptographic-module", "Cryptographic Module", "密碼模組", None,
        "1 組硬體、軟體、韌體或前述的組合，用以執行密碼的邏輯或程序（包含密碼演算法），並且被包含在此模組的密碼邊界之內。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "data-integrity", "Data Integrity", "資料完整性", None,
        "資料未遭受未經授權或意外的更改、破壞或遺失的性質。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "digital-signature", "Digital Signature", "數位簽章", None,
        "將電子文件以數學演算法或其他方式運算為一定長度之數位資料，以簽署人之私密金鑰對其加密，形成電子簽章，並得以公開金鑰加以驗證者。[電子簽章法第 2 條第 3 款]",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "domain-contact", "Domain Contact", "網域名稱聯絡人", None,
        "於網域名稱服務 Start of Authority 紀錄（DNS SOA record）或是基礎網域名稱之 WHOIS 紀錄所列，或透過直接聯絡網域名稱受理註冊機構所得的網域名稱註冊者（Domain Name Registrant）、技術聯絡人（technical contact）、或管理聯絡人（administrative contact）（或是在國碼頂級網域名稱（ccTLD）下對等的人員）。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "domain-name", "Domain Name", "網域名稱", None,
        "在網域名稱系統分配給 1 個節點（node）的標籤（label）。亦即轉換 IP 位址為人類容易記憶之文字名稱。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "domain-name-registrant", "Domain Name Registrant", "網域名稱註冊者", None,
        "有時被稱為網域名稱的擁有者（owner），但更恰當的是表示某人或某實體被網域名稱受理註冊機構（Domain Name Registrar）註冊為具有權利使用該網域名稱，亦即被網域名稱受理註冊機構或 WHOIS 列為「Registrant」之自然人或法人。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "domain-name-registrar", "Domain Name Registrar", "網域名稱受理註冊機構", None,
        "接受以下三類團體贊助、支持或簽署協議：(1) 網際網路名稱和編號註冊中心（the Internet Corporation for Assigned Names and Numbers, ICANN），(2) 國家級網域名稱註冊中心（a national Domain Name authority/registry），或 (3) 網路資訊中心（Network Information Center）及其加盟人、承包商、代表、繼承人或受讓人，受理網域名稱註冊的實體（Entity）或自然人。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "duration", "Duration", "憑證效期", None,
        "由「有效期限起始時間」（notBefore）及「有效期限截止時間」（notAfter）兩個子欄位所組成之憑證欄位。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "end-entity-certificate", "End-Entity Certificate", "終端個體憑證", None,
        "簽發給終端個體的憑證。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "root-ca", "Root CA", "根憑證機構", None,
        "在階層式公開金鑰基礎建設架構中屬於最頂層的憑證機構，其公開金鑰為信賴之起源。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "firewall", "Firewall", "防火牆", None,
        "符合近端（區域）安全政策而對網路之間做接取限制的閘道器。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "high-risk-certificate-request", "High Risk Certificate Request", "高風險憑證請求", None,
        "憑證機構標示參考由憑證機構維護的內部標準和資料庫審查其憑證請求，可包括用於網路釣魚或其他不正當使用之高風險的名稱，包含在先前被拒絕的憑證請求或廢止的憑證、Miller Smiles 網路釣魚列表（Miller Smiles phishing list）或 Google 的安全瀏覽列表（Google Safe Browsing list），或憑證機構使用其本身的風險降低標準識別的名稱。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "identification", "Identification", "識別", None,
        "識別是某使用者是誰（廣為週知）的陳述方式或表達方式。[A Guide to Understanding Identification and Authentication in Trusted Systems]\n識別是指描述或宣稱某個當事人或個體的方式，例如透過使用者帳號、姓名、電子郵件。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "integrity", "Integrity", "完整性", None,
        "對資訊的保護，使其不受未經授權的修改或破壞。資訊從來源產製後，經傳送、儲存到最終被收受方接收的期間中都維持不被篡改的一種狀態。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "ip-reverse-zone-suffix", "IP Reverse Zone Suffix", "IP 反向區域後綴", None,
        "由網域標籤「in-addr.arpa」或「ip6.arpa」所構成之兩個完全吻合網域名稱之一。此兩個完全吻合網域名稱分別作為網際網路協定第 4 版（IPv4）及第 6 版（IPv6）反向對應（Reverse Mapping）命名空間之根節點。其中，「in-addr.arpa」為 IPv4 反向對應命名空間之根節點，「ip6.arpa」則為 IPv6 反向對應命名空間之根節點。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "issuing-ca", "Issuing CA", "簽發憑證機構", None,
        "對於 1 張憑證而言，簽發該憑證的憑證機構即稱為該憑證的簽發憑證機構。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "key-escrow", "Key Escrow", "金鑰託管", None,
        "將用戶的私密金鑰及依據用戶必須遵守的託管協議（或類似的契約）所規定的相關資訊進行存放，此託管協議的條款要求 1 個或 1 個以上的代理機構基於有益於用戶、雇主或另一方的前提下，依據協議的規定，擁有用戶的金鑰。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "key-exchange", "Key Exchange", "金鑰交換", None,
        "交換彼此金鑰以建立安全通訊的處理過程。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "key-pair", "Key Pair", "金鑰對", None,
        "兩把數學上有相關性的金鑰，具有下列特性：\n（1）其中 1 把金鑰用來做訊息加密，而此加密訊息只有用成配對關係的另 1 把金鑰可以解密。\n（2）從其中 1 把金鑰要推出另 1 把金鑰（從計算的角度而言）是不可行的。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "linting", "Linting", "Linting", None,
        "用以檢查數位簽章資料（例如預簽憑證 [RFC 6962]、憑證、憑證廢止清冊或 OCSP response）或待簽章資料物件（例如 tbsCertificate（參考 RFC 5280 第 4.1.1.1 節））的內容是否符合這些要求中定義的剖繪和要求的流程。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "non-repudiation", "Non-Repudiation", "不可否認性", None,
        "對資料傳送方提供傳送證明以及對資料收受方提供傳送方的身分之保證，因而兩方在事後皆無法否認曾經處理過此項資料。技術上的不可否認性是指對信任者（信任之一方）而言，如果某個公開金鑰可用以驗核某個數位簽章，保證此簽章必定是由相對應的私密金鑰所簽署。在法律上，不可否認性是指建立私密簽章金鑰之擁有或控管機制。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "ocsp-responder", "OCSP Responder", "線上憑證狀態協定回應伺服器", None,
        "由憑證管理中心所授權維運的線上伺服器，並連接至其儲存庫以處理憑證狀態查詢請求。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "ocsp-stapling", "OCSP Stapling", "線上憑證狀態協定裝訂", None,
        "一種 TLS 憑證狀態請求擴展欄位（TLS Certificate Status Request extension），可替代線上憑證狀態協定（OCSP）成為另一種檢查 X.509 憑證狀態的方法。\n本方法在運作上，網站會事先向 OCSP 回應伺服器取得有「時間限制（例如兩小時）」的 OCSP Response 並暫存；接下來，在每一次的 TLS Handshake 的初始過程中，網站會將此暫存的 OCSP Response 傳送給用戶（通常為瀏覽器），用戶只需驗證該 OCSP Response 的有效性而不用再向 CA 發送 OCSP 請求，如此可避免用戶每次連結高流量 TLS 網站都需要向 CA 詢問其 TLS 憑證狀態，因此減輕 CA 的負擔。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "out-of-band", "Out-of-Band", "特殊安全管道", None,
        "不同於一般的傳送訊息管道的傳送方式。例如使用電子線上傳送的情形，可稱使用實體的掛號信為特殊安全管道。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "persistent-dcv-txt-record", "Persistent DCV TXT Record", "持久性網域控管權 TXT 紀錄", None,
        "依據 Baseline Requirements 第 3.2.2.4.22 節，用於識別申請者之 DNS TXT 紀錄。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "private-key", "Private Key", "私密金鑰", None,
        "（1）在簽章金鑰對中，用以產生數位簽章的金鑰。\n（2）在加解密金鑰對中，用以對機密資訊解密的金鑰。\n在這兩種情境中，此金鑰皆須保密。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "public-key", "Public Key", "公開金鑰", None,
        "（1）在簽章金鑰對中，用以驗證數位簽章有效的金鑰。\n（2）在加解密金鑰對中，用以對機密資訊加密的金鑰。\n在這兩種情境中，此金鑰皆須（一般以數位憑證的形式）公開可得。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "qualified-auditor", "Qualified Auditor", "合格稽核業者", None,
        "符合基本要求（Baseline Requirements）第 8.2 節規定之稽核資格要求，且與受稽方獨立的會計師事務所、法人或個人。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "random-value", "Random Value", "隨機值", None,
        "由憑證機構所指定提供給申請者具備至少 112 位元之亂度（熵，Entropy）的數值。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "re-key", "Re-key (a certificate)", "金鑰更換", None,
        "改變在密碼系統應用程式中所使用之金鑰之值。通常必須藉由對新的公開金鑰簽發新的憑證來達成。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "relying-party", "Relying Party", "信賴憑證者", None,
        "（1）信賴所收受之憑證及可用憑證中所載之公開金鑰加以驗證之數位簽章者，或信賴憑證中所命名主體之身分（或其他屬性）及憑證所載公開金鑰之對應關係者。[憑證實務作業基準應載明事項準則第 1 章第 2 條第 6 項]\n（2）個人或機構收到包含憑證及數位簽章（此數位簽章可藉由憑證上所列之公開金鑰做驗證）之資訊，並且可能信賴這些資訊。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "repository", "Repository", "儲存庫", None,
        "（1）用以儲存與檢索憑證或其他憑證相關資訊之可信賴系統（Trustworthy System）。[憑證實務作業基準應載明事項準則第 1 章第 2 條第 7 項]\n（2）包含本文件與憑證相關資訊的資料庫。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "request-token", "Request Token", "請求符記", None,
        "由憑證機構指定之方式所導出之數值，繫結（bind）對於憑證請求之控制的展現。請求符記應結合用於憑證請求之公開金鑰；可包含時戳以指出何時產製、可包含其他資訊以確保其唯一性。包含時戳的請求符記應從產製的時間開始後 30 天之內有效；時戳在未來則應視為無效。沒有包含時戳的請求符記針對單一一次使用有效，憑證機構不應該在隨後的驗證重覆使用該請求符記。此繫結至少要使用與簽章憑證請求檔強度相同之數位簽章演算法或密碼學雜湊函數演算法。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "required-website-content", "Required Website Content", "所要求的網站內容", None,
        "隨機值或請求符記其中之一，加上由憑證機構指定可唯一識別用戶之額外資訊。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "reserved-ip-addresses", "Reserved IP Addresses", "保留 IP 位址", None,
        "IANA 設定為保留的 IPv4 或 IPv6 位址，參見：\nhttp://www.iana.org/assignments/ipv4-address-space/ipv4-address-space.xml\nhttp://www.iana.org/assignments/ipv6-address-space/ipv6-address-space.xml",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "revoke-a-certificate", "Revoke a Certificate", "憑證廢止", None,
        "在憑證的有效期間內，提前終止憑證的運作。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "subordinate-ca", "Subordinate CA", "下屬憑證機構", None,
        "在階層架構的公開金鑰基礎建設中，憑證由另 1 個憑證機構所簽發，且其活動受限於此另 1 憑證機構的憑證機構。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "subscriber", "Subscriber", "用戶", None,
        "具下列特性之個體，包括（但不限於）個人、機構、應用程式或網路裝置：\n（a）憑證中所載明之主體；\n（b）擁有與憑證上所列公開金鑰相對應之私密金鑰；\n（c）本身不簽發憑證給其他方。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "technical-non-repudiation", "Technical Non-Repudiation", "技術上的不可否認性", None,
        "公開金鑰機制所提供的技術性證據以支援不可否認之安全服務。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "threat", "Threat", "威脅", None,
        "對資訊系統可能造成損害（包括損毀、揭露、惡意修改資料或拒絕服務）的任何狀況或事件。可分為內部威脅（Inside Threat）與外部威脅（Outside Threat）。內部威脅是指利用授與之權限，可能透過資料的破壞、揭露、篡改或拒絕服務等方式造成對資訊系統的損害。外部威脅是指來自外部未經授權，且對資訊系統具有潛在破壞能力（包括對資料的毀壞、篡改、洩漏，或是造成阻斷服務）的個體。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "time-stamp", "Time-stamp", "時戳", None,
        "由可信賴的權威機構以數位方式簽署，證明某特定數位物件在某特別時間之存在。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "top-level-domain", "Top-Level Domain", "頂級網域名稱", None,
        "依據 RFC 8499（https://tools.ietf.org/html/rfc8499）之定義，頂級網域名稱係指位於根網域下一層之區域，例如「com」或「jp」。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "trust-list", "Trust List", "信賴清單", None,
        "可信賴憑證之清單，信賴憑證者用以鑑別憑證。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "trusted-certificate", "Trusted Certificate", "可信賴憑證", None,
        "為信賴憑證者所信賴且經由安全可靠之傳送方式取得的憑證。此類憑證中所包含的公開金鑰用於信賴路徑之起始，又稱為信賴起源。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "trustworthy-system", "Trustworthy System", "可信賴系統", None,
        "具有下列性質之電腦硬體、軟體及程序：\n（1）對於入侵及誤用有相當的保護功能。\n（2）提供合理的可用性、可靠度及正確操作。\n（3）適當地執行預定功能。\n（4）與一般為人所接受的安全程序一致。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "validation", "Validation", "驗證", None,
        "憑證申請者的識別流程。驗證是識別（identification）的子集合，是指建立憑證申請者的身分背景之識別。[RFC 3647]",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "whois", "WHOIS", "WHOIS", None,
        "透過 RFC 3912 的 WHOIS、RFC 7482 的 RDAP（Registry Data Access Protocol）或 HTTPS 網站，向網域名稱受理註冊機構或註冊管理機構（Registry）直接擷取的資訊。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
    (
        "zeroize", "Zeroize", "零值化", None,
        "清除電子式儲存資料之方法，藉由改變資料儲存以防止資料被復原。",
        None, "HiPKICA CP/CPS v1.1 附錄 2",
    ),
]


def yaml_block_scalar(text: str, indent: int = 2) -> str:
    """以 YAML literal block (|) 編碼多行字串。"""
    pad = " " * indent
    lines = text.split("\n")
    return "|\n" + "\n".join(pad + ln for ln in lines)


def yaml_quoted(text: str) -> str:
    """單行：用雙引號並 escape 反斜線與雙引號。"""
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render(text: str) -> str:
    return yaml_block_scalar(text) if "\n" in text else yaml_quoted(text)


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "src" / "content" / "glossary"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 先清掉舊內容（避免殘留之前手動加的檔案造成 slug 衝突）
    for existing in out_dir.glob("*.md"):
        existing.unlink()

    slugs_seen: set[str] = set()
    for slug, term_en, term_zh, abbr, definition, first_seen, source in ENTRIES:
        if slug in slugs_seen:
            raise SystemExit(f"duplicate slug: {slug}")
        slugs_seen.add(slug)

        lines = ["---"]
        lines.append(f"term_en: {render(term_en)}")
        lines.append(f"term_zh: {render(term_zh)}")
        if abbr:
            lines.append(f"abbreviation: {render(abbr)}")
        lines.append(f"definition: {render(definition)}")
        if first_seen:
            lines.append(f"first_seen_at: {render(first_seen)}")
        if source:
            lines.append(f"source: {render(source)}")
        lines.append("---")
        lines.append("")

        (out_dir / f"{slug}.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"wrote {len(ENTRIES)} entries to {out_dir}")


if __name__ == "__main__":
    main()
