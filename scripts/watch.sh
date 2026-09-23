#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

WATCH_SPEC="${1:-drafts/cpp/invoking_annotations_r0.bs}"

if [[ "${WATCH_SPEC}" == "--all" ]]; then
    MAKE_CMD=(make build-all)
else
    MAKE_CMD=(make build "SPEC=${WATCH_SPEC}")
fi

if command -v watchexec >/dev/null 2>&1; then
    watchexec -w cpp -w drafts/cpp -w scripts -w Makefile -- "${MAKE_CMD[@]}"
elif command -v entr >/dev/null 2>&1; then
    find cpp drafts/cpp scripts -type f \( -name '*.bs' -o -name '*.sh' \) | sort | entr -c "${MAKE_CMD[@]}"
else
    echo "Install watchexec or entr for watch mode. Running one build instead."
    "${MAKE_CMD[@]}"
fi
