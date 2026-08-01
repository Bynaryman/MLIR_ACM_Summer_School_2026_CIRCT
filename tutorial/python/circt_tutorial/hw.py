from ._ops import result_op


class ConstantOp:
    @staticmethod
    def create(result_type, value):
        from mlir.ir import IntegerAttr

        return result_op(
            "hw.constant",
            result_type,
            attributes={"value": IntegerAttr.get(result_type, value)},
        )
