"""一次性：將第 3 章（含）以後章節的譯名對齊 §1.6.1／§1.6.2 定版。

依 scripts/lint_term_consistency.py 偵測 + 人工核對結果，逐一替換分歧譯名。
只動 chapter >= 3 的檔（含附錄）；ch1/ch2（含定版 1-6-1/1-6-2）不動。

GLOBAL：變體字串夠獨特，全域替換（含 bare 與標註形式、標題）。
RESTRICTED：變體為常用詞（資料庫=database），僅替換「變體（English）」標註形式。
"""
import pathlib
import re

BR = pathlib.Path(__file__).resolve().parent.parent / "src" / "content" / "br"

GLOBAL = [
    ("主體身分資訊", "主體識別資訊"),                      # Subject Identity Information
    ("交互憑證之下屬憑證機構憑證", "交互認證之下屬憑證機構憑證"),  # Cross-Certified Subordinate CA Certificate
    ("受技術約束下屬憑證機構憑證", "受技術約束的下屬憑證機構憑證"),  # Technically Constrained Sub CA Cert（補「的」）
    ("合格稽核機構", "合格稽核業者"),                      # Qualified Auditor
    ("合格稽核人", "合格稽核業者"),                        # Qualified Auditor（無「合格稽核人員」之虞）
    ("基底網域名稱", "基礎網域名稱"),                      # Base Domain Name
    ("憑證問題回報", "憑證問題報告"),                      # Certificate Problem Report
    ("憑證管理程序", "憑證管理流程"),                      # Certificate Management Process
    ("用戶合約", "用戶協議"),                              # Subscriber Agreement
    ("短期用戶憑證", "短效期用戶憑證"),                    # Short-lived Subscriber Certificate
    ("金鑰產生腳本", "金鑰產製腳本"),                      # Key Generation Script
    ("金鑰洩漏", "金鑰破解"),                              # Key Compromise（含 私密金鑰洩漏→私密金鑰破解、標題）
    ("預備憑證", "預簽憑證"),                              # Precertificate
    ("高風險憑證請求", "高風險憑證申請"),                  # High Risk Certificate Request
    ("可信賴資料來源", "可靠資料來源"),                    # Reliable Data Source
]

RESTRICTED = [
    ("資料庫（Repository）", "儲存庫（Repository）"),       # Repository（其他「資料庫」為 database，不動）
]


def chapter_of(path):
    name = path.stem
    if name.startswith("appendix"):
        return 99
    head = name.split("-")[0]
    return int(head) if head.isdigit() else -1


def main():
    total_files = 0
    total_subs = 0
    per_pair = {old: 0 for old, _ in GLOBAL + RESTRICTED}
    for path in sorted(BR.glob("*.md")):
        if chapter_of(path) < 3:
            continue
        text = path.read_text(encoding="utf-8")
        orig = text
        file_subs = 0
        for old, new in GLOBAL:
            n = text.count(old)
            if n:
                text = text.replace(old, new)
                per_pair[old] += n
                file_subs += n
        for old, new in RESTRICTED:
            n = text.count(old)
            if n:
                text = text.replace(old, new)
                per_pair[old] += n
                file_subs += n
        if text != orig:
            path.write_text(text, encoding="utf-8")
            total_files += 1
            total_subs += file_subs
            print(f"  {path.name:18} {file_subs} 處")

    print("\n各術語替換次數：")
    for old, new in GLOBAL + RESTRICTED:
        if per_pair[old]:
            print(f"  {old} → {new}: {per_pair[old]}")
    print(f"\n共 {total_subs} 處 / {total_files} 檔")


if __name__ == "__main__":
    main()
