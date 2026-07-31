#!/usr/bin/env bash
set -euo pipefail
cmake --build build
build/bin/circt-tutorial-opt examples/ex6_arith_muli.mlir \
  --tutorial-func-to-hw \
  -o build/ex6_hw_arith.mlir
circt-opt build/ex6_hw_arith.mlir \
  --map-arith-to-comb \
  --canonicalize \
  -o build/ex6_hw_comb.mlir
cat build/ex6_hw_comb.mlir
