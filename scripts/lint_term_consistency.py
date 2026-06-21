"""譯名一致性偵測：以 §1.6.1／§1.6.2 為定版，掃描第 3 章以後的譯名分歧。

定版來源：
  - src/content/br/1-6-1.md  名詞定義（**中譯（English）**：…）
  - src/content/br/1-6-2.md  縮寫（| ACR | 中譯（English） |）

偵測對象：第 3 章（含）以後章節檔（含附錄）中 `變體中譯（English）` 形式，
其「（English）」前的中文若與定版中譯不符 → 列為候選分歧。

只偵測「帶英文括註」的出現（最可靠）；純中文無括註者本腳本不處理。
未在 §1.6.1／§1.6.2 定義的英文詞一律跳過。
"""
import pathlib
import re
import sys
from collections import defaultdict

BR = pathlib.Path(__file__).resolve().parent.parent / "src" / "content" / "br"
CJK = r"一-鿿"


def parse_inside_terms(inside):
    """『ADN, Authorization Domain Name』→ ['ADN', 'Authorization Domain Name']。"""
    inside = inside.strip()
    if ", " in inside:
        parts = [p.strip() for p in inside.split(", ")]
        # 僅當第一段像縮寫（全大寫/含/數字）才拆，否則視為單一英文詞
        if re.match(r"^[A-Z0-9/]+$", parts[0]):
            return parts
        return [inside]
    return [inside]


def load_canonical():
    cmap = {}          # english or acronym -> canonical chinese
    multi = set()      # 中譯含 / 或多形，標記為需人工
    # ---- 1-6-1 ----
    for line in (BR / "1-6-1.md").read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith(">") or not s.startswith("**"):
            continue
        m = re.match(r"\*\*(.+?)\*\*[:：]", s)
        if not m:
            continue
        bold = m.group(1)
        if "（" not in bold:
            continue  # 純英文詞（P-Label/WHOIS/XN-Label/Requirements）→ 不譯，跳過
        head, rest = bold.split("（", 1)
        inside = rest.rsplit("）", 1)[0]
        if not re.match(rf"^[{CJK}]", head):
            continue  # English-led（Linting（語法檢查））→ 內文用英文，跳過
        chi = head.strip()
        for term in parse_inside_terms(inside):
            cmap[term] = chi
            if "/" in chi or "／" in chi:
                multi.add(term)
    # ---- 1-6-2 ----
    for line in (BR / "1-6-2.md").read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) != 2:
            continue
        acr, val = cells
        if acr in ("縮寫", "Acronym", "-", "") or acr.startswith("-"):
            continue
        m = re.match(rf"^([{CJK}].*?)（(.+)）$", val)
        if not m:
            continue
        chi, eng = m.group(1).strip(), m.group(2).strip()
        cmap.setdefault(eng, chi)
        cmap.setdefault(acr, chi)
    return cmap, multi


def chapter_of(path):
    name = path.stem
    if name.startswith("appendix"):
        return 99
    head = name.split("-")[0]
    return int(head) if head.isdigit() else -1


def main():
    cmap, multi = load_canonical()
    # 以長詞優先，避免短英文詞為長詞子字串時誤判
    terms = sorted(cmap.keys(), key=len, reverse=True)

    findings = defaultdict(list)  # term -> [(file, variant_chinese)]
    renderings = defaultdict(set)  # term -> {chinese variants seen}

    for path in sorted(BR.glob("*.md")):
        if chapter_of(path) < 3:
            continue
        text = path.read_text(encoding="utf-8")
        for term in terms:
            canon = cmap[term]
            # 捕捉 （term） 前的中文連續串（含 ·／）
            for m in re.finditer(rf"([{CJK}·／/]{{1,20}})（{re.escape(term)}）", text):
                preceding = m.group(1)
                renderings[term].add(preceding)
                # 若中文串「結尾」即為定版中譯 → 視為一致
                if preceding.endswith(canon):
                    continue
                # 若定版中譯結尾即為此中文串（定版較長、此處簡稱）→ 標記但分類較弱
                findings[term].append((path.name, preceding))

    print("=" * 78)
    print("譯名分歧候選（『（English）』前中文 ≠ §1.6.1／§1.6.2 定版）")
    print("=" * 78)
    if not findings:
        print("（無）")
    total = 0
    for term in sorted(findings, key=lambda t: cmap[t]):
        canon = cmap[term]
        rows = findings[term]
        total += len(rows)
        flag = " ⚠多形定版" if term in multi else ""
        print(f"\n● {term} → 定版「{canon}」{flag}")
        seen = defaultdict(list)
        for fn, variant in rows:
            seen[variant].append(fn)
        for variant, files in sorted(seen.items()):
            ufiles = sorted(set(files))
            shown = ", ".join(ufiles[:8]) + (" …" if len(ufiles) > 8 else "")
            print(f"    「{variant}」  ×{len(files)}  [{shown}]")

    print(f"\n分歧候選共 {total} 處，涉及 {len(findings)} 個術語。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
