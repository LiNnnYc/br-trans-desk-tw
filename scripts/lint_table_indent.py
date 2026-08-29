#!/usr/bin/env python3
"""表格欄位階層縮排檢查（U+2007）。

欄位從屬關係以儲存格前導的 U+2007 FIGURE SPACE 表示（見
`TRANSLATION_CONVENTIONS.md` §2.3）。人工審閱時容易寫壞兩種情況，兩種在畫面上
都是「縮排看起來不見了」，但原始 markdown 看起來卻是對的：

1. **混用半形空白**：`|    ␣␣␣`base`` —— U+2007 之後又補了半形空白。半形空白在
   HTML 會被摺疊，於是第二層與第一層縮排一樣寬，階層消失。
2. **中英表層級不一致**：英文表用 2／4，中文表用 4／4 之類。以第一欄的識別碼
   配對比對兩側層級。

用法：
    PYTHONUTF8=1 python scripts/lint_table_indent.py

exit code：發現第 1 類（≥2 個半形空白）或第 2 類問題回傳 1，否則 0。
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BR_DIR = ROOT / 'src' / 'content' / 'br'
FIG = chr(0x2007)

# 前導縮排：U+2007 與半形空白的任意組合
LEAD = re.compile(rf'^[ ]*({FIG}+)([ ]*)')
SEP_CHARS = set('-: |')


def cells_of(line: str):
    """回傳 (是否為英文 blockquote 側, 儲存格list)；非表格列回傳 (None, None)"""
    s = line.strip()
    quoted = s.startswith('>')
    core = s.lstrip('> ').strip()
    if not core.startswith('|'):
        return None, None
    if set(core) <= SEP_CHARS:  # | --- | --- | 分隔列
        return None, None
    return quoted, core.split('|')[1:-1]


def key_of(cell: str) -> tuple[int, str]:
    m = LEAD.match(cell)
    indent = len(m.group(1)) if m else 0
    return indent, cell.strip()


def main() -> int:
    mixed_bad: list[str] = []
    mixed_ok: list[str] = []
    mismatch: list[str] = []

    for path in sorted(BR_DIR.glob('*.md')):
        en: dict[str, list[int]] = defaultdict(list)
        cn: dict[str, list[int]] = defaultdict(list)
        for lineno, line in enumerate(path.read_text(encoding='utf-8').split('\n'), 1):
            quoted, cells = cells_of(line)
            if cells is None:
                continue
            for cell in cells:
                m = LEAD.match(cell)
                if not m:
                    continue
                pad = len(m.group(2))
                if pad:
                    where = f'{path.name}:{lineno} [{len(m.group(1))}×U+2007 + {pad} 半形] {cell.strip()[:40]}'
                    (mixed_bad if pad >= 2 else mixed_ok).append(where)
            indent, key = key_of(cells[0])
            if not key or key.startswith('**'):
                continue
            (en if quoted else cn)[key].append(indent)
        for key in sorted(set(en) & set(cn)):
            if sorted(en[key]) != sorted(cn[key]):
                mismatch.append(f'{path.name} {key[:36]} EN={sorted(en[key])} CN={sorted(cn[key])}')

    print('== 1. 縮排混用半形空白（半形部分會被 HTML 摺疊 → 階層消失）==')
    for r in mixed_bad:
        print('  ✗', r)
    if not mixed_bad:
        print('  （無）')
    if mixed_ok:
        print(f'  ⓘ 另有 {len(mixed_ok)} 處只多 1 個半形空白（BR.md 原文的對齊 padding，視覺無影響）：')
        for r in mixed_ok[:5]:
            print('     ', r)

    print('\n== 2. 中英表縮排層級不一致（以第一欄識別碼配對）==')
    for r in mismatch:
        print('  ✗', r)
    if not mismatch:
        print('  （無）')

    return 1 if (mixed_bad or mismatch) else 0


if __name__ == '__main__':
    raise SystemExit(main())
