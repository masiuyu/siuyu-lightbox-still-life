#!/usr/bin/env python3
"""Compose source-space print plates onto paper cards or woven carriers.

This path prevents the thin unscreened wedges produced by tracing print masks
after a scene has already been rasterized.  A photographic source is screened
in its own rectangular paper plane; the printed image and its paper border then
receive one shared transform.  Spot artwork is transferred directly to the
carrier without a cast shadow and with restrained substrate show-through.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import tempfile
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps, ImageStat
except ImportError as exc:  # pragma: no cover - environment-specific failure
    raise SystemExit("Pillow is required: python3 -m pip install Pillow") from exc

from render_halftone_zones import render as render_halftone, validate_render_card
from carrier_materials import RENDER_LIMITS, load_material_library, material_index, resolve_material


RESAMPLING = getattr(Image, "Resampling", Image)


def _rgb(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(isinstance(channel, int) and 0 <= channel <= 255 for channel in value)
    )


def _number_pair(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, (int, float)) for item in value)
    )


def _positive_int_pair(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, int) and item > 0 for item in value)
    )


def validate_card(card: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"version", "canvas", "carrier", "layers", "output"}
    for field in sorted(required - set(card)):
        errors.append(f"missing required field: {field}")
    for field in sorted(set(card) - required):
        errors.append(f"unexpected field: {field}")
    if card.get("version") != 1:
        errors.append("version must be 1")

    canvas = card.get("canvas")
    if not isinstance(canvas, dict) or set(canvas) != {"width", "height"}:
        errors.append("canvas must contain width and height")
    elif not all(isinstance(canvas.get(key), int) and canvas[key] >= 256 for key in ("width", "height")):
        errors.append("canvas width and height must be integers of at least 256")

    carrier = card.get("carrier")
    carrier_fields = {
        "material_id", "dye_rgb", "dye_strategy", "source_palette_evidence",
        "illumination", "seed",
    }
    if not isinstance(carrier, dict):
        errors.append("carrier must be an object")
    else:
        renderer_overrides = set(RENDER_LIMITS)
        allowed_carrier = carrier_fields | renderer_overrides | {
            "texture_source", "texture_source_strength",
        }
        for field in sorted(carrier_fields - set(carrier)):
            errors.append(f"carrier missing field: {field}")
        for field in sorted(set(carrier) - allowed_carrier):
            errors.append(f"carrier unexpected field: {field}")
        try:
            profiles = material_index(load_material_library())
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            profiles = {}
            errors.append(f"material library is invalid: {exc}")
        if carrier.get("material_id") not in profiles:
            errors.append("carrier.material_id must identify a material in references/material-library.json")
        if not _rgb(carrier.get("dye_rgb")):
            errors.append("carrier.dye_rgb must be an RGB triplet")
        if carrier.get("dye_strategy") not in {
            "explicit_user_palette",
            "recessive_complement",
            "analogous_shadow",
            "neutralized_source",
            "theme_directed",
        }:
            errors.append("carrier.dye_strategy is invalid")
        evidence = carrier.get("source_palette_evidence")
        if not isinstance(evidence, dict) or set(evidence) != {"source_rgb", "source_influence", "selection_basis"}:
            errors.append("carrier.source_palette_evidence must contain source_rgb, source_influence, and selection_basis")
        else:
            source_rgb = evidence.get("source_rgb")
            if (
                not isinstance(source_rgb, list)
                or not 1 <= len(source_rgb) <= 8
                or not all(_rgb(color) for color in source_rgb)
            ):
                errors.append("carrier.source_palette_evidence.source_rgb must contain 1 to 8 RGB triplets")
            if not isinstance(evidence.get("selection_basis"), str) or not evidence["selection_basis"].strip():
                errors.append("carrier.source_palette_evidence.selection_basis must be non-empty")
            influence = evidence.get("source_influence")
            if (
                not isinstance(influence, list)
                or not influence
                or any(
                    not isinstance(item, dict)
                    or set(item) != {"source_ref", "weight"}
                    or not isinstance(item.get("source_ref"), str)
                    or not item["source_ref"].strip()
                    or not isinstance(item.get("weight"), (int, float))
                    or not 0.1 <= item["weight"] <= 5.0
                    for item in influence
                )
            ):
                errors.append("carrier.source_palette_evidence.source_influence must record source_ref and a 0.1-5.0 weight")

        limits = {
            **RENDER_LIMITS,
            "illumination": (0.0, 0.18),
            "texture_source_strength": (0.0, 1.0),
        }
        for field, (minimum, maximum) in limits.items():
            if field not in carrier and field in renderer_overrides | {"texture_source_strength"}:
                continue
            value = carrier.get(field)
            if not isinstance(value, (int, float)) or not minimum <= value <= maximum:
                errors.append(f"carrier.{field} must be from {minimum} to {maximum}")
        if not isinstance(carrier.get("seed"), int):
            errors.append("carrier.seed must be an integer")
        if "texture_source_strength" in carrier and not carrier.get("texture_source"):
            errors.append("carrier.texture_source_strength requires texture_source")

    layers = card.get("layers")
    if not isinstance(layers, list) or not layers:
        errors.append("layers must contain at least one layer")
        layers = []
    ids: set[str] = set()
    for index, layer in enumerate(layers):
        prefix = f"layers[{index}]"
        if not isinstance(layer, dict):
            errors.append(f"{prefix} must be an object")
            continue
        layer_id = layer.get("id")
        if not isinstance(layer_id, str) or not layer_id.strip():
            errors.append(f"{prefix}.id must be non-empty")
        elif layer_id in ids:
            errors.append(f"duplicate layer id: {layer_id}")
        else:
            ids.add(layer_id)
        kind = layer.get("kind")
        common = {"id", "kind", "source", "position", "rotation_degrees"}
        if kind == "photo_card":
            required_photo = common | {
                "interior_size", "crop_focal", "border_px", "paper_rgb", "ink_rgb",
                "paper_texture", "reproduction", "screen", "tone", "shadow",
            }
            allowed_photo = required_photo | {
                "channel_angles_degrees", "channel_inks_rgb",
                "spot_angles_degrees", "spot_inks_rgb", "spot_split",
            }
            for field in sorted(required_photo - set(layer)):
                errors.append(f"{prefix} missing field: {field}")
            for field in sorted(set(layer) - allowed_photo):
                errors.append(f"{prefix} unexpected field: {field}")
            if not _positive_int_pair(layer.get("interior_size")):
                errors.append(f"{prefix}.interior_size must contain two positive integers")
            focal = layer.get("crop_focal")
            if not _number_pair(focal) or not all(0 <= item <= 1 for item in focal or []):
                errors.append(f"{prefix}.crop_focal must contain two values from 0 to 1")
            if not isinstance(layer.get("border_px"), int) or not 4 <= layer.get("border_px", 0) <= 160:
                errors.append(f"{prefix}.border_px must be an integer from 4 to 160")
            for field in ("paper_rgb", "ink_rgb"):
                if not _rgb(layer.get(field)):
                    errors.append(f"{prefix}.{field} must be an RGB triplet")
            if not isinstance(layer.get("screen"), dict):
                errors.append(f"{prefix}.screen must be an object")
            if not isinstance(layer.get("tone"), dict):
                errors.append(f"{prefix}.tone must be an object")
            if not isinstance(layer.get("shadow"), dict):
                errors.append(f"{prefix}.shadow must be an object")
            paper_texture = layer.get("paper_texture")
            if not isinstance(paper_texture, (int, float)) or not 0 <= paper_texture <= 3:
                errors.append(f"{prefix}.paper_texture must be from 0 to 3")
            reproduction = layer.get("reproduction")
            if reproduction not in {"monochrome_am", "spot_duotone_am", "subtractive_cmyk_am"}:
                errors.append(
                    f"{prefix}.reproduction must be monochrome_am, spot_duotone_am, or subtractive_cmyk_am"
                )
            if isinstance(layer.get("screen"), dict) and isinstance(layer.get("tone"), dict):
                tone = layer["tone"]
                zone = {
                    "name": str(layer_id or f"layer-{index}"),
                    "polygons": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]],
                    "exclusions": [],
                    "paper_rgb": layer.get("paper_rgb"),
                    "ink_rgb": layer.get("ink_rgb"),
                    "black_point": tone.get("black_point"),
                    "white_point": tone.get("white_point"),
                    "gamma": tone.get("gamma"),
                    "paper_texture_strength": paper_texture,
                    "paper_tooth_strength": tone.get("paper_tooth_strength"),
                    "preserve_lighting": tone.get("preserve_lighting"),
                    "prefilter": tone.get("prefilter"),
                    "reproduction": reproduction,
                }
                if reproduction == "subtractive_cmyk_am":
                    zone["channel_angles_degrees"] = layer.get("channel_angles_degrees")
                    zone["channel_inks_rgb"] = layer.get("channel_inks_rgb")
                elif reproduction == "spot_duotone_am":
                    zone["spot_angles_degrees"] = layer.get("spot_angles_degrees")
                    zone["spot_inks_rgb"] = layer.get("spot_inks_rgb")
                    zone["spot_split"] = layer.get("spot_split")
                dummy_render_card = {
                    "version": 1,
                    "route": "D_full_frame_reproduction",
                    "input": "source.png",
                    "output": "output.png",
                    "output_scale": 1,
                    "screen": layer["screen"],
                    "zones": [zone],
                }
                for render_error in validate_render_card(dummy_render_card):
                    errors.append(f"{prefix}: {render_error}")
            if isinstance(layer.get("shadow"), dict):
                shadow = layer["shadow"]
                if set(shadow) != {"offset_px", "blur_px", "opacity"}:
                    errors.append(f"{prefix}.shadow must contain offset_px, blur_px, and opacity")
                if not _number_pair(shadow.get("offset_px")):
                    errors.append(f"{prefix}.shadow.offset_px must contain x and y")
                blur = shadow.get("blur_px")
                opacity = shadow.get("opacity")
                if not isinstance(blur, (int, float)) or not 0 <= blur <= 60:
                    errors.append(f"{prefix}.shadow.blur_px must be from 0 to 60")
                if not isinstance(opacity, (int, float)) or not 0 <= opacity <= 0.6:
                    errors.append(f"{prefix}.shadow.opacity must be from 0 to 0.6")
        elif kind == "spot_screenprint":
            required_spot = common | {
                "width", "palette", "ink_opacity", "substrate_imprint", "fiber_relief",
                "pigment_penetration", "ink_deposit_variation", "seed", "edge_softness_px",
            }
            for field in sorted(required_spot - set(layer)):
                errors.append(f"{prefix} missing field: {field}")
            for field in sorted(set(layer) - required_spot):
                errors.append(f"{prefix} unexpected field: {field}")
            if not isinstance(layer.get("width"), int) or layer.get("width", 0) < 64:
                errors.append(f"{prefix}.width must be an integer of at least 64")
            palette = layer.get("palette")
            if not isinstance(palette, list) or not 2 <= len(palette) <= 8 or not all(_rgb(item) for item in palette):
                errors.append(f"{prefix}.palette must contain 2 to 8 RGB triplets")
            for field, minimum, maximum in (
                ("ink_opacity", 0.55, 1.0),
                ("substrate_imprint", 0.0, 0.35),
                ("fiber_relief", 0.0, 0.45),
                ("pigment_penetration", 0.0, 0.40),
                ("ink_deposit_variation", 0.0, 0.24),
                ("edge_softness_px", 0.0, 1.2),
            ):
                value = layer.get(field)
                if not isinstance(value, (int, float)) or not minimum <= value <= maximum:
                    errors.append(f"{prefix}.{field} must be from {minimum} to {maximum}")
            if not isinstance(layer.get("seed"), int):
                errors.append(f"{prefix}.seed must be an integer")
        else:
            errors.append(f"{prefix}.kind must be photo_card or spot_screenprint")

        if kind in {"photo_card", "spot_screenprint"}:
            if not isinstance(layer.get("source"), str) or not layer["source"].strip():
                errors.append(f"{prefix}.source must be a non-empty path")
            if not _number_pair(layer.get("position")):
                errors.append(f"{prefix}.position must contain x and y")
            angle = layer.get("rotation_degrees")
            if not isinstance(angle, (int, float)) or not -45 <= angle <= 45:
                errors.append(f"{prefix}.rotation_degrees must be from -45 to 45")

    if not isinstance(card.get("output"), str) or not card.get("output", "").strip():
        errors.append("output must be a non-empty path")
    return errors


def _resolve(path: str, root: Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def _cover_crop(image: Image.Image, size: tuple[int, int], focal: tuple[float, float]) -> Image.Image:
    target_width, target_height = size
    scale = max(target_width / image.width, target_height / image.height)
    resized = image.resize(
        (max(target_width, round(image.width * scale)), max(target_height, round(image.height * scale))),
        RESAMPLING.LANCZOS,
    )
    excess_x = resized.width - target_width
    excess_y = resized.height - target_height
    left = round(excess_x * focal[0])
    top = round(excess_y * focal[1])
    return resized.crop((left, top, left + target_width, top + target_height))


def _detail_map(image: Image.Image, radius: float = 2.4) -> Image.Image:
    gray = ImageOps.grayscale(image)
    blurred = gray.filter(ImageFilter.GaussianBlur(radius))
    return ImageChops.add(gray, ImageOps.invert(blurred), scale=1.0, offset=-127)


def _centered_scale(image: Image.Image, factor: float) -> Image.Image:
    return image.point(
        lambda value: max(0, min(255, round(128 + (value - 128) * factor)))
    )


def _offset_neutral(image: Image.Image, dx: int, dy: int) -> Image.Image:
    """Shift an L image without wrapping; newly exposed pixels stay neutral."""
    width, height = image.size
    result = Image.new("L", image.size, 128)
    source_left = max(0, -dx)
    source_top = max(0, -dy)
    source_right = min(width, width - dx)
    source_bottom = min(height, height - dy)
    if source_right > source_left and source_bottom > source_top:
        result.paste(
            image.crop((source_left, source_top, source_right, source_bottom)),
            (max(0, dx), max(0, dy)),
        )
    return result


def _relief_from_height(height: Image.Image) -> Image.Image:
    shifted = _offset_neutral(height, 1, 1)
    relief = ImageChops.add(height, ImageOps.invert(shifted), scale=1.0, offset=-127)
    return relief.filter(ImageFilter.GaussianBlur(0.22))


def build_book_cloth_material(
    size: tuple[int, int],
    carrier: dict[str, Any],
    root: Path,
) -> tuple[Image.Image, Image.Image, Image.Image, dict[str, Any]]:
    width, height = size
    profile, settings = resolve_material(carrier)
    rng = random.Random(int(carrier["seed"]))
    base_rgb = tuple(carrier["dye_rgb"])
    period = max(3, round(settings["weave_period_px"]))
    weave_contrast = settings["weave_contrast"]
    fiber_noise = settings["fiber_noise"]

    light = round(128 + weave_contrast)
    dark = round(128 - weave_contrast)
    thread_width = max(1, round(period * 0.28))
    bend_step = max(12, period * 4)

    warp = Image.new("L", size, 128)
    warp_draw = ImageDraw.Draw(warp)
    for nominal_x in range(period // 2, width + period, period):
        center = nominal_x + rng.choice((-1, 0, 0, 0, 1))
        points = []
        for y in range(-bend_step, height + bend_step, bend_step):
            points.append((center + rng.choice((-1, 0, 0, 0, 1)), y))
        thread_light = max(0, min(255, light + rng.choice((-2, -1, 0, 0, 1, 2))))
        warp_draw.line(points, fill=dark, width=thread_width + 2, joint="curve")
        warp_draw.line(points, fill=thread_light, width=thread_width, joint="curve")

    weft = Image.new("L", size, 128)
    weft_draw = ImageDraw.Draw(weft)
    for nominal_y in range(period // 2, height + period, period):
        center = nominal_y + rng.choice((-1, 0, 0, 0, 1))
        points = []
        for x in range(-bend_step, width + bend_step, bend_step):
            points.append((x, center + rng.choice((-1, 0, 0, 0, 1))))
        thread_light = max(0, min(255, light + rng.choice((-2, -1, 0, 0, 1, 2))))
        weft_draw.line(points, fill=dark, width=thread_width + 2, joint="curve")
        weft_draw.line(points, fill=thread_light, width=thread_width, joint="curve")

    over_under = Image.new("L", size, 128)
    over_under_draw = ImageDraw.Draw(over_under)
    for row, y in enumerate(range(0, height, period)):
        for column, x in enumerate(range(0, width, period)):
            value = 210 if (row + column) % 2 == 0 else 46
            over_under_draw.rectangle((x, y, min(width, x + period), min(height, y + period)), fill=value)
    over_under = over_under.filter(ImageFilter.GaussianBlur(0.52))
    weave = Image.composite(warp, weft, over_under)

    loose_fibers = Image.new("L", size, 128)
    fiber_draw = ImageDraw.Draw(loose_fibers)
    fiber_count = max(80, round(width * height / max(1, period * period) * 0.018))
    for _ in range(fiber_count):
        x = rng.randrange(width)
        y = rng.randrange(height)
        length = rng.randint(period, period * 4)
        value = round(128 + rng.uniform(-0.65, 0.65) * weave_contrast)
        if rng.random() < 0.5:
            fiber_draw.line((x, y, min(width - 1, x + length), y + rng.choice((-1, 0, 1))), fill=value)
        else:
            fiber_draw.line((x, y, x + rng.choice((-1, 0, 1)), min(height - 1, y + length)), fill=value)
    loose_fibers = loose_fibers.filter(ImageFilter.GaussianBlur(0.2))
    weave = Image.blend(weave, loose_fibers, 0.14).filter(ImageFilter.GaussianBlur(0.24))

    noise_size = (max(1, width // 5), max(1, height // 5))
    noise = Image.frombytes("L", noise_size, rng.randbytes(noise_size[0] * noise_size[1]))
    noise = noise.resize(size, RESAMPLING.BICUBIC).filter(ImageFilter.GaussianBlur(0.38))
    noise = ImageEnhance.Contrast(noise).enhance(fiber_noise / 10.0)
    height_map = Image.blend(weave, noise, min(0.42, fiber_noise / 24.0))

    source_path = carrier.get("texture_source")
    if source_path:
        source = Image.open(_resolve(source_path, root)).convert("RGB")
        source = _cover_crop(source, size, (0.5, 0.5))
        source_detail = _detail_map(source, 3.2)
        source_detail = ImageEnhance.Contrast(source_detail).enhance(1.2)
        height_map = Image.blend(
            height_map,
            source_detail,
            float(carrier.get("texture_source_strength", 0.0)),
        )

    height_map = ImageEnhance.Contrast(height_map).enhance(1.12)
    relief_map = _relief_from_height(height_map)

    illumination = float(carrier["illumination"])
    small = (max(2, width // 24), max(2, height // 24))
    broad = Image.new("L", small)
    broad_pixels = broad.load()
    for y in range(small[1]):
        for x in range(small[0]):
            nx = x / max(1, small[0] - 1)
            ny = y / max(1, small[1] - 1)
            directional = (0.62 - 0.45 * nx - 0.28 * ny)
            broad_pixels[x, y] = max(0, min(255, round(128 + 128 * illumination * directional)))
    broad = broad.resize(size, RESAMPLING.BICUBIC).filter(ImageFilter.GaussianBlur(max(width, height) * 0.015))
    relief_strength = settings["relief_strength"]
    surface_tone = _centered_scale(height_map, 0.42 + relief_strength * 0.72)
    directional_relief = _centered_scale(relief_map, relief_strength * 2.15)
    texture = ImageChops.add(surface_tone, directional_relief, scale=1.0, offset=-128)
    texture = ImageChops.add(texture, broad, scale=1.0, offset=-128)

    # The same height and relief maps are reused by transferred inks.  This is
    # what makes substrate shading continue through a print instead of reading
    # as a texture overlay pasted above or below it.
    channels = []
    for channel in base_rgb:
        constant = Image.new("L", size, channel)
        channels.append(ImageChops.add(constant, texture, scale=1.0, offset=-128))
    resolved = {
        "material_id": profile["id"],
        "display_name": profile["display_name"],
        "kind": profile["kind"],
        "renderer_support": profile["renderer_support"],
        "render_settings": settings,
    }
    return Image.merge("RGB", channels), height_map, relief_map, resolved


def build_book_cloth(size: tuple[int, int], carrier: dict[str, Any], root: Path) -> Image.Image:
    return build_book_cloth_material(size, carrier, root)[0]


def _paper(size: tuple[int, int], paper_rgb: list[int], strength: float, seed: int) -> Image.Image:
    rng = random.Random(seed)
    width, height = size
    noise_size = (max(1, width // 4), max(1, height // 4))
    noise = Image.frombytes("L", noise_size, rng.randbytes(noise_size[0] * noise_size[1]))
    noise = noise.resize(size, RESAMPLING.BICUBIC).filter(ImageFilter.GaussianBlur(0.5))
    noise = ImageEnhance.Contrast(noise).enhance(max(0.0, strength))
    base = tuple(paper_rgb)
    dark = tuple(max(0, round(channel - 7 * strength)) for channel in base)
    light = tuple(min(255, round(channel + 6 * strength)) for channel in base)
    return ImageOps.colorize(noise, dark, light)


def _photo_card(
    layer: dict[str, Any],
    root: Path,
    temporary_root: Path,
) -> tuple[Image.Image, dict[str, Any]]:
    interior_size = tuple(layer["interior_size"])
    source = Image.open(_resolve(layer["source"], root)).convert("RGB")
    focal = tuple(float(item) for item in layer["crop_focal"])
    source = _cover_crop(source, interior_size, focal)
    source_path = temporary_root / f"{layer['id']}-source.png"
    source.save(source_path)

    screen = dict(layer["screen"])
    tone = dict(layer["tone"])
    render_card = {
        "version": 1,
        "route": "D_full_frame_reproduction",
        "input": source_path.name,
        "output": f"{layer['id']}-print.png",
        "output_scale": 1,
        "screen": screen,
        "zones": [{
            "name": layer["id"],
            "polygons": [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]],
            "exclusions": [],
            "paper_rgb": layer["paper_rgb"],
            "ink_rgb": layer["ink_rgb"],
            "black_point": tone["black_point"],
            "white_point": tone["white_point"],
            "gamma": tone["gamma"],
            "paper_texture_strength": layer["paper_texture"],
            "paper_tooth_strength": tone["paper_tooth_strength"],
            "preserve_lighting": tone["preserve_lighting"],
            "prefilter": tone["prefilter"],
            "reproduction": layer["reproduction"],
        }],
    }
    if layer["reproduction"] == "subtractive_cmyk_am":
        render_card["zones"][0]["channel_angles_degrees"] = layer["channel_angles_degrees"]
        render_card["zones"][0]["channel_inks_rgb"] = layer["channel_inks_rgb"]
    elif layer["reproduction"] == "spot_duotone_am":
        render_card["zones"][0]["spot_angles_degrees"] = layer["spot_angles_degrees"]
        render_card["zones"][0]["spot_inks_rgb"] = layer["spot_inks_rgb"]
        render_card["zones"][0]["spot_split"] = layer["spot_split"]
    printed, render_report = render_halftone(render_card, temporary_root)
    border = int(layer["border_px"])
    card_size = (printed.width + 2 * border, printed.height + 2 * border)
    paper = _paper(card_size, layer["paper_rgb"], float(layer["paper_texture"]), int(screen["seed"]) + 97)
    paper.paste(printed, (border, border))
    card = paper.convert("RGBA")
    card.putalpha(Image.new("L", card.size, 255))
    image_window_alpha = card.getchannel("A").crop((border, border, border + printed.width, border + printed.height))
    unfilled = sum(image_window_alpha.histogram()[:-1])
    report = {
        "id": layer["id"],
        "kind": "photo_card",
        "source_space_plate": True,
        "shared_card_transform": True,
        "posthoc_scene_mask": False,
        "photo_window_unfilled_pixels": unfilled,
        "interior_size": list(interior_size),
        "card_size_before_transform": list(card_size),
        "reproduction": layer["reproduction"],
        "halftone": render_report,
    }
    return card, report


def _quantize_spot(image: Image.Image, colors: list[list[int]]) -> Image.Image:
    palette_image = Image.new("P", (1, 1))
    flat = [channel for color in colors for channel in color]
    flat.extend([0] * (768 - len(flat)))
    palette_image.putpalette(flat)
    rgb = image.convert("RGB")
    quantized = rgb.quantize(palette=palette_image, dither=Image.Dither.NONE)
    return quantized.convert("RGB")


def _spot_screenprint(layer: dict[str, Any], root: Path) -> tuple[Image.Image, dict[str, Any]]:
    source = Image.open(_resolve(layer["source"], root)).convert("RGBA")
    if source.getchannel("A").getextrema()[0] == 255:
        raise ValueError(
            f"spot layer {layer['id']} has no transparent background; extract a source-space alpha plate first"
        )
    bbox = source.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError(f"spot layer {layer['id']} has no nontransparent pixels")
    source = source.crop(bbox)
    width = int(layer["width"])
    height = max(1, round(source.height * width / source.width))
    source = source.resize((width, height), RESAMPLING.LANCZOS)
    rgb = _quantize_spot(source, layer["palette"])
    alpha = source.getchannel("A")
    softness = float(layer["edge_softness_px"])
    if softness > 0:
        alpha = alpha.filter(ImageFilter.GaussianBlur(softness))
    plate = rgb.convert("RGBA")
    plate.putalpha(alpha)
    report = {
        "id": layer["id"],
        "kind": "spot_screenprint",
        "source_space_plate": True,
        "continuous_tone_removed": True,
        "spot_color_count": len(layer["palette"]),
        "cast_shadow_added": False,
        "substrate_imprint": layer["substrate_imprint"],
        "fiber_relief": layer["fiber_relief"],
        "pigment_penetration": layer["pigment_penetration"],
        "ink_deposit_variation": layer["ink_deposit_variation"],
        "plate_size_before_transform": [width, height],
    }
    return plate, report


def _rotated(image: Image.Image, angle: float) -> Image.Image:
    return image.rotate(angle, resample=RESAMPLING.BICUBIC, expand=True)


def _placement_xy(position: list[float], size: tuple[int, int]) -> tuple[int, int]:
    return round(position[0] - size[0] / 2), round(position[1] - size[1] / 2)


def _paste_photo_card(
    canvas: Image.Image,
    card: Image.Image,
    layer: dict[str, Any],
) -> tuple[Image.Image, tuple[int, int, int, int]]:
    transformed = _rotated(card, float(layer["rotation_degrees"]))
    x, y = _placement_xy(layer["position"], transformed.size)
    shadow = layer["shadow"]
    alpha = transformed.getchannel("A")
    blur = float(shadow["blur_px"])
    shadow_alpha = alpha.filter(ImageFilter.GaussianBlur(blur)).point(
        lambda value: round(value * float(shadow["opacity"]))
    )
    shadow_layer = Image.new("RGBA", transformed.size, (0, 0, 0, 0))
    shadow_layer.putalpha(shadow_alpha)
    offset_x, offset_y = (int(value) for value in shadow["offset_px"])
    canvas.alpha_composite(shadow_layer, (x + offset_x, y + offset_y))
    canvas.alpha_composite(transformed, (x, y))
    return canvas, (x, y, x + transformed.width, y + transformed.height)


def _paste_spot_print(
    canvas: Image.Image,
    plate: Image.Image,
    carrier: Image.Image,
    carrier_height: Image.Image,
    carrier_relief: Image.Image,
    layer: dict[str, Any],
) -> tuple[Image.Image, tuple[int, int, int, int], dict[str, Any]]:
    before = canvas.copy()
    transformed = _rotated(plate, float(layer["rotation_degrees"]))
    x, y = _placement_xy(layer["position"], transformed.size)

    plate_canvas = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    plate_canvas.alpha_composite(transformed, (x, y))
    alpha = plate_canvas.getchannel("A")
    penetration = float(layer["pigment_penetration"])
    if penetration > 0:
        wicked = alpha.filter(ImageFilter.MaxFilter(3))
        wicked = wicked.filter(ImageFilter.GaussianBlur(0.18 + penetration * 0.9))
        alpha = Image.blend(alpha, wicked, min(0.36, penetration * 0.9))
    alpha = alpha.point(lambda value: round(value * float(layer["ink_opacity"])))

    imprint = float(layer["substrate_imprint"])
    tooth = carrier_height.point(
        lambda value: max(218, min(255, round(255 - imprint * (255 - value) * 0.58)))
    )
    alpha = ImageChops.multiply(alpha, tooth)

    deposit_variation = float(layer["ink_deposit_variation"])
    if deposit_variation > 0:
        rng = random.Random(int(layer["seed"]))
        small = (max(1, canvas.width // 5), max(1, canvas.height // 5))
        deposit_noise = Image.frombytes("L", small, rng.randbytes(small[0] * small[1]))
        deposit_noise = deposit_noise.resize(canvas.size, RESAMPLING.BICUBIC)
        deposit_noise = deposit_noise.filter(ImageFilter.GaussianBlur(0.32))
        deposit_map = deposit_noise.point(
            lambda value: max(
                220,
                min(255, round(255 - deposit_variation * (255 - value) * 0.68)),
            )
        )
        alpha = ImageChops.multiply(alpha, deposit_map)

    fiber_relief = float(layer["fiber_relief"])
    height_shading = _centered_scale(carrier_height, fiber_relief * 0.62)
    directional_shading = _centered_scale(carrier_relief, fiber_relief * 2.25)
    ink_shading = ImageChops.add(height_shading, directional_shading, scale=1.0, offset=-128)
    red, green, blue, _ = plate_canvas.split()
    plate_canvas = Image.merge(
        "RGBA",
        (
            ImageChops.add(red, ink_shading, scale=1.0, offset=-128),
            ImageChops.add(green, ink_shading, scale=1.0, offset=-128),
            ImageChops.add(blue, ink_shading, scale=1.0, offset=-128),
            alpha,
        ),
    )
    canvas.alpha_composite(plate_canvas)
    hard_inside = alpha.point(lambda value: 255 if value > 0 else 0)
    difference = ImageChops.difference(before.convert("RGB"), canvas.convert("RGB")).convert("L")
    outside = ImageChops.multiply(difference, ImageOps.invert(hard_inside))
    outside_changed = sum(outside.histogram()[1:])
    relief_std = round(ImageStat.Stat(ink_shading, hard_inside).stddev[0], 3)
    return (
        canvas,
        (x, y, x + transformed.width, y + transformed.height),
        {
            "outside_spot_changed_pixels": outside_changed,
            "ink_relief_modulation_std": relief_std,
            "effective_alpha_mean": round(ImageStat.Stat(alpha, hard_inside).mean[0], 3),
        },
    )


def compose(card: dict[str, Any], root: Path | None = None) -> tuple[Image.Image, dict[str, Any]]:
    errors = validate_card(card)
    if errors:
        raise ValueError("; ".join(errors))
    base_root = root or Path.cwd()
    size = (int(card["canvas"]["width"]), int(card["canvas"]["height"]))
    carrier, carrier_height, carrier_relief, resolved_material = build_book_cloth_material(
        size,
        card["carrier"],
        base_root,
    )
    carrier_gray = ImageOps.grayscale(carrier)
    carrier_high_pass = _detail_map(carrier, 8.0)
    carrier_local_std = round(ImageStat.Stat(carrier_gray).stddev[0], 3)
    carrier_high_pass_std = round(ImageStat.Stat(carrier_high_pass).stddev[0], 3)
    canvas = carrier.convert("RGBA")
    reports: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="preprinted-planes-") as directory:
        temporary_root = Path(directory)
        for layer in card["layers"]:
            if layer["kind"] == "photo_card":
                prepared, layer_report = _photo_card(layer, base_root, temporary_root)
                canvas, bounds = _paste_photo_card(canvas, prepared, layer)
            else:
                prepared, layer_report = _spot_screenprint(layer, base_root)
                canvas, bounds, coupling_report = _paste_spot_print(
                    canvas,
                    prepared,
                    carrier,
                    carrier_height,
                    carrier_relief,
                    layer,
                )
                layer_report.update(coupling_report)
            layer_report["canvas_bounds_after_transform"] = list(bounds)
            layer_report["inside_canvas"] = (
                bounds[0] >= 0 and bounds[1] >= 0 and bounds[2] <= size[0] and bounds[3] <= size[1]
            )
            reports.append(layer_report)

    result = canvas.convert("RGB")
    outside_zone_changed = sum(
        int(layer_report.get("outside_spot_changed_pixels", 0))
        for layer_report in reports
    )
    report = {
        "version": 1,
        "method": "source_space_preprinted_plane_compositor",
        "width": size[0],
        "height": size[1],
        "aspect_ratio": round(size[0] / size[1], 6),
        "carrier": {
            "material_id": resolved_material["material_id"],
            "display_name": resolved_material["display_name"],
            "kind": resolved_material["kind"],
            "renderer_support": resolved_material["renderer_support"],
            "dye_rgb": card["carrier"]["dye_rgb"],
            "dye_strategy": card["carrier"]["dye_strategy"],
            "source_palette_evidence": card["carrier"]["source_palette_evidence"],
            **resolved_material["render_settings"],
            "texture_source_used": bool(card["carrier"].get("texture_source")),
            "luminance_std": carrier_local_std,
            "high_pass_luminance_std": carrier_high_pass_std,
            "height_map_std": round(ImageStat.Stat(carrier_height).stddev[0], 3),
            "relief_map_std": round(ImageStat.Stat(carrier_relief).stddev[0], 3),
        },
        "layers": reports,
        "outside_zone_changed_pixels": outside_zone_changed,
        "all_layers_inside_canvas": all(report.get("inside_canvas") is True for report in reports),
        "geometry_claim": "Printed content and its substrate share one local transform; no final-scene polygon is estimated.",
        "claim_limit": "The report proves the declared construction path, not press provenance or aesthetic acceptance.",
    }
    return result, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path, help="preprinted-plane composition JSON")
    parser.add_argument("--output", type=Path, help="override output path")
    parser.add_argument("--report", type=Path, help="write construction report JSON")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    card = json.loads(args.input.read_text(encoding="utf-8"))
    errors = validate_card(card)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if args.validate_only:
        print("Preprinted-plane card is valid.")
        return 0

    result, report = compose(card, args.input.parent)
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
