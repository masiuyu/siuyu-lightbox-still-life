#!/usr/bin/env python3
"""Compile optional, surface-specific print directions for the native image tool."""
from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE = Path(__file__).resolve().parents[1] / "modules" / "print"


def _runtime(name):
    spec = importlib.util.spec_from_file_location("lightbox_" + name, MODULE / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + " must be a non-empty string")
    return value.strip()


def _fields(value, required, optional, label):
    if not isinstance(value, dict):
        raise ValueError(label + " must be an object")
    if set(value) - required - optional or required - set(value):
        raise ValueError(label + " needs fields " + ", ".join(sorted(required)) + "; optional: " + ", ".join(sorted(optional)))


def _selection(selection, fields, label):
    _fields(selection, set(fields) | {"selection_basis", "control_overrides"}, set(), label)
    for key in (*fields, "selection_basis"):
        _text(selection[key], label + "." + key)
    if not isinstance(selection["control_overrides"], dict):
        raise ValueError(label + ".control_overrides must be an object")


def print_lines(record, content_ids, content_scope, photography):
    _fields(record, {"layout", "art_direction", "carrier", "zones"}, set(), "design.print")
    layout = _text(record["layout"], "print.layout")
    layouts = {
        "object_prints": "Real objects and related bounded prints share one composed scene.",
        "carrier_transfer": "The selected graphic is deposited ink on the carrier; preserve its recognizable silhouette and source relationships.",
        "typographic": "Authorized exact copy and graphics share a declared physical carrier.",
        "full_frame": "Reproduce the complete authorized source image, preserving its crop, relative geometry and internal arrangement.",
    }
    if layout not in layouts:
        raise ValueError("print.layout must be object_prints, carrier_transfer, typographic or full_frame")
    if layout == "full_frame" and content_scope != "explicit_image":
        raise ValueError("full_frame printing requires explicit_image content scope")
    if layout == "full_frame" and not content_ids:
        raise ValueError("full_frame printing requires a supplied content image")
    style = _runtime("style_profiles")
    _selection(record["art_direction"], ("preset",), "print.art_direction")
    art = style.resolve_art_direction(record["art_direction"])
    carrier = record["carrier"]
    _fields(carrier, {"material_id", "base_rgb", "color_basis"}, {"description"}, "print.carrier")
    material_id = _text(carrier["material_id"], "carrier.material_id")
    materials = _runtime("carrier_materials").material_index()
    ordinary = {
        "uncoated_paper": "Uncoated paper with its own fine tooth and absorbed ink.",
        "light_table": "A luminous diffuser supporting separately described physical print surfaces.",
        "custom": "Use the authored material and its stated optical behavior.",
    }
    if material_id not in materials and material_id not in ordinary:
        raise ValueError("unknown print carrier material_id: " + material_id)
    if material_id in materials:
        description = materials[material_id]["intent"] + " An opaque woven carrier receives reflected light; its crossed fibers remain subordinate to the image."
        if photography.get("profile") in {"transmitted_inventory", "diffused_paper_archive"}:
            raise ValueError("woven print carriers require reflected-light photography; use print_editorial or a complete custom setup")
    else:
        description = ordinary[material_id]
    if material_id == "custom":
        description += " " + _text(carrier.get("description"), "custom carrier.description")
    elif "description" in carrier:
        description += " " + _text(carrier["description"], "carrier.description")
    rgb = carrier["base_rgb"]
    if not isinstance(rgb, list) or len(rgb) != 3 or any(type(x) is not int or not 0 <= x <= 255 for x in rgb):
        raise ValueError("carrier.base_rgb must contain three integers from 0 to 255")
    basis = _text(carrier["color_basis"], "carrier.color_basis")
    lines = [
        "Print composition: " + layouts[layout],
        "Print carrier: " + material_id + ". " + description,
        "Carrier base color RGB: " + str(rgb) + ". Color basis: " + basis,
        "Print art direction: " + art["name"] + ". " + record["art_direction"]["selection_basis"],
        "Relative art-direction priorities (0–100; descriptive priorities):\n" + "\n".join(style.format_control_lines(art["controls"], "art")),
        "Each print setting applies only to its named surface. Real objects retain their physical volume, reflections and contact. Paper has its own tooth and edge; carrier ink follows the carrier's texture. Transmission occurs only through materials declared translucent. The authored canvas and camera remain in force.",
    ]
    zones = record["zones"]
    if not isinstance(zones, list) or not zones:
        raise ValueError("print.zones must be a non-empty list")
    ids, surfaces = set(), []
    allowed_separations = {
        "fine_color_AM": {"duotone", "cmyk"}, "fine_monochrome_AM": {"monochrome"},
        "FM_stochastic": {"monochrome", "duotone", "cmyk"},
        "spot_screenprint": {"spot"}, "riso_spot_dither": {"spot"}, "gravure_cells": {"monochrome"},
    }
    for zone in zones:
        _fields(zone, {"id", "surface", "sources", "treatment"}, {"style_selection", "screen_mode", "color_separation", "exact_copy"}, "print zone")
        zone_id = _text(zone["id"], "print zone.id")
        if zone_id in ids:
            raise ValueError("print zone IDs must be unique")
        ids.add(zone_id)
        surface = _text(zone["surface"], "print zone.surface")
        if surface not in {"real_object", "paper_print", "carrier_print", "solid_ink"}:
            raise ValueError("invalid print zone surface: " + surface)
        surfaces.append(surface)
        sources = zone["sources"]
        if not isinstance(sources, list) or any(not isinstance(x, str) or x not in content_ids for x in sources) or len(sources) != len(set(sources)):
            raise ValueError("print zone.sources must name unique supplied content IDs")
        lines.append(f"Surface {zone_id} ({surface}; sources: {', '.join(sources) or 'authored concept'}): " + _text(zone["treatment"], "print zone.treatment"))
        if "exact_copy" in zone:
            if surface != "solid_ink":
                raise ValueError("exact_copy belongs to a solid_ink surface")
            lines.append("Authorized visible copy, reproduce exactly: " + _text(zone["exact_copy"], "zone.exact_copy"))
        if surface in {"real_object", "solid_ink"}:
            if set(zone) & {"style_selection", "screen_mode", "color_separation"}:
                raise ValueError(surface + " uses its stated material, without a photographic screen selection")
            lines.append("Use the declared object's physical finish." if surface == "real_object" else "Print these authored marks as solid ink; preserve letterforms and exact copy.")
            continue
        for key in ("style_selection", "screen_mode", "color_separation"):
            if key not in zone:
                raise ValueError("printed surface needs " + key)
        _selection(zone["style_selection"], ("process_preset", "art_direction_preset"), "zone.style_selection")
        if zone["style_selection"]["art_direction_preset"] != art["name"]:
            raise ValueError("all printed surfaces must share the selected art-direction preset")
        mode = _text(zone["screen_mode"], "zone.screen_mode")
        separation = _text(zone["color_separation"], "zone.color_separation")
        resolved = style.resolve_style_selection(zone["style_selection"], mode)
        if separation not in allowed_separations.get(mode, set()):
            raise ValueError("print color_separation is incompatible with screen_mode")
        lines += [
            "Process on " + zone_id + ": " + resolved["process_name"] + "; screen " + mode + "; color separation " + separation + ". " + zone["style_selection"]["selection_basis"],
            "Relative priorities within this surface and its authored geometry:\n" + "\n".join(style.format_control_lines(resolved["controls"], "process")),
        ]
        if surface == "carrier_print":
            lines.append("Carrier transfer: ink conforms to the same substrate relief, with restrained fiber-valley coverage variation and edge absorption. The graphic has deposited-ink thickness and substrate contact; its silhouette is the print boundary. Keep broad ink fills substantially opaque and retain the authored recognition features.")
        else:
            lines.append("Bounded print: the image and paper share one plane, crop, rotation and occlusion. Tonal values are formed by the selected separation; the paper edge and contact shadow belong to the physical sheet.")
    if layout == "carrier_transfer" and "carrier_print" not in surfaces:
        raise ValueError("carrier_transfer needs a carrier_print surface")
    if layout in {"object_prints", "full_frame"} and not set(surfaces) & {"paper_print", "carrier_print"}:
        raise ValueError(layout + " needs a printed image surface")
    if layout == "full_frame" and not any(x["surface"] in {"paper_print", "carrier_print"} and x["sources"] for x in zones):
        raise ValueError("full_frame needs its source bound to a printed surface")
    if layout == "typographic" and not any(x.get("exact_copy") for x in zones):
        raise ValueError("typographic layout needs authorized exact_copy")
    lines.append("These controls describe visual intent, not image-tool parameters, measured LPI or proof of mathematically constructed dots. Inspect the actual image at delivery size and 100-percent detail; record visual findings separately from compiler checks and user acceptance.")
    return lines
