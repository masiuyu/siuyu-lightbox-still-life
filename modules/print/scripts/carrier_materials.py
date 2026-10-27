#!/usr/bin/env python3
"""Load and resolve the executable woven-carrier material library."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MATERIAL_LIBRARY_PATH = ROOT / "references" / "material-library.json"

RENDER_LIMITS = {
    "weave_period_px": (3.0, 12.0),
    "weave_contrast": (0.0, 14.0),
    "fiber_noise": (0.0, 12.0),
    "relief_strength": (0.0, 0.45),
}
INK_RESPONSE_KEYS = {
    "substrate_imprint",
    "fiber_relief",
    "pigment_penetration",
}


def _bounded_pair(value: Any, minimum: float, maximum: float) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, (int, float)) for item in value)
        and minimum <= float(value[0]) <= float(value[1]) <= maximum
    )


def library_errors(library: dict[str, Any]) -> list[str]:
    """Return structural errors without mutating or normalizing the catalog."""
    errors: list[str] = []
    if library.get("version") != 1:
        errors.append("material library version must be 1")
    if library.get("library_kind") != "executable_woven_carriers":
        errors.append("material library kind must be executable_woven_carriers")
    if not isinstance(library.get("units_note"), str) or not library["units_note"].strip():
        errors.append("material library units_note must be non-empty")

    materials = library.get("materials")
    if not isinstance(materials, list) or not materials:
        errors.append("material library must contain materials")
        return errors

    identifiers: set[str] = set()
    required = {
        "id",
        "display_name",
        "kind",
        "intent",
        "renderer_support",
        "render_defaults",
        "dye_constraints",
        "ink_response_starting_ranges",
        "use_when",
        "avoid_when",
    }
    for index, material in enumerate(materials):
        prefix = f"materials[{index}]"
        if not isinstance(material, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = required - set(material)
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(sorted(missing))}")
        material_id = material.get("id")
        if not isinstance(material_id, str) or not material_id.strip():
            errors.append(f"{prefix}.id must be non-empty")
        elif material_id in identifiers:
            errors.append(f"duplicate material id: {material_id}")
        else:
            identifiers.add(material_id)
        if material.get("kind") != "woven_textile":
            errors.append(f"{prefix}.kind must be woven_textile")
        if material.get("renderer_support") != "source_space_compositor_v1":
            errors.append(f"{prefix}.renderer_support is unsupported")
        for field in ("display_name", "intent", "use_when", "avoid_when"):
            if not isinstance(material.get(field), str) or not material[field].strip():
                errors.append(f"{prefix}.{field} must be non-empty")

        defaults = material.get("render_defaults")
        if not isinstance(defaults, dict) or set(defaults) != set(RENDER_LIMITS):
            errors.append(f"{prefix}.render_defaults must contain the four renderer controls")
        else:
            for field, (minimum, maximum) in RENDER_LIMITS.items():
                value = defaults.get(field)
                if not isinstance(value, (int, float)) or not minimum <= float(value) <= maximum:
                    errors.append(f"{prefix}.render_defaults.{field} must be from {minimum} to {maximum}")

        constraints = material.get("dye_constraints")
        if not isinstance(constraints, dict):
            errors.append(f"{prefix}.dye_constraints must be an object")
        else:
            if constraints.get("color_space") != "HSL_normalized":
                errors.append(f"{prefix}.dye_constraints.color_space must be HSL_normalized")
            if not _bounded_pair(constraints.get("saturation_range"), 0.0, 1.0):
                errors.append(f"{prefix}.dye_constraints.saturation_range is invalid")
            if not _bounded_pair(constraints.get("lightness_range"), 0.0, 1.0):
                errors.append(f"{prefix}.dye_constraints.lightness_range is invalid")

        response = material.get("ink_response_starting_ranges")
        if not isinstance(response, dict) or set(response) != INK_RESPONSE_KEYS:
            errors.append(f"{prefix}.ink_response_starting_ranges is incomplete")
        else:
            for field, value in response.items():
                if not _bounded_pair(value, 0.0, 0.45):
                    errors.append(f"{prefix}.ink_response_starting_ranges.{field} is invalid")

    default_id = library.get("default_material_id")
    if not isinstance(default_id, str) or default_id not in identifiers:
        errors.append("default_material_id must identify a declared material")
    return errors


def load_material_library(path: Path | None = None) -> dict[str, Any]:
    source = path or MATERIAL_LIBRARY_PATH
    library = json.loads(source.read_text(encoding="utf-8"))
    errors = library_errors(library)
    if errors:
        raise ValueError("; ".join(errors))
    return library


def material_index(library: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    resolved = library or load_material_library()
    return {material["id"]: material for material in resolved["materials"]}


def resolve_material(
    carrier: dict[str, Any],
    library: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, float]]:
    """Resolve one material preset, then apply explicitly allowed renderer overrides."""
    profiles = material_index(library)
    material_id = carrier.get("material_id")
    if material_id not in profiles:
        raise ValueError(f"unknown material_id: {material_id}")
    profile = profiles[material_id]
    settings = {
        key: float(value)
        for key, value in profile["render_defaults"].items()
    }
    for key in RENDER_LIMITS:
        if key in carrier:
            settings[key] = float(carrier[key])
    return profile, settings
