#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
VENV_PYTHON="${VENV_DIR}/bin/python"

supported_python() {
    "$1" -c 'import sys; exit(0 if sys.version_info[:2] >= (3, 12) else 1)' >/dev/null 2>&1
}

find_python() {
    if [[ -n "${PYTHON:-}" ]]; then
        if command -v "${PYTHON}" >/dev/null 2>&1 && supported_python "${PYTHON}"; then
            echo "${PYTHON}"
            return 0
        fi
        return 1
    fi

    for candidate in python3.14 python3.13 python3.12 python3; do
        if command -v "${candidate}" >/dev/null 2>&1 && supported_python "${candidate}"; then
            echo "${candidate}"
            return 0
        fi
    done

    return 1
}

PYTHON_BIN=""
if [[ -e "${VENV_DIR}" || -L "${VENV_DIR}" ]]; then
    if [[ ! -x "${VENV_PYTHON}" ]] || ! supported_python "${VENV_PYTHON}"; then
        echo "Error: ${VENV_DIR} must contain a working Python 3.12 or newer environment. Move it aside before rerunning setup." >&2
        exit 1
    fi
    PYTHON_BIN="${VENV_PYTHON}"
fi

if [[ -z "${PYTHON_BIN}" || -n "${PYTHON:-}" ]]; then
    PYTHON_BIN="$(find_python || true)"
fi

if [[ -z "${PYTHON_BIN}" ]]; then
    cat >&2 <<'EOF'
Error: Could not find a supported Python.

Install Python 3.12 or newer, then rerun this script. If PYTHON is set, it must name a supported interpreter.

On macOS with Homebrew:

    brew install python@3.12
    PYTHON=python3.12 ./scripts/setup.sh
EOF
    exit 1
fi

PYTHON_VERSION="$("${PYTHON_BIN}" - <<'PY'
import sys
print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')
PY
)"

echo "Using Python ${PYTHON_VERSION}: ${PYTHON_BIN}"

if [[ -x "${VENV_PYTHON}" ]]; then
    REQUESTED_VERSION="$("${PYTHON_BIN}" -c 'import sys; print(sys.version_info[:2])')"
    EXISTING_VERSION="$("${VENV_PYTHON}" -c 'import sys; print(sys.version_info[:2])')"
    if [[ "${REQUESTED_VERSION}" != "${EXISTING_VERSION}" ]]; then
        echo "Error: existing environment uses Python ${EXISTING_VERSION}, but PYTHON selects ${REQUESTED_VERSION}. Unset PYTHON to reuse it, or move ${VENV_DIR} aside first." >&2
        exit 1
    fi
    echo "Reusing virtual environment: ${VENV_DIR}"
else
    "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

if [[ ! -x "${VENV_PYTHON}" ]]; then
    echo "Error: virtual environment was not created correctly." >&2
    exit 1
fi

if ! "${VENV_PYTHON}" -m pip --version >/dev/null 2>&1; then
    "${VENV_PYTHON}" -m ensurepip --upgrade --default-pip
fi

"${VENV_PYTHON}" -m pip install --upgrade pip setuptools wheel

"${VENV_PYTHON}" -m pip install -r "${ROOT_DIR}/requirements.txt"

echo
echo "Setup complete."
echo
echo "Activate the environment with:"
echo "    source .venv/bin/activate"
echo
echo "Build the spec with:"
echo "    make build"
echo
echo "Build all specs with:"
echo "    make build-all"
echo
echo "List available specs with:"
echo "    make list-specs"
