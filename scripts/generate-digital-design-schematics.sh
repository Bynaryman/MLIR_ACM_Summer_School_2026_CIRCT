#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="$ROOT_DIR/assets/images/digital-design/yosys"
DOT_DIR="$ROOT_DIR/tmp/digital-design/yosys"
IMAGE="openroad/orfs:latest"

mkdir -p "$OUTPUT_DIR" "$DOT_DIR"

for top in e4m3_mul_parts; do
  docker run --rm \
    --user "$(id -u):$(id -g)" \
    -v "$ROOT_DIR:/work" \
    -w /work \
    "$IMAGE" \
    yosys -q -p "read_verilog -sv figures/digital-design/concepts.sv; hierarchy -top $top; proc; opt; clean; show -stretch -width -notitle -format dot -prefix tmp/digital-design/yosys/$top $top"

  dot -Tsvg "$DOT_DIR/$top.dot" -o "$OUTPUT_DIR/$top.svg"
done

printf 'Generated schematics in %s\n' "$OUTPUT_DIR"
