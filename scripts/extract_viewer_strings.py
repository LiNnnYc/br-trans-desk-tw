"""抽出 Windows 與 Chrome 憑證檢視器的繁體中文顯示字串，供 `/glossary/cert-fields/` 對照表使用。

`src/config/cert-field-mappings.ts` 裡 Windows／Chrome 兩欄的中文**不是本站翻的**，
是這兩個產品自己的在地化資源。兩邊都會隨版本改字，所以改版後要重抽比對，不要憑印象改。

## 兩個來源怎麼抽

- **Windows**：`%SystemRoot%\\System32\\<語言>\\cryptui.dll.mui`（檢視器版面：欄位名、
  一般分頁、篩選選項）與 `crypt32.dll.mui`（擴充欄位、DN 屬性、EKU、CRL 理由等 OID 名稱）。
  以 `LoadLibraryEx(…AS_DATAFILE)` 載入後逐一 `LoadStringW`，掃字串表。
  同一顆字串在各語言的 MUI 裡 **ID 相同**，兩份對接就得到中英對照。
  ⚠️ 分頁名（一般／詳細資料／憑證路徑）與「顯示(S):」標籤寫在**對話框樣板**、不在字串表，
  這支腳本抽不到，對照表也刻意未收。

- **Chrome**：`<安裝目錄>\\<版本>\\Locales\\zh-TW.pak` 與 `en-US.pak`（pak v5）。
  pak 檔尾端有 alias 表，**內容相同的字串只存一份、其餘 ID 指向它**；
  不解 alias 會漏掉「Issued By」等數百筆（第一次抽就踩過這個坑）。
  憑證檢視器的字串分散在兩個不相鄰的 ID 區段，兩段互補、不重複。

## 用法

    python scripts/extract_viewer_strings.py
        # 只印憑證檢視器相關的 ID 區段（預設，三份來源各一段）

    python scripts/extract_viewer_strings.py --all
        # 印全部字串（Windows 兩支各數百筆、Chrome 一萬多筆）

    python scripts/extract_viewer_strings.py --grep "憑證|Certificate"
        # 以正規表示式篩選（比對英文與中文兩欄）

    python scripts/extract_viewer_strings.py --out <目錄> --all
        # 另存成 TSV（cryptui.tsv／crypt32.tsv／chrome.tsv），預設不寫檔

    python scripts/extract_viewer_strings.py --chrome-only --chrome-dir "D:\\Chrome\\Application"

    python scripts/extract_viewer_strings.py --verify
        # 不印字串，改為核對 src/config/cert-field-mappings.ts 的每一格是否還找得到

輸出為 TSV：`來源<tab>ID<tab>英文<tab>中文`。

## --verify 的判讀

每一格會拆成片段逐一比對（「甲／乙」是兩顆字串；「甲（一般分頁作「乙」）」的註解會剝掉；
`%1!s!`／`$1` 這類參數會換成萬用字元）。三種結果：

- **完全相同**：該片段就是產品現在的字串。
- **部分相符**：片段出現在某顆較長的字串裡，通常是本表刻意簡寫（如 Windows 沒有單獨的
  「延伸」、只有「只有延伸」「憑證延伸」）。**不算失敗，但改版後要掃一眼**——若產品是把舊名
  「加長」（A → A 某某），會落在這一類而不會報錯。
- **找不到**：產品多半改字了，逐筆確認後再改 `cert-field-mappings.ts` 與 `captureInfo`。

exit code：0＝至少抽到一個來源、且（有 --verify 時）沒有「找不到」的片段；
1＝兩個來源都抽不到（非 Windows、找不到 Chrome 等），或 --verify 有片段對不上。
"""

from __future__ import annotations

import argparse
import os
import re
import struct
import sys
from pathlib import Path

# Windows 主控台預設 cp950，印出中文字串時會當場 UnicodeEncodeError 中斷。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent

# 憑證檢視器相關的 ID 區段（2026-09-22 擷取時的實際分布，含前後緩衝）。
# 不是規格、只是觀察結果；改版後若某列抽不到，先用 --all 確認是不是搬到別的區段。
CRYPTUI_RANGES = [(3215, 3270), (3306, 3316), (3420, 3430)]
CRYPT32_RANGES = [(7002, 7060), (8000, 8145), (8500, 8560)]
CHROME_RANGES = [(9601, 9700), (35838, 35920)]

MUI_FILES = ("cryptui.dll.mui", "crypt32.dll.mui")


# ---------------------------------------------------------------- Windows MUI

def load_mui_strings(path: Path, max_id: int) -> dict[int, str]:
    """逐一 LoadStringW 掃出字串表。取不到的 ID 直接跳過（字串表本來就是稀疏的）。"""
    import ctypes
    from ctypes import wintypes

    LOAD_LIBRARY_AS_DATAFILE = 0x00000002

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32.LoadLibraryExW.restype = wintypes.HMODULE
    kernel32.LoadLibraryExW.argtypes = [wintypes.LPCWSTR, wintypes.HANDLE, wintypes.DWORD]
    # 不指定 argtypes 的話，64 位元的 handle 會被當成 int 轉換而 OverflowError
    kernel32.FreeLibrary.argtypes = [wintypes.HMODULE]
    user32.LoadStringW.restype = ctypes.c_int
    user32.LoadStringW.argtypes = [wintypes.HMODULE, wintypes.UINT, wintypes.LPWSTR, ctypes.c_int]

    handle = kernel32.LoadLibraryExW(str(path), None, LOAD_LIBRARY_AS_DATAFILE)
    if not handle:
        raise OSError(f"載入失敗（{ctypes.get_last_error()}）：{path}")
    try:
        out: dict[int, str] = {}
        buf = ctypes.create_unicode_buffer(4096)
        for sid in range(1, max_id + 1):
            n = user32.LoadStringW(handle, sid, buf, len(buf))
            if n > 0:
                out[sid] = buf.value
        return out
    finally:
        kernel32.FreeLibrary(handle)


def mui_path(name: str, lang: str) -> Path:
    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    return Path(system_root) / "System32" / lang / name


# ------------------------------------------------------------------ Chrome pak

def parse_pak(path: Path) -> dict[int, bytes]:
    """解 pak v5：header → 資源索引（id, offset）→ alias 表（id → 索引位置）。"""
    data = path.read_bytes()
    version = struct.unpack_from("<I", data, 0)[0]
    if version != 5:
        raise ValueError(f"只支援 pak v5，這個檔是 v{version}：{path}")
    resource_count, alias_count = struct.unpack_from("<HH", data, 8)
    index_off = 12
    entries = [struct.unpack_from("<HI", data, index_off + i * 6) for i in range(resource_count + 1)]

    out = {entries[i][0]: data[entries[i][1]:entries[i + 1][1]] for i in range(resource_count)}

    alias_off = index_off + (resource_count + 1) * 6
    for i in range(alias_count):
        rid, idx = struct.unpack_from("<HH", data, alias_off + i * 4)
        out[rid] = data[entries[idx][1]:entries[idx + 1][1]]
    return out


def find_chrome_locales(explicit: str | None) -> Path | None:
    """回傳含 *.pak 的 Locales 目錄；未指定時自動找版本最新的安裝。"""
    if explicit:
        given = Path(explicit)
        for cand in (given, given / "Locales"):
            if (cand / "zh-TW.pak").exists():
                return cand
        return None

    roots = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Google/Chrome/Application",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Google/Chrome/Application",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application",
    ]
    found: list[tuple[list[int], Path]] = []
    for root in roots:
        if not root.is_dir():
            continue
        for child in root.iterdir():
            locales = child / "Locales"
            if (locales / "zh-TW.pak").exists():
                parts = [int(p) for p in child.name.split(".") if p.isdigit()]
                found.append((parts, locales))
    if not found:
        return None
    return max(found)[1]


# ---------------------------------------------------------------------- 共用

def join_by_id(base: dict[int, str], target: dict[int, str]) -> list[tuple[int, str, str]]:
    return [(i, base[i], target[i]) for i in sorted(set(base) & set(target))]


def in_ranges(sid: int, ranges: list[tuple[int, int]]) -> bool:
    return any(lo <= sid <= hi for lo, hi in ranges)


def emit(
    source: str,
    rows: list[tuple[int, str, str]],
    ranges: list[tuple[int, int]],
    args: argparse.Namespace,
    out_dir: Path | None,
) -> None:
    if out_dir is not None:
        path = out_dir / f"{source}.tsv"
        with path.open("w", encoding="utf-8", newline="\n") as f:
            for sid, en, zh in rows:
                f.write(f"{sid}\t{en}\t{zh}\n")
        print(f"[{source}] 全部 {len(rows)} 筆 → {path}", file=sys.stderr)

    shown = rows if args.all else [r for r in rows if in_ranges(r[0], ranges)]
    if args.grep:
        pattern = re.compile(args.grep)
        shown = [r for r in shown if pattern.search(r[1]) or pattern.search(r[2])]

    print(f"# === {source}：共 {len(rows)} 筆，列出 {len(shown)} 筆 ===")
    for sid, en, zh in shown:
        # 字串裡的換行與 tab 會破壞 TSV，壓成空白
        print(f"{source}\t{sid}\t{flatten(en)}\t{flatten(zh)}")


def flatten(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


# ------------------------------------------------------------------- --verify

CONFIG_TS = ROOT / "src" / "config" / "cert-field-mappings.ts"

# 對照表裡有些格子是人工寫的說明，不是產品字串，核對時跳過
SKIP_FRAGMENTS = {"顯示 OID", "無篩選功能", "無對應區塊", "—"}

# `key: '…'` 與四類要核對的欄位；zh（本站譯名）不是產品字串，不核對
FIELD_RE = re.compile(
    r"\b(key|winZh|winEn|winRaw|chromeZh|chromeEn|chromeRaw):\s*'((?:[^'\\]|\\.)*)'"
)
PLACEHOLDER_RE = re.compile(r"%\d+![a-zA-Z]!|\$\d+")


def fragments(value: str) -> list[str]:
    """把一格拆成可逐一核對的片段。

    格子裡可能是「甲／乙」兩顆字串、「甲（一般分頁作「乙」）」這種帶註解的寫法，
    或「jurisdictionLocalityName 等原文」這種概括說法。
    """
    out: list[str] = []
    for part in re.split(r"[（）]", value):
        for frag in re.split(r"[／、]", part):
            frag = frag.strip()
            if not frag:
                continue
            quoted = re.search(r"「(.+?)」", frag)
            if quoted:
                # 「…」裡的才是產品字串，前面的「一般分頁作」之類是註解
                out.append(quoted.group(1))
                continue
            frag = re.sub(r"^(一般分頁|詳細資訊|篩選選項)(亦)?作\s*", "", frag)
            frag = re.sub(r"\s*等原文$", "", frag).strip()
            if frag and frag not in SKIP_FRAGMENTS:
                out.append(frag)
    return out


def match_fragment(frag: str, pool: set[str]) -> str:
    """回傳 'exact'（完全相同）、'partial'（出現在某顆字串裡）或 ''（找不到）。"""
    if frag in pool:
        return "exact"
    for s in pool:
        if PLACEHOLDER_RE.search(s):
            # 'Subject Type=%1!s!, …' / '中繼 CA 數目上限：$1' 這類含參數的字串：
            # 參數換成萬用字元再比。'$1 ($2)' 這種幾乎只有參數的字串會誤中任何一格，
            # 因此要求固定文字夠長（4 字以上）才拿來比。
            literals = PLACEHOLDER_RE.split(s)
            if max((len(t) for t in literals), default=0) >= 4:
                pattern = ".+".join(re.escape(t) for t in literals)
                if re.fullmatch(pattern, frag):
                    return "exact"
        if frag in s:
            return "partial"
    return ""


def read_config_cells() -> list[tuple[str, str, str]]:
    """讀出 (row key, 欄位名, 值)；找不到檔案時回空清單。"""
    if not CONFIG_TS.exists():
        return []
    text = CONFIG_TS.read_text(encoding="utf-8")
    cells: list[tuple[str, str, str]] = []
    current = "?"
    for field, value in FIELD_RE.findall(text):
        value = value.replace("\\'", "'")
        if field == "key":
            current = value
        else:
            cells.append((current, field, value))
    return cells


def verify(pools: dict[str, set[str]]) -> int:
    """拿新抽的字串核對 cert-field-mappings.ts 的每一格。回傳 exit code。"""
    cells = read_config_cells()
    if not cells:
        print(f"找不到 {CONFIG_TS}，無從核對。", file=sys.stderr)
        return 1

    missing_pool = [p for p in ("windows_zh", "chrome_zh") if not pools.get(p)]
    if missing_pool:
        print(f"⚠ 這次沒抽到 {'、'.join(missing_pool)}，對應欄位一律跳過。", file=sys.stderr)

    checked = exact = 0
    partials: list[str] = []
    failures: list[str] = []

    for key, field, value in cells:
        product = "windows" if field.startswith("win") else "chrome"
        # Raw 欄位是產品未在地化時畫面上的字，中英兩邊都可能命中
        pool_names = (
            [f"{product}_zh"]
            if field.endswith("Zh")
            else [f"{product}_en"]
            if field.endswith("En")
            else [f"{product}_zh", f"{product}_en"]
        )
        pool: set[str] = set()
        for name in pool_names:
            pool |= pools.get(name, set())
        if not pool:
            continue

        for frag in fragments(value):
            checked += 1
            result = match_fragment(frag, pool)
            if result == "exact":
                exact += 1
            elif result == "partial":
                partials.append(f"  [{key}] {field}：「{frag}」")
            else:
                failures.append(f"  [{key}] {field}：「{frag}」")

    try:
        shown_path = CONFIG_TS.relative_to(ROOT).as_posix()
    except ValueError:                  # 測試時可能指向專案外（甚至別的磁碟）
        shown_path = str(CONFIG_TS)
    print(f"# === verify：{shown_path} ===")
    print(f"核對 {checked} 個片段：完全相同 {exact}、部分相符 {len(partials)}、找不到 {len(failures)}")

    if partials:
        print("\n部分相符（片段出現在較長的字串裡，通常是刻意簡寫，不算錯）：")
        print("\n".join(partials))

    if failures:
        print("\n⚠ 找不到對應字串——可能是產品改字，或這格本來就是人工寫的說明：")
        print("\n".join(failures))
        print("\n逐筆確認後再改 cert-field-mappings.ts，並同步更新 captureInfo 的版本與日期。")
        return 1

    print("\n✓ 每一格都在新抽出來的字串裡找得到。")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="抽出 Windows／Chrome 憑證檢視器的在地化字串")
    parser.add_argument("--all", action="store_true", help="印出全部字串，不限憑證檢視器的 ID 區段")
    parser.add_argument("--grep", metavar="RE", help="以正規表示式篩選（比對英文與中文兩欄）")
    parser.add_argument("--out", metavar="DIR", help="另存 TSV 的目錄（預設不寫檔）")
    parser.add_argument("--lang", default="zh-TW", help="目標語言（預設 zh-TW）")
    parser.add_argument("--base-lang", default="en-US", help="對照語言（預設 en-US）")
    parser.add_argument("--max-id", type=int, default=12000, help="Windows 字串表掃到第幾個 ID（預設 12000）")
    parser.add_argument("--chrome-dir", metavar="DIR", help="Chrome 的 Application 或 Locales 目錄")
    parser.add_argument("--windows-only", action="store_true")
    parser.add_argument("--chrome-only", action="store_true")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="不印字串，改為核對 src/config/cert-field-mappings.ts 的每一格是否仍找得到",
    )
    args = parser.parse_args()

    out_dir = None
    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)

    ok = False
    # --verify 用：產品 → 該產品所有英文／中文字串（不受 ID 區段限制）
    pools: dict[str, set[str]] = {}

    def collect(product: str, rows: list[tuple[int, str, str]]) -> None:
        pools.setdefault(f"{product}_en", set()).update(r[1] for r in rows)
        pools.setdefault(f"{product}_zh", set()).update(r[2] for r in rows)

    if not args.chrome_only:
        if sys.platform != "win32":
            print("[windows] 略過：不是 Windows，讀不到 MUI 資源。", file=sys.stderr)
        else:
            for name in MUI_FILES:
                source = name.split(".")[0]
                base_path = mui_path(name, args.base_lang)
                target_path = mui_path(name, args.lang)
                missing = [p for p in (base_path, target_path) if not p.exists()]
                if missing:
                    for p in missing:
                        print(f"[{source}] 找不到 {p}（該語言套件未安裝？）", file=sys.stderr)
                    continue
                base = load_mui_strings(base_path, args.max_id)
                target = load_mui_strings(target_path, args.max_id)
                rows = join_by_id(base, target)
                collect("windows", rows)
                if not args.verify:
                    ranges = CRYPTUI_RANGES if source == "cryptui" else CRYPT32_RANGES
                    emit(source, rows, ranges, args, out_dir)
                ok = True

    if not args.windows_only:
        locales = find_chrome_locales(args.chrome_dir)
        if locales is None:
            print("[chrome] 找不到 Chrome 的 Locales 目錄，可用 --chrome-dir 指定。", file=sys.stderr)
        else:
            version = locales.parent.name
            print(f"[chrome] 來源：{locales}（版本 {version}）", file=sys.stderr)
            base_pak = parse_pak(locales / f"{args.base_lang}.pak")
            target_pak = parse_pak(locales / f"{args.lang}.pak")
            rows: list[tuple[int, str, str]] = []
            for rid in sorted(set(base_pak) & set(target_pak)):
                try:
                    en = base_pak[rid].decode("utf-8")
                    zh = target_pak[rid].decode("utf-8")
                except UnicodeDecodeError:
                    continue            # pak 裡也放圖片等二進位資源
                rows.append((rid, en, zh))
            collect("chrome", rows)
            if not args.verify:
                emit("chrome", rows, CHROME_RANGES, args, out_dir)
            ok = True

    if not ok:
        print("兩個來源都沒抽到東西。", file=sys.stderr)
        return 1
    if args.verify:
        return verify(pools)
    return 0


if __name__ == "__main__":
    sys.exit(main())
