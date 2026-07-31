#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/figures/arithmetic/e4m3-rewrite-datapath.tex"
OUTPUT_DIR="$ROOT/assets/images/arithmetic"
BUILD_DIR="$(mktemp -d)"
LAYERS=(base target sign significand normalize exponent pack)

cleanup() {
  rm -rf "$BUILD_DIR"
}
trap cleanup EXIT

mkdir -p "$OUTPUT_DIR"

for index in "${!LAYERS[@]}"; do
  layer="${LAYERS[$index]}"
  job="e4m3-rewrite-$layer"

  cd "$ROOT"
  pdflatex -interaction=nonstopmode -halt-on-error \
    -jobname="$job" \
    -output-directory="$BUILD_DIR" \
    "\\def\\DiagramLayer{$index}\\input{$SOURCE}" >/dev/null

  pdftocairo -svg -f 1 -l 1 \
    "$BUILD_DIR/$job.pdf" \
    "$OUTPUT_DIR/$job.svg"
done

printf '%s\n' "$OUTPUT_DIR"/e4m3-rewrite-*.svg
