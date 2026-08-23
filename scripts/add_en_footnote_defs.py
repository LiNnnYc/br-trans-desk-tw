#!/usr/bin/env python3
"""把註腳補成中英對照（一次性，可重跑）。

拆檔時只帶了中文註腳定義，英文側（`> ` blockquote）的引用標記指向同一條中文
註腳，是全站唯一沒做中英對照的內容。本腳本：

1. 從 web-spec-doc/BR.md 取出英文註腳定義（`[^label]: ...`）。
2. 把各章節檔「英文側」的引用標記改成獨立 label：`[^eku_ca]` → `[^eku_ca_en]`
   （只改 `> ` 開頭的行；中文側維持原 label）。
3. 在中文定義上方補一行 blockquote 形式的英文定義：
       > [^eku_ca_en]: While RFC 5280 ...

       [^eku_ca]: 雖然 RFC 5280 ...

顯示端由 scripts/rehype-footnotes.mjs 處理：英文項目加 `.fn-item-en`，跟著中英
對照 toggle 顯示／隱藏；中英兩項共用同一個註腳編號；全文頁只保留中文。

用法：
    python scripts/add_en_footnote_defs.py           # 乾跑，只列出會改什麼
    python scripts/add_en_footnote_defs.py --write   # 實際寫入
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BR_MD = ROOT / 'web-spec-doc' / 'BR.md'
CONTENT = ROOT / 'src' / 'content' / 'br'

DEF_RE = re.compile(r'^\[\^([A-Za-z0-9_]+)\]:[ ](.*)$')
EN_SUFFIX = '_en'


def load_en_defs() -> dict[str, str]:
    defs: dict[str, str] = {}
    for line in BR_MD.read_text(encoding='utf-8').split('\n'):
        m = DEF_RE.match(line)
        if m:
            defs[m.group(1)] = m.group(2).strip()
    return defs


def process(text: str, en_defs: dict[str, str]) -> tuple[str, int, int]:
    """回傳 (新內容, 改寫的引用數, 補上的英文定義數)"""
    lines = text.split('\n')
    refs_changed = 0
    defs_added = 0
    out: list[str] = []

    for line in lines:
        # 1) 英文側引用改用 _en label（定義行不動）
        if line.lstrip().startswith('>') and not DEF_RE.match(line.lstrip('> ')):
            for label in en_defs:
                pattern = rf'\[\^{re.escape(label)}\](?!:)'
                line, n = re.subn(pattern, f'[^{label}{EN_SUFFIX}]', line)
                refs_changed += n

        # 2) 中文定義上方補英文定義
        m = DEF_RE.match(line)
        if m and not m.group(1).endswith(EN_SUFFIX):
            label = m.group(1)
            en = en_defs.get(label)
            already = any(f'[^{label}{EN_SUFFIX}]:' in prev for prev in out[-4:])
            if en and not already:
                if out and out[-1].strip():
                    out.append('')
                out.append(f'> [^{label}{EN_SUFFIX}]: {en}')
                out.append('')
                defs_added += 1

        out.append(line)

    return '\n'.join(out), refs_changed, defs_added


def scan() -> tuple[dict, dict]:
    """掃描 src/content/br/：回傳 (定義位置, 引用位置)

    定義位置：label → [(檔名, 行號, 內文)]
    引用位置：base label → {檔名: {'cn': n, 'en': n}}
    """
    defs: dict[str, list[tuple[str, int, str]]] = {}
    refs: dict[str, dict[str, dict[str, int]]] = {}
    for path in sorted(CONTENT.glob('*.md')):
        text = path.read_text(encoding='utf-8')
        if '[^' not in text:
            continue
        for lineno, line in enumerate(text.split('\n'), 1):
            m = DEF_RE.match(line.lstrip('> '))
            if m:
                defs.setdefault(m.group(1), []).append((path.name, lineno, m.group(2).strip()))
                continue
            for label in re.findall(r'\[\^([A-Za-z0-9_]+)\]', line):
                base = label[: -len(EN_SUFFIX)] if label.endswith(EN_SUFFIX) else label
                slot = refs.setdefault(base, {}).setdefault(path.name, {'cn': 0, 'en': 0})
                slot['en' if label.endswith(EN_SUFFIX) else 'cn'] += 1
    return defs, refs


def write_doc(out_path: Path, en_defs: dict[str, str]) -> None:
    """產出「改註腳翻譯要動哪些檔」的審閱清單。"""
    defs, refs = scan()
    bases = [lb for lb in defs if not lb.endswith(EN_SUFFIX)]
    order = sorted(bases, key=lambda lb: -sum(v['cn'] for v in refs.get(lb, {}).values()))

    L: list[str] = []
    L.append('# 註腳翻譯修改清單')
    L.append('')
    L.append('> 由 `python scripts/add_en_footnote_defs.py --doc <路徑>` 產生，行號會隨檔案異動而變，'
             '改完請重跑一次。慣例見 `TRANSLATION_CONVENTIONS.md` §13。')
    L.append('')
    L.append('## 怎麼改（重要）')
    L.append('')
    L.append('- 只改**中文定義行** `[^label]: …`；`> [^label_en]: …` 是照抄 BR.md 的英文原文，**不要動**。')
    L.append('- 同一條註腳在多個章節檔各有一份副本，**必須全部改成一模一樣的文字**。'
             '全文頁合併時以首次出現者為準，沒同步到的檔在單章節頁會顯示成舊譯文。')
    L.append('- 改完自我檢查（每個 label 應只印出一行，出現兩行以上代表有檔案漏改）：')
    L.append('')
    L.append('  ```sh')
    L.append("  grep -h '^\\[\\^' src/content/br/*.md | sort -u")
    L.append('  ```')
    L.append('')
    total_cn = sum(sum(v['cn'] for v in refs.get(lb, {}).values()) for lb in bases)
    L.append(f'全庫共 **{len(bases)} 條**註腳、中文側 **{total_cn} 處**引用，全部集中在第 7 章。')
    L.append('')
    L.append('| # | 註腳 label | 中文定義要改的檔案（行號） | 內文引用處 |')
    L.append('|---|---|---|---|')
    for i, label in enumerate(order, 1):
        locs = '、'.join(f'`{n}`:{ln}' for n, ln, _ in defs[label])
        cites = '、'.join(
            f'§{n[:-3].replace("-", ".")}×{v["cn"]}' if v['cn'] > 1 else f'§{n[:-3].replace("-", ".")}'
            for n, v in sorted(refs.get(label, {}).items())
            if v['cn']
        )
        L.append(f'| {i} | `{label}` | {locs} | {cites} |')
    L.append('')

    for i, label in enumerate(order, 1):
        copies = defs[label]
        texts = {t for _, _, t in copies}
        L.append(f'## {i}. `{label}`（{len(copies)} 份副本）')
        L.append('')
        L.append('**英文原文（勿改）**：')
        L.append('')
        L.append(f'> {en_defs.get(label, "（BR.md 無對應定義）")}')
        L.append('')
        L.append('**目前中文譯文**：')
        L.append('')
        for t in sorted(texts):
            L.append(f'> {t}')
            L.append('')
        if len(texts) > 1:
            L.append(f'> ⚠️ **這 {len(copies)} 份副本內容不一致（{len(texts)} 種版本），請先統一。**')
            L.append('')
        L.append('要改的檔案：')
        L.append('')
        for n, ln, _ in copies:
            L.append(f'- [ ] `src/content/br/{n}` 第 {ln} 行')
        L.append('')

    out_path.write_text('\n'.join(L), encoding='utf-8')
    print(f'✔ 已產出 {out_path}（{len(bases)} 條註腳、{total_cn} 處中文引用）')


def main() -> int:
    write = '--write' in sys.argv
    if '--doc' in sys.argv:
        idx = sys.argv.index('--doc')
        if idx + 1 >= len(sys.argv):
            print('--doc 需要指定輸出路徑')
            return 1
        write_doc(Path(sys.argv[idx + 1]), load_en_defs())
        return 0
    en_defs = load_en_defs()
    if not en_defs:
        print(f'在 {BR_MD} 找不到任何註腳定義')
        return 1
    print(f'BR.md 英文註腳定義：{len(en_defs)} 條 → {", ".join(sorted(en_defs))}\n')

    total_files = total_refs = total_defs = 0
    for path in sorted(CONTENT.glob('*.md')):
        text = path.read_text(encoding='utf-8')
        if '[^' not in text:
            continue
        new, refs, defs = process(text, en_defs)
        if new == text:
            continue
        total_files += 1
        total_refs += refs
        total_defs += defs
        print(f'  {path.name}：英文側引用 {refs} 處、補英文定義 {defs} 條')
        if write:
            path.write_text(new, encoding='utf-8')

    print(f'\n{"已寫入" if write else "（乾跑）"} {total_files} 檔、'
          f'引用 {total_refs} 處、英文定義 {total_defs} 條')
    if not write:
        print('加 --write 實際寫入。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
