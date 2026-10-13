#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ $# -eq 0 ]]; then
    exec make watch
fi

WATCH_SPEC="$1"
if [[ "${WATCH_SPEC}" != "--all" ]]; then
    if [[ ! -f "${WATCH_SPEC}" ]]; then
        echo "Error: Bikeshed source does not exist: ${WATCH_SPEC}" >&2
        exit 1
    fi
    if [[ -x "${ROOT}/.venv/bin/bikeshed" ]]; then
        BIKESHED="${ROOT}/.venv/bin/bikeshed"
    elif command -v bikeshed >/dev/null 2>&1; then
        BIKESHED="$(command -v bikeshed)"
    else
        echo "Error: Bikeshed was not found. Run ./scripts/setup.sh first." >&2
        exit 1
    fi
    WATCH_OUT="${2:-out/${WATCH_SPEC#${ROOT}/}}"
    if [[ $# -lt 2 ]]; then WATCH_OUT="${WATCH_OUT%.bs}.html"; fi
    mkdir -p "$(dirname "${WATCH_OUT}")"
    exec "${BIKESHED}" --no-update watch "${WATCH_SPEC}" "${WATCH_OUT}"
fi

MAKE_CMD=(make build-all)

if command -v watchexec >/dev/null 2>&1; then
    watchexec -w cpp -w drafts/cpp -w scripts -w Makefile -- "${MAKE_CMD[@]}"
elif command -v entr >/dev/null 2>&1; then
    find cpp drafts/cpp scripts -type f \( -name '*.bs' -o -name '*.sh' \) | sort | entr -c "${MAKE_CMD[@]}"
else
    echo "Install watchexec or entr for watch mode. Running one build instead."
    "${MAKE_CMD[@]}"
fi
