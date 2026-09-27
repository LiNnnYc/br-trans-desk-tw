"""
Normalize BR translation headings to Style A:
    > ##### N.N.N English Title
    ##### N.N.N 中文標題

Run from project root:
    python scripts/unify_headings.py

Input:  web-spec-doc/翻譯工作區/BR_T_master.md
Output: web-spec-doc/翻譯工作區/BR_T_master.normalized.md
Also writes a diff report to: web-spec-doc/翻譯工作區/heading_diff.log
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BR_PATH = ROOT / "upstream" / "BR.md"
MASTER_PATH = ROOT / "web-spec-doc" / "翻譯工作區" / "BR_T_master.md"
OUT_PATH = ROOT / "web-spec-doc" / "翻譯工作區" / "BR_T_master.normalized.md"
LOG_PATH = ROOT / "web-spec-doc" / "翻譯工作區" / "heading_diff.log"

SEC_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
# Matches a section number prefix like "1.", "1.1", "3.2.2.4.21", "7.1.2.10.8"
NUM_PREFIX_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+(.+)$")
APP_RE = re.compile(r"^(Appendix\s+[A-Z])\b(.*)$", re.IGNORECASE)


def normalize_id(raw: str) -> str:
    """Strip trailing dot, e.g., '1.' -> '1'."""
    return raw.rstrip(".")


def parse_br_titles(text: str) -> dict[str, str]:
    """Build {section_id: english_title} from BR.md.

    section_id examples: "1", "1.1", "3.2.2.4.21", "appendix-a", "appendix-b"
    english_title: the part after the section number (no leading number).
    """
    titles: dict[str, str] = {}
    for line in text.splitlines():
        m = SEC_RE.match(line)
        if not m:
            continue
        body = m.group(2).strip()
        # Strip footnote markers like [^id]
        body = re.sub(r"\[\^[a-z_]+\]", "", body).strip()
        # Try Appendix first
        am = APP_RE.match(body)
        if am:
            letter = am.group(1).split()[-1].upper()
            rest = am.group(2).lstrip(" –-—").strip()
            titles[f"appendix-{letter.lower()}"] = rest
            continue
        nm = NUM_PREFIX_RE.match(body)
        if not nm:
            continue
        sec_id = normalize_id(nm.group(1))
        title = nm.group(2).strip()
        titles[sec_id] = title
    return titles


def extract_section_info(heading_body: str) -> tuple[str | None, str | None, str | None]:
    """From a heading body like '3.2.2.4.21 以帳號 ID 標記之 DNS - ACME', return
    (section_id, chinese_part, english_in_parens or None).

    Handles:
        '1.1 概觀（Overview）'           -> ('1.1', '概觀', 'Overview')
        '7.1.3 演算法物件識別字'         -> ('7.1.3', '演算法物件識別字', None)
        '附錄 A — CAA 聯絡標籤'          -> ('appendix-a', 'CAA 聯絡標籤', None)
        'Appendix A – CAA Contact Tag'  -> ('appendix-a', None, 'CAA Contact Tag')
    """
    body = heading_body.strip()
    body = re.sub(r"\[\^[a-z_]+\]", "", body).strip()

    # Appendix Chinese ("附錄 A — XXX") or English ("Appendix A – XXX")
    m = re.match(r"^附錄\s*([A-Z])\s*[—–-]\s*(.+)$", body)
    if m:
        return f"appendix-{m.group(1).lower()}", m.group(2).strip(), None
    m = re.match(r"^Appendix\s+([A-Z])\s*[–-—]\s*(.+)$", body, re.IGNORECASE)
    if m:
        return f"appendix-{m.group(1).lower()}", None, m.group(2).strip()
    m = re.match(r"^附錄\s*([A-Z])\s*$", body)
    if m:
        return f"appendix-{m.group(1).lower()}", "", None

    nm = NUM_PREFIX_RE.match(body)
    if not nm:
        return None, None, None
    sec_id = normalize_id(nm.group(1))
    rest = nm.group(2).strip()

    # Check for trailing parentheses with English: '中文（English）'
    pm = re.match(r"^(.+?)\s*[（(]([A-Za-z][^）)]*)[）)]\s*$", rest)
    if pm:
        chinese = pm.group(1).strip()
        english = pm.group(2).strip()
        # Only treat as bilingual if english is ASCII-ish (not a Chinese-only annotation)
        if re.search(r"[A-Za-z]", english):
            return sec_id, chinese, english
    return sec_id, rest, None


def main() -> int:
    br_text = BR_PATH.read_text(encoding="utf-8")
    master_text = MASTER_PATH.read_text(encoding="utf-8")

    br_titles = parse_br_titles(br_text)
    print(f"BR.md headings indexed: {len(br_titles)}")

    lines = master_text.splitlines()
    out_lines: list[str] = []
    diff_log: list[str] = []
    stats = {
        "kept_bilingual_pair": 0,
        "split_paren_bilingual": 0,
        "added_english_from_br": 0,
        "missing_english": 0,
        "passthrough": 0,
    }

    i = 0
    while i < len(lines):
        line = lines[i]

        # Case 1: already a "> #### EN" line followed by "#### CH" line — pass through.
        bm = re.match(r"^>\s+(#{1,6})\s+(.+?)\s*$", line)
        if bm:
            # Check next non-blank line for matching CH heading
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines):
                cm = re.match(r"^(#{1,6})\s+(.+?)\s*$", lines[j])
                if cm:
                    # Looks like the pair we want; pass both through unchanged.
                    out_lines.append(line)
                    for k in range(i + 1, j):
                        out_lines.append(lines[k])
                    out_lines.append(lines[j])
                    stats["kept_bilingual_pair"] += 1
                    i = j + 1
                    continue
            out_lines.append(line)
            i += 1
            continue

        # Case 2: plain heading
        hm = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if hm:
            hashes = hm.group(1)
            body = hm.group(2)
            sec_id, chinese, english_inline = extract_section_info(body)

            if sec_id is None:
                # Not a section-numbered heading (e.g., "## 附錄 A" without dash). Pass.
                out_lines.append(line)
                stats["passthrough"] += 1
                i += 1
                continue

            # Format section prefix: top-level chapters keep trailing dot ("1.")
            # appendix uses "Appendix X" / "附錄 X" instead of slug.
            if sec_id.startswith("appendix-"):
                letter = sec_id.rsplit("-", 1)[1].upper()
                en_prefix = f"Appendix {letter} –"
                ch_prefix = f"附錄 {letter} —"
            else:
                # Single-segment (top-level chapter) gets a trailing dot.
                en_prefix = sec_id + "." if "." not in sec_id else sec_id
                ch_prefix = en_prefix

            # Bilingual paren form: split into two-line.
            if english_inline:
                en_line = f"> {hashes} {en_prefix} {english_inline}"
                ch_line = f"{hashes} {ch_prefix} {chinese}"
                out_lines.append(en_line)
                out_lines.append(ch_line)
                stats["split_paren_bilingual"] += 1
                diff_log.append(
                    f"SPLIT  L{i+1}: '{line}' -> '{en_line}' + '{ch_line}'"
                )
                i += 1
                continue

            # Chinese-only: lookup English in BR.md
            en_from_br = br_titles.get(sec_id)
            if en_from_br:
                en_line = f"> {hashes} {en_prefix} {en_from_br}"
                ch_line = f"{hashes} {ch_prefix} {chinese}"
                out_lines.append(en_line)
                out_lines.append(ch_line)
                stats["added_english_from_br"] += 1
                diff_log.append(
                    f"ADD-EN L{i+1}: section {sec_id} '{chinese}' -> EN='{en_from_br}'"
                )
                i += 1
                continue

            # No English found
            out_lines.append(line)
            stats["missing_english"] += 1
            diff_log.append(
                f"MISS   L{i+1}: section {sec_id} '{chinese}' -- no English in BR.md"
            )
            i += 1
            continue

        # Skip wave-separator HTML comment lines unchanged (already covered by passthrough above,
        # but explicit to document intent).

        out_lines.append(line)
        i += 1

    OUT_PATH.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    LOG_PATH.write_text(
        "\n".join(diff_log) + "\n\n--- STATS ---\n"
        + "\n".join(f"{k}: {v}" for k, v in stats.items())
        + "\n",
        encoding="utf-8",
    )
    print("\n--- STATS ---")
    for k, v in stats.items():
        print(f"{k}: {v}")
    print(f"\nOutput: {OUT_PATH}")
    print(f"Diff log: {LOG_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
