#!/usr/bin/env python3
"""Solve Huanxin "enter the red characters" (请输入红色字符) graphic captchas.

The captcha overlays the answer glyphs in RED among same-shape decoy glyphs in
other colors, with a Chinese instruction line at the bottom. We keep only
red-dominant pixels, drop the instruction band, denoise, upscale, and OCR with
ddddocr. Prints the recognized code to stdout.

Usage: python scripts/solve_huanxin_captcha.py <captcha.png> [--debug out.png]
"""

import io
import sys

from PIL import Image


def solve(path, debug=None):
    import ddddocr  # local, lazy

    ocr = ddddocr.DdddOcr(show_ad=False)
    im = Image.open(path).convert("RGB")
    width, height = im.size
    # Instruction line sits in the bottom ~28%; keep the glyph band above it.
    crop = im.crop((0, 0, width, int(height * 0.60)))
    cw, ch = crop.size
    src = crop.load()
    mask = Image.new("L", (cw, ch), 255)
    mp = mask.load()
    for y in range(ch):
        for x in range(cw):
            r, g, b = src[x, y]
            # Red-dominant glyph pixel: red clearly above green and blue.
            if r > 105 and (r - g) > 38 and (r - b) > 38:
                mp[x, y] = 0
    mask = mask.resize((cw * 4, ch * 4), Image.LANCZOS)
    if debug:
        mask.save(debug)
    buf = io.BytesIO()
    mask.save(buf, format="PNG")
    code = ocr.classification(buf.getvalue())
    # keep only alphanumerics
    return "".join(c for c in code if c.isalnum())


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("usage: solve_huanxin_captcha.py <captcha.png> [--debug out.png]", file=sys.stderr)
        return 2
    path = args[0]
    debug = None
    if "--debug" in args:
        debug = args[args.index("--debug") + 1]
    code = solve(path, debug)
    print(code)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
