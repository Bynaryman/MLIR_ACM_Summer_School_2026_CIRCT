#!/usr/bin/env bash
set -euo pipefail
cmake --build build
build/bin/circt-tutorial-opt examples/e4m3fn-mul.mlir \
  --lower-e4m3fn-to-comb \
  --canonicalize
