#!/usr/bin/env python3

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from circt.dialects import comb, hw
from circt.ir import IntegerType

from circt_tutorial import match_e4m3_island
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

        lhs_sign = comb.ExtractOp.create(7, i1, lhs).result
        rhs_sign = comb.ExtractOp.create(7, i1, rhs).result
        sign = comb.XorOp.create(lhs_sign, rhs_sign).result

        lhs_fraction = comb.ExtractOp.create(0, i3, lhs).result
        rhs_fraction = comb.ExtractOp.create(0, i3, rhs).result
        one = hw.ConstantOp.create(i1, 1).result
        lhs_significand = comb.ConcatOp.create(one, lhs_fraction).result
        rhs_significand = comb.ConcatOp.create(one, rhs_fraction).result
        zero4 = hw.ConstantOp.create(i4, 0).result
        lhs_wide = comb.ConcatOp.create(zero4, lhs_significand).result
        rhs_wide = comb.ConcatOp.create(zero4, rhs_significand).result
        product = comb.MulOp.create(lhs_wide, rhs_wide).result

        norm = comb.ExtractOp.create(7, i1, product).result
        direct = comb.ExtractOp.create(3, i4, product).result
        shifted = comb.ExtractOp.create(4, i4, product).result
        mantissa = comb.MuxOp.create(
            norm.value, shifted.value, direct.value
        ).result
        fraction = comb.ExtractOp.create(0, i3, mantissa).result

        lhs_exponent = comb.ExtractOp.create(3, i4, lhs).result
        rhs_exponent = comb.ExtractOp.create(3, i4, rhs).result
        zero1 = hw.ConstantOp.create(i1, 0).result
        lhs_exponent5 = comb.ConcatOp.create(zero1, lhs_exponent).result
        rhs_exponent5 = comb.ConcatOp.create(zero1, rhs_exponent).result
        exponent_sum = comb.AddOp.create(lhs_exponent5, rhs_exponent5).result
        bias = hw.ConstantOp.create(i5, 7).result
        exponent_base = comb.SubOp.create(exponent_sum, bias).result
        norm5 = comb.ConcatOp.create(zero4, norm).result
        adjusted_exponent = comb.AddOp.create(exponent_base, norm5).result
        exponent = comb.ExtractOp.create(0, i4, adjusted_exponent).result

        result = comb.ConcatOp.create(sign, exponent, fraction).result

    rewriter.replace_op(out_cast, [result])
    return False


if __name__ == "__main__":
    run_cli(lower_e4m3_mul)
