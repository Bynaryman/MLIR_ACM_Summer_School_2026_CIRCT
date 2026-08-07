#!/usr/bin/env python3

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "exercises" / "ex5-reports"


def run(command):
    print("+", " ".join(str(part) for part in command), flush=True)
    return subprocess.run(command, cwd=ROOT, check=True)


def prepare_example():
    WORK.mkdir(parents=True, exist_ok=True)
    before = WORK / "before.mlir"
    after = WORK / "after.mlir"

    run(["circt-verilog", "exercises/ex5_aig.sv", "-o", before])
    run(["circt-verilog", "solutions/ex5_aig_optimized.sv", "-o", after])
    return before, after, "ex5_aig"


def check_equivalence(before, after, top):
    command = [
        "circt-lec",
        "--c1",
        top,
        before,
        "--c2",
        top,
        after,
    ]
    print("+", " ".join(str(part) for part in command), flush=True)
    completed = subprocess.run(
        command, cwd=ROOT, check=True, text=True, capture_output=True
    )
    result = completed.stdout.strip()
    print(result)
    if result != "c1 == c2":
        raise RuntimeError("the two designs are not equivalent")


def synthesize(input_file, label, top):
    analysis = WORK / f"{label}-analysis"
    output = WORK / f"{label}-aig.mlir"
    if analysis.exists():
        shutil.rmtree(analysis)

    run(
        [
            "circt-synth",
            input_file,
            f"--top={top}",
            f"--analysis-output={analysis}",
            "--analysis-output-format=json",
            "-o",
            output,
        ]
    )

    # CIRCT creates report directories as 0750. Keep bind-mounted outputs
    # readable by the host user even when Docker runs the script as root.
    analysis.chmod(0o755)
    for report in analysis.iterdir():
        report.chmod(0o644)

    resources = json.loads((analysis / "resource_usage.json").read_text())
    resource_record = next(item for item in resources if item["moduleName"] == top)
    aig_nodes = int(resource_record["total"].get("synth.aig.and_inv", 0))

    timing = json.loads((analysis / "longest_path.json").read_text())
    timing_record = next(item for item in timing if item["module_name"] == top)
    depth = max(
        (int(item["level"]) for item in timing_record["timing_levels"]),
        default=0,
    )
    return aig_nodes, depth


def main():
    if len(sys.argv) == 1:
        before, after, top = prepare_example()
    elif len(sys.argv) == 4:
        before = Path(sys.argv[1]).resolve()
        after = Path(sys.argv[2]).resolve()
        top = sys.argv[3]
    else:
        print(
            "usage: compare-aig.py [BEFORE.mlir AFTER.mlir TOP_MODULE]",
            file=sys.stderr,
        )
        return 2

    WORK.mkdir(parents=True, exist_ok=True)
    check_equivalence(before, after, top)
    before_stats = synthesize(before, "before", top)
    after_stats = synthesize(after, "after", top)

    print()
    print(f"AIG statistics for @{top}")
    print(f"{'metric':<24} {'before':>10} {'after':>10} {'delta':>10}")
    print(f"{'and-inverter nodes':<24} {before_stats[0]:>10} "
          f"{after_stats[0]:>10} {after_stats[0] - before_stats[0]:>+10}")
    print(f"{'maximum logic level':<24} {before_stats[1]:>10} "
          f"{after_stats[1]:>10} {after_stats[1] - before_stats[1]:>+10}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
