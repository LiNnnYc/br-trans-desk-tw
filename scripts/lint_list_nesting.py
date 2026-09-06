"""偵測「縮排清單被第 0 欄 blockquote 截斷 → render 掉一層」的譯稿寫法。

背景（TRANSLATION_CONVENTIONS.md §6.1）：本站採 Style A 中英交錯，英文原文寫成
`> ` blockquote。CommonMark 規定**寫在第 0 欄的 blockquote 會關掉當前清單**，因此
若一個縮排的清單項前面隔著第 0 欄的 blockquote，它不會續接上層清單，而會被當成
新的頂層清單 → 畫面上比同層兄弟少一層縮排。

    2. CA 應（MUST）…：
       1. **（a）** …

    > 2. **(b)** The CA MAY …      ← 第 0 欄：把上層清單關掉了

       2. **（b）** …               ← 掉到第 1 層，與（a）不同層 ✗

修法是把該段 blockquote 縮排到清單項的內容欄（`   > …`），詳見 §6.1。

## 判準

只有「該縮排項**確實有**一個上層清單項」時才算掉層。中英兩側各自維護一個
清單堆疊：

- 第 0 欄的**非清單段落**（散文／標題／表格）會結束清單 → 清空堆疊。
- 第 0 欄的 **blockquote** 是對照用的另一語言，不清空堆疊，但標記「已截斷」。
- 遇到縮排清單項時，若堆疊中仍有更淺的項目（＝有上層），且中途被截斷過 → 命中。

這條件排除了常見的誤報：`  a.` `  b.` 這種前面只有散文引言、2 格縮排純屬排版
的頂層清單（CommonMark 對頂層清單忽略 ≤3 格前導空白），它們沒有上層清單項，
render 結果與意圖一致。

本 lint 純掃描原始 markdown，不需要先 build。

用法：
    python scripts/lint_list_nesting.py            # 掃 src/content/br
    python scripts/lint_list_nesting.py <路徑…>    # 掃指定檔案

exit code：0 = 乾淨；1 = 有發現。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BR_DIR = ROOT / "src" / "content" / "br"

FRONT_MATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.S)
FENCE_RE = re.compile(r"^\s*(?:>\s*)*(?:```|~~~)")
# 清單標記：- * + / 1. 1) / a. a) / i. i)
LIST_ITEM_RE = re.compile(
    r"^(?P<indent> *)(?:[-*+]|\d+[.)]|[a-zA-Z][.)]|[ivxIVX]+[.)])\s+\S"
)
COL0_BLOCKQUOTE_RE = re.compile(r"^>")


class ListTracker:
    """單一語言側的清單堆疊；回報「縮排項失去上層」的行。"""

    def __init__(self) -> None:
        self.stack: list[int] = []   # 目前開著的清單項縮排
        self.interrupted = False     # 中途被第 0 欄 blockquote 截斷

    def feed(self, indent: int, is_list_item: bool) -> bool:
        """吃一行內容；回傳 True 表示這行是「掉層」的清單項。"""
        if not is_list_item:
            # 第 0 欄的非清單內容（散文／標題／表格）＝清單真的結束了
            if indent == 0:
                self.stack.clear()
                self.interrupted = False
            # 縮排的續行屬於清單項內部，不影響堆疊
            return False

        while self.stack and self.stack[-1] >= indent:
            self.stack.pop()
        # 有更淺的項目還開著＝這個縮排項理應是它的子項；被截斷過就會掉層
        hit = indent > 0 and self.interrupted and bool(self.stack)
        self.stack.append(indent)
        self.interrupted = False
        return hit


def scan(text: str) -> list[tuple[int, str, str]]:
    """回傳 [(行號, 側別, 該行內容)]，行號以 markdown 內文第一行為 1。"""
    hits: list[tuple[int, str, str]] = []
    cn = ListTracker()
    en = ListTracker()
    in_fence = False

    for lineno, raw in enumerate(text.split("\n"), start=1):
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence or not raw.strip():
            continue

        if COL0_BLOCKQUOTE_RE.match(raw):
            # 英文側：拆掉 `> ` 後照同一套判準
            inner = re.sub(r"^> ?", "", raw)
            if not inner.strip():
                # blockquote 內的空行（單獨一個 `>`）：等同空行，不影響清單堆疊。
                # 少了這條，它會被當成第 0 欄散文而把英文側堆疊清空 → 漏抓。
                cn.interrupted = True
                continue
            m = LIST_ITEM_RE.match(inner)
            indent = len(m.group("indent")) if m else len(inner) - len(inner.lstrip(" "))
            if en.feed(indent, bool(m)):
                hits.append((lineno, "英文側", raw))
            # 對中文側而言，這是「另一語言的對照段」：不結束清單，但會截斷
            cn.interrupted = True
            continue

        # 縮排的 blockquote（§6.1 的正確寫法）：留在清單項內，兩側都不受影響
        if raw.lstrip().startswith(">"):
            continue

        m = LIST_ITEM_RE.match(raw)
        indent = len(m.group("indent")) if m else len(raw) - len(raw.lstrip(" "))
        if cn.feed(indent, bool(m)):
            hits.append((lineno, "中文側", raw))
        # 對英文側而言，中文段落代表上一段 blockquote 已經結束：
        # 下一段 `> ` 是**新的** blockquote，其中的清單不會續接前一段（與中文側對稱）
        en.interrupted = True

    return hits


def main() -> int:
    args = sys.argv[1:]
    files = [Path(a) for a in args] if args else sorted(BR_DIR.glob("*.md"))

    total = 0
    flagged = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        body = FRONT_MATTER_RE.sub("", text)
        offset = text.count("\n", 0, len(text) - len(body))
        hits = scan(body)
        if not hits:
            continue
        flagged += 1
        total += len(hits)
        try:
            rel = f.relative_to(ROOT)
        except ValueError:
            rel = f  # 掃專案外的檔案（如比對用的暫存副本）
        print(f"\n{rel}")
        for lineno, side, raw in hits:
            print(f"  L{lineno + offset:<4} [{side}] {raw.strip()[:88]}")

    print(
        f"\n掃描 {len(files)} 檔："
        + (f"**{flagged} 檔 / {total} 處**需修正" if total else "乾淨")
    )
    if total:
        print("修法見 TRANSLATION_CONVENTIONS.md §6.1"
              "（把該段 blockquote 縮排到清單項的內容欄）。")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
