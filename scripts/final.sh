#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: final.sh PROJECT_ID DATA_ROOT" >&2
  exit 1
fi

PROJECT_ID=$1
DATA_ROOT=$2

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
pnpm --silent --dir "$ROOT" --filter @lightbox/cli start -- render final "$PROJECT_ID" \
  --data-root "$DATA_ROOT" \
  --json
