from __future__ import annotations

import json
import re
from pathlib import Path


BENCHMARK = Path("evals/benchmarks/qwen36_27b_user_rag_questions_v2.json")


def test_qwen36_rag_user_questions_v2_is_large_and_judgeable() -> None:
    payload = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    assert len(payload) >= 150

    ids = [item["id"] for item in payload]
    assert len(ids) == len(set(ids))

    coding_count = 0
    exact_coding_count = 0
    categories: set[str] = set()
    expected_sources: set[str] = set()
    for item in payload:
        categories.add(item["category"])
        expected_sources.update(item["expected_source_substrings"])
        if item["coding_problem"]:
            coding_count += 1

        assert isinstance(item["query"], str)
        assert len(item["query"].split()) >= 8
        assert item["expected_source_substrings"]
        assert len(item["expected_terms"]) >= 3
        assert 1 <= item["minimum_term_hits"] <= len(item["expected_terms"])
        assert "Pass if" in item["judge"]
        assert item["judge_type"] in {"source_and_terms", "unit_test_backed"}
        assert item["answer_requirements"]
        if item["judge_type"] == "unit_test_backed":
            exact_coding_count += 1
            assert item["coding_problem"] is True
            assert item["unit_test_file"].endswith("/tests.py")
            assert Path(item["unit_test_file"]).exists()
            assert item["example_io"]

    assert coding_count >= 100
    assert exact_coding_count >= 35
    assert {"install", "sdk_api", "algorithm", "repair", "quantum_coding_task", "quantum_coding_exact"} <= categories
    assert len(expected_sources) >= 25


def test_qwen36_rag_user_questions_v2_has_specific_quantum_coding_examples() -> None:
    payload = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in payload}

    required = {
        "task_phase_estimation_measurement": ["round(eigenvalue_phase * n_states)", "% n_states"],
        "task_qaoa_maxcut_cost": ["bitstring[u] != bitstring[v]", "cost += 1"],
        "task_grover_diffusion": ["mean = sum(state) / n", "2 * mean - a"],
        "task_partial_trace_b": ["trace_out == \"B\"", "rho[i * dim_b + k][j * dim_b + k]"],
        "task_shor_decode_phase": ["amp_000", "amp_111"],
        "task_teleportation_corrections": ["m0 controls the X", "m1 controls the Z"],
        "concrete_qaoa_triangle_costs": ["'010'", "2"],
        "concrete_grover_diffusion_exact": ["[0.0, 0.0, 0.0, 1.0]"],
        "concrete_partial_trace_bell_b": ["maximally mixed", "[[0.5, 0.0], [0.0, 0.5]]"],
        "concrete_teleportation_all_bits": ["(1, 0): [\"X\"]", "ValueError"],
    }
    for id_, expected_terms in required.items():
        assert id_ in by_id
        assert by_id[id_]["coding_problem"] is True
        for term in expected_terms:
            assert term in by_id[id_]["expected_terms"]


def test_qwen36_rag_user_questions_v2_exact_subset_has_examples() -> None:
    payload = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    exact_items = [item for item in payload if item["judge_type"] == "unit_test_backed"]

    assert exact_items
    assert all(item["category"] == "quantum_coding_exact" for item in exact_items)
    assert any("->" in " ".join(item["example_io"]) for item in exact_items)
    assert any("raises ValueError" in " ".join(item["example_io"]) for item in exact_items)
    assert any("p=0.5" in item["query"] for item in exact_items)


def test_qwen36_rag_user_questions_v2_is_concrete_for_user_judging() -> None:
    payload = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    concrete_marker = re.compile(r"->|returns|must|expects|==|\[[^\]]+\]|\([^)]*\)")

    concrete_queries = [item for item in payload if concrete_marker.search(item["query"])]
    exact_items = [item for item in payload if item["judge_type"] == "unit_test_backed"]
    exact_tasks = {Path(item["unit_test_file"]).parent.name for item in exact_items}

    assert len(concrete_queries) >= 100
    assert len(exact_tasks) >= 25
    assert all(item.get("example_io") for item in exact_items)
    assert all(Path(item["unit_test_file"]).exists() for item in exact_items)
