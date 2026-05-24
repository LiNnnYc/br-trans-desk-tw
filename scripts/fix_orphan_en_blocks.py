"""
Wave 1 §3.2.2.4.4–.20 had a layout where:
  plain EN heading | quoted EN heading | English body in `>` blockquote | plain CH heading | Chinese body

fix_wave1_triple_headings.py removed the two duplicate EN heading lines, but the
English body block now sits BEFORE its section's CH heading, getting attached to
the WRONG section by the splitter.

This script moves each orphan `>` blockquote block (that sits between two
heading-pair starts) to AFTER the heading-pair that comes next.

Run from project root:
    python scripts/fix_orphan_en_blocks.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER_PATH = ROOT / "web-spec-doc" / "翻譯工作區" / "BR_T_master.normalized.md"

QUOTE_HEAD_RE = re.compile(r"^>\s+(#{1,6})\s+")
PLAIN_HEAD_RE = re.compile(r"^(#{1,6})\s+")
QUOTE_LINE_RE = re.compile(r"^>")


def main() -> int:
    lines = MASTER_PATH.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    moved = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect a plain CH heading whose IMMEDIATELY-preceding non-blank line is `> #### EN`
        # heading (i.e., this is the start of a Style A heading pair).
        # If the previous content (before the `> #### EN`) contains an orphan `>` blockquote
        # block (without any plain CH text breaking it up), that's the misplaced English body.
        m = PLAIN_HEAD_RE.match(line)
        if m and not QUOTE_HEAD_RE.match(line):
            # Find the `> #### EN` paired heading above (within last few lines, skipping blanks).
            en_heading_idx = None
            j = len(out) - 1
            while j >= 0 and out[j].strip() == "":
                j -= 1
            if j >= 0 and QUOTE_HEAD_RE.match(out[j]):
                en_heading_idx = j
                # Now look further back: is there a contiguous `>` block above (an orphan English body)?
                # Allowed: blank lines, then a run of `>` lines (the orphan), then a heading-pair-end above.
                k = en_heading_idx - 1
                while k >= 0 and out[k].strip() == "":
                    k -= 1
                # k now points to the last non-blank line above the EN heading.
                # Collect the contiguous `>` block ending at k.
                block_end = k
                block_start = k
                while block_start >= 0 and (QUOTE_LINE_RE.match(out[block_start]) or out[block_start].strip() == ""):
                    block_start -= 1
                block_start += 1
                # Filter: block must contain at least one `>` line (not just blanks)
                has_quote = any(QUOTE_LINE_RE.match(out[x]) for x in range(block_start, block_end + 1))
                # Also ensure the block doesn't itself START with a `> #### N` heading
                # (because that'd be the previous section's already-paired heading).
                has_qhead = any(QUOTE_HEAD_RE.match(out[x]) for x in range(block_start, block_end + 1))
                if has_quote and not has_qhead:
                    # Check what comes BEFORE this orphan block — should be the end of the previous
                    # section's content (the previous CH paragraph), not another section heading.
                    if block_start > 0:
                        prev_line = out[block_start - 1] if block_start > 0 else ""
                        # If the line immediately before the block is itself a `> ####` heading,
                        # then this block is the body of THAT section, not an orphan. Skip.
                        if QUOTE_HEAD_RE.match(prev_line):
                            pass  # don't move
                        else:
                            # MOVE: remove out[block_start:block_end+1] and insert after the CH heading line.
                            orphan = out[block_start:block_end + 1]
                            # Trim trailing blanks from orphan, and leading blanks too
                            while orphan and orphan[-1].strip() == "":
                                orphan.pop()
                            while orphan and orphan[0].strip() == "":
                                orphan.pop(0)
                            # Delete from out
                            del out[block_start:block_end + 1]
                            # Also drop the blank line that used to follow the orphan (now between two blank-separated areas)
                            # Append the current EN+CH heading pair first
                            out.append(line)
                            # Then a blank line, then the orphan English body, then a blank
                            out.append("")
                            out.extend(orphan)
                            out.append("")
                            moved += 1
                            i += 1
                            continue
            out.append(line)
            i += 1
            continue

        out.append(line)
        i += 1

    MASTER_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Moved {moved} orphan English body blocks to their correct sections.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
