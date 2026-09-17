"""
一次性匯入腳本：依 web-spec-doc/縮寫及定義.txt 產生 src/content/acronyms/*.md（一縮寫一檔、多來源）。

txt 每行格式：`<縮寫><tab 或 2 個以上空白><中文>（<English>）--<來源>`，中文或英文可能缺。
推薦譯名優先序比照 glossary：BR → HiPKICA → TWCA → BR 翻譯小站（只取有中文的來源）。

用法：python scripts/generate_acronyms.py [--force]   （預設不覆寫既有檔）
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TXT = ROOT / "web-spec-doc" / "縮寫及定義.txt"
OUT = ROOT / "src" / "content" / "acronyms"

SOURCE_MAP = {
    "TLS BR": "BR",
    "中華電信 HiPKI CPS": "HiPKICA",
    "TWCA GLOBAL CA CPS": "TWCA",
    "BR 翻譯小站": "BR 翻譯小站",
}
PRIORITY = ["BR", "HiPKICA", "TWCA", "BR 翻譯小站"]

# BR 來源：多數在 §1.6.2 縮寫表；少數不在表內者指向實際出處
BR_REF = {"MPIC": "/server-cert-br/1-6-1/", "TLS BR": "/server-cert-br/1-5/"}


def source_meta(src: str, acronym: str) -> dict:
    if src == "BR":
        return {"version": "v2.3.0", "ref": BR_REF.get(acronym, "/server-cert-br/1-6-2/")}
    if src == "HiPKICA":
        return {"version": "v1.2", "ref": "HiPKICA CP/CPS v1.2 附錄 1"}
    if src == "TWCA":
        return {"version": "v3.2", "ref": "TWCA Global CPS v3.2 縮寫（Acronyms and Abbreviations）"}
    return {"version": "20260916查"}


def slugify(acronym: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", acronym.lower()).strip("-")


def q(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def parse():
    entries: dict[str, list[dict]] = {}
    order: list[str] = []
    for n, line in enumerate(TXT.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        m = re.match(r"^(.+?)(?:\t| {2,})\s*(.*)$", line)
        if not m:
            sys.exit(f"第 {n} 行無法解析：{line}")
        acronym, rest = m.group(1).strip(), m.group(2).strip()
        body, _, src_raw = rest.rpartition("--")
        src_raw = src_raw.strip().rstrip("）").strip()  # 第 83 行尾端多一個「）」
        if src_raw not in SOURCE_MAP:
            sys.exit(f"第 {n} 行來源不明：{src_raw}")
        pm = re.match(r"^(.*?)（(.*)）$", body.strip())
        zh, en = (pm.group(1).strip(), pm.group(2).strip()) if pm else (body.strip(), "")
        if acronym not in entries:
            entries[acronym] = []
            order.append(acronym)
        entries[acronym].append({"source": SOURCE_MAP[src_raw], "term_zh": zh, "expansion_en": en})
    return order, entries


def render(acronym: str, sources: list[dict]) -> str:
    sources = sorted(sources, key=lambda s: PRIORITY.index(s["source"]))
    rec = next(s for s in sources if s["term_zh"])
    rec_en = rec["expansion_en"] or next((s["expansion_en"] for s in sources if s["expansion_en"]), "")
    out = ["---", f"acronym: {q(acronym)}"]
    if rec_en:
        out.append(f"expansion_en: {q(rec_en)}")
    out += [f"recommended_zh: {q(rec['term_zh'])}", f"recommended_source: {q(rec['source'])}", "sources:"]
    for s in sources:
        meta = source_meta(s["source"], acronym)
        out.append(f"  - source: {q(s['source'])}")
        if "version" in meta:
            out.append(f"    version: {q(meta['version'])}")
        if s["term_zh"]:
            out.append(f"    term_zh: {q(s['term_zh'])}")
        if s["expansion_en"]:
            out.append(f"    expansion_en: {q(s['expansion_en'])}")
        if "ref" in meta:
            out.append(f"    ref: {q(meta['ref'])}")
    out += ["tags: []", "---", ""]
    return "\n".join(out)


def main():
    force = "--force" in sys.argv
    order, entries = parse()
    OUT.mkdir(parents=True, exist_ok=True)
    written = skipped = 0
    for acronym in order:
        path = OUT / f"{slugify(acronym)}.md"
        if path.exists() and not force:
            skipped += 1
            continue
        path.write_text(render(acronym, entries[acronym]), encoding="utf-8", newline="\n")
        written += 1
    print(f"縮寫 {len(order)} 個（來源列 {sum(len(v) for v in entries.values())}）；寫入 {written}、略過既有 {skipped}")


if __name__ == "__main__":
    main()
