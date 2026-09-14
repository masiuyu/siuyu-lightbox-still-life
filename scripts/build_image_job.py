#!/usr/bin/env python3
"""Compile an authored photographic direction into native image-tool arguments."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path


def words(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must contain an authored decision")
    return value.strip()


def decision_lines(record, content_ids):
    if not isinstance(record, dict):
        raise ValueError("decisions needs subject, scene and candidate selections")
    allowed = {"scope", "content_scope", "identity_sources", "subject_basis", "scene", "candidates", "selected", "selection_reason"}
    if set(record) - allowed:
        raise ValueError("unknown decisions fields: " + ", ".join(sorted(set(record) - allowed)))
    scope = record.get("scope")
    if scope not in {"open", "directed"}:
        raise ValueError("decisions.scope must be open or directed")
    content_scope = record.get("content_scope")
    if not isinstance(content_scope, dict) or set(content_scope) != {"kind", "basis"}:
        raise ValueError("decisions.content_scope needs kind and basis")
    subject_relations = {"subject_structure", "subject_surface", "fabrication_material", "independent_object"}
    scene_relations = subject_relations | {"scene_content", "complete_image"}
    permitted = {
        "subject_study": subject_relations,
        "explicit_scene": scene_relations,
        "explicit_image": subject_relations | {"complete_image"},
    }
    kind = content_scope.get("kind")
    if not isinstance(kind, str) or kind not in permitted:
        raise ValueError("decisions.content_scope.kind must be subject_study, explicit_scene or explicit_image")
    words(content_scope.get("basis"), "decisions.content_scope.basis")
    scope_intent = {
        "subject_study": "Depict the listed subject structures and surfaces. Drawings share those features; material samples study the selected fabrication materials. Each accompanying object has its own stated identity and purpose.",
        "explicit_scene": "Depict the objects and relationships in the user-specified scene, within each listed target scope and carrier.",
        "explicit_image": "Preserve the requested complete image on its stated depicted surface. Physical subjects and accompanying objects follow their separately listed target scopes.",
    }
    identity = record.get("identity_sources")
    if (not isinstance(identity, list) or (content_ids and not identity)
            or any(not isinstance(x, str) or x not in content_ids for x in identity)):
        raise ValueError("decisions.identity_sources must identify supplied content, or be empty for a textual concept")
    lines = ["Content scope: " + scope_intent[kind],
             "Identity sources: " + (", ".join(identity) or "text brief"),
             "Subject basis: " + words(record.get("subject_basis"), "decisions.subject_basis")]
    scene = record.get("scene")
    if not isinstance(scene, dict) or set(scene) - {"carrier", "state", "intent", "support", "activity"}:
        raise ValueError("decisions.scene needs carrier, state, intent, support and activity")
    for field in ("carrier", "intent", "support"):
        lines.append(f"Scene {field}: " + words(scene.get(field), "decisions.scene." + field))
    state, activity = scene.get("state"), scene.get("activity")
    if state not in {"static", "active"} or not isinstance(activity, list):
        raise ValueError("decisions.scene needs a static or active state and an activity list")
    if (state == "static" and activity) or (state == "active" and not activity):
        raise ValueError("decisions.scene.activity must match the selected state")
    lines.append("Scene state: " + state)
    lines += ["Scene activity: " + words(x, "decisions.scene.activity") for x in activity]
    candidates = record.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("decisions.candidates needs authored alternatives")
    indexed, lenses = {}, set()
    fields = ("lens", "cue", "basis", "proposal", "contribution", "scene_fit")
    for item in candidates:
        if not isinstance(item, dict) or set(item) - set(fields + ("id", "source_relations")):
            raise ValueError("each decisions candidate needs an id, source_relations, lens, cue, basis, proposal, contribution and scene_fit")
        key = words(item.get("id"), "candidate id")
        if key in indexed:
            raise ValueError("candidate IDs must be unique")
        candidate = {field: words(item.get(field), "candidate." + field) for field in fields}
        relations = item.get("source_relations")
        if (not isinstance(relations, list) or not relations
                or any(not isinstance(x, str) or x not in scene_relations for x in relations)
                or len(set(relations)) != len(relations)):
            raise ValueError(f"candidate {key}.source_relations needs unique source content relation names")
        candidate["source_relations"] = relations
        indexed[key] = candidate
        lenses.add(candidate["lens"].casefold())
    if scope == "open" and len(lenses) < 2:
        raise ValueError("open decisions need at least two distinct association lenses")
    selected = record.get("selected")
    if (not isinstance(selected, list) or not selected
            or any(not isinstance(x, str) or x not in indexed for x in selected)
            or len(set(selected)) != len(selected)):
        raise ValueError("decisions.selected must contain unique candidate IDs")
    words(record.get("selection_reason"), "decisions.selection_reason")
    for key in selected:
        item = indexed[key]
        outside = set(item["source_relations"]) - permitted[kind]
        if outside:
            raise ValueError(f"selected candidate {key} has source_relations outside content_scope {kind}: " + ", ".join(sorted(outside)))
        lines.append(f"Selected connection ({key}; {item['lens']}): Proposal: {item['proposal']} "
                     f"Visual contribution: {item['contribution']} Scene fit: {item['scene_fit']}")
    return lines, set(selected)


def material_lines(materials, input_ids):
    if isinstance(materials, str):
        return ["Materials: " + words(materials, "materials")]
    if not isinstance(materials, list) or not materials:
        raise ValueError("materials needs a description or a non-empty surface study")
    lines = []
    bases = {"observed": "source-observed appearance", "provided": "supplied specification", "designed": "authored concept"}
    for item in materials:
        if not isinstance(item, dict):
            raise ValueError("each material study must be an object")
        unknown = set(item) - {"sources", "part", "basis", "observation", "appearance", "light_response"}
        if unknown:
            raise ValueError("unknown material fields: " + ", ".join(sorted(unknown)))
        sources = item.get("sources")
        if not isinstance(sources, list) or any(not isinstance(x, str) or x not in input_ids for x in sources):
            raise ValueError("material sources must identify actual inputs")
        basis = item.get("basis")
        if basis not in bases:
            raise ValueError("material basis must be observed, provided or designed")
        part = words(item.get("part"), "material part")
        line = f"Material ({part}; {bases[basis]}; sources: {', '.join(sources) or 'text brief'}): "
        if basis == "observed":
            if not sources:
                raise ValueError("source-observed material needs material sources")
            line += "Observation: " + words(item.get("observation"), "material observation") + " "
        elif item.get("observation") is not None:
            line += "Evidence: " + words(item["observation"], "material observation") + " "
        line += "Appearance and certainty: " + words(item.get("appearance"), "material appearance")
        line += " Light response to preserve: " + words(item.get("light_response"), "material light_response")
        lines.append(line)
    return lines


def palette_lines(palette):
    if isinstance(palette, str):
        return ["Palette: " + words(palette, "palette")]
    fields = ("basis", "relationship", "application", "reflection_control")
    if not isinstance(palette, dict) or set(palette) - set(fields):
        raise ValueError("palette needs basis, relationship, application and reflection_control")
    return [f"Color {key.replace('_', ' ')}: " + words(palette.get(key), "palette." + key) for key in fields]


def photography_lines(settings):
    if not isinstance(settings, dict):
        raise ValueError("photography needs a profile or a complete custom setup")
    profiles = json.loads((Path(__file__).resolve().parents[1] / "assets/photography-profiles.json").read_text(encoding="utf-8"))
    profile = settings.get("profile")
    if profile is not None and (not isinstance(profile, str) or profile not in profiles):
        raise ValueError(f"unknown photography profile: {profile}")
    photo = {**(profiles[profile] if profile else {}), **settings}
    text_fields = ("camera_format", "shot_scale", "viewpoint", "lens", "lighting_setup",
                   "exposure_intent", "focus_and_depth", "support_and_motion", "visible_result")
    number_fields = ("focal_length_mm", "aperture_f", "iso", "shutter_seconds", "white_balance_k")
    unknown = set(photo) - set(text_fields + number_fields + ("profile", "lighting_mode", "flash_timing"))
    if unknown:
        raise ValueError("unknown photography settings: " + ", ".join(sorted(unknown)))
    for field in text_fields:
        photo[field] = words(photo.get(field), "photography." + field)
    for field in number_fields:
        value = photo.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"photography.{field} must be a finite positive number")
    if photo.get("lighting_mode") not in {"continuous", "flash", "mixed"}:
        raise ValueError("photography.lighting_mode must be continuous, flash or mixed")
    shutter = photo["shutter_seconds"]
    reciprocal = 1 / shutter
    time = f"1/{round(reciprocal)}" if shutter < 1 and math.isfinite(reciprocal) and math.isclose(reciprocal, round(reciprocal), rel_tol=1e-9) else f"{shutter:g}"
    lines = [
        "Photographic simulation: use these starting settings to express the visible optical intent; exposure is adjusted through the described lighting and highlight priorities.",
        f"Camera: {photo['camera_format']}",
        f"Framing: {photo['shot_scale']} Viewpoint and distance: {photo['viewpoint']}",
        f"Lens: {photo['lens']}; actual focal length {photo['focal_length_mm']:g} mm on the stated format.",
        f"Manual exposure: ISO {photo['iso']:g}, f/{photo['aperture_f']:g}, {time} s; white balance {photo['white_balance_k']:g} K.",
        f"Lighting ({photo['lighting_mode']}): {photo['lighting_setup']}",
        f"Exposure priority: {photo['exposure_intent']}",
        f"Focus and depth: {photo['focus_and_depth']}",
        f"Support and motion: {photo['support_and_motion']}",
        f"Visible photographic result: {photo['visible_result']}",
    ]
    if photo["lighting_mode"] in {"flash", "mixed"}:
        lines.append("Flash timing: " + words(photo.get("flash_timing"), "photography.flash_timing"))
    return lines


def build_job(plan, base):
    if not isinstance(plan, dict):
        raise ValueError("direction must be an object")
    operation = plan.get("operation")
    if operation not in {"recompose", "detail_edit", "concept"}:
        raise ValueError("operation must be recompose, detail_edit or concept")
    inputs = plan.get("inputs", [])
    if not isinstance(inputs, list):
        raise ValueError("inputs must be a list")
    ids, content_ids, target_ids, paths, source_lines = set(), set(), [], [], []
    for index, item in enumerate(inputs, 1):
        if not isinstance(item, dict):
            raise ValueError("each input must be an object")
        item_id = words(item.get("id"), "input id")
        if item_id in ids:
            raise ValueError("input IDs must be unique")
        ids.add(item_id)
        role = item.get("role")
        if role not in {"subject", "support", "reference", "edit_target"}:
            raise ValueError(f"unsupported input role: {role}")
        path = (base / words(item.get("path"), "input path")).resolve()
        if not path.is_file():
            raise ValueError(f"input file is missing: {path}")
        paths.append(str(path))
        line = f"Image {index} ({item_id}, {role}): {words(item.get('use'), 'input use')}"
        words(item.get("observation"), f"input observation ({item_id})")
        analysis = item.get("content_analysis")
        if role != "reference" or analysis is not None:
            fields = {"relationships", "target_scope", "basis"}
            if not isinstance(analysis, dict) or set(analysis) != fields:
                raise ValueError(f"input content_analysis ({item_id}) needs relationships, target_scope and basis")
            for key in fields:
                words(analysis[key], f"input content_analysis.{key} ({item_id})")
            line += " Target scope: " + analysis["target_scope"].strip()
        if role != "reference":
            content_ids.add(item_id)
            locks = item.get("preserve", [])
            if not isinstance(locks, list) or not locks:
                raise ValueError(f"preserve needs identity or content constraints: {item_id}")
            line += " Preserve: " + "; ".join(words(x, "preserve") for x in locks)
        if role == "edit_target":
            target_ids.append(item_id)
        source_lines.append(line)
    if operation == "recompose" and (target_ids or not content_ids):
        raise ValueError("recompose uses original content sources")
    if operation == "detail_edit" and len(target_ids) != 1:
        raise ValueError("detail_edit requires exactly one edit_target")
    decisions, selected = decision_lines(plan.get("decisions"), content_ids)
    design = plan.get("design")
    if not isinstance(design, dict):
        raise ValueError("design must contain authored decisions")
    unknown_design = set(design) - {"idea", "pairings", "composition", "palette", "materials"}
    if unknown_design:
        raise ValueError("unknown design fields; put photographic decisions in photography: " + ", ".join(sorted(unknown_design)))
    pairings = design.get("pairings")
    if not isinstance(pairings, list) or not pairings:
        raise ValueError("pairings need an object, surface or group relationship")
    pairing_lines, assigned, assigned_decisions = [], set(), set()
    for pairing in pairings:
        if not isinstance(pairing, dict):
            raise ValueError("pairing must be an object")
        sources = pairing.get("sources")
        if not isinstance(sources, list) or any(x not in content_ids for x in sources):
            raise ValueError("pairing source must identify supplied content")
        assigned.update(sources)
        choices = pairing.get("decisions")
        if (not isinstance(choices, list) or not choices
                or any(not isinstance(x, str) or x not in selected for x in choices)):
            raise ValueError("pairing decisions must identify selected candidates")
        assigned_decisions.update(choices)
        relation = words(pairing.get("relation"), "pairing relation")
        purpose = words(pairing.get("purpose"), "pairing purpose")
        pairing_lines.append(f"{relation} Visual purpose: {purpose}")
    if assigned != content_ids:
        raise ValueError("unassigned content: " + ", ".join(sorted(content_ids - assigned)))
    if assigned_decisions != selected:
        raise ValueError("unassigned decisions: " + ", ".join(sorted(selected - assigned_decisions)))
    targets = plan.get("review_targets")
    if not isinstance(targets, list) or not targets:
        raise ValueError("review_targets must identify visible outcomes")
    lines = ["Intent: " + words(plan.get("intent"), "intent"),
             "Content interpretation: each supplied image contributes its stated use, target scope and preservation "
             "features. Depict the listed entities and their defined boundaries. Models, drawings and material studies "
             "share that adopted content scope. Apply fabrication, support and photographic choices to those entities.",
             "Physical photograph: depict every subject, model, support, paper layer and prop as a tangible object "
             "photographed together in one coherent scene. Use plausible construction, material-specific edges "
             "and textures at the chosen scale, stable support, contact and occlusion, and shared lighting. "
             "Source objects follow their explicit preservation requirements. Designed figurines use the selected "
             "finished dimensions, artistic proportions, pose, colors and fabrication materials while retaining the listed recognition features. "
             "Their volumes, thickness, joins and surface details belong to that chosen physical model and making process; "
             "camera magnification determines how large the finished object appears in the image. "
             "Drawn or printed content belongs to its specified physical surface and follows that surface's shape, "
             "occlusion and transmitted light. Visible writing is limited to the requested scene content."]
    lines += source_lines
    lines += decisions
    lines += material_lines(design.get("materials"), ids)
    lines += ["Visual idea: " + words(design.get("idea"), "design idea")]
    lines += ["Relationships: " + " ".join(pairing_lines)]
    lines.append("Composition: " + words(design.get("composition"), "composition"))
    lines += palette_lines(design.get("palette"))
    lines += photography_lines(plan.get("photography"))
    lines.append("Visible outcomes: " + "; ".join(words(x, "review target") for x in targets))
    if operation == "detail_edit":
        lines.append("Edit scope: " + words(plan.get("edit_scope", "Follow the requested detail change and preserve the listed constraints."), "edit scope"))
    prompt = "\n".join(lines)
    job = {"prompt": prompt}
    if paths:
        job["referenced_image_paths"] = paths
    return job


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("direction", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        plan = json.loads(args.direction.read_text(encoding="utf-8"))
        job = build_job(plan, args.direction.resolve().parent)
        result = json.dumps(job, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(result)
        else:
            print(result, end="")
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
