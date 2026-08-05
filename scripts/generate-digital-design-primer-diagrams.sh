#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/figures/digital-design/primer-diagrams.tex"
OUTPUT_DIR="$ROOT/assets/images/digital-design"
BUILD_DIR="$(mktemp -d)"
DIAGRAMS=(
  register-timing-question
  register-timing-rising
  register-timing-negedge
  register-timing-sync-reset
  register-timing-async-reset
  clocked-datapath
  stored-program-models
  spatial-models
  cmos-inverter
  cmos-inverter-low
  cmos-inverter-high
  logic-inverter
)

cleanup() {
  rm -rf "$BUILD_DIR"
}
trap cleanup EXIT

mkdir -p "$OUTPUT_DIR"

for index in "${!DIAGRAMS[@]}"; do
  diagram="${DIAGRAMS[$index]}"

  cd "$ROOT"
  pdflatex -interaction=nonstopmode -halt-on-error \
    -jobname="$diagram" \
    -output-directory="$BUILD_DIR" \
    "\\def\\DiagramLayer{$index}\\input{$SOURCE}" >/dev/null

  pdftocairo -svg -f 1 -l 1 \
    "$BUILD_DIR/$diagram.pdf" \
    "$OUTPUT_DIR/$diagram.svg"
done

for diagram in "${DIAGRAMS[@]}"; do
  printf '%s\n' "$OUTPUT_DIR/$diagram.svg"
done
