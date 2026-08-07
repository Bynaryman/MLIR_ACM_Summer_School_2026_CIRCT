# MLIR Summer School 2026 CIRCT tutorial

Parts 1 and 2 reproduce the hands-on flow from the
[CIRCT Tutorial 2026](https://github.com/cowardsa/CIRCT_TUTORIAL_2026) by Sam
Coward and Louis Ledoux. Part 3 adds two summer-school lowering exercises: a
composed integer lowering, then a Python rewrite that materializes an E4M3
`arith.mulf` implementation with CIRCT `comb` operations.

## Start the container

Use the pre-built course image:

```bash
git clone https://github.com/Bynaryman/MLIR_ACM_Summer_School_2026_CIRCT
cd MLIR_ACM_Summer_School_2026_CIRCT/tutorial
docker run -it -v "$PWD:/workspace" \
  ghcr.io/bynaryman/mlir-summer-school-2026-circt:latest
```

Or build the same image from the `tutorial/` directory:

```bash
docker build -t mlir-summer-school-2026-circt .
docker run -it -v "$PWD:/workspace" mlir-summer-school-2026-circt
```

The bind mount maps the host `tutorial/` folder to `/workspace`. Use the same
`-v "$PWD:/workspace"` option each time: edit with the host IDE, then run and
test those files inside Docker. Generated files under `build/` also persist on
the host.

No setup or activation is needed inside the image. Its `/opt/mlir-python`
virtual environment is already on `PATH`; it isolates the pinned upstream MLIR
Python bindings used by Exercises 7-8. CIRCT, CMake, Ninja, GCC, Icarus
Verilog, Z3, and the remaining tools are installed in the same image.

## Files

```text
tutorial/
|-- exercises/
|   |-- ex1_fma.sv                 # Exercise 1 source
|   |-- ex5_aig.sv                 # Exercise 5 input
|   |-- ex6_arith_muli.mlir        # Exercise 6 integer input
|   |-- ex6_arith_mulf.mlir        # Same pipeline, unsupported float op
|   |-- ex7_e4m3fn_mul.mlir        # Exercise 7 arith.mulf input
|   |-- ex7_e4m3fn_mul_reference.sv # Complete E4M3 reference RTL
|   `-- ex8_e4m3fn_square.mlir     # Exercise 8 squarer input
|-- solutions/
|   |-- ex5_aig_optimized.sv       # Exercise 5 revealed solution
|   |-- lower-e4m3fn-normal.py     # Exercise 7 normal-path reference
|   `-- lower-e4m3fn-square.py     # Exercise 8 squarer reference
|-- include/Tutorial/Passes.h       # Course pass registration
|-- python/circt_tutorial/          # Supplied Python matcher and op builders
|-- lib/
|   |-- FuncToHWModule.cpp          # Function boundary to HW module pass
|   `-- Passes.cpp                  # Register the supplied pass
|-- tools/circt-tutorial-opt/       # Out-of-tree optimizer driver
|-- scripts/
|   |-- build.sh                    # Build circt-tutorial-opt
|   |-- run.sh                      # Run Exercise 6
|   |-- lower-e4m3fn.py             # Exercise 7 rewrite
|   |-- lower-e4m3fn-square.py      # Exercise 8 working intermediate
|   |-- compare-aig.py              # Compare Exercise 5 implementations
|   `-- test-e4m3-all.py            # Exhaustive E4M3 checker
|-- test/e4m3fn-exhaustive-tb.sv
|-- requirements.txt                # Pinned MLIR Python bindings
|-- CMakeLists.txt
`-- Dockerfile
```

All student-facing MLIR and SystemVerilog files live in `exercises/`. The
literal tutorial commands keep their intermediate files there too. Put larger
generated reports and binaries under `build/`; that directory is ignored by
Git.

# Part 1: CIRCT basics

## Exercise 1: compile a design

The original tutorial starts from this FMA-like expression:

```systemverilog
assign d = (a * b) + (c * 1'd1);
```

Print the CIRCT IR directly:

```bash
circt-verilog exercises/ex1_fma.sv
```

Then save it for the next tools:

```bash
circt-verilog exercises/ex1_fma.sv -o exercises/ex1_fma.mlir
```

Look for the `hw.module` interface and the `comb.concat`, `comb.mul`, and
`comb.add` operations. The prefix of each operation mnemonic names its dialect.

## Exercise 2: optimize a design

```bash
circt-opt exercises/ex1_fma.mlir \
  --comb-int-range-narrowing \
  --canonicalize \
  -o exercises/ex2_fma_optimized.mlir
```

`--comb-int-range-narrowing` proves that the four-bit multiplication needs only
eight bits. `--canonicalize` removes redundant local structure exposed by that
narrowing.

### Try another pass order

Swap the passes and compare the result:

```bash
circt-opt exercises/ex1_fma.mlir \
  --canonicalize \
  --comb-int-range-narrowing \
  -o exercises/ex2_fma_variant.mlir

diff -u exercises/ex2_fma_optimized.mlir exercises/ex2_fma_variant.mlir
```

Narrowing first gives canonicalization a chance to remove the extensions and
truncations it exposes. With the swapped order, those operations remain because
canonicalization has already run.

## Exercise 3: verify a transformation

```bash
circt-lec --c1 ex1_fma exercises/ex1_fma.mlir \
          --c2 ex1_fma exercises/ex2_fma_optimized.mlir
```

The expected result is:

```text
c1 == c2
```

`circt-lec` builds a miter, lowers it to SMT, and asks Z3 whether an input can
make the two outputs differ. `unsat` means that no counterexample exists.

### Break the circuit - 5 minutes

```bash
cp exercises/ex2_fma_optimized.mlir exercises/ex3_fma_broken.mlir
nano exercises/ex3_fma_broken.mlir

circt-lec --c1 ex1_fma exercises/ex1_fma.mlir \
          --c2 ex1_fma exercises/ex3_fma_broken.mlir
```

Introduce a functional bug while keeping the circuit valid and compilable.
Then check that `circt-lec` reports `c1 != c2`.

## Exercise 4: generate SystemVerilog

```bash
firtool exercises/ex2_fma_optimized.mlir
```

`exercises/ex2_fma_optimized.mlir` is created by Exercise 2. Run Exercises 1 and 2
first when following the tutorial in a fresh container.

### Verify the round trip - 5 minutes

1. Save the generated Verilog to a file.
2. Compile it back to CIRCT IR with `circt-verilog`.
3. Use `circt-lec` to verify that the round trip preserved equivalence.

One working sequence is:

```bash
firtool exercises/ex2_fma_optimized.mlir -o exercises/ex4_fma_roundtrip.sv
circt-verilog exercises/ex4_fma_roundtrip.sv -o exercises/ex4_fma_roundtrip.mlir
circt-lec --c1 ex1_fma exercises/ex2_fma_optimized.mlir \
          --c2 ex1_fma exercises/ex4_fma_roundtrip.mlir
```

# Part 2: logic synthesis and reports

`circt-synth` lowers `hw` and `comb` operations to a technology-independent
Boolean network. CIRCT represents that network as an **And-Inverter Graph
(AIG)**: internal vertices are two-input ANDs and edges may be inverted.

An **AIGER** file serializes an AIG for exchange with other EDA tools.
`circt-synth` builds the graph; `circt-translate --export-aiger` writes the
file. AIG node count and depth are structural estimates, not final physical
area or timing.

## Exercise 5: measure a supplied optimization

The source uses four cases:

```systemverilog
out = a ? (b ? -x : -(x + 8'd1))
        : (b ? x + 8'd1 : x);
```

For eight-bit modulo arithmetic, `-(x + 1) == ~x` and `-x == ~x + 1`. The
supplied optimized implementation is:

```systemverilog
assign out = (x ^ {8{a}}) + b;
```

Run the complete import, equivalence, synthesis, and reporting flow:

```bash
./scripts/compare-aig.py
```

The expected result is `c1 == c2`, 149 to 54 AIG nodes, and 13 to 8 logic
levels.

To export the synthesized graph after the script:

```bash
circt-translate build/aig-comparison/after-aig.mlir \
  --export-aiger -o build/aig-comparison/after.aiger
```

# Part 3: arithmetic becomes hardware

## Exercise 6: compose an integer hardware pipeline - 5 minutes

`exercises/ex6_arith_muli.mlir` starts with a `func.func` containing one
`arith.muli`. Two independent transformations produce the hardware:

- The course-specific `--tutorial-func-to-hw` pass turns function arguments and
  results into same-typed module ports and replaces `func.return` with
  `hw.output`. It is supplied boilerplate, not an upstream CIRCT pass.
- CIRCT's `--map-arith-to-comb` maps supported integer arithmetic operations to
  the `comb` dialect.

First inspect the upstream pass inventory:

```bash
circt-opt --help | grep -i arith
circt-opt --help | grep -i func
```

The first command reveals `--map-arith-to-comb`. The second reveals HLS routes
such as `--lower-cf-to-handshake`, but no direct generic conversion from
`func.func` to `hw.module`.

```bash
./scripts/build.sh
./scripts/run.sh
```

The output should contain:

```mlir
%0 = comb.mul %in0, %in1 : i8
```

`scripts/run.sh` deliberately uses two tool invocations and leaves both stages
for inspection:

```text
build/ex6_hw_arith.mlir  # hw.module containing arith.muli
build/ex6_hw_comb.mlir   # hw.module containing comb.mul
```

Now run the same pipeline after changing the arithmetic type:

```bash
circt-tutorial-opt exercises/ex6_arith_mulf.mlir \
  --tutorial-func-to-hw \
  -o build/ex6_float_hw_arith.mlir
circt-opt build/ex6_float_hw_arith.mlir --map-arith-to-comb
```

The command fails on `arith.mulf`. This is intentional: the documented
contract of `map-arith-to-comb` excludes floating-point and vector operations.
Exercise 7 fills that gap for one concrete floating-point operation and format.

## E4M3FN reference

E4M3FN uses one sign bit, four exponent bits, three stored fraction bits, and
an exponent bias of 7. Exponent zero encodes zero or subnormal values. The
format has finite values up to 448 and signed NaNs, but no infinity.

Verify the supplied hardware reference against all `256 x 256 = 65,536`
products generated by MLIR constant folding:

```bash
./scripts/test-e4m3-all.py
```

## Exercise 7: lower E4M3 multiplication - 30 minutes

Start from `exercises/ex7_e4m3fn_mul.mlir` and edit
`scripts/lower-e4m3fn.py`. The function boundary uses `i8` wires. Input and
output `arith.bitcast` operations delimit one `f8E4M3FN` multiplication island,
so the rewrite can replace it with an `i8 -> i8` `comb` datapath without a type
converter.

The upstream MLIR Python bindings supply `RewritePatternSet` and the greedy rewrite
driver. `python/circt_tutorial/` supplies the pattern matcher plus small
`comb`/`hw` builders. The starter callback also defines the integer type aliases
used by the staged solutions. The builders emit generic MLIR operations; the
next CIRCT invocation parses and verifies them as registered CIRCT operations.

The passes run in this order:

```bash
python scripts/lower-e4m3fn.py exercises/ex7_e4m3fn_mul.mlir \
  -o build/ex7_function_comb.mlir

circt-tutorial-opt build/ex7_function_comb.mlir \
  --tutorial-func-to-hw --canonicalize \
  -o build/ex7_hw_comb.mlir
```

The Python rewrite handles arithmetic first. `--tutorial-func-to-hw` then
converts only the structural function boundary.

1. Implement field extraction, sign, exponent, significand multiplication,
   normalization, and packing for normal inputs.
2. Check the exact normal finite products covered by the exercise:

```bash
./scripts/test-e4m3-all.py --pass --normal-path
```

This checks 11,892 input pairs and should pass after the normal datapath is
complete. The reference implementation is `solutions/lower-e4m3fn-normal.py`.

3. As an extension, add round-to-nearest-even, zero, subnormal, overflow, and
   NaN behavior. The full checker then covers all 65,536 pairs:

```bash
./scripts/test-e4m3-all.py --pass
```

`exercises/ex7_e4m3fn_mul_reference.sv` is the complete hardware reference for
that extension.

## Exercise 8 (optional): specialize the squarer

`exercises/ex8_e4m3fn_square.mlir` uses the same SSA value twice. The working
intermediate `scripts/lower-e4m3fn-square.py` already matches that stronger
case, decodes once, fixes the sign to zero, and doubles the exponent. Its
`build_square4` helper still emits a generic multiplier; replace only that
helper with the dedicated partial-product squarer. The final reference is
`solutions/lower-e4m3fn-square.py`.

```bash
python scripts/lower-e4m3fn-square.py exercises/ex8_e4m3fn_square.mlir | \
  circt-tutorial-opt --tutorial-func-to-hw --canonicalize \
  -o build/ex8_square_intermediate.mlir
```

Generate `build/ex8_square_specialized.mlir` after editing the helper, then use
`scripts/compare-aig.py` to prove equivalence and report AIG nodes and depth.
With the pinned tools, the generic Exercise 7 lowering has 57 AIG nodes and 14
levels; the supplied square intermediate has 51 nodes and 14 levels; the final
reference has 50 nodes and 13 levels.
