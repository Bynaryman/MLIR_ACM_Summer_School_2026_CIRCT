# MLIR Summer School 2026 CIRCT tutorial

This directory supports the complete CIRCT session: importing and optimizing a
small SystemVerilog design, inspecting AIG synthesis statistics, and building
an out-of-tree MLIR/CIRCT pass. The environment is pinned to CIRCT
`firtool-1.147.0`.

## Start the container

```bash
docker run -it ghcr.io/bynaryman/mlir-summer-school-2026-circt:latest
```

Docker downloads the image automatically when needed. To build the same image
locally, run these commands from this directory:

```bash
docker build -t mlir-summer-school-2026-circt .
docker run -it mlir-summer-school-2026-circt
```

## Directory structure

```text
tutorial/
|-- examples/
|   |-- fma.sv                       # CIRCT command-line tour
|   |-- aig-before.sv                # Two-multiplier architecture
|   |-- aig-after.sv                 # Factored architecture
|   `-- e4m3fn-mul.mlir              # Custom pass input
|-- include/Tutorial/Passes.h        # Pass registration API
|-- lib/LowerE4M3FNToComb.cpp        # Student pass exercise
|-- tools/circt-tutorial-opt/        # Course pass driver
|-- scripts/
|   |-- build.sh                     # Configure and compile
|   |-- run.sh                       # Run the custom pass
|   |-- compare-aig.py               # Compare AIG size and depth
|   `-- test-e4m3-all.py             # Test all 65,536 input pairs
|-- test/e4m3fn-exhaustive-tb.sv     # Verilog testbench
|-- CMakeLists.txt
`-- Dockerfile
```

## What is `circt-tutorial-opt`?

The `-opt` suffix follows `mlir-opt` and `circt-opt`: it means the executable is
a command-line driver for parsing MLIR and running passes. The installed
`circt-opt` cannot know about a pass compiled in this separate project, so this
small driver links the course pass directly.

The driver is for the whole course project, not specifically E4M3. It registers
the Arith, HW, and Comb dialects, the course passes, and the standard
canonicalization and common-subexpression-elimination passes. Additional course
passes can be registered in the same executable later. The E4M3 name remains
only on the E4M3 pass, example, and tests.

## CIRCT and AIG exercise

Import and optimize the FMA example:

```bash
mkdir -p build
circt-verilog examples/fma.sv -o build/fma.mlir
circt-opt build/fma.mlir --comb-int-range-narrowing --canonicalize \
  -o build/fma-optimized.mlir
```

Compare the synthesized AIG node count and maximum logic level of two
equivalent architectures:

```bash
./scripts/compare-aig.py
```

The script first uses `circt-lec` to prove that `a*b + a*c` and `a*(b+c)` are
equivalent. It then reports their AIG area and depth. The factored circuit uses
fewer AIG nodes but has a slightly longer path, making the area/delay tradeoff
visible. The three-argument form works with any two synthesizable MLIR files:

```bash
./scripts/compare-aig.py BEFORE.mlir AFTER.mlir TOP_MODULE
```

## Build and run the custom pass

```bash
./scripts/build.sh
./scripts/run.sh
```

Students edit `lib/LowerE4M3FNToComb.cpp`. The pass replaces this constrained
floating-point island with CIRCT Comb operations:

```text
i8 -> arith.bitcast -> f8E4M3FN
                             \
                              arith.mulf -> arith.bitcast -> i8
                             /
i8 -> arith.bitcast -> f8E4M3FN
```

The starter computes only the sign and fills the remaining seven bits with
zero. The exercise adds field extraction, hidden bits, significand
multiplication, exponent arithmetic, normalization, rounding, special cases,
and packing.

Run the pass manually with:

```bash
build/bin/circt-tutorial-opt examples/e4m3fn-mul.mlir \
  --lower-e4m3fn-to-comb --canonicalize -o lowered.mlir
```

## Exhaustive E4M3 test

```bash
./scripts/test-e4m3-all.py
```

It uses MLIR constant folding as the E4M3FN reference, generates all
`256 x 256 = 65,536` operand pairs, emits the lowered circuit as Verilog, and
simulates it with Icarus Verilog. It checks zeros, subnormals, normal values,
overflow, and NaN encodings. The intentionally incomplete starter is expected
to fail this test; the complete solution should pass it.
