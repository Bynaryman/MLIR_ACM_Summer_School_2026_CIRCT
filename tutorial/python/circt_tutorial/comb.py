from mlir.ir import IntegerType

from ._ops import integer_attr, integer_width, result_op, unwrap


class ExtractOp:
    @staticmethod
    def create(low_bit, result_type, value):
        return result_op(
            "comb.extract",
            result_type,
            value,
            attributes={"lowBit": integer_attr(32, low_bit)},
        )


class ConcatOp:
    @staticmethod
    def create(*values):
        width = sum(integer_width(value) for value in values)
        return result_op("comb.concat", IntegerType.get_signless(width), *values)


class MuxOp:
    @staticmethod
    def create(condition, true_value, false_value):
        return result_op(
            "comb.mux", unwrap(true_value).type, condition, true_value, false_value
        )


class AddOp:
    @staticmethod
    def create(*values):
        return result_op("comb.add", unwrap(values[0]).type, *values)


class SubOp:
    @staticmethod
    def create(lhs, rhs):
        return result_op("comb.sub", unwrap(lhs).type, lhs, rhs)


class MulOp:
    @staticmethod
    def create(lhs, rhs):
        return result_op("comb.mul", unwrap(lhs).type, lhs, rhs)


class AndOp:
    @staticmethod
    def create(lhs, rhs):
        return result_op("comb.and", unwrap(lhs).type, lhs, rhs)


class XorOp:
    @staticmethod
    def create(lhs, rhs):
        return result_op("comb.xor", unwrap(lhs).type, lhs, rhs)


class ShlOp:
    @staticmethod
    def create(value, amount):
        return result_op("comb.shl", unwrap(value).type, value, amount)
