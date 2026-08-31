"""Regression tests for the SAPO metrics poller's row parser.

Real cases that bit the live loop (2026-08-24):
1. terminal line-wrap splitting a float token ("loss -0.00" + "7 grad 0.75")
   -> the parser re-paired the fragment as a fresh key, corrupting the row
   (grad silently defaulted to 0.0 -> false NO-OP/SUB-PRECISION signals);
2. /exec capture truncation dropping leading lines -> partial rows must be
   DROPPED (essential-keys guard), not filled with 0.0 defaults;
3. skip-vs-noop predicate: repair-routed skips are NOT no-op updates;
4. corrupted values (non-float in a float key) must drop the row, not crash.

The parser is exercised with synthetic PARSER-emitter lines (the exact format
the box-side parser prints: "S<step> key val key val ...").
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".sapo-loop"))
import sapo_metrics_poll as poll  # noqa: E402


# ---- synthetic PARSER-emitter lines (as emitted by the box-side parser) ----
def full_step(
    step: int,
    *,
    loss: float = -0.0108,
    grad: float = 0.1582,
    pass_rate: float = 0.0,
    shaped: float = 0.0,
    entropy: float = 0.3,
    skipped: bool = False,
) -> str:
    s = f"S{step} loss {loss:.4f} grad {grad:.4f}\n"
    s += f"S{step} ratio 1.0428 rafter 1.0428 kl 6.08e-03\n"
    s += f"S{step} kl_aft 6.08e-03 ent {entropy:.3f}\n"
    s += f"S{step} pass {pass_rate:.3f} rew 0.1375 shaped {shaped:.4f}\n"
    s += f"S{step} rstd 0.2222 sig 0.2222 syn 1.000 trunc 0.000\n"
    s += f"S{step} tok 1668 rlen 417.0\n"
    s += f"S{step} clip 0.0000 fail False skip {str(skipped).lower()} trust False\n"
    s += f"S{step} lr 2e-05 ema 0.1200 ts 05:12:33Z\n"
    s += f"S{step} task quantum_phase_measurement_register\n"
    return s


def test_parse_rows_joins_float_token_split_across_terminal_wrap() -> None:
    """2026-08-24 real case: the daemon capture wrapped a line mid-float
    ("loss -0.00" newline "7 grad 0.75"). The old continuation logic re-paired
    the fragment as a fresh key (junk key "7"), leaving grad MISSING -> the
    float-keys default filled grad=0.0 -> false SUB-PRECISION/NO-OP alerts.
    The fragment must re-join the previous value: loss=-0.007, grad=0.75.
    """
    text = full_step(1)
    text = text.replace("loss -0.0108", "loss -0.00\n7", 1)
    text = text.replace("grad 0.1582", "grad 0.75", 1)
    rows = poll.parse_rows(text)
    assert len(rows) == 1
    assert rows[0]["step"] == 1
    assert rows[0]["loss"] == pytest.approx(-0.007, abs=1e-9)
    assert rows[0]["grad"] == pytest.approx(0.75)


def test_parse_rows_joins_wrap_split_between_pairs() -> None:
    """Wrap between key-value pairs ("... grad" newline "0.1582 ...") must
    keep the pairing intact (continuation tokens become pairs, not fragments)."""
    text = full_step(1).replace("loss -0.0108 grad 0.1582", "loss -0.0108 grad\n0.1582", 1)
    rows = poll.parse_rows(text)
    assert len(rows) == 1
    assert rows[0]["loss"] == pytest.approx(-0.0108)
    assert rows[0]["grad"] == pytest.approx(0.1582)


def test_parse_rows_drops_partial_rows_from_truncated_capture() -> None:
    """/exec capture truncation dropped the FIRST lines of step 2 (leading-line
    loss). A row missing essential keys (loss/entropy_mean/pass_rate/
    mean_reward/shaped) must be DROPPED, not defaulted to 0.0 (false alerts)."""
    text = full_step(1)
    text += "\n".join(full_step(2).splitlines()[2:]) + "\n"  # drop step-2 line 1 (loss)
    rows = poll.parse_rows(text)
    steps = [r["step"] for r in rows]
    assert 1 in steps
    assert 2 not in steps


def test_parse_rows_rejects_corrupted_float_values() -> None:
    """A non-float token pair (wrap corruption) in a float key must drop that
    row silently, not raise."""
    text = full_step(1).replace("grad 0.1582", "grad boom", 1)
    rows = poll.parse_rows(text)
    assert rows == []


def test_state_cursor_reconcile_detects_backward_reset() -> None:
    """2026-09-01 metrics audit (item 3): the poller's delta cursor must
    never silently sit AHEAD of the live data. A stale state whose last_step
    EXCEEDS the latest parsed step (run restarted with fresh step numbering,
    metrics file replaced, PID-reused trainer) must be detected and rebased
    — otherwise new_rows stays empty forever, the delta report silently
    prints "new steps 0", steps_advanced goes negative, and the verdict can
    read HEALTHY on mismatched run data (the silent-'all good' class)."""
    rows = [
        {
            "step": 10,
            "loss": -0.01,
            "grad": 0.1,
            "ratio_mean": 1.0,
            "seq_kl_after": 0.0,
            "pass_rate": 0.0,
            "mean_reward": 0.4,
            "shaped": 0.4,
            "sig_rms": 0.1,
            "truncation": 0.0,
            "entropy_mean": 0.3,
            "clip_after": 0.0,
            "gen_tok": 1000,
            "all_fail": False,
            "skipped": False,
            "trust": False,
            "ts": "",
            "task": "",
            "lr": "",
        }
    ]
    # backward counter (cursor 50 > live step 10): rebase + loud alert
    rebased, alert = poll.reconcile_state_cursor(50, rows)
    assert rebased == 10
    assert alert is not None and "STATE-RESET" in alert
    # cursor behind the data (normal: first poll after downtime): no alert,
    # cursor unchanged so all newer rows stay "new"
    rebased2, alert2 = poll.reconcile_state_cursor(5, rows)
    assert rebased2 == 5
    assert alert2 is None
    # cursor equal to the latest step (no new steps between polls): no alert
    assert poll.reconcile_state_cursor(10, rows)[1] is None
    # no cursor yet / no rows: never an alert
    assert poll.reconcile_state_cursor(0, rows) == (0, None)
    assert poll.reconcile_state_cursor(0, []) == (0, None)


def test_metrics_report_never_claims_trainer_alive_on_dead_or_unknown() -> None:
    # bug class 2026-08-31: write_metrics rendered "Process: trainer alive"
    # UNCONDITIONALLY — the TRAINER DEAD alert report simultaneously claimed
    # "trainer alive", and POLL-FAIL/POLL-NODATA (no liveness evidence)
    # reports claimed alive too. The Process line must reflect the passed
    # liveness state (dead/unknown), never invent "alive".
    import os
    import tempfile

    tmp = tempfile.mkdtemp()
    poll.METRICSMD = os.path.join(tmp, "metrics.md")
    poll.write_metrics(
        poll.cstnow(),
        [],
        "ALERT (TRAINER DEAD)",
        "do not relaunch",
        0,
        None,
        0,
        0,
        "?",
        trainer_alive=False,
    )
    text = open(poll.METRICSMD).read()
    assert "ALERT (TRAINER DEAD)" in text
    assert "trainer alive" not in text
    assert "Process: trainer DEAD" in text
    # POLL-FAIL path: no liveness evidence at all -> unknown, not alive
    poll.write_metrics(
        poll.cstnow(),
        [],
        "POLL-FAIL",
        "exec error",
        0,
        None,
        0,
        0,
        "?",
    )
    text = open(poll.METRICSMD).read()
    assert "trainer alive" not in text
    assert "Process: trainer unknown" in text


def test_parse_rows_merges_lines_of_same_step_and_splits_steps() -> None:
    text = full_step(1) + full_step(2)
    rows = poll.parse_rows(text)
    assert [r["step"] for r in rows] == [1, 2]
    assert rows[0]["task"].startswith("quantum_")
    assert rows[1]["gen_tok"] == 1668


def test_skip_vs_noop_predicate() -> None:
    """Skipped (repair-routed flat) steps are NOT no-op updates and do NOT
    break the consecutive no-op run; a genuine no-op (ratio ~1, tiny post-KL,
    loss > -0.005, tiny grad) counts; a healthy step breaks the run."""
    rows = [
        {
            "step": 1,
            "pass_rate": 0.0,
            "shaped": 0.0,
            "skipped": True,  # repair skip: not a no-op
            "ratio_mean": 1.0000,
            "seq_kl_after": 0.0,
            "loss": 0.0,
            "grad": 0.0,
        },
        {
            "step": 2,
            "pass_rate": 0.0,
            "shaped": 0.0,
            "skipped": False,
            "ratio_mean": 1.0005,
            "seq_kl_after": 1e-5,
            "loss": -0.001,
            "grad": 0.02,
        },
        {
            "step": 3,
            "pass_rate": 0.0,
            "shaped": 0.0,
            "skipped": False,
            "ratio_mean": 1.0004,
            "seq_kl_after": 1e-5,
            "loss": -0.0012,
            "grad": 0.03,
        },
    ]
    assert poll.count_noop(rows) == 2  # skips interleaved, still a no-op tail
    assert poll.count_dead_signal(rows) == 3  # flat all-fail tail (incl. skip)

    healthy_tail = rows + [
        {
            "step": 4,
            "pass_rate": 0.5,
            "shaped": 0.6,
            "skipped": False,
            "ratio_mean": 1.05,
            "seq_kl_after": 1e-3,
            "loss": -0.02,
            "grad": 0.2,
        }
    ]
    assert poll.count_noop(healthy_tail) == 0  # healthy step breaks the run
    assert poll.count_dead_signal(healthy_tail) == 0


def test_dead_signal_predicate_counts_flat_all_fail_tail() -> None:
    rows = [
        {"step": 1, "pass_rate": 0.25, "shaped": 0.4, "skipped": False},
        {"step": 2, "pass_rate": 0.0, "shaped": 0.0, "skipped": True},
        {"step": 3, "pass_rate": 0.0, "shaped": 0.0, "skipped": False},
        {"step": 4, "pass_rate": 0.0, "shaped": 0.0, "skipped": True},
    ]
    assert poll.count_dead_signal(rows) == 3  # steps 2-4 tail (step 1 had signal)
