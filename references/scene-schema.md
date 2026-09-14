# Scene Schema

Scope: Explicit offline renderer operation or implementation. Enter through [Offline workflow](offline-workflow.md) for the local runtime contract.

## Contents

1. Determinism
2. SceneSpec
3. Objects
4. Text
5. Lighting
6. Validation
7. Exact-layer map

## 1. Determinism

The tuple below determines scene JSON:

```text
manifest hash + visual-direction hash + template ID + template version + seed + normalized user constraints
```

When direction constraints exist, select the `layoutRouting` candidate whose `templateId` matches the scene and consume assets in that candidate's `compositionGrammar.readingOrder`; without a direction record, use stable asset ID order. Keep authored group membership contiguous, use a seeded PRNG, and serialize keys and arrays deterministically. Never use current time, random UUIDs, filesystem enumeration order, or model prose inside geometry generation.

## 2. SceneSpec

```json
{
  "version": 1,
  "sceneId": "scene_archive_731",
  "projectId": "project_001",
  "templateId": "archive_research_v1",
  "templateVersion": 1,
  "seed": 731,
  "manifestHash": "sha256:...",
  "canvas": {
    "width": 1600,
    "height": 2000,
    "pixelRatio": 1,
    "colorSpace": "srgb",
    "background": "lightbox"
  },
  "lightbox": {
    "widthMm": 600,
    "heightMm": 750,
    "surfaceThicknessMm": 8,
    "frameDepthMm": 35,
    "diffuserGapMm": 25,
    "intensity": 0.82,
    "temperatureKelvin": 4700,
    "edgeFalloff": 0.18,
    "diffuserRoughness": 0.72,
    "diffuserLayers": 2,
    "frameVisible": true
  },
  "lightboxEnvironment": {
    "mode": "hybrid_diffused_table",
    "calibration": "visual_preset_not_physical_measurement",
    "camera": { "projection": "orthographic", "tiltDeg": 1.2 },
    "emissiveSurface": { "state": "active", "intensity": 0.82, "temperatureKelvin": 4700 },
    "topFill": { "state": "active", "intensity": 1.23, "temperatureKelvin": 5200 },
    "falloff": { "model": "radial", "edge": 0.18 },
    "surface": { "material": "frosted_acrylic", "transmission": 0.9, "roughness": 0.72, "diffuserLayers": 2 },
    "contactShadow": { "model": "material_specific", "opacityScale": 1, "edgeFeather": 0.12 },
    "materialResponses": {
      "metal": { "opticalModel": "opaque_reflective", "renderStrategy": "native_material", "contactShadow": "defined" },
      "paper": { "opticalModel": "opaque_diffuse", "renderStrategy": "native_material", "contactShadow": "soft" },
      "tracingPaper": { "opticalModel": "translucent", "renderStrategy": "native_material", "contactShadow": "soft" },
      "film": { "opticalModel": "transmissive", "renderStrategy": "native_material", "contactShadow": "minimal" },
      "acrylicGlass": { "opticalModel": "refractive_highlight", "renderStrategy": "native_material", "contactShadow": "minimal" },
      "sourcePreserved": { "opticalModel": "source_preserved", "renderStrategy": "exact_2d_layer", "contactShadow": "source_alpha" }
    },
    "evidenceIds": ["evidence_lightbox_environment"]
  },
  "objects": [],
  "textBlocks": [],
  "compositionPlan": {
    "focalPoint": { "x": 0.5, "y": 0.5 },
    "safeMarginMm": 40,
    "minimumGapMm": 12,
    "maxOverlapRatio": 0.12,
    "targetCoverageRatio": 0.58,
    "balanceMode": "asymmetric"
  },
  "constraints": { "safeMargin": 0.05, "maxOverlapRatio": 0.12, "minReadableFontPx": 14 }
}
```

Use normalized `x`, `y`, `w`, and `h` values in `[0,1]`. Use degrees for rotation. Define a stable z-index; ties are invalid.

When a scene comes from `visualDirectionToBuildSceneRequest`, `directionConstraints` also records the canonical direction hash, all four asset-role groups, the closed `integrationPlan`, confirmed focal region and evidence, confirmed supporting placements, approved-text allowlist, manifest-approval timestamp, `manifestApprovalHash`, and the still-required second scene approval. This is provenance and an allowlist, not permission to invent text placement. The schema rejects role/hash drift, reference or excluded source objects, missing exact heroes, supporting assets that are absent or repeated, supporting transforms outside their user-confirmed pixel-space region, and text outside the allowlist.

`integrationPlan.requiredVisibleAssetIds` is the quantity ledger. In `merge_all`, it exactly equals the approved exact plus transformable asset set and has one assignment per ID. Each assignment records `hero`, `secondary`, or `supporting` hierarchy; one evidence-bound source representation; and one of `cutout`, `physical_photo`, `contact_print`, `film_sleeve`, or `tracing_sheet`. The plan also fixes the count-aware capacity family, `adapt_or_block`, minimum visible short edge, dominant/supporting material relation, and `layoutRouting`. Routing chooses one shared surface style and exactly three distinct candidate signatures from approved source evidence. An opaque manifest asset cannot use `cutout`; an opaque hero must use `physical_photo`.

The representation is semantic provenance, not replacement pixels. It records one closed kind (`physical_object`, `source_photograph`, `technical_drawing`, `material_field`, `contact_print`, `film_transparency`, `tracing_overlay`, `relief_impression`, or `exact_cutout`), its compatible form, `materialFamily`, render strategy, light behavior, `transformationEvidenceId`, `scaleEvidenceId`, `scaleEvidenceStatus`, and rationale. Exact product and branding sources allow only `exact_cutout` or `source_photograph`; opaque sources cannot use isolated representations. Derived drawing, field, overlay, and relief forms require an approved `can_transform` source plus user-supplied transformation evidence. Unknown material or scale remains explicit.

Every VisualDirection v6 layout candidate carries a complete `compositionGrammar`: one hero root, closed flow, all-source reading order, authored groups, rooted relative links, and one negative-space strategy. It is `relative-only`; its strict objects reject coordinates, regions, dimensions, and millimetres. The builder preserves confirmed user regions, then uses the active candidate's archetype, density, alignment, scale rhythm, and grammar links to choose deterministic remaining regions. Only a declared non-hero `shallow_overlap` link may add that parent object ID to `allowOverlapWith`; every other pair retains normal overlap and safe-margin validation.

VisualDirection v6 also carries the complete `lightboxEnvironment`. Its mode is one of `diffused_softbox`, `transmitted_light_table`, or `hybrid_diffused_table`; the top-level record and `directionConstraints.lightboxEnvironment` must be byte-equivalent after canonical parsing. The compatible legacy `lightbox` fields are derived from that same record and must match emitter intensity/temperature, radial edge falloff, surface roughness, and diffuser-layer count. The environment adds no object geometry or placement evidence.

The renderer consumes the declared orthographic camera, active emitter states, falloff, frosted surface, contact-shadow controls, and closed material catalog. Metal stays `opaque_reflective`; paper stays `opaque_diffuse`; tracing paper stays `translucent`; film stays `transmissive`; acrylic/glass stays `refractive_highlight`; protected identity pixels stay `source_preserved` through `exact_2d_layer`. An unsupported descriptor/environment pair is a hard renderer error, not permission to collapse it into a generic plastic material.

The current renderer continues to use the truthful carrier and exact source pixels. Carrying a representation through `BuildSceneRequest` and `SceneSpec.directionConstraints` does not claim that the renderer synthesized new geometry, material physics, a drawing, or a relief. The complete record remains hash-bound to the VisualDirection and both approval gates.

A confirmed supporting placement contains one transparent `can_transform` asset ID, user-markup or user-coordinate evidence ID, normalized region, and deterministic rotation. The scene must place that asset exactly once as `transformed_texture`; its rotated pixel bounds must remain within the region on the declared canvas. A candidate placement is intentionally absent from this trace and cannot create geometry.

## 3. Objects

```json
{
  "id": "hero_product_01",
  "sourceAssetId": "asset_001",
  "placementMode": "exact_composite",
  "geometry": "image_plane",
  "material": "cutout_object",
  "x": 0.68,
  "y": 0.30,
  "w": 0.28,
  "h": 0.28,
  "rotationDeg": -2.0,
  "zIndex": 120,
  "opacity": 1.0,
  "locked": true,
  "castsShadow": true,
  "receivesBacklight": false
}
```

Placement modes:

- `exact_composite`
- `transformed_texture`
- `generated_prop`
- `reference_hidden`

A `reference_only` asset may appear only as `reference_hidden`; it must not produce pixels in preview or final.

## 4. Text

```json
{
  "id": "folder_title",
  "content": "Material Field Study",
  "x": 0.70,
  "y": 0.18,
  "w": 0.18,
  "h": 0.06,
  "fontFamily": "Inter",
  "fontWeight": 500,
  "minFontPx": 14,
  "maxFontPx": 26,
  "maxLines": 2,
  "lineHeight": 1.2,
  "fitMode": "multiline_then_shrink",
  "requiredExact": true
}
```

Measure using the actual export font. If no fitting size at or above `minFontPx` exists, emit a blocking error. Do not truncate exact text unless the user approves revised copy. `approvedVisibleText` in a v1 direction trace approves content only; the bridge must not create a `TextBlock` until separate placement evidence is confirmed.

## 5. Lighting

Represent the light table separately from environment light:

```json
{
  "emitter": { "type": "rect", "intensity": 850, "temperatureK": 4700 },
  "diffuser": { "layers": 2, "scatter": 0.72 },
  "surface": { "transmission": 0.78, "roughness": 0.72 },
  "environment": { "intensity": 0.16, "temperatureK": 5200 },
  "camera": { "type": "orthographic", "tiltXDeg": 1.5, "tiltYDeg": -0.8 }
}
```

These are scene presets, not claims of calibrated physical measurements. Keep the renderer deterministic and tune them against approved reference outputs.

## 6. Validation

Every issue contains:

```json
{
  "code": "TEXT_OVERFLOW",
  "targetId": "folder_title",
  "severity": "blocking",
  "message": "Text requires 12px; minimum is 14px",
  "suggestedActions": ["increase box height", "shorten copy"]
}
```

Blocking codes include text overflow, text below minimum, out-of-bounds objects, missing required assets, missing integrated content, duplicate required usage, opaque false cutouts, product occlusion, stale approval, or invalid exact-layer transforms. `contentAssetCoverage` reports exactly-once coverage for `integrationPlan.requiredVisibleAssetIds`; it does not replace pixel review.

## 7. Exact-Layer Map

Final export records the source and transform for each protected layer:

```json
{
  "layers": [
    {
      "objectId": "hero_product_01",
      "assetId": "asset_001",
      "sourceHash": "sha256:...",
      "transformHash": "sha256:...",
      "compositedAfterEnhancement": true
    }
  ]
}
```

Use this map to prove that final products, logos, exact content images, and text were reapplied after enhancement.
