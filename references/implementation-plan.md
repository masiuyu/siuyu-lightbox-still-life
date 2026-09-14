# Siuyu Lightbox Still Life MVP Implementation Plan

Scope: Explicit offline renderer operation or implementation. Enter through [Offline workflow](offline-workflow.md) for the local runtime contract.

> **PREBUILT SKILL PACKAGE:** The canonical `siuyu-lightbox-still-life` skill is already bundled with this plan. In Task 17, copy the installed skill directory into the repository, preserve its `agents/`, `references/`, `scripts/`, and `assets/` contents, then add or adapt repository-local tests. Do not rewrite the skill from memory.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Codex-first, portable skill and local web application that accepts many uploaded visual assets, classifies their intended use, creates deterministic low-poly light-table scenes, blocks invalid scenes, requests human approval, and only then produces a final render or an optional AI-enhancement bundle.

**Architecture:** Use a TypeScript ESM monorepo with framework-independent domain packages. `AssetManifest`, `SceneSpec`, `ValidationReport`, and `WorkflowState` are the system of record. Three.js produces a deterministic, physically inspired preview from low-poly geometry and explicit light/material parameters; Playwright captures reproducible render layers; Sharp composites exact user assets and exact typography after any optional enhancement. External models, storage backends, cutout services, and image enhancers are adapters and are never imported by core packages.

**Tech Stack:** Node.js 24 LTS, pnpm workspaces, TypeScript strict mode, Vite + React, Fastify, Zod 4, Three.js, Sharp, Playwright Chromium, Vitest, ESLint, Docker.

## Global Constraints

- Use Node.js `24.x` and declare `engines.node: ">=24 <25"` at the repository root.
- Use pnpm workspaces without Turborepo or Nx in the MVP.
- Use ESM only: every package sets `"type": "module"` and TypeScript uses `moduleResolution: "Bundler"` for browser packages and `"NodeNext"` for Node packages.
- Enable `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, and `noImplicitOverride`.
- `SceneSpec` is the single source of truth for preview, validation, final export, and enhancement control assets.
- Required product images, logos, museum/reference images marked `must_use_exact`, and all exact text must never be redrawn by an image model.
- Style references marked `reference_only` must never appear as scene objects.
- A scene with a `blocking` validation issue cannot be approved or rendered as final.
- The same input manifest, template, and seed must produce byte-equivalent `SceneSpec` JSON.
- Preview generation must work without an API key or network access.
- Final deterministic export must work without an API key or network access.
- AI enhancement is optional and only runs after an explicit persisted approval record.
- Core packages must not import React, Fastify, OpenAI SDKs, cloud storage SDKs, or browser globals.
- User uploads are untrusted: validate MIME, decoded dimensions, pixel count, file size, and output paths before processing.
- Do not silently shrink text below the configured minimum font size; produce `TEXT_TOO_SMALL` or `TEXT_OVERFLOW`.
- Do not silently drop a `must_use_exact` asset; produce `REQUIRED_ASSET_MISSING`.
- Use generated image fixtures rather than committing copyrighted reference images.
- Every task uses test-first development and ends with a focused commit.

## Scope Decision

This plan treats the previous single-file HTML demo as a visual reference only. The available demo directory contains built artifacts but no source repository, package manifest, tests, or Git history. Start a greenfield repository and copy no implementation code from that demo.

## Repository Map

```text
lightbox-archive/
├─ AGENTS.md
├─ README.md
├─ package.json
├─ pnpm-lock.yaml
├─ pnpm-workspace.yaml
├─ tsconfig.base.json
├─ eslint.config.js
├─ .env.example
├─ .gitignore
├─ Dockerfile
├─ apps/
│  ├─ api/
│  │  ├─ package.json
│  │  ├─ tsconfig.json
│  │  └─ src/
│  │     ├─ server.ts
│  │     ├─ app.ts
│  │     └─ routes/
│  │        ├─ projects.ts
│  │        ├─ assets.ts
│  │        ├─ scenes.ts
│  │        └─ exports.ts
│  ├─ web/
│  │  ├─ package.json
│  │  ├─ vite.config.ts
│  │  ├─ tsconfig.json
│  │  └─ src/
│  │     ├─ main.tsx
│  │     ├─ App.tsx
│  │     ├─ api/client.ts
│  │     ├─ state/project-store.ts
│  │     ├─ components/
│  │     └─ steps/
│  └─ cli/
│     ├─ package.json
│     └─ src/index.ts
├─ packages/
│  ├─ schema/
│  ├─ storage/
│  ├─ testing-fixtures/
│  ├─ asset-ingestion/
│  ├─ asset-classifier/
│  ├─ text-engine/
│  ├─ scene-builder/
│  ├─ validator/
│  ├─ render-three/
│  ├─ final-compositor/
│  ├─ enhancer-contract/
│  └─ workflow/
├─ skills/
│  └─ siuyu-lightbox-still-life/
│     ├─ SKILL.md
│     ├─ references/
│     │  ├─ scene-schema.md
│     │  ├─ material-presets.md
│     │  └─ acceptance-checklist.md
│     └─ scripts/
│        ├─ ingest.sh
│        ├─ preview.sh
│        └─ final.sh
├─ docs/
│  ├─ architecture.md
│  └─ superpowers/plans/2026-08-04-siuyu-lightbox-still-life-mvp.md
└─ tests/
   └─ e2e/lightbox-workflow.spec.ts
```

---

### Task 1: Bootstrap the Portable Codex Workspace

**Files:**
- Create: `package.json`
- Create: `pnpm-workspace.yaml`
- Create: `tsconfig.base.json`
- Create: `eslint.config.js`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `AGENTS.md`
- Create: `README.md`
- Create: `apps/web/package.json`
- Create: `apps/api/package.json`
- Create: `apps/cli/package.json`
- Create: one `package.json` for every package listed in the repository map
- Test: `packages/schema/src/bootstrap.test.ts`

**Interfaces:**
- Consumes: no prior interfaces.
- Produces: pnpm workspace package names, strict TypeScript configuration, root scripts, Codex repository instructions.

- [ ] **Step 1: Write the failing workspace smoke test**

Create `packages/schema/src/bootstrap.test.ts`:

```ts
import { describe, expect, it } from "vitest";

describe("workspace bootstrap", () => {
  it("runs tests through the shared Vitest toolchain", () => {
    expect(process.versions.node.split(".")[0]).toBe("24");
  });
});
```

- [ ] **Step 2: Run the test and verify the workspace is not configured**

Run:

```bash
corepack enable
corepack prepare pnpm@10 --activate
pnpm test
```

Expected: failure because the root package, workspace packages, and `test` script do not exist.

- [ ] **Step 3: Create the root configuration**

Use this root `package.json`:

```json
{
  "name": "lightbox-archive",
  "private": true,
  "type": "module",
  "packageManager": "pnpm@10.0.0",
  "engines": { "node": ">=24 <25" },
  "scripts": {
    "build": "pnpm -r build",
    "dev": "pnpm --parallel --filter @lightbox/api --filter @lightbox/web dev",
    "lint": "eslint .",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:e2e": "playwright test",
    "typecheck": "pnpm -r typecheck",
    "verify": "pnpm lint && pnpm typecheck && pnpm test && pnpm build"
  },
  "devDependencies": {
    "@eslint/js": "latest",
    "@playwright/test": "latest",
    "@types/node": "latest",
    "eslint": "latest",
    "typescript": "latest",
    "typescript-eslint": "latest",
    "vitest": "latest"
  }
}
```

Use this `pnpm-workspace.yaml`:

```yaml
packages:
  - apps/*
  - packages/*
```

Use this `tsconfig.base.json`:

```json
{
  "compilerOptions": {
    "target": "ES2023",
    "lib": ["ES2023", "DOM", "DOM.Iterable"],
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }
}
```

Every package must use the naming convention `@lightbox/<directory-name>`. Browser packages use `moduleResolution: "Bundler"`; Node packages use `module: "NodeNext"` and `moduleResolution: "NodeNext"`.

- [ ] **Step 4: Add Codex execution rules**

Create `AGENTS.md` with these binding rules:

```md
# Repository Instructions

1. Read the active task in `docs/superpowers/plans/2026-08-04-siuyu-lightbox-still-life-mvp.md` before changing code.
2. Work on one numbered task at a time.
3. Write the failing test first and run it before implementation.
4. Do not import app frameworks or vendor SDKs into domain packages.
5. Preserve exact user assets and exact text; image enhancement never owns those layers.
6. Run the task-specific test, then `pnpm typecheck`, before committing.
7. Do not change public schemas without updating schema tests and generated JSON Schema files.
8. Do not bypass approval or blocking validation gates.
9. Do not add a dependency when the behavior can be implemented in fewer than 40 clear lines.
10. Report changed files, verification commands, and unresolved risks after each task.
```

- [ ] **Step 5: Install dependencies and verify the smoke test**

Run:

```bash
pnpm install
pnpm test packages/schema/src/bootstrap.test.ts
pnpm typecheck
```

Expected: one passing test and no type errors.

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "chore: bootstrap portable lightbox workspace"
```

---

### Task 2: Define the Shared Schemas and JSON Schema Exports

**Files:**
- Create: `packages/schema/src/asset.ts`
- Create: `packages/schema/src/scene.ts`
- Create: `packages/schema/src/validation.ts`
- Create: `packages/schema/src/workflow.ts`
- Create: `packages/schema/src/index.ts`
- Create: `packages/schema/src/schema.test.ts`
- Create: `packages/schema/src/export-json-schema.ts`
- Generate: `packages/schema/generated/asset-manifest.schema.json`
- Generate: `packages/schema/generated/scene-spec.schema.json`
- Generate: `packages/schema/generated/validation-report.schema.json`
- Generate: `packages/schema/generated/workflow-state.schema.json`

**Interfaces:**
- Consumes: root TypeScript and Vitest configuration.
- Produces: `AssetManifest`, `SceneSpec`, `ValidationReport`, `WorkflowState`, their Zod schemas, and JSON Schema documents.

- [ ] **Step 1: Write failing schema tests**

Create `packages/schema/src/schema.test.ts` with tests that assert:

```ts
import { describe, expect, it } from "vitest";
import {
  AssetManifestSchema,
  SceneSpecSchema,
  ValidationReportSchema,
  WorkflowStateSchema,
} from "./index.js";

const manifest = {
  version: 1,
  projectId: "project_demo",
  assets: [
    {
      assetId: "asset_product",
      fileName: "product.png",
      originalUri: "project://uploads/product.png",
      mimeType: "image/png",
      width: 1200,
      height: 1200,
      sha256: "a".repeat(64),
      category: "product_core",
      usage: "must_use_exact",
      needsCutout: false,
      allowGenerativeRedraw: false,
      status: "ready",
      tags: ["hero"],
    },
  ],
};

describe("shared schemas", () => {
  it("accepts a valid exact product manifest", () => {
    expect(AssetManifestSchema.parse(manifest)).toEqual(manifest);
  });

  it("rejects a reference-only asset placed in a scene", () => {
    const scene = {
      version: 1,
      sceneId: "scene_a",
      projectId: "project_demo",
      seed: 42,
      templateId: "archive_research_v1",
      canvas: { width: 1600, height: 2000, pixelRatio: 1 },
      lightbox: {
        intensity: 900,
        temperatureKelvin: 4700,
        edgeFalloff: 0.18,
        diffuserRoughness: 0.72,
        frameDepth: 28,
      },
      objects: [
        {
          id: "object_reference",
          kind: "asset_plane",
          sourceAssetId: "asset_reference",
          placementMode: "reference_hidden",
          materialId: "photo_print",
          transform: { x: 0.5, y: 0.5, z: 0.1, width: 0.2, height: 0.2, rotationDeg: 0 },
          exactLayer: false,
          locked: false,
        },
      ],
      textBlocks: [],
      constraints: { safeMargin: 0.03, maxOverlapRatio: 0.18, minReadableFontPx: 18 },
    };
    expect(() => SceneSpecSchema.parse(scene)).toThrow();
  });

  it("accepts a blocking validation report", () => {
    const report = {
      version: 1,
      sceneId: "scene_a",
      status: "fail",
      issues: [
        {
          code: "REQUIRED_ASSET_MISSING",
          targetId: "asset_product",
          severity: "blocking",
          message: "Required asset asset_product is not placed.",
        },
      ],
      metrics: { overlapScore: 0, outOfBoundsCount: 0, requiredAssetCoverage: 0 },
    };
    expect(ValidationReportSchema.parse(report)).toEqual(report);
  });

  it("prevents final rendering before approval", () => {
    const state = {
      version: 1,
      projectId: "project_demo",
      phase: "preview_ready",
      approvedSceneId: null,
      manifestApprovedAt: null,
      sceneApprovedAt: null,
    };
    expect(WorkflowStateSchema.parse(state).phase).toBe("preview_ready");
  });
});
```

- [ ] **Step 2: Run tests and verify imports fail**

```bash
pnpm test packages/schema/src/schema.test.ts
```

Expected: failure because the schemas do not exist.

- [ ] **Step 3: Implement the schemas**

Use Zod string enums for these exact values:

```ts
export const AssetCategorySchema = z.enum([
  "product_core",
  "document_sketch",
  "artifact_reference",
  "branding_asset",
  "style_reference",
  "supporting_prop",
  "duplicate_or_unused",
]);

export const AssetUsageSchema = z.enum([
  "must_use_exact",
  "can_transform",
  "reference_only",
  "ignore",
]);
```

`SceneSpecSchema` must use normalized `x`, `y`, `width`, and `height` values in `[0, 1]`; `z` is a non-negative world-space number. Reject `placementMode: "reference_hidden"` inside `objects` with a `.superRefine()` issue. Define `WorkflowState.phase` as:

```ts
z.enum([
  "created",
  "assets_ingested",
  "manifest_review",
  "manifest_approved",
  "scenes_generated",
  "preview_ready",
  "scene_approved",
  "final_rendered",
]);
```

- [ ] **Step 4: Export Draft 2020-12 JSON Schema**

Create `packages/schema/src/export-json-schema.ts`:

```ts
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import * as z from "zod";
import {
  AssetManifestSchema,
  SceneSpecSchema,
  ValidationReportSchema,
  WorkflowStateSchema,
} from "./index.js";

const outputs = [
  ["asset-manifest.schema.json", AssetManifestSchema],
  ["scene-spec.schema.json", SceneSpecSchema],
  ["validation-report.schema.json", ValidationReportSchema],
  ["workflow-state.schema.json", WorkflowStateSchema],
] as const;

const outputDir = resolve("packages/schema/generated");
await mkdir(outputDir, { recursive: true });
for (const [fileName, schema] of outputs) {
  const path = resolve(outputDir, fileName);
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, `${JSON.stringify(z.toJSONSchema(schema, { target: "draft-2020-12" }), null, 2)}\n`);
}
```

Add package scripts: `build`, `typecheck`, and `schema:export`.

- [ ] **Step 5: Verify schemas and deterministic generated output**

```bash
pnpm --filter @lightbox/schema schema:export
cp packages/schema/generated/scene-spec.schema.json /tmp/scene-spec.schema.json
pnpm --filter @lightbox/schema schema:export
diff -u /tmp/scene-spec.schema.json packages/schema/generated/scene-spec.schema.json
pnpm test packages/schema/src/schema.test.ts
pnpm --filter @lightbox/schema typecheck
```

Expected: no diff, four passing tests, no type errors.

- [ ] **Step 6: Commit**

```bash
git add packages/schema
git commit -m "feat: define portable lightbox schemas"
```

---

### Task 3: Implement Local Project Storage Behind Portable Interfaces

**Files:**
- Create: `packages/storage/src/types.ts`
- Create: `packages/storage/src/local-storage.ts`
- Create: `packages/storage/src/project-repository.ts`
- Create: `packages/storage/src/index.ts`
- Create: `packages/storage/src/local-storage.test.ts`

**Interfaces:**
- Consumes: schema types from `@lightbox/schema`.
- Produces: `BlobStore`, `ProjectRepository`, `LocalBlobStore`, `LocalProjectRepository`.

- [ ] **Step 1: Write failing storage tests**

```ts
import { mkdtemp, readFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { LocalBlobStore, LocalProjectRepository } from "./index.js";

it("rejects path traversal and stores project-relative blobs", async () => {
  const root = await mkdtemp(join(tmpdir(), "lightbox-storage-"));
  const store = new LocalBlobStore(root);
  await expect(store.put("../escape.txt", Buffer.from("bad"))).rejects.toThrow("Unsafe storage key");
  const record = await store.put("project_a/uploads/image.png", Buffer.from("png"));
  expect(record.uri).toBe("project://project_a/uploads/image.png");
  expect(await readFile(join(root, "project_a/uploads/image.png"), "utf8")).toBe("png");
});

it("round-trips typed project documents atomically", async () => {
  const root = await mkdtemp(join(tmpdir(), "lightbox-repo-"));
  const repository = new LocalProjectRepository(root);
  const state = {
    version: 1 as const,
    projectId: "project_a",
    phase: "created" as const,
    approvedSceneId: null,
    manifestApprovedAt: null,
    sceneApprovedAt: null,
  };
  await repository.writeWorkflowState(state);
  expect(await repository.readWorkflowState("project_a")).toEqual(state);
});
```

- [ ] **Step 2: Run tests and verify missing storage classes**

```bash
pnpm test packages/storage/src/local-storage.test.ts
```

Expected: failure because `LocalBlobStore` and `LocalProjectRepository` do not exist.

- [ ] **Step 3: Implement safe interfaces and local adapters**

Define:

```ts
export interface BlobStore {
  put(key: string, bytes: Uint8Array): Promise<{ uri: string; byteLength: number }>;
  get(uri: string): Promise<Uint8Array>;
  exists(uri: string): Promise<boolean>;
}

export interface ProjectRepository {
  writeManifest(manifest: AssetManifest): Promise<void>;
  readManifest(projectId: string): Promise<AssetManifest | null>;
  writeScene(scene: SceneSpec): Promise<void>;
  readScene(projectId: string, sceneId: string): Promise<SceneSpec | null>;
  writeValidation(report: ValidationReport): Promise<void>;
  writeWorkflowState(state: WorkflowState): Promise<void>;
  readWorkflowState(projectId: string): Promise<WorkflowState | null>;
}
```

`LocalBlobStore` must reject absolute paths, `..`, NUL bytes, empty path segments, and Windows drive prefixes. `LocalProjectRepository` writes to a temporary file and renames it into place so interrupted writes do not leave partial JSON.

- [ ] **Step 4: Verify storage behavior**

```bash
pnpm test packages/storage/src/local-storage.test.ts
pnpm --filter @lightbox/storage typecheck
```

Expected: two passing tests.

- [ ] **Step 5: Commit**

```bash
git add packages/storage
git commit -m "feat: add portable local project storage"
```

---

### Task 4: Generate Safe Test Assets and Ingest User Images

**Files:**
- Create: `packages/testing-fixtures/src/create-image-fixtures.ts`
- Create: `packages/testing-fixtures/src/index.ts`
- Create: `packages/asset-ingestion/src/ingest.ts`
- Create: `packages/asset-ingestion/src/image-probe.ts`
- Create: `packages/asset-ingestion/src/contact-sheet.ts`
- Create: `packages/asset-ingestion/src/index.ts`
- Create: `packages/asset-ingestion/src/ingest.test.ts`

**Interfaces:**
- Consumes: `BlobStore`, `AssetItem`, Node `File`-equivalent input `{ fileName, mimeType, bytes }`.
- Produces: `ingestAssets(input): Promise<AssetManifest>`, thumbnails, SHA-256 deduplication metadata, and a numbered contact-sheet PNG.

- [ ] **Step 1: Write failing ingestion tests**

```ts
import { mkdtemp } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { LocalBlobStore } from "@lightbox/storage";
import { createImageFixtures } from "@lightbox/testing-fixtures";
import { ingestAssets } from "./index.js";

it("decodes images, hashes content, and marks exact duplicates", async () => {
  const fixtures = await createImageFixtures();
  const root = await mkdtemp(join(tmpdir(), "lightbox-ingest-"));
  const manifest = await ingestAssets({
    projectId: "project_a",
    files: [fixtures.productPng, { ...fixtures.productPng, fileName: "copy.png" }],
    blobStore: new LocalBlobStore(root),
    limits: { maxBytes: 10_000_000, maxPixels: 20_000_000 },
  });
  expect(manifest.assets).toHaveLength(2);
  expect(manifest.assets[0]?.width).toBe(512);
  expect(manifest.assets[1]?.duplicateOfAssetId).toBe(manifest.assets[0]?.assetId);
});

it("rejects a declared PNG that cannot be decoded", async () => {
  const root = await mkdtemp(join(tmpdir(), "lightbox-ingest-bad-"));
  await expect(
    ingestAssets({
      projectId: "project_a",
      files: [{ fileName: "bad.png", mimeType: "image/png", bytes: Buffer.from("not-png") }],
      blobStore: new LocalBlobStore(root),
      limits: { maxBytes: 10_000_000, maxPixels: 20_000_000 },
    }),
  ).rejects.toThrow("Image decode failed");
});
```

- [ ] **Step 2: Run tests and verify ingestion is absent**

```bash
pnpm test packages/asset-ingestion/src/ingest.test.ts
```

Expected: failure because fixture generation and ingestion are absent.

- [ ] **Step 3: Implement generated fixtures**

Use Sharp to generate these assets at runtime:

```ts
const productPng = await sharp({
  create: { width: 512, height: 512, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } },
})
  .composite([{ input: Buffer.from('<svg width="512" height="512"><circle cx="256" cy="256" r="140" fill="#c8a64b"/></svg>') }])
  .png()
  .toBuffer();
```

Generate a transparent product, opaque sketch, cyanotype, logo, and two byte-identical duplicate files. Return `{ fileName, mimeType, bytes }` objects.

- [ ] **Step 4: Implement ingestion**

The function must:

1. Check declared MIME against `image/png`, `image/jpeg`, and `image/webp`.
2. Check bytes before decode.
3. Decode with Sharp and read width, height, channels, and alpha.
4. Reject missing dimensions and excessive pixel count.
5. Hash original bytes with SHA-256.
6. Assign stable asset IDs as `asset_${sha256.slice(0, 16)}`; append `_2`, `_3` for duplicate records while setting `duplicateOfAssetId`.
7. Store original and a 320-pixel thumbnail.
8. Initialize category as `duplicate_or_unused` for duplicates and `supporting_prop` for unique files; initialize usage as `ignore` for duplicates and `can_transform` for unique files.

Also implement `renderContactSheet(manifest, resolveThumbnail)` using Sharp. It outputs a 1600-pixel-wide PNG with numbered 280×280 thumbnail cells, filename, category, usage, and a visible `EXACT`, `REFERENCE`, or `IGNORE` status. Text is rendered through SVG with XML escaping and fixed bounds; filenames longer than 32 code points are truncated with an ellipsis.

- [ ] **Step 5: Verify ingestion, contact-sheet, and security cases**

```bash
pnpm test packages/asset-ingestion/src/ingest.test.ts
pnpm --filter @lightbox/asset-ingestion typecheck
```

Expected: two passing tests.

- [ ] **Step 6: Commit**

```bash
git add packages/testing-fixtures packages/asset-ingestion
git commit -m "feat: ingest and deduplicate uploaded assets"
```

---

### Task 5: Classify Assets with Rules First and an Optional Adapter Contract

**Files:**
- Create: `packages/asset-classifier/src/types.ts`
- Create: `packages/asset-classifier/src/rule-classifier.ts`
- Create: `packages/asset-classifier/src/apply-classification.ts`
- Create: `packages/asset-classifier/src/index.ts`
- Create: `packages/asset-classifier/src/rule-classifier.test.ts`

**Interfaces:**
- Consumes: `AssetManifest` and explicit user hints.
- Produces: `ClassificationSuggestion[]`, `AssetClassifierAdapter`, updated manifest after user acceptance.

- [ ] **Step 1: Write failing classification tests**

```ts
import { expect, it } from "vitest";
import { classifyWithRules } from "./index.js";

it("keeps explicit product and style-reference instructions separate", () => {
  const suggestions = classifyWithRules({
    assets: [
      { assetId: "a1", fileName: "product-front.png", hasAlpha: true, duplicateOfAssetId: null },
      { assetId: "a2", fileName: "lighting-reference.jpg", hasAlpha: false, duplicateOfAssetId: null },
    ],
    userHints: [
      { assetId: "a1", role: "product", required: true },
      { assetId: "a2", role: "style_reference", required: false },
    ],
  });
  expect(suggestions[0]).toMatchObject({ category: "product_core", usage: "must_use_exact", allowGenerativeRedraw: false });
  expect(suggestions[1]).toMatchObject({ category: "style_reference", usage: "reference_only" });
});

it("never promotes an exact duplicate to required use", () => {
  const suggestions = classifyWithRules({
    assets: [{ assetId: "a2", fileName: "copy.png", hasAlpha: true, duplicateOfAssetId: "a1" }],
    userHints: [],
  });
  expect(suggestions[0]).toMatchObject({ category: "duplicate_or_unused", usage: "ignore" });
});
```

- [ ] **Step 2: Run tests and verify classifier is absent**

```bash
pnpm test packages/asset-classifier/src/rule-classifier.test.ts
```

- [ ] **Step 3: Implement the classifier contract**

```ts
export interface AssetClassifierAdapter {
  suggest(input: ClassifierInput): Promise<ClassificationSuggestion[]>;
}

export interface ClassificationSuggestion {
  assetId: string;
  category: AssetCategory;
  usage: AssetUsage;
  needsCutout: boolean;
  allowGenerativeRedraw: boolean;
  confidence: number;
  reasons: string[];
}
```

The rule classifier uses explicit hints first, duplicate status second, alpha and filename tokens third. It does not inspect brand identity or infer protected facts. An optional model adapter can be added later without changing the contract.

- [ ] **Step 4: Implement explicit user acceptance**

`applyClassification(manifest, acceptedSuggestions)` must reject suggestions for unknown asset IDs and must not alter original dimensions, hash, or URI.

- [ ] **Step 5: Verify classification**

```bash
pnpm test packages/asset-classifier/src/rule-classifier.test.ts
pnpm --filter @lightbox/asset-classifier typecheck
```

- [ ] **Step 6: Commit**

```bash
git add packages/asset-classifier
git commit -m "feat: classify assets with portable rule engine"
```

---

### Task 6: Build a Deterministic Text Fitting Engine

**Files:**
- Create: `packages/text-engine/src/types.ts`
- Create: `packages/text-engine/src/wrap.ts`
- Create: `packages/text-engine/src/fit.ts`
- Create: `packages/text-engine/src/index.ts`
- Create: `packages/text-engine/src/fit.test.ts`

**Interfaces:**
- Consumes: text, text box dimensions, font metrics adapter.
- Produces: `TextLayoutResult` with fitted lines or explicit overflow status.

- [ ] **Step 1: Write failing text tests**

```ts
import { expect, it } from "vitest";
import { fitText } from "./index.js";

const metrics = {
  measure: (text: string, fontSizePx: number) => text.length * fontSizePx * 0.5,
};

it("shrinks and wraps text without exceeding box dimensions", () => {
  const result = fitText({
    text: "ARCHIVE FIELD STUDY",
    box: { widthPx: 180, heightPx: 54 },
    style: { maxFontSizePx: 24, minFontSizePx: 14, lineHeight: 1.2, maxLines: 2 },
    metrics,
  });
  expect(result.status).toBe("fit");
  if (result.status === "fit") {
    expect(result.lines.length).toBeLessThanOrEqual(2);
    expect(result.heightPx).toBeLessThanOrEqual(54);
  }
});

it("returns overflow instead of rendering unreadable text", () => {
  const result = fitText({
    text: "A VERY LONG TECHNICAL ARCHIVAL LABEL THAT CANNOT FIT",
    box: { widthPx: 40, heightPx: 20 },
    style: { maxFontSizePx: 18, minFontSizePx: 16, lineHeight: 1.2, maxLines: 1 },
    metrics,
  });
  expect(result).toEqual({ status: "overflow", reason: "minimum_font_size_exceeded" });
});
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pnpm test packages/text-engine/src/fit.test.ts
```

- [ ] **Step 3: Implement fitting**

Implement greedy word wrapping for whitespace-delimited text and per-character wrapping for text without whitespace. Iterate font sizes from maximum to minimum in one-pixel steps. Return a `fit` result only when width, total line height, and max-line constraints all pass.

- [ ] **Step 4: Verify text fitting**

```bash
pnpm test packages/text-engine/src/fit.test.ts
pnpm --filter @lightbox/text-engine typecheck
```

- [ ] **Step 5: Commit**

```bash
git add packages/text-engine
git commit -m "feat: add deterministic text fitting engine"
```

---

### Task 7: Generate Deterministic Scene Layouts from Approved Manifests

**Files:**
- Create: `packages/scene-builder/src/prng.ts`
- Create: `packages/scene-builder/src/templates.ts`
- Create: `packages/scene-builder/src/build-scene.ts`
- Create: `packages/scene-builder/src/index.ts`
- Create: `packages/scene-builder/src/build-scene.test.ts`
- Create: `packages/testing-fixtures/src/domain-fixtures.ts`
- Modify: `packages/testing-fixtures/src/index.ts`

**Interfaces:**
- Consumes: approved `AssetManifest`, `BuildSceneRequest` with template and seed.
- Produces: deterministic `SceneSpec` variants.

- [ ] **Step 1: Add domain fixtures and write failing scene-builder tests**

Create `packages/testing-fixtures/src/domain-fixtures.ts` with an approved manifest containing these stable IDs: `asset_product`, `asset_sketch`, `asset_artifact`, `asset_style_reference`, and `asset_logo`. Export `approvedManifestFixture()` as a new deep-cloned object on every call. Export `validSceneFixture()` with `asset_product`, `asset_sketch`, `asset_artifact`, and `asset_logo` placed inside the safe margin; never place `asset_style_reference`.

Then create the failing tests:

```ts
import { expect, it } from "vitest";
import { buildScene } from "./index.js";
import { approvedManifestFixture } from "@lightbox/testing-fixtures";

it("produces identical JSON for the same seed", () => {
  const input = { manifest: approvedManifestFixture(), templateId: "archive_research_v1" as const, seed: 731 };
  expect(buildScene(input)).toEqual(buildScene(input));
});

it("places every must-use asset and never places reference-only assets", () => {
  const manifest = approvedManifestFixture();
  const scene = buildScene({ manifest, templateId: "product_focus_v1", seed: 42 });
  const placed = new Set(scene.objects.flatMap((object) => object.sourceAssetId ? [object.sourceAssetId] : []));
  for (const asset of manifest.assets) {
    if (asset.usage === "must_use_exact") expect(placed.has(asset.assetId)).toBe(true);
    if (asset.usage === "reference_only") expect(placed.has(asset.assetId)).toBe(false);
  }
});
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pnpm test packages/scene-builder/src/build-scene.test.ts
```

- [ ] **Step 3: Implement the seeded PRNG and three templates**

Implement `mulberry32(seed)` locally. Define these templates:

- `archive_research_v1`: one large tracing-paper diagram, one hero product, one kraft folder, two to four secondary documents, two low-poly tools.
- `product_focus_v1`: product occupies 24–32% of canvas area; supporting documents remain outside a 6% protected halo.
- `art_lab_v1`: more overlapping translucent sheets, but the maximum requested overlap remains 18%.

Placement order is exact products, artifact references, transformable documents, generated props, then text. Rotations for paper are within `[-4, 4]` degrees; one optional tool may rotate within `[-18, 18]` degrees.

- [ ] **Step 4: Serialize scenes canonically**

Add `canonicalizeScene(scene)` that sorts object arrays by `zIndex` and then `id`, rounds normalized values to six decimals, and removes no fields. The workflow stores canonical output.

- [ ] **Step 5: Verify determinism**

```bash
pnpm test packages/scene-builder/src/build-scene.test.ts
pnpm --filter @lightbox/scene-builder typecheck
```

- [ ] **Step 6: Commit**

```bash
git add packages/scene-builder packages/testing-fixtures
git commit -m "feat: build deterministic lightbox scenes"
```

---

### Task 8: Validate Required Assets, Bounds, Overlap, Occlusion, and Text

**Files:**
- Create: `packages/validator/src/geometry.ts`
- Create: `packages/validator/src/rules.ts`
- Create: `packages/validator/src/validate-scene.ts`
- Create: `packages/validator/src/index.ts`
- Create: `packages/validator/src/validate-scene.test.ts`

**Interfaces:**
- Consumes: `SceneSpec`, approved `AssetManifest`, measured text results.
- Produces: `ValidationReport` and a boolean `canApproveScene(report)`.

- [ ] **Step 1: Write failing validator tests**

```ts
import { expect, it } from "vitest";
import { validateScene, canApproveScene } from "./index.js";
import { approvedManifestFixture, validSceneFixture } from "@lightbox/testing-fixtures";

it("blocks a scene missing a required product", () => {
  const scene = validSceneFixture();
  scene.objects = scene.objects.filter((object) => object.sourceAssetId !== "asset_product");
  const report = validateScene({ scene, manifest: approvedManifestFixture(), textLayouts: new Map() });
  expect(report.issues).toContainEqual(expect.objectContaining({ code: "REQUIRED_ASSET_MISSING", severity: "blocking" }));
  expect(canApproveScene(report)).toBe(false);
});

it("reports out-of-bounds and excessive overlap separately", () => {
  const scene = validSceneFixture();
  scene.objects[0]!.transform.x = 0.99;
  scene.objects[1]!.transform = { ...scene.objects[0]!.transform };
  const report = validateScene({ scene, manifest: approvedManifestFixture(), textLayouts: new Map() });
  expect(report.issues.some((issue) => issue.code === "OBJECT_OUT_OF_BOUNDS")).toBe(true);
  expect(report.issues.some((issue) => issue.code === "EXCESSIVE_OVERLAP")).toBe(true);
});
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pnpm test packages/validator/src/validate-scene.test.ts
```

- [ ] **Step 3: Implement geometry rules**

Use axis-aligned bounding boxes after rotating each rectangle's four corners and computing its world-aligned envelope. Calculate overlap area divided by the smaller object's area. Ignore intentional overlap only when the upper object's `allowOverlapWith` includes the lower object ID.

- [ ] **Step 4: Implement validation severity**

Use these severities:

- `REQUIRED_ASSET_MISSING`, `TEXT_OVERFLOW`, `REFERENCE_ASSET_PLACED`, and `PRODUCT_OCCLUDED` above 35%: `blocking`.
- `OBJECT_OUT_OF_BOUNDS`, `TEXT_TOO_SMALL`, and `EXCESSIVE_OVERLAP`: `high`.
- Product occlusion from 15% through 35%: `medium`.

`canApproveScene` returns false for `blocking` or `high` issues.

- [ ] **Step 5: Verify validator**

```bash
pnpm test packages/validator/src/validate-scene.test.ts
pnpm --filter @lightbox/validator typecheck
```

- [ ] **Step 6: Commit**

```bash
git add packages/validator
git commit -m "feat: block invalid lightbox scenes"
```

---

### Task 9: Build Low-Poly Geometry and Material Presets in Three.js

**Files:**
- Create: `packages/render-three/src/types.ts`
- Create: `packages/render-three/src/materials.ts`
- Create: `packages/render-three/src/geometry/paper.ts`
- Create: `packages/render-three/src/geometry/folder.ts`
- Create: `packages/render-three/src/geometry/tools.ts`
- Create: `packages/render-three/src/lightbox.ts`
- Create: `packages/render-three/src/create-scene.ts`
- Create: `packages/render-three/src/index.ts`
- Create: `packages/render-three/src/materials.test.ts`

**Interfaces:**
- Consumes: `SceneSpec`, an `AssetTextureResolver` that returns object URLs or texture sources.
- Produces: Three.js `Scene`, orthographic camera, renderer controller, material factory, low-poly prop meshes.

- [ ] **Step 1: Write failing material tests**

```ts
import { expect, it } from "vitest";
import { createMaterialDescriptor } from "./index.js";

it("keeps paper, film, metal, and acrylic physically distinct", () => {
  expect(createMaterialDescriptor("tracing_paper")).toMatchObject({ transmission: 0.42, roughness: 0.88, metalness: 0 });
  expect(createMaterialDescriptor("film_sleeve")).toMatchObject({ transmission: 0.78, roughness: 0.28, metalness: 0 });
  expect(createMaterialDescriptor("metal_tool")).toMatchObject({ transmission: 0, roughness: 0.34, metalness: 0.92 });
  expect(createMaterialDescriptor("acrylic")).toMatchObject({ transmission: 0.9, thickness: 0.6 });
});
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pnpm test packages/render-three/src/materials.test.ts
```

- [ ] **Step 3: Implement explicit material descriptors**

Create a pure-data material descriptor first, then map it to `MeshStandardMaterial` or `MeshPhysicalMaterial`. Use these initial presets:

```ts
const presets = {
  kraft_paper: { color: "#b89462", roughness: 0.94, metalness: 0, transmission: 0, thickness: 0.8 },
  tracing_paper: { color: "#eef0e7", roughness: 0.88, metalness: 0, transmission: 0.42, thickness: 0.12 },
  photo_print: { color: "#ffffff", roughness: 0.58, metalness: 0, transmission: 0.03, thickness: 0.18 },
  film_sleeve: { color: "#f2f7f2", roughness: 0.28, metalness: 0, transmission: 0.78, thickness: 0.08 },
  metal_tool: { color: "#72787a", roughness: 0.34, metalness: 0.92, transmission: 0, thickness: 1.2 },
  acrylic: { color: "#f3f8f5", roughness: 0.16, metalness: 0, transmission: 0.9, thickness: 0.6 },
  cutout_object: { color: "#ffffff", roughness: 0.5, metalness: 0, transmission: 0, thickness: 0.35 },
} as const;
```

- [ ] **Step 4: Implement the physically inspired light table**

Use:

1. An emissive diffuser plane with a radial falloff shader driven by `intensity`, `temperatureKelvin`, and `edgeFalloff`.
2. A dark low-poly frame with actual depth.
3. A `RectAreaLight` above the surface for readable metal and acrylic reflections.
4. Per-object contact-shadow planes generated from object bounds, thickness, and material transmission because Three.js rectangular area lights do not cast shadows.
5. An orthographic camera with a configurable 1.2-degree tilt to prevent a flat UI appearance.

Do not claim path-traced physical accuracy. Name the mode `physical_inspired_webgl` in render metadata.

- [ ] **Step 5: Implement low-poly props**

Use primitive geometry only:

- Folder: two thin boxes plus a tab.
- Envelope: thin box plus triangular flap.
- Scissors: two torus segments, two blade boxes, one pivot cylinder.
- Magnifier: torus, thin cylinder handle, transmissive lens disk.
- Ruler: thin box with procedural tick texture.

- [ ] **Step 6: Verify material tests and type safety**

```bash
pnpm test packages/render-three/src/materials.test.ts
pnpm --filter @lightbox/render-three typecheck
```

- [ ] **Step 7: Commit**

```bash
git add packages/render-three
git commit -m "feat: add low-poly lightbox rendering primitives"
```

---

### Task 10: Render Reviewable Previews and Capture Visual Regression Images

**Files:**
- Create: `apps/web/src/render-host.ts`
- Create: `apps/web/src/render-entry.tsx`
- Create: `apps/web/src/render.css`
- Create: `packages/render-three/src/controller.ts`
- Create: `tests/e2e/preview-render.spec.ts`
- Create: `playwright.config.ts`

**Interfaces:**
- Consumes: canonical `SceneSpec`, asset URLs.
- Produces: visible browser preview, transparent exact-layer mode, deterministic Playwright screenshot.

- [ ] **Step 1: Write a failing Playwright test**

```ts
import { expect, test } from "@playwright/test";

test("renders a stable archive preview without overflow markers", async ({ page }) => {
  await page.goto("/render-test?fixture=archive_research_v1");
  await page.waitForFunction(() => document.body.dataset.renderState === "ready");
  await expect(page.locator("[data-validation=blocking]")).toHaveCount(0);
  await expect(page.locator("canvas")).toHaveScreenshot("archive-research-v1.png", {
    animations: "disabled",
    maxDiffPixelRatio: 0.015,
  });
});
```

- [ ] **Step 2: Run the test and verify the route is missing**

```bash
pnpm exec playwright install chromium
pnpm test:e2e tests/e2e/preview-render.spec.ts
```

Expected: failure because the web app and test route do not exist.

- [ ] **Step 3: Implement the render host**

The route `/render-test` loads generated fixtures, creates the Three.js renderer at 800×1000 CSS pixels with device scale factor 1, sets deterministic color management, waits for every texture, renders twice, and sets `document.body.dataset.renderState = "ready"`.

- [ ] **Step 4: Add renderer debug overlays**

Support query parameter `debug=1` to render object IDs, bounds, safe margin, and validation issue markers as HTML overlays. These overlays are excluded in normal preview screenshots.

- [ ] **Step 5: Approve the first golden image intentionally**

Run:

```bash
pnpm test:e2e tests/e2e/preview-render.spec.ts --update-snapshots
pnpm test:e2e tests/e2e/preview-render.spec.ts
```

Expected: first command creates the golden image; second command passes without updating it.

- [ ] **Step 6: Commit**

```bash
git add apps/web packages/render-three tests playwright.config.ts
git commit -m "feat: render deterministic lightbox previews"
```

---

### Task 11: Implement the Workflow State Machine and Approval Gates

**Files:**
- Create: `packages/workflow/src/state-machine.ts`
- Create: `packages/workflow/src/workflow-service.ts`
- Create: `packages/workflow/src/index.ts`
- Create: `packages/workflow/src/workflow.test.ts`

**Interfaces:**
- Consumes: repository, ingestion, classifier, scene builder, validator.
- Produces: guarded workflow transitions and persisted approval records.

- [ ] **Step 1: Write failing workflow tests**

```ts
import { expect, it } from "vitest";
import { transition } from "./index.js";

it("forbids scene approval when validation has high issues", () => {
  const state = {
    version: 1 as const,
    projectId: "project_a",
    phase: "preview_ready" as const,
    approvedSceneId: null,
    manifestApprovedAt: "2026-08-04T07:00:00.000Z",
    sceneApprovedAt: null,
  };
  expect(() => transition(state, {
    type: "APPROVE_SCENE",
    sceneId: "scene_a",
    reportStatus: "warning",
    highestSeverity: "high",
    approvedAt: "2026-08-04T07:10:00.000Z",
  })).toThrow("Scene cannot be approved");
});

it("permits final rendering only after scene approval", () => {
  const state = {
    version: 1 as const,
    projectId: "project_a",
    phase: "scene_approved" as const,
    approvedSceneId: "scene_a",
    manifestApprovedAt: "2026-08-04T07:00:00.000Z",
    sceneApprovedAt: "2026-08-04T07:10:00.000Z",
  };
  expect(transition(state, { type: "FINAL_RENDERED" }).phase).toBe("final_rendered");
});
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pnpm test packages/workflow/src/workflow.test.ts
```

- [ ] **Step 3: Implement explicit transitions**

Implement a switch over event types. Reject skipped phases. `APPROVE_MANIFEST` records an ISO timestamp. `APPROVE_SCENE` requires highest severity `null`, `low`, or `medium`. `FINAL_RENDERED` requires `scene_approved`.

- [ ] **Step 4: Verify workflow gates**

```bash
pnpm test packages/workflow/src/workflow.test.ts
pnpm --filter @lightbox/workflow typecheck
```

- [ ] **Step 5: Commit**

```bash
git add packages/workflow
git commit -m "feat: enforce manifest and scene approval gates"
```

---

### Task 12: Expose the Workflow Through a Fastify API

**Files:**
- Create: `apps/api/src/app.ts`
- Create: `apps/api/src/server.ts`
- Create: `apps/api/src/routes/projects.ts`
- Create: `apps/api/src/routes/assets.ts`
- Create: `apps/api/src/routes/scenes.ts`
- Create: `apps/api/src/routes/exports.ts`
- Create: `apps/api/src/app.test.ts`

**Interfaces:**
- Consumes: workflow service and local adapters.
- Produces: versioned HTTP endpoints with JSON schema validation.

- [ ] **Step 1: Write failing API tests**

```ts
import { afterEach, beforeEach, expect, it } from "vitest";
import type { FastifyInstance } from "fastify";
import { createApp } from "./app.js";

let app: FastifyInstance;
beforeEach(() => { app = createApp({ dataRoot: ".tmp/api-test" }); });
afterEach(async () => app.close());

it("creates a project and returns its workflow state", async () => {
  const response = await app.inject({ method: "POST", url: "/v1/projects", payload: { projectId: "project_api" } });
  expect(response.statusCode).toBe(201);
  expect(response.json()).toMatchObject({ projectId: "project_api", phase: "created" });
});

it("rejects final rendering before approval", async () => {
  await app.inject({ method: "POST", url: "/v1/projects", payload: { projectId: "project_blocked" } });
  const response = await app.inject({ method: "POST", url: "/v1/projects/project_blocked/final" });
  expect(response.statusCode).toBe(409);
  expect(response.json().code).toBe("SCENE_NOT_APPROVED");
});
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pnpm test apps/api/src/app.test.ts
```

- [ ] **Step 3: Implement these endpoints**

```text
GET    /health
POST   /v1/projects
POST   /v1/projects/:projectId/assets
GET    /v1/projects/:projectId/manifest
PATCH  /v1/projects/:projectId/manifest
POST   /v1/projects/:projectId/manifest/approve
POST   /v1/projects/:projectId/scenes
GET    /v1/projects/:projectId/scenes/:sceneId
POST   /v1/projects/:projectId/scenes/:sceneId/validate
POST   /v1/projects/:projectId/scenes/:sceneId/approve
POST   /v1/projects/:projectId/final
GET    /v1/projects/:projectId/exports
```

`GET /health` returns `{ "status": "ok" }`. Multipart upload accepts a maximum of 40 files, 20 MB each, and 300 MB per request. Return stable machine codes for all errors.

- [ ] **Step 4: Verify API tests**

```bash
pnpm test apps/api/src/app.test.ts
pnpm --filter @lightbox/api typecheck
```

- [ ] **Step 5: Commit**

```bash
git add apps/api
git commit -m "feat: expose guarded lightbox workflow API"
```

---

### Task 13: Build the Five-Step Review UI

**Files:**
- Create: `apps/web/src/main.tsx`
- Create: `apps/web/src/App.tsx`
- Create: `apps/web/src/api/client.ts`
- Create: `apps/web/src/state/project-store.ts`
- Create: `apps/web/src/steps/UploadStep.tsx`
- Create: `apps/web/src/steps/ManifestStep.tsx`
- Create: `apps/web/src/steps/PreviewStep.tsx`
- Create: `apps/web/src/steps/ValidationStep.tsx`
- Create: `apps/web/src/steps/ExportStep.tsx`
- Create: `apps/web/src/components/AssetCard.tsx`
- Create: `apps/web/src/components/ValidationList.tsx`
- Create: `apps/web/src/test/create-fake-api.ts`
- Create: `apps/web/src/test/setup.ts`
- Create: `apps/web/src/App.test.tsx`

**Interfaces:**
- Consumes: API client and Three.js renderer controller.
- Produces: upload, manifest confirmation, A/B/C previews, validation review, approval, export UI.

- [ ] **Step 1: Write failing UI tests**

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import { App } from "./App.js";
import { createFakeApi } from "./test/create-fake-api.js";

it("does not expose final generation before scene approval", async () => {
  render(<App api={createFakeApi({ phase: "preview_ready" })} />);
  expect(screen.queryByRole("button", { name: "生成最终图" })).toBeNull();
  expect(screen.getByText("先处理阻断项并确认预览")).toBeVisible();
});

it("lets the user mark an asset as reference only", async () => {
  const updateManifest = vi.fn();
  render(<App api={createFakeApi({ phase: "manifest_review", updateManifest })} />);
  await userEvent.selectOptions(screen.getByLabelText("lighting-reference.jpg 用途"), "reference_only");
  expect(updateManifest).toHaveBeenCalledWith(expect.objectContaining({ usage: "reference_only" }));
});
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pnpm test apps/web/src/App.test.tsx
```

- [ ] **Step 3: Implement the test support and wizard**

`apps/web/src/test/setup.ts` imports `@testing-library/jest-dom/vitest`. `createFakeApi` returns a typed in-memory implementation of the web API contract and accepts overrides for phase and mocked methods. Configure Vitest `environment: "jsdom"` and `setupFiles: ["./src/test/setup.ts"]` in the web package.

Implement the wizard:

Use exactly these steps and primary actions:

1. 上传素材 → `分析素材`
2. 素材清单 → `确认素材用途`
3. 构图预览 → `校验所选方案`
4. 问题检查 → `确认该方案`
5. 最终输出 → `生成最终图`

Display every asset's thumbnail, filename, category, usage, and exact-use lock. Display `reference_only` assets in a separate non-scene section. Do not implement freeform canvas editing in the MVP; provide template, seed, lock, and regenerate controls only.

- [ ] **Step 4: Add accessible overflow and approval messages**

Blocking issues use text plus icon, never color alone. The final button does not exist in the DOM until workflow phase is `scene_approved`.

- [ ] **Step 5: Verify UI tests and build**

```bash
pnpm test apps/web/src/App.test.tsx
pnpm --filter @lightbox/web typecheck
pnpm --filter @lightbox/web build
```

- [ ] **Step 6: Commit**

```bash
git add apps/web
git commit -m "feat: add lightbox asset review workflow UI"
```

---

### Task 14: Produce Deterministic Final Layers and Exact Typography

**Files:**
- Create: `packages/final-compositor/src/types.ts`
- Create: `packages/final-compositor/src/render-layer-page.ts`
- Create: `packages/final-compositor/src/capture-layers.ts`
- Create: `packages/final-compositor/src/composite.ts`
- Create: `packages/final-compositor/src/index.ts`
- Create: `packages/final-compositor/src/composite.test.ts`
- Create: `apps/web/src/layer-entry.tsx`

**Interfaces:**
- Consumes: approved scene, exact assets, fitted text, optional enhanced background.
- Produces: `background.png`, `depth.png`, `exact-mask.png`, `exact-assets.png`, `exact-text.png`, `final.png`, `render-manifest.json`.

- [ ] **Step 1: Write failing compositor tests**

```ts
import { expect, it } from "vitest";
import sharp from "sharp";
import { compositeLayers } from "./index.js";

it("places exact text and product layers above the background", async () => {
  const background = await sharp({ create: { width: 100, height: 100, channels: 4, background: "#ffffff" } }).png().toBuffer();
  const product = await sharp({ create: { width: 100, height: 100, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } } })
    .composite([{ input: Buffer.from('<svg width="100" height="100"><circle cx="50" cy="50" r="20" fill="#ff0000"/></svg>') }])
    .png().toBuffer();
  const text = await sharp({ create: { width: 100, height: 100, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } } })
    .composite([{ input: Buffer.from('<svg width="100" height="100"><rect x="10" y="10" width="30" height="10" fill="#000000"/></svg>') }])
    .png().toBuffer();
  const final = await compositeLayers({ background, exactAssets: product, exactText: text });
  const pixel = await sharp(final).extract({ left: 50, top: 50, width: 1, height: 1 }).raw().toBuffer();
  expect([...pixel.slice(0, 3)]).toEqual([255, 0, 0]);
});
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pnpm test packages/final-compositor/src/composite.test.ts
```

- [ ] **Step 3: Implement three render modes**

The browser layer route receives `mode`:

- `background`: lightbox, low-poly props, transformable documents; hide exact products and text.
- `exact-assets`: transparent background; show only `exactLayer: true` asset planes and their integration shadows.
- `exact-text`: transparent background; show fitted text and logo assets only.
- `depth`: grayscale depth from the orthographic camera, with the light-table surface mapped near white and raised objects progressively darker.
- `exact-mask`: transparent background with protected exact-product and logo regions rendered as opaque white.

Use Playwright screenshots with `omitBackground: true` for transparent layers. Capture at 1600×2000 and optionally 3200×4000.

- [ ] **Step 4: Implement Sharp composition**

Select the base layer first, then composite in this immutable order:

```ts
const effectiveBackground = optionalEnhancedBackground ?? background;
effectiveBackground -> exactAssets -> exactText
```

When `optionalEnhancedBackground` is present, it must have exact dimensions. Store SHA-256 hashes for every input layer in `render-manifest.json`.

- [ ] **Step 5: Verify compositor**

```bash
pnpm test packages/final-compositor/src/composite.test.ts
pnpm --filter @lightbox/final-compositor typecheck
```

- [ ] **Step 6: Commit**

```bash
git add packages/final-compositor apps/web/src/layer-entry.tsx
git commit -m "feat: compose exact final image layers"
```

---

### Task 15: Define the Optional AI Enhancement Contract After Approval

**Files:**
- Create: `packages/enhancer-contract/src/types.ts`
- Create: `packages/enhancer-contract/src/noop-enhancer.ts`
- Create: `packages/enhancer-contract/src/control-bundle.ts`
- Create: `packages/enhancer-contract/src/index.ts`
- Create: `packages/enhancer-contract/src/enhancer.test.ts`

**Interfaces:**
- Consumes: approved workflow state and deterministic background/control layers.
- Produces: portable `EnhancementRequest`, `EnhancementResult`, and a no-network adapter.

- [ ] **Step 1: Write failing enhancement-gate tests**

```ts
import { expect, it } from "vitest";
import { buildEnhancementRequest } from "./index.js";

it("rejects enhancement when the approved scene record is absent", () => {
  expect(() => buildEnhancementRequest({
    workflow: {
      version: 1,
      projectId: "project_a",
      phase: "preview_ready",
      approvedSceneId: null,
      manifestApprovedAt: null,
      sceneApprovedAt: null,
    },
    sceneId: "scene_a",
    backgroundUri: "project://project_a/renders/background.png",
    depthUri: "project://project_a/renders/depth.png",
    exactAssetMaskUri: "project://project_a/renders/exact-mask.png",
  })).toThrow("Enhancement requires an approved scene");
});
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pnpm test packages/enhancer-contract/src/enhancer.test.ts
```

- [ ] **Step 3: Implement the adapter contract**

```ts
export interface ImageEnhancerAdapter {
  enhance(request: EnhancementRequest): Promise<EnhancementResult>;
}

export interface EnhancementRequest {
  projectId: string;
  sceneId: string;
  backgroundUri: string;
  depthUri: string;
  exactAssetMaskUri: string;
  prompt: string;
  negativeConstraints: string[];
  outputWidth: number;
  outputHeight: number;
}
```

`negativeConstraints` always contains:

- `Do not add text or logos.`
- `Do not redraw or move protected product regions.`
- `Do not add user-interface chrome.`
- `Preserve the light-table frame and top-down camera.`

The no-op adapter returns the original background URI and render metadata. Vendor adapters live outside this package.

- [ ] **Step 4: Generate the control bundle**

The bundle contains background PNG, depth visualization PNG, exact-asset mask PNG, scene JSON, validation JSON, and a prompt text file. It contains no exact text layer and no logo layer.

- [ ] **Step 5: Verify enhancement gate**

```bash
pnpm test packages/enhancer-contract/src/enhancer.test.ts
pnpm --filter @lightbox/enhancer-contract typecheck
```

- [ ] **Step 6: Commit**

```bash
git add packages/enhancer-contract
git commit -m "feat: add approved-scene enhancement contract"
```

---

### Task 16: Add a CLI That Codex and the Skill Can Invoke Reliably

**Files:**
- Create: `apps/cli/src/commands/ingest.ts`
- Create: `apps/cli/src/commands/classify.ts`
- Create: `apps/cli/src/commands/build-scenes.ts`
- Create: `apps/cli/src/commands/validate.ts`
- Create: `apps/cli/src/commands/approve.ts`
- Create: `apps/cli/src/commands/render.ts`
- Create: `apps/cli/src/index.ts`
- Create: `apps/cli/src/cli.test.ts`

**Interfaces:**
- Consumes: workflow services.
- Produces: stable non-interactive commands and JSON output for Codex automation.

- [ ] **Step 1: Write failing CLI tests**

```ts
import { expect, it } from "vitest";
import { runCli } from "./index.js";

it("returns machine-readable state after project creation", async () => {
  const output: string[] = [];
  const code = await runCli(["project", "create", "project_cli", "--data-root", ".tmp/cli"], {
    stdout: (line) => output.push(line),
    stderr: () => undefined,
  });
  expect(code).toBe(0);
  expect(JSON.parse(output.at(-1)!)).toMatchObject({ projectId: "project_cli", phase: "created" });
});

it("returns exit code 2 when final render is blocked", async () => {
  const code = await runCli(["render", "final", "project_cli", "--data-root", ".tmp/cli"], {
    stdout: () => undefined,
    stderr: () => undefined,
  });
  expect(code).toBe(2);
});
```

- [ ] **Step 2: Run tests and verify failure**

```bash
pnpm test apps/cli/src/cli.test.ts
```

- [ ] **Step 3: Implement commands and stable exit codes**

Use:

- `0`: success
- `1`: invalid command or invalid input
- `2`: workflow gate or blocking validation
- `3`: processing failure

Every command supports `--json`; skill scripts always use it. Do not prompt interactively. Implement these exact command forms:

```text
lightbox project create PROJECT_ID --data-root DATA_ROOT --json
lightbox ingest PROJECT_ID INPUT_DIRECTORY --data-root DATA_ROOT --json
lightbox classify PROJECT_ID --hints HINTS_JSON --data-root DATA_ROOT --json
lightbox manifest approve PROJECT_ID --data-root DATA_ROOT --json
lightbox scenes build PROJECT_ID --templates archive_research_v1,product_focus_v1,art_lab_v1 --seed 731 --data-root DATA_ROOT --json
lightbox scene validate PROJECT_ID SCENE_ID --data-root DATA_ROOT --json
lightbox scene approve PROJECT_ID SCENE_ID --data-root DATA_ROOT --json
lightbox render final PROJECT_ID --data-root DATA_ROOT --json
```

- [ ] **Step 4: Verify CLI**

```bash
pnpm test apps/cli/src/cli.test.ts
pnpm --filter @lightbox/cli typecheck
```

- [ ] **Step 5: Commit**

```bash
git add apps/cli
git commit -m "feat: add non-interactive lightbox workflow CLI"
```

---

### Task 17: Package the Reusable `siuyu-lightbox-still-life` Skill

**Prebuilt integration rule:** Copy the canonical installed skill into `skills/siuyu-lightbox-still-life` first. Treat its files as the baseline implementation; modify only when a repository test proves an integration gap.

**Files:**
- Create: `skills/siuyu-lightbox-still-life/SKILL.md`
- Create: `skills/siuyu-lightbox-still-life/references/scene-schema.md`
- Create: `skills/siuyu-lightbox-still-life/references/material-presets.md`
- Create: `skills/siuyu-lightbox-still-life/references/acceptance-checklist.md`
- Create: `skills/siuyu-lightbox-still-life/scripts/ingest.sh`
- Create: `skills/siuyu-lightbox-still-life/scripts/preview.sh`
- Create: `skills/siuyu-lightbox-still-life/scripts/final.sh`
- Create: `skills/siuyu-lightbox-still-life/skill.test.ts`

**Interfaces:**
- Consumes: CLI commands and generated project artifacts.
- Produces: a portable SKILL.md workflow with mandatory human approval stops.

- [ ] **Step 1: Write a failing skill structure test**

```ts
import { readFile } from "node:fs/promises";
import { expect, it } from "vitest";

it("documents both approval gates and forbids direct final generation", async () => {
  const content = await readFile("skills/siuyu-lightbox-still-life/SKILL.md", "utf8");
  expect(content).toContain("STOP: require asset-manifest approval");
  expect(content).toContain("STOP: require scene approval");
  expect(content).toContain("Never call final rendering before both approvals are persisted");
});
```

- [ ] **Step 2: Run the test and verify failure**

```bash
pnpm test skills/siuyu-lightbox-still-life/skill.test.ts
```

- [ ] **Step 3: Write SKILL.md**

The skill must define this exact workflow:

1. Collect uploaded files and user constraints.
2. Run ingestion and classification.
3. Present a numbered contact sheet and manifest summary.
4. `STOP: require asset-manifest approval`.
5. Generate three scenes using fixed template IDs and seeds.
6. Validate and render previews with issue annotations.
7. `STOP: require scene approval`.
8. Persist approved scene ID.
9. Produce deterministic final layers.
10. Ask whether optional enhancement is desired; if used, enhance background only.
11. Reapply exact assets and exact text.
12. Run the final acceptance checklist and report all output paths.

Include the sentence: `Never call final rendering before both approvals are persisted`.

- [ ] **Step 4: Implement wrapper scripts**

`ingest.sh`, `preview.sh`, and `final.sh` use `set -euo pipefail`, verify the repository root, call `pnpm --filter @lightbox/cli`, and return the CLI exit code. They accept project ID and data root as positional parameters.

- [ ] **Step 5: Verify skill package**

```bash
pnpm test skills/siuyu-lightbox-still-life/skill.test.ts
bash -n skills/siuyu-lightbox-still-life/scripts/*.sh
```

Expected: one passing test and no Bash syntax errors.

- [ ] **Step 6: Commit**

```bash
git add skills/siuyu-lightbox-still-life
git commit -m "feat: package reusable lightbox archive skill"
```

---

### Task 18: Add End-to-End Workflow Verification

**Files:**
- Create: `tests/e2e/lightbox-workflow.spec.ts`
- Create: `tests/e2e/fixtures.ts`
- Modify: `playwright.config.ts`

**Interfaces:**
- Consumes: built API, web app, generated fixtures.
- Produces: end-to-end evidence that final rendering is impossible before approval and exact layers survive the workflow.

- [ ] **Step 1: Write the failing end-to-end test**

```ts
import { expect, test } from "@playwright/test";
import { createUploadFiles } from "./fixtures.js";

test("uploads many assets, confirms roles, approves a valid scene, and exports exact layers", async ({ page }) => {
  await page.goto("/");
  await page.setInputFiles("input[type=file]", await createUploadFiles());
  await page.getByRole("button", { name: "分析素材" }).click();
  await expect(page.getByText("素材清单")).toBeVisible();
  await page.getByLabel("lighting-reference.jpg 用途").selectOption("reference_only");
  await page.getByRole("button", { name: "确认素材用途" }).click();
  await expect(page.getByText("构图预览")).toBeVisible();
  await page.getByRole("button", { name: "选择方案 A" }).click();
  await page.getByRole("button", { name: "校验所选方案" }).click();
  await expect(page.getByText("阻断项 0")).toBeVisible();
  await page.getByRole("button", { name: "确认该方案" }).click();
  await page.getByRole("button", { name: "生成最终图" }).click();
  await expect(page.getByText("final.png")).toBeVisible();
  await expect(page.getByText("exact-assets.png")).toBeVisible();
  await expect(page.getByText("exact-text.png")).toBeVisible();
});
```

- [ ] **Step 2: Run the test and verify the incomplete workflow fails**

```bash
pnpm test:e2e tests/e2e/lightbox-workflow.spec.ts
```

- [ ] **Step 3: Implement the upload fixture and wire missing application behavior**

`tests/e2e/fixtures.ts` calls `createImageFixtures()`, writes the returned buffers into a Playwright temporary directory, and returns absolute paths for `product-front.png`, `design-sketch.png`, `artifact-reference.png`, `lighting-reference.jpg`, and `brand-logo.png`. Use only existing public package interfaces. Do not add special test-only API routes. Start API and web through Playwright `webServer` entries.

- [ ] **Step 4: Run full verification**

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
pnpm test:e2e
```

Expected: all commands exit 0.

- [ ] **Step 5: Commit**

```bash
git add tests playwright.config.ts apps packages
git commit -m "test: verify complete approved lightbox workflow"
```

---

### Task 19: Containerize the Runtime and Document Portability

**Files:**
- Create: `Dockerfile`
- Create: `.dockerignore`
- Create: `docs/architecture.md`
- Create: `tooling/scripts/start-runtime.sh`
- Create: `tooling/scripts/container-smoke.sh`
- Modify: `README.md`
- Modify: `.env.example`

**Interfaces:**
- Consumes: built monorepo.
- Produces: reproducible Linux runtime with Chromium and CJK fonts; deployment-neutral documentation.

- [ ] **Step 1: Write a failing container smoke script**

Create `tooling/scripts/container-smoke.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
curl --fail --silent http://127.0.0.1:3001/health | grep '"status":"ok"'
curl --fail --silent http://127.0.0.1:4173/ | grep '<div id="root">'
```

- [ ] **Step 2: Create the runtime launcher and Dockerfile**

Create `tooling/scripts/start-runtime.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
pnpm --filter @lightbox/api start &
api_pid=$!
pnpm --filter @lightbox/web preview --host 0.0.0.0 --port 4173 &
web_pid=$!
trap 'kill "$api_pid" "$web_pid" 2>/dev/null || true' EXIT INT TERM
wait -n "$api_pid" "$web_pid"
```

Use a Node 24 Debian-based image. Install Playwright Chromium dependencies and `fonts-noto-cjk`. Use a build stage and a runtime stage. Run as a non-root user. Persist data under `/data` and expose API port 3001 and web port 4173.

- [ ] **Step 3: Document adapter boundaries**

`docs/architecture.md` must name each portable interface and show how to replace:

- local storage with S3-compatible storage,
- rule classifier with a model-assisted classifier,
- no-op enhancer with an image-generation service,
- WebGL preview with a Blender render adapter,
- Vite web app with another client.

- [ ] **Step 4: Verify the container**

```bash
docker build -t lightbox-archive:mvp .
docker run --rm -d --name lightbox-archive-test -p 3001:3001 -p 4173:4173 lightbox-archive:mvp
bash tooling/scripts/container-smoke.sh
docker stop lightbox-archive-test
```

Expected: health JSON and web root are found.

- [ ] **Step 5: Commit**

```bash
git add Dockerfile .dockerignore README.md docs .env.example tooling/scripts/start-runtime.sh tooling/scripts/container-smoke.sh
git commit -m "docs: containerize and document portable architecture"
```

---

### Task 20: Final Verification and MVP Acceptance

**Files:**
- Modify only files required to fix verification failures.
- Create: `docs/mvp-acceptance-report.md`

**Interfaces:**
- Consumes: complete repository.
- Produces: fresh verification evidence and an acceptance report.

- [ ] **Step 1: Run the complete verification suite**

```bash
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm test
pnpm build
pnpm test:e2e
docker build -t lightbox-archive:mvp .
```

- [ ] **Step 2: Run the acceptance scenario twice**

Run the deterministic acceptance driver. It creates a unique
`.tmp/task20-acceptance-*` evidence directory, executes the same CLI sequence in
`run-a` and `run-b`, discovers the generated scene ID from `scenes build`, and
compares all three scene JSON files plus every deterministic PNG layer:

```bash
pnpm acceptance:mvp
```

Expected: `ok: true`, three matching scene hashes, and matching hashes for all
six PNG layers across runs. The driver writes the full result to
`acceptance-summary.json` inside the reported evidence directory.

- [ ] **Step 3: Verify all MVP acceptance conditions**

Record pass or fail for each condition:

1. Forty image files can be uploaded within configured limits.
2. Duplicates are identified.
3. `must_use_exact` and `reference_only` are visibly distinct.
4. Same seed produces identical scene JSON.
5. Text overflow blocks approval.
6. Missing required assets block approval.
7. Three preview templates render.
8. Final generation is unavailable before approval.
9. Deterministic final export works offline.
10. Optional enhancement owns background only.
11. Exact assets and text are composited last.
12. Skill contains two explicit human stops.
13. Full test suite and container build pass.

- [ ] **Step 4: Write the acceptance report**

Create `docs/mvp-acceptance-report.md` with exact command output summaries, test counts, screenshot paths, output hashes, known limitations, and the next recommended milestone: automatic cutout adapter plus Blender path-traced final renderer.

- [ ] **Step 5: Commit**

```bash
git add docs/mvp-acceptance-report.md
git commit -m "chore: record lightbox MVP acceptance evidence"
```

### Task 21: Add the Codex-Native Visual Direction Workflow

**Files:**
- Create: `skills/siuyu-lightbox-still-life/references/visual-direction.md`
- Create: `skills/siuyu-lightbox-still-life/assets/visual-direction.example.json`
- Create: `skills/siuyu-lightbox-still-life/scripts/compile_generation_description.py`
- Create: `skills/siuyu-lightbox-still-life/visual-direction.test.ts`
- Modify: `skills/siuyu-lightbox-still-life/SKILL.md`
- Modify: `skills/siuyu-lightbox-still-life/skill.test.ts`
- Modify: `skills/siuyu-lightbox-still-life/scripts/validate_skill.py`
- Modify: `skills/siuyu-lightbox-still-life/evals/evals.json`
- Modify: `skills/siuyu-lightbox-still-life/agents/openai.yaml`
- Modify: `docs/architecture.md`
- Modify: `docs/mvp-acceptance-report.md` (supersede the Blender-first recommendation; do not change Task 20 evidence)

**Interfaces:**
- Consumes: the user's verbatim request, classified assets, approved visible-text allowlist, source-analysis evidence, and actual preview pixels when available.
- Produces: a Codex-authored `visual-direction.json`, a validated placement-opportunity list, an optimization priority order, a naturalness/restraint/flow review, and a canonical generation description.

This is a Codex Skill capability first. Codex performs the visual interpretation and bounded judgment; the local script validates the structured decision record and compiles it deterministically. Three.js remains the default local preview/final engine. Blender, another renderer, or ImageGen may consume the same description only through a separately available and explicitly authorized adapter; none is required, installed, or called by this task.

- [ ] **Step 1: Write failing Skill and compiler tests**

The tests must prove that:

1. `SKILL.md` names Codex as the visual-direction layer and the repository runtime as supporting execution infrastructure.
2. Blender is explicitly optional and lack of Blender never blocks brief analysis, placement planning, preview, or deterministic final output.
3. The visual-direction reference requires observed/user-supplied/inferred/unknown evidence labels.
4. Every suggested insertion has an evidenced bounded region, subject cause, viewer effect, removal impact, anchor/contact rule, scale, material, P3/P4 priority, confidence, and rejection constraints.
5. The quality review separately checks visual unity, component detail, texture scale, naturalness, restraint, reading flow, and physical plausibility.
6. A raw theme or vague request never becomes visible text or a fabricated physical dimension.
7. The compiler rejects unknown fields, manifest/hash/role mismatches, missing exact-asset locks, duplicate placement IDs, invalid normalized regions, invented visible text, unsupported deictic coordinates, direction-plan self-approval, and unresolved `unknown` facts represented as certainties.
8. The same valid JSON produces byte-identical generation-description text.

- [ ] **Step 2: Run the tests and verify RED**

```bash
pnpm test skills/siuyu-lightbox-still-life/visual-direction.test.ts skills/siuyu-lightbox-still-life/skill.test.ts
```

Expected: failure because the reference, example, compiler, and Codex-native contract do not yet exist.

- [ ] **Step 3: Define the Codex visual-direction protocol**

The protocol must operate in this order:

1. Preserve the user's original request verbatim.
2. Run form sanity: separate deliverable intent from visible copy, name viewer action and viewing context, and explain why the carrier fits.
3. Lock exact assets, transformable assets, reference-only sources, and exclusions.
4. Record evidence and unresolved unknowns without silently converting them to facts.
5. Establish one visual system for camera, hierarchy, detail level, material response, texture scale, light, color, and edge/shadow behavior.
6. Inspect occupied mass, negative space, reading path, focal competition, and physical support before suggesting any insertion.
7. Run the asset necessity test; suggest an element only when removal weakens identity, evidence, approved atmosphere, hierarchy, context, scale, linkage, balance, or material transition.
8. Put `P0` preservation/blockers, `P1` hierarchy/composition, and `P2` scale/contact/material repairs in `optimizationActions`; reserve `placementOpportunities` for P3/P4 additions.
9. Reject decorative filler, repeated evidence, floating props, impossible intersections, style-reference residue, unapproved text, and texture detail that does not survive output scale.
10. Compile one exact generation description plus explicit negative constraints and unknowns.

- [ ] **Step 4: Implement the portable validator/compiler**

`compile_generation_description.py` accepts one visual-direction JSON file, optionally verifies the current manifest through `--manifest`, validates a closed-world versioned contract, and writes the canonical description to stdout or `--output`. It uses only the Python standard library, performs no network or model calls, and never edits source JSON. Optimization actions are emitted P0-P4 and placement opportunities P3/P4 with stable ID tie-breaking. A direction plan keeps quality statuses pending; a pixel review requires scene and preview hashes.

- [ ] **Step 5: Integrate the protocol into the Codex Skill**

The Skill must run the visual-direction pass after source classification and before scene generation, then rerun the quality review against actual preview pixels before scene approval. Add eval cases for vague combination requests, user-directed placement, excessive decoration, inconsistent texture/detail, unknown dimensions, reference leakage, and missing Blender.

- [ ] **Step 6: Verify the Skill and repository**

```bash
pnpm test skills/siuyu-lightbox-still-life/visual-direction.test.ts skills/siuyu-lightbox-still-life/skill.test.ts
python3 skills/siuyu-lightbox-still-life/scripts/validate_skill.py skills/siuyu-lightbox-still-life
pnpm lint
pnpm typecheck
pnpm test
pnpm build
git diff --check
```

- [ ] **Step 7: Commit**

```bash
git add skills/siuyu-lightbox-still-life docs
git commit -m "feat: add codex-native visual direction workflow"
```

---

### Task 22: Bridge Visual Direction into Deterministic Scene Constraints

**Files:**
- Create: `packages/scene-builder/src/visual-direction-bridge.ts`
- Create: `packages/scene-builder/src/visual-direction-bridge.test.ts`
- Modify: `packages/scene-builder/src/build-scene.ts`
- Modify: `packages/scene-builder/src/index.ts`
- Modify: `packages/schema/src/scene.ts`
- Modify: `packages/schema/src/index.ts`
- Modify: `packages/schema/src/schema.test.ts`
- Generate: `packages/schema/generated/scene-spec.schema.json`
- Modify: `apps/cli/src/commands/build-scenes.ts`
- Modify: `apps/cli/src/index.ts`
- Modify: `apps/cli/src/cli.test.ts`
- Modify: `skills/siuyu-lightbox-still-life/SKILL.md`
- Modify: `skills/siuyu-lightbox-still-life/references/visual-direction.md`
- Modify: `skills/siuyu-lightbox-still-life/references/scene-schema.md`
- Modify: `skills/siuyu-lightbox-still-life/scripts/preview.sh`
- Modify: `skills/siuyu-lightbox-still-life/skill.test.ts`

**Interfaces:**
- Consumes: a compiler-valid `visual-direction.json`, the current `AssetManifest`, a persisted `manifest_approved` workflow state, a template ID, and a seed.
- Produces: `visualDirectionToBuildSceneRequest(...)`, a deterministic `BuildSceneRequest` constraint trace, and a `SceneSpec` bound to the direction hash when location evidence is confirmed.

The bridge is local and renderer-neutral. It must not call an API, model service, vendor SDK, or Blender. It preserves the canonical manifest hash, all four asset-role groups, location evidence, exact approved-text allowlist, first human approval evidence, and the requirement for a separate second human scene approval.

- [ ] **Step 1: Write failing bridge, schema, CLI, and Skill tests**

The tests must prove that:

1. The same manifest, workflow, direction, template, and seed produce byte-equivalent requests and scenes.
2. Manifest project/hash mismatches and asset-role mismatches are rejected.
3. Exact, transformable, reference-only, and excluded roles survive into `SceneSpec` without reference or excluded assets becoming scene objects.
4. Approved visible text survives as an exact allowlist; unapproved scene text is rejected and the bridge invents no text coordinates.
5. `user-markup` or `user-coordinate` with `confirmation: confirmed` deterministically bounds the hero transform and records the evidence ID.
6. `unresolved` keeps `region: null`; observed, inferred, and unconfirmed user regions remain non-executable. None can produce a `SceneSpec` coordinate.
7. Scene construction requires the persisted manifest approval and records that the independent scene approval is still required.
8. The production Skill wrapper supplies `--visual-direction`; final rendering remains blocked until the second persisted approval.

- [ ] **Step 2: Run the focused tests and verify RED**

```bash
pnpm test packages/scene-builder/src/visual-direction-bridge.test.ts packages/schema/src/schema.test.ts apps/cli/src/cli.test.ts skills/siuyu-lightbox-still-life/skill.test.ts
```

Expected: failure because the bridge, SceneSpec constraint trace, and CLI option do not exist.

- [ ] **Step 3: Implement the closed deterministic bridge**

Implement `visualDirectionToBuildSceneRequest(...)` without dependencies beyond existing workspace packages. Validate the direction's closed top-level record and every boundary-critical field again at runtime: project, manifest hash, asset locks, evidence records, focal placement, approved text, canvas, direction-plan review state, and approval phase. Canonicalize role and text arrays and hash the complete direction record.

The returned request carries a discriminated focal constraint:

- `confirmed`: only `user-markup` or `user-coordinate`, with a bounded normalized region and user-supplied evidence;
- `candidate`: observed, inferred, or unconfirmed user evidence; never executable;
- `unresolved`: `region: null`; never executable.

- [ ] **Step 4: Apply only confirmed constraints to `SceneSpec`**

Fit the exact hero asset inside the confirmed region while preserving source aspect ratio, derive the composition focal point from that region, and reject rather than silently moving a region that cannot satisfy safe margins. Include a canonical direction-constraint trace in `SceneSpec` and direction hash in the scene identity. Keep approved text as an allowlist; do not create text blocks without separate placement evidence.

Schema refinement must reject manifest-hash drift, reference/excluded source objects, source-role drift, missing hero placement, and text not present in the approved allowlist.

- [ ] **Step 5: Wire the production CLI and Skill wrapper**

Add `--visual-direction FILE` to `lightbox scenes build`. The option remains explicit and non-interactive. `preview.sh` requires the direction file and forwards it. An unresolved or candidate focal constraint returns the existing workflow-gate exit class and writes no scene.

- [ ] **Step 6: Verify focused and complete gates**

```bash
pnpm test packages/scene-builder/src/visual-direction-bridge.test.ts packages/schema/src/schema.test.ts apps/cli/src/cli.test.ts skills/siuyu-lightbox-still-life/skill.test.ts
pnpm --filter @lightbox/schema schema:export
python3 skills/siuyu-lightbox-still-life/scripts/validate_skill.py skills/siuyu-lightbox-still-life
pnpm lint
pnpm typecheck
pnpm test
pnpm build
git diff --check
python3 skills/siuyu-lightbox-still-life/scripts/verify_project.py --repo . --json
```

- [ ] **Step 7: Commit**

```bash
git add packages/scene-builder packages/schema/generated/scene-spec.schema.json packages/schema/src apps/cli skills/siuyu-lightbox-still-life docs/superpowers/plans/2026-08-04-siuyu-lightbox-still-life-mvp.md
git commit -m "feat: bridge visual direction into scene constraints"
```

---

### Task 23: Bind Human Approval Receipts to Artifact Hashes

**Files:**
- Create: `packages/schema/src/artifact-hash.ts`
- Create: `packages/schema/src/artifact-hash.test.ts`
- Modify: `packages/schema/src/common.ts`
- Modify: `packages/schema/src/workflow.ts`
- Modify: `packages/schema/src/scene.ts`
- Modify: `packages/schema/src/index.ts`
- Modify: `packages/schema/src/schema.test.ts`
- Generate: `packages/schema/generated/workflow-state.schema.json`
- Generate: `packages/schema/generated/scene-spec.schema.json`
- Modify: `packages/workflow/src/workflow-service.ts`
- Modify: `packages/workflow/src/workflow.test.ts`
- Modify: `packages/scene-builder/src/visual-direction-bridge.ts`
- Modify: `packages/scene-builder/src/visual-direction-bridge.test.ts`
- Modify: `apps/cli/src/commands/render.ts`
- Modify: `apps/cli/src/commands/build-scenes.ts`
- Modify: `apps/cli/src/cli.test.ts`
- Modify: `apps/api/src/routes/scenes.ts`
- Modify: `apps/api/src/routes/exports.ts`
- Modify: `apps/api/src/app.test.ts`
- Modify: `skills/siuyu-lightbox-still-life/SKILL.md`
- Modify: `skills/siuyu-lightbox-still-life/references/workflow-contract.md`
- Modify: `skills/siuyu-lightbox-still-life/references/scene-schema.md`
- Modify: `skills/siuyu-lightbox-still-life/references/visual-direction.md`
- Modify: `skills/siuyu-lightbox-still-life/skill.test.ts`

**Interfaces:**
- Consumes: persisted manifest and scene approval actions, the canonical manifest, a direction-bound `SceneSpec`, and its persisted `ValidationReport`.
- Produces: atomic human approval receipts in `WorkflowState`, canonical artifact hash helpers, a manifest-approval receipt hash in `SceneSpec`, and a final-render verification gate that rejects stale artifacts.

The receipts are local deterministic data. They must use `approvedBy: human`; the system may persist an approval only after the existing explicit approval command. No API, model service, vendor SDK, cloud store, or Blender dependency is permitted.

- [ ] **Step 1: Write failing schema, workflow, bridge, CLI, and Skill tests**

The tests must prove that:

1. Canonical scene, validation, and manifest-approval hashes are stable across object-key order and change when bound content changes.
2. Manifest approval atomically records project ID, canonical manifest hash, timestamp, and `approvedBy: human` in workflow state.
3. Scene approval records scene ID, manifest hash, manifest-approval hash, visual-direction hash, scene hash, validation hash, timestamp, and `approvedBy: human`.
4. Legacy timestamp-only workflow state may still parse for recovery, but cannot build a direction-bound production scene, approve a scene, or render a final.
5. Scene approval rejects a scene without `directionConstraints`, a stale manifest approval, or a direction receipt that does not match the current approval.
6. Final verification recomputes every bound hash and rejects manifest, scene, validation, direction, or receipt drift before a render server starts.
7. `SceneSpec.directionConstraints.approvalGates` preserves the exact manifest-approval receipt hash and still requires the independent second human approval.
8. The CLI exposes receipt data after both approval commands and maps stale final evidence to a workflow-gate error.

- [ ] **Step 2: Run the focused tests and verify RED**

```bash
pnpm test packages/schema/src/artifact-hash.test.ts packages/schema/src/schema.test.ts packages/workflow/src/workflow.test.ts packages/scene-builder/src/visual-direction-bridge.test.ts apps/cli/src/cli.test.ts skills/siuyu-lightbox-still-life/skill.test.ts
```

Expected: failure because approval receipt schemas, canonical artifact hashes, receipt-bound workflow transitions, and final verification do not exist.

- [ ] **Step 3: Add portable receipt schemas and canonical hashes**

Add closed `ManifestApprovalRecord` and `SceneApprovalRecord` schemas. Keep timestamp-only workflow fields for recovery compatibility, but make new receipts authoritative for production operations and require their summary fields to agree whenever a receipt exists. Canonically hash parsed artifact content with stable object-key order; preserve array order, exclude a SceneSpec self-hash field, and add no dependency.

- [ ] **Step 4: Persist and verify both human receipts**

On manifest approval, hash the current persisted manifest and store the receipt in the same atomic workflow-state write as the phase transition. On scene approval, require the current manifest receipt and direction trace, recompute manifest, scene, and validation hashes, then store the second receipt atomically with the transition. Never infer an approval or accept caller-supplied hashes.

Add one workflow verification method used both before final rendering and by `recordFinalRendered`. It must reread current persisted artifacts and compare every receipt field and hash before returning verified evidence.

- [ ] **Step 5: Bind the bridge and final-render gate**

Require a current manifest approval receipt in `visualDirectionToBuildSceneRequest`, carry its canonical hash into `SceneSpec.directionConstraints.approvalGates`, and reject timestamp-only or mismatched workflow state. Route both CLI and API production scene builds through this bridge; the API must reject an approved-manifest build that omits `visualDirection`. Make both CLI and API final commands verify receipts before contacting or opening a local render server. A stale receipt or artifact returns a workflow-gate error and produces no final output.

- [ ] **Step 6: Update the portable Skill contract**

Document that chat text and timestamps alone are not approvals. The first receipt binds the manifest; the second binds the direction-aware scene and validation report. Final rendering must revalidate both receipts. Update Skill tests without adding auxiliary documentation or remote adapters.

- [ ] **Step 7: Verify focused and complete gates**

```bash
pnpm test packages/schema/src/artifact-hash.test.ts packages/schema/src/schema.test.ts packages/workflow/src/workflow.test.ts packages/scene-builder/src/visual-direction-bridge.test.ts apps/cli/src/cli.test.ts skills/siuyu-lightbox-still-life/skill.test.ts
pnpm --filter @lightbox/schema schema:export
python3 skills/siuyu-lightbox-still-life/scripts/validate_skill.py skills/siuyu-lightbox-still-life
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/siuyu-lightbox-still-life
bash -n skills/siuyu-lightbox-still-life/scripts/*.sh
pnpm lint
pnpm typecheck
pnpm test
pnpm build
git diff --check
python3 skills/siuyu-lightbox-still-life/scripts/verify_project.py --repo . --json
```

- [ ] **Step 8: Commit**

```bash
git add packages/schema packages/workflow packages/scene-builder apps/cli apps/api skills/siuyu-lightbox-still-life docs/superpowers/plans/2026-08-04-siuyu-lightbox-still-life-mvp.md
git commit -m "feat: bind human approvals to artifact hashes"
```

---

### Task 24: Persist Hash-Bound Pre-Approval Preview Evidence

**Files:**
- Create: `packages/schema/src/preview.ts`
- Create: `packages/schema/src/preview-evidence.test.ts`
- Generate: `packages/schema/generated/preview-evidence.schema.json`
- Modify: `packages/schema/src/artifact-hash.ts`
- Modify: `packages/schema/src/workflow.ts`
- Modify: `packages/schema/src/index.ts`
- Modify: `packages/schema/src/export-json-schema.ts`
- Modify: `packages/storage/src/types.ts`
- Modify: `packages/storage/src/project-repository.ts`
- Modify: `packages/storage/src/local-storage.test.ts`
- Modify: `packages/final-compositor/src/project-render.ts`
- Modify: `packages/final-compositor/src/project-render.test.ts`
- Modify: `packages/final-compositor/src/index.ts`
- Modify: `packages/workflow/src/workflow-service.ts`
- Modify: `packages/workflow/src/workflow.test.ts`
- Modify: `apps/cli/src/commands/build-scenes.ts`
- Create: `apps/cli/src/commands/preview.ts`
- Create: `apps/cli/src/commands/local-render-server.ts`
- Modify: `apps/cli/src/commands/render.ts`
- Modify: `apps/cli/src/index.ts`
- Modify: `apps/cli/src/cli.test.ts`
- Modify: `apps/api/src/app.ts`
- Modify: `apps/api/src/routes/scenes.ts`
- Modify: `apps/api/src/app.test.ts`
- Modify: `apps/web/src/api/client.ts`
- Modify: `apps/web/src/App.tsx`
- Modify: `apps/web/src/App.test.tsx`
- Modify: `apps/web/src/test/create-fake-api.ts`
- Modify: `apps/web/src/layer-entry.tsx`
- Modify: `tests/e2e/final-layers.spec.ts`
- Modify: `tests/e2e/lightbox-workflow.spec.ts`
- Modify: `skills/siuyu-lightbox-still-life/SKILL.md`
- Modify: `skills/siuyu-lightbox-still-life/references/workflow-contract.md`
- Modify: `skills/siuyu-lightbox-still-life/scripts/ingest.sh`
- Modify: `skills/siuyu-lightbox-still-life/scripts/preview.sh`
- Modify: `skills/siuyu-lightbox-still-life/scripts/final.sh`
- Modify: `skills/siuyu-lightbox-still-life/skill.test.ts`

**Interfaces:**
- Consumes: a persisted direction-bound `SceneSpec`, its current manifest, approved source bytes, and the existing local Three.js render host.
- Produces: one full-composite PNG and one closed `PreviewEvidenceRecord` per candidate, stored below `project://PROJECT_ID/previews/SCENE_ID/`, plus a `preview_ready` state that carries those exact records.

This task establishes trustworthy pixels before visual judgment. It does not perform the seven-item Codex quality review, call a model or API, install a vendor SDK, or require Blender. A later task may bind a Codex-authored `preview-pixels` review to these records; this task must not claim that a valid hash proves visual quality.

- [ ] **Step 1: Write failing schema, storage, compositor, workflow, CLI, API, and Skill tests**

The tests must prove that:

1. Preview evidence is a strict versioned record bound to project ID, scene ID, canonical scene hash, exact project URI, PNG byte hash, byte length, pixel dimensions, and renderer version.
2. Canonical preview-record hashes are stable across key order; binary hashes change with any preview-byte change.
3. Repository reads and writes reject project, scene, and URI ownership mismatches.
4. The local renderer composites background, exact assets, and exact text, computes the hash from the actual PNG bytes, and persists those exact bytes before returning evidence.
5. `recordPreviewReady` rereads the scene, evidence record, and preview bytes; missing, stale, truncated, cross-project, or caller-invented evidence cannot advance workflow.
6. Scene approval and final verification bind the selected preview hash and preview-evidence hash, and reject scene, record, or PNG drift.
7. The CLI writes all candidate previews before reporting `preview_ready`, exposes their URIs and hashes, and offers an idempotent explicit preview-render command for recovery from `scenes_generated`.
8. The API never reports `preview_ready` from scene JSON alone; a configured local preview renderer may persist evidence, while an unavailable renderer leaves the recoverable `scenes_generated` phase.
9. The Skill states that preview pixels are a stored, hash-bound artifact and that this evidence is still distinct from the seven-item Codex visual judgment.

- [ ] **Step 2: Run focused tests and verify RED**

```bash
pnpm test packages/schema/src/preview-evidence.test.ts packages/storage/src/local-storage.test.ts packages/final-compositor/src/project-render.test.ts packages/workflow/src/workflow.test.ts apps/cli/src/cli.test.ts apps/api/src/app.test.ts apps/web/src/App.test.tsx skills/siuyu-lightbox-still-life/skill.test.ts
```

Expected: failure because `PreviewEvidenceRecord`, preview persistence/rendering, evidence-driven workflow transitions, and preview bindings do not exist.

- [ ] **Step 3: Add the closed preview-evidence contract and atomic repository document**

Add a strict record with no free-form claims. Require the exact URI `project://PROJECT_ID/previews/SCENE_ID/preview.png`, dimensions supported by the deterministic renderer, and `three-playwright-v1`. Export its JSON Schema and canonical record/binary hash helpers. Store its JSON atomically at `PROJECT_ID/previews/SCENE_ID/evidence.json` and validate identity and URI ownership again on read.

- [ ] **Step 4: Render and persist the full preview locally**

Reuse the existing offline layer capture and exact-layer compositor at 1600×2000. Verify approved source hashes before rendering. Persist the complete composited PNG, verify the returned URI and byte length, then construct the evidence record from the bytes actually written. Do not promote an in-memory Canvas, caller-supplied hash, or SceneSpec-only claim to preview evidence.

- [ ] **Step 5: Gate workflow and approvals on current bytes**

`recordPreviewReady` accepts the expected scene IDs, rereads every scene/evidence/PNG tuple, and writes the verified records into `WorkflowState` in the same atomic state transition. Scene approval binds the selected preview hash and evidence-record hash. Final verification recomputes both and blocks drift before a render server starts. Keep legacy records readable for recovery but non-production.

- [ ] **Step 6: Wire CLI, API, and Codex Skill**

The CLI `scenes build` command stops at `scenes_generated`; a separate stable `previews render` command opens only a loopback static host, renders all named candidates, persists evidence, and only then reports `preview_ready`. The Skill wrapper invokes both commands and preserves the scene IDs from the build result, while the explicit preview command remains available for retry after a capture failure. The API uses the same explicit split and returns `scenes_generated` until its configured local preview renderer succeeds. Update the Skill so Codex inspects the persisted preview URI before writing a separate pixel-quality review.

- [ ] **Step 7: Verify focused and complete gates**

```bash
pnpm test packages/schema/src/preview-evidence.test.ts packages/storage/src/local-storage.test.ts packages/final-compositor/src/project-render.test.ts packages/workflow/src/workflow.test.ts apps/cli/src/cli.test.ts apps/api/src/app.test.ts apps/web/src/App.test.tsx skills/siuyu-lightbox-still-life/skill.test.ts
pnpm --filter @lightbox/schema schema:export
python3 skills/siuyu-lightbox-still-life/scripts/validate_skill.py skills/siuyu-lightbox-still-life
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/siuyu-lightbox-still-life
bash -n skills/siuyu-lightbox-still-life/scripts/*.sh
pnpm lint
pnpm typecheck
pnpm test
pnpm build
git diff --check
python3 skills/siuyu-lightbox-still-life/scripts/verify_project.py --repo . --json
```

- [ ] **Step 8: Commit**

```bash
git add packages/schema packages/storage packages/final-compositor packages/workflow apps/cli apps/api apps/web tests/e2e/final-layers.spec.ts tests/e2e/lightbox-workflow.spec.ts skills/siuyu-lightbox-still-life docs/superpowers/plans/2026-08-04-siuyu-lightbox-still-life-mvp.md
git commit -m "feat: persist hash-bound preview evidence"
```

---

### Task 25: Persist Hash-Bound Codex Preview Quality Reviews

**Files:**
- Create: `packages/schema/src/preview-quality-review.ts`
- Create: `packages/schema/src/preview-quality-review.test.ts`
- Generate: `packages/schema/generated/preview-quality-review.schema.json`
- Modify: `packages/schema/src/artifact-hash.ts`
- Modify: `packages/schema/src/workflow.ts`
- Modify: `packages/schema/src/index.ts`
- Modify: `packages/schema/src/export-json-schema.ts`
- Modify: `packages/schema/src/schema.test.ts`
- Modify: `packages/storage/src/types.ts`
- Modify: `packages/storage/src/project-repository.ts`
- Modify: `packages/storage/src/local-storage.test.ts`
- Modify: `packages/workflow/src/workflow-service.ts`
- Modify: `packages/workflow/src/workflow.test.ts`
- Create: `apps/cli/src/commands/review-preview.ts`
- Modify: `apps/cli/src/index.ts`
- Modify: `apps/cli/src/cli.test.ts`
- Modify: `apps/api/src/routes/scenes.ts`
- Modify: `apps/api/src/app.ts`
- Modify: `apps/api/src/app.test.ts`
- Modify: `tests/e2e/lightbox-workflow.spec.ts`
- Create: `skills/siuyu-lightbox-still-life/assets/preview-quality-review.example.json`
- Create: `skills/siuyu-lightbox-still-life/scripts/review.sh`
- Modify: `skills/siuyu-lightbox-still-life/SKILL.md`
- Modify: `skills/siuyu-lightbox-still-life/references/visual-direction.md`
- Modify: `skills/siuyu-lightbox-still-life/references/workflow-contract.md`
- Modify: `skills/siuyu-lightbox-still-life/references/acceptance-checklist.md`
- Modify: `skills/siuyu-lightbox-still-life/scripts/preview.sh`
- Modify: `skills/siuyu-lightbox-still-life/scripts/validate_skill.py`
- Modify: `skills/siuyu-lightbox-still-life/skill.test.ts`

**Interfaces:**
- Consumes: actual persisted preview pixels, their current `PreviewEvidenceRecord`, the current direction-bound `SceneSpec`, and a Codex-authored seven-item `preview-pixels` judgment.
- Produces: one closed `PreviewQualityReviewRecord` per reviewed candidate, stored at `project://PROJECT_ID/previews/SCENE_ID/quality-review.json`, plus workflow and scene-approval bindings to its canonical hash.

This task makes visual judgment auditable without pretending that deterministic code can judge taste. Codex must inspect the actual preview pixels before authoring the seven observations. Runtime code validates identity, completeness, status derivation, and hash freshness only. It must not auto-score visual quality, call a remote API or model service, install a vendor SDK, or require Blender.

- [ ] **Step 1: Write failing schema, storage, workflow, CLI, API, E2E, and Skill tests**

The tests must prove that:

1. A review is strict, versioned, uses `reviewBasis: preview-pixels`, includes exactly visual unity, component detail, texture scale, naturalness, restraint, reading flow, and physical plausibility, and allows only pass, warning, or fail with a non-empty concrete note.
2. The persisted record binds project ID, scene ID, canonical scene hash, exact preview hash, preview-evidence hash, derived overall status, timestamp, and `reviewedBy: codex`; callers cannot supply the derived status, timestamp, reviewer, project ID, or evidence hash.
3. Canonical review hashes are stable across object-key order and change when any judgment or bound artifact changes.
4. Repository reads and writes reject project or scene identity mismatches and persist the record atomically below the matching preview directory.
5. Recording a review rereads the current scene, evidence record, and preview bytes; missing, stale, cross-project, truncated, or caller-mismatched scene/preview hashes cannot enter workflow state.
6. A fail blocks the second human approval, a warning stays visible and may proceed, and scene approval binds the exact quality-review hash in addition to the existing manifest, scene, validation, preview, and evidence hashes.
7. Final verification rereads and rehashes the quality review and rejects record, scene, evidence, preview-byte, or judgment drift before a render server starts.
8. `previews review PROJECT_ID SCENE_ID --review FILE` and the matching local API route accept only the seven Codex judgments bound to current scene/preview hashes and expose the persisted record; neither path fabricates a review.
9. The Skill makes pixel inspection and review persistence mandatory between preview rendering and the second human gate, while keeping deterministic validation findings separate.

- [ ] **Step 2: Run focused tests and verify RED**

```bash
pnpm test packages/schema/src/preview-quality-review.test.ts packages/schema/src/schema.test.ts packages/storage/src/local-storage.test.ts packages/workflow/src/workflow.test.ts apps/cli/src/cli.test.ts apps/api/src/app.test.ts skills/siuyu-lightbox-still-life/skill.test.ts
```

Expected: failure because the closed quality-review record, repository document, workflow hash binding, CLI/API command, and Skill wrapper do not exist.

- [ ] **Step 3: Add the closed review contract and canonical hash**

Reuse the seven established visual-direction item names. Accept a closed Codex input containing only `reviewBasis`, scene/preview identity hashes, and the seven observations. Derive overall status with `fail > warning > pass`, add local clock/reviewer/evidence bindings in the workflow service, export JSON Schema, and hash the parsed persisted record canonically. Do not infer quality from validation metrics or image bytes.

- [ ] **Step 4: Persist and verify the current pixel review**

Write the review atomically beside `evidence.json`. Before persistence, reread and verify the current scene, evidence record, and exact PNG bytes, then require the Codex-supplied scene ID, scene hash, and preview hash to match. Persist the record first and place the same parsed record in workflow state. A replacement review is allowed only while the workflow remains `preview_ready`.

- [ ] **Step 5: Bind approval and final verification**

Require a current non-failing review before the second human approval. Add its canonical hash to `SceneApprovalRecord`; keep legacy workflow documents parseable for recovery but not production approval or final rendering. Final verification must reread the review and recompute all review, evidence, scene, and preview-byte bindings. Warnings remain in the persisted record and returned workflow state.

- [ ] **Step 6: Wire the stable local CLI, API, and Codex Skill**

Add the explicit `previews review` command and a closed local API route. The Skill wrapper accepts a Codex-authored review JSON only after Codex has inspected the persisted PNG. `preview.sh` must stop at pixels and instruct the caller to inspect them; `review.sh` persists the review but never performs human approval. No wrapper may invent pass results or invoke a remote service.

- [ ] **Step 7: Verify focused and complete gates**

```bash
pnpm test packages/schema/src/preview-quality-review.test.ts packages/schema/src/schema.test.ts packages/storage/src/local-storage.test.ts packages/workflow/src/workflow.test.ts apps/cli/src/cli.test.ts apps/api/src/app.test.ts skills/siuyu-lightbox-still-life/skill.test.ts
pnpm --filter @lightbox/schema schema:export
python3 skills/siuyu-lightbox-still-life/scripts/validate_skill.py skills/siuyu-lightbox-still-life
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/siuyu-lightbox-still-life
bash -n skills/siuyu-lightbox-still-life/scripts/*.sh
pnpm lint
pnpm typecheck
pnpm test
pnpm build
git diff --check
python3 skills/siuyu-lightbox-still-life/scripts/verify_project.py --repo . --json
```

- [ ] **Step 8: Commit**

```bash
git add packages/schema packages/storage packages/workflow apps/cli apps/api tests/e2e/lightbox-workflow.spec.ts skills/siuyu-lightbox-still-life docs/superpowers/plans/2026-08-04-siuyu-lightbox-still-life-mvp.md
git commit -m "feat: bind codex preview reviews to pixels"
```

---

## Codex Execution Protocol

Run one task per Codex thread or isolated worktree. Use this prompt, replacing only the task number:

```text
Read AGENTS.md and docs/superpowers/plans/2026-08-04-siuyu-lightbox-still-life-mvp.md.
Execute Task 1 only.
Follow every test-first step in order, do not implement subsequent tasks, and commit the result with the plan's commit message.
Before reporting completion, run the task-specific test and pnpm typecheck.
Report changed files, command output summary, commit hash, and any unresolved risk.
```

After every third task, run:

```bash
pnpm lint && pnpm typecheck && pnpm test
```

Recommended parallelization after Task 2 is merged:

- Track A: Tasks 3–5.
- Track B: Tasks 6–8.
- Track C: Task 9 only.

Merge Tracks A–C before Task 10. Tasks 10–20 are sequential because they integrate renderer, workflow, API, UI, and export behavior.

## Plan Self-Review

- Spec coverage: asset upload, classification, confirmation, deterministic modeling, low-poly materials, light-source simulation, text overflow prevention, validation, preview approval, final rendering, optional AI enhancement, exact recomposition, Codex skill packaging, and portability are each assigned to explicit tasks.
- Placeholder scan: no unresolved markers, vague implementation gaps, or undefined task references remain.
- Type consistency: `AssetManifest`, `SceneSpec`, `ValidationReport`, `WorkflowState`, `BlobStore`, `ProjectRepository`, `AssetClassifierAdapter`, and `ImageEnhancerAdapter` retain the same names and responsibilities across tasks.
- Scope check: automatic background removal and Blender path tracing are deliberately excluded from the MVP and named as the next milestone rather than partially implemented.
