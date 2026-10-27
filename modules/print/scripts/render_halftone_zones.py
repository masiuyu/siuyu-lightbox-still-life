#!/usr/bin/env python3
"""Render fine, deterministic AM halftone inside explicit normalized polygons.

Image generation remains responsible for the physical scene. This renderer is the
fallback when a generated edit cannot produce verifiable dot structure without
contaminating cloth, objects, paper borders, or typography.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps
except ImportError as exc:  # pragma: no cover - environment-specific failure
    raise SystemExit("Pillow is required: python3 -m pip install Pillow") from exc


RESAMPLING = getattr(Image, "Resampling", Image)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _rgb(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(isinstance(channel, int) and 0 <= channel <= 255 for channel in value)
    )


def _polygon(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) >= 3
        and all(
            isinstance(point, list)
            and len(point) == 2
            and all(isinstance(coordinate, (int, float)) and 0 <= coordinate <= 1 for coordinate in point)
            for point in value
        )
    )


def validate_render_card(card: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"version", "route", "input", "output", "output_scale", "screen", "zones"}
    missing = required - set(card)
    extra = set(card) - required
    for field in sorted(missing):
        errors.append(f"missing required field: {field}")
    for field in sorted(extra):
        errors.append(f"unexpected field: {field}")
    if card.get("version") != 1:
        errors.append("version must be 1")
    if card.get("route") not in {"B_object_print_artifacts", "D_full_frame_reproduction"}:
        errors.append("route must be B_object_print_artifacts or D_full_frame_reproduction")
    for field in ("input", "output"):
        if field in card and not _nonempty(card[field]):
            errors.append(f"{field} must be a non-empty path")
    if card.get("output_scale") not in {1, 2}:
        errors.append("output_scale must be 1 or 2")

    screen = card.get("screen")
    if not isinstance(screen, dict):
        errors.append("screen must be an object")
    else:
        required_screen_fields = {
            "cells_per_short_edge", "angle_degrees", "supersample", "dot_gain",
            "max_coverage", "jitter_fraction", "ink_load_variation", "edge_softness_px", "seed",
        }
        allowed_screen_fields = required_screen_fields | {"dot_shape_roughness"}
        for field in sorted(required_screen_fields - set(screen)):
            errors.append(f"screen missing field: {field}")
        for field in sorted(set(screen) - allowed_screen_fields):
            errors.append(f"screen unexpected field: {field}")
        cells = screen.get("cells_per_short_edge")
        if not isinstance(cells, int) or not 180 <= cells <= 960:
            errors.append("screen.cells_per_short_edge must be an integer from 180 to 960")
        angle = screen.get("angle_degrees")
        if not isinstance(angle, (int, float)) or not -45 <= angle <= 45:
            errors.append("screen.angle_degrees must be from -45 to 45")
        if screen.get("supersample") not in {2, 4}:
            errors.append("screen.supersample must be 2 or 4")
        limits = {
            "dot_gain": (-0.03, 0.10),
            "max_coverage": (0.50, 0.76),
            "jitter_fraction": (0.0, 0.10),
            "ink_load_variation": (0.0, 0.08),
            "edge_softness_px": (0.0, 0.45),
        }
        for field, (minimum, maximum) in limits.items():
            value = screen.get(field)
            if not isinstance(value, (int, float)) or not minimum <= value <= maximum:
                errors.append(f"screen.{field} must be from {minimum} to {maximum}")
        roughness = screen.get("dot_shape_roughness", 0.0)
        if not isinstance(roughness, (int, float)) or not 0 <= roughness <= 0.15:
            errors.append("screen.dot_shape_roughness must be from 0 to 0.15 when present")
        if not isinstance(screen.get("seed"), int):
            errors.append("screen.seed must be an integer")

    zones = card.get("zones")
    if not isinstance(zones, list) or not zones:
        errors.append("zones must contain at least one zone")
        zones = []
    names: set[str] = set()
    for index, zone in enumerate(zones):
        prefix = f"zones[{index}]"
        if not isinstance(zone, dict):
            errors.append(f"{prefix} must be an object")
            continue
        required_zone_fields = {
            "name", "polygons", "exclusions", "paper_rgb", "ink_rgb", "black_point",
            "white_point", "gamma", "paper_texture_strength", "preserve_lighting",
        }
        allowed_zone_fields = required_zone_fields | {
            "screen_angle_degrees", "reproduction", "channel_angles_degrees",
            "channel_inks_rgb", "spot_angles_degrees", "spot_inks_rgb", "spot_split",
            "prefilter", "paper_tooth_strength",
        }
        for field in sorted(required_zone_fields - set(zone)):
            errors.append(f"{prefix} missing field: {field}")
        for field in sorted(set(zone) - allowed_zone_fields):
            errors.append(f"{prefix} unexpected field: {field}")
        name = zone.get("name")
        if not _nonempty(name):
            errors.append(f"{prefix}.name must be non-empty")
        elif name in names:
            errors.append(f"duplicate zone name: {name}")
        else:
            names.add(name)
        polygons = zone.get("polygons")
        if not isinstance(polygons, list) or not polygons or not all(_polygon(item) for item in polygons):
            errors.append(f"{prefix}.polygons must contain normalized polygons")
        exclusions = zone.get("exclusions")
        if not isinstance(exclusions, list) or not all(_polygon(item) for item in exclusions):
            errors.append(f"{prefix}.exclusions must contain normalized polygons")
        for field in ("paper_rgb", "ink_rgb"):
            if not _rgb(zone.get(field)):
                errors.append(f"{prefix}.{field} must contain three 0-255 integers")
        black = zone.get("black_point")
        white = zone.get("white_point")
        if not isinstance(black, int) or not 0 <= black <= 120:
            errors.append(f"{prefix}.black_point must be an integer from 0 to 120")
        if not isinstance(white, int) or not 135 <= white <= 255:
            errors.append(f"{prefix}.white_point must be an integer from 135 to 255")
        if isinstance(black, int) and isinstance(white, int) and black >= white:
            errors.append(f"{prefix}.black_point must be below white_point")
        gamma = zone.get("gamma")
        if not isinstance(gamma, (int, float)) or not 0.65 <= gamma <= 1.8:
            errors.append(f"{prefix}.gamma must be from 0.65 to 1.8")
        texture = zone.get("paper_texture_strength")
        if not isinstance(texture, (int, float)) or not 0 <= texture <= 3:
            errors.append(f"{prefix}.paper_texture_strength must be from 0 to 3")
        tooth = zone.get("paper_tooth_strength", 0.0)
        if not isinstance(tooth, (int, float)) or not 0 <= tooth <= 0.25:
            errors.append(f"{prefix}.paper_tooth_strength must be from 0 to 0.25 when present")
        lighting = zone.get("preserve_lighting")
        if not isinstance(lighting, (int, float)) or not 0 <= lighting <= 0.25:
            errors.append(f"{prefix}.preserve_lighting must be from 0 to 0.25")
        zone_angle = zone.get("screen_angle_degrees")
        if zone_angle is not None and (
            not isinstance(zone_angle, (int, float)) or not -90 <= zone_angle <= 90
        ):
            errors.append(f"{prefix}.screen_angle_degrees must be from -90 to 90 when present")
        reproduction = zone.get("reproduction", "monochrome_am")
        if reproduction not in {"monochrome_am", "spot_duotone_am", "subtractive_cmyk_am"}:
            errors.append(
                f"{prefix}.reproduction must be monochrome_am, spot_duotone_am, or subtractive_cmyk_am"
            )
        channel_names = {"cyan", "magenta", "yellow", "black"}
        channel_angles = zone.get("channel_angles_degrees")
        channel_inks = zone.get("channel_inks_rgb")
        spot_names = {"midtone", "shadow"}
        spot_angles = zone.get("spot_angles_degrees")
        spot_inks = zone.get("spot_inks_rgb")
        spot_split = zone.get("spot_split")
        if reproduction == "subtractive_cmyk_am":
            if not isinstance(channel_angles, dict) or set(channel_angles) != channel_names:
                errors.append(f"{prefix}.channel_angles_degrees must contain cyan, magenta, yellow, and black")
            elif any(not isinstance(value, (int, float)) or not -90 <= value <= 90 for value in channel_angles.values()):
                errors.append(f"{prefix}.channel_angles_degrees values must be from -90 to 90")
            if not isinstance(channel_inks, dict) or set(channel_inks) != channel_names:
                errors.append(f"{prefix}.channel_inks_rgb must contain cyan, magenta, yellow, and black")
            elif any(not _rgb(value) for value in channel_inks.values()):
                errors.append(f"{prefix}.channel_inks_rgb values must be RGB triplets")
            if spot_angles is not None or spot_inks is not None or spot_split is not None:
                errors.append(f"{prefix} spot duotone fields require spot_duotone_am reproduction")
        elif reproduction == "spot_duotone_am":
            if not isinstance(spot_angles, dict) or set(spot_angles) != spot_names:
                errors.append(f"{prefix}.spot_angles_degrees must contain midtone and shadow")
            elif any(not isinstance(value, (int, float)) or not -90 <= value <= 90 for value in spot_angles.values()):
                errors.append(f"{prefix}.spot_angles_degrees values must be from -90 to 90")
            if not isinstance(spot_inks, dict) or set(spot_inks) != spot_names:
                errors.append(f"{prefix}.spot_inks_rgb must contain midtone and shadow")
            elif any(not _rgb(value) for value in spot_inks.values()):
                errors.append(f"{prefix}.spot_inks_rgb values must be RGB triplets")
            if not isinstance(spot_split, (int, float)) or not 0.35 <= spot_split <= 0.75:
                errors.append(f"{prefix}.spot_split must be from 0.35 to 0.75")
            if channel_angles is not None or channel_inks is not None:
                errors.append(f"{prefix} CMYK channel fields require subtractive_cmyk_am reproduction")
        elif (
            channel_angles is not None
            or channel_inks is not None
            or spot_angles is not None
            or spot_inks is not None
            or spot_split is not None
        ):
            errors.append(f"{prefix} color separation fields require their matching reproduction mode")
        prefilter = zone.get("prefilter")
        if prefilter is not None:
            expected_prefilter = {"contrast", "lightness", "blur_px", "black_generation"}
            if not isinstance(prefilter, dict) or set(prefilter) != expected_prefilter:
                errors.append(f"{prefix}.prefilter must contain contrast, lightness, blur_px, and black_generation")
            else:
                limits = {
                    "contrast": (0.75, 1.35),
                    "lightness": (-0.2, 0.2),
                    "blur_px": (0.0, 2.0),
                    "black_generation": (0.0, 1.0),
                }
                for field, (minimum, maximum) in limits.items():
                    value = prefilter.get(field)
                    if not isinstance(value, (int, float)) or not minimum <= value <= maximum:
                        errors.append(f"{prefix}.prefilter.{field} must be from {minimum} to {maximum}")
    return errors


def _points(polygon: list[list[float]], width: int, height: int) -> list[tuple[int, int]]:
    return [
        (round(point[0] * (width - 1)), round(point[1] * (height - 1)))
        for point in polygon
    ]


def build_zone_mask(zone: dict[str, Any], size: tuple[int, int]) -> Image.Image:
    width, height = size
    scale = 4
    mask = Image.new("L", (width * scale, height * scale), 0)
    draw = ImageDraw.Draw(mask)
    for polygon in zone["polygons"]:
        draw.polygon([(x * scale, y * scale) for x, y in _points(polygon, width, height)], fill=255)
    for polygon in zone["exclusions"]:
        draw.polygon([(x * scale, y * scale) for x, y in _points(polygon, width, height)], fill=0)
    return mask.resize(size, RESAMPLING.LANCZOS)


def _paper_layer(
    base: Image.Image,
    mask: Image.Image,
    zone: dict[str, Any],
    rng: random.Random,
) -> Image.Image:
    width, height = base.size
    paper = Image.new("RGB", base.size, tuple(zone["paper_rgb"]))
    strength = float(zone["paper_texture_strength"])
    lighting_weight = float(zone["preserve_lighting"])

    if strength > 0:
        fine_size = (max(1, width // 3), max(1, height // 3))
        coarse_size = (max(1, width // 32), max(1, height // 32))
        fine = Image.frombytes("L", fine_size, rng.randbytes(fine_size[0] * fine_size[1]))
        coarse = Image.frombytes("L", coarse_size, rng.randbytes(coarse_size[0] * coarse_size[1]))
        fine = fine.resize(base.size, RESAMPLING.BICUBIC).filter(ImageFilter.GaussianBlur(0.28))
        coarse = coarse.resize(base.size, RESAMPLING.BICUBIC).filter(ImageFilter.GaussianBlur(0.6))
        noise = Image.blend(coarse, fine, 0.72)
        paper_rgb = tuple(zone["paper_rgb"])
        bounded_strength = min(strength, 1.5)
        dark = tuple(max(0, round(channel - 12 * bounded_strength)) for channel in paper_rgb)
        light = tuple(min(255, round(channel + 8 * bounded_strength)) for channel in paper_rgb)
        paper = ImageOps.colorize(noise, dark, light)

    if lighting_weight > 0:
        broad = ImageOps.grayscale(base).filter(ImageFilter.GaussianBlur(max(width, height) * 0.09))
        broad_rgb = ImageOps.colorize(broad, (18, 18, 18), (250, 250, 250))
        paper = Image.blend(paper, broad_rgb, lighting_weight)
    return Image.composite(paper, base, mask)


def _apply_paper_tooth(
    alpha: Image.Image,
    rng: random.Random,
    strength: float,
) -> Image.Image:
    """Let uncoated paper tooth alter ink fill without adding a noise overlay."""
    if strength <= 0:
        return alpha
    width, height = alpha.size
    fine_size = (max(1, width // 6), max(1, height // 6))
    coarse_size = (max(1, width // 36), max(1, height // 36))
    fine = Image.frombytes("L", fine_size, rng.randbytes(fine_size[0] * fine_size[1]))
    coarse = Image.frombytes("L", coarse_size, rng.randbytes(coarse_size[0] * coarse_size[1]))
    fine = fine.resize(alpha.size, RESAMPLING.BICUBIC).filter(ImageFilter.GaussianBlur(0.35))
    coarse = coarse.resize(alpha.size, RESAMPLING.BICUBIC).filter(ImageFilter.GaussianBlur(0.75))
    tooth = Image.blend(coarse, fine, 0.78)
    absorption = tooth.point(
        lambda value: max(0, min(255, round(255 - strength * (255 - value) * 1.5)))
    )
    spread = alpha.filter(ImageFilter.MaxFilter(3))
    ink = Image.blend(alpha, spread, min(0.18, strength * 0.55))
    return ImageChops.multiply(ink, absorption)


def _screen_alpha(
    tone: Image.Image,
    mask: Image.Image,
    zone: dict[str, Any],
    screen: dict[str, Any],
    rng: random.Random,
    *,
    direct_coverage: bool = False,
    effective_angle_override: float | None = None,
    report_name: str | None = None,
) -> tuple[Image.Image, dict[str, Any]]:
    width, height = tone.size
    bbox = mask.getbbox()
    if bbox is None:
        raise ValueError(f"zone {zone['name']} has an empty rasterized mask")
    left, top, right, bottom = bbox
    short_edge = min(width, height)
    cell = short_edge / float(screen["cells_per_short_edge"])
    supersample = int(screen["supersample"])
    effective_angle = float(
        effective_angle_override
        if effective_angle_override is not None
        else zone.get("screen_angle_degrees", screen["angle_degrees"])
    )
    theta = math.radians(effective_angle)
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    blur = tone.filter(ImageFilter.GaussianBlur(max(0.75, cell * 0.45)))
    pixels = blur.load()
    mask_pixels = mask.load()

    corners = ((left, top), (right, top), (left, bottom), (right, bottom))
    transformed = [
        (x * cos_theta + y * sin_theta, -x * sin_theta + y * cos_theta)
        for x, y in corners
    ]
    min_u = min(item[0] for item in transformed) - cell
    max_u = max(item[0] for item in transformed) + cell
    min_v = min(item[1] for item in transformed) - cell
    max_v = max(item[1] for item in transformed) + cell

    alpha_large = Image.new("L", ((right - left) * supersample, (bottom - top) * supersample), 0)
    draw = ImageDraw.Draw(alpha_large)
    black = int(zone["black_point"])
    white = int(zone["white_point"])
    gamma = float(zone["gamma"])
    maximum = float(screen["max_coverage"])
    gain = float(screen["dot_gain"])
    jitter = float(screen["jitter_fraction"])
    load_variation = float(screen["ink_load_variation"])
    shape_roughness = float(screen.get("dot_shape_roughness", 0.0))
    paper_tooth = float(zone.get("paper_tooth_strength", 0.0))
    inked_dots = 0
    coverage_sum = 0.0

    u = math.floor(min_u / cell) * cell + cell / 2
    while u <= max_u:
        v = math.floor(min_v / cell) * cell + cell / 2
        while v <= max_v:
            x = u * cos_theta - v * sin_theta
            y = u * sin_theta + v * cos_theta
            sample_x = min(width - 1, max(0, round(x)))
            sample_y = min(height - 1, max(0, round(y)))
            if left <= sample_x < right and top <= sample_y < bottom and mask_pixels[sample_x, sample_y] > 8:
                if direct_coverage:
                    normalized = pixels[sample_x, sample_y] / 255.0
                else:
                    normalized = (white - pixels[sample_x, sample_y]) / max(1, white - black)
                coverage = min(maximum, max(0.0, normalized) ** gamma + gain)
                if coverage >= 0.008:
                    radius = cell * math.sqrt(coverage / math.pi)
                    radius *= 1 + rng.uniform(-load_variation, load_variation)
                    dx = rng.uniform(-jitter, jitter) * cell
                    dy = rng.uniform(-jitter, jitter) * cell
                    local_x = (x + dx - left) * supersample
                    local_y = (y + dy - top) * supersample
                    radius_large = max(0.35 * supersample, radius * supersample)
                    if shape_roughness > 0:
                        points = []
                        for point_index in range(12):
                            point_angle = math.tau * point_index / 12
                            point_radius = radius_large * (1 + rng.uniform(-shape_roughness, shape_roughness))
                            points.append(
                                (
                                    local_x + math.cos(point_angle) * point_radius,
                                    local_y + math.sin(point_angle) * point_radius,
                                )
                            )
                        draw.polygon(points, fill=255)
                    else:
                        draw.ellipse(
                            (
                                local_x - radius_large,
                                local_y - radius_large,
                                local_x + radius_large,
                                local_y + radius_large,
                            ),
                            fill=255,
                        )
                    inked_dots += 1
                    coverage_sum += coverage
            v += cell
        u += cell

    alpha_large = _apply_paper_tooth(alpha_large, rng, paper_tooth)
    softness = float(screen["edge_softness_px"]) * supersample
    if softness > 0:
        alpha_large = alpha_large.filter(ImageFilter.GaussianBlur(softness))
    alpha_crop = alpha_large.resize((right - left, bottom - top), RESAMPLING.LANCZOS)
    alpha = Image.new("L", tone.size, 0)
    alpha.paste(alpha_crop, (left, top))
    alpha = ImageChops.multiply(alpha, mask)
    return alpha, {
        "name": report_name or zone["name"],
        "mask_bbox_px": [left, top, right, bottom],
        "screen_cell_px": round(cell, 3),
        "screen_cell_px_at_1080_short_edge": round(1080 / float(screen["cells_per_short_edge"]), 3),
        "effective_angle_degrees": round(effective_angle, 3),
        "inked_dot_count": inked_dots,
        "mean_requested_coverage": round(coverage_sum / inked_dots, 4) if inked_dots else 0.0,
        "paper_tooth_strength": round(paper_tooth, 4),
        "paper_rgb": zone["paper_rgb"],
        "ink_rgb": zone["ink_rgb"],
    }


def _prefilter(base: Image.Image, zone: dict[str, Any]) -> Image.Image:
    settings = zone.get("prefilter") or {
        "contrast": 1.0,
        "lightness": 0.0,
        "blur_px": 0.0,
        "black_generation": 0.72,
    }
    prepared = base
    blur_px = float(settings["blur_px"])
    if blur_px > 0:
        prepared = prepared.filter(ImageFilter.GaussianBlur(blur_px))
    contrast = float(settings["contrast"])
    if contrast != 1:
        prepared = ImageEnhance.Contrast(prepared).enhance(contrast)
    lightness = float(settings["lightness"])
    if lightness != 0:
        prepared = ImageEnhance.Brightness(prepared).enhance(1 + lightness)
    return prepared


def _cmyk_coverage_channels(base: Image.Image, black_generation: float) -> dict[str, Image.Image]:
    red, green, blue = base.split()
    cyan_raw = ImageOps.invert(red)
    magenta_raw = ImageOps.invert(green)
    yellow_raw = ImageOps.invert(blue)
    shared_neutral = ImageChops.darker(ImageChops.darker(cyan_raw, magenta_raw), yellow_raw)
    black = shared_neutral.point(lambda value: round(value * black_generation))
    return {
        "cyan": ImageChops.subtract(cyan_raw, black),
        "magenta": ImageChops.subtract(magenta_raw, black),
        "yellow": ImageChops.subtract(yellow_raw, black),
        "black": black,
    }


def _duotone_coverage_channels(
    base: Image.Image,
    black_point: int,
    white_point: int,
    gamma: float,
    split: float,
) -> dict[str, Image.Image]:
    """Build two tonal separations whose overprint preserves open paper highlights."""
    gray = ImageOps.grayscale(base)
    scale = max(1, white_point - black_point)

    def darkness(value: int) -> float:
        normalized = max(0.0, min(1.0, (white_point - value) / scale))
        return normalized ** gamma

    dark = gray.point(lambda value: round(255 * darkness(value)))
    midtone = dark.point(
        lambda value: round(
            value
            * (
                1.0
                - 0.34
                * max(0.0, (value / 255.0 - split) / max(0.001, 1.0 - split))
            )
        )
    )
    shadow = dark.point(
        lambda value: round(
            255
            * max(0.0, min(1.0, (value / 255.0 - split) / max(0.001, 1.0 - split)))
        )
    )
    return {"midtone": midtone, "shadow": shadow}


def _multiply_absorbed_ink(
    base: Image.Image,
    ink_rgb: list[int],
    alpha: Image.Image,
    opacity: float,
) -> Image.Image:
    effective_alpha = alpha.point(lambda value: round(value * opacity))
    factors = [
        effective_alpha.point(lambda value, channel=channel: round(255 - value * (255 - channel) / 255))
        for channel in ink_rgb
    ]
    return ImageChops.multiply(base, Image.merge("RGB", factors))


def render(card: dict[str, Any], root: Path | None = None) -> tuple[Image.Image, dict[str, Any]]:
    errors = validate_render_card(card)
    if errors:
        raise ValueError("; ".join(errors))
    base_root = root or Path.cwd()
    input_path = Path(card["input"])
    if not input_path.is_absolute():
        input_path = base_root / input_path
    base = Image.open(input_path).convert("RGB")
    output_scale = int(card["output_scale"])
    if output_scale == 2:
        base = base.resize((base.width * 2, base.height * 2), RESAMPLING.LANCZOS)
    result = base.copy()
    combined_mask = Image.new("L", base.size, 0)
    zone_reports: list[dict[str, Any]] = []

    zone_masks = [build_zone_mask(zone, base.size) for zone in card["zones"]]
    for mask in zone_masks:
        combined_mask = ImageChops.lighter(combined_mask, mask)
    hard_inside = combined_mask.point(lambda value: 255 if value > 0 else 0)
    mask_pixels = sum(hard_inside.histogram()[1:])
    mask_percent = mask_pixels * 100.0 / (base.width * base.height)
    if card["route"] == "B_object_print_artifacts" and mask_percent > 55:
        raise ValueError(
            f"Route B halftone zones cover {mask_percent:.3f} percent; more than 55 percent is a probable global-screen error"
        )

    for index, (zone, mask) in enumerate(zip(card["zones"], zone_masks)):
        rng = random.Random(int(card["screen"]["seed"]) + index * 1009)
        result = _paper_layer(result, mask, zone, rng)
        prepared = _prefilter(base, zone)
        reproduction = zone.get("reproduction", "monochrome_am")
        if reproduction == "subtractive_cmyk_am":
            black_generation = float((zone.get("prefilter") or {}).get("black_generation", 0.72))
            coverages = _cmyk_coverage_channels(prepared, black_generation)
            channel_reports: list[dict[str, Any]] = []
            channel_opacity = {"cyan": 0.78, "magenta": 0.78, "yellow": 0.72, "black": 0.84}
            for channel_index, channel_name in enumerate(("yellow", "cyan", "magenta", "black")):
                channel_rng = random.Random(int(card["screen"]["seed"]) + index * 1009 + channel_index * 173)
                alpha, channel_report = _screen_alpha(
                    coverages[channel_name],
                    mask,
                    zone,
                    card["screen"],
                    channel_rng,
                    direct_coverage=True,
                    effective_angle_override=float(zone["channel_angles_degrees"][channel_name]),
                    report_name=channel_name,
                )
                result = _multiply_absorbed_ink(
                    result,
                    zone["channel_inks_rgb"][channel_name],
                    alpha,
                    channel_opacity[channel_name],
                )
                channel_reports.append(channel_report)
            zone_report = {
                "name": zone["name"],
                "reproduction": reproduction,
                "mask_bbox_px": list(mask.getbbox() or (0, 0, 0, 0)),
                "paper_rgb": zone["paper_rgb"],
                "channel_reports": channel_reports,
                "prefilter": zone.get("prefilter") or {
                    "contrast": 1.0,
                    "lightness": 0.0,
                    "blur_px": 0.0,
                    "black_generation": 0.72,
                },
            }
        elif reproduction == "spot_duotone_am":
            coverages = _duotone_coverage_channels(
                prepared,
                int(zone["black_point"]),
                int(zone["white_point"]),
                float(zone["gamma"]),
                float(zone["spot_split"]),
            )
            channel_reports = []
            for channel_index, channel_name in enumerate(("midtone", "shadow")):
                channel_rng = random.Random(int(card["screen"]["seed"]) + index * 1009 + channel_index * 173)
                channel_zone = dict(zone)
                channel_zone["gamma"] = 1.0
                channel_zone["ink_rgb"] = zone["spot_inks_rgb"][channel_name]
                alpha, channel_report = _screen_alpha(
                    coverages[channel_name],
                    mask,
                    channel_zone,
                    card["screen"],
                    channel_rng,
                    direct_coverage=True,
                    effective_angle_override=float(zone["spot_angles_degrees"][channel_name]),
                    report_name=channel_name,
                )
                result = _multiply_absorbed_ink(
                    result,
                    zone["spot_inks_rgb"][channel_name],
                    alpha,
                    0.9 if channel_name == "midtone" else 0.94,
                )
                channel_reports.append(channel_report)
            zone_report = {
                "name": zone["name"],
                "reproduction": reproduction,
                "mask_bbox_px": list(mask.getbbox() or (0, 0, 0, 0)),
                "paper_rgb": zone["paper_rgb"],
                "spot_split": zone["spot_split"],
                "channel_reports": channel_reports,
                "prefilter": zone.get("prefilter") or {
                    "contrast": 1.0,
                    "lightness": 0.0,
                    "blur_px": 0.0,
                    "black_generation": 0.72,
                },
            }
        else:
            tone = ImageOps.grayscale(prepared)
            alpha, zone_report = _screen_alpha(tone, mask, zone, card["screen"], rng)
            zone_report["reproduction"] = reproduction
            ink = Image.new("RGB", base.size, tuple(zone["ink_rgb"]))
            result = Image.composite(ink, result, alpha)
        zone_reports.append(zone_report)

    difference = ImageChops.difference(base, result).convert("L")
    outside = ImageChops.multiply(difference, ImageOps.invert(hard_inside))
    histogram = outside.histogram()
    outside_changed = sum(histogram[1:])
    width, height = base.size
    report = {
        "version": 1,
        "method": "deterministic_clustered_am_zone_render",
        "route": card["route"],
        "input": str(input_path),
        "output": card["output"],
        "width": width,
        "height": height,
        "aspect_ratio": round(width / height, 6),
        "screen": card["screen"],
        "combined_zone_percent": round(mask_percent, 3),
        "zones": zone_reports,
        "outside_zone_changed_pixels": outside_changed,
        "claim_limit": "This report proves renderer parameters and zone containment, not press provenance or aesthetic acceptance.",
    }
    return result, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path, help="render-card JSON")
    parser.add_argument("--output", type=Path, help="override card output path")
    parser.add_argument("--report", type=Path, help="write renderer evidence JSON")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    card = json.loads(args.input.read_text(encoding="utf-8"))
    errors = validate_render_card(card)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if args.validate_only:
        print("Halftone render card is valid.")
        return 0

    result, report = render(card, args.input.parent)
    output = args.output or Path(card["output"])
    if not output.is_absolute():
        output = args.input.parent / output
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    report["output"] = str(output)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
