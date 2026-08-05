# CIRCT hands-on cheat sheet

Run these commands from `/workspace` inside the course container. Generated
files belong under `build/` unless an exercise explicitly names another path.

Open this file at any time with:

```bash
less CHEATSHEET.md
```

In `less`, type `/Python`, `/synthesis`, or another word to search; press `q`
to leave.

## Start and build

The published image already contains the tools and a built
`circt-tutorial-opt`:

```bash
docker run -it ghcr.io/bynaryman/mlir-summer-school-2026-circt:latest
circt-opt --version
```

Rebuild the course optimizer after changing its C++ source:

```bash
./scripts/build.sh
```

The script is equivalent to:

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build build
```

Run the supplied integer pipeline:

```bash
./scripts/run.sh
```

## Tool map

| Task | Command |
|---|---|
| SystemVerilog to CIRCT IR | `circt-verilog input.sv -o output.mlir` |
| Run upstream CIRCT passes | `circt-opt input.mlir PASS... -o output.mlir` |
| Run the course pass | `circt-tutorial-opt input.mlir PASS... -o output.mlir` |
| Check two modules | `circt-lec --c1 TOP before.mlir --c2 TOP after.mlir` |
| CIRCT IR to SystemVerilog | `firtool input.mlir -o output.sv` |
| Compile a testbench | `iverilog -g2012 -s TOP -o simulation design.sv testbench.sv` |
| Run a simulation | `vvp simulation` |
| CIRCT IR to an AIG | `circt-synth input.mlir --top=TOP -o aig.mlir` |
| AIG IR to AIGER | `circt-translate aig.mlir --export-aiger -o circuit.aiger` |

Use `-o -` or omit `-o` when you want a tool to print to the terminal.

## Inspect available passes

```bash
circt-opt --help | less
circt-opt --help | grep -i arith
circt-opt --help | grep -i comb
circt-tutorial-opt --help | grep -i tutorial
```

Print the IR after every pass when debugging a pipeline:

```bash
circt-opt input.mlir PASS... --mlir-print-ir-after-all -o /dev/null
```

Parse and verify an MLIR file without keeping another output:

```bash
circt-opt input.mlir -o /dev/null
```

## SystemVerilog, MLIR, and back

SystemVerilog to CIRCT IR:

```bash
mkdir -p build
circt-verilog rtl/ex1_fma.sv -o build/ex1_fma.mlir
```

Run a pass pipeline:

```bash
circt-opt build/ex1_fma.mlir \
  --comb-int-range-narrowing \
  --canonicalize \
  -o build/ex1_fma_optimized.mlir
```

CIRCT IR to SystemVerilog:

```bash
firtool build/ex1_fma_optimized.mlir -o build/ex1_fma_optimized.sv
```

Compile the emitted SystemVerilog back to CIRCT IR:

```bash
circt-verilog build/ex1_fma_optimized.sv \
  -o build/ex1_fma_roundtrip.mlir
```

Compile and run emitted SystemVerilog when you have a testbench:

```bash
iverilog -g2012 -s TOP_MODULE \\
  -o build/simulation DESIGN.sv TESTBENCH.sv
vvp build/simulation
```

## Prove equivalence

Both files must contain the named top module. Pass the module name without `@`:

```bash
circt-lec \
  --c1 ex1_fma build/ex1_fma.mlir \
  --c2 ex1_fma build/ex1_fma_optimized.mlir
```

Expected output:

```text
c1 == c2
```

`c1 != c2` means CIRCT found a counterexample or the circuits are genuinely
different.

## Synthesis statistics

Create the AIG and JSON reports:

```bash
rm -rf build/report
circt-synth build/ex1_fma_optimized.mlir \
  --top=ex1_fma \
  --analysis-output=build/report \
  --analysis-output-format=json \
  -o build/ex1_fma_aig.mlir
```

Inspect node counts and logic depth:

```bash
python3 -m json.tool build/report/resource_usage.json | less
python3 -m json.tool build/report/longest_path.json | less
```

Export the graph as AIGER when another tool needs it:

```bash
circt-translate build/ex1_fma_aig.mlir \
  --export-aiger -o build/ex1_fma.aiger
```

Prove equivalence and compare AIG nodes and depth in one command:

```bash
./scripts/compare-aig.py BEFORE.mlir AFTER.mlir TOP_MODULE
```

Exercise 5 has ready-made inputs, so this shorter command is enough:

```bash
./scripts/compare-aig.py
```

## Integer arithmetic pipeline

Convert the function boundary, then lower integer arithmetic:

```bash
circt-tutorial-opt examples/ex6_arith_muli.mlir \
  --tutorial-func-to-hw \
  -o build/ex6_hw_arith.mlir

circt-opt build/ex6_hw_arith.mlir \
  --map-arith-to-comb \
  --canonicalize \
  -o build/ex6_hw_comb.mlir
```

Emit SystemVerilog or synthesize the result:

```bash
firtool build/ex6_hw_comb.mlir -o build/ex6_hw_comb.sv
circt-synth build/ex6_hw_comb.mlir --top=ex6_mul -o build/ex6_aig.mlir
```

## Run the Python lowering

Edit `scripts/lower-e4m3fn.py`, then run:

```bash
python scripts/lower-e4m3fn.py examples/ex7_e4m3fn_mul.mlir \
  -o build/ex7_function_comb.mlir

circt-tutorial-opt build/ex7_function_comb.mlir \
  --tutorial-func-to-hw \
  --canonicalize \
  -o build/ex7_hw_comb.mlir

firtool build/ex7_hw_comb.mlir -o build/ex7_hw_comb.sv
```

## Python rewrite skeleton

The exercise matches the output `arith.bitcast`, builds an `i8` CIRCT
datapath, and replaces that cast:

```python
from mlir.ir import IntegerType

from circt_tutorial import comb, hw, match_e4m3_island
from circt_tutorial.driver import run_cli


def lower_e4m3_mul(out_cast, rewriter):
    matched = match_e4m3_island(out_cast)
    if matched is None:
        return True
    lhs, rhs = matched

    with rewriter.ip:
        i1 = IntegerType.get_signless(1)
        i3 = IntegerType.get_signless(3)
        i4 = IntegerType.get_signless(4)
        i5 = IntegerType.get_signless(5)
        i7 = IntegerType.get_signless(7)
        i8 = IntegerType.get_signless(8)

        lhs_sign = comb.ExtractOp.create(7, i1, lhs).result
        rhs_sign = comb.ExtractOp.create(7, i1, rhs).result
        sign = comb.XorOp.create(lhs_sign, rhs_sign).result

        zero_payload = hw.ConstantOp.create(i7, 0).result
        result = comb.ConcatOp.create(sign, zero_payload).result

    rewriter.replace_op(out_cast, [result])
    return False


if __name__ == "__main__":
    run_cli(lower_e4m3_mul)
```

Keep the exercise callback convention unchanged:

- return `True` when the operation did not match;
- return `False` after a successful replacement;
- create replacement operations inside `with rewriter.ip:`;
- pass a list of replacement values to `rewriter.replace_op`;
- the replacement must have the same `i8` type as `out_cast`.

## Supplied Python builders

Every builder returns a small wrapper; append `.result` to obtain its SSA
value.

| CIRCT operation | Python builder |
|---|---|
| Extract bits | `comb.ExtractOp.create(low_bit, result_type, value).result` |
| Concatenate, MSB first | `comb.ConcatOp.create(msb, ..., lsb).result` |
| Select | `comb.MuxOp.create(condition, true_value, false_value).result` |
| Add | `comb.AddOp.create(lhs, rhs, ...).result` |
| Subtract | `comb.SubOp.create(lhs, rhs).result` |
| Multiply | `comb.MulOp.create(lhs, rhs).result` |
| AND | `comb.AndOp.create(lhs, rhs).result` |
| XOR | `comb.XorOp.create(lhs, rhs).result` |
| Shift left | `comb.ShlOp.create(value, amount).result` |
| Constant | `hw.ConstantOp.create(result_type, integer).result` |

Examples:

```python
sign = comb.XorOp.create(lhs_sign, rhs_sign).result
fraction = comb.ExtractOp.create(0, i3, value).result
packed = comb.ConcatOp.create(sign, exponent, fraction).result
one = hw.ConstantOp.create(i1, 1).result
```

`comb` arithmetic is width-explicit. Extend operands with `comb.concat` before
an operation when their widths differ; do not rely on implicit language casts.

## Test the E4M3 exercise

Check the supplied complete RTL reference over all 65,536 inputs:

```bash
./scripts/test-e4m3-all.py
```

Check the exact normal finite cases required by Exercise 7:

```bash
./scripts/test-e4m3-all.py --pass --normal-path
```

Check every input pair after implementing the optional special cases and
rounding:

```bash
./scripts/test-e4m3-all.py --pass
```

Test the instructor normal-path implementation without replacing your file:

```bash
./scripts/test-e4m3-all.py \
  --pass --normal-path \
  --lowerer solutions/lower-e4m3fn-normal.py
```

## Common checks

| Symptom | Check |
|---|---|
| `circt-tutorial-opt` is missing | Run `./scripts/build.sh` |
| `arith.mulf` remains | Confirm the input matches the bitcast-mul-bitcast island |
| CIRCT reports a type error | Check every operand width and the concat order |
| The output file cannot be created | Create its parent with `mkdir -p build` |
| `circt-lec` cannot find a circuit | Pass the correct top module name without `@` |
| Synthesis reports already exist | Remove the old report directory first |
| The normal-path test fails | Inspect the first failing operands before adding more logic |
