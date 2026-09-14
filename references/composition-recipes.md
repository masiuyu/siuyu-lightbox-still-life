# Composition Recipes

Scope: Explicit offline renderer operation or implementation. Enter through [Offline workflow](offline-workflow.md) for the local runtime contract.

Use this protocol after manifest approval and before scene generation. It turns a broad visual brief into controlled, testable variation without changing source truth.

## 1. Fixed System

These rules stay fixed across all three candidate scenes:

- approved canvas and aspect ratio;
- top-down or near-orthographic light-table camera;
- exact source roles, preservation levels, and text allowlist;
- exact product, logo, museum-image, and typography layers;
- light-table source stack and physically differentiated materials;
- no visible `reference_only` assets;
- both human approval gates and deterministic serialization.

These are invariants, not aesthetic suggestions.

## 2. Variable System

Vary only declared axes:

| Axis | Controlled choices |
|---|---|
| layout route | compatible archetype, density, alignment, and scale rhythm from `layoutRouting` |
| supporting field | optical stage, unequal inventory, evidence ribbon, editorial spine, material bridge, or taxonomy |
| reading path | horizontal, vertical, diagonal, radial, stepped, or banded sequence |
| overlap graph | separated, edge-touching, or shallow overlap that never hides protected content |
| prop family | one coherent family of tools, sleeves, frames, folders, or measurement objects |
| material emphasis | paper/film, metal/acrylic, or mixed with explicit hierarchy |
| light character | neutral, slightly warm, or slightly cool within the implemented preset range |
| text placement | one approved safe region that preserves minimum type size |

Do not vary exact identity, approved copy, asset usage, source hashes, or physical-truth labels.

## 3. Recipe Record

For every candidate, report:

```text
template ID + version + seed
layout archetype + density + alignment + scale rhythm
hero asset and anchor zone
supporting asset set
prop family and scale rationale
material emphasis
reading path and overlap graph
text safe region
fixed constraints retained
known uncertainties
```

The recipe describes decisions already represented by the manifest, normalized constraints, and `SceneSpec`; it is not a second source of geometry truth.

## 4. Three-Candidate Diversity

The three fixed templates must be recognizably different at thumbnail scale. `layoutRouting` gives each template a distinct signature. At minimum, each candidate must differ from the others on:

- hero anchor or dominant reading path;
- supporting-field structure;
- prop/material emphasis.

Changing only a seed, small rotation, or decorative prop does not count as a distinct composition. Conversely, diversity must not alter exact assets, approved text, or user-approved constraints.

## 5. Adaptive Merge-All Families

Choose the family from the number of approved content assets, not from a favorite template. This is a capacity family, not an art direction; route the actual composition through [Layout routing](layout-routing.md).

| Approved content count | Required family | Composition behavior |
|---|---|---|
| `1 asset` | `relational_field` | One authored product event. Build material, light, crop, and contact around the source; do not pad the frame with invented thumbnails. |
| `2–6 assets` | `asymmetric_cluster` | One hero plus a connected supporting cluster. Vary carriers and scale; establish one reading path and physical adjacency. |
| `7–16 assets` | `editorial_taxonomy` | Use a dominant event plus grouped evidence bands, contact-print runs, sleeves, or layered papers. Avoid a rigid equal-card dashboard. |
| `17–40 assets` | `expanded_taxonomy` | Use denser but legible taxonomy, nested physical groupings, and multiple reading bands under one dominant material field. Preserve the minimum visible short edge. |

All families use `overflowPolicy: adapt_or_block`. If the canvas cannot keep every `requiredVisibleAssetIds` contribution above `minimumVisibleShortEdgePx`, enlarge or change the canvas, reduce the approved content set through an explicit user decision, or block. Never silently omit a file and never turn the overflow into a ring of tiny corner stamps.

All-visible is a quantity constraint, not a demand for full-frame or equal-sized sources. A contribution may be a faithful cutout, a bounded physical photograph, an authored contact-print frame, a film sleeve, or an approved tracing-paper crop. It must remain visible, recognizable at the declared floor, attributable to its source ID, and materially connected to the scene.

## 6. Authored Relative Grammar

Every VisualDirection v6 candidate must encode one `compositionGrammar`; prose about balance or mood is not enough. Work in this order: `source representation → hero event → groups → rooted links → reading order → negative space → executable geometry`.

The grammar is `rooted` and `relative-only`. It chooses one hero root; partitions every required visible source into contiguous `hero_event`, `support_cluster`, `evidence_band`, or `material_bridge` groups; gives every non-hero source one earlier parent; and protects one coherent negative-space strategy. Links specify only relative axis, contact, spacing, and purpose. They never contain normalized coordinates, regions, millimetres, or inferred user anchors.

Build group structure from source meaning and representation:

- use `hero_event` once for the exact product event;
- use `support_cluster` for sources that directly contextualize or balance the hero;
- use `evidence_band` for drawings, process images, contact prints, and documentary sequences;
- use `material_bridge` when one approved source carries a necessary color, surface, or light transition between groups.

Adapt the graph to source count. A one-source scene can be deliberately sparse. A two-to-six-source scene usually needs one connected cluster, not four detached corners. Seven-to-sixteen sources can become contiguous evidence bands around one dominant event. Seventeen-to-forty sources can use multiple bands and bridges, but still require one rooted reading order and legible minimum size. `tools are optional`; never add workshop inventory merely to fill a grammar slot.

For a one-to-six-source cluster, calculate the reading result in this order: truthful carrier, hero hierarchy, semantic link, relative scale, optical centroid, then negative space. Default the cluster's visual mass toward the safe-field center while allowing a deliberate asymmetric arm only when it continues the reading path. Treat accidental unilateral emptiness as `recoverable_by_recomposition`; scale, shift, or reconnect the approved sources before considering any new content. Preserve deliberate air as `functional_breathing_space`. Only a residual subject-led need becomes a `supplement_candidate`, and that candidate stays out of the scene until explicit user selection and any required manifest re-approval.

Reject a candidate if its graph would merely encode equal cards, a dashboard, a ring of postage stamps, or floating source planes without semantic and physical linkage. A coordinate may enter executable geometry only from confirmed user-markup/user-coordinate evidence or from the deterministic solver; solver output is not retroactive user evidence.

## 7. Precision Atelier Route

Use the `precision atelier` route when the subject and evidence support jewelry, watchmaking, instrument, or craft-tool language. It is a recipe, not the universal house style:

- let one exact product be the singular optical event;
- use a silver-gray working field with pale pink acrylic only when it supports the product palette;
- stage supplied metal tools at credible relative scale with restrained highlights, real edge thickness, and contact shadows;
- use partial edge crops to imply a working surface rather than centering every object;
- translate other required images into different truthful carriers such as contact prints, translucent film, or tracing sheets;
- keep one dominant material/light relationship across those carriers;
- reject four-corner stamps, floating source rectangles, decorative metadata, and a second competing hero.

If the product source is opaque, either obtain a transparent cutout or treat the unchanged full source as a designed physical photograph. A black or white source rectangle is not the product itself and cannot masquerade as a cutout.

## 8. Reference Safety

Use the `fixed system`, `variable system`, and `sample residue` split from Source analysis. A reference may guide density, light falloff, material contrast, or hierarchy, but its wording, logo, subject, distinctive one-off arrangement, and accidental artifacts remain excluded.

## 9. Physical Plausibility Gate

Before preview approval, check:

- relative product and prop scale is supported or explicitly marked uncertain;
- thickness cues match material and object role;
- every raised object has a plausible contact shadow;
- transparent, translucent, reflective, and opaque materials react differently;
- no tool, folder, or document intersects a protected product impossibly;
- no generated prop claims a precise real-world size without evidence;
- paper grain, labels, handles, fasteners, and tool geometry are proportionate to their object.

If the implementation cannot express verified physical dimensions, report `visual-scale only`; do not claim calibrated realism.

## 10. Preview Quality Gate

Inspect actual rendered pixels, not only JSON or DOM state. Reject or regenerate a candidate when:

- a protected asset is distorted, redrawn, occluded, or missing;
- unapproved text appears;
- reference sample residue leaks into content;
- material or contact behavior is implausible;
- the three candidates are trivial variations;
- annotations and the visible preview disagree.

Always fail the pixel review when any of these is present:

- `NESTED_BACKGROUND_RECTANGLE` — a source-background rectangle sits inside another generic panel without a designed physical carrier;
- `CORNER_THUMBNAIL_TEMPLATE` — the design falls back to a hero plus detached corner stamps;
- `FLOATING_ASSET_PLANES` — image planes lack contact, support, shadow, or semantic linkage;
- `SINGLE_GENERIC_MATERIAL` — unrelated materials receive one undifferentiated finish;
- `PALETTE_FRAGMENTATION` — source colors remain disconnected rather than subordinated to one controlled field;
- `NO_DOMINANT_MATERIAL_RELATION` — no material/light/contact relationship organizes the frame.

Persist only validation facts produced by the implemented pipeline. A visual judgment may be reported as a review note, but it must not be disguised as a deterministic validator result.
