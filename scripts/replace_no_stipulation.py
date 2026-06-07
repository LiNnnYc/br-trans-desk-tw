"""一次性：把 BR 譯稿中的「無規定。」改為「未作規定。」（no stipulation 章節）。

只動中文行；英文 blockquote `> No stipulation.` 不受影響。
"""
import pathlib

BR_DIR = pathlib.Path(__file__).resolve().parent.parent / "src" / "content" / "br"
OLD = "無規定。"
NEW = "未作規定。"

changed = 0
for path in sorted(BR_DIR.glob("*.md")):
    text = path.read_text(encoding="utf-8")
    if OLD in text:
        path.write_text(text.replace(OLD, NEW), encoding="utf-8")
        changed += 1
        print(f"  {path.name}")

print(f"Modified {changed} files")
