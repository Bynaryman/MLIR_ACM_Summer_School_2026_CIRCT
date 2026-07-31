#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/figures/microprocessor-trends.tex"
OUTPUT="$ROOT/assets/images/motivation/microprocessor-trends.svg"
BUILD_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$BUILD_DIR"
}
trap cleanup EXIT

cd "$ROOT"
latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -outdir="$BUILD_DIR" "$SOURCE"
pdftocairo -svg -f 1 -l 1 \
  "$BUILD_DIR/microprocessor-trends.pdf" "$OUTPUT"

printf '%s\n' "$OUTPUT"
