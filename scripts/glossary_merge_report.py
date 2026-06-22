"""乾跑（dry-run，不寫檔）：分析 glossary 多來源合併結果。

來源：
  - BR：src/content/br/1-6-1.md（名詞定義）+ 1-6-2.md（縮寫）
  - HiPKICA / TWCA：現有 src/content/glossary/*.md（依 frontmatter source 分類）

依英文詞正規化後合併，報告：合併分布、譯名衝突（一字多義重點）、單來源詞。
"""
import pathlib
import re
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
BR = ROOT / "src" / "content" / "br"
GLOS = ROOT / "src" / "content" / "glossary"
CJK = r"一-鿿"


def norm(en):
    return re.sub(r"\s+", " ", en.strip().lower()).rstrip(".")


def parse_inside_terms(inside):
    inside = inside.strip()
    if ", " in inside:
        parts = [p.strip() for p in inside.split(", ")]
        if re.match(r"^[A-Z0-9/]+$", parts[0]):
            return parts[0], parts[1]  # (acronym, english)
        return None, inside
    return None, inside


# term registry: norm_en -> {"en":, "abbr":, "src": {SRC: term_zh}}
reg = defaultdict(lambda: {"en": None, "abbr": None, "src": {}})


def add(en, zh, source, abbr=None):
    k = norm(en)
    e = reg[k]
    e["en"] = e["en"] or en
    if abbr and not e["abbr"]:
        e["abbr"] = abbr
    e["src"].setdefault(source, zh)


# ---- BR 1-6-1 ----
for line in (BR / "1-6-1.md").read_text(encoding="utf-8").splitlines():
    s = line.strip()
    if s.startswith(">") or not s.startswith("**"):
        continue
    m = re.match(r"\*\*(.+?)\*\*[:：]", s)
    if not m:
        continue
    bold = m.group(1)
    if "（" in bold:
        head, rest = bold.split("（", 1)
        inside = rest.rsplit("）", 1)[0]
        if re.search(rf"[{CJK}]", head):           # 中文（English）；含拉丁縮寫開頭如「CA 金鑰對」
            acr, eng = parse_inside_terms(inside)
            add(eng, head.strip(), "BR", acr)
        else:                                       # English（中譯）  例：Linting（語法檢查）
            add(head.strip(), inside.strip(), "BR")
    else:                                           # 純英文詞（P-Label/WHOIS/XN-Label/Requirements）
        add(bold.strip(), bold.strip(), "BR")

# ---- BR 1-6-2 acronyms ----
for line in (BR / "1-6-2.md").read_text(encoding="utf-8").splitlines():
    s = line.strip()
    if not s.startswith("|"):
        continue
    cells = [c.strip() for c in s.strip("|").split("|")]
    if len(cells) != 2 or cells[0] in ("縮寫", "Acronym") or cells[0].startswith("-"):
        continue
    acr, val = cells
    m = re.match(rf"^([{CJK}].*?)（(.+)）$", val)
    if m:
        add(m.group(2).strip(), m.group(1).strip(), "BR", acr)

# ---- existing glossary (HiPKICA / TWCA) ----
src_count = defaultdict(int)
for path in sorted(GLOS.glob("*.md")):
    text = path.read_text(encoding="utf-8")
    fm = re.search(r"^---\n(.*?)\n---", text, re.S)
    if not fm:
        continue
    body = fm.group(1)

    def field(name):
        mm = re.search(rf'^{name}:\s*"?(.+?)"?\s*$', body, re.M)
        return mm.group(1).strip() if mm else None

    en = field("term_en")
    zh = field("term_zh")
    abbr = field("abbreviation")
    source = field("source") or ""
    if not en or not zh:
        continue
    src = "HiPKICA" if "HiPKICA" in source else ("TWCA" if "TWCA" in source else "OTHER")
    src_count[src] += 1
    add(en, zh, src, abbr)

# ---- report ----
terms = sorted(reg.values(), key=lambda e: norm(e["en"]))
by_n = defaultdict(int)
conflicts = []
only = defaultdict(list)
multi = []
for e in terms:
    srcs = e["src"]
    by_n[len(srcs)] += 1
    if len(srcs) == 1:
        only[next(iter(srcs))].append(e["en"])
    else:
        multi.append(e)
    zhs = set(srcs.values())
    if len(zhs) > 1:
        conflicts.append(e)

print("=" * 78)
print("glossary 多來源合併乾跑報告")
print("=" * 78)
print(f"\n現有 glossary 檔來源分布：{dict(src_count)}")
print(f"合併後唯一英文詞：{len(terms)}")
print(f"  3 來源：{by_n[3]}　2 來源：{by_n[2]}　1 來源：{by_n[1]}")
print(f"  單來源細分：BR-only {len(only['BR'])}　HiPKICA-only {len(only['HiPKICA'])}　TWCA-only {len(only['TWCA'])}　OTHER {len(only.get('OTHER', []))}")

print(f"\n{'='*78}\n譯名衝突（同詞、不同來源譯法不同）共 {len(conflicts)} 個 ← 一字多義重點\n{'='*78}")
for e in conflicts:
    abbr = f" [{e['abbr']}]" if e["abbr"] else ""
    print(f"\n● {e['en']}{abbr}")
    for src, zh in e["src"].items():
        print(f"    {src:8} {zh}")

print(f"\n{'='*78}\n多來源但譯名一致（{len(multi)-len(conflicts)} 個，抽樣 15）\n{'='*78}")
agree = [e for e in multi if len(set(e["src"].values())) == 1]
for e in agree[:15]:
    print(f"  {e['en']:45} {next(iter(e['src'].values()))}  ({'+'.join(e['src'])})")

print(f"\n{'='*78}\nBR-only（BR 有、現有 glossary 無）共 {len(only['BR'])}，抽樣 20\n{'='*78}")
for en in sorted(only["BR"])[:20]:
    print(f"  {en}")
