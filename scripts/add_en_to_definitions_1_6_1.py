# -*- coding: utf-8 -*-
"""一次性：把 §1.6.1（src/content/br/1-6-1.md）由「**英文詞（中譯）**：中文釋義」
改成標準 Style A：每條定義上方加 BR.md 英文原文 blockquote，中文行的粗體改為中譯。

- 英文原文取自 upstream/BR.md 的 ### 1.6.1 Definitions 區（行 280–531）。
- BR 區塊以 `^\\*\\*<ASCII 開頭的詞>\\*\\*:` 為界，多行／多段定義一併納入；
  其中 `**Note**:` 不視為新詞（屬 Request Token 內文）。
- 中文單元以 `^\\*\\*<ASCII 開頭>\\*\\*：` 為界（全形冒號）；`**註**` 為 CJK 開頭，
  自然留在所屬單元內。
- 中譯粗體：取原括號內文；若括號內為「中文，ACRONYM」則轉成「中文（ACRONYM）」；
  無括號者（Linting / WHOIS / P-Label / XN-Label / Requirements）保留原英文粗體。
"""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BR = ROOT / "upstream" / "BR.md"
TARGET = ROOT / "src" / "content" / "br" / "1-6-1.md"

DEF_START, DEF_END = 280, 531  # BR.md 行號（1-based），含頭尾
HEADER_RE = re.compile(r"^\*\*([A-Za-z][^*]*?)\*\*:")          # BR 英文詞
CN_HEADER_RE = re.compile(r"^\*\*([A-Za-z][^*]*?)\*\*：(.*)$")  # 中文單元首行

# 英文詞別名：中文檔的英文寫法 → BR.md 的英文寫法
ALIASES = {
    "Registration Authority, RA": "Registration Authority (RA)",
}


def load_br_blocks():
    lines = BR.read_text(encoding="utf-8").splitlines()
    section = lines[DEF_START - 1 : DEF_END]  # 0-based slice
    blocks = {}
    cur_term = None
    cur_lines = []

    def flush():
        if cur_term is not None:
            # 去尾端空行
            block = cur_lines[:]
            while block and block[-1].strip() == "":
                block.pop()
            blocks[cur_term] = block

    for ln in section:
        m = HEADER_RE.match(ln)
        if m and m.group(1).strip() != "Note":
            flush()
            cur_term = m.group(1).strip()
            cur_lines = [ln]
        else:
            if cur_term is not None:
                cur_lines.append(ln)
    flush()
    return blocks


def to_blockquote(block):
    out = []
    for ln in block:
        out.append(">" if ln.strip() == "" else "> " + ln)
    return out


def cn_bold(en_bold_raw):
    """由中文檔原粗體（如 'Affiliate（關係企業）'）算出新的中文粗體。"""
    m = re.match(r"^(.*?)（(.+)）$", en_bold_raw)
    if not m:
        return en_bold_raw  # 無括號 → 維持英文（Linting / WHOIS / Requirements…）
    inner = m.group(2)
    # 「中文，ACRONYM」→「中文（ACRONYM）」
    m2 = re.match(r"^(.+)，([A-Z][A-Za-z0-9\-]*)$", inner)
    if m2:
        return f"{m2.group(1)}（{m2.group(2)}）"
    return inner


def en_term_for_lookup(en_bold_raw):
    base = en_bold_raw.split("（")[0].strip()
    return ALIASES.get(base, base)


def main():
    br_blocks = load_br_blocks()
    text = TARGET.read_text(encoding="utf-8").splitlines()

    # 找出 frontmatter 與 preamble（第一個中文單元之前）的界線
    first_unit = next(i for i, ln in enumerate(text) if CN_HEADER_RE.match(ln))
    head = text[:first_unit]
    body = text[first_unit:]

    # 切單元
    units = []
    cur = []
    for ln in body:
        if CN_HEADER_RE.match(ln):
            if cur:
                units.append(cur)
            cur = [ln]
        else:
            cur.append(ln)
    if cur:
        units.append(cur)

    out = list(head)
    missing = []
    for unit in units:
        # 去單元尾端空行
        while unit and unit[-1].strip() == "":
            unit.pop()
        m = CN_HEADER_RE.match(unit[0])
        en_bold_raw, rest = m.group(1).strip(), m.group(2)
        term = en_term_for_lookup(en_bold_raw)
        block = br_blocks.get(term)
        if block is None:
            missing.append((en_bold_raw, term))
        else:
            out += to_blockquote(block)
            out.append("")
        # 改寫中文首行粗體
        unit[0] = f"**{cn_bold(en_bold_raw)}**：{rest}"
        out += unit
        out.append("")

    # 收尾：移除多餘結尾空行，保留單一換行
    while out and out[-1].strip() == "":
        out.pop()
    TARGET.write_text("\n".join(out) + "\n", encoding="utf-8")

    print(f"BR blocks: {len(br_blocks)}  CN units: {len(units)}")
    if missing:
        print("UNMATCHED:")
        for raw, term in missing:
            print(f"  - bold='{raw}'  lookup='{term}'")
    else:
        print("All units matched.")


if __name__ == "__main__":
    main()
