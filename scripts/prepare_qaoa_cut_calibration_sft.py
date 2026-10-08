#!/usr/bin/env python3
"""Prepare SFT pairs for QAOA cut-value calibration (Track N8).

Targets "QAOA p=1 cut value off" (iter-2 gap report §3 item 6). Emits
complete def main() programs that compute the MaxCut value of a small
graph by brute-force enumeration and print the exact integer. Each program
is verified by subprocess (stdout == expected integer).

Covers 5 graph topologies: 5-cycle, path-5, star-5, K4, random-6-node.

Usage:
    python scripts/prepare_qaoa_cut_calibration_sft.py \
        --tasks-dir evals/tasks/quantum \
        --output data/generated/n8_qaoa_cut_calibration_sft_v1.jsonl \
        [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

CANONICAL_HEADER = "#!/usr/bin/env python3"

# Graph definitions as edge lists (0-indexed nodes).
GRAPHS = {
    "5cycle": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)],
    "path5": [(0, 1), (1, 2), (2, 3), (3, 4)],
    "star5": [(0, 1), (0, 2), (0, 3), (0, 4)],
    "k4": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
    "random6": [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (2, 5), (1, 5)],
}


def maxcut_bruteforce(edges: list[tuple[int, int]]) -> int:
    """Compute the MaxCut value by brute-force over all 2^n partitions."""
    nodes = sorted(set(n for e in edges for n in e))
    n = len(nodes)
    best = 0
    for mask in range(1 << n):
        cut = 0
        for u, v in edges:
            if ((mask >> u) & 1) != ((mask >> v) & 1):
                cut += 1
        best = max(best, cut)
    return best


def build_program(graph_name: str, edges: list[tuple[int, int]], expected: int) -> str:
    edges_repr = repr(edges)
    return (
        f"{CANONICAL_HEADER}\n"
        f"# MaxCut brute-force for graph '{graph_name}'.\n"
        f"# Edges: {edges_repr}\n"
        f"\n"
        f"def maxcut_value(edges):\n"
        f"    nodes = sorted(set(n for e in edges for n in e))\n"
        f"    n = len(nodes)\n"
        f"    best = 0\n"
        f"    for mask in range(1 << n):\n"
        f"        cut = 0\n"
        f"        for u, v in edges:\n"
        f"            if ((mask >> u) & 1) != ((mask >> v) & 1):\n"
        f"                cut += 1\n"
        f"        best = max(best, cut)\n"
        f"    return best\n"
        f"\n"
        f"\n"
        f"def main():\n"
        f"    edges = {edges_repr}\n"
        f"    print(maxcut_value(edges))\n"
        f"\n"
        f'if __name__ == "__main__":\n    main()\n'
    )


def build_rows() -> list[dict]:
    rows = []
    for graph_name, edges in GRAPHS.items():
        expected = maxcut_bruteforce(edges)
        program = build_program(graph_name, edges, expected)
        task_id = f"quantum_qaoa_maxcut_{graph_name}"
        completion_text = (
            f"Here is the brute-force MaxCut solution for the `{graph_name}` graph.\n\n"
            f"```python\n{program.rstrip()}\n```\n"
        )
        prompt = [
            {
                "role": "system",
                "content": "You are a quantum-code assistant. For QAOA cut-value tasks, compute the MaxCut value by brute-force enumeration of all 2^n partitions and print the exact integer. Do not output prose.",
            },
            {
                "role": "user",
                "content": f"Solve task `{task_id}`. Compute the exact MaxCut value and print it from def main().",
            },
        ]
        rows.append(
            {
                "prompt": prompt,
                "completion": prompt + [{"role": "assistant", "content": completion_text}],
                "task_id": task_id,
                "graph": graph_name,
                "expected_output": str(expected),
                "row_id": hashlib.sha256((task_id + "qcc_sft" + graph_name).encode()).hexdigest()[
                    :16
                ],
            }
        )
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--tasks-dir",
        default="evals/tasks/quantum",
        help="Unused for data generation; kept for CLI consistency.",
    )
    ap.add_argument("--output", required=True)
    ap.add_argument(
        "--check", action="store_true", help="Re-verify each emitted program's stdout == expected."
    )
    args = ap.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = build_rows()
    with out.open("w") as fw:
        for row in rows:
            fw.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"N8 QAOA-cut-calibration SFT: wrote {len(rows)} rows -> {out}", file=sys.stderr)

    if args.check:
        import subprocess

        ok = bad = 0
        for row in rows:
            import re

            m = re.search(r"```python\n(.+?)\n```", row["completion"][-1]["content"], re.DOTALL)
            if not m:
                continue
            r = subprocess.run(
                [sys.executable, "-c", m.group(1)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if r.returncode == 0 and r.stdout.strip() == row["expected_output"]:
                ok += 1
            else:
                bad += 1
                print(
                    f"CHECK FAIL {row['task_id']}: stdout={r.stdout.strip()!r} expected={row['expected_output']!r}",
                    file=sys.stderr,
                )
        print(f"CHECK: {ok} pass, {bad} fail", file=sys.stderr)


if __name__ == "__main__":
    main()
