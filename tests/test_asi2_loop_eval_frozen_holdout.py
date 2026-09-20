"""TDD (2026-09-01, manager): the box-side perpetual eval loop MUST measure
the FROZEN promotion holdout, never a training benchmark.

Bug found: scripts/asi2_loop_eval.sh launched
run_asi2_base_adapter_rubric_eval.py WITHOUT --benchmark, so it defaulted to
evals/benchmarks/quantum_grpo_training_v1.txt — the 13-task TRAINING set whose
own header says "Do NOT use for evaluation/generalization testing". The
STANDUP #232 "step_000037 vs base TIED 1/13" verdict came from that wrong
instrument (13 tasks, only 4/18 overlap with the frozen holdout). Even a
genuinely-better adapter would never show beats-base through that loop.

Contract: the eval loop's EVAL_CMD must pass --benchmark pointing at the
frozen promotion holdout (env-overridable via EVAL_BENCHMARK for
experiments), and the loop must never fall back to a training benchmark.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOP = ROOT / "scripts" / "asi2_loop_eval.sh"
PROMOTION = ROOT / "evals/benchmarks/sapo_promotion_holdout_v1_18.txt"
TRAINING_V1 = ROOT / "evals/benchmarks/quantum_grpo_training_v1.txt"


def test_eval_loop_pins_frozen_holdout_benchmark() -> None:
    source = LOOP.read_text(encoding="utf-8")
    # the launch command must name the benchmark explicitly
    assert "--benchmark" in source
    # and the default must be the FROZEN promotion holdout (not v1 training)
    assert PROMOTION.name in source
    # env-overridable for experiments, but the default is the frozen holdout
    assert "${EVAL_BENCHMARK:-" in source


def test_eval_loop_default_benchmark_is_not_training_v1() -> None:
    source = LOOP.read_text(encoding="utf-8")
    # the training set must not appear as the benchmark default anywhere
    assert TRAINING_V1.name not in source


def test_promotion_holdout_is_frozen_18_and_disjoint_from_training() -> None:
    """Sanity: the promotion holdout the loop points at is the real 18-task
    frozen gate, disjoint from the current training manifest."""

    def ids(path: Path) -> set[str]:
        return {
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }

    promo = ids(PROMOTION)
    v8 = ids(ROOT / "evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt")
    assert len(promo) == 18
    assert promo.isdisjoint(v8)


def test_eval_benchmark_override_reaches_launch_command() -> None:
    """P-7 (code-steward, 2026-09-01): EVAL_BENCHMARK was DEAD CONFIG — the
    loop documented it as the env override but only the hardcoded
    EVAL_BENCHMARK_BOX reached the EVAL_CMD, so setting EVAL_BENCHMARK=...
    silently did nothing. The fix: derive EVAL_BENCHMARK_BOX from
    EVAL_BENCHMARK by stripping the local ROOT_DIR prefix (falling back to
    the basename for box-relative use). The source must derive the box path
    from the override knob, not hardcode it."""
    source = LOOP.read_text(encoding="utf-8")
    # the box path must be DERIVED from EVAL_BENCHMARK (strip ROOT_DIR prefix)
    assert "${EVAL_BENCHMARK#" in source, "EVAL_BENCHMARK_BOX must derive from EVAL_BENCHMARK"
    # the launch command uses the derived box path
    assert "'${EVAL_BENCHMARK_BOX}'" in source


def test_only_provable_inert_skips_holdout_eval() -> None:
    """2026-09-02 (manager, realtime bug fix): the precheck must SKIP the
    frozen holdout eval ONLY for the PROVABLY-inert case (adapter delta exactly
    0 / all LoRA-B zero). Any nonzero delta — including the 'inert_at_precision'
    category (nonzero but below one bf16 ULP at the largest weight) — MUST reach
    the rubric eval, because rank-16 LoRA deltas (~1e-4-1e-3) are far below the
    bf16 ULP at ~19-magnitude weights (0.125) yet are behaviorally significant
    (resume-3 step_000009: 25% strict pass in the trainer, and adapter_delta
    classified inert_at_precision). Gating inert_at_precision out silently made
    the beats-base instrument unable to EVER return a verdict.
    """
    source = LOOP.read_text(encoding="utf-8")
    # the skip branch must select ONLY the provable-inert case
    skip = source.split('if [[ "$PRECHECK_VERDICT"', 1)[1].split("fi", 1)[0]
    assert '== "inert"' in skip
    assert '== "inert_at_precision"' not in skip
    # the inert_at_precision branch must proceed (not skip) to the eval
    assert "proceeding to the frozen holdout eval" in source
    # the inert skip must exit before the rubric eval, and the write must be
    # keyed by the checkpoint's full-path identity (E2, the B-105 law)
    assert 'update_state "$STATE_KEY" "inert" "adapter_delta_zero"' in source
    assert 'update_state "$TS"' not in source
