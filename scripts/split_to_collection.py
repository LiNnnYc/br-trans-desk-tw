"""
Split BR_T_master.normalized.md into one file per section under src/content/br/.

Run from project root:
    python scripts/split_to_collection.py

For each section heading (`### N.N.N CH-title` preceded by `> ### N.N.N EN-title`):
  - section_id: numeric dotted form, or 'appendix-a' / 'appendix-b'
  - filename: src/content/br/{section_id.replace('.', '-')}.md
  - body: lines between this CH heading and the next heading at ANY depth
  - footnote definitions referenced in body but not defined locally are appended
    (looked up from BR.md)

Front-matter defaults (per HANDOFF discussion):
  status: draft, translator: "免費 AI 初譯 + Claude (Opus) 潤稿",
  original_version: 2.2.7, ballot_refs: [], tags: [], last_updated: today.

Existing files under src/content/br/ are wiped first so re-runs are clean.
"""

from __future__ import annotations

import datetime as dt
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BR_PATH = ROOT / "web-spec-doc" / "BR.md"
MASTER_PATH = ROOT / "web-spec-doc" / "翻譯工作區" / "BR_T_master.normalized.md"
OUT_DIR = ROOT / "src" / "content" / "br"
LOG_PATH = ROOT / "web-spec-doc" / "翻譯工作區" / "split_report.log"

ORIGINAL_VERSION = "2.2.7"
BR_BASE_URL = (
    "https://cabforum.org/working-groups/server/baseline-requirements/requirements/"
)
TRANSLATOR = "免費 AI 初譯 + Claude (Opus) 潤稿"
TODAY = dt.date.today().isoformat()

# Heading lines:
#   `> #### EN title`   (blockquote, optional in some pairs)
#   `#### CH title`     (plain)
PLAIN_HEAD_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
QUOTE_HEAD_RE = re.compile(r"^>\s+(#{1,6})\s+(.+?)\s*$")
WAVE_COMMENT_RE = re.compile(r"^<!--\s*=====")
FOOTNOTE_REF_RE = re.compile(r"\[\^([a-z_][a-z_0-9]*)\]")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^([a-z_][a-z_0-9]*)\]:\s*(.*)$")
NUM_PREFIX_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+(.+)$")
APPENDIX_RE = re.compile(r"^Appendix\s+([A-Z])\b(.*)$", re.IGNORECASE)
APPENDIX_CH_RE = re.compile(r"^附錄\s*([A-Z])\s*[—–-]?\s*(.*)$")


def github_anchor(heading_body: str) -> str:
    """Convert a heading body to a GitHub-style anchor.

    "1.1 Overview" -> "11-overview"
    "3.2.2.4 Validation of Domain Authorization or Control"
        -> "3224-validation-of-domain-authorization-or-control"
    "Appendix A – CAA Contact Tag" -> "appendix-a--caa-contact-tag"
    """
    s = heading_body.lower()
    # Drop footnote markers like [^id]
    s = re.sub(r"\[\^[a-z_0-9]+\]", "", s)
    # Drop characters GitHub strips: anything that isn't alphanum, space, hyphen, or CJK
    # Periods inside section numbers are dropped (so "3.2.2.4" -> "3224")
    s = re.sub(r"[^\w\s\-]", "", s, flags=re.UNICODE)
    s = re.sub(r"\.+", "", s)
    s = re.sub(r"_+", "", s)
    # Collapse runs of whitespace into single hyphen; preserve existing hyphens
    s = re.sub(r"\s+", "-", s.strip())
    return s


def parse_br_titles(text: str) -> dict[str, dict[str, str]]:
    """Returns {section_id_or_appendix_slug: {'en_title': str, 'anchor': str}}."""
    out: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        m = PLAIN_HEAD_RE.match(line)
        if not m:
            continue
        body = m.group(2).strip()
        body_clean = re.sub(r"\[\^[a-z_0-9]+\]", "", body).strip()
        anchor = github_anchor(body)

        am = APPENDIX_RE.match(body_clean)
        if am:
            letter = am.group(1).lower()
            rest = am.group(2).lstrip(" –-—").strip()
            out[f"appendix-{letter}"] = {"en_title": rest, "anchor": anchor}
            continue
        nm = NUM_PREFIX_RE.match(body_clean)
        if not nm:
            continue
        sec_id = nm.group(1).rstrip(".")
        en_title = nm.group(2).strip()
        out[sec_id] = {"en_title": en_title, "anchor": anchor}
    return out


def parse_br_footnotes(text: str) -> dict[str, str]:
    """Returns {footnote_id: definition_text}.

    Footnote definitions may span multiple lines (until a blank line). For the
    BR.md ones we care about, each definition is a single paragraph.
    """
    defs: dict[str, str] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = FOOTNOTE_DEF_RE.match(lines[i])
        if m:
            fid = m.group(1)
            buf = [m.group(2)]
            j = i + 1
            while j < len(lines) and lines[j].strip() != "" and not FOOTNOTE_DEF_RE.match(lines[j]) and not PLAIN_HEAD_RE.match(lines[j]) and not QUOTE_HEAD_RE.match(lines[j]):
                # Continuation lines for multi-line footnotes (indented continuation).
                if lines[j].startswith("    ") or lines[j].startswith("\t"):
                    buf.append(lines[j].strip())
                    j += 1
                else:
                    break
            defs[fid] = " ".join(s for s in buf if s).strip()
            i = j
        else:
            i += 1
    return defs


def extract_section_info_ch(body: str) -> tuple[str | None, str | None]:
    """From a CH heading body, return (section_id, ch_title)."""
    body = body.strip()
    body = re.sub(r"\[\^[a-z_0-9]+\]", "", body).strip()
    am = APPENDIX_CH_RE.match(body)
    if am:
        return f"appendix-{am.group(1).lower()}", am.group(2).strip()
    nm = NUM_PREFIX_RE.match(body)
    if not nm:
        return None, None
    return nm.group(1).rstrip("."), nm.group(2).strip()


def yaml_str(s: str) -> str:
    """Quote a string for YAML front-matter safely."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> int:
    br_text = BR_PATH.read_text(encoding="utf-8")
    master_text = MASTER_PATH.read_text(encoding="utf-8")

    br_titles = parse_br_titles(br_text)
    # Footnote definitions come from the Chinese master (where we have the translated text),
    # not BR.md (English).
    br_footnotes = parse_br_footnotes(master_text)
    print(f"BR.md indexed: {len(br_titles)} headings; master footnotes: {len(br_footnotes)}")

    lines = master_text.splitlines()

    # Pass 1: identify all heading positions.
    # A "section" is identified by a CH heading line (plain `### N ...` or appendix form).
    # If the immediately preceding non-blank line is `> ### N ...`, treat as paired.
    sections: list[dict] = []  # each: {section_id, ch_title, en_title, hashes, line_index, body_start}
    i = 0
    while i < len(lines):
        line = lines[i]
        if WAVE_COMMENT_RE.match(line):
            i += 1
            continue
        m = PLAIN_HEAD_RE.match(line)
        if m and not QUOTE_HEAD_RE.match(line):
            hashes = m.group(1)
            body = m.group(2)
            sec_id, ch_title = extract_section_info_ch(body)
            if sec_id is None:
                i += 1
                continue
            # Look back for `> ##### EN`
            en_title = None
            j = i - 1
            while j >= 0 and lines[j].strip() == "":
                j -= 1
            if j >= 0:
                qm = QUOTE_HEAD_RE.match(lines[j])
                if qm:
                    qbody = qm.group(2).strip()
                    # Extract EN title — for appendices, format is "Appendix X – Title"; for numbered, "N.N.N Title"
                    qbody = re.sub(r"\[\^[a-z_0-9]+\]", "", qbody).strip()
                    am = APPENDIX_RE.match(qbody)
                    if am:
                        en_title = am.group(2).lstrip(" –-—").strip()
                    else:
                        nm = NUM_PREFIX_RE.match(qbody)
                        if nm:
                            en_title = nm.group(2).strip()
            sections.append({
                "section_id": sec_id,
                "ch_title": ch_title,
                "en_title": en_title or br_titles.get(sec_id, {}).get("en_title", ""),
                "hashes": hashes,
                "line_index": i,
                "ch_heading_end": i,  # body starts after this line
                "en_heading_line": j if (j >= 0 and QUOTE_HEAD_RE.match(lines[j])) else None,
            })
            i += 1
            continue
        i += 1

    # Pass 2: determine body range for each section: from end_of(ch_heading) to start_of(next section's EN-or-CH heading)
    for idx, sec in enumerate(sections):
        body_start = sec["ch_heading_end"] + 1
        if idx + 1 < len(sections):
            next_sec = sections[idx + 1]
            # Body ends BEFORE next section's EN heading (if any) or CH heading.
            end = next_sec["en_heading_line"] if next_sec["en_heading_line"] is not None else next_sec["line_index"]
        else:
            end = len(lines)
        sec["body_start"] = body_start
        sec["body_end"] = end

    print(f"Sections detected: {len(sections)}")

    # Clean output dir (preserve any non-md files, just in case)
    if OUT_DIR.exists():
        for p in OUT_DIR.iterdir():
            if p.suffix == ".md":
                p.unlink()
    else:
        OUT_DIR.mkdir(parents=True, exist_ok=True)

    log: list[str] = []
    used_footnotes_total: dict[str, int] = {}
    files_with_footnotes = 0

    for order_idx, sec in enumerate(sections, start=1):
        sec_id = sec["section_id"]
        ch_title = sec["ch_title"]
        en_title = sec["en_title"]
        body_lines = lines[sec["body_start"]:sec["body_end"]]

        # Strip trailing blank lines and wave-separator comments.
        body_lines = [ln for ln in body_lines if not WAVE_COMMENT_RE.match(ln)]
        while body_lines and body_lines[0].strip() == "":
            body_lines.pop(0)
        while body_lines and body_lines[-1].strip() == "":
            body_lines.pop()

        body = "\n".join(body_lines)

        # Footnote handling: if body references [^id] but doesn't define it, append the BR.md definition.
        refs = set(FOOTNOTE_REF_RE.findall(body))
        local_defs = set(FOOTNOTE_DEF_RE.match(ln).group(1) for ln in body_lines if FOOTNOTE_DEF_RE.match(ln))
        missing = refs - local_defs
        if missing:
            files_with_footnotes += 1
            footnote_appendix = []
            for fid in sorted(missing):
                used_footnotes_total[fid] = used_footnotes_total.get(fid, 0) + 1
                definition = br_footnotes.get(fid)
                if definition:
                    footnote_appendix.append(f"[^{fid}]: {definition}")
                else:
                    log.append(f"WARN section {sec_id}: footnote ^{fid} referenced but not found in BR.md")
            if footnote_appendix:
                if body and not body.endswith("\n"):
                    body += "\n"
                body += "\n" + "\n\n".join(footnote_appendix)

        # Compute parent + original URL.
        if "." in sec_id:
            parent = sec_id.rsplit(".", 1)[0]
        elif sec_id.startswith("appendix-"):
            parent = None
        else:
            parent = None
        anchor = br_titles.get(sec_id, {}).get("anchor", "")
        original_url = f"{BR_BASE_URL}#{anchor}" if anchor else BR_BASE_URL

        # Build heading display title for h1: "中文標題" (without section number prefix)
        # The template already prepends section_id when needed.
        title_for_frontmatter = ch_title

        # Front-matter
        slug = sec_id.replace(".", "-")
        fm_lines = [
            "---",
            f"title: {yaml_str(title_for_frontmatter)}",
            f"section_id: {yaml_str(sec_id)}",
        ]
        if parent:
            fm_lines.append(f"parent: {yaml_str(parent)}")
        fm_lines.extend([
            f"order: {order_idx}",
            f"original_url: {yaml_str(original_url)}",
            f"original_version: {yaml_str(ORIGINAL_VERSION)}",
            f"ballot_refs: []",
            f"translator: {yaml_str(TRANSLATOR)}",
            f"last_updated: {TODAY}",
            f"status: draft",
            f"tags: []",
            "---",
            "",
        ])
        if en_title:
            # Keep English heading as commented context for translators (not rendered as <h1>;
            # rendered as a blockquote inside body so bilingual toggle can show/hide).
            fm_lines.append(f"> **{en_title}**")
            fm_lines.append("")
        fm_lines.append(body)

        out_path = OUT_DIR / f"{slug}.md"
        out_path.write_text("\n".join(fm_lines).rstrip() + "\n", encoding="utf-8")
        log.append(f"OK  {slug}.md  ({sec_id} / {ch_title[:30]}, {len(body_lines)} body lines)")

    LOG_PATH.write_text(
        "\n".join(log)
        + f"\n\n--- SUMMARY ---\nsections written: {len(sections)}\n"
        + f"files with appended footnote definitions: {files_with_footnotes}\n"
        + f"footnote appends: {used_footnotes_total}\n",
        encoding="utf-8",
    )
    print(f"\nWrote {len(sections)} files to {OUT_DIR}")
    print(f"Files with appended footnote defs: {files_with_footnotes}")
    print(f"Footnote append tally: {used_footnotes_total}")
    print(f"\nLog: {LOG_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
