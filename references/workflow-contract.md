# Workflow Contract

Scope: Operation or implementation of the separate local renderer project. In this document, CLI means the renderer package `@lightbox/cli`. Its prerequisites and command environment are described in [Renderer CLI](../CLI.md#renderer-cli). Enter through [Local renderer workflow](offline-workflow.md) for the runtime contract.

## Contents

1. State machine
2. Approval records
3. Artifact layout
4. CLI contract
5. Blocking conditions
6. Recovery rules

## 1. State Machine

Use these phases only:

```text
created
→ assets_ingested
→ manifest_review
→ manifest_approved
→ scenes_generated
→ preview_ready
→ scene_approved
→ final_rendered
```

Do not skip phases. Reclassifying assets invalidates downstream scene approval. Changing scene geometry, text, material, lighting, template, or seed invalidates scene approval and final artifacts.
Changing a reference `influenceScopes` list changes the canonical manifest hash and therefore invalidates the first approval, VisualDirection, every scene, and the second approval.

## 2. Approval Records

Persist approvals as data, not chat inference.

The runtime stores the first record as `WorkflowState.manifestApproval` and the
second as `WorkflowState.sceneApproval` in the same atomic workflow-state write
as each phase transition. Legacy summary timestamps remain readable for
recovery, but they are not production approval receipts.

### Manifest approval

```json
{
  "kind": "asset_manifest",
  "projectId": "project_001",
  "manifestHash": "sha256:...",
  "approvedAt": "2026-08-04T09:00:00Z",
  "approvedBy": "human"
}
```

### Scene approval

```json
{
  "kind": "scene",
  "projectId": "project_001",
  "sceneId": "scene_archive_731",
  "manifestHash": "sha256:...",
  "manifestApprovalHash": "sha256:...",
  "visualDirectionHash": "sha256:...",
  "sceneHash": "sha256:...",
  "validationHash": "sha256:...",
  "previewHash": "sha256:...",
  "previewEvidenceHash": "sha256:...",
  "previewQualityReviewHash": "sha256:...",
  "approvedAt": "2026-08-04T09:20:00Z",
  "approvedBy": "human"
}
```

Reject an approval when its referenced hash no longer matches the current artifact.
Before final rendering, recompute the canonical manifest, manifestApproval,
SceneSpec, and ValidationReport hashes and compare the direction hash recorded
by both the scene and sceneApproval. Re-read the selected preview bytes and
recompute both `previewHash` and `previewEvidenceHash`. Do this before opening a render server.
Re-read `quality-review.json`, recompute `previewQualityReviewHash`, and verify that its scene, preview, and evidence hashes still match. A missing or failing review blocks the second human approval; a warning remains in workflow state for that decision.

### Preview evidence

`PreviewEvidenceRecord` binds a direction-aware SceneSpec to one persisted PNG:

- exact URI: `project://PROJECT_ID/previews/SCENE_ID/preview.png`;
- canonical `sceneHash`;
- hash and byte length of the bytes re-read from storage;
- 1600×2000 or 3200×4000 dimensions;
- renderer identifier `three-playwright-v1`.

The record proves which pixels were reviewed, not that the composition is good. The separate Codex `preview-pixels` review still evaluates all seven visual qualities.

### Preview quality review

`PreviewQualityReviewRecord` persists a Codex-authored judgment with `reviewedBy: codex`. It contains exactly seven concrete observations: visual unity, component detail, texture scale, naturalness, restraint, reading flow, and physical plausibility. It also contains the closed `hardFailures` array for nested background rectangles, corner-thumbnail templates, floating asset planes, one generic material, palette fragmentation, and a missing dominant material relation. Runtime code derives the overall pass/warning/fail status and binds the record to the current `sceneHash`, `previewHash`, and `previewEvidenceHash`; any hard failure forces `fail`. Runtime code verifies the record but does not perform visual judgment.

## 3. Artifact Layout

```text
DATA_ROOT/PROJECT_ID/
├─ uploads/
├─ derivatives/
│  ├─ thumbnails/
│  ├─ cutouts/
│  └─ normalized/
├─ manifest/
│  ├─ asset-manifest.json
│  ├─ contact-sheet.png
│  └─ approval.json
├─ scenes/
│  └─ SCENE_ID/
│     ├─ scene.json
│     ├─ validation.json
│     ├─ preview.png
│     ├─ issues.png
│     └─ approval.json
├─ controls/
│  ├─ background.png
│  ├─ depth.png
│  ├─ exact-assets-mask.png
│  └─ enhancement-prompt.txt
└─ exports/
   ├─ final.png
   ├─ exact-layer-map.json
   └─ export-metadata.json
```

## 4. CLI Contract

Stable exit codes:

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Invalid command or input |
| `2` | Workflow gate or blocking validation |
| `3` | Processing failure |

Required non-interactive commands:

```text
lightbox project create PROJECT_ID --data-root DATA_ROOT --json
lightbox ingest PROJECT_ID INPUT_DIRECTORY --data-root DATA_ROOT --json
lightbox classify PROJECT_ID --hints HINTS_JSON --data-root DATA_ROOT --json
lightbox manifest approve PROJECT_ID --data-root DATA_ROOT --json
lightbox scenes build PROJECT_ID --templates archive_research_v1,product_focus_v1,art_lab_v1 --seed 731 --visual-direction VISUAL_DIRECTION_JSON --data-root DATA_ROOT --json
lightbox previews render PROJECT_ID --scene-ids SCENE_ID_A,SCENE_ID_B,SCENE_ID_C --data-root DATA_ROOT --json
lightbox previews review PROJECT_ID SCENE_ID --review REVIEW_JSON --data-root DATA_ROOT --json
lightbox scene validate PROJECT_ID SCENE_ID --data-root DATA_ROOT --json
lightbox scene approve PROJECT_ID SCENE_ID --data-root DATA_ROOT --json
lightbox render final PROJECT_ID --data-root DATA_ROOT --json
```

The CLI must never prompt interactively. Human confirmation occurs in the calling interface; the caller invokes approval commands only after explicit user approval.

The portable planning compiler is also non-interactive and requires both current records:

```text
compile_generation_description.py VISUAL_DIRECTION_JSON --manifest MANIFEST_JSON --workflow WORKFLOW_JSON
```

It accepts only a workflow phase carrying a current human `manifestApproval` whose project, timestamp, and manifest hash match. It emits a SceneSpec planning control rather than image-generation authorization. Failure writes neither stdout content nor an output file.

## 5. Blocking Conditions

Block approval or final rendering for:

- `TEXT_OVERFLOW`
- `TEXT_TOO_SMALL`
- `OBJECT_OUT_OF_BOUNDS`
- `REQUIRED_ASSET_MISSING`
- `DUPLICATE_REQUIRED_USAGE`
- `PRODUCT_OCCLUDED`
- invalid or stale approval hashes
- undecodable or unsafe uploads
- missing deterministic renderer output
- missing, stale, or failing `PreviewQualityReviewRecord`
- a `reference_only` asset with missing `influenceScopes`
- a reference influence outside its approved closed scope list
- no `product_core` + `must_use_exact` content asset
- any all-reference/all-ignore attempt to create VisualDirection, a planning control, SceneSpec, preview, or final

Warnings may proceed only when they do not contradict the user brief or exact-layer rules.

## 6. Recovery Rules

- Asset change: return to `manifest_review`.
- Manifest change after approval: invalidate all scenes and approvals.
- Concept-only request with reference inputs: keep Production stopped; ingest the separately created candidate as a new content asset and return to `manifest_review`.
- Scene change after approval: invalidate scene approval and final artifacts.
- Enhancer failure: keep deterministic final; do not block export.
- Exact-layer composite failure: block export.
- Missing fonts: use an approved fallback or request a font choice; do not change line breaks silently.
