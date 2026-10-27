#!/usr/bin/env python3
"""Dependency-free PNG statistics for evidence-backed visual review.

The probe measures format, tone, saturation, and local contrast. It cannot decide
material ownership, source fidelity, or aesthetic quality; those remain visual gates.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import zlib
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def paeth(a: int, b: int, c: int) -> int:
    prediction = a + b - c
    pa = abs(prediction - a)
    pb = abs(prediction - b)
    pc = abs(prediction - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def decode_png(path: Path) -> tuple[int, int, list[tuple[int, int, int]]]:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG file")

    position = len(PNG_SIGNATURE)
    width = height = bit_depth = color_type = interlace = None
    compressed = bytearray()
    palette: list[tuple[int, int, int]] = []
    while position < len(data):
        length = struct.unpack(">I", data[position:position + 4])[0]
        chunk_type = data[position + 4:position + 8]
        payload = data[position + 8:position + 8 + length]
        position += 12 + length
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", payload)
        elif chunk_type == b"PLTE":
            palette = [tuple(payload[index:index + 3]) for index in range(0, len(payload), 3)]  # type: ignore[list-item]
        elif chunk_type == b"IDAT":
            compressed.extend(payload)
        elif chunk_type == b"IEND":
            break

    if None in {width, height, bit_depth, color_type, interlace}:
        raise ValueError("PNG lacks a complete IHDR")
    if bit_depth != 8 or interlace != 0:
        raise ValueError("only non-interlaced 8-bit PNG files are supported")
    channels_by_type = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
    if color_type not in channels_by_type:
        raise ValueError(f"unsupported PNG color type: {color_type}")
    channels = channels_by_type[color_type]
    row_bytes = width * channels
    raw = zlib.decompress(bytes(compressed))
    expected = height * (row_bytes + 1)
    if len(raw) != expected:
        raise ValueError(f"unexpected decoded PNG size: {len(raw)} instead of {expected}")

    rows: list[bytearray] = []
    offset = 0
    previous = bytearray(row_bytes)
    for _ in range(height):
        filter_type = raw[offset]
        scan = raw[offset + 1:offset + 1 + row_bytes]
        offset += row_bytes + 1
        reconstructed = bytearray(row_bytes)
        for index, value in enumerate(scan):
            left = reconstructed[index - channels] if index >= channels else 0
            up = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 3:
                predictor = (left + up) // 2
            elif filter_type == 4:
                predictor = paeth(left, up, upper_left)
            else:
                raise ValueError(f"unsupported PNG filter: {filter_type}")
            reconstructed[index] = (value + predictor) & 0xFF
        rows.append(reconstructed)
        previous = reconstructed

    pixels: list[tuple[int, int, int]] = []
    for row in rows:
        for index in range(0, len(row), channels):
            if color_type == 0:
                red = green = blue = row[index]
                alpha = 255
            elif color_type == 2:
                red, green, blue = row[index:index + 3]
                alpha = 255
            elif color_type == 3:
                palette_index = row[index]
                if palette_index >= len(palette):
                    raise ValueError("palette index is out of range")
                red, green, blue = palette[palette_index]
                alpha = 255
            elif color_type == 4:
                red = green = blue = row[index]
                alpha = row[index + 1]
            else:
                red, green, blue, alpha = row[index:index + 4]
            if alpha < 255:
                red = round((red * alpha + 255 * (255 - alpha)) / 255)
                green = round((green * alpha + 255 * (255 - alpha)) / 255)
                blue = round((blue * alpha + 255 * (255 - alpha)) / 255)
            pixels.append((red, green, blue))
    return width, height, pixels


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * fraction)))
    return ordered[position]


def ratio_value(value: str) -> float:
    if ":" in value:
        left, right = value.split(":", 1)
        return float(left) / float(right)
    return float(value)


def probe(path: Path, maximum_samples: int = 250_000) -> dict[str, object]:
    width, height, pixels = decode_png(path)
    sample_step = max(1, math.ceil(math.sqrt(len(pixels) / maximum_samples)))
    sampled: list[tuple[int, int, int]] = []
    sampled_positions: list[tuple[int, int]] = []
    for y in range(0, height, sample_step):
        for x in range(0, width, sample_step):
            sampled.append(pixels[y * width + x])
            sampled_positions.append((x, y))

    luminance = [0.2126 * red + 0.7152 * green + 0.0722 * blue for red, green, blue in sampled]
    saturation = [0 if max(pixel) == 0 else (max(pixel) - min(pixel)) / max(pixel) for pixel in sampled]
    count = len(sampled)
    mean_luma = sum(luminance) / count
    variance = sum((value - mean_luma) ** 2 for value in luminance) / count
    mean_rgb = [round(sum(pixel[channel] for pixel in sampled) / count, 2) for channel in range(3)]

    edge_values: list[float] = []
    sample_width = len(range(0, width, sample_step))
    for index, value in enumerate(luminance):
        if index % sample_width:
            edge_values.append(abs(value - luminance[index - 1]))
        if index >= sample_width:
            edge_values.append(abs(value - luminance[index - sample_width]))

    region_totals = [[0.0 for _ in range(4)] for _ in range(5)]
    region_counts = [[0 for _ in range(4)] for _ in range(5)]
    for (x, y), value in zip(sampled_positions, luminance):
        column = min(3, x * 4 // width)
        row = min(4, y * 5 // height)
        region_totals[row][column] += value
        region_counts[row][column] += 1
    region_luma = [
        [round(region_totals[row][column] / region_counts[row][column], 2) for column in range(4)]
        for row in range(5)
    ]

    return {
        "asset": path.name,
        "format": "PNG",
        "width": width,
        "height": height,
        "aspect_ratio_decimal": round(width / height, 6),
        "sample_step_pixels": sample_step,
        "sample_count": count,
        "mean_rgb": mean_rgb,
        "luminance": {
            "mean": round(mean_luma, 2),
            "standard_deviation": round(math.sqrt(variance), 2),
            "p05": round(percentile(luminance, 0.05), 2),
            "p50": round(percentile(luminance, 0.50), 2),
            "p95": round(percentile(luminance, 0.95), 2),
            "pixels_below_16_percent": round(100 * sum(value < 16 for value in luminance) / count, 3),
            "pixels_below_32_percent": round(100 * sum(value < 32 for value in luminance) / count, 3),
            "pixels_above_245_percent": round(100 * sum(value > 245 for value in luminance) / count, 3)
        },
        "color": {
            "mean_saturation": round(sum(saturation) / count, 4),
            "pixels_above_0_65_saturation_percent": round(100 * sum(value > 0.65 for value in saturation) / count, 3)
        },
        "local_contrast": {
            "mean_neighbor_luminance_delta": round(sum(edge_values) / len(edge_values), 3)
        },
        "regional_mean_luminance_4x5": region_luma,
        "interpretation_limit": "Statistics do not determine composition quality, source fidelity, material ownership, or true halftone structure."
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--expect-ratio", default="4:5")
    parser.add_argument("--ratio-tolerance", type=float, default=0.02)
    parser.add_argument("--strict-ratio", action="store_true")
    args = parser.parse_args()

    result = probe(args.image)
    expected = ratio_value(args.expect_ratio)
    actual = float(result["aspect_ratio_decimal"])
    delta = abs(actual - expected)
    result["ratio_check"] = {
        "expected": args.expect_ratio,
        "tolerance": args.ratio_tolerance,
        "delta": round(delta, 6),
        "pass": delta <= args.ratio_tolerance,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if args.strict_ratio and delta > args.ratio_tolerance else 0


if __name__ == "__main__":
    raise SystemExit(main())
