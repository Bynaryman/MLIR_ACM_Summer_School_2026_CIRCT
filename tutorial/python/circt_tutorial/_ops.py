from dataclasses import dataclass

from mlir.ir import IntegerAttr, IntegerType, Operation


@dataclass(frozen=True)
class CreatedOp:
    operation: Operation

    @property
    def result(self):
        return self.operation.results[0]


def unwrap(value):
    return value.result if isinstance(value, CreatedOp) else value


def integer_width(value):
    return IntegerType(unwrap(value).type).width


def result_op(name, result_type, *operands, attributes=None):
    operation = Operation.create(
        name,
        results=[result_type],
        operands=[unwrap(operand) for operand in operands],
        attributes=attributes or {},
    )
    return CreatedOp(operation)


def integer_attr(width, value):
    return IntegerAttr.get(IntegerType.get_signless(width), value)
