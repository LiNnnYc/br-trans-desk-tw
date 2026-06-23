# -*- coding: utf-8 -*-
"""一次性遷移：glossary schema 升級。

1. 每個 source 新增 version（同 source 可能有不同版本）。
   - 由 ref 字串解析 vX.Y.Z；BR（站內路徑 ref）預設 v2.2.7（BR.md 來源版本）。
2. 新增 recommended_definition：總覽頁顯示的推薦解釋，與 source 解耦、可獨立編輯。
   - 回填預設值＝recommended_source 的定義（找不到則取第一個來源）。

以 pyyaml 解析 frontmatter，再以固定格式重新輸出（保留 block scalar 樣式與欄位順序）。
非冪等，僅執行一次。執行：PYTHONUTF8=1 python scripts/glossary_add_version_and_recdef.py
"""
import re
import pathlib
import yaml

GLOSSARY = pathlib.Path("src/content/glossary")
BR_DEFAULT_VERSION = "v2.2.7"
VER_RE = re.compile(r"v\d+(?:\.\d+)*")


def detect_version(source: str, ref: str | None) -> str | None:
    if ref:
        m = VER_RE.search(ref)
        if m:
            return m.group(0)
    if source == "BR":
        return BR_DEFAULT_VERSION
    return None


def q(s: str) -> str:
    """雙引號標量；轉義內含的反斜線與雙引號。"""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def block(text: str, indent: int) -> str:
    pad = " " * indent
    lines = text.rstrip("\n").split("\n")
    return "\n".join(pad + ln if ln else pad.rstrip() for ln in lines)


def emit(data: dict) -> str:
    out = ["---"]
    out.append(f"term_en: {q(data['term_en'])}")
    if data.get("abbreviation"):
        out.append(f"abbreviation: {q(data['abbreviation'])}")
    out.append(f"recommended_zh: {q(data['recommended_zh'])}")
    out.append("recommended_definition: |")
    out.append(block(data["recommended_definition"], 2))
    if data.get("recommended_source"):
        out.append(f"recommended_source: {q(data['recommended_source'])}")
    if data.get("first_seen_at"):
        out.append(f"first_seen_at: {q(data['first_seen_at'])}")
    out.append("sources:")
    for s in data["sources"]:
        out.append(f"  - source: {q(s['source'])}")
        if s.get("version"):
            out.append(f"    version: {q(s['version'])}")
        out.append(f"    term_zh: {q(s['term_zh'])}")
        out.append("    definition: |")
        out.append(block(s["definition"], 6))
        if s.get("ref"):
            out.append(f"    ref: {q(s['ref'])}")
    tags = data.get("tags") or []
    if tags:
        out.append("tags:")
        for t in tags:
            out.append(f"  - {q(t)}")
    else:
        out.append("tags: []")
    out.append("---")
    out.append("")
    return "\n".join(out)


def main() -> None:
    files = sorted(GLOSSARY.glob("*.md"))
    changed = 0
    for fp in files:
        raw = fp.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n?", raw, re.S)
        if not m:
            print("SKIP (no frontmatter):", fp.name)
            continue
        data = yaml.safe_load(m.group(1))

        # 1. 每個 source 補 version
        for s in data["sources"]:
            if not s.get("version"):
                v = detect_version(s["source"], s.get("ref"))
                if v:
                    s["version"] = v

        # 2. recommended_definition 回填（取自 recommended_source，否則首個來源）
        rec_src = data.get("recommended_source")
        rec_def = None
        if rec_src:
            for s in data["sources"]:
                if s["source"] == rec_src:
                    rec_def = s["definition"]
                    break
        if rec_def is None:
            rec_def = data["sources"][0]["definition"]
        data["recommended_definition"] = rec_def

        fp.write_text(emit(data), encoding="utf-8")
        changed += 1

    print(f"done. {changed}/{len(files)} files rewritten.")


if __name__ == "__main__":
    main()
