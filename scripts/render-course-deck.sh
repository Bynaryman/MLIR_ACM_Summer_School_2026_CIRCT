#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# Every file in dist is generated; clear stale profile directories first.
if [[ -d dist ]]; then
  find dist -mindepth 1 -delete
fi

quarto render mlir-circt-summer-school.qmd

printf '%s\n' \
  "Course deck: dist/mlir-circt-summer-school-2026.html"
