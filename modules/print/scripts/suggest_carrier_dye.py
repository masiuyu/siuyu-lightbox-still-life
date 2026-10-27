#!/usr/bin/env python3
"""Recommend a restrained carrier dye from source-image color evidence."""

from __future__ import annotations

import argparse
import colorsys
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - environment-specific failure
    raise SystemExit("Pillow is required: python3 -m pip install Pillow") from exc

from carrier_materials import load_material_library, material_index


RESAMPLING = getattr(Image, "Resampling", Image)
QUANTIZE = getattr(Image, "Quantize", Image)
DITHER = getattr(Image, "Dither", Image)

STRATEGIES = {
    "auto",
    "recessive_complement",
    "analogous_shadow",
    "neutralized_source",
    "explicit_user_palette",
    "theme_directed",
}
ALGORITHMIC_STRATEGIES = {
    "recessive_complement",
    "analogous_shadow",
    "neutralized_source",
}
VISIBLE_CONSEQUENCES = {
    "recessive_complement": "Creates clear hue separation from the dominant source family while keeping the carrier muted.",
    "analogous_shadow": "Keeps the carrier related to the source palette but darker and quieter than the image content.",
    "neutralized_source": "Retains the source hue family at strongly reduced chroma for the least assertive color relationship.",
    "explicit_user_palette": "Preserves the user's declared carrier color without silently normalizing it.",
    "theme_directed": "Uses the art-directed dye selected for the stated theme while retaining the chosen physical material.",
}


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _rgb_to_hsl(rgb: Iterable[int]) -> tuple[float, float, float]:
    red, green, blue = (int(channel) / 255.0 for channel in rgb)
    hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    return hue, saturation, lightness


def _hsl_to_rgb(hue: float, saturation: float, lightness: float) -> list[int]:
    red, green, blue = colorsys.hls_to_rgb(hue % 1.0, lightness, saturation)
    return [round(red * 255), round(green * 255), round(blue * 255)]


def _hue_distance(first: float, second: float) -> float:
    difference = abs(first - second) % 1.0
    return min(difference, 1.0 - difference)


def _weighted_hue(samples: list[tuple[list[int], float]]) -> tuple[float, float, float]:
    weighted: list[tuple[float, float, float, float]] = []
    for rgb, count in samples:
        hue, saturation, lightness = _rgb_to_hsl(rgb)
        middle_value_weight = 0.55 + 0.45 * (1.0 - abs(lightness - 0.5) * 2.0)
        weight = float(count) * max(0.08, saturation) * middle_value_weight
        weighted.append((hue, saturation, lightness, weight))
    total = sum(item[3] for item in weighted)
    if total <= 0:
        return 0.58, 0.0, 0.5
    x = sum(math.cos(item[0] * math.tau) * item[3] for item in weighted)
    y = sum(math.sin(item[0] * math.tau) * item[3] for item in weighted)
    hue = (math.atan2(y, x) / math.tau) % 1.0
    saturation = sum(item[1] * item[3] for item in weighted) / total
    lightness = sum(item[2] * item[3] for item in weighted) / total
    return hue, saturation, lightness


def _quantize_pixels(
    pixels: list[tuple[int, int, int]],
    colors: int,
) -> Counter[tuple[int, int, int]]:
    if not pixels:
        return Counter()
    sample_width = min(192, len(pixels))
    sample_height = math.ceil(len(pixels) / sample_width)
    padded_pixels = pixels + [pixels[-1]] * (
        sample_width * sample_height - len(pixels)
    )
    sample = Image.new("RGB", (sample_width, sample_height))
    sample.putdata(padded_pixels)
    quantized = sample.quantize(
        colors=colors,
        method=QUANTIZE.MEDIANCUT,
        dither=DITHER.NONE,
    )
    palette = quantized.getpalette() or []
    counts: Counter[tuple[int, int, int]] = Counter()
    for count, palette_index in quantized.getcolors(maxcolors=colors) or []:
        offset = palette_index * 3
        rgb = tuple(palette[offset:offset + 3])
        if len(rgb) == 3:
            counts[rgb] += count
    return counts


def _quantized_counts(image: Image.Image, colors: int = 12) -> Counter[tuple[int, int, int]]:
    rgba = image.convert("RGBA")
    rgba.thumbnail((192, 192), RESAMPLING.LANCZOS)
    pixel_reader = getattr(rgba, "get_flattened_data", None)
    pixel_data = pixel_reader() if pixel_reader is not None else rgba.getdata()
    opaque_pixels = [
        (red, green, blue)
        for red, green, blue, alpha in pixel_data
        if alpha >= 32
    ]
    counts = _quantize_pixels(opaque_pixels, colors)
    chromatic_pixels = [
        rgb
        for rgb in opaque_pixels
        if _rgb_to_hsl(rgb)[1] >= 0.18 and 0.06 <= _rgb_to_hsl(rgb)[2] <= 0.94
    ]
    if len(chromatic_pixels) >= max(8, round(len(opaque_pixels) * 0.003)):
        accent_counts = _quantize_pixels(chromatic_pixels, min(4, colors))
        for rgb, count in accent_counts.items():
            counts[rgb] += round(count * 1.4)
    return counts


def _validated_image_weights(
    image_paths: list[Path],
    image_weights: list[float] | None,
) -> list[float]:
    if image_weights is None:
        return [1.0] * len(image_paths)
    if len(image_weights) != len(image_paths):
        raise ValueError("image_weights must contain one value for every image")
    normalized: list[float] = []
    for weight in image_weights:
        if not isinstance(weight, (int, float)) or not math.isfinite(float(weight)):
            raise ValueError("each image weight must be a finite number")
        numeric = float(weight)
        if not 0.1 <= numeric <= 5.0:
            raise ValueError("each image weight must be from 0.1 to 5.0")
        normalized.append(numeric)
    return normalized


def extract_source_palette(
    image_paths: list[Path],
    maximum_colors: int = 8,
    image_weights: list[float] | None = None,
) -> dict[str, Any]:
    weights = _validated_image_weights(image_paths, image_weights)
    combined: Counter[tuple[int, int, int]] = Counter()
    for path, image_weight in zip(image_paths, weights):
        with Image.open(path) as image:
            full_counts = _quantized_counts(image)
            left = round(image.width * 0.12)
            top = round(image.height * 0.12)
            right = max(left + 1, round(image.width * 0.88))
            bottom = max(top + 1, round(image.height * 0.88))
            center_counts = _quantized_counts(image.crop((left, top, right, bottom)))
            for counts, pass_weight in ((full_counts, 0.58), (center_counts, 0.42)):
                pass_total = sum(counts.values())
                if pass_total:
                    for rgb, count in counts.items():
                        combined[rgb] += image_weight * pass_weight * count / pass_total
    if not combined:
        raise ValueError("the supplied images contain no visible pixels")

    total = sum(combined.values())
    chromatic: list[tuple[list[int], float]] = []
    usable_neutrals: list[tuple[list[int], float]] = []
    for rgb, count in combined.most_common():
        _, saturation, lightness = _rgb_to_hsl(rgb)
        if 0.06 <= lightness <= 0.94:
            usable_neutrals.append((list(rgb), count))
            if saturation >= 0.08:
                chromatic.append((list(rgb), count))

    if chromatic:
        evidence = sorted(
            chromatic,
            key=lambda item: item[1] * (0.35 + 1.65 * _rgb_to_hsl(item[0])[1]),
            reverse=True,
        )[:maximum_colors]
    else:
        evidence = (usable_neutrals or [(list(rgb), count) for rgb, count in combined.most_common()])[
            :maximum_colors
        ]
    dominant_hue, dominant_saturation, dominant_lightness = _weighted_hue(evidence)
    return {
        "source_rgb": [rgb for rgb, _ in evidence],
        "source_evidence_weights": [
            {
                "rgb": rgb,
                "evidence_weight": round(count / total, 4),
            }
            for rgb, count in evidence
        ],
        "dominant_hsl": [
            round(dominant_hue * 360.0, 1),
            round(dominant_saturation * 100.0, 1),
            round(dominant_lightness * 100.0, 1),
        ],
        "chromatic_evidence": bool(chromatic),
        "source_influence": [
            {"source_ref": path.name, "weight": round(weight, 3)}
            for path, weight in zip(image_paths, weights)
        ],
    }


def _candidate(
    strategy: str,
    hue: float,
    saturation: float,
    lightness: float,
    source_palette: dict[str, Any],
) -> dict[str, Any]:
    dye_rgb = _hsl_to_rgb(hue, saturation, lightness)
    source_hues = [
        _rgb_to_hsl(rgb)
        for rgb in source_palette["source_rgb"]
    ]
    chromatic_hues = [(value[0], value[1]) for value in source_hues if value[1] >= 0.08]
    if chromatic_hues:
        separation = sum(
            _hue_distance(hue, source_hue) * source_saturation
            for source_hue, source_saturation in chromatic_hues
        ) / sum(source_saturation for _, source_saturation in chromatic_hues)
        separation = separation / 0.5
    else:
        separation = 0.45
    restraint = 1.0 - saturation
    tonal_fit = 1.0 - min(1.0, abs(lightness - 0.38) / 0.38)
    score = round(50.0 * separation + 30.0 * restraint + 20.0 * tonal_fit, 1)
    return {
        "dye_strategy": strategy,
        "dye_rgb": dye_rgb,
        "dye_hsl": [
            round((hue % 1.0) * 360.0, 1),
            round(saturation * 100.0, 1),
            round(lightness * 100.0, 1),
        ],
        "noncompetition_score": score,
        "visible_consequence": VISIBLE_CONSEQUENCES[strategy],
    }


def _inside_dye_guidance(rgb: list[int], material: dict[str, Any]) -> bool:
    _, saturation, lightness = _rgb_to_hsl(rgb)
    constraints = material["dye_constraints"]
    saturation_range = constraints["saturation_range"]
    lightness_range = constraints["lightness_range"]
    quantization_tolerance = 0.012
    return (
        saturation_range[0] - quantization_tolerance
        <= saturation
        <= saturation_range[1] + quantization_tolerance
        and lightness_range[0] - quantization_tolerance
        <= lightness
        <= lightness_range[1] + quantization_tolerance
    )


def recommend_dye(
    image_paths: list[Path],
    material_id: str = "tight_book_cloth",
    selection_strategy: str = "auto",
    dye_rgb: list[int] | None = None,
    theme_note: str | None = None,
    image_weights: list[float] | None = None,
) -> dict[str, Any]:
    if selection_strategy not in STRATEGIES:
        raise ValueError(f"unknown selection strategy: {selection_strategy}")
    library = load_material_library()
    materials = material_index(library)
    if material_id not in materials:
        raise ValueError(f"unknown material_id: {material_id}")
    material = materials[material_id]
    palette = extract_source_palette(image_paths, image_weights=image_weights)

    source_hue, source_saturation, _ = (
        palette["dominant_hsl"][0] / 360.0,
        palette["dominant_hsl"][1] / 100.0,
        palette["dominant_hsl"][2] / 100.0,
    )
    saturation_min, saturation_max = material["dye_constraints"]["saturation_range"]
    lightness_min, lightness_max = material["dye_constraints"]["lightness_range"]
    candidates = [
        _candidate(
            "recessive_complement",
            source_hue + 0.5,
            _clamp(source_saturation * 0.44, saturation_min, min(saturation_max, 0.44)),
            _clamp(0.36, lightness_min, lightness_max),
            palette,
        ),
        _candidate(
            "analogous_shadow",
            source_hue + (25.0 / 360.0 if source_hue < 0.55 else -25.0 / 360.0),
            _clamp(source_saturation * 0.36, saturation_min, min(saturation_max, 0.4)),
            _clamp(0.32, lightness_min, lightness_max),
            palette,
        ),
        _candidate(
            "neutralized_source",
            source_hue,
            _clamp(source_saturation * 0.18, saturation_min, min(saturation_max, 0.3)),
            _clamp(0.4, lightness_min, lightness_max),
            palette,
        ),
    ]

    warnings: list[str] = []
    if dye_rgb is not None:
        if len(dye_rgb) != 3 or not all(isinstance(channel, int) and 0 <= channel <= 255 for channel in dye_rgb):
            raise ValueError("dye_rgb must contain three integers from 0 to 255")
        if selection_strategy in ALGORITHMIC_STRATEGIES:
            raise ValueError("dye_rgb cannot override an explicitly selected algorithmic strategy")
        effective_strategy = selection_strategy
        if selection_strategy == "auto":
            effective_strategy = "theme_directed" if theme_note else "explicit_user_palette"
        if effective_strategy == "theme_directed" and not theme_note:
            raise ValueError("theme_directed requires a non-empty theme_note")
        selected = {
            "dye_strategy": effective_strategy,
            "dye_rgb": list(dye_rgb),
            "dye_hsl": [
                round(_rgb_to_hsl(dye_rgb)[0] * 360.0, 1),
                round(_rgb_to_hsl(dye_rgb)[1] * 100.0, 1),
                round(_rgb_to_hsl(dye_rgb)[2] * 100.0, 1),
            ],
            "noncompetition_score": None,
            "visible_consequence": VISIBLE_CONSEQUENCES[effective_strategy],
        }
        if not _inside_dye_guidance(list(dye_rgb), material):
            warnings.append(
                "The explicit dye falls outside this material's restrained starting range; it was preserved unchanged."
            )
    else:
        if selection_strategy in {"explicit_user_palette", "theme_directed"}:
            raise ValueError(f"{selection_strategy} requires dye_rgb")
        if theme_note:
            warnings.append(
                "The theme note is recorded but not semantically converted into color; supply dye_rgb for a theme-directed choice."
            )
        if selection_strategy == "auto":
            if not palette["chromatic_evidence"] or source_saturation < 0.28:
                auto_strategy = "neutralized_source"
            elif source_saturation < 0.52:
                auto_strategy = "analogous_shadow"
            else:
                auto_strategy = "recessive_complement"
            selected = next(item for item in candidates if item["dye_strategy"] == auto_strategy)
        else:
            selected = next(item for item in candidates if item["dye_strategy"] == selection_strategy)

    basis = (
        f"Selected {selected['dye_strategy']} from {len(image_paths)} supplied image(s); "
        "each image was normalized before role weighting; the material preset contributes weave and ink response, "
        "while source color evidence contributes dye."
    )
    if theme_note:
        basis += f" Theme direction recorded: {theme_note.strip()}"
    source_evidence = {
        "source_rgb": palette["source_rgb"],
        "source_influence": palette["source_influence"],
        "selection_basis": basis,
    }
    recommended = {
        "material_id": material_id,
        "dye_rgb": selected["dye_rgb"],
        "dye_strategy": selected["dye_strategy"],
        "source_palette_evidence": source_evidence,
        "dye_hsl": selected["dye_hsl"],
        "noncompetition_score": selected["noncompetition_score"],
        "visible_consequence": selected["visible_consequence"],
        "within_material_dye_guidance": _inside_dye_guidance(selected["dye_rgb"], material),
    }
    return {
        "version": 1,
        "material_id": material_id,
        "material_display_name": material["display_name"],
        "source_files": [path.name for path in image_paths],
        "source_palette": palette,
        "candidates": candidates,
        "recommended": recommended,
        "warnings": warnings,
        "claim_limit": "This is a deterministic palette recommendation, not proof of theme meaning, composition quality, or final aesthetic acceptance.",
    }


def _parse_rgb(value: str) -> list[int]:
    try:
        channels = [int(item.strip()) for item in value.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("RGB must use R,G,B integers") from exc
    if len(channels) != 3 or not all(0 <= channel <= 255 for channel in channels):
        raise argparse.ArgumentTypeError("RGB must contain three integers from 0 to 255")
    return channels


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", action="append", required=True, type=Path)
    parser.add_argument(
        "--image-weight",
        action="append",
        type=float,
        help="repeat once per --image; 0.1-5.0 role influence on dye evidence",
    )
    parser.add_argument("--material-id", default="tight_book_cloth")
    parser.add_argument("--strategy", choices=sorted(STRATEGIES), default="auto")
    parser.add_argument("--dye-rgb", type=_parse_rgb)
    parser.add_argument("--theme-note")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = recommend_dye(
            image_paths=args.image,
            material_id=args.material_id,
            selection_strategy=args.strategy,
            dye_rgb=args.dye_rgb,
            theme_note=args.theme_note,
            image_weights=args.image_weight,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
