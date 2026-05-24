"""
For wave 1 §3.2.2.4.4–§3.2.2.4.20 (except .15 which is already interleaved),
the body currently is "all English block → all Chinese block". This script
re-arranges them to alternate paragraph-by-paragraph: EN para → CH para → EN para → ...

Only operates on .md files where:
  - The body has exactly one `>` blockquote chunk at the start (English)
  - Followed by plain Chinese paragraphs
  - The number of `>` sub-paragraphs equals the number of plain Chinese paragraphs

Run from project root:
    python scripts/interleave_wave1_paragraphs.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BR_DIR = ROOT / "src" / "content" / "br"

# Target files: §3.2.2.4.4 through §3.2.2.4.20 except .15 (which has different style)
TARGET_SLUGS = [f"3-2-2-4-{n}" for n in range(4, 21) if n != 15]


def split_blockquote_paragraphs(lines: list[str]) -> list[list[str]]:
    """Split a contiguous `>` blockquote block into sub-paragraphs.

    A sub-paragraph is separated from the next by a `>` (blank quote) line.
    Returns each sub-paragraph as a list of lines (each line still has `> ` prefix).
    """
    paras: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line.strip() == ">":
            if current:
                paras.append(current)
                current = []
        else:
            current.append(line)
    if current:
        paras.append(current)
    return paras


def split_plain_paragraphs(lines: list[str]) -> list[list[str]]:
    """Split plain text lines into paragraphs (separated by blank lines)."""
    paras: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line.strip() == "":
            if current:
                paras.append(current)
                current = []
        else:
            current.append(line)
    if current:
        paras.append(current)
    return paras


def process_file(path: Path) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        return False, "no front-matter found"
    _, fm, body = parts

    # Split body into "preamble lines" (heading > **English Title**, then blank) +
    # body lines we want to interleave.
    body_lines = body.splitlines()
    # Find the start of the actual content (skip the `> **Title**` line and blank line)
    i = 0
    preamble = []
    while i < len(body_lines):
        line = body_lines[i]
        if line.startswith("> **") and line.endswith("**"):
            preamble.append(line)
            i += 1
            # Consume following blank
            if i < len(body_lines) and body_lines[i].strip() == "":
                preamble.append(body_lines[i])
                i += 1
            break
        if line.strip() == "":
            preamble.append(line)
            i += 1
            continue
        break
    rest = body_lines[i:]

    # Find the contiguous `>` blockquote chunk at the start of rest, then plain content.
    eng_lines: list[str] = []
    j = 0
    # Skip leading blanks in rest
    while j < len(rest) and rest[j].strip() == "":
        j += 1
    while j < len(rest) and (rest[j].startswith(">") or (rest[j].strip() == "")):
        # Stop if we hit a blank-line break-out: i.e., blank followed by non-`>`
        if rest[j].strip() == "":
            # peek ahead
            k = j + 1
            while k < len(rest) and rest[k].strip() == "":
                k += 1
            if k < len(rest) and not rest[k].startswith(">"):
                break
        eng_lines.append(rest[j])
        j += 1
    # Trim trailing blanks from eng_lines
    while eng_lines and eng_lines[-1].strip() == "":
        eng_lines.pop()

    # Remaining is the Chinese plain content
    ch_lines = rest[j:]
    while ch_lines and ch_lines[0].strip() == "":
        ch_lines.pop(0)
    while ch_lines and ch_lines[-1].strip() == "":
        ch_lines.pop()

    if not eng_lines or not ch_lines:
        return False, f"empty eng({len(eng_lines)}) or ch({len(ch_lines)})"

    eng_paras = split_blockquote_paragraphs(eng_lines)
    ch_paras = split_plain_paragraphs(ch_lines)

    if len(eng_paras) != len(ch_paras):
        return False, f"para count mismatch: eng={len(eng_paras)} ch={len(ch_paras)}"

    # Interleave
    new_body_lines = list(preamble)
    for ep, cp in zip(eng_paras, ch_paras):
        new_body_lines.extend(ep)
        new_body_lines.append("")
        new_body_lines.extend(cp)
        new_body_lines.append("")
    # Trim trailing blank
    while new_body_lines and new_body_lines[-1].strip() == "":
        new_body_lines.pop()

    new_text = "---\n" + fm + "---\n" + "\n".join(new_body_lines) + "\n"
    path.write_text(new_text, encoding="utf-8")
    return True, f"interleaved {len(eng_paras)} paragraph pairs"


def main() -> int:
    ok = 0
    skipped = 0
    for slug in TARGET_SLUGS:
        path = BR_DIR / f"{slug}.md"
        if not path.exists():
            print(f"SKIP  {slug}.md  (not found)")
            skipped += 1
            continue
        success, msg = process_file(path)
        if success:
            print(f"OK    {slug}.md  ({msg})")
            ok += 1
        else:
            print(f"SKIP  {slug}.md  ({msg})")
            skipped += 1
    print(f"\nProcessed: {ok} interleaved, {skipped} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
