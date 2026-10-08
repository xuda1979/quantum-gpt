#!/usr/bin/env python3
"""Unit tests for the multi-round self-correcting distillation orchestrator.

Covers:
  - teacher_question_generator: JSON parsing, weakness briefing, contract
    sampling (determinism + blend), batch generation with a fake HTTP
    callable, Q-gate rejection path, question-id stability.
  - analyze_scd_weakness: per-cell pass-rate aggregation, min-cell-n
    filtering, overall pass rate, skipped handling.
  - self_correcting_distill_rounds: config loading, round-state
    resume/skip logic, prior-distribution passthrough.

These tests do NOT hit the network: the HTTP POST in
teacher_question_generator._post_json is bypassed by injecting a fake
`_call_teacher_chat` via monkeypatch.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_scd_weakness as scdw  # noqa: E402
import teacher_question_generator as tqg  # noqa: E402

# ---------------------------------------------------------------------------
# parse_teacher_json
# ---------------------------------------------------------------------------


def test_parse_teacher_json_plain():
    assert tqg.parse_teacher_json('{"a": 1}') == {"a": 1}


def test_parse_teacher_json_with_fences():
    raw = '```json\n{"is_valid": true}\n```'
    assert tqg.parse_teacher_json(raw) == {"is_valid": True}


def test_parse_teacher_json_with_preamble():
    raw = 'Here is the answer: {"question": "x"} done'
    assert tqg.parse_teacher_json(raw) == {"question": "x"}


def test_parse_teacher_json_raises_on_garbage():
    with pytest.raises(json.JSONDecodeError):
        tqg.parse_teacher_json("not json at all")


# ---------------------------------------------------------------------------
# build_weakness_brief
# ---------------------------------------------------------------------------


def test_weakness_brief_empty_report():
    brief = tqg.build_weakness_brief({})
    assert "round 0" in brief


def test_weakness_brief_no_cells():
    brief = tqg.build_weakness_brief({"cells": [], "overall_pass_rate": 0.5})
    assert "balanced mix" in brief


def test_weakness_brief_with_cells():
    report = {
        "overall_pass_rate": 0.3,
        "cells": [
            {
                "framework": "qiskit",
                "topic": "circuits",
                "difficulty": "easy",
                "pass_rate": 0.1,
                "n": 5,
            },
            {"framework": "cirq", "topic": "noise", "difficulty": "hard", "pass_rate": 0.2, "n": 4},
        ],
    }
    brief = tqg.build_weakness_brief(report)
    assert "qiskit" in brief
    assert "circuits" in brief
    assert "pass=" in brief


# ---------------------------------------------------------------------------
# sample_contracts
# ---------------------------------------------------------------------------


def test_sample_contracts_count_and_keys():
    import random

    rng = random.Random(42)
    prior = {
        "framework": {"qiskit": 0.5, "cirq": 0.5},
        "topic": {"circuits": 0.5, "noise": 0.5},
        "difficulty": {"easy": 0.5, "hard": 0.5},
    }
    contracts = tqg.sample_contracts(50, {}, prior, rng)
    assert len(contracts) == 50
    for c in contracts:
        assert c.framework in {"qiskit", "cirq"}
        assert c.topic in {"circuits", "noise"}
        assert c.difficulty in {"easy", "hard"}


def test_sample_contracts_deterministic_with_seed():
    import random

    prior = {
        "framework": {"qiskit": 0.5, "cirq": 0.5},
        "topic": {"circuits": 1.0},
        "difficulty": {"easy": 1.0},
    }
    rng1 = random.Random(123)
    rng2 = random.Random(123)
    c1 = tqg.sample_contracts(20, {}, prior, rng1)
    c2 = tqg.sample_contracts(20, {}, prior, rng2)
    assert [c.framework for c in c1] == [c.framework for c in c2]


def test_sample_contracts_weakness_upweights_weak_cells():
    """When the weakness report shows qiskit is much weaker than cirq,
    and blend_alpha is high, qiskit should be sampled more often."""
    import random

    prior = {
        "framework": {"qiskit": 0.5, "cirq": 0.5},
        "topic": {"circuits": 1.0},
        "difficulty": {"easy": 1.0},
    }
    weakness = {
        "cells": [
            {
                "framework": "qiskit",
                "topic": "circuits",
                "difficulty": "easy",
                "pass_rate": 0.0,
                "n": 10,
            },
            {
                "framework": "cirq",
                "topic": "circuits",
                "difficulty": "easy",
                "pass_rate": 1.0,
                "n": 10,
            },
        ]
    }
    rng = random.Random(7)
    contracts = tqg.sample_contracts(200, weakness, prior, rng, blend_alpha=0.9, min_weight=0.01)
    n_qiskit = sum(1 for c in contracts if c.framework == "qiskit")
    n_cirq = sum(1 for c in contracts if c.framework == "cirq")
    # qiskit (pass_rate=0) should dominate cirq (pass_rate=1).
    assert n_qiskit > n_cirq * 2


def test_sample_contracts_empty_prior_uses_weakness_keys():
    import random

    rng = random.Random(0)
    weakness = {
        "cells": [
            {
                "framework": "qiskit",
                "topic": "circuits",
                "difficulty": "easy",
                "pass_rate": 0.0,
                "n": 5,
            },
        ]
    }
    contracts = tqg.sample_contracts(10, weakness, {}, rng)
    assert len(contracts) == 10
    # With empty prior, the fallback should at least produce "qiskit" sometimes.
    frameworks = {c.framework for c in contracts}
    assert "qiskit" in frameworks or frameworks == {"unknown"}


# ---------------------------------------------------------------------------
# teacher_generate_one + teacher_generate_batch (with fake HTTP)
# ---------------------------------------------------------------------------


def _fake_qgen_response(
    question_text: str, framework="qiskit", topic="circuits", difficulty="easy"
) -> str:
    return json.dumps(
        {
            "question": question_text,
            "framework": framework,
            "topic": topic,
            "difficulty": difficulty,
            "requires_full_program": True,
            "expected_answer_summary": "A correct solution prints 42.",
        }
    )


def _fake_qgate_response(is_valid: bool, improved: str = "") -> str:
    return json.dumps(
        {
            "is_valid": is_valid,
            "reasons": [] if is_valid else ["too vague"],
            "improved_question": improved,
        }
    )


def test_teacher_generate_one_success(monkeypatch):
    """Teacher returns a valid question and the Q-gate accepts it."""
    calls = {"n": 0}

    def fake_chat(cfg, system_prompt, user_prompt, json_mode=True):
        calls["n"] += 1
        if "Author ONE new quantum-coding question" in user_prompt:
            return _fake_qgen_response("Write a Qiskit program that prints 42.")
        if "Review the following proposed quantum-coding question" in user_prompt:
            return _fake_qgate_response(True)
        raise AssertionError(f"unexpected prompt: {user_prompt[:80]}")

    monkeypatch.setattr(tqg, "_call_teacher_chat", fake_chat)
    cfg = tqg.TeacherQGenConfig(
        api_base="http://fake/v1", api_key="k", model="glm5.2", qgate_enabled=True
    )
    contract = tqg.QuestionContract(framework="qiskit", topic="circuits", difficulty="easy")
    gq = tqg.teacher_generate_one(cfg, contract, {}, round_index=0)
    assert gq.question.startswith("Write a Qiskit program")
    assert gq.framework == "qiskit"
    assert gq.source == "teacher_glm52"
    assert gq.round_index == 0
    assert gq.question_id.startswith("tq_")
    assert gq.qgate_verdict == {"is_valid": True, "reasons": [], "improved_question": ""}


def test_teacher_generate_one_qgate_replaces_with_improved(monkeypatch):
    def fake_chat(cfg, system_prompt, user_prompt, json_mode=True):
        if "Author ONE" in user_prompt:
            return _fake_qgen_response("Write a program that prints a number.")
        if "Review the following" in user_prompt:
            return _fake_qgate_response(
                True, improved="Write a Qiskit program that prints exactly 42."
            )
        raise AssertionError

    monkeypatch.setattr(tqg, "_call_teacher_chat", fake_chat)
    cfg = tqg.TeacherQGenConfig(api_base="http://fake/v1", api_key="k", model="glm5.2")
    contract = tqg.QuestionContract(framework="qiskit", topic="circuits", difficulty="easy")
    gq = tqg.teacher_generate_one(cfg, contract, {}, round_index=1)
    assert gq.question == "Write a Qiskit program that prints exactly 42."


def test_teacher_generate_one_empty_question_raises(monkeypatch):
    def fake_chat(cfg, system_prompt, user_prompt, json_mode=True):
        return json.dumps(
            {"question": "", "framework": "qiskit", "topic": "circuits", "difficulty": "easy"}
        )

    monkeypatch.setattr(tqg, "_call_teacher_chat", fake_chat)
    cfg = tqg.TeacherQGenConfig(
        api_base="http://fake/v1", api_key="k", model="glm5.2", qgate_enabled=False
    )
    contract = tqg.QuestionContract(framework="qiskit", topic="circuits", difficulty="easy")
    with pytest.raises(RuntimeError, match="empty question"):
        tqg.teacher_generate_one(cfg, contract, {}, round_index=0)


def test_teacher_generate_batch_drops_qgate_rejections(monkeypatch):
    """If the Q-gate rejects, the question should be dropped from the batch."""

    def fake_chat(cfg, system_prompt, user_prompt, json_mode=True):
        if "Author ONE" in user_prompt:
            return _fake_qgen_response("vague question")
        if "Review the following" in user_prompt:
            return _fake_qgate_response(False)
        raise AssertionError

    monkeypatch.setattr(tqg, "_call_teacher_chat", fake_chat)
    cfg = tqg.TeacherQGenConfig(
        api_base="http://fake/v1", api_key="k", model="glm5.2", max_concurrency=2
    )
    contracts = [tqg.QuestionContract("qiskit", "circuits", "easy") for _ in range(5)]
    results = tqg.teacher_generate_batch(cfg, contracts, {}, round_index=0)
    assert results == [], "all Q-gate rejections should be dropped"


def test_teacher_generate_batch_accepts_valid(monkeypatch):
    def fake_chat(cfg, system_prompt, user_prompt, json_mode=True):
        if "Author ONE" in user_prompt:
            return _fake_qgen_response(f"Question #{user_prompt.count('qiskit')}")
        if "Review" in user_prompt:
            return _fake_qgate_response(True)
        raise AssertionError

    monkeypatch.setattr(tqg, "_call_teacher_chat", fake_chat)
    cfg = tqg.TeacherQGenConfig(
        api_base="http://fake/v1", api_key="k", model="glm5.2", max_concurrency=3
    )
    contracts = [tqg.QuestionContract("qiskit", "circuits", "easy") for _ in range(8)]
    results = tqg.teacher_generate_batch(cfg, contracts, {}, round_index=0)
    assert len(results) == 8
    for gq in results:
        assert gq.qgate_verdict["is_valid"] is True


def test_generated_question_to_pool_row_roundtrip():
    gq = tqg.GeneratedQuestion(
        question_id="tq_abc123",
        question="Write a program.",
        framework="qiskit",
        topic="circuits",
        difficulty="easy",
        requires_full_program=True,
        expected_answer_summary="prints 42",
        round_index=2,
        contract=tqg.QuestionContract("qiskit", "circuits", "easy", "pass=0.1"),
        qgate_verdict={"is_valid": True, "reasons": [], "improved_question": ""},
        generated_at="2026-07-16T00:00:00Z",
    )
    row = tqg.generated_question_to_pool_row(gq)
    assert row["question_id"] == "tq_abc123"
    assert row["source"] == "teacher_glm52"
    assert row["round_index"] == 2
    assert row["framework"] == "qiskit"
    assert row["contract"]["weakness_hint"] == "pass=0.1"
    # Serialize + parse roundtrip.
    parsed = json.loads(json.dumps(row))
    assert parsed["question_id"] == "tq_abc123"


def test_question_id_stability():
    """Same question text + round + contract => same id."""
    c = tqg.QuestionContract("qiskit", "circuits", "easy")
    qid1 = tqg._make_question_id("Write a program.", 0, c)
    qid2 = tqg._make_question_id("Write a program.", 0, c)
    qid3 = tqg._make_question_id("Write a different program.", 0, c)
    assert qid1 == qid2
    assert qid1 != qid3


# ---------------------------------------------------------------------------
# analyze_scd_weakness
# ---------------------------------------------------------------------------


def _write_evals(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def test_weakness_report_basic(tmp_path):
    records = [
        {
            "question_id": "q1",
            "status": "accepted",
            "is_correct": True,
            "student_answer": {"framework": "qiskit", "topic": "circuits", "difficulty": "easy"},
            "teacher_eval": {"parsed": {"is_correct": True}},
        },
        {
            "question_id": "q2",
            "status": "corrected",
            "is_correct": False,
            "student_answer": {"framework": "qiskit", "topic": "circuits", "difficulty": "easy"},
            "teacher_eval": {"parsed": {"is_correct": False}},
        },
        {
            "question_id": "q3",
            "status": "accepted",
            "is_correct": True,
            "student_answer": {"framework": "cirq", "topic": "noise", "difficulty": "hard"},
            "teacher_eval": {"parsed": {"is_correct": True}},
        },
    ]
    _write_evals(tmp_path / "teacher_evals.jsonl", records)
    report = scdw.build_weakness_report(tmp_path, min_cell_n=1)
    assert report["n_samples"] == 3
    assert report["n_pass"] == 2
    assert report["overall_pass_rate"] == round(2 / 3, 4)
    # Weakest cell first (qiskit/circuits/easy: 1/2 = 0.5; cirq/noise/hard: 1/1 = 1.0).
    assert report["cells"][0]["framework"] == "qiskit"
    assert report["cells"][0]["pass_rate"] == 0.5


def test_weakness_report_min_cell_n(tmp_path):
    """Cells with n < min_cell_n are dropped."""
    records = [
        {
            "status": "accepted",
            "is_correct": True,
            "student_answer": {"framework": "qiskit", "topic": "circuits", "difficulty": "easy"},
            "teacher_eval": {"parsed": {"is_correct": True}},
        },
        {
            "status": "accepted",
            "is_correct": True,
            "student_answer": {"framework": "cirq", "topic": "noise", "difficulty": "hard"},
            "teacher_eval": {"parsed": {"is_correct": True}},
        },
        {
            "status": "accepted",
            "is_correct": True,
            "student_answer": {"framework": "cirq", "topic": "noise", "difficulty": "hard"},
            "teacher_eval": {"parsed": {"is_correct": True}},
        },
    ]
    _write_evals(tmp_path / "teacher_evals.jsonl", records)
    report = scdw.build_weakness_report(tmp_path, min_cell_n=2)
    # qiskit cell has n=1 -> dropped; cirq cell has n=2 -> kept.
    assert report["n_cells"] == 1
    assert report["cells"][0]["framework"] == "cirq"


def test_weakness_report_skipped_not_counted(tmp_path):
    records = [
        {
            "question_id": "q1",
            "status": "skipped_no_eval",
            "is_correct": False,
            "student_answer": {},
        },
        {
            "question_id": "q2",
            "status": "accepted",
            "is_correct": True,
            "student_answer": {"framework": "qiskit", "topic": "circuits", "difficulty": "easy"},
            "teacher_eval": {"parsed": {"is_correct": True}},
        },
    ]
    _write_evals(tmp_path / "teacher_evals.jsonl", records)
    report = scdw.build_weakness_report(tmp_path, min_cell_n=1)
    assert report["n_samples"] == 1
    assert report["n_skipped"] == 1
    assert report["n_pass"] == 1


def test_weakness_report_falls_back_to_top_level_is_correct(tmp_path):
    """When teacher_eval.parsed.is_correct is missing, use record.is_correct."""
    records = [
        {
            "status": "accepted",
            "is_correct": False,
            "student_answer": {"framework": "qiskit", "topic": "circuits", "difficulty": "easy"},
            "teacher_eval": {},
        },
    ]
    _write_evals(tmp_path / "teacher_evals.jsonl", records)
    report = scdw.build_weakness_report(tmp_path, min_cell_n=1)
    assert report["n_pass"] == 0
    assert report["cells"][0]["pass_rate"] == 0.0


def test_weakness_report_empty_dir(tmp_path):
    report = scdw.build_weakness_report(tmp_path)
    assert report["n_samples"] == 0
    assert report["overall_pass_rate"] == 0.0
    assert report["cells"] == []


# ---------------------------------------------------------------------------
# self_correcting_distill_rounds config loading
# ---------------------------------------------------------------------------


def test_rounds_config_loads(tmp_path):
    import self_correcting_distill_rounds as scdr

    cfg_path = tmp_path / "cfg.json"
    cfg_dict = {
        "name": "test",
        "output_dir": "data/generated/test_rounds",
        "seed": 42,
        "dataset_spec": {"target_question_count": 100},
        "rounds": {
            "enabled": True,
            "max_rounds": 3,
            "batch_size": 50,
            "teacher_qgen": {
                "model": "glm5.2",
                "api_base_env": "GLM52_API_BASE",
                "api_key_env": "GLM52_API_KEY",
                "temperature": 0.5,
                "qgate_enabled": True,
                "max_concurrency": 4,
            },
            "prior_distribution": {
                "framework": {"qiskit": 1.0},
                "topic": {"circuits": 1.0},
                "difficulty": {"easy": 1.0},
            },
            "blend_alpha": 0.3,
        },
    }
    cfg_path.write_text(json.dumps(cfg_dict))
    args = type(
        "A",
        (),
        {
            "max_rounds": 0,
            "batch_size": 0,
            "workers": 2,
            "no_git_sync": False,
            "no_git_push": False,
        },
    )()
    cfg = scdr.load_rounds_config(cfg_path, args)
    assert cfg.max_rounds == 3
    assert cfg.batch_size == 50
    assert cfg.teacher_qgen.model == "glm5.2"
    assert cfg.blend_alpha == 0.3
    assert cfg.prior_distribution["framework"]["qiskit"] == 1.0


def test_rounds_config_disabled_raises(tmp_path):
    import self_correcting_distill_rounds as scdr

    cfg_path = tmp_path / "cfg.json"
    cfg_dict = {
        "output_dir": "data/generated/x",
        "seed": 1,
        "dataset_spec": {"target_question_count": 10},
        "rounds": {"enabled": False},
    }
    cfg_path.write_text(json.dumps(cfg_dict))
    args = type(
        "A",
        (),
        {
            "max_rounds": 0,
            "batch_size": 0,
            "workers": 1,
            "no_git_sync": False,
            "no_git_push": False,
        },
    )()
    with pytest.raises(SystemExit):
        scdr.load_rounds_config(cfg_path, args)


def test_round_dir_naming():
    import self_correcting_distill_rounds as scdr

    d = scdr.round_dir(Path("/tmp/out"), 7)
    assert d.name == "round_007"
    d0 = scdr.round_dir(Path("/tmp/out"), 0)
    assert d0.name == "round_000"


def test_round_state_write_read(tmp_path):
    import self_correcting_distill_rounds as scdr

    rdir = tmp_path / "round_001"
    state = {"round_index": 1, "status": "completed"}
    scdr.write_round_state(rdir, state)
    loaded = scdr.load_round_state(rdir)
    assert loaded == state
    assert scdr.load_round_state(tmp_path / "round_999") is None


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
