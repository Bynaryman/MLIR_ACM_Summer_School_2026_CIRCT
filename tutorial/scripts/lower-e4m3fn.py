#!/usr/bin/env python3

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

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

        # Exercise 7: replace this placeholder with {exponent, fraction}.
        zero_payload = hw.ConstantOp.create(i7, 0).result
        result = comb.ConcatOp.create(sign, zero_payload).result

    rewriter.replace_op(out_cast, [result])
    return False


if __name__ == "__main__":
    run_cli(lower_e4m3_mul)
