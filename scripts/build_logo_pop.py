#!/usr/bin/env python3
"""【已被取代，保留備查】POP 風格版的站台 logo 產生器。

2026-09-22 使用者拿到 ChatGPT 重畫的扁平風新圖（`BR_Desk_Logo_2.png`）後，
頁首改用 `scripts/build_logo.py` 直接描那張新圖；這支只在想回到 POP 風時才用，
產出請自行指定 `--out`，不要直接覆蓋 public/br-logo.svg。

原說明：組出頁首用的站台 logo（POP 風格版）。

使用者設計的原圖是機甲風的點陣稿（web-spec-doc/BR_logo/*.png）。照著原圖做了三輪
（全圖描邊 → 字改字型輪廓 → 板金改擬合 → 板金改設計稿）之後，使用者決定**不再仿機甲質感**，
改走 POP／美式漫畫風。現在只從原圖取一樣東西：

- **「BR」的字形**——描邊取出。那是品牌本體，本來就粗、卡通感重，很適合 POP。

其餘全是幾何繪製或字型輪廓，所以每條邊都乾淨：

- 背後的爆炸星形（厚描邊）
- 「BR」：深色剪影 ＋ 位移陰影 ＋ 青色面（漫畫式厚描邊、錯位印刷感）
- 緞帶橫幅（含兩端燕尾）＋ 深色「翻譯小站」（Noto Sans TC 字型輪廓，SIL OFL）
- 兩顆星芒點綴

    pip install potracer fonttools
    python scripts/build_logo.py                 # 重新產生 public/br-logo.svg
    python scripts/build_logo.py --weight 700    # 「翻譯小站」字重（100–900）
    python scripts/build_logo.py --no-burst      # 不要背後的爆炸星形

⚠️ 產出的 SVG 已進版控，平時不需要重跑。檢視產出可用 `pip install resvg-py` 把 SVG 描繪成 PNG
（本機沒有 cairo，cairosvg 裝了也跑不動）。
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
SRC = ROOT / "web-spec-doc" / "BR_logo" / "ChatGPT Image 2026年9月19日 下午02_33_28.png"
OUT = ROOT / "public" / "br-logo.svg"
FONT = Path(r"C:\Windows\Fonts\NotoSansTC-VF.ttf")

PALETTE = {
    "ink": "#18212f",        # 描邊與深色字
    "shadow": "#8fd3f0",     # BR 的位移陰影（淡青，POP 常見的錯位印刷感）
    "cyan": "#37b8eb",       # BR 本體（＝站台主色 --bs-primary）
    "burst": "#d3eefb",      # 背後的爆炸星形
    "gold": "#f6c85a",       # 緞帶本體
    "gold_dark": "#dda63c",  # 緞帶燕尾
}

CANVAS = (760, 448)
# 實際有畫東西的範圍（爆炸星形上緣～緞帶下緣、燕尾左右端，都含描邊）。
# 輸出的 viewBox 用這個而不是整張畫布，頁首才不會在 logo 四周留一圈空白。
VIEWBOX = (46.0, 0.0, 668.0, 416.0)
INK_W = 13.0                  # 描邊粗細
LETTER_BOX = (150.0, 30.0, 596.0, 292.0)  # BR 要塞進去的方框
LETTER_SHADOW = (11.0, 13.0)  # BR 陰影位移

# 爆炸星形：以 BR 為中心，垂直壓扁成橢圓感，免得超出畫布
BURST_CENTER = (372.0, 168.0)
BURST_POINTS = 12
BURST_RADII = (300.0, 246.0)
BURST_SQUASH = 0.52

# 緞帶橫幅
BAND = (118.0, 316.0, 642.0, 404.0)  # x0, y0, x1, y1
BAND_CHAMFER = 13.0
TAIL_W = 62.0        # 燕尾往外延伸多長
TAIL_INSET = 9.0     # 燕尾比本體窄多少
TAIL_NOTCH = 20.0    # 燕尾缺口深度

# 「翻譯小站」
TEXT = "翻譯小站"
TEXT_INK_HEIGHT = 58.0
TEXT_TRACKING = 7.0

# 星芒點綴：(x, y, 外徑, 內徑)
SPARKS = ((86.0, 44.0, 26.0, 8.5), (668.0, 36.0, 20.0, 6.5))


# --------------------------------------------------------------------------- 從原圖取 BR 字形
def load_rgba(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    alpha = np.array(im)[..., 3] > 128
    ys, xs = np.nonzero(alpha)
    pad = 4
    box = (
        max(int(xs.min()) - pad, 0),
        max(int(ys.min()) - pad, 0),
        min(int(xs.max()) + 1 + pad, im.width),
        min(int(ys.max()) + 1 + pad, im.height),
    )
    return im.crop(box)


def letter_masks(im: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    """回傳（含字腔的 BR 遮罩, 補滿字腔的 BR 剪影）。"""
    rgba = np.array(im)
    rgb = rgba[..., :3].astype(np.int16)
    opaque = rgba[..., 3] > 110
    hsv = np.array(Image.fromarray(rgba[..., :3], "RGB").convert("HSV")).astype(np.float32) / 255
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    warm = ((rgb[..., 0] - rgb[..., 2]) > 20) & (v > 0.30) & opaque  # 原圖的金色飾件
    cyan = (h > 0.47) & (h < 0.60) & (s > 0.32) & (v > 0.38) & opaque & ~warm
    cyan = ndimage.binary_closing(cyan, iterations=2)
    cyan = ndimage.binary_opening(cyan, iterations=2)

    # 只留最大的兩塊＝B 與 R；原圖其他青色（斜向光條、底部光帶）都不要
    lab, n = ndimage.label(cyan)
    if n < 2:
        raise SystemExit("找不到 BR 兩個字的青色區塊，原圖或門檻有變")
    sizes = ndimage.sum(cyan, lab, range(1, n + 1))
    keep = np.argsort(sizes)[::-1][:2] + 1
    letters = np.isin(lab, keep)
    return letters, ndimage.binary_fill_holes(letters)


def trace(mask: np.ndarray, scale: float, turdsize: int = 8) -> str:
    """描出 mask 的輪廓。⚠️ potracer 把 True 視為背景，要餵反相的 bool 遮罩。"""
    bmp = potrace.Bitmap(np.ascontiguousarray(~mask, dtype=bool))
    path = bmp.trace(
        turdsize=turdsize,
        turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,
        alphamax=1.0,
        opticurve=True,
        opttolerance=0.4,
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


def fit_box(mask: np.ndarray, scale: float, target: tuple[float, float, float, float]):
    """算出把字形塞進 target 方框所需的縮放與位移（輸入遮罩的座標已先除以 scale）。"""
    ys, xs = np.nonzero(mask)
    bw = (xs.max() - xs.min() + 1) / scale
    bh = (ys.max() - ys.min() + 1) / scale
    x0, y0, x1, y1 = target
    k = min((x1 - x0) / bw, (y1 - y0) / bh)
    dx = x0 + ((x1 - x0) - bw * k) / 2 - xs.min() / scale * k
    dy = y0 + ((y1 - y0) - bh * k) / 2 - ys.min() / scale * k
    return k, dx, dy


# --------------------------------------------------------------------------- 幾何元件
def star(cx: float, cy: float, points: int, r_out: float, r_in: float, phase: float = 0.0) -> str:
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = np.pi * i / points + phase
        pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "z"


def band_path() -> str:
    """緞帶本體：四角切角的橫長方形。"""
    x0, y0, x1, y1 = BAND
    c = BAND_CHAMFER
    pts = [
        (x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c),
        (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c),
    ]
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "z"


def tail_paths() -> list[str]:
    """兩端的燕尾，外緣切一個 V 形缺口。"""
    x0, y0, x1, y1 = BAND
    out = []
    for side in (-1.0, 1.0):
        anchor = x0 if side < 0 else x1
        tip = anchor + side * TAIL_W
        pts = [
            (anchor, y0 + TAIL_INSET),
            (tip, y0 + TAIL_INSET * 2),
            (tip - side * TAIL_NOTCH, (y0 + y1) / 2),
            (tip, y1 - TAIL_INSET * 2),
            (anchor, y1 - TAIL_INSET),
        ]
        out.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "z")
    return out


def text_paths(weight: int) -> list[str]:
    """把「翻譯小站」取成字型輪廓路徑，置中於緞帶。"""
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

    size = TEXT_INK_HEIGHT / (ink_top - ink_bottom)
    advance = font["hmtx"][names[0]][0] * size
    total = advance * len(names) + TEXT_TRACKING * (len(names) - 1)

    x0, y0, x1, y1 = BAND
    x = (x0 + x1) / 2 - total / 2
    baseline = (y0 + y1) / 2 + (ink_top + ink_bottom) / 2 * size

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
    return paths


# --------------------------------------------------------------------------- 組裝
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--detail", type=float, default=2.0, help="BR 字形描邊解析度是輸出畫布的幾倍")
    ap.add_argument("--weight", type=int, default=800, help="「翻譯小站」的字重（100–900）")
    ap.add_argument("--no-burst", action="store_true", help="不要背後的爆炸星形")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    w, h = CANVAS
    im = load_rgba(SRC).resize((round(w * args.detail), round(h * args.detail)), Image.LANCZOS)
    letters, solid = letter_masks(im)

    d_letters = trace(letters, args.detail)
    d_solid = trace(solid, args.detail)
    k, dx, dy = fit_box(solid, args.detail, LETTER_BOX)
    place = f"translate({dx:.1f} {dy:.1f}) scale({k:.4f})"

    ink, cyan = PALETTE["ink"], PALETTE["cyan"]
    body: list[str] = []

    if not args.no_burst:
        # 壓扁的變換會連描邊一起壓，所以描邊寬度先除回來
        body.append(
            f'<g transform="translate({BURST_CENTER[0]:.1f} {BURST_CENTER[1]:.1f}) '
            f'scale(1 {BURST_SQUASH})">'
            f'<path d="{star(0, 0, BURST_POINTS, *BURST_RADII, phase=np.pi / BURST_POINTS)}" '
            f'fill="{PALETTE["burst"]}" stroke="{ink}" stroke-width="{INK_W / BURST_SQUASH:.1f}" '
            f'stroke-linejoin="round"/></g>'
        )

    # BR：陰影 → 深色剪影（含描邊）→ 青色面。字腔靠剪影透出深色。
    # 描邊與位移都在縮放後的座標系裡，所以要先除以 k。
    body.append(
        f'<g transform="{place}">'
        f'<g transform="translate({LETTER_SHADOW[0] / k:.1f} {LETTER_SHADOW[1] / k:.1f})">'
        f'<path d="{d_solid}" fill="{PALETTE["shadow"]}" stroke="{ink}" '
        f'stroke-width="{INK_W / k:.1f}" stroke-linejoin="round"/></g>'
        f'<path d="{d_solid}" fill="{ink}" stroke="{ink}" stroke-width="{INK_W / k:.1f}" '
        f'stroke-linejoin="round"/>'
        f'<path d="{d_letters}" fill="{cyan}" fill-rule="evenodd"/>'
        f"</g>"
    )

    # 緞帶：燕尾在後、本體在前，最後放深色的「翻譯小站」
    for d in tail_paths():
        body.append(
            f'<path d="{d}" fill="{PALETTE["gold_dark"]}" stroke="{ink}" '
            f'stroke-width="{INK_W:.1f}" stroke-linejoin="round"/>'
        )
    body.append(
        f'<path d="{band_path()}" fill="{PALETTE["gold"]}" stroke="{ink}" '
        f'stroke-width="{INK_W:.1f}" stroke-linejoin="round"/>'
    )
    body.append(f'<g fill="{ink}">' + "".join(text_paths(args.weight)) + "</g>")

    for cx, cy, r_out, r_in in SPARKS:
        body.append(
            f'<path d="{star(cx, cy, 4, r_out, r_in, phase=np.pi / 4)}" fill="{cyan}" '
            f'stroke="{ink}" stroke-width="{INK_W * 0.55:.1f}" stroke-linejoin="round"/>'
        )

    vb = " ".join(f"{v:g}" for v in VIEWBOX)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
        f'role="img" aria-label="BR 翻譯小站"><title>BR 翻譯小站</title>'
        + "".join(body)
        + "</svg>"
    )
    args.out.write_text(svg, encoding="utf-8")
    print(f"BR 字形 d={len(d_letters)}+{len(d_solid)} chars, 縮放 {k:.3f}", file=sys.stderr)
    print(f"wrote {args.out} ({len(svg) / 1024:.1f} KB, viewBox {vb})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
