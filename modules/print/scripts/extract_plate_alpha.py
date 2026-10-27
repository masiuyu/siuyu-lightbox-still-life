#!/usr/bin/env python3
"""Remove only a bright neutral background connected to the source border.

The operation is intentionally source-space.  It is suitable for converting a
generated plate preview with a white or light checkerboard backdrop into an
RGBA plate while preserving enclosed light ink marks inside the subject.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

try:
    from PIL import Image, ImageFilter
except ImportError as exc:  # pragma: no cover - environment-specific failure
    raise SystemExit("Pillow is required: python3 -m pip install Pillow") from exc


def extract_background(
    source: Image.Image,
    minimum_channel: int = 205,
    maximum_chroma: int = 30,
    edge_softness_px: float = 0.55,
) -> tuple[Image.Image, dict[str, object]]:
    if not 0 <= minimum_channel <= 255:
        raise ValueError("minimum_channel must be from 0 to 255")
    if not 0 <= maximum_chroma <= 80:
        raise ValueError("maximum_chroma must be from 0 to 80")
    if not 0 <= edge_softness_px <= 2:
        raise ValueError("edge_softness_px must be from 0 to 2")

    rgb = source.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    candidates = bytearray(width * height)
    for y in range(height):
        row = y * width
        for x in range(width):
            red, green, blue = pixels[x, y]
            if min(red, green, blue) >= minimum_channel and max(red, green, blue) - min(red, green, blue) <= maximum_chroma:
                candidates[row + x] = 1

    background = bytearray(width * height)
    queue: deque[int] = deque()

    def enqueue(index: int) -> None:
        if candidates[index] and not background[index]:
            background[index] = 1
            queue.append(index)

    for x in range(width):
        enqueue(x)
        enqueue((height - 1) * width + x)
    for y in range(height):
        enqueue(y * width)
        enqueue(y * width + width - 1)

    while queue:
        index = queue.popleft()
        x = index % width
        y = index // width
        if x:
            enqueue(index - 1)
        if x + 1 < width:
            enqueue(index + 1)
        if y:
            enqueue(index - width)
        if y + 1 < height:
            enqueue(index + width)

    alpha = Image.new("L", (width, height))
    alpha.putdata([0 if value else 255 for value in background])
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    if edge_softness_px:
        alpha = alpha.filter(ImageFilter.GaussianBlur(edge_softness_px))
    output = rgb.convert("RGBA")
    output.putalpha(alpha)
    bbox = alpha.getbbox()
    report: dict[str, object] = {
        "version": 1,
        "method": "edge_connected_bright_neutral_alpha_extraction",
        "width": width,
        "height": height,
        "minimum_channel": minimum_channel,
        "maximum_chroma": maximum_chroma,
        "edge_softness_px": edge_softness_px,
        "background_pixels": int(sum(background)),
        "foreground_bbox": list(bbox) if bbox else None,
        "alpha_extrema": list(alpha.getextrema()),
        "claim_limit": "This report proves border-connected background removal, not semantic segmentation or plate quality.",
    }
    return output, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--minimum-channel", type=int, default=205)
    parser.add_argument("--maximum-chroma", type=int, default=30)
    parser.add_argument("--edge-softness-px", type=float, default=0.55)
    args = parser.parse_args()
    source = Image.open(args.input)
    output, report = extract_background(
        source,
        minimum_channel=args.minimum_channel,
        maximum_chroma=args.maximum_chroma,
        edge_softness_px=args.edge_softness_px,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.save(args.output)
    report["input"] = str(args.input)
    report["output"] = str(args.output)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
