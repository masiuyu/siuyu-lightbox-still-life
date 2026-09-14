#!/usr/bin/env python3
"""Validate a Codex visual-direction record and compile a stable description."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime
from math import gcd
from pathlib import Path
from typing import Any, Iterable

IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
HASH = re.compile(r"^sha256:[a-f0-9]{64}$")
PRIORITY_ORDER = {f"P{index}": index for index in range(5)}
EVIDENCE_STATUS = {"observed", "user-supplied", "inferred", "unknown"}
QUALITY_STATUS = {"pending", "pass", "warning", "fail"}
QUALITY_HARD_FAILURES = {
    "NESTED_BACKGROUND_RECTANGLE",
    "CORNER_THUMBNAIL_TEMPLATE",
    "FLOATING_ASSET_PLANES",
    "SINGLE_GENERIC_MATERIAL",
    "PALETTE_FRAGMENTATION",
    "NO_DOMINANT_MATERIAL_RELATION",
    "REFERENCE_SCOPE_LEAKAGE",
    "REPRESENTATION_AS_FLOATING_STICKER",
    "LIGHTBOX_SPATIAL_RELATIONSHIP_LOST",
    "UNJUSTIFIED_ELEMENT_DOMINANCE",
}
REFERENCE_INFLUENCE_SCOPES = (
    "layout",
    "palette",
    "lighting",
    "material",
    "texture",
    "typography",
    "motif",
)
REGION_EVIDENCE_STATUS = {
    "user-markup": "user-supplied",
    "user-coordinate": "user-supplied",
    "observed-negative-space": "observed",
    "inferred-option": "inferred",
    "unresolved": "unknown",
}

ROOT_KEYS = {
    "version",
    "projectId",
    "manifestHash",
    "sourceRequest",
    "deliverable",
    "canvas",
    "lightboxEnvironment",
    "approvedVisibleText",
    "assetLocks",
    "referenceInfluencePlan",
    "integrationPlan",
    "evidence",
    "designRationale",
    "visualSystem",
    "composition",
    "optimizationActions",
    "placementOpportunities",
    "qualityReview",
    "negativeConstraints",
    "unknowns",
}
DELIVERABLE_KEYS = {"kind", "description", "viewerAction", "viewingContext"}
CANVAS_KEYS = {"width", "height", "aspectRatio", "orientation"}
LIGHTBOX_ENVIRONMENT_KEYS = {
    "mode",
    "calibration",
    "camera",
    "emissiveSurface",
    "topFill",
    "falloff",
    "surface",
    "contactShadow",
    "materialResponses",
    "evidenceIds",
}
LIGHTBOX_CAMERA_KEYS = {"projection", "tiltDeg"}
LIGHTBOX_EMITTER_KEYS = {"state", "intensity", "temperatureKelvin"}
LIGHTBOX_FALLOFF_KEYS = {"model", "edge"}
LIGHTBOX_SURFACE_KEYS = {"material", "transmission", "roughness", "diffuserLayers"}
LIGHTBOX_CONTACT_SHADOW_KEYS = {"model", "opacityScale", "edgeFeather"}
LIGHTBOX_MATERIAL_RESPONSE_KEYS = {
    "metal",
    "paper",
    "tracingPaper",
    "film",
    "acrylicGlass",
    "sourcePreserved",
}
LIGHTBOX_RESPONSE_KEYS = {"opticalModel", "renderStrategy", "contactShadow"}
LIGHTBOX_MATERIAL_RESPONSES = {
    "metal": ("opaque_reflective", "native_material", "defined"),
    "paper": ("opaque_diffuse", "native_material", "soft"),
    "tracingPaper": ("translucent", "native_material", "soft"),
    "film": ("transmissive", "native_material", "minimal"),
    "acrylicGlass": ("refractive_highlight", "native_material", "minimal"),
    "sourcePreserved": ("source_preserved", "exact_2d_layer", "source_alpha"),
}
VISIBLE_TEXT_KEYS = {"content", "approvalEvidenceId"}
ASSET_LOCK_KEYS = {"mustUseExact", "canTransform", "referenceOnly", "excluded"}
REFERENCE_INFLUENCE_KEYS = {"assetId", "scope", "rule", "evidenceId"}
INTEGRATION_PLAN_KEYS = {
    "mode",
    "intentEvidenceId",
    "requiredVisibleAssetIds",
    "layoutFamily",
    "overflowPolicy",
    "minimumVisibleShortEdgePx",
    "assignments",
    "materialRelation",
    "layoutRouting",
}
INTEGRATION_ASSIGNMENT_KEYS = {"assetId", "hierarchy", "carrier", "evidenceId", "representation"}
REPRESENTATION_KEYS = {
    "kind",
    "form",
    "materialFamily",
    "renderStrategy",
    "lightBehavior",
    "transformationEvidenceId",
    "scaleEvidenceId",
    "scaleEvidenceStatus",
    "rationale",
}
REPRESENTATION_MATERIAL_FAMILIES = {
    "source_preserved",
    "metal",
    "paper",
    "photographic_paper",
    "film",
    "pigment",
    "acrylic",
    "glass",
    "ceramic",
    "stone",
    "wood",
    "textile",
    "leather",
    "polymer",
    "organic",
    "mixed",
    "unknown",
}
REPRESENTATION_RULES = {
    "physical_object": {
        "forms": {"isolated_object"},
        "carriers": {"cutout"},
        "renderStrategies": {"exact_source_layer"},
        "lightBehaviors": {"source_preserved"},
    },
    "source_photograph": {
        "forms": {"bounded_sheet"},
        "carriers": {"physical_photo"},
        "renderStrategies": {"exact_source_on_carrier"},
        "lightBehaviors": {"source_preserved", "opaque_diffuse", "unknown"},
    },
    "technical_drawing": {
        "forms": {"linework_overlay", "bounded_sheet"},
        "carriers": {"tracing_sheet", "contact_print"},
        "renderStrategies": {"authorized_source_derivation"},
        "lightBehaviors": {"translucent", "opaque_diffuse"},
    },
    "material_field": {
        "forms": {"surface_field"},
        "carriers": {"physical_photo", "contact_print", "film_sleeve", "tracing_sheet"},
        "renderStrategies": {"authorized_source_derivation"},
        "lightBehaviors": {"source_preserved", "opaque_diffuse", "translucent", "transmissive", "unknown"},
    },
    "contact_print": {
        "forms": {"bounded_sheet"},
        "carriers": {"contact_print"},
        "renderStrategies": {"exact_source_on_carrier"},
        "lightBehaviors": {"opaque_diffuse"},
    },
    "film_transparency": {
        "forms": {"bounded_sheet"},
        "carriers": {"film_sleeve"},
        "renderStrategies": {"exact_source_on_carrier"},
        "lightBehaviors": {"transmissive"},
    },
    "tracing_overlay": {
        "forms": {"linework_overlay"},
        "carriers": {"tracing_sheet"},
        "renderStrategies": {"authorized_source_derivation"},
        "lightBehaviors": {"translucent"},
    },
    "relief_impression": {
        "forms": {"relief_surface"},
        "carriers": {"physical_photo", "contact_print"},
        "renderStrategies": {"authorized_source_derivation"},
        "lightBehaviors": {"relief_raking"},
    },
    "exact_cutout": {
        "forms": {"isolated_object"},
        "carriers": {"cutout"},
        "renderStrategies": {"exact_source_layer"},
        "lightBehaviors": {"source_preserved"},
    },
}
DERIVED_REPRESENTATIONS = {
    "technical_drawing",
    "material_field",
    "tracing_overlay",
    "relief_impression",
}
CARRIER_LIGHT_BEHAVIORS = {
    "contact_print": {"opaque_diffuse"},
    "film_sleeve": {"transmissive"},
    "tracing_sheet": {"translucent"},
}
INTEGRATION_MATERIAL_KEYS = {"dominant", "supporting", "relationship"}
COMPOSITION_GRAMMAR_KEYS = {
    "rootAssetId",
    "flow",
    "readingOrder",
    "groups",
    "links",
    "negativeSpace",
}
COMPOSITION_GROUP_KEYS = {"groupId", "role", "arrangement", "assetIds", "purpose"}
COMPOSITION_LINK_KEYS = {
    "parentAssetId",
    "childAssetId",
    "axis",
    "contact",
    "spacing",
    "purpose",
}
COMPOSITION_NEGATIVE_SPACE_KEYS = {"mode", "anchorAssetId", "purpose"}
COMPOSITION_FLOWS = {
    "horizontal",
    "vertical",
    "diagonal_descending",
    "diagonal_ascending",
    "radial",
}
COMPOSITION_GROUP_ROLES = {
    "hero_event",
    "support_cluster",
    "evidence_band",
    "material_bridge",
}
COMPOSITION_GROUP_ARRANGEMENTS = {
    "singular",
    "paired",
    "linear",
    "staggered",
    "constellation",
}
COMPOSITION_LINK_AXES = {
    "right",
    "left",
    "below",
    "above",
    "diagonal_down",
    "diagonal_up",
}
COMPOSITION_LINK_CONTACTS = {"separated", "edge_touch", "shallow_overlap"}
COMPOSITION_LINK_SPACING = {"tight", "regular", "open"}
COMPOSITION_NEGATIVE_SPACE_MODES = {
    "single_breathing_field",
    "directional_channel",
    "perimeter_relief",
}
LAYOUT_ROUTING_KEYS = {"surfaceStyle", "selectionSignals", "styleRationale", "candidates"}
LAYOUT_CANDIDATE_KEYS = {
    "templateId",
    "archetype",
    "density",
    "alignment",
    "scaleRhythm",
    "rationale",
    "compositionGrammar",
}
LAYOUT_TEMPLATE_IDS = (
    "archive_research_v1",
    "product_focus_v1",
    "art_lab_v1",
)
LAYOUT_ARCHETYPE_COUNT_RANGES = {
    "singular_stage": (1, 3),
    "paired_dialogue": (2, 6),
    "asymmetric_constellation": (2, 16),
    "modular_inventory": (4, 20),
    "editorial_spine": (3, 40),
    "evidence_ribbon": (3, 40),
    "material_stage": (2, 16),
    "dense_taxonomy": (9, 40),
}
LAYOUT_SURFACE_STYLES = {
    "luminous_neutral",
    "graphite_precision",
    "warm_archive",
    "chromatic_acrylic",
    "monochrome_technical",
    "translucent_film",
}
LAYOUT_SELECTION_SIGNALS = {
    "asset_count",
    "aspect_mix",
    "alpha_mix",
    "role_mix",
    "representation_mix",
    "series_cohesion",
    "text_presence",
    "palette_evidence",
    "material_evidence",
    "user_direction",
}
LAYOUT_DENSITIES = {"airy", "balanced", "compact"}
LAYOUT_ALIGNMENTS = {"optical_axis", "edge_grid", "spine", "band", "radial"}
LAYOUT_SCALE_RHYTHMS = {"hero_dominant", "progressive", "modular"}
LAYOUT_ALIGNMENT_BY_ARCHETYPE = {
    "singular_stage": "optical_axis",
    "paired_dialogue": "optical_axis",
    "asymmetric_constellation": "radial",
    "modular_inventory": "edge_grid",
    "editorial_spine": "spine",
    "evidence_ribbon": "band",
    "material_stage": "optical_axis",
    "dense_taxonomy": "edge_grid",
}
EVIDENCE_KEYS = {"id", "claim", "status", "sourceAssetIds"}
RATIONALE_KEYS = {
    "subjectCause",
    "viewerEffect",
    "carrierReason",
    "dominantRelation",
    "rejectedAlternative",
}
VISUAL_SYSTEM_KEYS = {
    "camera",
    "hierarchy",
    "componentDetail",
    "textureScale",
    "materials",
    "lighting",
    "palette",
    "edgeAndShadow",
    "evidenceIds",
}
COMPOSITION_KEYS = {
    "heroAssetId",
    "focalPlacement",
    "readingPath",
    "occupiedMass",
    "negativeSpace",
    "density",
}
FOCAL_PLACEMENT_KEYS = {
    "region",
    "regionEvidence",
    "evidenceId",
    "confirmation",
    "relationship",
}
REGION_KEYS = {"x", "y", "width", "height"}
OPTIMIZATION_KEYS = {
    "id",
    "priority",
    "issue",
    "action",
    "subjectCause",
    "viewerEffect",
    "targetAssetIds",
    "evidenceIds",
    "constraints",
}
PLACEMENT_KEYS = {
    "id",
    "priority",
    "region",
    "regionEvidence",
    "evidenceId",
    "confirmation",
    "element",
    "purpose",
    "subjectCause",
    "viewerEffect",
    "removalImpact",
    "anchor",
    "scale",
    "material",
    "orientation",
    "confidence",
    "constraints",
}
ANCHOR_KEYS = {
    "targetAssetId",
    "relation",
    "minimumGapFraction",
    "maximumOverlapFraction",
    "contactMode",
}
SCALE_KEYS = {"basis", "minFraction", "maxFraction"}
ORIENTATION_KEYS = {"minDegrees", "maxDegrees"}
QUALITY_REVIEW_KEYS = {
    "reviewBasis",
    "sceneId",
    "sceneHash",
    "previewHash",
    "hardFailures",
    "items",
}
QUALITY_KEYS = {
    "visualUnity",
    "componentDetail",
    "textureScale",
    "naturalness",
    "restraint",
    "readingFlow",
    "physicalPlausibility",
}
QUALITY_ITEM_KEYS = {"status", "note"}
WORKFLOW_KEYS = {
    "version",
    "projectId",
    "phase",
    "approvedSceneId",
    "manifestApprovedAt",
    "sceneApprovedAt",
    "manifestApproval",
    "previewEvidence",
    "previewQualityReviews",
    "sceneApproval",
}
WORKFLOW_REQUIRED_KEYS = {
    "version",
    "projectId",
    "phase",
    "approvedSceneId",
    "manifestApprovedAt",
    "sceneApprovedAt",
    "manifestApproval",
}
MANIFEST_APPROVAL_KEYS = {
    "kind",
    "projectId",
    "manifestHash",
    "approvedAt",
    "approvedBy",
}


class DirectionError(ValueError):
    def __init__(self, message: str, code: str = "INVALID_VISUAL_DIRECTION") -> None:
        super().__init__(message)
        self.code = code


def reject_duplicate_keys(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DirectionError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def strict_object(value: Any, keys: set[str], path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DirectionError(f"{path} must be an object")
    actual = set(value)
    if actual != keys:
        missing = sorted(keys - actual)
        extra = sorted(actual - keys)
        details = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if extra:
            details.append(f"unknown {', '.join(extra)}")
        raise DirectionError(f"{path} has invalid fields: {'; '.join(details)}")
    return value


def closed_object(
    value: Any,
    allowed_keys: set[str],
    required_keys: set[str],
    path: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DirectionError(f"{path} must be an object")
    actual = set(value)
    missing = sorted(required_keys - actual)
    extra = sorted(actual - allowed_keys)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if extra:
            details.append(f"unknown {', '.join(extra)}")
        raise DirectionError(f"{path} has invalid fields: {'; '.join(details)}")
    return value


def nonempty_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise DirectionError(f"{path} must be a non-empty string without NUL")
    return value


def identifier(value: Any, path: str) -> str:
    text = nonempty_string(value, path)
    if IDENTIFIER.fullmatch(text) is None:
        raise DirectionError(f"{path} must be a portable identifier")
    return text


def nullable_identifier(value: Any, path: str) -> str | None:
    return None if value is None else identifier(value, path)


def hash_value(value: Any, path: str) -> str:
    text = nonempty_string(value, path)
    if HASH.fullmatch(text) is None:
        raise DirectionError(f"{path} must be sha256 followed by 64 lowercase hex characters")
    return text


def timestamp(value: Any, path: str) -> str:
    text = nonempty_string(value, path)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise DirectionError(f"{path} must be an ISO 8601 timestamp with offset") from error
    if parsed.tzinfo is None:
        raise DirectionError(f"{path} must include a timezone offset")
    return text


def nullable_hash(value: Any, path: str) -> str | None:
    return None if value is None else hash_value(value, path)


def string_list(value: Any, path: str, *, identifiers: bool = False) -> list[str]:
    if not isinstance(value, list):
        raise DirectionError(f"{path} must be an array")
    result = [
        identifier(item, f"{path}[{index}]")
        if identifiers
        else nonempty_string(item, f"{path}[{index}]")
        for index, item in enumerate(value)
    ]
    if len(set(result)) != len(result):
        raise DirectionError(f"{path} cannot contain duplicates")
    return result


def positive_integer(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0 or value > 100_000:
        raise DirectionError(f"{path} must be an integer between 1 and 100000")
    return value


def finite_number(value: Any, path: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise DirectionError(f"{path} must be a finite number")
    number = float(value)
    if number < minimum or number > maximum:
        raise DirectionError(f"{path} must be between {minimum} and {maximum}")
    return number


def region(value: Any, path: str) -> dict[str, float]:
    item = strict_object(value, REGION_KEYS, path)
    result = {
        key: finite_number(item[key], f"{path}.{key}", 0, 1)
        for key in ("x", "y", "width", "height")
    }
    if result["width"] <= 0 or result["height"] <= 0:
        raise DirectionError(f"{path} must have positive size")
    if result["x"] + result["width"] > 1 or result["y"] + result["height"] > 1:
        raise DirectionError(f"{path} must remain within normalized canvas bounds")
    return result


def stable_value(value: Any) -> Any:
    if isinstance(value, list):
        return [stable_value(item) for item in value]
    if not isinstance(value, dict):
        return value
    return {key: stable_value(value[key]) for key in sorted(value)}


def validate_manifest(value: Any) -> tuple[dict[str, Any], dict[str, dict[str, Any]], str]:
    manifest = strict_object(value, {"version", "projectId", "assets"}, "manifest")
    if manifest["version"] != 1:
        raise DirectionError("manifest.version must be 1")
    project_id = identifier(manifest["projectId"], "manifest.projectId")
    if not isinstance(manifest["assets"], list):
        raise DirectionError("manifest.assets must be an array")
    assets_by_id: dict[str, dict[str, Any]] = {}
    for index, asset in enumerate(manifest["assets"]):
        if not isinstance(asset, dict):
            raise DirectionError(f"manifest.assets[{index}] must be an object")
        asset_id = identifier(asset.get("assetId"), f"manifest.assets[{index}].assetId")
        usage = asset.get("usage")
        if usage not in {"must_use_exact", "can_transform", "reference_only", "ignore"}:
            raise DirectionError(f"manifest.assets[{index}].usage is invalid")
        if asset_id in assets_by_id:
            raise DirectionError(f"manifest contains duplicate asset ID: {asset_id}")
        has_alpha = asset.get("hasAlpha")
        if has_alpha is not None and not isinstance(has_alpha, bool):
            raise DirectionError(f"manifest.assets[{index}].hasAlpha must be boolean when present")
        has_scopes = "influenceScopes" in asset
        if usage == "reference_only":
            if not has_scopes:
                raise DirectionError(
                    f"manifest reference requires renewed influenceScopes review: {asset_id}"
                )
            influence_scopes = string_list(
                asset["influenceScopes"],
                f"manifest.assets[{index}].influenceScopes",
            )
            if any(scope not in REFERENCE_INFLUENCE_SCOPES for scope in influence_scopes):
                raise DirectionError(
                    f"manifest.assets[{index}].influenceScopes contains an unknown scope"
                )
        else:
            if has_scopes:
                raise DirectionError(
                    f"manifest.assets[{index}].influenceScopes requires reference_only usage"
                )
            influence_scopes = []
        assets_by_id[asset_id] = {
            "usage": usage,
            "hasAlpha": has_alpha is True,
            "category": asset.get("category"),
            "influenceScopes": sorted(influence_scopes),
        }
    exact_products = [
        asset_id
        for asset_id, asset in assets_by_id.items()
        if asset["usage"] == "must_use_exact" and asset["category"] == "product_core"
    ]
    if not exact_products:
        raise DirectionError("manifest requires an exact product content asset for production")
    normalized = dict(manifest)
    normalized["assets"] = []
    for asset in sorted(manifest["assets"], key=lambda item: item["assetId"]):
        normalized_asset = dict(asset)
        if asset.get("usage") == "reference_only" and "influenceScopes" in asset:
            normalized_asset["influenceScopes"] = sorted(asset["influenceScopes"])
        normalized["assets"].append(normalized_asset)
    canonical = json.dumps(stable_value(normalized), ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return manifest, assets_by_id, f"sha256:{digest}"


def validate_workflow(value: Any, project_id: str, manifest_hash: str) -> dict[str, Any]:
    workflow = closed_object(value, WORKFLOW_KEYS, WORKFLOW_REQUIRED_KEYS, "workflow")
    if workflow["version"] != 1:
        raise DirectionError("workflow.version must be 1")
    if identifier(workflow["projectId"], "workflow.projectId") != project_id:
        raise DirectionError("workflow projectId does not match manifest")
    if workflow["phase"] not in {
        "manifest_approved",
        "scenes_generated",
        "preview_ready",
        "scene_approved",
        "final_rendered",
    }:
        raise DirectionError("workflow phase does not carry a current manifest approval")
    approved_at = timestamp(workflow["manifestApprovedAt"], "workflow.manifestApprovedAt")
    approval = strict_object(
        workflow["manifestApproval"],
        MANIFEST_APPROVAL_KEYS,
        "workflow.manifestApproval",
    )
    if approval["kind"] != "asset_manifest":
        raise DirectionError("workflow manifest approval kind is invalid")
    if identifier(approval["projectId"], "workflow.manifestApproval.projectId") != project_id:
        raise DirectionError("workflow manifest approval project does not match manifest")
    if hash_value(approval["manifestHash"], "workflow.manifestApproval.manifestHash") != manifest_hash:
        raise DirectionError("workflow manifest approval hash does not match manifest")
    if timestamp(approval["approvedAt"], "workflow.manifestApproval.approvedAt") != approved_at:
        raise DirectionError("workflow manifest approval timestamp does not match summary")
    if approval["approvedBy"] != "human":
        raise DirectionError("workflow manifest approval must be approvedBy human")
    return workflow


def evidence_ids(value: Any, path: str, evidence: dict[str, dict[str, Any]]) -> list[str]:
    result = string_list(value, path, identifiers=True)
    missing = sorted(set(result) - set(evidence))
    if missing:
        raise DirectionError(f"{path} references unknown evidence: {', '.join(missing)}")
    return result


def validate_lightbox_environment(
    value: Any,
    evidence: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    environment = strict_object(value, LIGHTBOX_ENVIRONMENT_KEYS, "lightboxEnvironment")
    mode = environment["mode"]
    if mode not in {
        "diffused_softbox",
        "transmitted_light_table",
        "hybrid_diffused_table",
    }:
        raise DirectionError("lightboxEnvironment.mode is invalid")
    if environment["calibration"] != "visual_preset_not_physical_measurement":
        raise DirectionError("lightboxEnvironment.calibration is invalid")

    camera = strict_object(
        environment["camera"], LIGHTBOX_CAMERA_KEYS, "lightboxEnvironment.camera"
    )
    if camera["projection"] != "orthographic":
        raise DirectionError("lightboxEnvironment.camera.projection must be orthographic")
    finite_number(camera["tiltDeg"], "lightboxEnvironment.camera.tiltDeg", 0, 15)

    emitter_states: dict[str, bool] = {}
    for key in ("emissiveSurface", "topFill"):
        path = f"lightboxEnvironment.{key}"
        emitter = strict_object(environment[key], LIGHTBOX_EMITTER_KEYS, path)
        if emitter["state"] not in {"active", "inactive"}:
            raise DirectionError(f"{path}.state is invalid")
        intensity = finite_number(emitter["intensity"], f"{path}.intensity", 0, 1_000_000)
        finite_number(
            emitter["temperatureKelvin"], f"{path}.temperatureKelvin", 0.000001, 100_000
        )
        active = emitter["state"] == "active"
        if active != (intensity > 0):
            raise DirectionError(f"{path} state contradicts its intensity")
        emitter_states[key] = active

    valid_mode = (
        (mode == "diffused_softbox" and not emitter_states["emissiveSurface"] and emitter_states["topFill"])
        or (mode == "transmitted_light_table" and emitter_states["emissiveSurface"] and not emitter_states["topFill"])
        or (mode == "hybrid_diffused_table" and emitter_states["emissiveSurface"] and emitter_states["topFill"])
    )
    if not valid_mode:
        raise DirectionError("lightboxEnvironment mode contradicts its active emitter controls")

    falloff = strict_object(
        environment["falloff"], LIGHTBOX_FALLOFF_KEYS, "lightboxEnvironment.falloff"
    )
    if falloff["model"] != "radial":
        raise DirectionError("lightboxEnvironment.falloff.model must be radial")
    finite_number(falloff["edge"], "lightboxEnvironment.falloff.edge", 0, 1)

    surface = strict_object(
        environment["surface"], LIGHTBOX_SURFACE_KEYS, "lightboxEnvironment.surface"
    )
    if surface["material"] != "frosted_acrylic":
        raise DirectionError("lightboxEnvironment.surface.material is invalid")
    finite_number(surface["transmission"], "lightboxEnvironment.surface.transmission", 0, 1)
    finite_number(surface["roughness"], "lightboxEnvironment.surface.roughness", 0, 1)
    layers = surface["diffuserLayers"]
    if isinstance(layers, bool) or not isinstance(layers, int) or layers < 1 or layers > 20:
        raise DirectionError("lightboxEnvironment.surface.diffuserLayers must be an integer from 1 to 20")

    contact = strict_object(
        environment["contactShadow"],
        LIGHTBOX_CONTACT_SHADOW_KEYS,
        "lightboxEnvironment.contactShadow",
    )
    if contact["model"] != "material_specific":
        raise DirectionError("lightboxEnvironment.contactShadow.model is invalid")
    finite_number(contact["opacityScale"], "lightboxEnvironment.contactShadow.opacityScale", 0, 2)
    finite_number(contact["edgeFeather"], "lightboxEnvironment.contactShadow.edgeFeather", 0.000001, 0.5)

    responses = strict_object(
        environment["materialResponses"],
        LIGHTBOX_MATERIAL_RESPONSE_KEYS,
        "lightboxEnvironment.materialResponses",
    )
    for family, expected in LIGHTBOX_MATERIAL_RESPONSES.items():
        path = f"lightboxEnvironment.materialResponses.{family}"
        response = strict_object(responses[family], LIGHTBOX_RESPONSE_KEYS, path)
        actual = (
            response["opticalModel"],
            response["renderStrategy"],
            response["contactShadow"],
        )
        if actual != expected:
            raise DirectionError(f"{path} does not match the supported material response")

    supporting_evidence = evidence_ids(
        environment["evidenceIds"], "lightboxEnvironment.evidenceIds", evidence
    )
    if not supporting_evidence:
        raise DirectionError("lightboxEnvironment.evidenceIds cannot be empty")
    if any(evidence[item]["status"] == "unknown" for item in supporting_evidence):
        raise DirectionError("lightboxEnvironment cannot cite unknown evidence as a design fact")
    return environment


def asset_ids(value: Any, path: str, known_assets: set[str]) -> list[str]:
    result = string_list(value, path, identifiers=True)
    missing = sorted(set(result) - known_assets)
    if missing:
        raise DirectionError(f"{path} references unknown assets: {', '.join(missing)}")
    return result


def validate_region_evidence(
    item: dict[str, Any],
    path: str,
    evidence: dict[str, dict[str, Any]],
    *,
    allow_unresolved: bool,
) -> None:
    kind = item["regionEvidence"]
    if kind not in REGION_EVIDENCE_STATUS:
        raise DirectionError(f"{path}.regionEvidence is invalid")
    if not allow_unresolved and kind == "unresolved":
        raise DirectionError(f"{path}.regionEvidence cannot be unresolved for a placement opportunity")
    evidence_id = identifier(item["evidenceId"], f"{path}.evidenceId")
    record = evidence.get(evidence_id)
    if record is None:
        raise DirectionError(f"{path}.evidenceId references unknown evidence")
    expected_status = REGION_EVIDENCE_STATUS[kind]
    if record["status"] != expected_status:
        raise DirectionError(
            f"{path}.regionEvidence requires {expected_status} evidence, got {record['status']}"
        )


def validate_composition_grammar(
    value: Any,
    path: str,
    known_assets: set[str],
    required_assets: set[str],
    hero_id: str,
) -> dict[str, Any]:
    grammar = strict_object(value, COMPOSITION_GRAMMAR_KEYS, path)
    grammar_root = identifier(grammar["rootAssetId"], f"{path}.rootAssetId")
    if grammar_root != hero_id:
        raise DirectionError(f"{path} root must match the integration hero")
    if grammar["flow"] not in COMPOSITION_FLOWS:
        raise DirectionError(f"{path}.flow is invalid")
    reading_order = asset_ids(grammar["readingOrder"], f"{path}.readingOrder", known_assets)
    if not reading_order or len(reading_order) > 40:
        raise DirectionError(f"{path} requires between 1 and 40 reading-order assets")
    if reading_order[0] != grammar_root:
        raise DirectionError(f"{path} reading order must begin with the root asset")
    if set(reading_order) != required_assets:
        raise DirectionError(f"{path} must cover every required visible asset exactly once")
    reading_index = {asset_id: index for index, asset_id in enumerate(reading_order)}

    groups = grammar["groups"]
    if not isinstance(groups, list) or not groups or len(groups) > 40:
        raise DirectionError(f"{path}.groups must contain between 1 and 40 items")
    group_ids: set[str] = set()
    grouped_assets: set[str] = set()
    hero_groups: list[dict[str, Any]] = []
    for index, raw_group in enumerate(groups):
        group_path = f"{path}.groups[{index}]"
        group = strict_object(raw_group, COMPOSITION_GROUP_KEYS, group_path)
        group_id = identifier(group["groupId"], f"{group_path}.groupId")
        if group_id in group_ids:
            raise DirectionError(f"duplicate composition group ID: {group_id}")
        group_ids.add(group_id)
        if group["role"] not in COMPOSITION_GROUP_ROLES:
            raise DirectionError(f"{group_path}.role is invalid")
        if group["arrangement"] not in COMPOSITION_GROUP_ARRANGEMENTS:
            raise DirectionError(f"{group_path}.arrangement is invalid")
        members = asset_ids(group["assetIds"], f"{group_path}.assetIds", set(reading_order))
        if not members:
            raise DirectionError(f"{group_path}.assetIds cannot be empty")
        if grouped_assets.intersection(members):
            raise DirectionError("composition assets cannot belong to more than one group")
        grouped_assets.update(members)
        if group["arrangement"] == "singular" and len(members) != 1:
            raise DirectionError("a singular composition group must contain exactly one asset")
        if group["arrangement"] == "paired" and len(members) != 2:
            raise DirectionError("a paired composition group must contain exactly two assets")
        if group["arrangement"] not in {"singular", "paired"} and len(members) < 2:
            raise DirectionError(f"{group['arrangement']} composition groups require at least two assets")
        member_indexes = sorted(reading_index[asset_id] for asset_id in members)
        if len(member_indexes) > 1 and member_indexes[-1] - member_indexes[0] + 1 != len(member_indexes):
            raise DirectionError("composition group members must stay contiguous in the reading order")
        nonempty_string(group["purpose"], f"{group_path}.purpose")
        if group["role"] == "hero_event":
            hero_groups.append(group)
    if grouped_assets != set(reading_order):
        raise DirectionError("composition groups must partition the reading order exactly once")
    if (
        len(hero_groups) != 1
        or hero_groups[0]["arrangement"] != "singular"
        or hero_groups[0]["assetIds"] != [grammar_root]
    ):
        raise DirectionError(
            "composition grammar requires one singleton hero_event group containing the root asset"
        )

    links = grammar["links"]
    if not isinstance(links, list) or len(links) != max(0, len(reading_order) - 1):
        raise DirectionError("composition links must form one rooted tree over every non-root asset")
    child_ids: set[str] = set()
    link_pairs: set[tuple[str, str]] = set()
    for index, raw_link in enumerate(links):
        link_path = f"{path}.links[{index}]"
        link = strict_object(raw_link, COMPOSITION_LINK_KEYS, link_path)
        parent_id = identifier(link["parentAssetId"], f"{link_path}.parentAssetId")
        child_id = identifier(link["childAssetId"], f"{link_path}.childAssetId")
        if parent_id not in reading_index or child_id not in reading_index:
            raise DirectionError("composition links may reference only assets in the reading order")
        if parent_id == child_id:
            raise DirectionError("a composition link cannot point to itself")
        pair = (parent_id, child_id)
        if pair in link_pairs:
            raise DirectionError("composition links cannot duplicate a parent-child pair")
        link_pairs.add(pair)
        if child_id == grammar_root:
            raise DirectionError("the composition root cannot have an incoming link")
        if child_id in child_ids:
            raise DirectionError(f"composition asset has more than one incoming link: {child_id}")
        child_ids.add(child_id)
        if reading_index[parent_id] >= reading_index[child_id]:
            raise DirectionError("each composition link parent must precede its child in the reading order")
        if link["axis"] not in COMPOSITION_LINK_AXES:
            raise DirectionError(f"{link_path}.axis is invalid")
        if link["contact"] not in COMPOSITION_LINK_CONTACTS:
            raise DirectionError(f"{link_path}.contact is invalid")
        if link["spacing"] not in COMPOSITION_LINK_SPACING:
            raise DirectionError(f"{link_path}.spacing is invalid")
        if link["contact"] != "separated" and link["spacing"] != "tight":
            raise DirectionError(f"{link['contact']} composition links require tight spacing")
        if link["contact"] == "shallow_overlap" and grammar_root in {parent_id, child_id}:
            raise DirectionError("shallow overlap cannot involve the composition hero")
        nonempty_string(link["purpose"], f"{link_path}.purpose")
    disconnected = set(reading_order[1:]) - child_ids
    if disconnected:
        raise DirectionError(
            "composition assets are disconnected from the root: " + ", ".join(sorted(disconnected))
        )

    negative_space = strict_object(
        grammar["negativeSpace"],
        COMPOSITION_NEGATIVE_SPACE_KEYS,
        f"{path}.negativeSpace",
    )
    if negative_space["mode"] not in COMPOSITION_NEGATIVE_SPACE_MODES:
        raise DirectionError(f"{path}.negativeSpace.mode is invalid")
    negative_anchor = identifier(
        negative_space["anchorAssetId"],
        f"{path}.negativeSpace.anchorAssetId",
    )
    if negative_anchor not in reading_index:
        raise DirectionError("composition negative-space anchor must be in the reading order")
    nonempty_string(negative_space["purpose"], f"{path}.negativeSpace.purpose")
    return grammar


def validate(payload: Any, manifest_value: Any | None = None) -> dict[str, Any]:
    if isinstance(payload, dict) and (
        "lightboxEnvironment" not in payload or payload["lightboxEnvironment"] is None
    ):
        raise DirectionError(
            "lightboxEnvironment is required",
            code="LIGHTBOX_ENVIRONMENT_MISSING",
        )
    root = strict_object(payload, ROOT_KEYS, "root")
    if root["version"] != 6:
        raise DirectionError("version must be 6")
    project_id = identifier(root["projectId"], "projectId")
    manifest_hash = hash_value(root["manifestHash"], "manifestHash")
    nonempty_string(root["sourceRequest"], "sourceRequest")

    deliverable = strict_object(root["deliverable"], DELIVERABLE_KEYS, "deliverable")
    if deliverable["kind"] not in {"generation-description", "scene-preview"}:
        raise DirectionError("deliverable.kind is invalid")
    for key in ("description", "viewerAction", "viewingContext"):
        nonempty_string(deliverable[key], f"deliverable.{key}")

    canvas = strict_object(root["canvas"], CANVAS_KEYS, "canvas")
    width = positive_integer(canvas["width"], "canvas.width")
    height = positive_integer(canvas["height"], "canvas.height")
    expected_ratio = f"{width // gcd(width, height)}:{height // gcd(width, height)}"
    if nonempty_string(canvas["aspectRatio"], "canvas.aspectRatio") != expected_ratio:
        raise DirectionError(f"canvas.aspectRatio must be {expected_ratio}")
    expected_orientation = "square" if width == height else "portrait" if height > width else "landscape"
    if canvas["orientation"] != expected_orientation:
        raise DirectionError(f"canvas.orientation must be {expected_orientation}")

    locks = strict_object(root["assetLocks"], ASSET_LOCK_KEYS, "assetLocks")
    lock_groups = {
        key: string_list(locks[key], f"assetLocks.{key}", identifiers=True)
        for key in ("mustUseExact", "canTransform", "referenceOnly", "excluded")
    }
    seen_assets: set[str] = set()
    for assets in lock_groups.values():
        overlap = seen_assets.intersection(assets)
        if overlap:
            raise DirectionError(f"assetLocks assigns conflicting roles: {', '.join(sorted(overlap))}")
        seen_assets.update(assets)

    manifest_assets: dict[str, dict[str, Any]] | None = None
    if manifest_value is not None:
        _, manifest_assets, computed_hash = validate_manifest(manifest_value)
        if manifest_value["projectId"] != project_id:
            raise DirectionError("manifest projectId does not match visual direction")
        if computed_hash != manifest_hash:
            raise DirectionError("manifestHash does not match the supplied manifest")
        expected_locks = {
            "mustUseExact": sorted(asset_id for asset_id, item in manifest_assets.items() if item["usage"] == "must_use_exact"),
            "canTransform": sorted(asset_id for asset_id, item in manifest_assets.items() if item["usage"] == "can_transform"),
            "referenceOnly": sorted(asset_id for asset_id, item in manifest_assets.items() if item["usage"] == "reference_only"),
            "excluded": sorted(asset_id for asset_id, item in manifest_assets.items() if item["usage"] == "ignore"),
        }
        for key in ASSET_LOCK_KEYS:
            if sorted(lock_groups[key]) != expected_locks[key]:
                raise DirectionError(f"assetLocks.{key} does not match manifest usage")

    if not isinstance(root["evidence"], list) or not root["evidence"]:
        raise DirectionError("evidence must be a non-empty array")
    evidence: dict[str, dict[str, Any]] = {}
    unknown_claims: list[str] = []
    for index, raw_evidence in enumerate(root["evidence"]):
        item = strict_object(raw_evidence, EVIDENCE_KEYS, f"evidence[{index}]")
        evidence_id = identifier(item["id"], f"evidence[{index}].id")
        if evidence_id in evidence:
            raise DirectionError(f"duplicate evidence ID: {evidence_id}")
        claim = nonempty_string(item["claim"], f"evidence[{index}].claim")
        if item["status"] not in EVIDENCE_STATUS:
            raise DirectionError(f"evidence[{index}].status is invalid")
        asset_ids(item["sourceAssetIds"], f"evidence[{index}].sourceAssetIds", seen_assets)
        evidence[evidence_id] = item
        if item["status"] == "unknown":
            unknown_claims.append(claim)

    validate_lightbox_environment(root["lightboxEnvironment"], evidence)

    reference_plan = root["referenceInfluencePlan"]
    if not isinstance(reference_plan, list):
        raise DirectionError(
            "referenceInfluencePlan must be an array",
            code="REFERENCE_SCOPE_VIOLATION",
        )
    reference_pairs: set[tuple[str, str]] = set()
    for index, raw_influence in enumerate(reference_plan):
        path = f"referenceInfluencePlan[{index}]"
        influence = strict_object(raw_influence, REFERENCE_INFLUENCE_KEYS, path)
        asset_id = identifier(influence["assetId"], f"{path}.assetId")
        if asset_id not in lock_groups["referenceOnly"]:
            raise DirectionError(
                "Reference influence requires a reference-only asset",
                code="REFERENCE_SCOPE_VIOLATION",
            )
        scope = nonempty_string(influence["scope"], f"{path}.scope")
        if scope not in REFERENCE_INFLUENCE_SCOPES:
            raise DirectionError(
                "Reference influence scope is invalid",
                code="REFERENCE_SCOPE_VIOLATION",
            )
        pair = (asset_id, scope)
        if pair in reference_pairs:
            raise DirectionError(
                "Reference influence plan cannot duplicate an asset and scope",
                code="REFERENCE_SCOPE_VIOLATION",
            )
        reference_pairs.add(pair)
        nonempty_string(influence["rule"], f"{path}.rule")
        evidence_id = identifier(influence["evidenceId"], f"{path}.evidenceId")
        evidence_item = evidence.get(evidence_id)
        if (
            evidence_item is None
            or evidence_item["status"] not in {"observed", "user-supplied"}
            or asset_id not in evidence_item["sourceAssetIds"]
        ):
            raise DirectionError(
                "Reference influence requires observed or user-supplied evidence from that reference",
                code="REFERENCE_SCOPE_VIOLATION",
            )
        if manifest_assets is not None:
            approved_scopes = manifest_assets.get(asset_id, {}).get("influenceScopes", [])
            if scope not in approved_scopes:
                raise DirectionError(
                    "Reference influence scope is not approved by the manifest",
                    code="REFERENCE_SCOPE_VIOLATION",
                )

    visible_text = root["approvedVisibleText"]
    if not isinstance(visible_text, list):
        raise DirectionError("approvedVisibleText must be an array")
    visible_strings: set[str] = set()
    for index, raw_text in enumerate(visible_text):
        item = strict_object(raw_text, VISIBLE_TEXT_KEYS, f"approvedVisibleText[{index}]")
        content = nonempty_string(item["content"], f"approvedVisibleText[{index}].content")
        if content in visible_strings:
            raise DirectionError("approvedVisibleText cannot contain duplicate content")
        visible_strings.add(content)
        approval_id = identifier(
            item["approvalEvidenceId"], f"approvedVisibleText[{index}].approvalEvidenceId"
        )
        approval = evidence.get(approval_id)
        if approval is None or approval["status"] != "user-supplied":
            raise DirectionError("visible text requires user-supplied approval evidence")
        if content not in approval["claim"]:
            raise DirectionError("visible text approval evidence must contain the exact approved string")

    rationale = strict_object(root["designRationale"], RATIONALE_KEYS, "designRationale")
    for key in RATIONALE_KEYS:
        nonempty_string(rationale[key], f"designRationale.{key}")

    visual = strict_object(root["visualSystem"], VISUAL_SYSTEM_KEYS, "visualSystem")
    for key in VISUAL_SYSTEM_KEYS - {"evidenceIds"}:
        nonempty_string(visual[key], f"visualSystem.{key}")
    visual_evidence = evidence_ids(visual["evidenceIds"], "visualSystem.evidenceIds", evidence)
    if not visual_evidence:
        raise DirectionError("visualSystem.evidenceIds cannot be empty")
    if any(evidence[item]["status"] == "unknown" for item in visual_evidence):
        raise DirectionError("visualSystem cannot cite unknown evidence as a design fact")

    composition = strict_object(root["composition"], COMPOSITION_KEYS, "composition")
    hero_id = identifier(composition["heroAssetId"], "composition.heroAssetId")
    if hero_id not in set(lock_groups["mustUseExact"] + lock_groups["canTransform"]):
        raise DirectionError("composition.heroAssetId must be an exact or transformable asset")
    if manifest_assets is not None:
        hero_asset = manifest_assets.get(hero_id)
        if hero_asset is None or hero_asset["usage"] != "must_use_exact" or hero_asset["category"] != "product_core":
            raise DirectionError("production requires an exact product content asset")
    focal = strict_object(composition["focalPlacement"], FOCAL_PLACEMENT_KEYS, "composition.focalPlacement")
    validate_region_evidence(focal, "composition.focalPlacement", evidence, allow_unresolved=True)
    if focal["regionEvidence"] == "unresolved":
        if focal["region"] is not None or focal["confirmation"] != "unresolved":
            raise DirectionError("unresolved focal placement cannot contain coordinates or confirmation")
    else:
        region(focal["region"], "composition.focalPlacement.region")
        allowed_confirmation = (
            {"candidate", "confirmed"}
            if focal["regionEvidence"] in {"user-markup", "user-coordinate"}
            else {"candidate"}
        )
        if focal["confirmation"] not in allowed_confirmation:
            raise DirectionError("focal placement confirmation conflicts with region evidence")
    nonempty_string(focal["relationship"], "composition.focalPlacement.relationship")
    for key in ("readingPath", "occupiedMass", "negativeSpace"):
        nonempty_string(composition[key], f"composition.{key}")
    if composition["density"] not in {"restrained", "balanced", "dense"}:
        raise DirectionError("composition.density is invalid")

    integration = strict_object(root["integrationPlan"], INTEGRATION_PLAN_KEYS, "integrationPlan")
    if integration["mode"] not in {"merge_all", "curated"}:
        raise DirectionError("integrationPlan.mode is invalid")
    intent_evidence_id = identifier(integration["intentEvidenceId"], "integrationPlan.intentEvidenceId")
    intent_evidence = evidence.get(intent_evidence_id)
    if intent_evidence is None or intent_evidence["status"] != "user-supplied":
        raise DirectionError("integrationPlan intent requires user-supplied evidence")
    required_visible = asset_ids(
        integration["requiredVisibleAssetIds"],
        "integrationPlan.requiredVisibleAssetIds",
        seen_assets,
    )
    if not required_visible or len(required_visible) > 40:
        raise DirectionError("integrationPlan requires between 1 and 40 visible assets")
    visible_assets = set(lock_groups["mustUseExact"] + lock_groups["canTransform"])
    required_set = set(required_visible)
    if integration["mode"] == "merge_all" and required_set != visible_assets:
        raise DirectionError("merge-all required visible assets must equal every approved content asset")
    if integration["mode"] == "curated" and not set(lock_groups["mustUseExact"]).issubset(required_set):
        raise DirectionError("curated integration cannot omit a must-use-exact asset")
    if not required_set.issubset(set(intent_evidence["sourceAssetIds"])):
        raise DirectionError("integrationPlan intent evidence must identify every required visible asset")
    expected_layout = (
        "relational_field"
        if len(required_visible) == 1
        else "asymmetric_cluster"
        if len(required_visible) <= 6
        else "editorial_taxonomy"
        if len(required_visible) <= 16
        else "expanded_taxonomy"
    )
    if integration["layoutFamily"] != expected_layout:
        raise DirectionError(f"integrationPlan.layoutFamily must be {expected_layout} for this asset count")
    if integration["overflowPolicy"] != "adapt_or_block":
        raise DirectionError("integrationPlan.overflowPolicy must be adapt_or_block")
    minimum_short_edge = integration["minimumVisibleShortEdgePx"]
    if (
        isinstance(minimum_short_edge, bool)
        or not isinstance(minimum_short_edge, int)
        or minimum_short_edge < 48
        or minimum_short_edge > 2000
    ):
        raise DirectionError("integrationPlan.minimumVisibleShortEdgePx must be an integer from 48 to 2000")
    assignments = integration["assignments"]
    if not isinstance(assignments, list):
        raise DirectionError("integrationPlan.assignments must be an array")
    assignment_ids: set[str] = set()
    hero_assignments: list[str] = []
    for index, raw_assignment in enumerate(assignments):
        path = f"integrationPlan.assignments[{index}]"
        assignment = strict_object(raw_assignment, INTEGRATION_ASSIGNMENT_KEYS, path)
        asset_id = identifier(assignment["assetId"], f"{path}.assetId")
        if asset_id in assignment_ids:
            raise DirectionError("integrationPlan assignments cannot contain duplicate assets")
        assignment_ids.add(asset_id)
        if assignment["hierarchy"] not in {"hero", "secondary", "supporting"}:
            raise DirectionError(f"{path}.hierarchy is invalid")
        if assignment["hierarchy"] == "hero":
            hero_assignments.append(asset_id)
        if assignment["carrier"] not in {
            "cutout",
            "physical_photo",
            "contact_print",
            "film_sleeve",
            "tracing_sheet",
        }:
            raise DirectionError(f"{path}.carrier is invalid")
        assignment_evidence_id = identifier(assignment["evidenceId"], f"{path}.evidenceId")
        assignment_evidence = evidence.get(assignment_evidence_id)
        if (
            assignment_evidence is None
            or assignment_evidence["status"] == "unknown"
            or asset_id not in assignment_evidence["sourceAssetIds"]
        ):
            raise DirectionError(f"{path} requires non-unknown evidence for its asset")
        if (
            manifest_assets is not None
            and assignment["carrier"] == "cutout"
            and manifest_assets.get(asset_id, {}).get("hasAlpha") is not True
        ):
            raise DirectionError(
                f"opaque asset cannot use a cutout carrier: {asset_id}",
                code="MATERIAL_FORM_MISMATCH",
            )
        representation = strict_object(
            assignment["representation"], REPRESENTATION_KEYS, f"{path}.representation"
        )
        representation_kind = representation["kind"]
        rules = REPRESENTATION_RULES.get(representation_kind)
        if rules is None:
            raise DirectionError(
                f"{path}.representation.kind is invalid",
                code="REPRESENTATION_UNSUPPORTED",
            )
        if representation["form"] not in rules["forms"]:
            raise DirectionError(
                f"{path}.representation.form is incompatible with {representation_kind}",
                code="MATERIAL_FORM_MISMATCH",
            )
        if assignment["carrier"] not in rules["carriers"]:
            raise DirectionError(
                f"{path}.carrier is incompatible with {representation_kind}",
                code="MATERIAL_FORM_MISMATCH",
            )
        if representation["materialFamily"] not in REPRESENTATION_MATERIAL_FAMILIES:
            raise DirectionError(
                f"{path}.representation.materialFamily is invalid",
                code="MATERIAL_FORM_MISMATCH",
            )
        if representation["renderStrategy"] not in rules["renderStrategies"]:
            raise DirectionError(
                f"{path}.representation.renderStrategy is incompatible with {representation_kind}",
                code="MATERIAL_FORM_MISMATCH",
            )
        if representation["lightBehavior"] not in rules["lightBehaviors"]:
            raise DirectionError(
                f"{path}.representation.lightBehavior is incompatible with {representation_kind}",
                code="MATERIAL_FORM_MISMATCH",
            )
        carrier_light_behaviors = CARRIER_LIGHT_BEHAVIORS.get(assignment["carrier"])
        if (
            carrier_light_behaviors is not None
            and representation_kind != "relief_impression"
            and representation["lightBehavior"] not in carrier_light_behaviors
        ):
            raise DirectionError(
                f"{path}.representation.lightBehavior is incompatible with {assignment['carrier']}",
                code="MATERIAL_FORM_MISMATCH",
            )
        nonempty_string(representation["rationale"], f"{path}.representation.rationale")

        transformation_evidence_id = identifier(
            representation["transformationEvidenceId"],
            f"{path}.representation.transformationEvidenceId",
        )
        transformation_evidence = evidence.get(transformation_evidence_id)
        if (
            transformation_evidence is None
            or transformation_evidence["status"] == "unknown"
            or asset_id not in transformation_evidence["sourceAssetIds"]
        ):
            raise DirectionError(f"{path}.representation requires transformation evidence for its asset")
        if (
            representation_kind in DERIVED_REPRESENTATIONS
            and transformation_evidence["status"] != "user-supplied"
        ):
            raise DirectionError(f"{path}.representation requires user-supplied transformation evidence")

        scale_evidence_id = identifier(
            representation["scaleEvidenceId"], f"{path}.representation.scaleEvidenceId"
        )
        scale_evidence = evidence.get(scale_evidence_id)
        scale_status = representation["scaleEvidenceStatus"]
        if scale_status not in {"observed", "user-supplied", "unknown"}:
            raise DirectionError(f"{path}.representation.scaleEvidenceStatus is invalid")
        if (
            scale_evidence is None
            or scale_evidence["status"] != scale_status
            or asset_id not in scale_evidence["sourceAssetIds"]
        ):
            raise DirectionError(f"{path}.representation requires matching scale evidence for its asset")

        if manifest_assets is not None:
            asset = manifest_assets[asset_id]
            if (
                asset["usage"] == "must_use_exact"
                and asset["category"] in {"product_core", "branding_asset"}
                and representation_kind not in {"exact_cutout", "source_photograph"}
            ):
                raise DirectionError(
                    f"exact product or branding asset cannot use a derived representation: {asset_id}",
                    code="REPRESENTATION_UNSUPPORTED",
                )
            if (
                asset.get("hasAlpha") is not True
                and representation_kind in {"exact_cutout", "physical_object"}
            ):
                raise DirectionError(
                    f"opaque asset cannot use an isolated representation: {asset_id}",
                    code="MATERIAL_FORM_MISMATCH",
                )
            if representation_kind in DERIVED_REPRESENTATIONS and asset["usage"] != "can_transform":
                raise DirectionError(
                    f"derived representation requires a can_transform source: {asset_id}",
                    code="REPRESENTATION_UNSUPPORTED",
                )
    if assignment_ids != required_set:
        raise DirectionError("integrationPlan assignments must cover every required visible asset exactly once")
    if hero_assignments != [hero_id]:
        raise DirectionError("integrationPlan must contain exactly one hero matching composition.heroAssetId")
    if (
        manifest_assets is not None
        and manifest_assets.get(hero_id, {}).get("hasAlpha") is not True
        and next(item for item in assignments if item["assetId"] == hero_id)["carrier"] != "physical_photo"
    ):
        raise DirectionError("opaque hero must use the physical_photo carrier")
    material_relation = strict_object(
        integration["materialRelation"], INTEGRATION_MATERIAL_KEYS, "integrationPlan.materialRelation"
    )
    nonempty_string(material_relation["dominant"], "integrationPlan.materialRelation.dominant")
    supporting_materials = string_list(
        material_relation["supporting"], "integrationPlan.materialRelation.supporting"
    )
    if not supporting_materials:
        raise DirectionError("integrationPlan.materialRelation.supporting cannot be empty")
    nonempty_string(material_relation["relationship"], "integrationPlan.materialRelation.relationship")

    routing = strict_object(
        integration["layoutRouting"],
        LAYOUT_ROUTING_KEYS,
        "integrationPlan.layoutRouting",
    )
    if routing["surfaceStyle"] not in LAYOUT_SURFACE_STYLES:
        raise DirectionError("integrationPlan.layoutRouting.surfaceStyle is invalid")
    selection_signals = string_list(
        routing["selectionSignals"],
        "integrationPlan.layoutRouting.selectionSignals",
    )
    if not selection_signals or len(selection_signals) > 10:
        raise DirectionError("layout routing requires between 1 and 10 selection signals")
    if not set(selection_signals).issubset(LAYOUT_SELECTION_SIGNALS):
        raise DirectionError("integrationPlan.layoutRouting.selectionSignals contains an invalid signal")
    nonempty_string(routing["styleRationale"], "integrationPlan.layoutRouting.styleRationale")

    candidates = routing["candidates"]
    if not isinstance(candidates, list) or len(candidates) != 3:
        raise DirectionError("layout routing requires exactly three candidates")
    template_ids: list[str] = []
    route_signatures: set[tuple[str, str, str, str]] = set()
    for index, raw_candidate in enumerate(candidates):
        candidate_path = f"integrationPlan.layoutRouting.candidates[{index}]"
        candidate = strict_object(raw_candidate, LAYOUT_CANDIDATE_KEYS, candidate_path)
        template_id = identifier(candidate["templateId"], f"{candidate_path}.templateId")
        if template_id not in LAYOUT_TEMPLATE_IDS:
            raise DirectionError(f"{candidate_path}.templateId is invalid")
        template_ids.append(template_id)
        archetype = candidate["archetype"]
        count_range = LAYOUT_ARCHETYPE_COUNT_RANGES.get(archetype)
        if count_range is None:
            raise DirectionError(f"{candidate_path}.archetype is invalid")
        if not count_range[0] <= len(required_visible) <= count_range[1]:
            raise DirectionError(
                f"{archetype} is incompatible with {len(required_visible)} visible assets"
            )
        if candidate["density"] not in LAYOUT_DENSITIES:
            raise DirectionError(f"{candidate_path}.density is invalid")
        if candidate["alignment"] not in LAYOUT_ALIGNMENTS:
            raise DirectionError(f"{candidate_path}.alignment is invalid")
        required_alignment = LAYOUT_ALIGNMENT_BY_ARCHETYPE[archetype]
        if candidate["alignment"] != required_alignment:
            raise DirectionError(f"{archetype} requires {required_alignment} alignment")
        if candidate["scaleRhythm"] not in LAYOUT_SCALE_RHYTHMS:
            raise DirectionError(f"{candidate_path}.scaleRhythm is invalid")
        nonempty_string(candidate["rationale"], f"{candidate_path}.rationale")
        signature = (
            archetype,
            candidate["density"],
            candidate["alignment"],
            candidate["scaleRhythm"],
        )
        if signature in route_signatures:
            raise DirectionError("layout candidates must use three distinct route signatures")
        route_signatures.add(signature)

        grammar = validate_composition_grammar(
            candidate["compositionGrammar"],
            f"{candidate_path}.compositionGrammar",
            seen_assets,
            required_set,
            hero_id,
        )
        if archetype == "editorial_spine" and grammar["flow"] != "vertical":
            raise DirectionError("editorial_spine requires a vertical composition flow")
        if archetype in {"modular_inventory", "evidence_ribbon"} and grammar["flow"] != "horizontal":
            raise DirectionError(f"{archetype} requires a horizontal composition flow")
        if archetype == "asymmetric_constellation" and grammar["flow"] != "radial":
            raise DirectionError("asymmetric_constellation requires a radial composition flow")
        group_roles = [group["role"] for group in grammar["groups"]]
        if archetype == "evidence_ribbon" and "evidence_band" not in group_roles:
            raise DirectionError("evidence_ribbon requires an evidence_band group")
        if archetype == "material_stage" and "material_bridge" not in group_roles:
            raise DirectionError("material_stage requires a material_bridge group")
        if archetype in {"modular_inventory", "dense_taxonomy"} and not any(
            group["role"] != "hero_event" and group["arrangement"] != "singular"
            for group in grammar["groups"]
        ):
            raise DirectionError(f"{archetype} requires an authored multi-asset group")
    if len(set(template_ids)) != 3 or set(template_ids) != set(LAYOUT_TEMPLATE_IDS):
        raise DirectionError("layout routing must contain each supported template exactly once")

    actions = root["optimizationActions"]
    if not isinstance(actions, list):
        raise DirectionError("optimizationActions must be an array")
    action_ids: set[str] = set()
    for index, raw_action in enumerate(actions):
        item = strict_object(raw_action, OPTIMIZATION_KEYS, f"optimizationActions[{index}]")
        action_id = identifier(item["id"], f"optimizationActions[{index}].id")
        if action_id in action_ids:
            raise DirectionError(f"duplicate optimization action ID: {action_id}")
        action_ids.add(action_id)
        if item["priority"] not in PRIORITY_ORDER:
            raise DirectionError(f"optimizationActions[{index}].priority is invalid")
        for key in ("issue", "action", "subjectCause", "viewerEffect"):
            nonempty_string(item[key], f"optimizationActions[{index}].{key}")
        asset_ids(item["targetAssetIds"], f"optimizationActions[{index}].targetAssetIds", seen_assets)
        evidence_ids(item["evidenceIds"], f"optimizationActions[{index}].evidenceIds", evidence)
        if not string_list(item["constraints"], f"optimizationActions[{index}].constraints"):
            raise DirectionError(f"optimizationActions[{index}].constraints cannot be empty")

    opportunities = root["placementOpportunities"]
    if not isinstance(opportunities, list):
        raise DirectionError("placementOpportunities must be an array")
    opportunity_ids: set[str] = set()
    visible_assets = set(lock_groups["mustUseExact"] + lock_groups["canTransform"])
    for index, raw_opportunity in enumerate(opportunities):
        path = f"placementOpportunities[{index}]"
        item = strict_object(raw_opportunity, PLACEMENT_KEYS, path)
        opportunity_id = identifier(item["id"], f"{path}.id")
        if opportunity_id in opportunity_ids:
            raise DirectionError(f"duplicate placement ID: {opportunity_id}")
        opportunity_ids.add(opportunity_id)
        if item["priority"] not in {"P3", "P4"}:
            raise DirectionError(f"{path}.priority must be P3 or P4; use optimizationActions for P0-P2")
        region(item["region"], f"{path}.region")
        validate_region_evidence(item, path, evidence, allow_unresolved=False)
        if item["confirmation"] not in {"candidate", "confirmed"}:
            raise DirectionError(f"{path}.confirmation is invalid")
        if item["regionEvidence"] in {"observed-negative-space", "inferred-option"} and item["confirmation"] != "candidate":
            raise DirectionError(f"{path} cannot mark an observed or inferred region confirmed")
        if item["confirmation"] == "confirmed":
            placement_evidence = evidence[identifier(item["evidenceId"], f"{path}.evidenceId")]
            source_asset_ids = placement_evidence["sourceAssetIds"]
            source_asset = (
                manifest_assets.get(source_asset_ids[0])
                if manifest_assets is not None and len(source_asset_ids) == 1
                else None
            )
            if (
                len(source_asset_ids) != 1
                or source_asset is None
                or source_asset["usage"] != "can_transform"
                or source_asset["category"] != "supporting_prop"
                or source_asset.get("hasAlpha") is not True
            ):
                raise DirectionError(
                    f"{path} lacks one approved transparent supporting source",
                    code="UNJUSTIFIED_GENERATED_ELEMENT",
                )
        for key in ("element", "purpose", "subjectCause", "viewerEffect", "removalImpact", "material"):
            nonempty_string(item[key], f"{path}.{key}")

        anchor = strict_object(item["anchor"], ANCHOR_KEYS, f"{path}.anchor")
        target_id = nullable_identifier(anchor["targetAssetId"], f"{path}.anchor.targetAssetId")
        if target_id is not None and target_id not in visible_assets:
            raise DirectionError(f"{path}.anchor.targetAssetId must reference a visible asset")
        if anchor["relation"] not in {
            "canvas-region",
            "left-of",
            "right-of",
            "above",
            "below",
            "overlapping-edge",
            "inside-sleeve",
            "attached-to",
        }:
            raise DirectionError(f"{path}.anchor.relation is invalid")
        gap = finite_number(anchor["minimumGapFraction"], f"{path}.anchor.minimumGapFraction", 0, 1)
        overlap = finite_number(anchor["maximumOverlapFraction"], f"{path}.anchor.maximumOverlapFraction", 0, 1)
        if anchor["contactMode"] not in {"separated", "resting", "overlapping", "attached", "sleeved"}:
            raise DirectionError(f"{path}.anchor.contactMode is invalid")
        if anchor["contactMode"] == "separated" and overlap != 0:
            raise DirectionError(f"{path} separated contact cannot allow overlap")
        if anchor["contactMode"] != "separated" and gap > 0:
            raise DirectionError(f"{path} contact cannot require a positive gap")

        scale = strict_object(item["scale"], SCALE_KEYS, f"{path}.scale")
        if scale["basis"] not in {"canvas-short-edge", "hero-width", "hero-height"}:
            raise DirectionError(f"{path}.scale.basis is invalid")
        minimum_scale = finite_number(scale["minFraction"], f"{path}.scale.minFraction", 0.001, 1)
        maximum_scale = finite_number(scale["maxFraction"], f"{path}.scale.maxFraction", 0.001, 1)
        if minimum_scale > maximum_scale:
            raise DirectionError(f"{path}.scale minimum cannot exceed maximum")

        orientation = strict_object(item["orientation"], ORIENTATION_KEYS, f"{path}.orientation")
        minimum_angle = finite_number(orientation["minDegrees"], f"{path}.orientation.minDegrees", -360, 360)
        maximum_angle = finite_number(orientation["maxDegrees"], f"{path}.orientation.maxDegrees", -360, 360)
        if minimum_angle > maximum_angle:
            raise DirectionError(f"{path}.orientation minimum cannot exceed maximum")
        if item["confidence"] not in {"high", "medium", "low"}:
            raise DirectionError(f"{path}.confidence is invalid")
        if not string_list(item["constraints"], f"{path}.constraints"):
            raise DirectionError(f"{path}.constraints cannot be empty")

    review = strict_object(root["qualityReview"], QUALITY_REVIEW_KEYS, "qualityReview")
    if review["reviewBasis"] not in {"direction-plan", "preview-pixels"}:
        raise DirectionError("qualityReview.reviewBasis is invalid")
    items = strict_object(review["items"], QUALITY_KEYS, "qualityReview.items")
    statuses: list[str] = []
    for key in QUALITY_KEYS:
        item = strict_object(items[key], QUALITY_ITEM_KEYS, f"qualityReview.items.{key}")
        if item["status"] not in QUALITY_STATUS:
            raise DirectionError(f"qualityReview.items.{key}.status is invalid")
        statuses.append(item["status"])
        nonempty_string(item["note"], f"qualityReview.items.{key}.note")
    scene_id = nullable_identifier(review["sceneId"], "qualityReview.sceneId")
    scene_hash = nullable_hash(review["sceneHash"], "qualityReview.sceneHash")
    preview_hash = nullable_hash(review["previewHash"], "qualityReview.previewHash")
    hard_failures = string_list(review["hardFailures"], "qualityReview.hardFailures")
    if any(item not in QUALITY_HARD_FAILURES for item in hard_failures):
        raise DirectionError("qualityReview.hardFailures contains an invalid code")
    if review["reviewBasis"] == "direction-plan":
        if any(value is not None for value in (scene_id, scene_hash, preview_hash)):
            raise DirectionError("direction-plan review cannot claim scene or preview evidence")
        if any(status != "pending" for status in statuses):
            raise DirectionError("direction-plan quality items must remain pending until preview pixels exist")
        if hard_failures:
            raise DirectionError("direction-plan cannot claim pixel hard failures")
    else:
        if scene_id is None or scene_hash is None or preview_hash is None:
            raise DirectionError("preview-pixels review requires sceneId, sceneHash, and previewHash")
        if any(status == "pending" for status in statuses):
            raise DirectionError("preview-pixels quality items cannot remain pending")

    if not string_list(root["negativeConstraints"], "negativeConstraints"):
        raise DirectionError("negativeConstraints cannot be empty")
    unknowns = string_list(root["unknowns"], "unknowns")
    if set(unknowns) != set(unknown_claims):
        raise DirectionError("unknowns must exactly match evidence claims with status unknown")
    return root


def format_number(value: Any) -> str:
    return f"{float(value):.6f}".rstrip("0").rstrip(".")


def format_region(value: dict[str, Any]) -> str:
    return (
        f"x={format_number(value['x'])}, y={format_number(value['y'])}, "
        f"width={format_number(value['width'])}, height={format_number(value['height'])}"
    )


def bullet_list(items: list[str], empty: str) -> list[str]:
    return [f"- {item}" for item in items] if items else [empty]


def compile_description(payload: dict[str, Any]) -> str:
    deliverable = payload["deliverable"]
    canvas = payload["canvas"]
    locks = payload["assetLocks"]
    rationale = payload["designRationale"]
    composition = payload["composition"]
    focal = composition["focalPlacement"]
    visual = payload["visualSystem"]
    environment = payload["lightboxEnvironment"]
    review = payload["qualityReview"]
    integration = payload["integrationPlan"]
    routing = integration["layoutRouting"]
    reference_plan = payload["referenceInfluencePlan"]
    evidence_by_id = {item["id"]: item for item in payload["evidence"]}

    lines = [
        "【SceneSpec 规划控制文档】",
        "本文件用于已批准素材的确定性场景规划，不构成图像生成授权。",
        "",
        "【生成目标】",
        deliverable["description"],
        f"原始请求（仅作为意图，不自动成为画中文字）：{payload['sourceRequest']}",
        f"素材清单哈希：{payload['manifestHash']}",
        "",
        "【交付载体】",
        f"类型：{deliverable['kind']}",
        f"观看条件：{deliverable['viewingContext']}",
        f"观者动作：{deliverable['viewerAction']}",
        f"载体原因：{rationale['carrierReason']}",
        "",
        "【主体原因与视觉效果】",
        f"主体原因：{rationale['subjectCause']}",
        f"观者效果：{rationale['viewerEffect']}",
        f"主导关系：{rationale['dominantRelation']}",
        f"拒绝方案：{rationale['rejectedAlternative']}",
        "",
        "【画布与视角】",
        f"输出 {canvas['width']}×{canvas['height']} px，比例 {canvas['aspectRatio']}，方向 {canvas['orientation']}。",
        f"相机：{visual['camera']}",
        "",
        "【统一柔光箱环境】",
        f"模式：{environment['mode']}；标定：{environment['calibration']}。",
        f"相机：{environment['camera']['projection']}；倾角 {format_number(environment['camera']['tiltDeg'])}°。",
        "发光面："
        f"{environment['emissiveSurface']['state']}；"
        f"强度 {format_number(environment['emissiveSurface']['intensity'])}；"
        f"色温 {format_number(environment['emissiveSurface']['temperatureKelvin'])}K。",
        "顶部补光："
        f"{environment['topFill']['state']}；"
        f"强度 {format_number(environment['topFill']['intensity'])}；"
        f"色温 {format_number(environment['topFill']['temperatureKelvin'])}K。",
        f"衰减：{environment['falloff']['model']}；edge={format_number(environment['falloff']['edge'])}。",
        "表面："
        f"{environment['surface']['material']}；"
        f"transmission={format_number(environment['surface']['transmission'])}；"
        f"roughness={format_number(environment['surface']['roughness'])}；"
        f"diffuserLayers={environment['surface']['diffuserLayers']}。",
        "接触阴影："
        f"{environment['contactShadow']['model']}；"
        f"opacityScale={format_number(environment['contactShadow']['opacityScale'])}；"
        f"edgeFeather={format_number(environment['contactShadow']['edgeFeather'])}。",
        *[
            f"- {family} · {environment['materialResponses'][family]['opticalModel']} · "
            f"{environment['materialResponses'][family]['renderStrategy']} · "
            f"{environment['materialResponses'][family]['contactShadow']}"
            for family in (
                "metal",
                "paper",
                "tracingPaper",
                "film",
                "acrylicGlass",
                "sourcePreserved",
            )
        ],
        f"环境证据：{', '.join(environment['evidenceIds'])}。",
        "",
        "【资产锁定】",
        f"必须原样使用：{', '.join(locks['mustUseExact']) if locks['mustUseExact'] else '无'}。",
        f"允许受控变换：{', '.join(locks['canTransform']) if locks['canTransform'] else '无'}。",
        f"仅作风格参考、不得出现在画面：{', '.join(locks['referenceOnly']) if locks['referenceOnly'] else '无'}。",
        f"排除：{', '.join(locks['excluded']) if locks['excluded'] else '无'}。",
        "",
        "【参考影响边界】",
    ]
    if reference_plan:
        lines.extend(
            f"- {item['assetId']} · {item['scope']} · {item['evidenceId']}：{item['rule']}"
            for item in sorted(
                reference_plan,
                key=lambda item: (item["assetId"], REFERENCE_INFLUENCE_SCOPES.index(item["scope"])),
            )
        )
    else:
        lines.append("无。参考素材不得影响任何输出轴。")
    scopes_by_reference = {
        asset_id: {
            item["scope"] for item in reference_plan if item["assetId"] == asset_id
        }
        for asset_id in locks["referenceOnly"]
    }
    for asset_id in sorted(scopes_by_reference):
        prohibited = [
            scope
            for scope in REFERENCE_INFLUENCE_SCOPES
            if scope not in scopes_by_reference[asset_id]
        ]
        lines.append(
            f"{asset_id} 禁止影响：" + ("、".join(prohibited) if prohibited else "无") + "。"
        )
    lines.extend([
        "参考素材不得成为可见对象、贴图、文字或可识别内容。",
        "",
        "【素材整合】",
        f"模式：{integration['mode']}；意图证据：{integration['intentEvidenceId']}。",
        f"可见素材数：{len(integration['requiredVisibleAssetIds'])}。",
        f"布局族：{integration['layoutFamily']}。",
        f"溢出策略：{integration['overflowPolicy']}；最小可见短边：{integration['minimumVisibleShortEdgePx']} px。",
        *[
            f"- {item['assetId']} · {item['hierarchy']} · {item['carrier']} · evidence={item['evidenceId']}"
            for item in sorted(integration["assignments"], key=lambda item: item["assetId"])
        ],
        f"主导材料：{integration['materialRelation']['dominant']}。",
        f"支撑材料：{'；'.join(integration['materialRelation']['supporting'])}。",
        f"材料关系：{integration['materialRelation']['relationship']}",
        "",
        "【版式路由】",
        f"共享表面风格：{routing['surfaceStyle']}。",
        f"选择信号：{', '.join(routing['selectionSignals'])}。",
        f"风格原因：{routing['styleRationale']}",
        "【构图语法】",
        *[
            line
            for candidate in sorted(
                routing["candidates"],
                key=lambda item: LAYOUT_TEMPLATE_IDS.index(item["templateId"]),
            )
            for grammar in [candidate["compositionGrammar"]]
            for line in (
                f"- {candidate['templateId']} · {candidate['archetype']} · {candidate['density']} · "
                f"{candidate['alignment']} · {candidate['scaleRhythm']}",
                f"  路由原因：{candidate['rationale']}",
                f"  根节点：{grammar['rootAssetId']}。",
                f"  主流向：{grammar['flow']}。",
                f"  阅读顺序：{' → '.join(grammar['readingOrder'])}。",
                *(
                    f"  分组 {group['groupId']} · {group['role']} · {group['arrangement']} · "
                    f"{', '.join(group['assetIds'])}：{group['purpose']}"
                    for group in grammar["groups"]
                ),
                *(
                    f"  {link['parentAssetId']} → {link['childAssetId']} · {link['axis']} · "
                    f"{link['contact']} · {link['spacing']}：{link['purpose']}"
                    for link in sorted(
                        grammar["links"],
                        key=lambda link: grammar["readingOrder"].index(link["childAssetId"]),
                    )
                ),
                f"  负空间：{grammar['negativeSpace']['mode']} · "
                f"anchor={grammar['negativeSpace']['anchorAssetId']}："
                f"{grammar['negativeSpace']['purpose']}",
            )
        ],
        "每个候选语法只表达相对关系；可执行坐标只能来自已确认的位置证据或确定性布局求解。",
        "",
        "【素材表现】",
        *[
            line
            for item in sorted(integration["assignments"], key=lambda item: item["assetId"])
            for line in (
                f"- {item['assetId']} · {item['representation']['kind']} · {item['representation']['form']}",
                f"  carrier={item['carrier']}；material={item['representation']['materialFamily']}；"
                f"render={item['representation']['renderStrategy']}；light={item['representation']['lightBehavior']}",
                f"  transformation={item['representation']['transformationEvidenceId']} "
                f"[{evidence_by_id[item['representation']['transformationEvidenceId']]['status']}]；"
                f"scale={item['representation']['scaleEvidenceId']} "
                f"[{item['representation']['scaleEvidenceStatus']}]",
                f"  rationale={item['representation']['rationale']}",
            )
        ],
        "",
        "【构图】",
        f"主角：{composition['heroAssetId']}。",
    ])
    if focal["region"] is None:
        lines.append("焦点区域：未解析；不得从‘这里’推断坐标。")
    else:
        lines.append(f"焦点区域：{format_region(focal['region'])}。")
    lines.extend(
        [
            f"位置证据：{focal['regionEvidence']}（{focal['confirmation']}），证据 {focal['evidenceId']}。",
            f"空间关系：{focal['relationship']}",
            f"视觉重量：{composition['occupiedMass']}",
            f"负空间：{composition['negativeSpace']}",
            f"阅读路径：{composition['readingPath']}",
            f"密度：{composition['density']}。",
            "",
            "【优化动作（按优先级）】",
        ]
    )

    actions = sorted(
        payload["optimizationActions"],
        key=lambda item: (PRIORITY_ORDER[item["priority"]], item["id"]),
    )
    if not actions:
        lines.append("无。")
    for item in actions:
        lines.extend(
            [
                f"- {item['priority']} · {item['id']}：{item['issue']}",
                f"  动作：{item['action']}",
                f"  主体原因：{item['subjectCause']}",
                f"  观者效果：{item['viewerEffect']}",
                f"  目标资产：{', '.join(item['targetAssetIds']) if item['targetAssetIds'] else '无'}",
                f"  证据：{', '.join(item['evidenceIds'])}",
                f"  限制：{'；'.join(item['constraints'])}",
            ]
        )

    lines.extend(["", "【组件与元素增加位置（P3/P4）】"])
    opportunities = sorted(
        payload["placementOpportunities"],
        key=lambda item: (PRIORITY_ORDER[item["priority"]], item["id"]),
    )
    if not opportunities:
        lines.append("无。保留现有负空间，不为填满画面而添加装饰物。")
    for item in opportunities:
        anchor = item["anchor"]
        scale = item["scale"]
        orientation = item["orientation"]
        lines.extend(
            [
                f"- {item['priority']} · {item['id']}：{item['element']}",
                f"  区域：{format_region(item['region'])}",
                f"  位置证据：{item['regionEvidence']}（{item['confirmation']}），证据 {item['evidenceId']}",
                f"  目的：{item['purpose']}",
                f"  主体原因：{item['subjectCause']}",
                f"  观者效果：{item['viewerEffect']}",
                f"  移除影响：{item['removalImpact']}",
                "  锚定："
                f"{anchor['relation']} {anchor['targetAssetId'] or 'canvas'}；"
                f"最小间隙 {format_number(anchor['minimumGapFraction'])}；"
                f"最大重叠 {format_number(anchor['maximumOverlapFraction'])}；"
                f"接触 {anchor['contactMode']}",
                "  尺度："
                f"{scale['basis']} 的 {format_number(scale['minFraction'])}–"
                f"{format_number(scale['maxFraction'])}",
                f"  材料：{item['material']}",
                "  方向："
                f"{format_number(orientation['minDegrees'])}°–"
                f"{format_number(orientation['maxDegrees'])}°",
                f"  置信度：{item['confidence']}",
                f"  限制：{'；'.join(item['constraints'])}",
            ]
        )

    system_labels = [
        ("层级", "hierarchy"),
        ("组件细节", "componentDetail"),
        ("纹理尺度", "textureScale"),
        ("材料", "materials"),
        ("光线", "lighting"),
        ("色彩", "palette"),
        ("边缘与阴影", "edgeAndShadow"),
    ]
    lines.extend(["", "【统一画面系统】"])
    lines.extend(f"- {label}：{visual[key]}" for label, key in system_labels)
    lines.append(f"- 系统证据：{', '.join(visual['evidenceIds'])}")

    lines.extend(["", "【证据边界】"])
    for item in payload["evidence"]:
        assets = f"（{', '.join(item['sourceAssetIds'])}）" if item["sourceAssetIds"] else ""
        lines.append(f"- {item['id']} [{item['status']}] {item['claim']}{assets}")

    lines.extend(["", "【可见文字】"])
    visible_text = payload["approvedVisibleText"]
    if visible_text:
        lines.extend(
            f"- {item['content']}（批准证据：{item['approvalEvidenceId']}）"
            for item in visible_text
        )
        lines.append("除以上逐字批准内容外，不得生成任何其他文字、数字、坐标或品牌标记。")
    else:
        lines.append("无。不得生成任何文字、数字、坐标或品牌标记。")

    quality_labels = [
        ("视觉统一", "visualUnity"),
        ("组件细节", "componentDetail"),
        ("纹理尺度", "textureScale"),
        ("自然性", "naturalness"),
        ("克制", "restraint"),
        ("阅读流", "readingFlow"),
        ("物理合理性", "physicalPlausibility"),
    ]
    lines.extend(["", "【质量门】"])
    if review["reviewBasis"] == "direction-plan":
        lines.append("复核依据：direction-plan；未查看预览像素。")
    else:
        lines.append(
            "复核依据：preview-pixels；"
            f"scene={review['sceneId']}；sceneHash={review['sceneHash']}；"
            f"previewHash={review['previewHash']}。"
        )
    lines.extend(
        f"- {label} [{review['items'][key]['status']}]：{review['items'][key]['note']}"
        for label, key in quality_labels
    )
    lines.append(
        "- 像素硬失败："
        + ("、".join(review["hardFailures"]) if review["hardFailures"] else "无")
    )

    lines.extend(["", "【负向约束】"])
    lines.extend(bullet_list(payload["negativeConstraints"], "无。"))
    lines.extend(["", "【未决信息】"])
    lines.extend(bullet_list(payload["unknowns"], "无。"))
    return "\n".join(lines) + "\n"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--workflow", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)


def main() -> None:
    arguments = parse_arguments()
    try:
        payload = read_json(arguments.input)
        manifest_value = read_json(arguments.manifest)
        workflow_value = read_json(arguments.workflow)
        manifest, _assets, computed_hash = validate_manifest(manifest_value)
        validate_workflow(workflow_value, manifest["projectId"], computed_hash)
        description = compile_description(validate(payload, manifest))
        if arguments.output is None:
            sys.stdout.write(description)
        else:
            arguments.output.write_text(description, encoding="utf-8")
    except (OSError, json.JSONDecodeError, DirectionError) as error:
        code = error.code if isinstance(error, DirectionError) else "INVALID_VISUAL_DIRECTION"
        print(f"Invalid visual direction [{code}]: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
