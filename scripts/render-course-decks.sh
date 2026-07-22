#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# Every file in dist is generated; clear stale deck names before rebuilding.
if [[ -d dist ]]; then
  find dist -mindepth 1 -delete
fi

quarto render mlir-circt-summer-school.qmd --profile student
quarto render mlir-circt-summer-school.qmd --profile instructor

printf '%s\n' \
  "Student deck:    dist/student/mlir-circt-summer-school-2026.html" \
  "Instructor deck: dist/instructor/mlir-circt-summer-school-2026.html"
