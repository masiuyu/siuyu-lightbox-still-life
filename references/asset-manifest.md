# Asset Manifest

Scope: Explicit offline renderer operation or implementation. Enter through [Offline workflow](offline-workflow.md) for the local runtime contract.

## Contents

1. Categories
2. Usage modes
3. Classification precedence
4. Reference influence contract
5. Required fields
6. Contact-sheet presentation
7. Examples

## 1. Categories

```text
product_core
branding_asset
document_sketch
artifact_reference
style_reference
supporting_prop
duplicate_or_unused
```

## 2. Usage Modes

| Usage | Meaning | Scene behavior |
|---|---|---|
| `must_use_exact` | Identity, geometry, logo, text, or provenance must remain exact | Composite the source or approved derivative as an exact layer |
| `can_transform` | Cropping, desaturation, paperization, cyanotype, sleeve, or tracing-paper treatment is allowed | Use as texture or approved derivative |
| `reference_only` | Approved abstract influence only | Never create a scene object, visible carrier, copied subject, or visible count from it |
| `ignore` | Duplicate, UI screenshot, irrelevant, unsafe, or unusable | Exclude from layout and final |

## 3. Classification Precedence

Determine integration intent before automated inference. Explicit user instructions are always authoritative:

1. User says “must use,” “1:1,” “do not change,” “logo,” or “exact text” → `must_use_exact`.
2. User says “only reference,” “style,” “mood,” or “lighting reference” → `reference_only`.
3. User explicitly excludes a file → `ignore`.
4. Under `merge_all`, every other upload remains `must_use_exact` or `can_transform` pending manifest approval. `merge_all conservation overrides filename and duplicate heuristics`; those heuristics may warn but cannot silently remove scene content.
5. Under `default`, an exact duplicate of a stronger source may become `ignore`, linked to its canonical asset, and a filename may suggest reference or UI status.
6. Sketch, paper, diagram, or photo without an exactness requirement → usually `can_transform`.
7. Unclear high-value product or branding asset → flag for human review; do not guess it is transformable.

The first human gate must display the content count and every explicit non-visible decision. A screenshot-looking file may be deliberate content, and two byte-identical uploads may represent two requested physical placements; only the user can resolve those cases under `merge_all`.

## 4. Reference Influence Contract

Every newly classified `reference_only` asset must carry an explicit, sorted `influenceScopes` array. The closed values are:

```text
layout
palette
lighting
material
texture
typography
motif
```

An empty array means the first-gate proposal is “no approved influence”; it is different from a missing field. For backward compatibility an old manifest may still parse without the field, but `missing influenceScopes requires fresh human review` and blocks Production approval. Non-reference assets must not carry the field.

The manifest hash sorts scope order before hashing, so equivalent orderings have one hash while any permission change produces a new hash. The human `manifestApproval` receipt binds that result. A scope change invalidates the prior first approval and every downstream scene receipt; it never inherits permission from chat wording or a previous manifest.

VisualDirection v6 may use only manifest-approved axes. Each use is represented by one `referenceInfluencePlan` entry bound to the reference asset and observed or user-supplied evidence from that same source. Reference pixels, subjects, logos, wording, and distinctive one-off arrangements remain prohibited even when an abstract axis is approved. References receive no integration assignment or source representation.

A manifest with no `product_core` + `must_use_exact` content asset cannot receive production approval. An explicitly requested concept starts as an offline `ConceptAssetBrief`; a resulting candidate must be ingested as new content, change the manifest hash, and return to the first human approval.

## 5. Required Fields

```json
{
  "assetId": "asset_001",
  "fileName": "product-front.png",
  "originalUri": "project://project_demo/uploads/product-front.png",
  "sha256": "...",
  "mimeType": "image/png",
  "width": 2400,
  "height": 2400,
  "category": "product_core",
  "usage": "must_use_exact",
  "needsCutout": true,
  "allowGenerativeRedraw": false,
  "status": "ready",
  "tags": ["hero"],
  "hasAlpha": true,
  "duplicateOfAssetId": null
}
```

Validate MIME by decoded content, not filename. Enforce configured file size, dimensions, and total pixel count before derivatives are created.

## 6. Contact-Sheet Presentation

Show each asset with:

- stable number and asset ID;
- thumbnail;
- filename and decoded dimensions;
- category and usage badge;
- duplicate or parent-crop relationship;
- intended treatment;
- warning icon when classification confidence is low.
- for every reference, `SCOPES REVIEW REQUIRED`, `SCOPES none`, or the wrapped approved scope list.

Separate `must_use_exact`, `can_transform`, `reference_only`, and `ignore` into visibly distinct groups. Never bury a must-use omission inside a warning list.

## 7. Examples

- Product front PNG: `product_core` + `must_use_exact`.
- Hand-drawn sketch intended as tracing paper: `document_sketch` + `can_transform`.
- Screenshot demonstrating desired light falloff: `style_reference` + `reference_only` + `influenceScopes: ["lighting"]`.
- Brand logo SVG: `branding_asset` + `must_use_exact`.
- Duplicate compressed screenshot of the same product: `duplicate_or_unused` + `ignore`.

The last example applies only after an explicit user decision or in `default` classification. In `merge_all`, keep it visible and flagged until the first human gate resolves it.
