#!/usr/bin/env python3

import argparse
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "build" / "ex7_e4m3_exhaustive"
PAIR_COUNT = 256 * 256


def run(command, **kwargs):
    print("+", " ".join(str(part) for part in command), flush=True)
    return subprocess.run(command, cwd=ROOT, check=True, **kwargs)


def generate_reference_vectors():
    lhs = bytes(value for value in range(256) for _ in range(256))
    rhs = bytes(range(256)) * 256
    reference_ir = f"""module {{
  func.func @reference() -> vector<{PAIR_COUNT}xi8> {{
    %lhs = arith.constant dense<\"0x{lhs.hex()}\"> : vector<{PAIR_COUNT}xi8>
    %rhs = arith.constant dense<\"0x{rhs.hex()}\"> : vector<{PAIR_COUNT}xi8>
    %lhsf = arith.bitcast %lhs : vector<{PAIR_COUNT}xi8> to vector<{PAIR_COUNT}xf8E4M3FN>
    %rhsf = arith.bitcast %rhs : vector<{PAIR_COUNT}xi8> to vector<{PAIR_COUNT}xf8E4M3FN>
    %product = arith.mulf %lhsf, %rhsf : vector<{PAIR_COUNT}xf8E4M3FN>
    %bits = arith.bitcast %product : vector<{PAIR_COUNT}xf8E4M3FN> to vector<{PAIR_COUNT}xi8>
    return %bits : vector<{PAIR_COUNT}xi8>
  }}
}}
"""

    folded = run(
        [
            "mlir-opt",
            "--canonicalize",
            "--mlir-print-elementsattrs-with-hex-if-larger=1",
        ],
        input=reference_ir,
        text=True,
        capture_output=True,
    ).stdout

    constants = re.findall(r'dense<"0x([0-9A-Fa-f]+)"', folded)
    if len(constants) != 1 or len(constants[0]) != PAIR_COUNT * 2:
        raise RuntimeError("MLIR did not fold the exhaustive reference vector")
    expected = bytes.fromhex(constants[0])

    known_results = {
        (0x38, 0x38): 0x38,
        (0x3C, 0x3C): 0x41,
        (0xB8, 0x38): 0xB8,
    }
    for (lhs_value, rhs_value), result in known_results.items():
        index = lhs_value * 256 + rhs_value
        if expected[index] != result:
            raise RuntimeError("unexpected byte order in MLIR reference vector")

    vectors = WORK / "vectors.hex"
    with vectors.open("w") as output:
        for index, expected_value in enumerate(expected):
            lhs_value, rhs_value = divmod(index, 256)
            output.write(f"{lhs_value:02x} {rhs_value:02x} {expected_value:02x}\n")
    return vectors


def build_pass_verilog():
    optimizer = ROOT / "build" / "bin" / "circt-tutorial-opt"
    if not optimizer.exists():
        raise RuntimeError("run ./scripts/build.sh before testing the pass")

    lowered = WORK / "ex7_e4m3fn_mul_lowered.mlir"
    verilog = WORK / "ex7_e4m3fn_mul_from_pass.sv"
    run(
        [
            optimizer,
            "examples/ex7_e4m3fn_mul.mlir",
            "--lower-e4m3fn-to-comb",
            "--tutorial-func-to-hw",
            "--canonicalize",
            "-o",
            lowered,
        ]
    )
    run(["firtool", lowered, "-o", verilog])
    return verilog


def main():
    parser = argparse.ArgumentParser(
        description="Exhaustively test an E4M3FN multiplier against MLIR"
    )
    parser.add_argument(
        "--pass",
        dest="test_pass",
        action="store_true",
        help="test the custom lowering pass instead of the provided RTL",
    )
    args = parser.parse_args()

    WORK.mkdir(parents=True, exist_ok=True)
    vectors = generate_reference_vectors()
    verilog = (
        build_pass_verilog()
        if args.test_pass
        else ROOT / "examples" / "ex7_e4m3fn_mul_reference.sv"
    )
    simulator = WORK / "ex7_e4m3fn_test"

    run(
        [
            "iverilog",
            "-g2012",
            "-s",
            "e4m3fn_exhaustive_tb",
            "-o",
            simulator,
            verilog,
            "test/e4m3fn-exhaustive-tb.sv",
        ],
        capture_output=True,
        text=True,
    )

    print(f"Testing all {PAIR_COUNT:,} input pairs", flush=True)
    completed = subprocess.run(
        ["vvp", simulator, f"+VECTORS={vectors}"], cwd=ROOT, check=False
    )
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
