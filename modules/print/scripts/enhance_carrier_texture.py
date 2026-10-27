#!/usr/bin/env python3
"""Increase existing carrier micro-contrast without moving scene geometry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps
except ImportError as exc:  # pragma: no cover - environment-specific failure
    raise SystemExit("Pillow is required: python3 -m pip install Pillow") from exc


def _bounded_int(value: int, minimum: int, maximum: int, name: str) -> int:
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be from {minimum} to {maximum}")
    return value


def _circular_hue_mask(channel: Image.Image, center: int, tolerance: int) -> Image.Image:
    return channel.point(
        lambda value: 255 if min(abs(value - center), 256 - abs(value - center)) <= tolerance else 0
    )


def build_carrier_mask(
    image: Image.Image,
    *,
    hue_center: int,
    hue_tolerance: int,
    minimum_saturation: int,
    maximum_value: int,
) -> Image.Image:
    hsv = image.convert("HSV")
    hue, saturation, value = hsv.split()
    hue_mask = _circular_hue_mask(hue, hue_center, hue_tolerance)
    saturation_mask = saturation.point(lambda item: 255 if item >= minimum_saturation else 0)
    value_mask = value.point(lambda item: 255 if item <= maximum_value else 0)
    mask = ImageChops.multiply(ImageChops.multiply(hue_mask, saturation_mask), value_mask)
    # Close tiny holes inside the textile, then retreat from non-carrier edges.
    return mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(5))


def enhance(
    image: Image.Image,
    mask: Image.Image,
    *,
    radius: float,
    percent: int,
    threshold: int,
    contrast: float,
) -> tuple[Image.Image, dict[str, float | int]]:
    source = image.convert("RGB")
    sharpened = source.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))
    if contrast != 1.0:
        sharpened = ImageEnhance.Contrast(sharpened).enhance(contrast)
    result = Image.composite(sharpened, source, mask)
    difference = ImageChops.difference(source, result).convert("L")
    hard_mask = mask.point(lambda value: 255 if value else 0)
    outside = ImageChops.multiply(difference, ImageOps.invert(hard_mask))
    selected = sum(hard_mask.histogram()[1:])
    changed = sum(difference.histogram()[1:])
    return result, {
        "selected_carrier_percent": round(selected * 100.0 / (source.width * source.height), 3),
        "changed_pixel_percent": round(changed * 100.0 / (source.width * source.height), 3),
        "outside_carrier_changed_pixels": sum(outside.histogram()[1:]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--hue-center", type=int, default=132)
    parser.add_argument("--hue-tolerance", type=int, default=18)
    parser.add_argument("--minimum-saturation", type=int, default=35)
    parser.add_argument("--maximum-value", type=int, default=150)
    parser.add_argument("--radius", type=float, default=1.1)
    parser.add_argument("--percent", type=int, default=150)
    parser.add_argument("--threshold", type=int, default=1)
    parser.add_argument("--contrast", type=float, default=1.025)
    args = parser.parse_args()

    hue_center = _bounded_int(args.hue_center, 0, 255, "hue-center")
    hue_tolerance = _bounded_int(args.hue_tolerance, 0, 128, "hue-tolerance")
    minimum_saturation = _bounded_int(args.minimum_saturation, 0, 255, "minimum-saturation")
    maximum_value = _bounded_int(args.maximum_value, 0, 255, "maximum-value")
    if not 0.1 <= args.radius <= 4.0:
        raise ValueError("radius must be from 0.1 to 4.0")
    _bounded_int(args.percent, 1, 300, "percent")
    _bounded_int(args.threshold, 0, 32, "threshold")
    if not 1.0 <= args.contrast <= 1.12:
        raise ValueError("contrast must be from 1.0 to 1.12")

    source = Image.open(args.input).convert("RGB")
    mask = build_carrier_mask(
        source,
        hue_center=hue_center,
        hue_tolerance=hue_tolerance,
        minimum_saturation=minimum_saturation,
        maximum_value=maximum_value,
    )
    result, metrics = enhance(
        source,
        mask,
        radius=args.radius,
        percent=args.percent,
        threshold=args.threshold,
        contrast=args.contrast,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output)
    report = {
        "version": 1,
        "method": "geometry_locked_carrier_microcontrast",
        "input": str(args.input),
        "output": str(args.output),
        "width": source.width,
        "height": source.height,
        "selection": {
            "hue_center": hue_center,
            "hue_tolerance": hue_tolerance,
            "minimum_saturation": minimum_saturation,
            "maximum_value": maximum_value,
        },
        "enhancement": {
            "radius": args.radius,
            "percent": args.percent,
            "threshold": args.threshold,
            "contrast": args.contrast,
        },
        **metrics,
        "claim_limit": "This report proves geometry preservation and color-bounded containment, not material identity or aesthetic acceptance.",
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
