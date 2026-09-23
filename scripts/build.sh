#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
BIKESHED="${VENV_DIR}/bin/bikeshed"

usage() {
    cat <<EOF
Usage:
    ./scripts/build.sh [SPEC_FILE] [OUTPUT_FILE]
    ./scripts/build.sh --all

Examples:
    ./scripts/build.sh
    ./scripts/build.sh drafts/cpp/invoking_annotations_r0.bs
    ./scripts/build.sh cpp/P1234.bs out/cpp/P1234.html
    ./scripts/build.sh --all
EOF
}

resolve_bikeshed() {
    if [[ -x "${BIKESHED}" ]]; then
        echo "${BIKESHED}"
        return 0
    fi

    if command -v bikeshed >/dev/null 2>&1; then
        command -v bikeshed
        return 0
    fi

    cat >&2 <<EOF
Error: Bikeshed was not found at:

    ${BIKESHED}

Run setup first, or activate an environment with Bikeshed on PATH:

    ./scripts/setup.sh
EOF
    exit 1
}

normalize_path() {
    local path="$1"
    if [[ "${path}" = /* ]]; then
        printf '%s\n' "${path}"
    else
        printf '%s\n' "${ROOT_DIR}/${path}"
    fi
}

output_for() {
    local spec_file="$1"
    local relative="${spec_file#${ROOT_DIR}/}"
    printf '%s\n' "${ROOT_DIR}/out/${relative%.bs}.html"
}

build_one() {
    local spec_file="$1"
    local output_file="$2"

    mkdir -p "$(dirname "${output_file}")"

    echo "Building:"
    echo "    ${spec_file}"
    echo
    echo "Output:"
    echo "    ${output_file}"
    echo

    "${BIKESHED_BIN}" spec "${spec_file}" "${output_file}"
}

cd "${ROOT_DIR}"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    usage
    exit 0
fi

BIKESHED_BIN="$(resolve_bikeshed)"

if [[ "${1:-}" == "--all" ]]; then
    spec_files=()
    while IFS= read -r spec_file; do
        spec_files+=("${spec_file}")
    done < <(find "${ROOT_DIR}/cpp" "${ROOT_DIR}/drafts/cpp" -maxdepth 1 -type f -name '*.bs' 2>/dev/null | sort)

    if [[ "${#spec_files[@]}" -eq 0 ]]; then
        cat >&2 <<EOF
Error: Could not find any Bikeshed .bs files under:

    ${ROOT_DIR}/cpp
    ${ROOT_DIR}/drafts/cpp
EOF
        exit 1
    fi

    for spec_file in "${spec_files[@]}"; do
        build_one "${spec_file}" "$(output_for "${spec_file}")"
    done
    exit 0
fi

SPEC_FILE=""
if [[ $# -ge 1 ]]; then
    SPEC_FILE="$(normalize_path "$1")"
else
    for candidate in \
        "${ROOT_DIR}/drafts/cpp/invoking_annotations_r0.bs"
    do
        if [[ -f "${candidate}" ]]; then
            SPEC_FILE="${candidate}"
            break
        fi
    done
fi

if [[ -z "${SPEC_FILE}" || ! -f "${SPEC_FILE}" ]]; then
    cat >&2 <<EOF
Error: Could not find the requested Bikeshed spec file.

Requested:
    ${1:-<default>}
EOF
    exit 1
fi

if [[ $# -ge 2 ]]; then
    OUTPUT_FILE="$(normalize_path "$2")"
else
    OUTPUT_FILE="$(output_for "${SPEC_FILE}")"
fi

build_one "${SPEC_FILE}" "${OUTPUT_FILE}"
