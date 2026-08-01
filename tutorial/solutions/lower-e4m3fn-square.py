#!/usr/bin/env python3

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from mlir.ir import IntegerType

from circt_tutorial import comb, hw, match_e4m3_island
from circt_tutorial.driver import run_cli


def build_square4(value):
    i1 = IntegerType.get_signless(1)
    i7 = IntegerType.get_signless(7)
    i8 = IntegerType.get_signless(8)
    bits = [comb.ExtractOp.create(index, i1, value).result for index in range(4)]
    zero7 = hw.ConstantOp.create(i7, 0).result

    def at_weight(bit, weight):
        wide = comb.ConcatOp.create(zero7, bit).result
        shift = hw.ConstantOp.create(i8, weight).result
        return comb.ShlOp.create(wide, shift).result

    terms = [at_weight(bits[index], 2 * index) for index in range(4)]
    for index in range(4):
        for other in range(index):
            cross = comb.AndOp.create(bits[index], bits[other]).result
            terms.append(at_weight(cross, index + other + 1))
    return comb.AddOp.create(*terms).result


def lower_e4m3_square(out_cast, rewriter):
    matched = match_e4m3_island(out_cast)
    if matched is None:
        return True
    lhs, rhs = matched
    if lhs != rhs:
        return True
    value = lhs

    with rewriter.ip:
        i1 = IntegerType.get_signless(1)
        i3 = IntegerType.get_signless(3)
        i4 = IntegerType.get_signless(4)
        i5 = IntegerType.get_signless(5)

        sign = hw.ConstantOp.create(i1, 0).result

        fraction_bits = comb.ExtractOp.create(0, i3, value).result
        one = hw.ConstantOp.create(i1, 1).result
        significand = comb.ConcatOp.create(one, fraction_bits).result
        product = build_square4(significand)

        norm = comb.ExtractOp.create(7, i1, product).result
        direct = comb.ExtractOp.create(3, i4, product).result
        shifted = comb.ExtractOp.create(4, i4, product).result
        mantissa = comb.MuxOp.create(norm, shifted, direct).result
        fraction = comb.ExtractOp.create(0, i3, mantissa).result

        encoded_exponent = comb.ExtractOp.create(3, i4, value).result
        zero1 = hw.ConstantOp.create(i1, 0).result
        exponent5 = comb.ConcatOp.create(zero1, encoded_exponent).result
        one5 = hw.ConstantOp.create(i5, 1).result
        doubled = comb.ShlOp.create(exponent5, one5).result
        bias = hw.ConstantOp.create(i5, 7).result
        exponent_base = comb.SubOp.create(doubled, bias).result
        zero4 = hw.ConstantOp.create(i4, 0).result
        norm5 = comb.ConcatOp.create(zero4, norm).result
        adjusted_exponent = comb.AddOp.create(exponent_base, norm5).result
        exponent = comb.ExtractOp.create(0, i4, adjusted_exponent).result

        result = comb.ConcatOp.create(sign, exponent, fraction).result

    rewriter.replace_op(out_cast, [result])
    return False


if __name__ == "__main__":
    run_cli(lower_e4m3_square)
