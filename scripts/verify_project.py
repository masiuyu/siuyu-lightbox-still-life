#!/usr/bin/env python3
"""Check bootstrap structure and production evidence for a lightbox-archive repository."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

BOOTSTRAP_REQUIRED_PATHS = [
    "package.json",
    "pnpm-workspace.yaml",
    "apps/cli/package.json",
    "packages/schema/package.json",
    "packages/asset-ingestion/package.json",
    "packages/asset-classifier/package.json",
    "packages/text-engine/package.json",
    "packages/scene-builder/package.json",
    "packages/validator/package.json",
    "packages/render-three/package.json",
    "packages/final-compositor/package.json",
    "packages/workflow/package.json",
]

PRODUCTION_SENTINELS = [
    {
        "path": "apps/cli/src/index.ts",
        "reason": "the CLI implementation entry point is absent or empty",
    },
    {
        "path": "tests/e2e/lightbox-workflow.spec.ts",
        "reason": "the end-to-end acceptance sentinel is absent or empty",
    },
    {
        "path": "docs/mvp-acceptance-report.md",
        "reason": "the final MVP acceptance report sentinel is absent or empty",
    },
]


def has_content(repo: Path, relative_path: str) -> bool:
    path = repo / relative_path
    return path.is_file() and path.stat().st_size > 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    repo = args.repo.expanduser().resolve()
    missing = [rel for rel in BOOTSTRAP_REQUIRED_PATHS if not (repo / rel).is_file()]
    production_missing = [
        check
        for check in PRODUCTION_SENTINELS
        if not has_content(repo, check["path"])
    ]
    bootstrap_ready = not missing
    production_ready = bootstrap_ready and not production_missing
    payload = {
        "repo": str(repo),
        # Keep the historical keys: ready/missing describe bootstrap readiness.
        "ready": bootstrap_ready,
        "missing": missing,
        "nextMode": "production" if production_ready else "implementation",
        "bootstrapReady": bootstrap_ready,
        "productionReady": production_ready,
        "productionMissing": production_missing,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Repository: {repo}")
        print(f"Mode: {payload['nextMode']}")
        if missing:
            print("Missing:")
            for item in missing:
                print(f"- {item}")
        else:
            print("Portable bootstrap structure is present.")
        if production_missing:
            print("Production evidence missing:")
            for item in production_missing:
                print(f"- {item['path']}: {item['reason']}")
        else:
            print("Production implementation and acceptance evidence are present.")
    raise SystemExit(0 if not missing else 2)


if __name__ == "__main__":
    main()
