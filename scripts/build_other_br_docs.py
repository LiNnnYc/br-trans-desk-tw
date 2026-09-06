"""從 cabforum.org 的 BR「Documents」頁原文產生 `src/md/other-br-docs.md`（中文索引）。

輸入：`web-spec-doc/BR_側邊欄/documents_index.md`（自 cabforum.org 抓下的 markdown）
輸出：`src/md/other-br-docs.md`

這頁是**連結索引**而非條文散文，故不採 Style A 中英對照（英文側與中文側會幾乎
一模一樣）。文件名稱與投票案編號是識別碼，保留英文原樣；翻譯的是外圍語句
（現行版本／歷史版本／由投票案…通過採納）。

上游相對連結解析：
  `CA-Browser-Forum-TLS-BR-2.2.9.pdf` → <documents 頁目錄>/…
  `/2026/07/01/ballot-…`              → <站台根>/…

BR 升版後重抓原文即可重跑（`--write` 才實際寫入）。**日期或句型無法解析時會拋錯**，
不會默默輸出錯誤內容——寧可中斷讓人檢查。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "web-spec-doc" / "BR_側邊欄" / "documents_index.md"
OUT = ROOT / "src" / "md" / "other-br-docs.md"

SITE = "https://cabforum.org"
DOCS_BASE = f"{SITE}/working-groups/server/baseline-requirements/documents/"

REF_DEF_RE = re.compile(r"^\[([^\]]+)\]:\s*(\S+)")
REF_LINK_RE = re.compile(r"\[([^\]]*)\]\[([^\]]+)\]")

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}

# 「14 September, 2012」「3 October 2013」「16-March-2015」「22 Nov. 2011」
DATE_RE = re.compile(
    r"^(\d{1,2})[\s-]+([A-Za-z]+)\.?,?[\s-]+(\d{4})$"
)


def zh_date(s: str) -> str:
    m = DATE_RE.match(s.strip().rstrip("."))
    if not m:
        raise ValueError(f"無法解析日期：{s!r}")
    day, mon, year = m.group(1), m.group(2).lower().rstrip("."), m.group(3)
    if mon not in MONTHS:
        raise ValueError(f"無法解析月份：{s!r}")
    return f"{year} 年 {MONTHS[mon]} 月 {int(day)} 日"


def resolve(url: str) -> str:
    if url.startswith(("http://", "https://")):
        return url
    if url.startswith("/"):
        return SITE + url
    return DOCS_BASE + url


def main() -> int:
    write = "--write" in sys.argv
    text = SRC.read_text(encoding="utf-8")
    body = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    # 上游原頁有一個標籤為空、且跨行的壞連結（`[` 換行 `][221]`），它不指向任何
    # 可辨識的文件，直接清掉；不清的話會把後面的正常條目一起卡住。
    body = re.sub(r"\[\s*\n\s*\]\[[^\]]+\]\s*", "", body)

    refs: dict[str, str] = {}
    for line in body.split("\n"):
        m = REF_DEF_RE.match(line)
        if m:
            # CommonMark 的參照連結標籤不分大小寫（上游就有 [SC085v2] 定義／
            # [sc085v2] 引用的例子），故一律以小寫為鍵
            refs[m.group(1).lower()] = resolve(m.group(2))

    def inline(s: str) -> str:
        """把 `[文字][ref]` 換成 `[文字](絕對網址)`。"""
        def rep(m):
            label, ref = m.group(1), m.group(2).lower()
            if ref not in refs:
                raise ValueError(f"找不到連結定義 [{m.group(2)}]")
            return f"[{label.strip() or m.group(2)}]({refs[ref]})"
        return REF_LINK_RE.sub(rep, s)

    out: list[str] = []
    stats = {"entry": 0, "heading": 0, "plain": 0}

    for raw in body.split("\n"):
        line = raw.strip()
        if not line or REF_DEF_RE.match(line):
            continue

        if line.startswith("#"):
            zh = {
                "Baseline Requirements": "《基本要求》",
                "Current Version": "現行版本",
                "Previous Versions": "歷史版本",
                "Public Discussion Drafts": "公開討論草案",
            }
            title = line.lstrip("#").strip()
            level = len(line) - len(line.lstrip("#"))
            if title not in zh:
                raise ValueError(f"未預期的標題：{title!r}")
            out.append(f"{'#' * level} {zh[title]}")
            stats["heading"] += 1
            continue

        # 少數殘缺行（原頁面有個空連結 `[\n][221]`）：略過空標籤的孤立連結
        if re.fullmatch(r"\[\s*\]\[[^\]]+\]", line):
            continue

        m = re.match(
            r"^(?P<title>\[[^\]]*\]\[[^\]]+\])"
            r"(?:\s*[–-])?"
            r"(?:\s*\((?P<paren>[^()]*)\))?"
            r"(?:\s*[–-]\s*(?P<rest>.*))?$",
            line,
        )
        if not m:
            raise ValueError(f"無法解析條目：{line!r}")

        parts = [inline(m.group("title"))]

        paren = (m.group("paren") or "").strip()
        if paren:
            if paren.lower() == "translated into japanese":
                parts.append("（日文譯本）")
            elif "redlined" in paren.lower():
                # 只改連結「文字」，不可對整串做字串替換——URL 裡也有 redlined
                # （…-redlined.pdf），一起換掉會產生指向不存在檔案的死連結。
                parts.append(f"（{inline(re.sub(r'\[redlined\]', '[修訂對照]', paren, flags=re.I))}）")
            else:
                raise ValueError(f"未預期的括號內容：{paren!r}")

        rest = (m.group("rest") or "").strip()
        if rest:
            parts.append("——" + translate_rest(rest, inline))

        out.append("- " + "".join(parts))
        stats["entry"] += 1

    md = "\n".join(render(out)) + "\n"
    print(f"標題 {stats['heading']} 個、條目 {stats['entry']} 筆、連結定義 {len(refs)} 個")
    if write:
        OUT.write_text(md, encoding="utf-8")
        print(f"已寫入 {OUT.relative_to(ROOT)}（{len(md.splitlines())} 行）")
    else:
        print("（未加 --write，僅試算；以下為前 12 行）")
        print("\n".join(md.split("\n")[:12]))
    return 0


def translate_rest(rest: str, inline) -> str:
    """處理『– adopted by Ballot X on <date>』這類尾句。"""
    # adopted on <date> with an Effective Date of <date>
    m = re.match(r"^adopted on (?P<d1>.+?) with an Effective Date of (?P<d2>.+)$", rest)
    if m:
        return f"於 {zh_date(m.group('d1'))}通過採納，並自 {zh_date(m.group('d2'))}生效"

    m = re.match(r"^adopted on (?P<d>.+)$", rest)
    if m:
        return f"於 {zh_date(m.group('d'))}通過採納"

    m = re.match(r"^effective\s+(?P<d>.+)$", rest, re.I)
    if m:
        return f"自 {zh_date(m.group('d'))}生效"

    m = re.match(r"^adopted by (?P<who>.+?)(?:\s+on\s+(?P<d>[\d].*))?$", rest)
    if m:
        who = m.group("who").strip()
        is_ballot = who.lower().startswith("ballot")
        who = re.sub(r"^Ballots?\s+", "", who, flags=re.I)
        who = inline(who).replace(" and ", "、").replace(", ", "、")
        head = f"由投票案 {who}" if is_ballot else f"由 {who}"
        # 中文日期後直接接「通過採納」；沒有日期時才需空格隔開拉丁連結與中文
        tail = f"於 {zh_date(m.group('d'))}" if m.group("d") else " "
        return f"{head}{tail}通過採納"

    raise ValueError(f"無法解析尾句：{rest!r}")


def render(items: list[str]) -> list[str]:
    """標題與清單之間補空行。"""
    out: list[str] = []
    for it in items:
        if it.startswith("#"):
            if out:
                out.append("")
            out.append(it)
            out.append("")
        else:
            out.append(it)
    return out


if __name__ == "__main__":
    raise SystemExit(main())
