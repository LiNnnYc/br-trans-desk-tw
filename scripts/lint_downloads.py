"""檢查 /changelog/ 提供的下載檔（HTML／PDF／Markdown）是否齊全、最新版是否跟得上內容。

下載檔是手動產生、進版控的（`node scripts/build_downloads.mjs`），潤稿之後若忘了重跑，
站上的下載檔就會和章節頁對不上。這支由 pre-push hook 呼叫，擋下這種狀態。

檢查：
  1. br-versions.ts 每一列有 `archive` 的，`public/archive/<archive>.{html,pdf,md}` 三個檔都要在。
  2. 最新版（第一列）必須有 `archive`。
  3. 最新版的指紋（src/content/br/*.md 的 SHA-256）要等於 `src/config/downloads-stamp.json`
     記錄的值——不相等代表下載檔產生之後內容又改過。

指紋只涵蓋章節內容。改了 CSS、匯出腳本或 rehype plugin 不會被抓到；那種情況請自行重跑。
行尾先統一成 LF 再算（core.autocrlf=true，工作區行尾不可靠）。

用法：
  python scripts/lint_downloads.py           # 檢查；有問題 exit 1
  python scripts/lint_downloads.py --write   # 蓋章：把目前指紋寫進 stamp（build_downloads.mjs 最後一步呼叫）
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BR_DIR = ROOT / "src" / "content" / "br"
VERSIONS_TS = ROOT / "src" / "config" / "br-versions.ts"
STAMP = ROOT / "src" / "config" / "downloads-stamp.json"
ARCHIVE_DIR = ROOT / "public" / "archive"
EXTS = ("html", "pdf", "md")


def read_versions() -> list[dict[str, str]]:
    ts = VERSIONS_TS.read_text(encoding="utf-8")
    body = ts[ts.index("export const brVersions") :]
    entries = []
    for block in re.findall(r"\{([^{}]*)\}", body):
        fields = dict(re.findall(r"^\s*(\w+):\s*'([^']*)'", block, re.M))
        if "version" in fields:
            entries.append(fields)
    if not entries:
        raise SystemExit("br-versions.ts 讀不到任何版本列；格式可能已變動")
    return entries


def content_hash() -> str:
    h = hashlib.sha256()
    for p in sorted(BR_DIR.glob("*.md")):
        h.update(p.name.encode("utf-8") + b"\0")
        h.update(p.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    return h.hexdigest()


def main() -> int:
    # Windows 主控台預設 cp950，印不出 ✓／✗（pre-push 有設 PYTHONIOENCODING，直接跑的時候沒有）
    sys.stdout.reconfigure(encoding="utf-8")
    versions = read_versions()
    latest = versions[0]

    if "--write" in sys.argv:
        stamp = {
            "version": latest["version"],
            "sourceHash": content_hash(),
            "exportedAt": dt.date.today().isoformat(),
        }
        STAMP.write_text(json.dumps(stamp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"✓ 已蓋章：v{stamp['version']}，{stamp['exportedAt']}")
        return 0

    problems: list[str] = []

    if "archive" not in latest:
        problems.append(f"最新版 v{latest['version']} 在 br-versions.ts 沒有 archive 欄位（沒有下載檔）")

    for v in versions:
        if "archive" not in v:
            continue
        for ext in EXTS:
            f = ARCHIVE_DIR / f"{v['archive']}.{ext}"
            if not f.exists():
                problems.append(f"v{v['version']} 缺下載檔：{f.relative_to(ROOT).as_posix()}")

    if "archive" in latest:
        try:
            stamp = json.loads(STAMP.read_text(encoding="utf-8"))
        except FileNotFoundError:
            stamp = {}
        if stamp.get("version") != latest["version"]:
            problems.append(
                f"下載檔蓋章版本是 v{stamp.get('version', '（無）')}，但最新版是 v{latest['version']}"
            )
        elif stamp.get("sourceHash") != content_hash():
            problems.append(
                f"章節內容在 {stamp.get('exportedAt', '?')} 產生下載檔之後又改過，下載檔已過期"
            )

    if problems:
        print("✗ 下載檔檢查未通過：")
        for p in problems:
            print(f"  · {p}")
        print("\n  重新產生：node scripts/build_downloads.mjs（再把 public/archive/ 與 stamp 一起 commit）")
        return 1

    print(f"✓ 下載檔齊全，v{latest['version']} 與章節內容一致（{stamp['exportedAt']} 產生）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
