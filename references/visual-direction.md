# Codex Visual Direction

Scope: Explicit offline renderer operation or implementation. Enter through [Offline workflow](offline-workflow.md) for the local runtime contract.

## Purpose

This protocol turns an imprecise request and classified user assets into an auditable visual-direction plan and a precise SceneSpec planning control.

`Codex is the visual-direction layer`. Codex inspects supplied files and, when available, actual preview pixels. It separates evidence from interpretation, selects a deliverable form, makes bounded composition judgments, finds or rejects insertion opportunities, and explains the cause of every visual move. The repository runtime supplies offline validation, persistence, deterministic scenes, and exact-layer output. A validator cannot certify taste.

`Blender is optional`. Missing Blender never blocks source analysis, brief normalization, placement planning, Three.js previews, deterministic compositing, or planning-control compilation. This Skill does not install a renderer, call an API, or treat a compiled control document as authorization to invoke an image model.

## Form Sanity and Task Grounding

Run a `form sanity` check before choosing a visual direction:

1. quote or preserve the user statement that fixes the deliverable;
2. identify what the viewer must understand or do;
3. record the viewing context and canvas;
4. test whether the proposed carrier can perform that action without an explanation from the author;
5. if form evidence is missing, choose the least-assumptive supported form and keep the uncertainty visible.

The supported pre-scene direction kinds are `generation-description` and `scene-preview`. A final image is produced only by the approved local final workflow after the independent scene approval; it is not a compiler direction kind. Do not promise HTML, video, Figma, Blender, or a remote render merely because another workflow uses it.

Before a new visual decision, freeze the current-task truth:

- the user's request verbatim;
- the classified `AssetManifest` and its canonical hash;
- required identity, approved visible text, and refusal list;
- observed, user-supplied, inferred, and unknown evidence;
- one subject cause, intended viewer effect, carrier reason, dominant material relation, and rejected generic alternative.

A style name, attractive reference, prior successful output, or model-written concept is not evidence for the current task by itself.

## Two-Pass Workflow

### Pass A: Direction Before Scene Generation

After asset classification and before scene generation, Codex must:

1. preserve the user's request verbatim;
2. run form sanity and separate deliverable intent from visible copy;
3. bind the direction to the current manifest hash;
4. lock exact, transformable, reference-only, and excluded assets;
5. write a closed `referenceInfluencePlan` using only manifest-approved axes;
6. write a closed `integrationPlan` that conserves the approved content count;
7. assign one evidence-bound representation to every visible source before choosing its carrier;
8. record every material claim as `observed`, `user-supplied`, `inferred`, or `unknown`;
9. define one evidence-backed visual system;
10. declare one strict evidence-bound `lightboxEnvironment` for the complete composition;
11. map occupied mass, negative space, focal competition, and reading path;
12. rank P0–P4 optimization actions separately from P3/P4 placement opportunities;
13. write `visual-direction.json` and compile it into a renderer-neutral planning control.

At this stage `reviewBasis` is `direction-plan`, every quality status is `pending`, and all scene/preview hashes are `null`. Planning rules do not prove that pixels are natural, restrained, unified, or physically plausible.

### Pass B: Pixel Review Before Scene Approval

After a preview exists, inspect the actual `preview pixels` rather than only scene JSON. Change `reviewBasis` to `preview-pixels`, bind `sceneId`, `sceneHash`, and `previewHash`, then evaluate:

- visual unity;
- component detail;
- texture scale;
- naturalness;
- restraint;
- reading flow;
- physical plausibility.

Each item becomes `pass`, `warning`, or `fail` with a concrete observation. Record these Codex judgments separately from deterministic validator findings. A `fail` blocks scene approval; a `warning` stays visible to the user.

Record the ten closed pixel hard failures separately in `hardFailures`: `NESTED_BACKGROUND_RECTANGLE`, `CORNER_THUMBNAIL_TEMPLATE`, `FLOATING_ASSET_PLANES`, `SINGLE_GENERIC_MATERIAL`, `PALETTE_FRAGMENTATION`, `NO_DOMINANT_MATERIAL_RELATION`, `REFERENCE_SCOPE_LEAKAGE`, `REPRESENTATION_AS_FLOATING_STICKER`, `LIGHTBOX_SPATIAL_RELATIONSHIP_LOST`, and `UNJUSTIFIED_ELEMENT_DOMINANCE`. Any non-empty `hardFailures` array derives overall `fail`; seven passing item scores cannot override it.

Persist that second-pass input with `previews review PROJECT_ID SCENE_ID --review FILE`. The workflow rereads the current scene, evidence record, and PNG bytes, derives the overall status, and stores `quality-review.json` beside `evidence.json`. The caller supplies no reviewer, timestamp, overall status, or evidence hash. A hash match proves which pixels were judged; it does not prove that the judgment is aesthetically correct.

## Convert Vague Requests Without Inventing Facts

Treat phrases such as “把这几个东西合成一个展览研究桌面”, “元素在这里”, or “我要一个更高级的档案感” as intent, not complete instructions.

Compile them in this order:

1. **Deliverable:** supported kind, description, viewer action, viewing context, pixel dimensions, aspect ratio, and orientation.
2. **Subject hierarchy:** hero, supporting assets, references, exclusions, and exact-use locks.
3. **Spatial evidence:** normalized region only when there is a user markup, user coordinate, observed negative-space finding, or explicitly labeled inferred option.
4. **Visual system:** camera, hierarchy, component detail, texture scale, material behavior, lighting, palette, and edge/shadow behavior.
5. **Visible text:** exact strings tied to user-supplied approval evidence. A theme, translation, filename, date, coordinate, issue number, or generated label is not approved copy.
6. **Negative constraints:** identity drift, reference leakage, clutter, impossible contact, unapproved text, and renderer-specific failures.
7. **Unknowns:** missing dimensions, hidden surfaces, uncertain material, ambiguous pointing words, or unclear asset roles remain explicit.

Do not fabricate millimetres, focal lengths, product materials, dates, weights, collection numbers, historical facts, or brand copy to make a request sound precise.

## Manifest-Bound Reference Influence

References are grammar-only evidence. Every `reference_only` asset must have an explicit first-gate `influenceScopes` array drawn from the closed set `layout`, `palette`, `lighting`, `material`, `texture`, `typography`, and `motif`. A missing field means a legacy record awaiting renewed human review; `[]` means no approved influence. Neither state makes the source visible.

VisualDirection v6 retains `referenceInfluencePlan`. Each entry contains exactly:

- `assetId`: one manifest asset whose usage is `reference_only`;
- `scope`: one axis present in that asset's approved `influenceScopes`;
- `rule`: a concrete abstract instruction, never source pixels or sample residue;
- `evidenceId`: an `observed` or `user-supplied` record whose `sourceAssetIds` includes that reference.

Reject unknown axes, duplicate asset/scope pairs, evidence from another asset, inferred evidence presented as permission, and any integration assignment or visible object sourced from a reference. `unlisted influence axes are prohibited`. Permission for `layout` does not imply palette, typography, material, motif, texture, or lighting.

Before any direction work, require at least one approved `product_core` + `must_use_exact` content asset. When all usable files are reference-only or ignored, stop Production and emit no VisualDirection, compiled control, BuildSceneRequest, SceneSpec, preview, or final. If the user separately requests a new concept, produce only the offline `ConceptAssetBrief`; ingest any later candidate as new content, recompute the manifest hash, and return to the first human approval.

## Merge-All Integration Plan

Interpret an unqualified request to “combine these uploads into one image” as `merge_all`. This means every uploaded and approved content image has one visible, auditable contribution; it does not mean every file receives equal area or becomes a full rectangular thumbnail. Explicit style references and exclusions remain outside the visible scene.

The closed `integrationPlan` contains:

- `mode`: `merge_all` or an explicitly requested `curated` subset;
- `intentEvidenceId`: user-supplied evidence for the integration decision;
- `requiredVisibleAssetIds`: exactly all approved content IDs in `merge_all`;
- `layoutFamily`: the count-aware family required for the approved content count;
- `overflowPolicy`: always `adapt_or_block`;
- `minimumVisibleShortEdgePx`: the legibility floor that must survive the final canvas;
- `assignments`: exactly one per required ID, each with `hero`, `secondary`, or `supporting` hierarchy plus a truthful carrier and non-unknown evidence;
- `materialRelation`: one dominant material, bounded supporting materials, and the physical/light/contact relationship connecting them;
- `layoutRouting`: one evidence-backed surface style, the actual routing signals, and three candidate-specific composition grammars.

There must be exactly one hero and it must match `composition.heroAssetId`. Use `cutout` only for a decoded transparent source. An opaque exact hero must be a `physical_photo`; other opaque content may use `physical_photo`, `contact_print`, `film_sleeve`, or `tracing_sheet` when allowed by its preservation contract. If the requested visual treatment needs isolation but no true cutout exists, block or obtain one; never pretend the original background rectangle is the isolated product.

The supported adaptive families are `1 asset`, `2–6 assets`, `7–16 assets`, and `17–40 assets`. The renderer changes hierarchy, scale, carrier, crop, and reading order across these families while preserving every required contribution. More than 40 approved content assets or a layout that cannot meet its minimum visible size must block rather than omit, repeat, or create tiny stamps.

## Source Representation Contract

VisualDirection v6 resolves every approved visible source in this order: `source truth → authorized transformation → representation → carrier → material/light behavior → evidence`.

Each integration assignment has exactly one `representation` with:

- `kind`: `physical_object`, `source_photograph`, `technical_drawing`, `material_field`, `contact_print`, `film_transparency`, `tracing_overlay`, `relief_impression`, or `exact_cutout`;
- a closed `form`, `materialFamily`, `renderStrategy`, and `lightBehavior` compatible with the carrier;
- `transformationEvidenceId` tied to that source;
- `scaleEvidenceId` plus `scaleEvidenceStatus`, which may remain `unknown`;
- a non-empty rationale explaining why this embodiment is truthful and useful.

Use these defaults unless stronger evidence authorizes another closed choice:

| Source truth | Default representation | Boundary |
|---|---|---|
| transparent exact product or logo | `exact_cutout` | preserve the exact source layer, silhouette, markings, and approved colors |
| opaque exact product or logo | `source_photograph` | keep the source visibly bounded on `physical_photo`; obtain a genuine cutout before isolation |
| transparent real tool or support asset | `physical_object` when it is approved visible content | keep its exact source identity; a tool is never inferred from a visual style |
| sketch, diagram, or process image | `source_photograph` | `technical_drawing` or `tracing_overlay` requires `can_transform` plus explicit user-supplied authority |
| material image | `source_photograph` | `material_field` requires `can_transform` plus explicit user-supplied authority |
| ordinary photograph | `source_photograph`, `contact_print`, or `film_transparency` | preserve recognizable source content and choose only a carrier whose light behavior is declared truthfully |

`relief_impression` is also a derived representation and requires the same explicit authority. A transformation cannot be authorized by an observed resemblance, a filename, a reference composition, or Codex taste. Exact products, logos, and approved text remain exact. `references receive no representation`; their only permitted effect is an approved abstract rule in `referenceInfluencePlan`. `tools are optional`: both sparse and populated soft-light-table scenes are valid, and no workshop inventory is implied by the lightbox form.

Unknown material remains `materialFamily: unknown` or `source_preserved`. Unknown scale remains `scaleEvidenceStatus: unknown`; neither state permits invented dimensions or coordinates. The current renderer continues to use the truthful carrier and exact source layer for pixels. Representation metadata does not claim that unsupported three-dimensional geometry, relief, material physics, or a new source asset was synthesized.

## Adaptive Layout Routing

VisualDirection v6 requires one closed `layoutRouting` object. `layoutFamily` remains the count-based capacity contract; it is not the visual design. Read [Layout routing](layout-routing.md), inspect the approved upload set, choose one shared `surfaceStyle`, record only the `selectionSignals` that caused the choice, and create exactly one candidate for each supported template.

Each candidate contains `templateId`, `archetype`, `density`, `alignment`, `scaleRhythm`, rationale, and its own complete grammar. The three signatures must differ so the previews test materially different modern compositions rather than seed variations. Count compatibility, archetype alignment, and required group/flow relationships are closed schema rules. EDC-like `modular_inventory` is available when the sources truly form an inventory; it is not a universal fallback.

The shared surface style keeps palette, light, and material direction stable while layout candidates vary. It does not recolor exact assets or collapse distinct material responses. References may influence only their approved abstract scopes; their pixels, labels, brands, wording, subjects, and object choices remain unavailable.

## Authored Composition Grammar

Every VisualDirection v6 route requires one closed `compositionGrammar` inside its candidate. Its decision order is `source representation → hero event → groups → rooted links → reading order → negative space → executable geometry`. The grammar is `rooted` and `relative-only`: it records authorship and topology without claiming absolute position evidence.

The grammar contains exactly:

- `rootAssetId`: the single integration hero;
- `flow`: `horizontal`, `vertical`, `diagonal_descending`, `diagonal_ascending`, or `radial`;
- `readingOrder`: every required visible source exactly once, beginning with the root;
- `groups`: a complete partition using `hero_event`, `support_cluster`, `evidence_band`, or `material_bridge`;
- `links`: one parent-child relationship for every non-root source, with the parent earlier in reading order;
- `negativeSpace`: one `single_breathing_field`, `directional_channel`, or `perimeter_relief` strategy anchored to a visible source.

Each group has a stable ID, one role, an arrangement (`singular`, `paired`, `linear`, `staggered`, or `constellation`), a contiguous source list, and a purpose. Exactly one group is a singleton `hero_event` containing the root. Every other source belongs to one group only. A group describes a meaningful optical or evidentiary unit, not a generic card container.

Each link uses one relative axis (`right`, `left`, `below`, `above`, `diagonal_down`, or `diagonal_up`), contact (`separated`, `edge_touch`, or `shallow_overlap`), spacing (`tight`, `regular`, or `open`), and purpose. Edge touch and shallow overlap require tight spacing. Shallow overlap cannot involve the hero and authorizes only that named parent-child pair; it cannot become a global overlap exemption.

The grammar rejects `x`, `y`, `region`, dimensions, millimetres, unknown vocabulary, duplicate membership, disconnected sources, backwards links, a second root, and links into the hero. Confirmed user markup or user coordinates remain the only absolute focal/supporting evidence. The deterministic builder may solve open regions from the relative grammar, but it must not relabel those solved coordinates as user-supplied.

Source count changes density and group structure, not truth. One source may remain a sparse product-led event. Two to six sources form an authored connected cluster. Seven to sixteen may use evidence bands and material bridges. Seventeen to forty may use multiple contiguous groups under one rooted reading path. `tools are optional`: no tool is implied by a soft-light table, and a tool appears only when it is an approved visible source with a necessary role.

## Unified Lightbox Environment

VisualDirection v6 contains exactly one strict `lightboxEnvironment`. It is the renderer-neutral source of truth for `one coherent soft-light field`; every approved visible source shares its camera, emitter relationship, falloff, surface, and contact system while retaining its own material response.

Choose one closed mode from the subject and authorized representation plan:

- `diffused_softbox`: the table emitter is inactive and broad top fill is active; use it for opaque, diffuse, or reflective subject-led scenes.
- `transmitted_light_table`: the table emitter is active and top fill is inactive; use it when film, tracing layers, or another transmissive source is the dominant visual cause.
- `hybrid_diffused_table`: table emission and top fill are both active; use it when transmissive and opaque materials must coexist in the same field.

The record also fixes an orthographic camera and restrained tilt, active/inactive emitter state with intensity and temperature, radial edge falloff, a frosted-acrylic surface with transmission/roughness/diffuser layers, and material-specific contact-shadow controls. Mode and emitter states must agree. Every `evidenceIds` entry must resolve to non-`unknown` current-task evidence; the environment cannot contain placement coordinates, millimetres, hidden regions, or inferred physical calibration.

The material-response catalog is complete and immutable:

| Family | Optical model | Render strategy | Contact behavior |
|---|---|---|---|
| metal | `opaque_reflective` | `native_material` | `defined` |
| paper | `opaque_diffuse` | `native_material` | `soft` |
| tracing paper | `translucent` | `native_material` | `soft` |
| film | `transmissive` | `native_material` | `minimal` |
| acrylic/glass | `refractive_highlight` | `native_material` | `minimal` |
| protected source | `source_preserved` | `exact_2d_layer` | `source_alpha` |

Do not apply one generic plastic material, one global texture, or one identical shadow to all families. Exact products, logos, and approved text remain exact source pixels. If the current renderer cannot represent a declared native response, stop that scene; for protected identity layers, retain the exact two-dimensional source layer. Never hide a renderer mismatch behind an approximate fallback.

### Deictic location rule

`regionEvidence` is one of:

- `user-markup` — an arrow, mask, box, or annotated image supplied by the user;
- `user-coordinate` — an explicit point or bounded region supplied by the user;
- `observed-negative-space` — Codex observed a candidate gap in an actual image;
- `inferred-option` — Codex proposes a candidate that has not been confirmed;
- `unresolved` — “here”, “there”, “this side”, or similar language has no locatable evidence.

Each value cites an evidence record with the matching status. `unresolved` requires `region: null` and `confirmation: unresolved`. It is a hard error to convert unsupported “here” language into coordinates. Observed and inferred regions stay `candidate`; only user markup or coordinates can support a confirmed region.

## Evidence-Backed Visual System

The direction record specifies:

| Field | Required decision |
|---|---|
| camera | top-down or near-orthographic relation, crop, and perspective restraint |
| hierarchy | one primary focal level and bounded secondary/tertiary levels |
| component detail | supporting silhouette, label, contrast, and internal-detail budget relative to the hero |
| texture scale | material-specific grain or structure that remains credible at final output size |
| materials | distinct paper, film, metal, acrylic, glass, textile, wood, or product behavior |
| lighting | backlight/top-light relation, temperature, highlight restraint, and contact behavior |
| palette | dominant neutrals, limited accents, and exact colors that cannot drift |
| edge and shadow | edge acuity, shadow direction, softness, height, and integration |
| evidenceIds | the non-unknown records that caused these choices |

Uniform noise is not unity. Paper, metal, glass, film, textile, and the product retain distinct transmission, roughness, thickness, texture scale, and shadow behavior while sharing one camera, light field, hierarchy, and output treatment.

## Asset Necessity and Placement

Run an `asset necessity test` before proposing any addition: remove it mentally. If the viewer loses no information, identity, approved atmosphere role, scale cue, linkage, balance, or material transition, reject it.

Inspect the full frame:

1. occupied mass and existing support;
2. intentional versus unresolved negative space;
3. reading path and where it stops or jumps;
4. focal competition;
5. semantic adjacency;
6. physical contact and shadow support;
7. survival at final output size.

A placement opportunity is only P3 or P4. It contains:

- a stable ID and bounded normalized region;
- `regionEvidence`, evidence ID, and candidate/confirmed state;
- the element and functional purpose;
- `subject cause`, `viewer effect`, and removal impact;
- an anchor target and relation;
- minimum gap, maximum overlap, and contact mode;
- a structured relative scale range;
- material and orientation range;
- confidence and rejection constraints.

“Put something in the empty corner” is not a cause. An empty placement list is valid. Remove the lowest-value element before adding another when the frame already has competing focal points, inconsistent textures, floating objects, leaked reference content, or exhausted safe area.

Annotations are instructions, not final content. A red arrow, selection box, mask, crop guide, or markup can locate a region but must not appear in the final image unless separately classified as visible content.

### Sparse-space triage

For one-to-six visible sources, classify every materially large empty field before proposing an insert:

- `functional_breathing_space` — the field has a named job in the reading path, product isolation, approved copy channel, motion direction, or material/light transition;
- `recoverable_by_recomposition` — the field reads as accidental because the existing group is underscaled, disconnected, or optically displaced;
- `supplement_candidate` — the existing approved sources are already well-scaled, connected, and balanced, yet the subject still lacks a useful evidentiary, material, or atmospheric link.

The required order is `recompose before supplement`. Repair `recoverable_by_recomposition` as P1: scale or regroup existing approved sources and bring the weighted optical centroid toward the safe-field center. Estimate visual weight from occupied area, contrast, opacity, and semantic hierarchy rather than from box count. Do not mechanically center every object and do not destroy an evidenced asymmetric reading channel. Coordinates produced by the deterministic solver remain solver geometry, not retroactive user-coordinate evidence.

Only a residual `supplement_candidate` may create a P3/P4 placement opportunity. Before execution, present no more than three ranked options in user-facing language: proposed element, subject cause, viewer effect, carrier/material, approximate candidate area, relative scale, and removal impact. Nothing is inserted without explicit user selection. If selection requires a new exact or transformable source, ingest that source, change the manifest hash, and return to the first human approval before building a new preview batch.

## Optimization Priority

Use `optimizationActions` for existing defects and required corrections:

| Priority | Meaning | Typical action |
|---|---|---|
| `P0` | preservation or blocking truth | restore an exact asset, remove leaked reference content or unapproved text, keep unsupported coordinates unresolved |
| `P1` | hierarchy and composition | establish the hero, reduce focal competition, repair reading path, recover necessary negative space |
| `P2` | scale, contact, material, and texture unity | correct size relationships, intersections, floating objects, shadows, material response, or texture scale |
| `P3` | useful supporting content | add one justified sketch, tool, document, sleeve, frame, connector, or scale cue |
| `P4` | optional micro-detail | add a restrained detail only when it survives output scale and has approval/evidence |

Never use P3/P4 additions to hide unresolved P0–P2 defects. `placementOpportunities` accepts only P3/P4; lower-priority repairs belong in `optimizationActions`.

## Quality Review Order

Review in this order:

1. exact identity, source truth, reference leakage, and visible text;
2. subject specificity and dominant material relation;
3. visual unity, hero hierarchy, negative space, and reading flow;
4. component detail and texture scale;
5. naturalness and restraint;
6. physical plausibility;
7. deterministic geometry, hash, bounds, and overflow checks.

Deterministic checks can reject concrete defects. They cannot self-approve taste.

## Closed Direction Record

Use [the example](../assets/visual-direction.example.json) as the exact field contract. The top-level record contains:

```text
version
projectId
manifestHash
sourceRequest
deliverable
canvas
approvedVisibleText
assetLocks
referenceInfluencePlan
integrationPlan
evidence
designRationale
visualSystem
composition
optimizationActions
placementOpportunities
qualityReview
negativeConstraints
unknowns
```

Unknown fields are rejected. Asset lock groups are mutually exclusive. Every `unknown` claim appears in `unknowns`. Approved text cites user-supplied evidence containing the exact string. Production compilation requires the current manifest and workflow so the compiler checks canonical hash, project ownership, asset IDs, runtime roles, current phase, and the persisted human manifest approval:

```bash
python3 <skill-dir>/scripts/compile_generation_description.py \
  /path/to/visual-direction.json \
  --manifest /path/to/manifest.json \
  --workflow /path/to/workflow.json \
  --output /path/to/generation-description.txt
```

The compiler uses only the Python standard library, performs no network/model call, and never edits the source records. Missing either required input fails before stdout or output-file creation. The result identifies itself as a `SceneSpec planning control document` and explicitly states that it does not constitute image-generation authorization.

## Deterministic Scene Bridge

After compiler validation and the persisted manifest approval, pass the same record to `visualDirectionToBuildSceneRequest`. The bridge rechecks the boundary-critical fields at runtime and carries these into `BuildSceneRequest` and `SceneSpec`:

The workflow input must include the current hash-bound `manifestApproval`
receipt, not only `manifestApprovedAt`. The bridge records its canonical
`manifestApprovalHash`; scene approval later binds that receipt hash together
with the visual-direction, scene, and validation hashes.

- canonical manifest and visual-direction hashes;
- exact, transformable, reference-only, and excluded asset-role groups;
- manifest-approved reference scope checks plus the full VisualDirection hash that binds `referenceInfluencePlan`;
- the count-bound `integrationPlan`, `requiredVisibleAssetIds`, evidence-bound source representations, truthful carrier assignments, and `adapt_or_block` policy;
- the hero asset and its region evidence ID;
- every confirmed supporting cutout, its user evidence ID, bounded region, and deterministic rotation;
- the exact approved-visible-text allowlist without inventing text boxes;
- the manifest-approval timestamp and `sceneApprovalRequired: true`.

Only `user-markup` or `user-coordinate` with `confirmation: confirmed` is executable geometry. `unresolved` preserves `region: null`; observed, inferred, and unconfirmed user regions remain candidates. In those cases construction stops with `Focal placement requires confirmed user location evidence` and writes no scene. A confirmed region that cannot satisfy the safe margin is rejected rather than silently shifted.

The v2 bridge preserves approved copy as an allowlist and does not turn it into positioned `textBlocks`. It also does not turn a candidate `placementOpportunity` into a transformed source asset or generated semantic proxy. A supporting opportunity becomes executable only when confirmed user-markup or user-coordinate evidence identifies exactly one transparent `supporting_prop` whose manifest usage is `can_transform`. The bridge fits that source cutout inside the confirmed region, uses the deterministic midpoint of the approved orientation range, records it in `directionConstraints.supportingPlacements`, and suppresses generated props that would claim the same role. Opaque, ambiguous, repeated, observed, inferred, unresolved, and unconfirmed mappings remain non-executable.

The direction bridge does not persist either approval on the user's behalf. It requires the first persisted approval before building, and the workflow still requires a separate validation-backed human scene approval before final rendering.

The deterministic chain is `VisualDirection → BuildSceneRequest → SceneSpec`. It preserves the canonical manifest hash, all four asset-role sets, every representation and location evidence ID, approved English copy exactly, `manifestApprovalHash`, and `sceneApprovalRequired: true`. An unresolved location remains coordinate-free and cannot reach `SceneSpec` geometry.

Boundary failures use a closed machine-readable vocabulary:

- `REFERENCE_SCOPE_VIOLATION`: reference influence exceeds its manifest-approved scope or evidence.
- `REPRESENTATION_UNSUPPORTED`: the requested source representation is outside the supported vocabulary or violates source-truth authority.
- `MATERIAL_FORM_MISMATCH`: representation form, carrier, optical behavior, transparency, or renderer material response is incompatible.
- `UNJUSTIFIED_GENERATED_ELEMENT`: a confirmed insert lacks exactly one approved transparent supporting source and user location evidence.
- `LIGHTBOX_ENVIRONMENT_MISSING`: the required coherent soft-light-box environment is absent.

The compiler prints the same code and CLI/API surfaces return it unchanged. These errors stop scene creation; they do not authorize a fallback representation, generated prop, material, or environment.

## Planning Control Contract

The compiled description contains, in order:

1. generation goal, verbatim request boundary, and manifest hash;
2. deliverable form, viewer action, viewing context, and carrier reason;
3. subject cause, viewer effect, dominant relation, and rejected generic alternative;
4. canvas and camera;
5. exact/transformable/reference-only/excluded asset rules;
6. approved reference influence rules and every prohibited axis;
7. merge-all or curated integration count, assignments, carriers, and material relation;
8. hero, evidenced or unresolved focal placement, mass, negative space, density, and reading path;
9. optimization actions ordered P0–P4;
10. placement opportunities ordered P3/P4;
11. unified component, texture, material, light, palette, and shadow instructions;
12. evidence boundaries and approved visible text;
13. direction-plan or preview-pixels quality status plus hard failures;
14. negative constraints and unresolved unknowns.

The control is renderer-neutral and exists only to feed the approved deterministic SceneSpec path. Do not add provider parameters, model syntax, or a direct generation fallback.

## Reject These Outputs

Reject and revise when:

- the proposed carrier conflicts with the user's deliverable or viewing task;
- exact assets are replaced by prose approximations or redraws;
- a raw theme appears as visible text without approval evidence;
- an insert has no subject cause, viewer effect, removal impact, or bounded evidenced region;
- unsupported “here” language becomes a coordinate;
- all empty space is treated as a defect;
- the same grain, shadow, or gloss is applied to every material;
- supporting detail competes with the hero;
- measurements or factual metadata are inferred from pixels;
- a style reference contributes visible sample residue;
- lack of Blender is described as a blocker;
- a direction plan claims `pass` before preview pixels exist;
- a preview review lacks scene and preview hashes.
- `merge_all` omits, repeats, or hides an approved content asset;
- all uploads become equal corner thumbnails or disconnected floating planes;
- a central source rectangle is nested inside a larger generic background without a physical carrier relationship;
- an opaque source is presented as an isolated cutout;
- one generic material treatment flattens distinct sources, the palette fragments, or no dominant material relation is visible;
- the approved content count cannot meet the minimum visible size and the system tries to continue instead of blocking.
- a reference influences an axis missing from its manifest scope list;
- all usable uploads are reference-only or ignored and the workflow attempts direction, scene, preview, or final production;
- the compiler is invoked without the current manifest and human-approved workflow receipt;
- a planning control is treated as a direct image-generation prompt.
