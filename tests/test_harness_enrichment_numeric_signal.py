"""Regression tests: numeric harness-detail enrichment for prose-only tasks.

2026-08-24 harness-enrichment workstream. The four training tasks
stabilizer_tableau_update_repair, measurement_bug_repair, superdense_pauli_router,
bitstring_maxcut_landscape emitted only prose failure details
("mapping for '10' was incorrect", "qaoa_cost_landscape is not sorted..."),
so shaped_reward_from_details() returned 0.0 for every failing candidate —
indistinguishable from a SyntaxError crash — and all-fail groups carried no
continuous policy signal (live-run steps 5-8: shaped 0.0, debugger report
reports/sapo-dead-signal-investigation-2026-08-24.md).

Enriched harnesses append numeric closeness summaries (key=value / expected
forms the shaped parser scores) while keeping every pre-existing failure
template byte-identical (prompt behavior-hints are extracted from tests.py).
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from training.grpo_utils import (
    extract_behavior_hints_from_test_source,
    shaped_reward_from_details,
)

ROOT = Path(__file__).resolve().parents[1]
TASKS = [
    "stabilizer_tableau_update_repair",
    "measurement_bug_repair",
    "superdense_pauli_router",
    "bitstring_maxcut_landscape",
]


def _run(task: str, code: str) -> dict:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name
    try:
        spec = importlib.util.spec_from_file_location(
            f"{task}_tests", str(ROOT / "evals/tasks/quantum" / task / "tests.py")
        )
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        return mod.run_tests(path)
    finally:
        os.unlink(path)


def _shaped(task: str, code: str) -> float:
    result = _run(task, code)
    if result["passed"]:
        return 1.0
    return shaped_reward_from_details(False, result.get("details") or [])


def test_references_still_pass_all_four_enriched_harnesses() -> None:
    for task in TASKS:
        result = _run(task, (ROOT / "evals/tasks/quantum" / task / "candidate.py").read_text())
        assert result["passed"], f"{task} reference failed: {result['details']}"


def test_stabilizer_near_miss_scores_positive() -> None:
    # Correct H/S rules, wrong SDG rule -> 12/13 axes correct (near miss).
    code = """
def apply_gate_sequence(pauli, gates):
    rules = {
        "H": {"I": (1, "I"), "X": (1, "Z"), "Y": (-1, "Y"), "Z": (1, "X")},
        "S": {"I": (1, "I"), "X": (1, "Y"), "Y": (-1, "X"), "Z": (1, "Z")},
        "SDG": {"I": (1, "I"), "X": (1, "Y"), "Y": (-1, "X"), "Z": (1, "Z")},
    }
    raw = pauli.strip()
    sign = -1 if raw.startswith("-") else 1
    label = raw[1:] if raw.startswith("-") else raw
    label = label.strip().upper()
    for gate in gates:
        name = gate.strip().upper()
        if name not in rules:
            raise ValueError("unsupported gate")
        gs, label = rules[name][label]
        sign *= gs
    return sign, label
"""
    near = _shaped("stabilizer_tableau_update_repair", code)
    assert near > 0.5, f"near-miss shaped={near}"
    assert near <= 0.9, f"near-miss must stay below the pass cap: {near}"


def test_stabilizer_all_wrong_scores_low_but_positive() -> None:
    code = """
def apply_gate_sequence(pauli, gates):
    return ("Q", 9)
"""
    shaped = _shaped("stabilizer_tableau_update_repair", code)
    assert 0.0 < shaped < 0.6, f"all-wrong shaped={shaped}"


def test_stabilizer_crash_stays_zero() -> None:
    code = """
def apply_gate_sequence(pauli, gates):
    raise TypeError("boom")
"""
    with __import__("pytest").raises(Exception):
        _run("stabilizer_tableau_update_repair", code)


def test_measurement_near_miss_scores_positive() -> None:
    # '10' mapped correctly (q0=0, q1=1), '01' mapped wrong (both 1).
    code = """
def measurement_mapping(bitstring):
    if len(bitstring) != 2 or any(ch not in "01" for ch in bitstring):
        raise ValueError("expected a two-bit measurement string")
    return {"q0": int(bitstring[1]), "q1": 1}
"""
    shaped = _shaped("measurement_bug_repair", code)
    assert 0.0 < shaped <= 0.9, f"measurement near-miss shaped={shaped}"


def test_measurement_all_wrong_scores_low_but_positive() -> None:
    code = """
def measurement_mapping(bitstring):
    return {"q0": 0, "q1": 0}
"""
    shaped = _shaped("measurement_bug_repair", code)
    assert 0.0 < shaped < 0.7, f"measurement all-wrong shaped={shaped}"


def test_superdense_near_miss_scores_positive() -> None:
    # encode correct for 3 of 4 bitstrings (00->X is wrong), decode correct.
    code = """
def encode_message(bits):
    return {"00": "X", "01": "X", "10": "Z", "11": "XZ"}[bits]

def decode_message(opcode):
    mapping = {"I": "00", "X": "01", "Z": "10", "XZ": "11"}
    op = opcode.strip().upper().replace("ZX", "XZ")
    if op not in mapping:
        raise ValueError("invalid opcode")
    return mapping[op]
"""
    shaped = _shaped("superdense_pauli_router", code)
    assert 0.0 < shaped <= 0.9, f"superdense near-miss shaped={shaped}"


def test_bitstring_sortedness_only_failure_scores_positive() -> None:
    # Everything correct except the landscape is not sorted descending.
    code = """
def maxcut_cost(bitstring, edges):
    bits = str(bitstring)
    cost = 0
    for left, right in edges:
        if bits[left] != bits[right]:
            cost += 1
    return cost

def brute_force_maxcut(n_nodes, edges):
    from itertools import product
    best = ""
    best_cost = -1
    for bits in product("01", repeat=n_nodes):
        b = "".join(bits)
        c = maxcut_cost(b, edges)
        if c > best_cost or (c == best_cost and b < best):
            best, best_cost = b, c
    return best, best_cost

def qaoa_cost_landscape(n_nodes, edges):
    from itertools import product
    return [(b, maxcut_cost(b, edges)) for b in ("".join(p) for p in product("01", repeat=n_nodes))][::-1]
"""
    shaped = _shaped("bitstring_maxcut_landscape", code)
    assert 0.0 < shaped <= 0.9, f"bitstring sortedness-only shaped={shaped}"


def test_bitstring_invalid_input_failure_scores_positive() -> None:
    # Correct implementation except it accepts an invalid bitstring.
    code = """
def maxcut_cost(bitstring, edges):
    bits = str(bitstring)
    cost = 0
    for left, right in edges:
        if bits[left] != bits[right]:
            cost += 1
    return cost

def brute_force_maxcut(n_nodes, edges):
    from itertools import product
    best = ""
    best_cost = -1
    for bits in product("01", repeat=n_nodes):
        b = "".join(bits)
        c = maxcut_cost(b, edges)
        if c > best_cost or (c == best_cost and b < best):
            best, best_cost = b, c
    return best, best_cost

def qaoa_cost_landscape(n_nodes, edges):
    from itertools import product
    return sorted(((b, maxcut_cost(b, edges)) for b in ("".join(p) for p in product("01", repeat=n_nodes))), key=lambda x: -x[1])
"""
    shaped = _shaped("bitstring_maxcut_landscape", code)
    assert 0.0 < shaped <= 0.9, f"bitstring invalid-input shaped={shaped}"


def test_enrichment_does_not_change_extracted_behavior_hints() -> None:
    # Prompt hints are extracted from tests.py source; enrichment lines are
    # string-concatenation appends that _append_message_template cannot
    # extract, and every pre-existing append template is preserved in order.
    for task in TASKS:
        source = (ROOT / "evals/tasks/quantum" / task / "tests.py").read_text()
        hints = extract_behavior_hints_from_test_source(source, cap=6)
        assert hints, f"{task} lost all hints"
        for hint in hints:
            assert "axis_correct" not in hint, (task, hint)
            assert "correct_bits" not in hint, (task, hint)
            assert "expected 13" not in hint, (task, hint)
            assert "landscape_ordered" not in hint, (task, hint)
        assert (
            any("apply_gate_sequence" in h for h in hints)
            or task != "stabilizer_tableau_update_repair"
        )
        assert any("mapping for" in h for h in hints) or task != "measurement_bug_repair"
        assert (
            any("encode_message" in h or "decode_message" in h for h in hints)
            or task != "superdense_pauli_router"
        )
        assert any("maxcut_cost" in h for h in hints) or task != "bitstring_maxcut_landscape"
