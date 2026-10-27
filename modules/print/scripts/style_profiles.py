#!/usr/bin/env python3
"""Resolve quantified print-process and art-direction profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "references" / "print-style-presets.json"


def load_catalog() -> dict[str, Any]:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("print-style-presets.json must contain an object")
    return data


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def catalog_errors(catalog: dict[str, Any] | None = None) -> list[str]:
    data = catalog or load_catalog()
    errors: list[str] = []
    process_keys = data.get("process_control_keys")
    art_keys = data.get("art_control_keys")
    processes = data.get("process_presets")
    arts = data.get("art_direction_presets")
    recommendations = data.get("recommendation_sets")
    if not isinstance(process_keys, list) or not process_keys or len(set(process_keys)) != len(process_keys):
        errors.append("process_control_keys must be a unique non-empty array")
        process_keys = []
    if not isinstance(art_keys, list) or not art_keys or len(set(art_keys)) != len(art_keys):
        errors.append("art_control_keys must be a unique non-empty array")
        art_keys = []
    if not isinstance(processes, dict) or not processes:
        errors.append("process_presets must be a non-empty object")
        processes = {}
    if not isinstance(arts, dict) or not arts:
        errors.append("art_direction_presets must be a non-empty object")
        arts = {}

    for name, profile in processes.items():
        prefix = f"process_presets.{name}"
        if not isinstance(profile, dict):
            errors.append(f"{prefix} must be an object")
            continue
        defaults = profile.get("default_controls")
        ranges = profile.get("allowed_ranges")
        if not isinstance(defaults, dict) or set(defaults) != set(process_keys):
            errors.append(f"{prefix}.default_controls must contain every process control exactly once")
        if not isinstance(ranges, dict) or set(ranges) != set(process_keys):
            errors.append(f"{prefix}.allowed_ranges must contain every process control exactly once")
        if isinstance(defaults, dict):
            for key, value in defaults.items():
                if not isinstance(value, int) or not 0 <= value <= 100:
                    errors.append(f"{prefix}.default_controls.{key} must be an integer from 0 to 100")
                limits = ranges.get(key) if isinstance(ranges, dict) else None
                if (
                    isinstance(limits, list) and len(limits) == 2
                    and all(isinstance(item, int) for item in limits)
                    and isinstance(value, int) and not limits[0] <= value <= limits[1]
                ):
                    errors.append(f"{prefix}.default_controls.{key} falls outside its allowed range")
        if not isinstance(profile.get("allowed_screen_modes"), list) or not profile["allowed_screen_modes"]:
            errors.append(f"{prefix}.allowed_screen_modes must be a non-empty array")
        if not isinstance(profile.get("prompt_anchors"), list) or not profile["prompt_anchors"]:
            errors.append(f"{prefix}.prompt_anchors must be a non-empty array")
        renderer = profile.get("renderer_defaults")
        if renderer is not None:
            required_renderer = {
                "supported_reproductions", "cells_per_short_edge", "dot_gain", "max_coverage",
                "jitter_fraction", "ink_load_variation", "edge_softness_px", "dot_shape_roughness",
                "paper_tooth_strength", "gamma", "cmyk_angles_degrees",
            }
            if not isinstance(renderer, dict) or set(renderer) != required_renderer:
                errors.append(f"{prefix}.renderer_defaults must contain the complete renderer target set")
            else:
                supported = renderer["supported_reproductions"]
                if not isinstance(supported, list) or not supported or any(
                    value not in {"monochrome_am", "subtractive_cmyk_am"} for value in supported
                ):
                    errors.append(f"{prefix}.renderer_defaults.supported_reproductions is invalid")
                limits = {
                    "cells_per_short_edge": (180, 960),
                    "dot_gain": (-0.03, 0.10),
                    "max_coverage": (0.50, 0.76),
                    "jitter_fraction": (0.0, 0.10),
                    "ink_load_variation": (0.0, 0.08),
                    "edge_softness_px": (0.0, 0.45),
                    "dot_shape_roughness": (0.0, 0.15),
                    "paper_tooth_strength": (0.0, 0.25),
                    "gamma": (0.65, 1.8),
                }
                for key, (minimum, maximum) in limits.items():
                    value = renderer[key]
                    if not isinstance(value, (int, float)) or not minimum <= value <= maximum:
                        errors.append(f"{prefix}.renderer_defaults.{key} must be from {minimum} to {maximum}")
                angles = renderer["cmyk_angles_degrees"]
                if not isinstance(angles, dict) or set(angles) != {"cyan", "magenta", "yellow", "black"}:
                    errors.append(f"{prefix}.renderer_defaults.cmyk_angles_degrees is invalid")
                elif any(not isinstance(value, (int, float)) or not -90 <= value <= 90 for value in angles.values()):
                    errors.append(f"{prefix}.renderer_defaults.cmyk_angles_degrees values must be from -90 to 90")

    for name, profile in arts.items():
        prefix = f"art_direction_presets.{name}"
        if not isinstance(profile, dict):
            errors.append(f"{prefix} must be an object")
            continue
        defaults = profile.get("default_controls")
        if not isinstance(defaults, dict) or set(defaults) != set(art_keys):
            errors.append(f"{prefix}.default_controls must contain every art control exactly once")
        elif any(not isinstance(value, int) or not 0 <= value <= 100 for value in defaults.values()):
            errors.append(f"{prefix}.default_controls values must be integers from 0 to 100")
        compatible = profile.get("compatible_processes")
        if not isinstance(compatible, list) or not compatible:
            errors.append(f"{prefix}.compatible_processes must be a non-empty array")
        elif any(process not in processes for process in compatible):
            errors.append(f"{prefix}.compatible_processes names an unknown process")

    if not isinstance(recommendations, dict) or not recommendations:
        errors.append("recommendation_sets must be a non-empty object")
    else:
        for goal, options in recommendations.items():
            if not isinstance(options, list) or not 1 <= len(options) <= 3:
                errors.append(f"recommendation_sets.{goal} must contain one to three options")
                continue
            for index, option in enumerate(options):
                prefix = f"recommendation_sets.{goal}[{index}]"
                if not isinstance(option, dict):
                    errors.append(f"{prefix} must be an object")
                    continue
                if option.get("process") not in processes or option.get("art") not in arts:
                    errors.append(f"{prefix} names an unknown preset")
                elif option["process"] not in arts[option["art"]]["compatible_processes"]:
                    errors.append(f"{prefix} uses an incompatible process and art direction")
                for field in ("label", "reason", "tradeoff"):
                    if not _nonempty(option.get(field)):
                        errors.append(f"{prefix}.{field} must be a non-empty string")
    return errors


def _validate_overrides(
    overrides: Any,
    allowed_keys: set[str],
    prefix: str,
    allowed_ranges: dict[str, list[int]] | None = None,
) -> list[str]:
    if not isinstance(overrides, dict):
        return [f"{prefix}.control_overrides must be an object"]
    errors: list[str] = []
    for key, value in overrides.items():
        if key not in allowed_keys:
            errors.append(f"{prefix}.control_overrides contains unknown control: {key}")
            continue
        if not isinstance(value, int) or not 0 <= value <= 100:
            errors.append(f"{prefix}.control_overrides.{key} must be an integer from 0 to 100")
            continue
        if allowed_ranges and key in allowed_ranges:
            minimum, maximum = allowed_ranges[key]
            if not minimum <= value <= maximum:
                errors.append(
                    f"{prefix}.control_overrides.{key} must be from {minimum} to {maximum} for the selected process"
                )
    return errors


def validate_art_direction(selection: Any) -> list[str]:
    if not isinstance(selection, dict):
        return ["art_direction must be an object"]
    required = {"preset", "selection_basis", "control_overrides"}
    errors = [f"art_direction missing field: {field}" for field in sorted(required - set(selection))]
    errors.extend(f"art_direction unexpected field: {field}" for field in sorted(set(selection) - required))
    catalog = load_catalog()
    preset = selection.get("preset")
    if preset not in catalog["art_direction_presets"]:
        errors.append("art_direction.preset is invalid")
    if not _nonempty(selection.get("selection_basis")):
        errors.append("art_direction.selection_basis must be a non-empty string")
    errors.extend(
        _validate_overrides(
            selection.get("control_overrides"),
            set(catalog["art_control_keys"]),
            "art_direction",
        )
    )
    return errors


def validate_style_selection(selection: Any, screen_mode: Any) -> list[str]:
    if not isinstance(selection, dict):
        return ["style_selection must be an object"]
    required = {"process_preset", "art_direction_preset", "selection_basis", "control_overrides"}
    errors = [f"style_selection missing field: {field}" for field in sorted(required - set(selection))]
    errors.extend(f"style_selection unexpected field: {field}" for field in sorted(set(selection) - required))
    catalog = load_catalog()
    process_name = selection.get("process_preset")
    art_name = selection.get("art_direction_preset")
    process = catalog["process_presets"].get(process_name)
    art = catalog["art_direction_presets"].get(art_name)
    if process is None:
        errors.append("style_selection.process_preset is invalid")
    if art is None:
        errors.append("style_selection.art_direction_preset is invalid")
    if process is not None and screen_mode not in process["allowed_screen_modes"]:
        errors.append("screen.mode is incompatible with style_selection.process_preset")
    if process is not None and art is not None and process_name not in art["compatible_processes"]:
        errors.append("style_selection process and art direction are incompatible")
    if not _nonempty(selection.get("selection_basis")):
        errors.append("style_selection.selection_basis must be a non-empty string")
    errors.extend(
        _validate_overrides(
            selection.get("control_overrides"),
            set(catalog["process_control_keys"]),
            "style_selection",
            process.get("allowed_ranges") if process else None,
        )
    )
    return errors


def resolve_art_direction(selection: dict[str, Any]) -> dict[str, Any]:
    errors = validate_art_direction(selection)
    if errors:
        raise ValueError("; ".join(errors))
    catalog = load_catalog()
    profile = catalog["art_direction_presets"][selection["preset"]]
    controls = dict(profile["default_controls"])
    controls.update(selection["control_overrides"])
    return {"name": selection["preset"], "profile": profile, "controls": controls}


def resolve_style_selection(selection: dict[str, Any], screen_mode: str) -> dict[str, Any]:
    errors = validate_style_selection(selection, screen_mode)
    if errors:
        raise ValueError("; ".join(errors))
    catalog = load_catalog()
    process = catalog["process_presets"][selection["process_preset"]]
    art = catalog["art_direction_presets"][selection["art_direction_preset"]]
    controls = dict(process["default_controls"])
    controls.update(selection["control_overrides"])
    return {
        "process_name": selection["process_preset"],
        "process": process,
        "art_name": selection["art_direction_preset"],
        "art": art,
        "controls": controls,
    }


def _band(value: int) -> str:
    if value <= 10:
        return "minimal"
    if value <= 30:
        return "restrained"
    if value <= 55:
        return "moderate"
    if value <= 80:
        return "strong"
    return "dominant"


def _process_anchor(name: str, value: int) -> str:
    if name == "source_fidelity":
        return (
            "source identity, geometry, pose, markings, and color relationships are near-locked; change reproduction only"
            if value >= 80 else "retain recognizability while permitting deliberate graphic simplification"
        )
    if name == "geometry_lock":
        return (
            "crop, object count, positions, scale, overlap, camera, and card boundaries remain fixed"
            if value >= 80 else "preserve the scene skeleton while permitting controlled layout movement"
        )
    if name == "material_separation":
        return (
            "cloth, paper, solid ink, skin, metal, glass, leather, and shadows must read as different physical materials"
            if value >= 80 else "separate major material families without emphasizing microscopic differences"
        )
    if name == "screen_visibility":
        if value <= 10:
            return "the screen is imperceptible at normal size and appears only in a magnified crop"
        if value <= 25:
            return "the image reads first at normal size; discrete dots become clear only at close or 100-percent inspection"
        if value <= 45:
            return "a fine screen is just perceptible at normal size but remains subordinate to the subject"
        if value <= 70:
            return "screen structure is an explicit graphic property while facial and object recognition remain intact"
        return "screen structure is the dominant event and photographic nuance is intentionally sacrificed"
    if name == "paper_fiber_visibility":
        if value <= 10:
            return "paper tooth is nearly invisible except in flat highlights"
        if value <= 30:
            return "quiet fine fibers appear close up and never cross into real objects or cloth"
        return "paper tooth is visibly tactile but must remain physically scaled and zone-bound"
    if name == "ink_absorption":
        if value <= 12:
            return "ink edges stay clean with only microscopic settling into the stock"
        if value <= 35:
            return "ink sits matte within the fibers with restrained edge relaxation and no dirty bleed"
        return "porous-stock absorption is clearly visible and reduces edge crispness"
    if name == "dot_gain":
        if value <= 8:
            return "printed dots remain close to their nominal area and highlights stay very open"
        if value <= 25:
            return "dots expand slightly in middle and dark values while visible paper channels remain"
        return "dot expansion is conspicuous and tonal compression is intentional"
    if name == "edge_softness":
        if value <= 8:
            return "printed edges stay crisp but avoid digital vector sharpness"
        if value <= 28:
            return "printed edges relax by a microscopic amount without blurring identity or object geometry"
        return "soft deposited-ink edges are visible and fine detail is deliberately reduced"
    if name == "ink_load_variation":
        if value <= 10:
            return "ink density variation is barely visible in close crops and never becomes a global noise layer"
        if value <= 28:
            return "small local density variation appears inside deposited ink while solids remain designed"
        return "ink-density variation is a pronounced handmade process characteristic"
    if name == "midtone_retention":
        return (
            "cheeks, hands, metal curvature, fabric folds, and process detail keep a long separated middle-value scale"
            if value >= 80 else "midtones are intentionally compressed into fewer graphic steps"
        )
    if name == "shadow_openness":
        return (
            "three-quarter tones and shadows retain internal separation and visible paper channels"
            if value >= 75 else "shadows may consolidate into broader graphic masses while preserving the subject silhouette"
        )
    if name == "color_restraint":
        if value >= 80:
            return "color approaches a quiet monochrome or highly restrained ink family"
        if value >= 50:
            return "source hues remain recognizable but lose luminous RGB glow and read as matte printed color"
        return "spot colors may be vivid and assertive while remaining ink-like rather than backlit"
    if name == "registration_variance":
        if value <= 5:
            return "channels or spot layers read as cleanly registered; no novelty color fringe"
        if value <= 20:
            return "minute directional registration variation may appear at selected edges only"
        return "registration offset is visibly expressive and must be purposeful rather than random"
    if name == "surface_wear":
        if value <= 5:
            return "the print is clean and contemporary, with intact edges and no theatrical aging"
        if value <= 20:
            return "minor handling evidence may appear only where physically plausible"
        return "wear is a major narrative layer and requires explicit user authorization"
    raise ValueError(f"unknown process control: {name}")


def _art_anchor(name: str, value: int) -> str:
    if name == "physical_realism":
        return (
            "page, cards, frames, objects, thickness, light, and contact must form one photographable physical scene"
            if value >= 80 else "permit deliberate graphic abstraction while preserving plausible contact and depth cues"
        )
    if name == "material_separation":
        return (
            "every material remains identifiable through its own edge, response, texture scale, and shadow"
            if value >= 80 else "separate only the major material families"
        )
    if name == "layout_restraint":
        return (
            "one first read, one supporting read, and calm negative space control the page"
            if value >= 75 else "allow several active graphic events while preserving a decisive reading order"
        )
    if name == "graphic_flatness":
        return (
            "large flat shapes and reduced tonal modeling are deliberate compositional tools"
            if value >= 60 else "retain modeled photographic volume and use flat shapes sparingly"
        )
    if name == "palette_boldness":
        return (
            "use a confident high-contrast color-area relationship with only source-supported hues"
            if value >= 60 else "keep color compressed, material-led, and secondary to hierarchy"
        )
    if name == "type_assertiveness":
        return (
            "authorized display type may become a major page event with controlled scale jumps"
            if value >= 60 else "authorized type stays informational and visually subordinate"
        )
    if name == "asymmetry":
        return (
            "use clear off-axis tension and unequal modules while maintaining physical balance"
            if value >= 55 else "use restrained asymmetry close to a stable central balance"
        )
    if name == "annotation_density":
        return (
            "several factual labels or leaders may organize evidence, but every mark must be source-authorized"
            if value >= 45 else "use zero or one quiet factual note and invent no metadata"
        )
    raise ValueError(f"unknown art control: {name}")


def format_control_lines(controls: dict[str, int], kind: str) -> list[str]:
    anchor = _process_anchor if kind == "process" else _art_anchor
    return [
        f"- {name}: {value}/100 ({_band(value)}) — {anchor(name, value)}."
        for name, value in controls.items()
    ]


def style_recommendations(goal: str) -> list[dict[str, str]]:
    catalog = load_catalog()
    recommendations = catalog["recommendation_sets"]
    if goal not in recommendations:
        raise ValueError(f"unknown recommendation goal: {goal}")
    return recommendations[goal]
