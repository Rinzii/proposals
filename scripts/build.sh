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
    ./scripts/build.sh drafts/cpp/P1219R3.bs
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
    local python_bin="${VENV_DIR}/bin/python"
    if [[ ! -x "${python_bin}" ]]; then
        python_bin="${PYTHON:-python3}"
    fi
    "${python_bin}" -c 'import os, sys; print(os.path.abspath(os.path.join(sys.argv[1], sys.argv[2])))' "${ROOT_DIR}" "$1"
}

output_for() {
    local spec_file="$1"
    local relative="${spec_file#${ROOT_DIR}/}"
    printf '%s\n' "${ROOT_DIR}/out/${relative%.bs}.html"
}

write_alias() {
    local output_file="$1"
    local target="$2"
    local paper="$3"
    mkdir -p "$(dirname "${output_file}")"
    cat > "${output_file}" <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>${paper}: Latest revision</title>
</head>
<body>
<p>Continue to the <a href="${target}">latest ${paper} draft</a>.</p>
<script>location.replace("${target}" + location.search + location.hash);</script>
</body>
</html>
EOF
}

update_latest_alias() {
    local spec_file="$1"
    local output_file="$2"
    [[ "${output_file}" == "$(output_for "${spec_file}")" ]] || return 0

    [[ "${spec_file}" == *.bs ]] || return 0
    local relative_source="${spec_file#${ROOT_DIR}/}"
    case "$(dirname "${relative_source}")" in cpp|drafts/cpp) ;; *) return 0 ;; esac
    local stem="$(basename "${spec_file}" .bs)"
    local paper="${stem%R*}"
    local revision="${stem##*R}"
    [[ "${paper}" == P* ]] || return 0
    case "${paper#P}" in ''|*[!0-9]*) return 0 ;; esac
    case "${revision}" in ''|*[!0-9]*) return 0 ;; esac

    local latest_spec="${spec_file}"
    local latest_revision=-1
    local candidate_spec candidate_stem candidate_revision
    local revision_stems=()
    for candidate_spec in "${ROOT_DIR}/cpp/${paper}"R*.bs "${ROOT_DIR}/drafts/cpp/${paper}"R*.bs; do
        [[ -f "${candidate_spec}" ]] || continue
        candidate_stem="$(basename "${candidate_spec}" .bs)"
        candidate_revision="${candidate_stem##*R}"
        case "${candidate_revision}" in ''|*[!0-9]*) continue ;; esac
        revision_stems+=("${candidate_stem}")
        if (( 10#${candidate_revision} >= latest_revision )); then
            latest_spec="${candidate_spec}"
            latest_revision="$((10#${candidate_revision}))"
        fi
    done

    local latest_output="$(output_for "${latest_spec}")"
    if [[ "${latest_spec}" != "${spec_file}" && ( ! -s "${latest_output}" || "${latest_spec}" -nt "${latest_output}" ) ]]; then
        build_one "${latest_spec}" "${latest_output}"
        return
    fi

    local latest_relative="${latest_spec#${ROOT_DIR}/}"
    local target="${latest_relative%.bs}.html"
    write_alias "${ROOT_DIR}/out/cpp/${paper}.html" "../${target}" "${paper}"
    write_alias "${ROOT_DIR}/out/drafts/cpp/${paper}.html" "../../${target}" "${paper}"
    write_alias "${ROOT_DIR}/out/${paper}/index.html" "../${target}" "${paper}"
    for candidate_stem in "${revision_stems[@]}"; do
        write_alias "${ROOT_DIR}/out/${candidate_stem}/index.html" "../${paper}/" "${paper}"
    done
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

    "${BIKESHED_BIN}" --no-update spec "${spec_file}" "${output_file}"
    update_latest_alias "${spec_file}" "${output_file}"
}

cd "${ROOT_DIR}"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    usage
    exit 0
fi

if [[ $# -eq 0 ]]; then
    exec make build
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

SPEC_FILE="$(normalize_path "$1")"

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
