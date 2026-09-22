#!/usr/bin/env python3
"""把站台 logo 的原圖向量化成 public/br-logo.svg。

原圖是 `web-spec-doc/BR_logo/BR_Desk_Logo_2.png`（使用者請 ChatGPT 依第一版機甲稿重畫的
**扁平風**版本：1616×932，只有五個平塗色、邊緣乾淨、沒有漸層與顆粒噪點）。

⚠️ 這點是關鍵：第一版原圖（`ChatGPT Image …02_33_28.png`）是照片式材質，描邊只會把噪點
一起描進去，當時繞了四輪都做不乾淨（詳見 HANDOFF「頁首站台 logo」段）。這張新圖本來就是
色塊分明的扁平稿，所以直接按色分層描邊就很準——整支腳本因此單純很多。

流程：裁到 alpha 邊界 → 縮到描邊解析度 → 每個像素歸到最近的原圖色 → 四層遮罩各自描邊
→ 由後往前疊成扁平 SVG。**金色那一層（「翻譯小站」＋齒輪＋飾線）不描圖、改用字型輪廓與幾何重畫**
——原圖那四個字是筆畫細、字腔窄又包深色描邊的裝飾字體，縮到頁首尺寸會糊掉（使用者退過）。

    pip install potracer
    python scripts/build_logo.py                  # 重新產生 public/br-logo.svg
    python scripts/build_logo.py --detail 3       # 描邊解析度倍率（越大越細、檔案越肥）
    python scripts/build_logo.py --art-cyan       # 青色保留原圖的 #33c8fb（預設換成站台主色）
    python scripts/build_logo.py --weight 600     # 「翻譯小站」的字重（那一層是重畫的，見下）

⚠️ 產出的 SVG 已進版控，平時不需要重跑。檢視產出可用 `pip install resvg-py` 把 SVG 描繪成 PNG
（本機沒有 cairo，cairosvg 裝了也跑不動）。

`scripts/build_logo_pop.py` 是被這支取代的 POP 風版本，保留備查。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import potrace
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "web-spec-doc" / "BR_logo" / "BR_Desk_Logo_2.png"
OUT = ROOT / "public" / "br-logo.svg"

CANVAS_W = 760  # 輸出畫布寬；高度依原圖比例算

# 原圖實際用到的五個平塗色（k-means 量出來的）。分類時比對這些值，
# 輸出時換成 PALETTE_OUT——差別只有青色：預設換成站台主色，讓 logo 與全站色系一致。
PALETTE_SRC = {
    "ink": (4, 25, 44),
    "slate": (65, 97, 127),
    "steel": (140, 160, 181),
    "cyan": (51, 200, 251),
    "gold": (249, 206, 74),
}
PALETTE_OUT = {
    "ink": "#0a1a2c",     # 外框與飾板底
    "slate": "#41617f",   # 板金暗面
    "steel": "#8ca0b5",   # 板金亮面
    "cyan": "#37b8eb",    # BR 與光條（＝站台主色 --bs-primary）
    "gold": "#f6c84a",    # 「翻譯小站」與齒輪飾線
}
ART_CYAN = "#33c8fb"

# 由後往前疊。ink 用整張剪影（不分類），板金之間的縫隙才會是深色。
# ⚠️ gold 不在這裡——金色那一層是重畫的，見下面的常數與 text_paths()／gear_paths()／accent_paths()。
LAYER_ORDER = ("ink", "slate", "steel", "cyan")

FONT = Path(r"C:\Windows\Fonts\NotoSansTC-VF.ttf")

# 金色層（「翻譯小站」＋齒輪＋飾線）**不描圖**。
# 原圖那四個字是裝飾字體：筆畫細、字腔窄，外面還包一圈深色描邊，縮到頁首尺寸（約 16px）
# 筆畫不到 1px 就糊掉；齒輪的齒紋與飾線的細線同理。所以這一層改成重畫：
# 字用 Noto Sans TC（SIL OFL）的字型輪廓（筆畫均勻、字腔開、深色底上不再加描邊），
# 齒輪與飾線用純幾何並加粗，在頁首尺寸才站得住。
# 以下座標是從原圖量出來的（畫布 760×437）：字塊 x 227–535、y 321–386，齒輪中心 y≈358。
TEXT = "翻譯小站"
# ⚠️ 飾板中央的凹槽（純深色帶）只有 y 314–393（高 79、中心 353.5），齒輪那一段是 y 317–394。
# 這些數字是從原圖量的：整列都必須是深色才算凹槽。字與齒輪一旦超出就會壓到上方的板金，
# 使用者退過一次（當時字放到 78 高、中心移到 350）。放大前先回頭量，別再憑感覺調。
# 現在字高 68（原圖 65）、上下各留約 5.5 的邊；齒輪維持原圖的中心與外徑。
TEXT = "翻譯小站"
TEXT_CENTER = (381.0, 353.5)
TEXT_INK_HEIGHT = 68.0   # 原圖約 65；凹槽高 79，別超過 70
TEXT_TRACKING = 6.0
TEXT_WEIGHT = 700
GEAR_CENTERS = ((71.5, 358.0), (689.0, 358.0))  # 與原圖同位置
GEAR_OUTER_R = 26.0      # 與原圖同大小；齒紋簡化掉、環加粗
GEAR_RING_W = 8.0
GEAR_DOT_R = 7.0
ACCENT_Y = 358.0
ACCENT_OUTER_X = (104.0, 658.0)  # 飾線最外側（靠齒輪那端）
ACCENT_GAP = 16.0                # 飾線與文字之間留白
ACCENT_HALF_T = 3.0              # 飾線半厚
ACCENT_TAPER = 11.0              # 兩端收尖長度


def load_rgba(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    alpha = np.array(im)[..., 3] > 160
    ys, xs = np.nonzero(alpha)
    pad = 3
    box = (
        max(int(xs.min()) - pad, 0),
        max(int(ys.min()) - pad, 0),
        min(int(xs.max()) + 1 + pad, im.width),
        min(int(ys.max()) + 1 + pad, im.height),
    )
    return im.crop(box)


def classify(im: Image.Image) -> dict[str, np.ndarray]:
    """每個不透明像素歸到最近的原圖色，回傳每層的遮罩。"""
    rgba = np.array(im)
    opaque = rgba[..., 3] > 160
    rgb = rgba[..., :3].astype(np.int32)

    names = list(PALETTE_SRC)
    refs = np.array([PALETTE_SRC[n] for n in names], dtype=np.int32)
    dist = ((rgb[:, :, None, :] - refs[None, None, :, :]) ** 2).sum(axis=3)
    nearest = dist.argmin(axis=2)

    masks = {"ink": opaque}  # 深色層直接用整張剪影
    for i, name in enumerate(names):
        if name == "ink":
            continue
        masks[name] = (nearest == i) & opaque
    return masks


def clean(mask: np.ndarray, min_size: int, hole_size: int) -> np.ndarray:
    """扁平稿只需要很輕的清理：削掉反鋸齒造成的 1px 邊緣，再清小雜點與小洞。"""
    m = ndimage.binary_opening(mask, iterations=1)
    m = ndimage.binary_closing(m, iterations=1)

    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, np.nonzero(sizes >= min_size)[0] + 1)

    holes = ~m
    lab, n = ndimage.label(holes)
    if n:
        border = set(lab[0].tolist()) | set(lab[-1].tolist()) | set(lab[:, 0].tolist()) | set(lab[:, -1].tolist())
        sizes = ndimage.sum(holes, lab, range(1, n + 1))
        fill = [i for i in range(1, n + 1) if sizes[i - 1] <= hole_size and i not in border]
        if fill:
            m = m | np.isin(lab, fill)
    return m


def trace(mask: np.ndarray, scale: float, turdsize: int) -> str:
    """描出 mask 的輪廓。⚠️ potracer 把 True 視為背景，要餵反相的 bool 遮罩。"""
    bmp = potrace.Bitmap(np.ascontiguousarray(~mask, dtype=bool))
    path = bmp.trace(
        turdsize=turdsize,
        turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,
        alphamax=1.0,
        opticurve=True,
        opttolerance=0.2,
    )
    k = 1.0 / scale
    parts: list[str] = []
    for curve in path:
        p0 = curve.start_point
        parts.append(f"M{p0.x * k:.1f} {p0.y * k:.1f}")
        for seg in curve:
            end = seg.end_point
            if seg.is_corner:
                parts.append(f"L{seg.c.x * k:.1f} {seg.c.y * k:.1f}L{end.x * k:.1f} {end.y * k:.1f}")
            else:
                parts.append(
                    f"C{seg.c1.x * k:.1f} {seg.c1.y * k:.1f} {seg.c2.x * k:.1f} {seg.c2.y * k:.1f}"
                    f" {end.x * k:.1f} {end.y * k:.1f}"
                )
        parts.append("z")
    return "".join(parts)


def text_paths(weight: int) -> tuple[list[str], tuple[float, float]]:
    """把「翻譯小站」取成字型輪廓路徑（已置中）。回傳路徑與整排字的左右界。"""
    if not FONT.exists():
        raise SystemExit(f"找不到字型 {FONT}（Noto Sans TC）。換台機器請改 FONT 常數。")
    font = instantiateVariableFont(TTFont(FONT, fontNumber=0), {"wght": weight}, inplace=False)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()

    names = [cmap[ord(ch)] for ch in TEXT]
    bounds = []
    for name in names:
        bp = BoundsPen(glyphs)
        glyphs[name].draw(bp)
        bounds.append(bp.bounds)
    ink_top = max(b[3] for b in bounds)
    ink_bottom = min(b[1] for b in bounds)

    size = TEXT_INK_HEIGHT / (ink_top - ink_bottom)  # 一個字型單位對應幾個畫布像素
    advance = font["hmtx"][names[0]][0] * size
    total = advance * len(names) + TEXT_TRACKING * (len(names) - 1)

    x = TEXT_CENTER[0] - total / 2
    baseline = TEXT_CENTER[1] + (ink_top + ink_bottom) / 2 * size  # 以墨色而非 baseline 置中

    paths = []
    for name in names:
        pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.1f}")
        glyphs[name].draw(pen)
        d = pen.getCommands()
        if d:
            paths.append(
                f'<path transform="translate({x:.1f} {baseline:.1f}) scale({size:.5f} {-size:.5f})" d="{d}"/>'
            )
        x += advance + TEXT_TRACKING
    return paths, (TEXT_CENTER[0] - total / 2, TEXT_CENTER[0] + total / 2)


def gear_paths() -> list[str]:
    """左右兩顆齒輪：外環 + 中心點。齒紋在頁首尺寸看不見，簡化掉、環也加粗。"""
    out = []
    for cx, cy in GEAR_CENTERS:
        r, ri = GEAR_OUTER_R, GEAR_OUTER_R - GEAR_RING_W
        out.append(
            f'<path fill-rule="evenodd" d="'
            f"M{cx - r:.1f} {cy:.1f}a{r:.1f} {r:.1f} 0 1 0 {2 * r:.1f} 0a{r:.1f} {r:.1f} 0 1 0 {-2 * r:.1f} 0z"
            f"M{cx - ri:.1f} {cy:.1f}a{ri:.1f} {ri:.1f} 0 1 1 {2 * ri:.1f} 0a{ri:.1f} {ri:.1f} 0 1 1 {-2 * ri:.1f} 0z"
            f'"/>'
        )
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{GEAR_DOT_R:.1f}"/>')
    return out


def accent_paths(text_left: float, text_right: float) -> list[str]:
    """齒輪與文字之間的飾線：一條兩端收尖的粗線 + 三個小點。"""
    spans = [
        (ACCENT_OUTER_X[0], text_left - ACCENT_GAP),
        (text_right + ACCENT_GAP, ACCENT_OUTER_X[1]),
    ]
    out = []
    for x0, x1 in spans:
        t, taper, y = ACCENT_HALF_T, ACCENT_TAPER, ACCENT_Y
        out.append(
            f'<path d="M{x0:.1f} {y:.1f}L{x0 + taper:.1f} {y - t:.1f}'
            f"L{x1 - taper:.1f} {y - t:.1f}L{x1:.1f} {y:.1f}"
            f'L{x1 - taper:.1f} {y + t:.1f}L{x0 + taper:.1f} {y + t:.1f}z"/>'
        )
        inner = x0 + 28 if x0 == ACCENT_OUTER_X[0] else x1 - 48
        for i in range(3):
            out.append(f'<circle cx="{inner + i * 10:.1f}" cy="{y + 13:.1f}" r="2.4"/>')
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--detail", type=float, default=2.0, help="描邊解析度是輸出畫布的幾倍")
    ap.add_argument("--art-cyan", action="store_true", help="青色保留原圖的 #33c8fb")
    ap.add_argument("--weight", type=int, default=TEXT_WEIGHT, help="「翻譯小站」的字重（100–900）")
    ap.add_argument("--src", type=Path, default=SRC)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    im = load_rgba(args.src)
    w = CANVAS_W
    h = round(im.height * w / im.width)
    size = (round(w * args.detail), round(h * args.detail))
    small = im.resize(size, Image.LANCZOS)
    area = size[0] * size[1]

    masks = classify(small)
    palette = dict(PALETTE_OUT)
    if args.art_cyan:
        palette["cyan"] = ART_CYAN

    body = []
    for name in LAYER_ORDER:
        mask = masks[name]
        if name == "ink":
            mask = clean(mask, area // 2000, area // 400)
        else:
            mask = clean(mask, area // 4000, area // 4000)
        d = trace(mask, args.detail, turdsize=max(4, round(area / 60000)))
        body.append(f'<path fill="{palette[name]}" fill-rule="evenodd" d="{d}"/>')
        print(f"{name:6s} px={int(mask.sum()):8d}  d={len(d):6d} chars", file=sys.stderr)

    glyphs, (left, right) = text_paths(args.weight)
    body.append(
        f'<g fill="{palette["gold"]}">'
        + "".join(gear_paths() + accent_paths(left, right) + glyphs)
        + "</g>"
    )
    print(f"gold   重畫 {TEXT} wght={args.weight} x={left:.0f}-{right:.0f}、齒輪與飾線", file=sys.stderr)

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="BR 翻譯小站"><title>BR 翻譯小站</title>'
        + "".join(body)
        + "</svg>"
    )
    args.out.write_text(svg, encoding="utf-8")
    print(f"wrote {args.out} ({len(svg) / 1024:.1f} KB, viewBox 0 0 {w} {h})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
