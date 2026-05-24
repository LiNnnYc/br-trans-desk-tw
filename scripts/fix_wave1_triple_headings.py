"""
Pre-process BR_T_master.md to fix the wave 1 §3.2.2.4.4–.20 triple-heading bug.

Original wave 1 author used this pattern for §3.2.2.4.4 onwards:

    ##### 3.2.2.4.4 Email to a Constructed Address       <- plain EN heading
    (blank)
    > ##### 3.2.2.4.4 Email to a Constructed Address     <- duplicate heading INSIDE quote
    >
    > Confirm the Applicant's control over the FQDN by:
    > ...
    (blank)
    ##### 3.2.2.4.4 寄送電子郵件至指定建置地址            <- plain CH heading

After fix (Style A):

    > ##### 3.2.2.4.4 Email to a Constructed Address     <- paired EN (blockquoted)
    ##### 3.2.2.4.4 寄送電子郵件至指定建置地址            <- paired CH (plain)

    > Confirm the Applicant's control over the FQDN by:
    > ...

This is done by deleting the plain EN heading and the duplicate quoted EN heading.
The subsequent unify_headings.py pass will pair the surviving CH heading correctly.

Run from project root:
    python scripts/fix_wave1_triple_headings.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER_PATH = ROOT / "web-spec-doc" / "翻譯工作區" / "BR_T_master.md"
OUT_PATH = ROOT / "web-spec-doc" / "翻譯工作區" / "BR_T_master.fixed.md"

PLAIN_HEAD_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
QUOTE_HEAD_RE = re.compile(r"^>\s+(#{1,6})\s+(.+?)\s*$")
NUM_PREFIX_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+(.+)$")


def has_cjk(s: str) -> bool:
    return bool(re.search(r"[一-鿿]", s))


def parse_heading_body(body: str) -> tuple[str | None, str | None]:
    body = body.strip()
    body = re.sub(r"\[\^[a-z_0-9]+\]", "", body).strip()
    nm = NUM_PREFIX_RE.match(body)
    if not nm:
        return None, None
    return nm.group(1).rstrip("."), nm.group(2).strip()


def main() -> int:
    text = MASTER_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    out = []
    i = 0
    removed_plain = 0
    removed_quoted = 0

    while i < len(lines):
        line = lines[i]

        # Detect plain EN heading (CJK-free body) followed by a duplicate inside `>`
        m = PLAIN_HEAD_RE.match(line)
        if m and not QUOTE_HEAD_RE.match(line):
            hashes = m.group(1)
            body = m.group(2)
            sec_id, title_part = parse_heading_body(body)
            if sec_id and title_part and not has_cjk(title_part):
                # Pure ASCII heading body — candidate for wave 1 triple-heading pattern.
                # Look ahead: skip blank lines; is the next non-blank a `> ##### N text` with same sec_id?
                j = i + 1
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                if j < len(lines):
                    qm = QUOTE_HEAD_RE.match(lines[j])
                    if qm:
                        qbody = qm.group(2)
                        q_sec_id, q_title = parse_heading_body(qbody)
                        if q_sec_id == sec_id and q_title and not has_cjk(q_title):
                            # MATCH! This is the triple-heading pattern.
                            # Drop:
                            #   - the plain EN heading (current line i)
                            #   - the duplicate quoted EN heading (line j)
                            # Keep blank lines in between (preserve spacing) and continue scan.
                            removed_plain += 1
                            removed_quoted += 1
                            # Skip line i (plain EN). For line j (quoted EN), drop it too.
                            # Re-emit blank lines between them.
                            for k in range(i + 1, j):
                                out.append(lines[k])
                            i = j + 1
                            # Also drop subsequent blank-quote lines like `>` immediately after the
                            # dropped quoted heading (those were spacing inside the blockquote).
                            while i < len(lines) and lines[i].strip() == ">":
                                i += 1
                            continue

        out.append(line)
        i += 1

    OUT_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Removed: {removed_plain} plain EN headings + {removed_quoted} quoted EN headings")
    print(f"Output: {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
