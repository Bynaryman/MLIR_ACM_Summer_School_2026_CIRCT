#!/usr/bin/env python3

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "build" / "ex7_e4m3_exhaustive"
PAIR_COUNT = 256 * 256


def run(command, **kwargs):
    print("+", " ".join(str(part) for part in command), flush=True)
    return subprocess.run(command, cwd=ROOT, check=True, **kwargs)


def is_exact_normal_case(lhs, rhs, expected):
    lhs_exponent = (lhs >> 3) & 0xF
    rhs_exponent = (rhs >> 3) & 0xF
    lhs_fraction = lhs & 0x7
    rhs_fraction = rhs & 0x7
    expected_exponent = (expected >> 3) & 0xF
    expected_fraction = expected & 0x7

    if lhs_exponent == 0 or rhs_exponent == 0:
        return False
    if (lhs_exponent == 0xF and lhs_fraction == 0x7) or (
        rhs_exponent == 0xF and rhs_fraction == 0x7
    ):
        return False
    if expected_exponent == 0:
        return False
    if expected_exponent == 0xF and expected_fraction == 0x7:
        return False

    product = (8 + lhs_fraction) * (8 + rhs_fraction)
    unrounded_exponent = (
        lhs_exponent + rhs_exponent - 7 + (1 if product >= 128 else 0)
    )
    if not 1 <= unrounded_exponent <= 0xF:
        return False

    discarded_width = 4 if product >= 128 else 3
    return product & ((1 << discarded_width) - 1) == 0


def generate_reference_vectors(normal_path=False):
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
    selected = 0
    with vectors.open("w") as output:
        for index, expected_value in enumerate(expected):
            lhs_value, rhs_value = divmod(index, 256)
            if normal_path and not is_exact_normal_case(
                lhs_value, rhs_value, expected_value
            ):
                continue
            output.write(f"{lhs_value:02x} {rhs_value:02x} {expected_value:02x}\n")
            selected += 1
    return vectors, selected


def build_pass_verilog(lowerer):
    optimizer = ROOT / "build" / "bin" / "circt-tutorial-opt"
    if not optimizer.exists():
        optimizer = shutil.which("circt-tutorial-opt")
    if optimizer is None:
        raise RuntimeError("circt-tutorial-opt is unavailable; run ./scripts/build.sh")

    lowered_function = WORK / "ex7_e4m3fn_mul_function.mlir"
    lowered = WORK / "ex7_e4m3fn_mul_lowered.mlir"
    verilog = WORK / "ex7_e4m3fn_mul_from_pass.sv"
    run(
        [
            sys.executable,
            lowerer,
            "exercises/ex7_e4m3fn_mul.mlir",
            "-o",
            lowered_function,
        ]
    )
    run(
        [
            optimizer,
            lowered_function,
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
    parser.add_argument(
        "--normal-path",
        action="store_true",
        help="check exact normal finite products covered by Exercise 7",
    )
    parser.add_argument(
        "--lowerer",
        type=Path,
        default=Path("scripts/lower-e4m3fn.py"),
        help="Python lowering script to test with --pass",
    )
    args = parser.parse_args()

    WORK.mkdir(parents=True, exist_ok=True)
    vectors, vector_count = generate_reference_vectors(args.normal_path)
    verilog = (
        build_pass_verilog(args.lowerer)
        if args.test_pass
        else ROOT / "exercises" / "ex7_e4m3fn_mul_reference.sv"
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

    print(f"Testing {vector_count:,} input pairs", flush=True)
    completed = subprocess.run(
        ["vvp", simulator, f"+VECTORS={vectors}", f"+COUNT={vector_count}"],
        cwd=ROOT,
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
