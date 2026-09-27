#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產出缺漏英文引用的修正工作清單。

對每個目標檔的每個缺漏 BR.md 散文單元，輸出：
  - 完整英文原文
  - 中文是否已存在於譯稿（用語言不變 token：反引號識別碼 / 章節號 / OID 判斷）
    type-1 = 中文在、只缺英文；type-2 = 中英都缺。
排除：1-6-1（定義）、7-1-6-1（OID）、appendix-*（已雙語）、footnote 行。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BR_MD = ROOT / "upstream" / "BR.md"
BR_DIR = ROOT / "src" / "content" / "br"
HEADING_RE = re.compile(r"^#{1,6}\s+(\d+(?:\.\d+)*|Appendix\s+[A-Z])\b\s*(.*)$")

EXCLUDE_FILES = {"1-6-1.md", "7-1-6-1.md", "appendix-a.md", "appendix-b.md"}


def split_blocks(lines):
    blocks, cur = [], []
    for line in lines:
        if line.strip() == "":
            if cur:
                blocks.append(cur); cur = []
        else:
            cur.append(line)
    if cur:
        blocks.append(cur)
    return blocks


def is_prose(bl):
    text = " ".join(bl).strip()
    if "|" in text:                       # 表格（已雙語處理）
        return False
    first = bl[0].lstrip()
    if re.match(r"^Table:", first):       # pandoc caption
        return False
    if first.startswith("```"):           # code fence（語言中性）
        return False
    if re.match(r"\s*\[\^", first):       # footnote 定義（譯者註）
        return False
    if not re.search(r"[A-Za-z]", text):  # 無英文（如 OID 行）
        return False
    return True  # 含散文、note、清單


def invariants(text):
    """語言不變 token：反引號識別碼、章節號、OID、ISO 號等。"""
    toks = set(re.findall(r"`([^`]+)`", text))
    toks |= set(re.findall(r"\b\d+(?:\.\d+)+\b", text))
    toks |= set(re.findall(r"\b\d{3,5}\b", text))  # RFC 號、ISO 號
    return {t.lower() for t in toks if len(t) >= 2}


def norm_cmp(s):
    s = re.sub(r"(?m)^\s*>\s?", "", s)
    s = re.sub(r"\]\([^)]*\)", "]", s)
    s = re.sub(r"[^0-9A-Za-z一-鿿]+", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def parse_br_sections():
    sections, cur_id, cur = {}, None, []
    for line in BR_MD.read_text(encoding="utf-8").split("\n"):
        m = HEADING_RE.match(line)
        if m:
            if cur_id:
                sections[cur_id] = cur
            cur_id = m.group(1).replace("Appendix ", "appendix-").lower()
            cur = []
        elif cur_id:
            cur.append(line)
    if cur_id:
        sections[cur_id] = cur
    out = {}
    for sid, lines in sections.items():
        units = []
        for b in split_blocks(lines):
            if is_prose(b):
                units.append("\n".join(b))
        out[sid] = units
    return out


def main():
    br = parse_br_sections()
    out_lines = []
    type1 = type2 = 0
    for path in sorted(BR_DIR.glob("*.md")):
        if path.name in EXCLUDE_FILES:
            continue
        text = path.read_text(encoding="utf-8")
        m = re.search(r'^section_id:\s*"?([^"\n]+)"?', text, re.MULTILINE)
        if not m:
            continue
        sid = m.group(1).strip()
        if sid not in br:
            continue
        body = text.split("---", 2)[-1]
        bq = norm_cmp("\n".join(l for l in body.split("\n") if l.lstrip().startswith(">")))
        cn = norm_cmp("\n".join(l for l in body.split("\n") if not l.lstrip().startswith(">")))
        misses = []
        for unit in br[sid]:
            key = norm_cmp(unit)[:45]
            if key and key not in bq:
                # 排除 footnote
                if re.match(r"\s*\[\^", unit):
                    continue
                inv = invariants(unit)
                cn_has = bool(inv) and all(tok.lower() in cn for tok in inv) if inv else None
                misses.append((unit, inv, cn_has))
        if not misses:
            continue
        out_lines.append(f"\n========== {path.name}  (§{sid}) ==========")
        for unit, inv, cn_has in misses:
            kind = "type-1(中文在)" if cn_has else ("type-2(中英都缺)" if cn_has is False else "type-?(無token)")
            if cn_has:
                type1 += 1
            else:
                type2 += 1
            out_lines.append(f"\n[{kind}] invariants={sorted(inv)}")
            out_lines.append(unit)
    print("\n".join(out_lines))
    print(f"\n\n=== 合計 type-1≈{type1}  type-2/?≈{type2} ===")


if __name__ == "__main__":
    main()
