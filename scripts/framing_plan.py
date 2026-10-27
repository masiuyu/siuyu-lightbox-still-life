#!/usr/bin/env python3
"""Estimate coplanar framing margins and detail allocation from a declared plan."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


def fields(value, required, optional, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    missing = set(required) - value.keys()
    extra = value.keys() - set(required) - set(optional)
    if missing or extra:
        raise ValueError(f"{label}: missing {sorted(missing)}, unknown {sorted(extra)}")


def number(value, label, minimum=None, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    try:
        result = float(value)
    except OverflowError as error:
        raise ValueError(f"{label} is outside the numeric range") from error
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    if (positive and result <= 0) or (minimum is not None and result < minimum):
        raise ValueError(f"{label} is outside the allowed range")
    return result


def pair(value, label, positive=False):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{label} must contain two numbers")
    return [number(v, label, positive=positive) for v in value]


def identifier(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value.strip()


def finite_result(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("calculated result exceeds the numeric range")
    if isinstance(value, dict):
        for child in value.values():
            finite_result(child)
    if isinstance(value, list):
        for child in value:
            finite_result(child)


def fit_view(width, height, ratio):
    """Expand about the fixed origin to match output aspect, preserving scale."""
    if width / height >= ratio:
        result = [width, width / ratio]
    else:
        result = [height * ratio, height]
    finite_result(result)
    if min(result) <= 0:
        raise ValueError("calculated view is too small for the numeric range")
    return result


def analyze_plan(plan):
    fields(plan, ("dimension_basis", "unit", "output_px", "view_size", "items"),
           ("basis_note", "margin", "details"), "plan")
    basis = plan["dimension_basis"]
    if basis not in ("design_assumption", "user_supplied", "measured"):
        raise ValueError("dimension_basis must be design_assumption, user_supplied or measured")
    if plan["unit"] not in ("mm", "cm", "m"):
        raise ValueError("unit must be mm, cm or m; all lengths use this unit")
    note = plan.get("basis_note", "")
    if not isinstance(note, str):
        raise ValueError("basis_note must be text")
    output = plan["output_px"]
    if not isinstance(output, list) or len(output) != 2 or any(type(v) is not int or v <= 0 for v in output):
        raise ValueError("output_px must contain two positive integers")
    for value in output:
        number(value, "output_px", positive=True)
    ratio = number(output[0] / output[1], "output aspect", positive=True)
    requested_view = pair(plan["view_size"], "view_size", positive=True)
    view = fit_view(*requested_view, ratio)
    margin = number(plan.get("margin", 0), "margin", minimum=0)
    # A rounding tolerance, not a physical or perceptual acceptance threshold.
    tolerance = max(view) * 1e-12
    px_per_unit = number(output[0] / view[0], "pixels per unit", positive=True)
    items = plan["items"]
    if not isinstance(items, list) or not items:
        raise ValueError("items must be a nonempty list")
    seen, results = set(), []
    for item in items:
        fields(item, ("id", "center", "size"), ("rotation_deg",), "item")
        name = identifier(item["id"], "item id")
        if name in seen:
            raise ValueError(f"duplicate item id: {name}")
        seen.add(name)
        x, y = pair(item["center"], f"{name} center")
        width, height = pair(item["size"], f"{name} size", positive=True)
        angle = number(item.get("rotation_deg", 0), f"{name} rotation_deg") % 360
        radians = math.radians(angle)
        c, s = math.cos(radians), math.sin(radians)
        bx = abs(width * c) + abs(height * s)
        by = abs(width * s) + abs(height * c)
        box = [x - bx / 2, y - by / 2, x + bx / 2, y + by / 2]
        distances = {"left": box[0] + view[0] / 2, "top": box[1] + view[1] / 2,
                     "right": view[0] / 2 - box[2], "bottom": view[1] / 2 - box[3]}
        finite_result([*box, *distances.values()])
        results.append({"id": name, "center": [x, y], "size": [width, height],
                        "rotation_deg_clockwise": angle, "bounds_xyxy": box,
                        "edge_clearance": distances,
                        "inside_view": all(v >= -tolerance for v in distances.values()),
                        "planned_margin_met": all(v >= margin - tolerance for v in distances.values())})
    union = [min(row["bounds_xyxy"][0] for row in results), min(row["bounds_xyxy"][1] for row in results),
             max(row["bounds_xyxy"][2] for row in results), max(row["bounds_xyxy"][3] for row in results)]
    required = [2 * (max(abs(union[0]), abs(union[2])) + margin),
                2 * (max(abs(union[1]), abs(union[3])) + margin)]
    finite_result(required)
    recommended = fit_view(*required, ratio)
    detail_results, seen_details = [], set()
    details = plan.get("details", [])
    if not isinstance(details, list):
        raise ValueError("details must be a list")
    for detail in details:
        fields(detail, ("id", "width"), (), "detail")
        name = identifier(detail["id"], "detail id")
        if name in seen_details:
            raise ValueError(f"duplicate detail id: {name}")
        seen_details.add(name)
        width = number(detail["width"], f"{name} width", positive=True)
        pixels = number(width * px_per_unit, f"{name} projected pixels", positive=True)
        after = number(width * output[0] / recommended[0], f"{name} fitted pixels", positive=True)
        detail_results.append({"id": name, "width": width, "span_px_in_current_view": pixels,
                               "span_px_in_minimum_centered_view": after, "subpixel_span_in_current_view": pixels < 1})
    result = {"state": "PLANNING_ESTIMATE", "unit": plan["unit"],
              "dimension_basis_declared": basis, "dimension_basis_verified": False,
              "basis_note": note, "coordinate_system": "origin at view center; x right; y down; positive rotation clockwise",
              "output_px": output, "requested_minimum_view_size": requested_view,
              "effective_view_size": view, "aspect_expansion_applied": view != requested_view,
              "requested_margin": margin, "rounding_tolerance": tolerance,
              "pixels_per_unit": px_per_unit, "items": results, "layout_bounds_xyxy": union,
              "all_planned_margins_met": all(row["planned_margin_met"] for row in results),
              "minimum_centered_view_size_for_layout_and_margin": recommended,
              "details": detail_results, "visual_readability_evaluated": False,
              "image_generation": "NOT_RUN"}
    finite_result(result)
    return result


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def framing_report(plan_path, output=None):
    path = plan_path.resolve()
    raw = path.read_bytes()
    plan = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_object)
    result = analyze_plan(plan)
    result["plan_file"] = {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()}
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        result["output"] = str(output.resolve())
    return result
