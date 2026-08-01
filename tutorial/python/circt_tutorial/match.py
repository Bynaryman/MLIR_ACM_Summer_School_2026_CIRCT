def _defining_operation(value):
    owner = getattr(value, "owner", None)
    return owner if getattr(owner, "name", None) is not None else None


def _has_type(value, spelling):
    return str(value.type) == spelling


def match_e4m3_island(out_cast):
    operation = out_cast.operation
    if len(operation.operands) != 1 or len(operation.results) != 1:
        return None
    if not _has_type(operation.operands[0], "f8E4M3FN"):
        return None
    if not _has_type(operation.results[0], "i8"):
        return None

    multiply = _defining_operation(operation.operands[0])
    if multiply is None or multiply.name != "arith.mulf":
        return None

    input_bits = []
    for operand in multiply.operands:
        input_cast = _defining_operation(operand)
        if input_cast is None or input_cast.name != "arith.bitcast":
            return None
        if len(input_cast.operands) != 1:
            return None
        if not _has_type(input_cast.operands[0], "i8"):
            return None
        input_bits.append(input_cast.operands[0])

    return tuple(input_bits)
