#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""偵測 BR.md 中重複使用的段落（block-level），輸出 markdown 報告。"""
import re
import sys
from collections import defaultdict

SRC = "upstream/BR.md"

with open(SRC, encoding="utf-8") as f:
    lines = f.readlines()

# 找出每一行所屬的章節（最近一個 heading 的 section id + title）
heading_re = re.compile(r'^(#{1,6})\s+(.*)$')
# section id 例：1.6.1、3.2.2.4.20、Appendix A
sid_re = re.compile(r'^([0-9]+(?:\.[0-9]+)*|Appendix\s+[A-Z])', re.I)

line_section = [None] * (len(lines) + 1)
cur = "(前言)"
# 跳過 YAML frontmatter
in_fm = False
fm_done = False
for i, ln in enumerate(lines):
    s = ln.rstrip("\n")
    if i == 0 and s.strip() == "---":
        in_fm = True
        line_section[i] = cur
        continue
    if in_fm:
        line_section[i] = cur
        if s.strip() == "---":
            in_fm = False
            fm_done = True
        continue
    m = heading_re.match(s)
    if m:
        title = m.group(2).strip()
        sm = sid_re.match(title)
        if sm:
            cur = "§" + sm.group(1)
        else:
            cur = title[:40]
    line_section[i] = cur

# 切 block：以空白行為界，連續非空白行 = 一個 block
blocks = []  # (start_line_idx, end_line_idx, text)
buf = []
start = None
for i, ln in enumerate(lines):
    s = ln.rstrip("\n")
    if s.strip() == "":
        if buf:
            blocks.append((start, i - 1, "\n".join(buf)))
            buf = []
            start = None
    else:
        if start is None:
            start = i
        buf.append(s)
if buf:
    blocks.append((start, len(lines) - 1, "\n".join(buf)))

def normalize(text):
    """正規化：去前後空白、壓縮內部空白，供比對。"""
    t = text.strip()
    t = re.sub(r'\s+', ' ', t)
    return t

def is_heading_block(text):
    return all(heading_re.match(l) for l in text.split("\n") if l.strip())

def is_table_block(text):
    # 表格分隔列或多數行含 |
    pipes = sum(1 for l in text.split("\n") if l.strip().startswith("|"))
    return pipes >= 1

# 分組：normalized text -> list of occurrences
groups = defaultdict(list)
for (a, b, text) in blocks:
    norm = normalize(text)
    # 過濾雜訊：太短、純標題、frontmatter
    word_count = len(norm.split())
    if word_count < 6:
        continue
    if is_heading_block(text):
        continue
    groups[norm].append((a, b, text))

# 找重複（出現 >= 2 次）
dupes = [(norm, occ) for norm, occ in groups.items() if len(occ) >= 2]
# 依出現次數排序（多的在前），其次依長度
dupes.sort(key=lambda x: (-len(x[1]), -len(x[0])))

# 統計
total_dupe_groups = len(dupes)
total_redundant = sum(len(occ) - 1 for _, occ in dupes)

out = []
out.append("# BR.md 重複段落報告\n")
out.append(f"> 來源：`{SRC}`（v2.2.7）｜自動偵測，供翻譯時「第一次譯、之後複製貼上」參考\n")
out.append("")
out.append("## 摘要\n")
out.append(f"- 重複段落組數（同一段落出現 ≥ 2 次）：**{total_dupe_groups}** 組")
out.append(f"- 可省下的重複翻譯次數（總出現數 − 各組首次）：**{total_redundant}** 段次")
out.append("")
out.append("> 說明：每組列出「正規化後完全相同」的段落。已排除純標題、過短段落（<6 詞）。")
out.append("> 表格列、清單項也算 block；若同一句在不同章節以相同文字出現即視為重複。")
out.append("")
out.append("**怎麼用：**")
out.append("1. 下方「完全重複」各組 = **一字不差**，翻第一個出現位置後，其餘可直接複製貼上。建議在第一個位置加註「※此段於 X、Y… 重複，譯文同步」。")
out.append("2. 文末「附錄：近似重複」各群 = **高度相似但有小差異**，複製後只需改差異字句（已逐段並列，方便對照）。")
out.append("3. 各組依「出現次數」由多到少排序；位置標出 §章節 與 BR.md 行號。")
out.append("")
out.append("> ⚠️ 同步複製時記得：若某段內含 `[Section X.Y](#...)` 連結或章節參照，貼到別節後要確認參照對象不變（多數情況不變）。")
out.append("")
out.append("---\n")
out.append("## 一、完全重複段落\n")

for idx, (norm, occ) in enumerate(dupes, 1):
    n = len(occ)
    secs = []
    for (a, b, text) in occ:
        sec = line_section[a]
        secs.append(f"{sec}（行 {a+1}）")
    # 顯示原文（取第一筆原始文字，截斷過長）
    sample = occ[0][2]
    display = sample if len(sample) <= 600 else sample[:600] + " …（截斷）"
    out.append(f"### 重複 {idx}　出現 {n} 次\n")
    out.append("**出現位置：**")
    for s in secs:
        out.append(f"- {s}")
    out.append("")
    out.append("**原文：**")
    out.append("")
    out.append("```")
    out.append(display)
    out.append("```")
    out.append("")

# ---- 近似重複（copy 後微調）----
import difflib

# 只取「非完全重複」的代表性 block：每個唯一 norm 取首次出現
exact_norms = set(norm for norm, occ in groups.items() if len(occ) >= 2)
reps = []  # (norm, a, b, text)
seen = set()
for (a, b, text) in blocks:
    norm = normalize(text)
    if len(norm.split()) < 10:
        continue
    if is_heading_block(text):
        continue
    if norm in seen:
        continue
    seen.add(norm)
    reps.append((norm, a, b, text))

# 以相似度 >= 0.80 且 < 1.0 分群（單向掃描，避免 O(n^2) 爆量已用 quick ratio 過濾）
THRESH = 0.82
used = [False] * len(reps)
near_clusters = []
for i in range(len(reps)):
    if used[i]:
        continue
    ni = reps[i][0]
    si = difflib.SequenceMatcher(None, a=ni, b=ni)
    cluster = [i]
    for j in range(i + 1, len(reps)):
        if used[j]:
            continue
        nj = reps[j][0]
        # 長度差過大先跳過
        if abs(len(ni) - len(nj)) > max(len(ni), len(nj)) * 0.4:
            continue
        sm = difflib.SequenceMatcher(None, ni, nj)
        if sm.quick_ratio() < THRESH:
            continue
        r = sm.ratio()
        if THRESH <= r < 1.0:
            cluster.append(j)
    if len(cluster) >= 2:
        for k in cluster:
            used[k] = True
        near_clusters.append(cluster)

# 過濾：(1) 群內須有實際差異（>=2 種 norm）；(2) 須跨 >=2 個不同章節
# （同章節內的雷同多為表格列／並列清單，翻譯時自然一起處理，非「跨節複製」標的）
filtered_near = []
for cluster in near_clusters:
    norms = set(reps[k][0] for k in cluster)
    secs_in = set(line_section[reps[k][1]] for k in cluster)
    if len(norms) >= 2 and len(secs_in) >= 2:
        filtered_near.append(cluster)

if filtered_near:
    out.append("\n---\n")
    out.append("## 附錄：近似重複段落（複製後需微調）\n")
    out.append("> 以下段落彼此**高度相似但不完全相同**（相似度 ≥ 82%），多為 §3.2.2.4.x 各驗證方法的 MPIC／Random Value 註記、")
    out.append("> §7.1.2.x 憑證剖繪的雷同敘述。翻第一個後可複製，再依差異字句（如 `Random Value`／`token`／`Request Token`）微調。\n")
    for ci, cluster in enumerate(filtered_near, 1):
        out.append(f"### 近似群 {ci}（{len(cluster)} 段）\n")
        out.append("**出現位置：**")
        for k in cluster:
            norm, a, b, text = reps[k]
            out.append(f"- {line_section[a]}（行 {a+1}）")
        out.append("")
        # 顯示群內各段，並標出與第一段的差異
        base_text = reps[cluster[0]][3]
        for idx_k, k in enumerate(cluster):
            norm, a, b, text = reps[k]
            tag = "（基準）" if idx_k == 0 else "（差異）"
            disp = text if len(text) <= 500 else text[:500] + " …（截斷）"
            out.append(f"**{line_section[a]} 行 {a+1}** {tag}")
            out.append("")
            out.append("```")
            out.append(disp)
            out.append("```")
            out.append("")

report = "\n".join(out)
with open(sys.argv[1] if len(sys.argv) > 1 else "DUP_REPORT.md", "w", encoding="utf-8") as f:
    f.write(report)

print(f"groups={total_dupe_groups} redundant={total_redundant}")
