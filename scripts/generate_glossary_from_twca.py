"""
一次性匯入腳本：依 TWCA Global CPS v3.1 附錄一（詞彙 Glossary）
補入 HiPKICA 未涵蓋的詞條到 src/content/glossary/*.md。

執行：
    python scripts/generate_glossary_from_twca.py

只新增；不覆寫已存在的檔案（避免動到 HiPKICA 來源的譯名）。
每筆 entry 標註 source: 'TWCA Global CPS v3.1 附錄一'。
"""
from __future__ import annotations
from pathlib import Path

# (slug, term_en, term_zh, abbreviation, definition)
ENTRIES: list[tuple[str, str, str, str | None, str]] = [
    (
        "internet", "Internet", "網際網路", None,
        "許多不同的電腦網路相互連結，經過標準的通訊協定，得以相互交換資訊。",
    ),
    (
        "electronic-message", "Electronic Message", "（電子）訊息", None,
        "指文字、聲音、影像、符號或其他資料，以電子、磁性或人之知覺無法直接認識之方式，所製成足以表示其用意之紀錄，而供電子處理之用者。",
    ),
    (
        "rsa-algorithm", "RSA Algorithm", "RSA 演算法", "RSA",
        "一種非對稱加密演算法，由 Ron Rivest、Adi Shamir 和 Leonard Adleman 於 1977 年提出，其安全強度建構於針對大數做質因數分解的困難性上。",
    ),
    (
        "ecc", "Elliptic Curve Cryptography", "橢圓曲線密碼學", "ECC",
        "一種基於橢圓曲線數學的公開密鑰加密演算法，由 Neal Koblitz 和 Victor Miller 於 1985 年提出，其安全強度建構於解決橢圓曲線離散對數問題的困難性上。",
    ),
    (
        "ecc-p256-curve", "ECC P-256 Curve", "ECC P-256 曲線", None,
        "由 NIST 於 FIPS 186-3 中所制定之橢圓曲線標準，其定義了橢圓曲線之相關參數 p, a, b, G, n, h，其中曲線之基點 G 的 x、y 座標長度分別為 256 bits。",
    ),
    (
        "electronic-signature", "Electronic Signature", "電子簽章", None,
        "指以電子型式存在之資料訊息，依附在電子文件可用以辨識及確認電子文件簽署人身分及簽署人以數位、聲音、指紋、或其他生物光學技術的特性產生的訊息，其依附在電子訊息上，具有與簽名同等的效力，可用以辨識及確認電子文件簽署人的身分，及辨識簽署訊息的完整性。",
    ),
    (
        "encrypt", "Encrypt", "加密", None,
        "指利用數學演算法或其他方法，將電子文件以亂碼方式處理，以確保資料傳輸的安全。",
    ),
    (
        "decrypt", "Decrypt", "解密", None,
        "將經加密後形成人無法辨識其代表意義的訊息，以相關的數學演算法或其他方法將該訊息還原為人可以辨識其代表意義的訊息。",
    ),
    (
        "asymmetric-cryptosystem", "Asymmetric Cryptosystem", "非對稱型密碼演算法", None,
        "以電腦為媒介基礎的一種數學演算法，可以產生及使用一組數學運算上相關連的安全金鑰對。其中私密金鑰用以對訊息作簽章，對應的公開金鑰則用以對簽章後的訊息作驗證；公開金鑰亦可用以對訊息作加密，而對應的私密金鑰則用以對加密後的訊息作解密。",
    ),
    (
        "hash-function", "Hash Function", "雜湊函數", None,
        "一種可以將一長串的位元訊息轉換成固定長度位元訊息的數學演算法。相同的訊息輸入經由壓縮函數運算產生輸出結果必定相同，且決無法由輸出產生的結果推算出輸入的訊息。",
    ),
    (
        "acme", "Automated Certificate Management Environment", "自動憑證更新環境", "ACME",
        "一種通訊協議，用於自動化執行憑證機構（CA）與其用戶端 Web 伺服器之間的憑證相關管理作業（例如憑證申請），允許用戶以極低的成本自動化部署公鑰基礎設施。該協議主要透過 HTTPS 傳輸格式化之 JSON 訊息，相關標準定義於 RFC 8555 中。",
    ),
    (
        "csr", "Certificate Signing Request", "憑證簽名請求", "CSR",
        "一種經過編碼的檔案，讓憑證申請者透過標準化的方式，把公開金鑰、憑證相關資訊（例如網域名稱）傳給憑證機構進行憑證簽發。該檔案可具體證明申請者為私密金鑰之擁有者。",
    ),
    (
        "issue-a-certificate", "Issue a Certificate", "簽發憑證", None,
        "係指認證中心（憑證機構）依憑證實務作業基準，審驗公開金鑰憑證申請人之身分資格、相關文件，並驗證其公開金鑰及私密金鑰之配對關係後，簽發公開金鑰憑證或其他憑證。",
    ),
    (
        "psl", "Public Suffix List", "公用後綴列表", "PSL",
        "由 Mozilla 創建的公共資源，列表位於 https://publicsuffix.org/，該列表由兩部分組成：一部分是由 ICANN 提供的 TLD（Top Level Domain，頂級域名）列表，一部分是由個人或機構提供的 PRIVATE 列表。",
    ),
    (
        "mrsp", "Mozilla Root Store Policy", "Mozilla 根儲存庫政策", "MRSP",
        "由 Mozilla 組織為其 Firefox 網頁瀏覽器和其他相關產品定義的一套規定和準則。該政策旨在確保 Mozilla 瀏覽器信任的根憑證機構（CA）遵守一系列標準和最佳實踐，以保障使用者的安全和隱私。",
    ),
    (
        "bugzilla", "Bugzilla", "Bugzilla", None,
        "由 Mozilla 維護之瀏覽器問題的追蹤管理網路程式，當 CA 發生重大缺失時，必須回報於此處。位於 https://bugzilla.mozilla.org/home。",
    ),
    (
        "smime", "Secure Multipurpose Internet Mail Extensions", "安全的多用途 Internet 郵件擴充", "S/MIME",
        "一種 Internet 標準，它在安全方面對 MIME 協定進行了擴充，可以將 MIME 實體（比如數位簽章和加密資訊等）封裝成安全物件，為電子郵件應用增添了訊息真實性、完整性和保密性服務。依 S/MIME BR 之定義，S/MIME 憑證有四種不同類型，分別為 Mailbox-validated、Organization-validated、Sponsor-validated、Individual-validated，每種類型皆有 legacy、multipurpose、strict 三種剖繪，各類型及剖繪差異可參考 S/MIME BR（https://cabforum.org/smime-br）。",
    ),
    (
        "mpic", "Multi-Perspective Issuance Corroboration", "多視角驗證", "MPIC",
        "多視角驗證要求 CA 在核發憑證前，必須由多個地理位置分散的驗證節點交叉確認 DNS 記錄與網域驗證結果是否一致，以降低因 BGP 劫持、DNS 汙染或區域性網路攻擊所導致的錯誤驗證風險。在 MPIC 架構中，驗證流程包含兩種視角：主視角驗證（Primary Perspective）由 CA 的主要驗證節點執行，負責取得 DNS、CAA、HTTP-01 或 TLS-ALPN-01 等基礎驗證資料，作為後續比對的基準；遠端視角驗證（Remote Perspective）由分布於不同地理區域、不同網路路徑的節點執行，必須能取得與主視角一致的驗證資訊。CA 只有在主視角與所有遠端視角均取得一致結果時，方可視該網域驗證為有效。",
    ),
]

SOURCE = "TWCA Global CPS v3.1 附錄一"


def yaml_escape(s: str) -> str:
    # 內含雙引號改用 YAML literal block
    return s.replace("\\", "\\\\").replace('"', '\\"')


def write_entry(slug: str, term_en: str, term_zh: str, abbr: str | None, definition: str) -> bool:
    path = Path("src/content/glossary") / f"{slug}.md"
    if path.exists():
        print(f"skip (exists): {slug}")
        return False
    lines = [
        "---",
        f'term_en: "{yaml_escape(term_en)}"',
        f'term_zh: "{yaml_escape(term_zh)}"',
    ]
    if abbr:
        lines.append(f'abbreviation: "{yaml_escape(abbr)}"')
    lines.append(f'definition: "{yaml_escape(definition)}"')
    lines.append(f'source: "{SOURCE}"')
    lines.append("---")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote: {slug}")
    return True


def main() -> None:
    wrote = 0
    for entry in ENTRIES:
        if write_entry(*entry):
            wrote += 1
    print(f"\ntotal: {wrote} new entries (skipped {len(ENTRIES) - wrote})")


if __name__ == "__main__":
    main()
