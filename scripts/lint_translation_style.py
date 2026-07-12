"""翻譯風格 lint（Phase A）：以已審閱基準掃第 4 章以後 draft 的譯名分歧與機翻 artifact。

基準來源（信任度高→低）：
  1. §1.6.1／§1.6.2 定版（src/content/br/1-6-1.md、1-6-2.md）— BR 自身定義，最高信任
  2. glossary recommended_zh（src/content/glossary/*.md）— 參考；各 source 的 term_zh 視為可接受變體
  3. CURATED — 手動策展的機翻 artifact／片語（如 method 誤譯「模式」、控管權誤成控制權）

偵測（僅掃 chapter ≥ 4；第 1–3 章已人工審閱，作為風格基準不掃）：
  A. 標註錨定：`中文（English）` 形式中，「（English）」前中文若非定版中譯 → 分歧候選（§1.6 與 glossary 分開列）
  B. 策展 artifact：字面掃 CURATED 的已知誤譯字串

輸出：console 摘要 + 詳細報告寫入 web-spec-doc/翻譯工作區/風格審查_PhaseA報告.md
用法：PYTHONUTF8=1 python scripts/lint_translation_style.py
"""
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
BR = ROOT / "src" / "content" / "br"
GLO = ROOT / "src" / "content" / "glossary"
REPORT = ROOT / "web-spec-doc" / "翻譯工作區" / "風格審查_PhaseA報告.md"
CJK = r"一-鿿"

# ── 策展機翻 artifact（字面掃，bad → 建議）；由 Phase B 逐步擴充 ──────────
CURATED = [
    # (regex, 建議, 說明)
    (r"網域授權或控制", "網域授權或控管", "Domain Authorization or Control 定版為「網域授權或控管權」（§3）"),
    (r"模式", "方法／方式", "method 常被免費 AI 誤譯為「模式」；前三章一律「方法」，請對照原文確認"),
    # ── 2026-07-12 Phase B ch4 揪出的系統性同形誤譯／陸味詞 ──
    (r"擴充套件", "擴充欄位", "extension 誤譯為「套件」（=軟體套件）；定版「擴充欄位」"),
    (r"擴充元件", "擴充欄位", "extension 誤譯為「元件」（=component）；定版「擴充欄位」"),
    (r"延伸欄位", "擴充欄位", "extension 定版統一為「擴充欄位」（對齊 ch1-3 審閱定版，2026-07-12）"),
    (r"延伸金鑰使用", "擴充金鑰使用", "Extended Key Usage 定版「擴充金鑰使用」（同 extension→擴充）"),
    (r"授權資訊存取", "憑證機構資訊存取", "Authority Information Access：Authority=憑證機構，非 authorization"),
    (r"運營", "營運", "operate 陸味用詞；台灣定版「營運」"),
    (r"數據", "資料", "data 陸味用詞；台灣定版「資料」"),
    (r"公開信任", "公開信賴", "Publicly-Trusted 定版「公開信賴」"),
    (r"培訓", "訓練", "train 陸味用詞；台灣定版「訓練」"),
    (r"預憑證", "預簽憑證", "Precertificate 定版「預簽憑證」（對齊 ch1-3；預備憑證→預簽憑證）"),
    (r"授權的 OCSP 回應", "具權威性的 OCSP 回應", "authoritative 誤譯為「授權」（≠authorized）"),
]


def parse_inside_terms(inside):
    inside = inside.strip()
    if ", " in inside:
        parts = [p.strip() for p in inside.split(", ")]
        if re.match(r"^[A-Z0-9/]+$", parts[0]):
            return parts
        return [inside]
    return [inside]


def load_br_canonical():
    """§1.6.1／§1.6.2 → {english: canonical_zh}, multi_set。"""
    cmap, multi = {}, set()
    for line in (BR / "1-6-1.md").read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith(">") or not s.startswith("**"):
            continue
        m = re.match(r"\*\*(.+?)\*\*[:：]", s)
        if not m:
            continue
        bold = m.group(1)
        if "（" not in bold:
            continue
        head, rest = bold.split("（", 1)
        inside = rest.rsplit("）", 1)[0]
        if not re.match(rf"^[{CJK}]", head):
            continue
        chi = head.strip()
        for term in parse_inside_terms(inside):
            cmap[term] = chi
            if "/" in chi or "／" in chi:
                multi.add(term)
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


def load_glossary():
    """glossary → {english: (recommended_zh, {accepted_variants})}。"""
    gmap = {}
    for path in GLO.glob("*.md"):
        txt = path.read_text(encoding="utf-8")
        te = re.search(r'^term_en:\s*"?(.+?)"?\s*$', txt, re.M)
        rz = re.search(r'^recommended_zh:\s*"?(.+?)"?\s*$', txt, re.M)
        ab = re.search(r'^abbreviation:\s*"?(.+?)"?\s*$', txt, re.M)
        if not te or not rz:
            continue
        rec = rz.group(1).strip()
        variants = {rec}
        for m in re.finditer(r'^\s+term_zh:\s*"?(.+?)"?\s*$', txt, re.M):
            variants.add(m.group(1).strip())
        gmap[te.group(1).strip()] = (rec, variants)
        if ab:
            gmap[ab.group(1).strip()] = (rec, variants)
    return gmap


def chapter_of(path):
    name = path.stem
    if name.startswith("appendix"):
        return 99
    head = name.split("-")[0]
    return int(head) if head.isdigit() else -1


def expand_accepted(canon_list):
    """把含 / ／ 的多形定版拆成個別可接受變體。"""
    acc = set()
    for c in canon_list:
        for part in re.split(r"[/／]", c):
            part = part.strip()
            if part:
                acc.add(part)
    return acc


def anchored_scan(text, term, canon_list):
    """回傳該檔中 `(中文)（term）` 前中文不屬 accepted 的變體清單。

    錨定字元集含空格與 ASCII 英數，以容納譯名中間夾 Latin 的情形
    （如「保留 IP 位址」「Onion 網域名稱」），endswith 比對確保正確性。
    """
    accepted = expand_accepted(canon_list)
    out = []
    for m in re.finditer(rf"([{CJK}A-Za-z0-9 ·／/]{{1,28}})（{re.escape(term)}）", text):
        preceding = m.group(1).strip()
        if any(preceding.endswith(a) for a in accepted if a):
            continue
        out.append(preceding)
    return out


def main():
    br_map, multi = load_br_canonical()
    glo_map = load_glossary()
    br_terms = sorted(br_map.keys(), key=len, reverse=True)
    # glossary 只用 BR 未定義者，避免與 §1.6 衝突（§1.6 優先）
    glo_terms = sorted([t for t in glo_map if t not in br_map], key=len, reverse=True)

    br_find = defaultdict(list)   # term -> [(file, variant)]
    glo_find = defaultdict(list)
    cur_find = defaultdict(list)  # (regex說明) -> [(file, line, ctx)]
    per_file = defaultdict(int)

    targets = [p for p in sorted(BR.glob("*.md")) if chapter_of(p) >= 4]
    for path in targets:
        text = path.read_text(encoding="utf-8")
        fn = path.name
        for term in br_terms:
            for v in anchored_scan(text, term, [br_map[term]]):
                br_find[term].append((fn, v))
                per_file[fn] += 1
        for term in glo_terms:
            rec, variants = glo_map[term]
            for v in anchored_scan(text, term, list(variants)):
                glo_find[term].append((fn, v))
                per_file[fn] += 1
        # 策展 artifact（只掃非 blockquote CN 行）
        in_fm = False
        for i, line in enumerate(text.splitlines(), 1):
            s = line.strip()
            if i == 1 and s == "---":
                in_fm = True
                continue
            if in_fm:
                if s == "---":
                    in_fm = False
                continue
            if s.startswith(">") or s.startswith("[^"):
                continue
            for rgx, sug, note in CURATED:
                for mm in re.finditer(rgx, line):
                    st, en = max(0, mm.start() - 12), min(len(line), mm.end() + 12)
                    cur_find[(rgx, sug, note)].append((fn, i, line[st:en]))
                    per_file[fn] += 1

    # ---- 輸出 ----
    lines = []
    def w(x=""):
        lines.append(x)

    w("# 翻譯風格審查 Phase A 報告（機械掃描）")
    w()
    w("> 掃描範圍：第 4 章以後 draft（第 1–3 章為已審閱基準，不掃）。")
    w("> 此為機械候選，**須人工對照英文原文確認**；標註錨定用 endswith 定版比對，仍可能有邊界誤報。")
    w()

    w("## 1. 譯名分歧 — 對 §1.6.1／§1.6.2 定版（高信任）")
    w()
    if not br_find:
        w("（無）")
    for term in sorted(br_find, key=lambda t: br_map[t]):
        flag = " ⚠多形定版" if term in multi else ""
        w(f"### {term} → 定版「{br_map[term]}」{flag}")
        seen = defaultdict(list)
        for fn, v in br_find[term]:
            seen[v].append(fn)
        for v, files in sorted(seen.items()):
            uf = sorted(set(files))
            w(f"- 「{v}」 ×{len(files)}　[{', '.join(uf[:10])}{' …' if len(uf) > 10 else ''}]")
        w()

    w("## 2. 譯名分歧 — 對 glossary recommended_zh（參考，信任度較低）")
    w()
    w("> 注意：glossary 為多來源；BR 本身可能刻意採不同譯（如 Certificate Profile：BR「憑證剖繪」／HiPKI「憑證格式剖繪」）。此節僅供參考。")
    w()
    if not glo_find:
        w("（無）")
    for term in sorted(glo_find, key=lambda t: glo_map[t][0]):
        w(f"### {term} → glossary 建議「{glo_map[term][0]}」")
        seen = defaultdict(list)
        for fn, v in glo_find[term]:
            seen[v].append(fn)
        for v, files in sorted(seen.items()):
            uf = sorted(set(files))
            w(f"- 「{v}」 ×{len(files)}　[{', '.join(uf[:10])}{' …' if len(uf) > 10 else ''}]")
        w()

    w("## 3. 策展機翻 artifact（字面掃）")
    w()
    if not cur_find:
        w("（無）")
    for (rgx, sug, note), rows in cur_find.items():
        w(f"### 疑似：`{rgx}` → 建議「{sug}」")
        w(f"　{note}")
        for fn, i, ctx in rows:
            w(f"- {fn} L{i}：…{ctx.strip()}…")
        w()

    w("## 4. 各檔旗標數排名（Phase B 切入參考）")
    w()
    ranked = sorted(per_file.items(), key=lambda kv: -kv[1])
    for fn, n in ranked:
        w(f"- {fn}　{n}")
    if not ranked:
        w("（無旗標）")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # console 摘要
    tb = sum(len(v) for v in br_find.values())
    tg = sum(len(v) for v in glo_find.values())
    tc = sum(len(v) for v in cur_find.values())
    print(f"掃描 {len(targets)} 檔（chapter ≥ 4）")
    print(f"  §1.6 定版分歧：{tb} 處 / {len(br_find)} 術語")
    print(f"  glossary 參考分歧：{tg} 處 / {len(glo_find)} 術語")
    print(f"  策展 artifact：{tc} 處")
    print(f"  有旗標的檔：{len(per_file)} 個（最多前 8）：")
    for fn, n in ranked[:8]:
        print(f"    {fn}: {n}")
    print(f"\n報告已寫入：{REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
