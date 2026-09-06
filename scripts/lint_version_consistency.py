"""發布前把關：確認全庫沒有處在「升版做到一半」的混版狀態。

升版時 414 個章節檔不可能一次改完，中途必然是「部分 2.2.9、部分 2.2.7」。這種狀態
**本地 commit 沒問題**（升版本來就要分次提交），但**絕不能發布出去**——站上會同時
存在兩個版本的條文，而版本徽章只會顯示其中一個，客服照著引用就會出錯。

因此本檢查設計成在 `git push` 前擋（安裝方式見 RUNBOOK §1.1，升版流程見 §2.4），
日常 build／dev／commit 完全不受影響。

檢查項目：

1. `src/content/br/*.md` 的 `original_version` 是否全庫一致
2. 該版本是否等於 `src/config/br-versions.ts` 的 `brVersions[0].version`
   （＝版本徽章與全站顯示的版本）
3. 是否還有 `status: draft` / `outdated` 的檔案（＝該版尚未譯完或審完）

用法：
    python scripts/lint_version_consistency.py

exit code：0 = 可發布；1 = 尚不可發布（訊息會說明卡在哪一項）。
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BR_DIR = ROOT / "src" / "content" / "br"
VERSIONS_TS = ROOT / "src" / "config" / "br-versions.ts"

VERSION_RE = re.compile(r'^original_version:\s*"([^"]+)"', re.M)
STATUS_RE = re.compile(r"^status:\s*(\w+)", re.M)
# brVersions 陣列中第一個 version 欄位＝本站發布版
DECLARED_RE = re.compile(r"brVersions[^=]*=\s*\[\s*\{[^}]*?version:\s*'([^']+)'", re.S)

PUBLISHABLE_STATUS = {"translated", "reviewed"}


def main() -> int:
    files = sorted(BR_DIR.glob("*.md"))
    if not files:
        print("✗ 找不到任何章節檔")
        return 1

    versions: dict[str, list[str]] = collections.defaultdict(list)
    statuses: dict[str, list[str]] = collections.defaultdict(list)
    for f in files:
        text = f.read_text(encoding="utf-8")
        vm = VERSION_RE.search(text)
        sm = STATUS_RE.search(text)
        versions[vm.group(1) if vm else "（缺 original_version）"].append(f.stem)
        statuses[sm.group(1) if sm else "（缺 status）"].append(f.stem)

    declared_m = DECLARED_RE.search(VERSIONS_TS.read_text(encoding="utf-8"))
    declared = declared_m.group(1) if declared_m else None

    problems: list[str] = []

    # ── 1. 全庫版本是否一致 ────────────────────────────────────────
    if len(versions) > 1:
        ranked = sorted(versions.items(), key=lambda kv: -len(kv[1]))
        detail = "、".join(f"{v} {len(names)} 檔" for v, names in ranked)
        problems.append(f"混版：{detail}")
        # 不用「檔數多寡」推論哪個是目標版——升版初期少數才是新版，猜錯會把訊息講反。
        # 除了最大群以外的每一群都列出檔名，兩個方向的落單檔都看得到。
        for ver, names in ranked[1:]:
            sample = "、".join(names[:10])
            more = f"…等 {len(names)} 檔" if len(names) > 10 else ""
            problems.append(f"  {ver}（{len(names)} 檔）：{sample}{more}")
    corpus_version = next(iter(versions)) if len(versions) == 1 else None

    # ── 2. 是否與 br-versions.ts 宣告的版本相符 ─────────────────────
    if declared is None:
        problems.append("讀不到 src/config/br-versions.ts 的 brVersions[0].version")
    elif corpus_version and corpus_version != declared:
        problems.append(
            f"章節檔是 {corpus_version}，但 br-versions.ts 宣告本站發布版為 {declared}"
            "——版本徽章會顯示錯誤的版本"
        )

    # ── 3. 是否還有未譯完／未審完的檔案 ─────────────────────────────
    pending = {s: n for s, n in statuses.items() if s not in PUBLISHABLE_STATUS}
    if pending:
        detail = "、".join(f"{s} {len(n)} 檔" for s, n in sorted(pending.items()))
        problems.append(f"仍有未完成的章節：{detail}")
        for s, names in sorted(pending.items()):
            sample = "、".join(names[:8])
            more = f"…等 {len(names)} 檔" if len(names) > 8 else ""
            problems.append(f"  {s}：{sample}{more}")

    # ── 輸出 ──────────────────────────────────────────────────────
    total = len(files)
    if not problems:
        print(f"✓ 可發布：{total} 檔全數為 {corpus_version}，狀態皆已完成"
              f"（br-versions.ts 宣告 {declared}）")
        return 0

    print(f"✗ 尚不可發布（{total} 檔）")
    for p in problems:
        print(f"  {p}")
    print()
    print("升版做到一半是正常的，本地 commit 不受影響。")
    print("全部更新完成後再 push；若確定要推出未完成狀態：git push --no-verify")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
