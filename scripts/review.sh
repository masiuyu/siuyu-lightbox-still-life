#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 4 ]]; then
  echo "Usage: review.sh PROJECT_ID SCENE_ID DATA_ROOT REVIEW_JSON" >&2
  exit 1
fi

PROJECT_ID=$1
SCENE_ID=$2
DATA_ROOT=$3
REVIEW_JSON=$4

find_root() {
  if [[ -n "${LIGHTBOX_REPO_ROOT:-}" ]]; then
    printf '%s\n' "$LIGHTBOX_REPO_ROOT"
    return
  fi
  local dir=$PWD
  while [[ "$dir" != "/" ]]; do
    if [[ -f "$dir/pnpm-workspace.yaml" && -f "$dir/apps/cli/package.json" ]]; then
      printf '%s\n' "$dir"
      return
    fi
    dir=$(dirname "$dir")
  done
  echo "Cannot locate lightbox-archive repository. Set LIGHTBOX_REPO_ROOT." >&2
  exit 1
}

ROOT=$(find_root)
pnpm --silent --dir "$ROOT" --filter @lightbox/cli start -- previews review \
  "$PROJECT_ID" "$SCENE_ID" \
  --review "$REVIEW_JSON" \
  --data-root "$DATA_ROOT" \
  --json

echo "Present deterministic validation and Codex pixel judgments separately." >&2
echo "STOP: require scene approval" >&2
