#!/usr/bin/env bash
set -euo pipefail
cmake --build build
build/bin/circt-tutorial-opt examples/ex6_arith_muli.mlir \
  --tutorial-func-to-hw \
  --map-arith-to-comb \
  --canonicalize
