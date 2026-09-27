"""比對上游兩個版本的 BR.md，列出哪些章節變動、對應到本站哪些檔案。

升版時 414 節裡通常只有一二十節真的改過。這支腳本決定升版是「一週」還是「一個月」
——`TRANSLATION_CONVENTIONS.md` §10 步驟 2 早就預告了它。

## 舊版原文從哪來

兩種來源都吃，優先序如下（都不必手動保存檔案）：

1. `upstream/BR_archive/BR-v<版本>.md`——升版前封存的副本（檔名帶版本號，好找）
2. `git show br-v<版本>:upstream/BR.md`——tag 裡的原文

## 用法

    python scripts/diff_br_versions.py                      # 自動挑最新的封存版比對
    python scripts/diff_br_versions.py --old br-v2.2.7      # 指定 git tag
    python scripts/diff_br_versions.py --old <路徑>          # 指定檔案
    python scripts/diff_br_versions.py --show-diff 7.1.2.7  # 看某節的實際差異
    python scripts/diff_br_versions.py --mark-outdated --write
        # 把「內容變動」的章節檔 status 改為 outdated（--write 才實際寫入）

exit code：0＝比對完成（不論有無變動）；1＝來源取不到或解析失敗。
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

# Windows 主控台預設 cp950，原文含 ✔（§3.2.2.4 方法能力對照表）等字元時
# `--show-diff` 會在 print 當場 UnicodeEncodeError 中斷。統一改用 UTF-8 輸出。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
BR_MD = ROOT / "upstream" / "BR.md"
ARCHIVE_DIR = ROOT / "upstream" / "BR_archive"
CONTENT_DIR = ROOT / "src" / "content" / "br"

# `# 1. INTRODUCTION` / `## 1.1 Overview` / `# Appendix A – …` / `## A.1. CAA Methods`
HEAD_RE = re.compile(
    r"^(#{1,6})\s+((?:\d+(?:\.\d+)*)|Appendix\s+([A-Z])|([A-Z])(\.\d+(?:\.\d+)*))\.?\s"
)
VERSION_RE = re.compile(r"^subtitle:\s*Version\s+(\S+)\s*$", re.M)
ARCHIVE_NAME_RE = re.compile(r"^BR-v(.+)\.md$")


def section_id(line: str) -> str:
    """把標題行換成本站的 section_id（附錄用 appendix-<letter> 前綴）。"""
    m = HEAD_RE.match(line)
    assert m, line
    if m.group(3):                      # Appendix A
        return f"appendix-{m.group(3).lower()}"
    if m.group(4):                      # A.1.1
        return f"appendix-{m.group(4).lower()}{m.group(5)}"
    return m.group(2)


def split_sections(text: str) -> dict[str, str]:
    """切成 {section_id: 該節內文}；內文不含標題行本身。"""
    out: dict[str, str] = {}
    cur: str | None = None
    buf: list[str] = []
    for line in text.split("\n"):
        if HEAD_RE.match(line):
            if cur is not None:
                out[cur] = "\n".join(buf).strip("\n")
            cur = section_id(line)
            buf = []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out[cur] = "\n".join(buf).strip("\n")
    return out


def normalise(body: str) -> list[str]:
    """比對用：去掉行尾空白與空行，避免純排版差異被當成內容變動。"""
    return [ln.rstrip() for ln in body.split("\n") if ln.strip()]


def _display_path(p: Path) -> str:
    """顯示用的路徑：能相對於 repo 就相對，否則原樣。

    relative_to() 對 repo 外的絕對路徑會丟 ValueError——比對暫存區裡的候選原文
    （如升版前先試算 /tmp 的新版）時就會炸在這行，而這只是要印個標籤而已。
    """
    if p.is_absolute():
        try:
            return str(p.relative_to(ROOT))
        except ValueError:
            return str(p)
    return str(p)


def load_old(spec: str | None) -> tuple[str, str]:
    """回傳 (來源說明, 內文)。spec 可為 git tag、檔案路徑，或 None（自動挑）。"""
    if spec is None:
        candidates = sorted(ARCHIVE_DIR.glob("BR-v*.md")) if ARCHIVE_DIR.is_dir() else []
        if candidates:
            spec = str(candidates[-1])
        else:
            tags = subprocess.run(
                ["git", "tag", "--list", "br-v*", "--sort=v:refname"],
                cwd=ROOT, capture_output=True, text=True,
            ).stdout.split()
            if not tags:
                print("✗ 找不到任何封存原文（BR_archive/BR-v*.md）或 br-v* tag，"
                      "請用 --old 指定", file=sys.stderr)
                raise SystemExit(1)
            spec = tags[-1]

    p = Path(spec)
    if p.is_file():
        return f"檔案 {_display_path(p)}", p.read_text(encoding="utf-8")

    r = subprocess.run(
        ["git", "show", f"{spec}:upstream/BR.md"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0:
        print(f"✗ 既不是檔案也取不到 git 物件：{spec}", file=sys.stderr)
        raise SystemExit(1)
    return f"git tag {spec}", r.stdout


def content_file(sid: str) -> Path:
    return CONTENT_DIR / (sid.replace(".", "-") + ".md")


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--old", help="舊版來源：git tag 或檔案路徑（預設自動挑最新封存）")
    ap.add_argument("--new", default=str(BR_MD), help="新版原文路徑（預設 upstream/BR.md）")
    ap.add_argument("--show-diff", metavar="SECTION", help="顯示指定章節的逐行差異")
    ap.add_argument("--mark-outdated", action="store_true",
                    help="把內容變動的章節檔 status 改為 outdated")
    ap.add_argument("--write", action="store_true", help="實際寫入（否則僅試算）")
    args = ap.parse_args()

    old_label, old_text = load_old(args.old)
    new_text = Path(args.new).read_text(encoding="utf-8")

    old_v = (VERSION_RE.search(old_text) or [None, "?"])[1]
    new_v = (VERSION_RE.search(new_text) or [None, "?"])[1]
    old_s, new_s = split_sections(old_text), split_sections(new_text)

    print(f"舊：v{old_v}（{old_label}）　{len(old_s)} 節")
    print(f"新：v{new_v}（{args.new}）　{len(new_s)} 節")
    if old_v == new_v:
        print("\n⚠️ 兩邊版本號相同，可能還沒換上新原文。")

    added = [s for s in new_s if s not in old_s]
    removed = [s for s in old_s if s not in new_s]
    changed = [s for s in new_s if s in old_s and normalise(old_s[s]) != normalise(new_s[s])]
    same = len(new_s) - len(added) - len(changed)

    if args.show_diff:
        sid = args.show_diff
        if sid not in old_s or sid not in new_s:
            print(f"\n✗ 找不到章節 {sid}")
            return 1
        print(f"\n── §{sid} 差異 ──")
        for ln in difflib.unified_diff(normalise(old_s[sid]), normalise(new_s[sid]),
                                       f"v{old_v}", f"v{new_v}", lineterm="", n=2):
            print("  " + ln[:160])
        return 0

    def show(title: str, ids: list[str], with_file: bool = True) -> None:
        print(f"\n{title}：{len(ids)} 節")
        for sid in sorted(ids, key=lambda s: (s.startswith("appendix"), s)):
            f = content_file(sid)
            mark = "" if not with_file else ("  " + (str(f.relative_to(ROOT)) if f.exists()
                                                    else "（本站無對應檔）"))
            print(f"   §{sid}{mark}")

    print(f"\n未變：{same} 節")
    if changed: show("內容變動", changed)
    if added: show("新增（本站需新建檔案）", added)
    if removed: show("刪除（本站檔案需處理）", removed)
    if not (changed or added or removed):
        print("\n✓ 兩版之間沒有章節內容差異")

    if args.mark_outdated and changed:
        n = 0
        for sid in changed:
            f = content_file(sid)
            if not f.exists():
                continue
            t = f.read_text(encoding="utf-8")
            # `[\w-]+`：狀態值可能含連字號（pending-review）。用 `\w+` 的話，
            # 對已經是 pending-review 的檔案重跑會寫出 `status: outdated-review`
            # ——Zod 會擋下，但檔案已經被寫壞了。
            t2 = re.sub(r"^status:\s*[\w-]+", "status: outdated", t, count=1, flags=re.M)
            if t2 != t:
                n += 1
                if args.write:
                    f.write_text(t2, encoding="utf-8")
        print(f"\n{'已' if args.write else '將'}把 {n} 個章節檔的 status 改為 outdated"
              + ("" if args.write else "（加 --write 才實際寫入）"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
