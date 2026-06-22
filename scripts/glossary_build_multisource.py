"""一次性：把 glossary 重建為多來源（一字多義）結構。

來源：BR（1-6-1 定義 + 1-6-2 縮寫）、現有 glossary 的 HiPKICA / TWCA 條目。
依英文詞合併 → 刪除舊 glossary/*.md → 產生 1 英文詞 1 檔（full-english slug）。

recommended_zh：BR 有則用 BR 定版，否則 HiPKICA，再否則 TWCA。
見 memory project_glossary_multisource。
"""
import pathlib
import re
import sys
from collections import OrderedDict

ROOT = pathlib.Path(__file__).resolve().parent.parent
BR = ROOT / "src" / "content" / "br"
GLOS = ROOT / "src" / "content" / "glossary"
CJK = r"一-鿿"
SRC_ORDER = ["BR", "HiPKICA", "TWCA"]


def norm(en):
    return re.sub(r"\s+", " ", en.strip().lower()).rstrip(".")


def slugify(en):
    s = en.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def parse_head(head):
    """**…** 內文 → (term_en, term_zh, abbr)。"""
    if "（" in head:
        chead, rest = head.split("（", 1)
        inside = rest.rsplit("）", 1)[0].strip()
        if re.search(rf"[{CJK}]", chead):           # 中文（English）
            if ", " in inside:
                parts = [p.strip() for p in inside.split(", ")]
                if re.match(r"^[A-Z0-9/]+$", parts[0]):
                    return parts[1], chead.strip(), parts[0]
            return inside, chead.strip(), None
        return chead.strip(), inside, None          # English（中譯）
    return head.strip(), head.strip(), None          # 純英文（P-Label 等）


# registry: norm_en -> dict(en, abbr, first_seen, src=OrderedDict{SRC: {zh, def, ref}})
reg = {}


def entry(en):
    k = norm(en)
    if k not in reg:
        reg[k] = {"en": en, "abbr": None, "first_seen": None, "src": OrderedDict()}
    return reg[k]


def add_src(en, src, zh, definition, ref, abbr=None, first_seen=None):
    e = entry(en)
    if not e["en"] or len(en) > len(e["en"]):
        e["en"] = en
    if abbr and not e["abbr"]:
        e["abbr"] = abbr
    if first_seen and not e["first_seen"]:
        e["first_seen"] = first_seen
    if src not in e["src"]:
        e["src"][src] = {"zh": zh, "def": definition, "ref": ref}


# ---------- BR §1.6.1 ----------
body = (BR / "1-6-1.md").read_text(encoding="utf-8")
body = re.split(r"\n---\n", body, maxsplit=1)[1] if body.startswith("---") else body
lines = body.splitlines()
BOUNDARY = re.compile(r"^>\s*\*\*([^*]+?)\*\*\s*[:：]")


def is_boundary(line):
    m = BOUNDARY.match(line)
    return m and m.group(1).strip() not in ("Note", "註", "Definitions")


# 收集每個 entry 的行範圍
idxs = [i for i, ln in enumerate(lines) if is_boundary(ln)]
idxs.append(len(lines))
for a, b in zip(idxs, idxs[1:]):
    blk = lines[a:b]
    cn_lines = [ln for ln in blk if not ln.lstrip().startswith(">")]
    # 找第一個中文粗體定義行
    head = defstart = None
    rest_lines = []
    for j, ln in enumerate(cn_lines):
        m = re.match(r"^\*\*(.+?)\*\*\s*[:：](.*)$", ln.strip())
        if m:
            head = m.group(1)
            defstart = m.group(2).strip()
            rest_lines = [x for x in cn_lines[j + 1:]]
            break
    if head is None:
        continue
    term_en, term_zh, abbr = parse_head(head)
    deftext = defstart
    tail = "\n".join(rest_lines).strip()
    if tail:
        deftext = (deftext + "\n" + tail).strip()
    deftext = re.sub(r"\n{3,}", "\n\n", deftext)
    add_src(term_en, "BR", term_zh, deftext or term_zh, "/server-cert-br/1-6-1/", abbr)

# ---------- BR §1.6.2 acronyms ----------
for line in (BR / "1-6-2.md").read_text(encoding="utf-8").splitlines():
    s = line.strip()
    if not s.startswith("|"):
        continue
    cells = [c.strip() for c in s.strip("|").split("|")]
    if len(cells) != 2 or cells[0] in ("縮寫", "Acronym") or cells[0].startswith("-"):
        continue
    acr, val = cells
    m = re.match(rf"^([{CJK}].*?)（(.+)）$", val)
    if not m:
        continue
    zh, eng = m.group(1).strip(), m.group(2).strip()
    e = entry(eng)
    if not e["abbr"]:
        e["abbr"] = acr
    if "BR" not in e["src"]:
        # §1.6.2-only：無 §1.6.1 定義，給縮寫表說明
        e["src"]["BR"] = {
            "zh": zh,
            "def": f"《基本要求》第 1.6.2 節縮寫表所列，全稱為「{eng}」。",
            "ref": "/server-cert-br/1-6-2/",
        }


# ---------- 現有 glossary（HiPKICA / TWCA）----------
def parse_frontmatter(text):
    m = re.search(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    fm = m.group(1).splitlines()
    data, i = {}, 0
    while i < len(fm):
        line = fm[i]
        km = re.match(r"^(\w+):\s*(.*)$", line)
        if km:
            key, val = km.group(1), km.group(2)
            if val.strip() in ("|", ">", "|-", ">-"):
                block, i = [], i + 1
                while i < len(fm) and (fm[i].startswith("  ") or fm[i].strip() == ""):
                    block.append(fm[i][2:] if fm[i].startswith("  ") else fm[i])
                    i += 1
                data[key] = "\n".join(block).strip()
                continue
            data[key] = val.strip().strip('"')
        i += 1
    return data


for path in sorted(GLOS.glob("*.md")):
    d = parse_frontmatter(path.read_text(encoding="utf-8"))
    en, zh = d.get("term_en"), d.get("term_zh")
    if not en or not zh:
        continue
    source = d.get("source") or ""
    src = "HiPKICA" if "HiPKICA" in source else ("TWCA" if "TWCA" in source else "OTHER")
    add_src(en, src, zh, d.get("definition") or zh, source or None,
            abbr=d.get("abbreviation"), first_seen=d.get("first_seen_at"))


# ---------- 輸出 ----------
def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def block(s, indent):
    pad = " " * indent
    out = ["|"]
    for ln in s.split("\n"):
        out.append(pad + ln if ln else "")
    return "\n".join(out)


# 刪除舊檔（已全部讀入記憶體）
old = list(GLOS.glob("*.md"))
if len(reg) < 100:
    print(f"ERROR: 合併僅 {len(reg)} 詞，異常，中止（未刪檔）")
    sys.exit(1)
for f in old:
    f.unlink()

slugs = {}
written = 0
for k in sorted(reg):
    e = reg[k]
    slug = slugify(e["en"])
    if slug in slugs:
        slug = f"{slug}-{slugify(e['abbr']) if e['abbr'] else len(slugs)}"
    slugs[slug] = e["en"]

    ordered = [s for s in SRC_ORDER if s in e["src"]] + \
              [s for s in e["src"] if s not in SRC_ORDER]
    rec_src = ordered[0]
    rec_zh = e["src"][rec_src]["zh"]

    fm = ["---", f"term_en: {q(e['en'])}"]
    if e["abbr"]:
        fm.append(f"abbreviation: {q(e['abbr'])}")
    fm.append(f"recommended_zh: {q(rec_zh)}")
    fm.append(f"recommended_source: {q(rec_src)}")
    if e["first_seen"]:
        fm.append(f"first_seen_at: {q(e['first_seen'])}")
    fm.append("sources:")
    for s in ordered:
        sd = e["src"][s]
        fm.append(f"  - source: {q(s)}")
        fm.append(f"    term_zh: {q(sd['zh'])}")
        fm.append(f"    definition: {block(sd['def'], 6)}")
        if sd["ref"]:
            fm.append(f"    ref: {q(sd['ref'])}")
    fm.append("tags: []")
    fm.append("---")
    (GLOS / f"{slug}.md").write_text("\n".join(fm) + "\n", encoding="utf-8")
    written += 1

print(f"刪除舊檔 {len(old)}，寫入新檔 {written}")
