import argparse
from pathlib import Path

from mlir import rewrite
from mlir.dialects import arith, func  # noqa: F401
from mlir.ir import Context, Location, Module


def lower(source, callback):
    with Context() as context, Location.unknown():
        context.allow_unregistered_dialects = True
        module = Module.parse(source)

        patterns = rewrite.RewritePatternSet()
        patterns.add(arith.BitcastOp, callback)
        rewrite.apply_patterns_and_fold_greedily(module, patterns.freeze())

        result = str(module)
        if "arith.mulf" in result:
            raise RuntimeError("no supported E4M3 multiplication island was rewritten")
        return result


def run_cli(callback):
    parser = argparse.ArgumentParser(
        description="Lower an E4M3FN arith.mulf island to CIRCT comb operations"
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    result = lower(args.input.read_text(), callback)
    if args.output is None:
        print(result)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result + "\n")
