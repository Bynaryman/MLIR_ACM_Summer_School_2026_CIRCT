#!/usr/bin/env bash
set -euo pipefail

circt-tutorial-opt exercises/ex6_arith_muli.mlir \
  --tutorial-func-to-hw \
  -o exercises/ex6_hw_arith.mlir
circt-opt exercises/ex6_hw_arith.mlir \
  --map-arith-to-comb \
  --canonicalize \
  -o exercises/ex6_hw_comb.mlir
cat exercises/ex6_hw_comb.mlir
