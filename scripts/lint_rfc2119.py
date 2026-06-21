"""RFC 2119 加粗對照 lint。

對每個 src/content/br/*.md：
  - 英文側：英文 blockquote 行（以 `>` 起始）中「全大寫 RFC 2119 關鍵字」出現次數
  - 中文側：非 blockquote 行中「（關鍵字）」加粗標註（如 **得（MAY）**）出現次數

若中文標註數 > 英文關鍵字數 → 疑似「原文無大寫關鍵字、譯稿誤判」(over-bold)。
反向（英文有、中文未標）→ 疑似漏標 (under-bold)，附帶列出。

只做機械對照，最終仍須人工逐處確認（英文片段或有改寫、引號內舉例等例外）。
"""
import pathlib
import re
import sys

BR_DIR = pathlib.Path(__file__).resolve().parent.parent / "src" / "content" / "br"

# 中文標註 token（括號內字串）→ 對應英文計數 regex（case-sensitive）
# 順序：長片語在前，避免子字串重複計數
KEYWORDS = [
    ("MUST NOT",        r"\bMUST NOT\b"),
    ("SHALL NOT",       r"\bSHALL NOT\b"),
    ("SHOULD NOT",      r"\bSHOULD NOT\b"),
    ("NOT RECOMMENDED", r"\bNOT RECOMMENDED\b"),
    ("NOT REQUIRED",    r"\bNOT REQUIRED\b"),
    ("MUST",            r"\bMUST\b(?! NOT)"),
    ("SHALL",           r"\bSHALL\b(?! NOT)"),
    ("SHOULD",          r"\bSHOULD\b(?! NOT)"),
    # 含大寫動詞形 RECOMMENDS／RECOMMEND（BR 常用 "This Profile RECOMMENDS that…"）
    ("RECOMMENDED",     r"(?<!NOT )\bRECOMMEND(?:ED|S)?\b"),
    ("REQUIRED",        r"(?<!NOT )\bREQUIRED\b"),
    ("MAY",             r"\bMAY\b"),
    ("OPTIONAL",        r"\bOPTIONAL\b"),
]

# 中文標註：（KEYWORD），全形括號
CN_PATTERNS = {kw: re.compile(r"（" + re.escape(kw) + r"）") for kw, _ in KEYWORDS}
EN_PATTERNS = {kw: re.compile(rgx) for kw, rgx in KEYWORDS}


def split_lines(text):
    """回傳 (english_text, chinese_text)。英文 = blockquote 行；中文 = 其餘。"""
    en, cn = [], []
    in_frontmatter = False
    for i, line in enumerate(text.splitlines()):
        if i == 0 and line.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
            continue
        if line.lstrip().startswith(">"):
            en.append(line)
        elif re.match(r"^\[\^[^\]]+\]:", line):
            # 譯者註腳定義行：無英文 blockquote 對照（註腳本身來自 BR.md footnote），
            # 跳過以免 EN=0 的假誤報（如 7-1-2-10-7 [^ocsp_signing] 對應 BR.md MUST NOT）
            continue
        else:
            cn.append(line)
    return "\n".join(en), "\n".join(cn)


def count_en(en_text):
    counts = {}
    remaining = en_text
    # 為避免長片語的子字串被短 regex 重複計數，先把已計數片語遮蔽
    for kw, _ in KEYWORDS:
        pat = EN_PATTERNS[kw]
        found = pat.findall(remaining)
        counts[kw] = len(found)
        # 把已配對的長片語從文本移除（用空白替換等長），避免 MUST 計到 MUST NOT 的 MUST
        if " " in kw:  # 長片語
            remaining = pat.sub(lambda m: " " * len(m.group(0)), remaining)
    return counts


def count_cn(cn_text):
    return {kw: len(CN_PATTERNS[kw].findall(cn_text)) for kw, _ in KEYWORDS}


def main():
    over = []   # (file, kw, cn, en)  中文 > 英文 = 疑似誤判
    under = []  # (file, kw, cn, en)  英文 > 中文 = 疑似漏標
    for path in sorted(BR_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        en_text, cn_text = split_lines(text)
        en_counts = count_en(en_text)
        cn_counts = count_cn(cn_text)
        for kw, _ in KEYWORDS:
            c, e = cn_counts[kw], en_counts[kw]
            if c > e:
                over.append((path.name, kw, c, e))
            elif e > c:
                under.append((path.name, kw, c, e))

    print("=" * 70)
    print("疑似誤判（中文標註 > 英文大寫關鍵字）— over-bold")
    print("=" * 70)
    if not over:
        print("（無）")
    for f, kw, c, e in over:
        print(f"  {f:18}  {kw:16}  中文標註 {c}  英文大寫 {e}")

    print()
    print("=" * 70)
    print("疑似漏標（英文大寫關鍵字 > 中文標註）— under-bold（參考）")
    print("=" * 70)
    if not under:
        print("（無）")
    for f, kw, c, e in under:
        print(f"  {f:18}  {kw:16}  中文標註 {c}  英文大寫 {e}")

    print()
    print(f"over-bold {len(over)} 處 / under-bold {len(under)} 處")
    return 0


if __name__ == "__main__":
    sys.exit(main())
