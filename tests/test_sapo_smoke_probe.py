"""Regression: promotion-leg smoke probe must report greedy Pass@1 AND
sampled Pass@K=4, and REFUSE the full leg when greedy syntax is fragile.

2026-08-27 audit (Research Audit T2): run-5 step-26 scored 0/18 because its
GREEDY (temp 0) decoding collapsed into unparseable prompt-echoes while the
trainer's SAMPLED rollouts (temp 1.0-1.15) looked healthy — a greedy-only
probe pass was the trap. The probe therefore measures BOTH modes and gates
the full leg on the greedy syntax rate (< 0.6 → BLOCKED).

These tests lock the pure logic (rate math + refusal gate). The model-driven
probe itself runs on the box via scripts/sapo_smoke_probe.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.sapo_smoke_probe import (  # noqa: E402
    candidate_parses,
    gate_verdict,
    offline_probe,
    pass_at_k,
    pass_at_k_estimator,
    syntax_rate,
)

# ── candidate_parses ────────────────────────────────────────────────────────


def test_candidate_parses_accepts_valid_code() -> None:
    assert candidate_parses("def solve():\n    return 42\n")


def test_candidate_parses_rejects_prompt_echo_with_unicode() -> None:
    # The run-5 s26 failure class: prompt echo with math Unicode.
    assert not candidate_parses("I need to implement ρ = |ψ⟩⟨ψ| → compute it.")


def test_candidate_parses_rejects_unterminated_string() -> None:
    assert not candidate_parses("x = 'oops")


# ── syntax_rate (greedy Pass@1) ─────────────────────────────────────────────


def test_syntax_rate_fraction() -> None:
    assert syntax_rate([True, True, False]) == pytest.approx(2 / 3)
    assert syntax_rate([True, True, True]) == 1.0
    assert syntax_rate([False, False]) == 0.0


def test_syntax_rate_empty_is_zero() -> None:
    assert syntax_rate([]) == 0.0


# ── pass_at_k (sampled Pass@K=4: task passes if >=1 of K parses) ────────────


def test_pass_at_k_task_passes_with_any_parseable_sample() -> None:
    # 3 tasks x 4 samples; task 2 has only 1 parseable sample.
    task_results = [
        [True, True, True, True],
        [False, False, False, True],
        [False, False, False, False],
    ]
    assert pass_at_k(task_results) == pytest.approx(2 / 3)


def test_pass_at_k_all_or_nothing() -> None:
    assert pass_at_k([[True] * 4] * 3) == 1.0
    assert pass_at_k([[False] * 4] * 3) == 0.0


def test_pass_at_k_empty_is_zero() -> None:
    assert pass_at_k([]) == 0.0


# ── unbiased pass@k estimator ────────────────────────────────────────────────


def test_pass_at_k_estimator_exact_on_synthetic_sets() -> None:
    # n = k = 4: any correct sample → 1.0; none → 0.0 (the probe default).
    assert pass_at_k_estimator(4, 0, 4) == 0.0
    assert pass_at_k_estimator(4, 1, 4) == 1.0
    assert pass_at_k_estimator(4, 4, 4) == 1.0
    # Non-degenerate n > k: exact closed form.
    assert pass_at_k_estimator(8, 1, 4) == pytest.approx(1 - 35 / 70)  # C(7,4)/C(8,4)
    assert pass_at_k_estimator(8, 2, 4) == pytest.approx(1 - 15 / 70)  # C(6,4)/C(8,4)
    assert pass_at_k_estimator(8, 4, 4) == pytest.approx(1 - 1 / 70)  # C(4,4)/C(8,4)
    assert pass_at_k_estimator(8, 5, 4) == 1.0  # k >= n-c+1: any draw has a correct


def test_pass_at_k_estimator_guards() -> None:
    assert pass_at_k_estimator(0, 0, 4) == 0.0
    assert pass_at_k_estimator(4, -1, 4) == 0.0
    assert pass_at_k_estimator(4, 1, 0) == 0.0


# ── offline probe on cached candidates (spec: estimator runs offline) ────────


def test_offline_probe_rates_and_gate(tmp_path: Path) -> None:
    tasks = ["t1", "t2", "t3"]
    # t1: greedy ok, 4/4 sampled ok. t2: greedy broken, 1/4 sampled ok.
    # t3: greedy ok, 0/4 sampled ok.
    (tmp_path / "t1.py").write_text("def solve():\n    return 1\n")
    for i in range(4):
        (tmp_path / f"t1__k{i}.py").write_text("def solve():\n    return 1\n")
    (tmp_path / "t2.py").write_text("I need to implement ρ = |ψ⟩⟨ψ| → nope")
    (tmp_path / "t2__k0.py").write_text("def solve():\n    return 2\n")
    (tmp_path / "t3.py").write_text("def solve():\n    return 3\n")

    rec = offline_probe(tmp_path, tasks, sample_k=4)
    assert rec["greedy"]["syntax_rate"] == pytest.approx(2 / 3)
    assert rec["sampled"]["pass_at_k"] == pytest.approx(2 / 3)  # t1, t2 pass
    assert rec["gate"]["verdict"] == "CLEAR"  # 2/3 >= 0.6


def test_offline_probe_blocks_greedy_fragile(tmp_path: Path) -> None:
    tasks = ["a", "b", "c"]
    for t in tasks:
        (tmp_path / f"{t}.py").write_text("prompt echo → broken")
        (tmp_path / f"{t}__k0.py").write_text("def ok():\n    pass\n")  # sampled only
    rec = offline_probe(tmp_path, tasks, sample_k=4)
    assert rec["greedy"]["syntax_rate"] == 0.0
    assert rec["sampled"]["pass_at_k"] == 1.0  # sampled healthy — the s26 trap
    assert rec["gate"]["verdict"] == "BLOCKED"  # greedy gate fires anyway


# ── refusal gate: greedy syntax rate < 0.6 → BLOCKED ────────────────────────


def test_gate_blocks_below_threshold() -> None:
    # 1/3 parseable — the run-5 s26 class.
    assert gate_verdict(1 / 3, min_rate=0.6) == "BLOCKED"
    assert gate_verdict(0.0, min_rate=0.6) == "BLOCKED"


def test_gate_clears_at_and_above_threshold() -> None:
    assert gate_verdict(0.6, min_rate=0.6) == "CLEAR"  # boundary inclusive
    assert gate_verdict(2 / 3, min_rate=0.6) == "CLEAR"
    assert gate_verdict(1.0, min_rate=0.6) == "CLEAR"


def test_gate_requires_evidence() -> None:
    # No tasks measured: no evidence → BLOCKED, never a silent CLEAR.
    assert gate_verdict(0.0, min_rate=0.6, measured_tasks=0) == "BLOCKED"
    assert gate_verdict(1.0, min_rate=0.6, measured_tasks=0) == "BLOCKED"


# ── CLI: offline mode must parse without model args ─────────────────────────


def test_offline_cli_parses_without_ckpt_or_base_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """--offline alone must be a valid invocation (no model load); the live
    mode still demands --ckpt/--base-model."""
    import sys as _sys

    from scripts.sapo_smoke_probe import main as probe_main

    argv = [
        "sapo_smoke_probe.py",
        "--offline",
        "/tmp/cands",
        "--task-id-file",
        "evals/benchmarks/sapo_smoke_probe_v1_3.txt",
        "--sample-k",
        "4",
        "--run-name",
        "x",
        "--out",
        "/tmp/x.json",
    ]
    monkeypatch.setattr(_sys, "argv", argv)
    # Runs offline and BLOCKs on an empty dir (no evidence) — exit code 3 is
    # the correct offline verdict path (main() returns the exit code).
    assert probe_main() == 3  # empty offline dir -> no evidence -> BLOCKED


# ── T2b: runner accepts the informational temp-0.6 path ─────────────────────


def test_runner_accepts_temperature_0_6(monkeypatch: pytest.MonkeyPatch) -> None:
    """The informational temp-0.6 leg is the same runner with
    --temperature 0.6 — the CLI path must accept it (spec T2b)."""
    import sys as _sys

    from scripts.run_hf_pass1_eval import parse_args

    argv = [
        "run_hf_pass1_eval.py",
        "--run-dir",
        "evals/runs/x",
        "--base-model",
        "/models/base",
        "--device",
        "npu",
        "--device-map",
        "balanced-layers",
        "--npu-max-memory-gib",
        "54",
        "--token-budget-preset",
        "quantum_heavy",
        "--temperature",
        "0.6",
        "--score",
    ]
    monkeypatch.setattr(_sys, "argv", argv)
    args = parse_args()
    assert args.temperature == 0.6
    assert args.score is True
