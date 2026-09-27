#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回填 BR.md 的 Pandoc `Table:` caption 到 src/content/br 章節檔，
供 rehype-table-caption plugin 轉成表格底端 <caption>。

來源：
- EN caption（權威）：web-spec-doc/BR.md 的 41 個 `Table: ...`
- CN caption（已譯）：git c233144^ 各章節檔被移除的 `表：...`（commit c233144 移除）
比對鍵：表格內容簽章（normalize 後的 header + data rows，吸收 U+2007/空白差異）。

用法：
  python scripts/restore_table_captions.py            # dry-run，只報告
  python scripts/restore_table_captions.py --write     # 實際寫入章節檔
"""
import os
import re
import sys
import subprocess
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BR_MD = os.path.join(ROOT, "web-spec-doc", "BR.md")
CONTENT_DIR = os.path.join(ROOT, "src", "content", "br")
REMOVE_COMMIT = "c233144"

WS = "".join([" ", " ", " ", "​", "\t"])
_ws_re = re.compile("[" + re.escape(WS) + "]+")


def norm_cell(c):
    return _ws_re.sub("", c).strip("|").strip()


def table_signature(rows):
    """rows: list of raw table lines（可能含前導 '>'）。回傳內容簽章。"""
    sig_rows = []
    for ln in rows:
        ln = ln.lstrip()
        if ln.startswith(">"):
            ln = ln[1:].lstrip()
        if not ln.startswith("|"):
            continue
        cells = [norm_cell(c) for c in ln.strip().strip("|").split("|")]
        # 跳過分隔列（全是 - 或 :）
        joined = "".join(cells)
        if joined and all(ch in "-:" for ch in joined):
            continue
        sig_rows.append("|".join(cells))
    return "\n".join(sig_rows)


def is_table_line(ln):
    s = ln.lstrip()
    if s.startswith(">"):
        s = s[1:].lstrip()
    return s.startswith("|")


# ---------- 1. 解析 BR.md：(section_id, en_caption, signature) ----------
def parse_br_captions():
    with open(BR_MD, encoding="utf-8") as f:
        lines = f.read().split("\n")
    heading_re = re.compile(r"^(#{1,6})\s+(.*)$")
    sid_re = re.compile(r"^([0-9]+(?:\.[0-9]+)*|Appendix\s+[A-Z])", re.I)
    cur_sid = "(前言)"
    caps = []  # (sid, en_caption, sig, caption_line_index)
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        m = heading_re.match(ln)
        if m:
            sm = sid_re.match(m.group(2).strip())
            cur_sid = sm.group(1) if sm else m.group(2).strip()
            i += 1
            continue
        cm = re.match(r"^Table:\s*(.+)$", ln.strip())
        if cm:
            en_caption = cm.group(1).strip()
            # 往下找下一個表格 block
            j = i + 1
            while j < n and not is_table_line(lines[j]):
                if lines[j].strip() and not is_table_line(lines[j]):
                    # 容許一個空白行；若遇到非空白非表格行就停（保險）
                    if lines[j].strip() != "":
                        break
                j += 1
            tbl = []
            while j < n and is_table_line(lines[j]):
                tbl.append(lines[j])
                j += 1
            sig = table_signature(tbl)
            caps.append((cur_sid, en_caption, sig))
        i += 1
    return caps


# ---------- 2. 從 c233144^ 取 CN caption：signature -> cn_caption ----------
def parse_cn_captions():
    # 列出當時被改的檔
    out = subprocess.run(
        ["git", "show", "--name-only", "--pretty=format:", REMOVE_COMMIT],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
    ).stdout
    files = [f.strip() for f in out.split("\n")
             if f.strip().startswith("src/content/br/") and f.strip().endswith(".md")]
    sig2cn = {}
    cn_orphans = []  # 找不到表格的 CN caption（保留供人工）
    for rel in files:
        try:
            content = subprocess.run(
                ["git", "show", f"{REMOVE_COMMIT}^:{rel}"],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            ).stdout
        except Exception:
            continue
        lines = content.split("\n")
        n = len(lines)
        for i, ln in enumerate(lines):
            cm = re.match(r"^表[:：]\s*(.+)$", ln.strip())
            if not cm:
                continue
            cn_caption = cm.group(1).strip()
            # 找接下來最近的表格 block（優先 EN '> |'，否則任何 '|'）
            j = i + 1
            while j < n and not is_table_line(lines[j]):
                j += 1
            if j >= n:
                cn_orphans.append((rel, cn_caption))
                continue
            tbl = []
            while j < n and is_table_line(lines[j]):
                tbl.append(lines[j])
                j += 1
            sig = table_signature(tbl)
            if sig and sig not in sig2cn:
                sig2cn[sig] = cn_caption
    return sig2cn, cn_orphans


def find_table_blocks(lines):
    """回傳 [(start, end_exclusive, kind)]，kind = 'EN'（blockquote）或 'CN'。"""
    blocks = []
    i = 0
    n = len(lines)
    while i < n:
        if is_table_line(lines[i]):
            s = i
            kind = "EN" if lines[i].lstrip().startswith(">") else "CN"
            while i < n and is_table_line(lines[i]):
                i += 1
            blocks.append((s, i, kind))
        else:
            i += 1
    return blocks


def inject_file(path, sig2en, sig2cn, report):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    blocks = find_table_blocks(lines)

    # 先算每個 block 的 signature 與要插入的 caption
    inserts = {}  # start_line -> list[str]（插在該行之前）
    k = 0
    nb = len(blocks)
    while k < nb:
        s, e, kind = blocks[k]
        if kind != "EN":
            k += 1
            continue
        sig = table_signature(lines[s:e])
        en_cap = sig2en.get(sig)
        if not en_cap:
            k += 1
            continue
        cn_cap = sig2cn.get(sig)
        # 防呆：上一行已是 caption 就跳過（idempotent）
        prev = lines[s - 1].strip() if s > 0 else ""
        if not re.match(r"^>?\s*Table:", prev):
            inserts.setdefault(s, []).extend(["> Table: " + en_cap, ">"])
        # 找這個 EN block 之後、下一個 EN block 之前的第一個 CN block 作為配對
        if cn_cap and k + 1 < nb and blocks[k + 1][2] == "CN":
            cs = blocks[k + 1][0]
            cprev = lines[cs - 1].strip() if cs > 0 else ""
            if not re.match(r"^表[:：]", cprev):
                inserts.setdefault(cs, []).extend(["表：" + cn_cap, ""])
            report.append((os.path.basename(path), en_cap, cn_cap, True))
        else:
            report.append((os.path.basename(path), en_cap, cn_cap, False))
        k += 1

    if not inserts:
        return False
    out = []
    for idx, ln in enumerate(lines):
        if idx in inserts:
            out.extend(inserts[idx])
        out.append(ln)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    return True


def main():
    write = "--write" in sys.argv
    br_caps = parse_br_captions()
    sig2cn, cn_orphans = parse_cn_captions()

    # 偵測 BR.md 內 sig 衝突（同一 sig 對到不同 caption）
    sig2en = {}
    conflicts = []
    for sid, en, sig in br_caps:
        if not sig:
            continue
        if sig in sig2en and sig2en[sig] != en:
            conflicts.append((sig, sig2en[sig], en))
        else:
            sig2en[sig] = en

    print(f"BR.md captioned tables: {len(br_caps)}")
    print(f"  unique signatures    : {len(sig2en)}")
    print(f"  sig conflicts (同表異標題): {len(conflicts)}")
    for sig, a, b in conflicts:
        print(f"    - [{a}] vs [{b}]  sig={sig[:50]!r}")
    print(f"CN captions recovered (c233144^): {len(sig2cn)} signatures")
    if cn_orphans:
        print(f"  CN orphan (無對應表格): {len(cn_orphans)}")

    # 覆蓋率：每個 BR.md caption 是否有 CN
    missing_cn = []
    for sid, en, sig in br_caps:
        cn = sig2cn.get(sig)
        if not cn:
            missing_cn.append((sid, en, sig))
    print(f"\nBR.md caption 缺 CN 譯文: {len(missing_cn)}")
    for sid, en, sig in missing_cn:
        print(f"  §{sid}: {en}")

    # ---------- 3. 注入（dry-run 或 --write）----------
    report = []
    files = sorted(
        os.path.join(CONTENT_DIR, f)
        for f in os.listdir(CONTENT_DIR)
        if f.endswith(".md")
    )
    changed = 0
    if write:
        for p in files:
            if inject_file(p, sig2en, sig2cn, report):
                changed += 1
    else:
        # dry-run：只跑分析、不寫
        for p in files:
            with open(p, encoding="utf-8") as f:
                lines = f.read().split("\n")
            blocks = find_table_blocks(lines)
            k = 0
            nb = len(blocks)
            while k < nb:
                s, e, kind = blocks[k]
                if kind == "EN":
                    sig = table_signature(lines[s:e])
                    en_cap = sig2en.get(sig)
                    if en_cap:
                        cn_cap = sig2cn.get(sig)
                        paired = (k + 1 < nb and blocks[k + 1][2] == "CN")
                        report.append((os.path.basename(p), en_cap, cn_cap, paired))
                k += 1

    matched = len(report)
    no_cn_pair = [r for r in report if not r[3]]
    print(f"\n注入計畫：匹配到 caption 的 EN 表格 = {matched}（{'已寫入' if write else 'dry-run'}）")
    print(f"  缺 CN 表格配對（只會放 EN caption）: {len(no_cn_pair)}")
    for fn, en, cn, paired in report:
        flag = "" if paired else "  ⚠無CN配對"
        print(f"  {fn:20s} | {en}{flag}")
    if write:
        print(f"\n已修改檔案數: {changed}")

    # ---------- 4. 產生人類可讀清單（--doc PATH）----------
    if "--doc" in sys.argv:
        di = sys.argv.index("--doc")
        doc_path = sys.argv[di + 1] if di + 1 < len(sys.argv) else "表格caption清單.md"
        write_doc(doc_path, br_caps, sig2cn)
        print(f"\n已輸出清單：{doc_path}")

    return br_caps, sig2en, sig2cn


def slug_of(sid):
    if sid.lower().startswith("appendix"):
        letter = sid.split()[-1].lower()
        return f"appendix-{letter}"
    return sid.replace(".", "-")


def write_doc(path, br_caps, sig2cn):
    # 依 BR.md 文件順序；標出重複（同簽章出現多次）
    from collections import Counter
    sig_counts = Counter(sig for _, _, sig in br_caps if sig)
    rows = []
    seen_sig = {}
    for idx, (sid, en, sig) in enumerate(br_caps, 1):
        cn = sig2cn.get(sig, "—")
        slug = slug_of(sid)
        dup = sig_counts.get(sig, 1)
        first = sig not in seen_sig
        seen_sig[sig] = True
        rows.append((idx, sid, slug, en, cn, dup, first))

    out = []
    out.append("# BR 表格 caption 清單\n")
    out.append("> 來源：`web-spec-doc/BR.md`（v2.2.7）的 Pandoc `Table:` caption。")
    out.append("> 英文＝BR.md 原文；中文＝已回填譯文（git `c233144^` 回收）。")
    out.append("> 顯示位置：各表格**底端**（`rehype-table-caption.mjs` → `<caption>` + `caption-side: bottom`）。\n")
    total = len(rows)
    uniq = len(sig_counts)
    out.append(f"- 表格 caption 總數：**{total}**（唯一內容 {uniq} 種；其餘為跨章節重複表格）")
    out.append(f"- 涵蓋章節檔：見下表「章節檔」欄（`/server-cert-br/<slug>/`）\n")
    out.append("> 「重複」欄：標 `×N` 表示該表格（內容相同）在全文共出現 N 次、共用同一 caption；")
    out.append("> 同一內容只在首次出現處標 N，其餘標「↑同上」。\n")
    out.append("| # | § | 章節檔 | 英文 caption | 中文 caption | 重複 |")
    out.append("|---|---|---|---|---|---|")
    for idx, sid, slug, en, cn, dup, first in rows:
        dup_mark = (f"×{dup}" if first and dup > 1 else ("↑同上" if not first else "—"))
        en_disp = en.replace("|", "\\|")
        cn_disp = cn.replace("|", "\\|")
        out.append(f"| {idx} | §{sid} | `{slug}` | {en_disp} | {cn_disp} | {dup_mark} |")
    out.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


if __name__ == "__main__":
    main()
