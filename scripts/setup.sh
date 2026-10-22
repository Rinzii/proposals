#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f md/wg21/paper.mk ]]; then
    git submodule update --init md/wg21
fi

for patch_file in "$(pwd)"/md/patches/*.patch; do
    if git -C md/wg21 apply --check "$patch_file" 2>/dev/null; then
        git -C md/wg21 apply "$patch_file"
    else
        git -C md/wg21 apply --reverse --check "$patch_file"
    fi
done

make -C "papers/${1:-1219_homogeneous_parameters}" setup
