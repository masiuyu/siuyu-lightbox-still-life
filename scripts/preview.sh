#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 || $# -gt 4 ]]; then
  echo "Usage: preview.sh PROJECT_ID DATA_ROOT VISUAL_DIRECTION_JSON [SEED]" >&2
  exit 1
fi

PROJECT_ID=$1
DATA_ROOT=$2
VISUAL_DIRECTION_JSON=$3
SEED=${4:-731}
TEMPLATES=archive_research_v1,product_focus_v1,art_lab_v1

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
BUILD_JSON=$(pnpm --silent --dir "$ROOT" --filter @lightbox/cli start -- scenes build "$PROJECT_ID" \
  --templates "$TEMPLATES" \
  --seed "$SEED" \
  --visual-direction "$VISUAL_DIRECTION_JSON" \
  --data-root "$DATA_ROOT" \
  --json)
printf '%s\n' "$BUILD_JSON"

SCENE_IDS=$(python3 -c 'import json,sys; print(",".join(json.loads(sys.stdin.read())["sceneIds"]))' <<<"$BUILD_JSON")
pnpm --silent --dir "$ROOT" --filter @lightbox/cli start -- previews render "$PROJECT_ID" \
  --scene-ids "$SCENE_IDS" \
  --data-root "$DATA_ROOT" \
  --json

echo "Validate every returned scene and present previews with issue overlays." >&2
echo "STOP: Codex must inspect persisted preview pixels and persist a seven-item review." >&2
echo "STOP: require scene approval" >&2
