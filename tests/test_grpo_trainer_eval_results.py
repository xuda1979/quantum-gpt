"""TDD: per-candidate harness results persist (verifier G1, 2026-08-25, r5).

The trainer used to parse the harness subprocess JSON into ``details`` and
DROP the rest — the reward-path verifier could only band-check live records
and candidates could not be re-run. This suite pins the append-only
``eval_results.jsonl`` contract:

  (a) a scored candidate's row appears and matches the recorded rewards
      (rollout_rewards components == row components; code_hash == sha256);
  (b) append-only across steps, parse-clean on a torn-write tolerant read
      (the reward audit's loader counts corrupt lines, never crashes);
  (c) the reward audit's --harness-results exact mode validates a LIVE row
      end-to-end (audit_step consumes the row the trainer wrote).

Loss math is untouched.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.sapo_reward_audit import (  # noqa: E402
    DEFAULT_WEIGHTS,
    audit_step,
    compose_total,
    load_step_records,
)
from training.grpo_trainer import (  # noqa: E402
    EVAL_RESULTS_FILENAME,
    build_eval_result_row,
    build_rollout_rewards,
    termination_save,
)
from training.grpo_utils import (  # noqa: E402
    append_grpo_metric_jsonl,
    shaped_reward_from_details,
)

CODE = "def solve():\n    return 42\n"


def _entry(passed: bool, details: list[str], verifier: float) -> dict:
    """A scored candidate entry in the shape evaluate_candidate returns."""
    shaped = float(shaped_reward_from_details(passed, details))
    return {
        "passed": passed,
        "pass_reward": 1.0 if passed else 0.0,
        "shaped_reward": shaped,
        "syntax_reward": 1.0,
        "interface_reward": 1.0 if passed else 0.5,
        "verifier_reward": verifier,
        "brevity_reward": 0.5,
        "import_hygiene_reward": 1.0,
        "total_reward": 1.0 if passed else 0.3,
        "details": list(details),
    }


# ---------------------------------------------------------------------------
# (a) row matches the recorded rewards
# ---------------------------------------------------------------------------


def test_eval_result_row_matches_recorded_rewards() -> None:
    entry = _entry(True, ["all tests passed"], verifier=1.0)
    row = build_eval_result_row(step=3, index=1, code=CODE, entry=entry, detail_budget=8)
    assert row["step"] == 3 and row["index"] == 1
    assert row["passed"] is True
    assert row["details"] == ["all tests passed"]
    assert row["detail_budget"] == 8
    assert row["code_hash"] == hashlib.sha256(CODE.encode("utf-8")).hexdigest()
    assert row["syntax"] == 1.0
    assert row["interface"] == 1.0
    assert row["verifier"] == 1.0
    assert row["import_hygiene"] == 1.0
    # the same candidate as recorded in rollout_rewards (post-merge total
    # excluded from the row by contract; the components must match exactly)
    rollout = build_rollout_rewards([entry], torch.zeros(1))[0]
    assert rollout["pass"] is row["passed"]
    assert rollout["syntax_reward"] == row["syntax"]
    assert rollout["interface_reward"] == row["interface"]
    assert rollout["verifier_reward"] == row["verifier"]
    assert rollout["import_hygiene_reward"] == row["import_hygiene"]
    # the builder's missing-fields regression: interface/brevity/hygiene now
    # ride in rollout_rewards (they used to be dropped)
    assert rollout["brevity_reward"] == 0.5
    assert row["detail_budget"] is not None  # fail case keeps budget too


def test_eval_result_row_failing_candidate() -> None:
    entry = _entry(False, ["fail: test_a", "fail: test_b"], verifier=0.6)
    row = build_eval_result_row(step=1, index=0, code="x = 1", entry=entry, detail_budget=5)
    assert row["passed"] is False
    assert row["details"] == ["fail: test_a", "fail: test_b"]
    assert row["verifier"] == 0.6
    assert row["syntax"] == 1.0  # syntax is code-level, not pass-gated


def test_eval_result_row_no_detail_budget() -> None:
    entry = _entry(False, ["fail"], verifier=0.0)
    row = build_eval_result_row(step=1, index=0, code="x", entry=entry)
    assert row["detail_budget"] is None


# ---------------------------------------------------------------------------
# (b) append-only across steps + torn-write tolerant read
# ---------------------------------------------------------------------------


def test_eval_results_append_only_across_steps_and_torn_tolerant(tmp_path: Path) -> None:
    path = tmp_path / EVAL_RESULTS_FILENAME
    # step 1: two candidates; step 2: one candidate
    for step, n_cands in ((1, 2), (2, 1)):
        for index in range(n_cands):
            entry = _entry(True, ["ok"], verifier=1.0)
            append_grpo_metric_jsonl(
                path,
                build_eval_result_row(
                    step=step, index=index, code=CODE, entry=entry, detail_budget=8
                ),
            )
    # torn mid-append tail (the write the snapshot/audit readers must survive)
    with path.open("a") as fh:
        fh.write('{"step": 2, "index": 1, "passed": tru\n')
    records, corrupt = load_step_records(path)
    assert corrupt == 1
    assert [(r["step"], r["index"]) for r in records] == [(1, 0), (1, 1), (2, 0)]
    # append-only: a resumed run's new step lands AFTER the prior records
    entry = _entry(False, ["fail"], verifier=0.0)
    append_grpo_metric_jsonl(
        path,
        build_eval_result_row(step=3, index=0, code=CODE, entry=entry, detail_budget=4),
    )
    records, corrupt = load_step_records(path)
    assert corrupt == 1
    assert [(r["step"], r["index"]) for r in records] == [(1, 0), (1, 1), (2, 0), (3, 0)]
    # parse-clean: every surviving row is valid JSON with the contract fields
    for r in records:
        for field in (
            "step",
            "index",
            "passed",
            "details",
            "detail_budget",
            "code_hash",
            "syntax",
            "interface",
            "verifier",
            "import_hygiene",
        ):
            assert field in r, (field, r)


# ---------------------------------------------------------------------------
# (c) reward audit --harness-results exact mode on a LIVE row
# ---------------------------------------------------------------------------


def test_reward_audit_exact_mode_validates_live_row() -> None:
    """The audit's exact mode (H1/H2) consumes the row the trainer persists:
    harness_pass_verdict, harness_shaped_recomputed (via the production
    shaped_reward_from_details) and harness_verifier_recomputed (via
    detail_budget) must all pass on a LIVE row."""
    details = ["all tests passed"]
    entry = _entry(True, details, verifier=1.0)
    row = build_eval_result_row(step=1, index=0, code=CODE, entry=entry, detail_budget=8)
    cand = build_rollout_rewards([entry], torch.zeros(1))[0]
    record = {"step": 1, "task": "quantum_demo", "rollout_rewards": [cand]}
    weights = dict(DEFAULT_WEIGHTS)
    result = audit_step(record, weights, harness_details=[row])
    assert result["ok"], result["errors"]
    assert result["errors"] == []


def test_reward_audit_exact_mode_validates_live_failing_row() -> None:
    """Fail case with the verifier band: verifier = 1 - failures/budget on a
    failing candidate must recompute exactly from the live row, and the total
    must sit at the exact composition point (interface/hygiene now recorded,
    so total_band collapses to [x, x])."""
    details = ["fail: test_a", "fail: test_b"]
    budget = 5
    verifier = 1.0 - min(len(details), budget) / budget  # 0.6
    entry = _entry(False, details, verifier=verifier)
    weights = dict(DEFAULT_WEIGHTS)
    # total must be the exact p_dominant composition (no free band once
    # interface/hygiene are recorded) — mirror the audit's compose_total
    entry["total_reward"] = compose_total(
        pass_reward=0.0,
        shaped=float(shaped_reward_from_details(False, details)),
        syntax=1.0,
        interface=0.5,
        verifier=verifier,
        brevity=0.5,
        hygiene=1.0,
        weights=weights,
    )
    row = build_eval_result_row(step=2, index=0, code=CODE, entry=entry, detail_budget=budget)
    cand = build_rollout_rewards([entry], torch.zeros(1))[0]
    record = {"step": 2, "task": "quantum_demo", "rollout_rewards": [cand]}
    result = audit_step(record, weights, harness_details=[row])
    assert result["ok"], result["errors"]


def test_eval_result_row_detail_budget_zero_preserved() -> None:
    """F4 (code-review wave): the falsy-zero check stored detail_budget 0 as
    None, diverging from the entry's capped budget and silently skipping the
    audit's H2 verifier check for that candidate."""
    entry = _entry(False, ["fail"], verifier=0.0)
    row = build_eval_result_row(step=1, index=0, code="x", entry=entry, detail_budget=0)
    assert row["detail_budget"] == 0  # preserved, not None


def test_termination_save_adapter_dir_atomic_under_save_failure(tmp_path: Path) -> None:
    """F3 (code-review wave): the SIGTERM adapter-dir save must be atomic —
    a save_pretrained interrupted mid-write (KILL escalation) must never
    leave a truncated adapter/ dir for the next launch's --adapter-init."""
    out = tmp_path / "run"
    out.mkdir()

    class _TornSave:
        """The step checkpoint save succeeds; the adapter-dir save (2nd call)
        writes a partial marker then dies (KILL-mid-write)."""

        def __init__(self) -> None:
            self.calls = 0

        def save_pretrained(self, path: Path) -> None:
            self.calls += 1
            path = Path(path)
            path.mkdir(parents=True, exist_ok=True)
            (path / "adapter_config.json").write_text("{}")
            (path / "adapter_model.safetensors").write_text("x")  # completeness rule
            if self.calls >= 2:
                raise RuntimeError("killed mid-write")

    import pytest as _pytest

    from tests.test_grpo_trainer_sigterm import TinyPreprocessor  # noqa: F401
    from training.grpo_trainer import GracefulStop  # noqa: F401

    with _pytest.raises(RuntimeError):
        termination_save(_TornSave(), TinyPreprocessor(), out, step=2, distributed=False, rank=0)
    adapter = out / "adapter"
    # no partial adapter dir survived; no temp leftovers
    assert not adapter.exists() or not (adapter / "adapter_config.json").exists()
    leftovers = [p for p in out.iterdir() if ".tmp-" in p.name or ".incomplete-" in p.name]
    assert leftovers == []
    # and the step checkpoint is still intact (the atomic step save)
    assert (out / "step_000002_adapter").is_dir()
