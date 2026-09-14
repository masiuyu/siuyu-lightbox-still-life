#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 || $# -gt 4 ]]; then
  echo "Usage: ingest.sh PROJECT_ID INPUT_DIRECTORY DATA_ROOT [HINTS_JSON]" >&2
  exit 1
fi

PROJECT_ID=$1
INPUT_DIRECTORY=$2
DATA_ROOT=$3
HINTS_JSON=${4:-}
TEMP_HINTS=""

cleanup() {
  if [[ -n "$TEMP_HINTS" && -f "$TEMP_HINTS" ]]; then
    rm -f "$TEMP_HINTS"
  fi
}
trap cleanup EXIT

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
CLI=(pnpm --silent --dir "$ROOT" --filter @lightbox/cli start --)

if [[ "${LIGHTBOX_SKIP_CREATE:-0}" != "1" ]]; then
  "${CLI[@]}" project create "$PROJECT_ID" --data-root "$DATA_ROOT" --json
fi
"${CLI[@]}" ingest "$PROJECT_ID" "$INPUT_DIRECTORY" --data-root "$DATA_ROOT" --json

if [[ -z "$HINTS_JSON" ]]; then
  TEMP_HINTS=$(mktemp)
  printf '{"integrationIntent":"merge_all","userHints":[]}\n' > "$TEMP_HINTS"
  HINTS_JSON=$TEMP_HINTS
fi
"${CLI[@]}" classify "$PROJECT_ID" --hints "$HINTS_JSON" --data-root "$DATA_ROOT" --json

echo "STOP: require asset-manifest approval" >&2
