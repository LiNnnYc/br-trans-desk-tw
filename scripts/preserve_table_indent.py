"""把 BR.md 原文表格儲存格的「前導縮排空白」轉成 U+2007（FIGURE SPACE），
讓 markdown table parser 不再 strip 掉縮排階層（如 §7.1.2.6/7 內 ASN.1 欄位
名稱原本以 5 / 10 個半形空白縮排表示父子層級）。

為什麼用 U+2007 而不是 &nbsp;？
  - cabforum.org 自己就是用 U+2007（FIGURE SPACE）做表格縮排。BR.md
    經 cabforum 自家 markdown 流程後，輸出 HTML 即為 `<td>....<code>...`
    的形式（4 個 figure space / level）。本站對齊其視覺寬度。
  - U+2007 ≈ 0.5em（數字寬），&nbsp; ≈ 0.25em（半形空白寬）。同 count
    的縮排在 figure space 下視覺更明顯。

規則：
  - 比對 `|` 之後出現連續 ≥ 4 個半形空白，且後接非空白、非 `-`、非 `|` 的字元
  - 將該段空白替換為 1 個半形空白 + (N-1) 個 U+2007
  - 不影響「| --- |」分隔列（後接 `-`）與空 cell（後接 `|`）
  - threshold = 4 避開 markdown 表格 alignment padding（典型 2~3 空白）；
    BR.md 中真正的縮排用 5 或 10 空白，明顯高於 4。

只跑一次（idempotent：再跑會找不到 ≥ 4 半形空白的 pattern）。
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BR_DIR = ROOT / "src" / "content" / "br"

# `|` + N 個空白 (N≥4) + 非空白且非 `-` `|`
PATTERN = re.compile(r"\|( {4,})(?=[^\s\-|])")


FIGURE_SPACE = " "


def replace(match: re.Match[str]) -> str:
    n = len(match.group(1))
    return "| " + (FIGURE_SPACE * (n - 1))


def process(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    new_text, count = PATTERN.subn(replace, text)
    if count:
        path.write_text(new_text, encoding="utf-8")
    return count


def main() -> None:
    total = 0
    touched = 0
    for f in sorted(BR_DIR.glob("*.md")):
        c = process(f)
        if c:
            print(f"  {f.name}: {c} replacement(s)")
            touched += 1
            total += c
    print(f"\nDone. {touched} files, {total} replacements.")


if __name__ == "__main__":
    main()
