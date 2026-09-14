# Source Analysis

Scope: Explicit offline renderer operation or implementation. Enter through [Offline workflow](offline-workflow.md) for the local runtime contract.

Use this protocol before classification, layout, or style extraction. Its purpose is to preserve source truth while allowing controlled transformation.

## 1. Resolve the Role of Every File

Assign one primary role before assigning a manifest category:

| Source role | Meaning | Default preservation |
|---|---|---|
| `edit target` | The supplied subject must remain visibly and structurally the same in the result | High; normally `must_use_exact` |
| `content asset` | The file contributes visible scene content but may allow an approved transform | High or medium |
| `style reference` | Only composition, lighting, color, material, or visual rhythm may inform the result | Low; always `reference_only` |
| `supporting insert` | A supplied document, sketch, texture, or prop is intended as secondary visible content | Medium unless the user requires exact use |

When one file appears to serve two roles, split the roles explicitly or ask for review. Never let a `style reference` become visible scene content by convenience.

### Merge-all precedence

When the user's observable request is to combine the uploads into one image, begin with `integrationIntent: merge_all`. Unless the user explicitly identifies a file as a style reference or exclusion, treat it as content pending the first human gate. Every uploaded and approved content image must remain eligible for a visible, auditable contribution.

Use this precedence:

1. explicit user role or exclusion;
2. approved manifest correction;
3. merge-all conservation;
4. duplicate and filename heuristics as warnings only.

A filename or duplicate hash cannot silently reduce the visible count. A duplicate may be intentionally visible because the user supplied two files for two different physical carriers. A screenshot-looking file may be genuine content. Surface the warning and let the user decide. Explicit `reference_only` and `ignore` decisions remain non-visible and must not be counted as scene content.

## 2. Set Preservation Before Transformation

| Preservation | Protect | Allowed operations |
|---|---|---|
| High | identity, silhouette, geometry, component count, proportions, visible markings, approved colors | exact compositing, approved crop, scale, rotation, and integration shadow |
| Medium | recognizable structure and source relationship | crop, desaturation, paperization, sleeve, tracing, or other declared transform |
| Low | abstract visual rules only | derive new layout or material choices; do not copy source subject, wording, logo, or distinctive arrangement |

Map High to `must_use_exact` unless the user explicitly approves a derivative. Map Low style sources to `reference_only`. Record the decision in manifest notes and set `requiresHumanReview` when the role or preservation level is uncertain.

## 3. Keep an Evidence Ledger

Every important claim about an upload must carry one of these labels:

- `observed`: visible pixels or decoded file metadata directly support the claim;
- `user-supplied`: the user explicitly provided the fact or constraint;
- `inferred`: a bounded interpretation is being used and may be wrong;
- `unknown`: the evidence is absent or contradictory.

Never promote `inferred` to `observed`. Pixel width and height are not physical dimensions. A familiar-looking object is not proof of its model, material, age, manufacturer, or size.

## 4. Analyze References Without Copying Samples

Separate a reference set into:

- `fixed system`: recurring structural rules that define the requested visual language;
- `variable system`: choices that may change safely between scenes;
- `sample residue`: incidental text, subject matter, logos, exact marks, one-off positions, or artifacts unique to the examples.

Only the fixed system and bounded variable system may influence a new scene. Never reproduce sample residue unless the user separately supplies and approves it as content.

Return reference analysis in four blocks: observed evidence, fixed system, variable system, and excluded sample residue. State confidence limits when the examples are too few to distinguish a rule from an accident.

### Approve influence by axis

`reference_only` means grammar, not content. Record an explicit `influenceScopes` array using only `layout`, `palette`, `lighting`, `material`, `texture`, `typography`, and `motif`. Approve the narrowest axes supported by the user's instruction:

| User intent | Scope result | Boundary |
|---|---|---|
| “Only learn this spacing and hierarchy” | `layout` | Do not inherit color, type, material, subject, or exact arrangement |
| “Use this soft transmitted-light behavior” | `lighting` | Do not copy visible objects or palette unless separately approved |
| “Use this paper/acrylic relation” | `material`, possibly `texture` | Derive a material rule; do not paste the sample surface or source image |
| “Use only the composition of these two references” | `layout` | The references do not imply tools, archival labels, or workshop props |

Every VisualDirection rule must bind one approved asset/scope pair to observed or user-supplied evidence from that same asset. `unlisted influence axes are prohibited`; absence of a rule is not permission.

### Decide how visible content is embodied

For each approved visible content asset, apply `source truth → authorized transformation → representation → carrier → material/light behavior → evidence`. The source role says why a file is present; its representation says what that source becomes in this scene; its carrier says how the current renderer keeps it physically legible. Do not collapse those decisions into one style label.

- A transparent exact product or logo defaults to `exact_cutout` on `cutout` with `exact_source_layer` and source-preserved light behavior.
- Opaque source photographs stay visibly bounded. An opaque exact product or logo defaults to `source_photograph` on `physical_photo`; it cannot become an isolated object without a genuine transparent source.
- A transparent real tool or support asset may be `physical_object` only when it is approved visible content. Preserve the exact source layer and record its material as observed, user-supplied, or unknown.
- A sketch, diagram, or process image defaults to `source_photograph`. It may become `technical_drawing` or `tracing_overlay` only when its manifest usage is `can_transform` and explicit user-supplied evidence authorizes that semantic transformation.
- A material image defaults to `source_photograph`. It may become `material_field` only under the same explicit transformation authority.
- An ordinary photograph may remain `source_photograph`, or use `contact_print` or `film_transparency` when that carrier preserves recognizable source content and declares compatible opaque or transmissive behavior.
- A `relief_impression` is a derived interpretation, not a neutral texture treatment. It requires a `can_transform` source and explicit user-supplied transformation evidence.

Exact products, logos, and approved text remain exact. Unknown material stays `unknown` or `source_preserved`; unknown scale stays `unknown`. Neither missing fact permits invented dimensions, material identity, relief, or coordinates. Every representation records transformation and scale evidence tied to its source.

Style references receive no representation and never become carriers. The lightbox is the illumination and physical staging system, not a compulsory inventory. Tools are optional. A scene may contain only a product and one material field when that is the strongest truthful solution. Add a tool, drawing, carrier, or archive element only after the asset necessity test identifies a concrete information or hierarchy function.

If every usable upload is `reference_only` or `ignore`, stop Production before VisualDirection. An explicitly requested new concept may create only an offline `ConceptAssetBrief`. Any later candidate must be ingested as a new content asset, change the manifest hash, and repeat the first human approval before scene work.

## 5. Text Intent Gate

Before typesetting, classify every candidate string:

1. `subject_or_theme`: describes what the work is about; not authorized for display.
2. `approved_exact_copy`: supplied or explicitly approved for visible rendering.
3. `factual_metadata`: dates, dimensions, locations, IDs, prices, credits, or calls to action; use only when user-supplied and approved.
4. `generated_label`: prohibited by default; require explicit approval before it becomes exact copy.

Translations, invented titles, issue numbers, dates, coordinates, archival labels, and decorative characters are not implied by a theme. The final visible-text inventory must equal the approved allowlist.

## 6. Physical Dimensions and Prop Truth

For every scale-critical product or prop, record physical dimensions as one of:

- `user-supplied` measurement;
- decoded or authoritative asset metadata;
- a named reference standard;
- `inferred` estimate with a visible uncertainty note;
- `unknown`.

Do not infer millimeters from image pixels without a known scale reference. Do not use a category average as if it were the user's object. If dimensions are `unknown`, use a conservative relative scale for preview, flag it for approval, and report that the scene is visually plausible rather than physically calibrated.

Transparency is also source truth. `hasAlpha: false` forbids the `cutout` carrier. Preserve that source as a bounded physical photograph, contact print, film sleeve, or tracing sheet, or obtain a genuine transparent asset before isolating the subject. Do not erase or visually ignore the source background while continuing to claim exact compositing.

Generated props must have explicit relative scale, thickness, contact, and material behavior. A metal tool cannot transmit backlight; paper and film cannot share one thickness or shadow response; a prop cannot intersect a protected product or float without a contact cue.

## 7. Required Review Summary

Before the first approval gate, show for each asset:

- source role and preservation level;
- category and usage;
- observed, user-supplied, inferred, and unknown facts;
- approved visible text associated with it;
- physical-dimension status when scale matters;
- any conflict that requires human review.

For `merge_all`, also report the approved content count, the exact list that will become `requiredVisibleAssetIds`, and every explicit reference/exclusion that explains why an upload is not visible.
