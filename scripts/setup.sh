#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"

find_python() {
    if [[ -n "${PYTHON:-}" ]] && command -v "${PYTHON}" >/dev/null 2>&1; then
        echo "${PYTHON}"
        return 0
    fi

    for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "${candidate}" >/dev/null 2>&1; then
            if "${candidate}" - <<'PY' >/dev/null 2>&1
import sys
raise SystemExit(0 if (3, 10) <= sys.version_info[:2] < (3, 14) else 1)
PY
            then
                echo "${candidate}"
                return 0
            fi
        fi
    done

    return 1
}

PYTHON_BIN="$(find_python || true)"

if [[ -z "${PYTHON_BIN}" ]]; then
    cat >&2 <<'EOF'
Error: Could not find a supported Python.

Install Python 3.10, 3.11, 3.12, or 3.13, then rerun this script.

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

if [[ -d "${VENV_DIR}" ]]; then
    echo "Removing existing virtual environment: ${VENV_DIR}"
    rm -rf "${VENV_DIR}"
fi

"${PYTHON_BIN}" -m venv "${VENV_DIR}"

VENV_PYTHON="${VENV_DIR}/bin/python"
VENV_PIP="${VENV_DIR}/bin/pip"

if [[ ! -x "${VENV_PYTHON}" ]]; then
    echo "Error: virtual environment was not created correctly." >&2
    exit 1
fi

if [[ ! -x "${VENV_PIP}" ]]; then
    "${VENV_PYTHON}" -m ensurepip --upgrade --default-pip
fi

"${VENV_PYTHON}" -m pip install --upgrade pip setuptools wheel

if [[ -f "${ROOT_DIR}/requirements.txt" ]]; then
    "${VENV_PYTHON}" -m pip install -r "${ROOT_DIR}/requirements.txt"
else
    "${VENV_PYTHON}" -m pip install bikeshed
fi

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
