"""Tests for the QAOA Max-Cut 5-cycle task.

The candidate is a self-contained Python script that runs QAOA on the
5-vertex undirected cycle graph and prints the binary solution, the two
vertex sets, and the maximum cut value. We execute it as a subprocess
using the project venv Python (which has qiskit installed) and validate
the printed output.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VENV_PY = ROOT / ".venv" / "bin" / "python3"

EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
N = 5
EXPECTED_OPTIMAL_CUT = 4  # 5-cycle optimum: 4 of 5 edges can be cut.


def _select_python() -> str:
    """Prefer the project venv python (it has qiskit installed)."""
    if VENV_PY.exists():
        return str(VENV_PY)
    return sys.executable


def _maxcut_cost(bitstring: str, edges: list[tuple[int, int]]) -> int:
    return sum(1 for u, v in edges if bitstring[u] != bitstring[v])


def run_tests(candidate_path: str) -> dict:
    failures: list[str] = []
    candidate = Path(candidate_path).resolve()
    if not candidate.exists():
        return {"passed": False, "details": [f"candidate file not found: {candidate}"]}

    env = os.environ.copy()
    # Keep HOME so qiskit can write any caches; isolate from user site additions.
    env.setdefault("PYTHONNOUSERSITE", "1")

    try:
        completed = subprocess.run(
            [_select_python(), str(candidate)],
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "details": ["candidate execution timed out (>180s)"]}
    except Exception as exc:  # noqa: BLE001
        return {"passed": False, "details": [f"candidate execution failed: {exc}"]}

    if completed.returncode != 0:
        stderr_tail = (completed.stderr or "").strip().splitlines()[-10:]
        failures.append(
            f"candidate exited with code {completed.returncode}; stderr tail:\n"
            + "\n".join(stderr_tail)
        )
        return {"passed": False, "details": failures}

    output = completed.stdout or ""

    # Extract the binary solution. Accept either a 5-char 0/1 string (e.g.
    # "10100") or a Python list of 5 ints (e.g. "[1, 0, 1, 0, 0]").
    binary_solution: str | None = None
    bin_str_match = re.search(r"\b([01]{5})\b", output)
    list_match = re.search(
        r"\[\s*([01])\s*,\s*([01])\s*,\s*([01])\s*,\s*([01])\s*,\s*([01])\s*\]", output
    )
    if bin_str_match:
        binary_solution = bin_str_match.group(1)
    elif list_match:
        binary_solution = "".join(list_match.groups())
    if binary_solution is None:
        failures.append(
            "stdout does not contain a 5-char binary solution string or "
            "a 5-element list of 0/1 ints"
        )
        return {"passed": False, "details": failures}

    # Look for a cut-value integer near a "max-cut" / "cut value" / "maxcut" label,
    # otherwise fall back to the last integer in the output.
    cut_value: int | None = None
    cut_label_match = re.search(
        r"(?:max[-\s]?cut(?:\s*value)?|cut(?:\s*value)?|maxcut)\s*[:=]?\s*(\d+)",
        output,
        re.IGNORECASE,
    )
    if cut_label_match:
        cut_value = int(cut_label_match.group(1))
    else:
        ints = re.findall(r"\b(\d+)\b", output)
        if ints:
            cut_value = int(ints[-1])

    if cut_value is None:
        failures.append("stdout does not contain an integer max-cut value")

    # Validate the binary solution against the 5-cycle graph.
    actual_cut = _maxcut_cost(binary_solution, EDGES)

    # Look for set listings: "Set A: [...]" / "Set 0: [...]" / "Group 1: [...]" etc.
    set_matches = re.findall(
        r"(?:set|partition|group|side)\s*[ab01]\s*[:=]?\s*\[([^\]]*)\]",
        output,
        re.IGNORECASE,
    )
    set_a: set[int] | None = None
    set_b: set[int] | None = None
    if len(set_matches) >= 2:

        def _parse_ints(s: str) -> set[int]:
            return {int(x) for x in re.findall(r"\d+", s)}

        set_a = _parse_ints(set_matches[0])
        set_b = _parse_ints(set_matches[1])

    # Now run the assertions.
    if cut_value is not None and cut_value != actual_cut:
        failures.append(
            f"printed cut value {cut_value} does not match the actual cut value "
            f"{actual_cut} of binary solution {binary_solution}"
        )

    if set_a is not None and set_b is not None:
        union = set_a | set_b
        if union != set(range(N)):
            failures.append(
                f"vertex sets {sorted(set_a)} and {sorted(set_b)} do not partition "
                f"{{0,1,2,3,4}} (union={sorted(union)})"
            )
        if set_a & set_b:
            failures.append(f"vertex sets overlap: A={sorted(set_a)}, B={sorted(set_b)}")
        # Verify the partition matches the binary solution bit assignment.
        expected_a = {i for i in range(N) if binary_solution[i] == "0"}
        expected_b = {i for i in range(N) if binary_solution[i] == "1"}
        # Allow either A==0-side or A==1-side labelling.
        ok_partition = (set_a == expected_a and set_b == expected_b) or (
            set_a == expected_b and set_b == expected_a
        )
        if not ok_partition:
            failures.append(
                f"printed sets A={sorted(set_a)}, B={sorted(set_b)} do not match "
                f"binary solution {binary_solution} (expected 0-side={sorted(expected_a)}, "
                f"1-side={sorted(expected_b)})"
            )

    if actual_cut != EXPECTED_OPTIMAL_CUT:
        failures.append(
            f"binary solution {binary_solution} has cut value {actual_cut}, "
            f"expected the optimum {EXPECTED_OPTIMAL_CUT} for a 5-cycle"
        )

    return {
        "passed": not failures,
        "details": failures
        or [
            f"QAOA Max-Cut on 5-cycle correct: binary={binary_solution}, "
            f"cut={actual_cut} (optimum {EXPECTED_OPTIMAL_CUT})"
        ],
    }
