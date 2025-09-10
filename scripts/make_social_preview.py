#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_social_preview.py
---------------------------------
Generate a 1200x630 social preview image by composing three core charts.
Inputs (defaults):
 - reports/figs/ic_timeseries.png
 - reports/figs/deciles.png
 - reports/figs/corr_heatmap.png
Output:
 - docs/social_preview.png
"""

from pathlib import Path
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1200, 630
PADDING = 30
BG_COLOR = (245, 247, 250)
TEXT_COLOR = (30, 41, 59)
SUBTEXT_COLOR = (71, 85, 105)
TITLE = "HK Equities NLP Sentiment Factor"
SUB = "IC | Quantile | Style Correlation"


def load_and_fit(path: Path, box: Tuple[int, int]) -> Image.Image:
    img = Image.open(path).convert("RGB")
    target_w, target_h = box
    img.thumbnail((target_w, target_h), Image.LANCZOS)
    # pad to exact box size with white bg
    canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))
    x = (target_w - img.width) // 2
    y = (target_h - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def main():
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "social_preview.png"

    figs = [
        root / "reports/figs/ic_timeseries.png",
        root / "reports/figs/deciles.png",
        root / "reports/figs/corr_heatmap.png",
    ]
    for p in figs:
        if not p.exists():
            raise FileNotFoundError(f"Missing figure: {p}")

    # layout: title on top, three images in a row below
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    # fonts (fallback to default)
    try:
        font_title = ImageFont.truetype("Arial.ttf", 44)
        font_sub = ImageFont.truetype("Arial.ttf", 28)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # title
    try:
        tw, th = draw.textlength(TITLE, font=font_title), font_title.size
    except Exception:
        tw, th = draw.textbbox((0, 0), TITLE, font=font_title)[2:4]
    draw.text(((WIDTH - tw) // 2, PADDING), TITLE, fill=TEXT_COLOR, font=font_title)
    # subtitle
    try:
        sw, sh = draw.textlength(SUB, font=font_sub), font_sub.size
    except Exception:
        sw, sh = draw.textbbox((0, 0), SUB, font=font_sub)[2:4]
    draw.text(((WIDTH - sw) // 2, PADDING + th + 8), SUB, fill=SUBTEXT_COLOR, font=font_sub)

    # image row box
    top = PADDING + th + sh + 24
    available_h = HEIGHT - top - PADDING
    each_w = (WIDTH - PADDING * 4) // 3
    each_h = available_h

    boxes = [
        (PADDING, top, each_w, each_h),
        (PADDING * 2 + each_w, top, each_w, each_h),
        (PADDING * 3 + each_w * 2, top, each_w, each_h),
    ]

    for fig_path, (x, y, w, h) in zip(figs, boxes):
        tile = load_and_fit(fig_path, (w, h))
        canvas.paste(tile, (x, y))

    canvas.save(out_path, format="PNG")
    print(f"Saved social preview to: {out_path}")


if __name__ == "__main__":
    main()


