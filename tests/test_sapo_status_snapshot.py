"""TDD: the status snapshot tool must expose the fields the manager displays.

The user demanded the training process be DISPLAYED in the chat, not hidden:
every loss value, the reduction, all rollout rewards, drift, and the
zero-change alarm must be visible in the snapshot. These tests lock that.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.sapo_status_snapshot import newest_run_dir, newest_train_log, snapshot


def _write_records(run_dir: Path, records: list[dict]) -> None:
    with open(run_dir / "grpo_step_metrics.jsonl", "w") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")


def test_snapshot_exposes_losses_rewards_reduction_and_alarm(tmp_path: Path) -> None:
    run = tmp_path / "sapo-27b-ai-20260825T000000"
    run.mkdir()
    _write_records(
        run,
        [
            {
                "step": 1,
                "timestamp_utc": "2026-08-25T00:10:00+00:00",
                "loss": -0.01,
                "loss_breakdown": {"loss_recomputed": -0.01000001},
                "mean_reward": 0.25,
                "pass_rate": 0.5,
                "rollout_rewards": [
                    {"pass": True, "total_reward": 1.0},
                    {"pass": False, "total_reward": 0.4},
                ],
                "per_candidate_losses": [{"loss_i": -0.02, "n_tokens": 100}],
                "loss_reduction": "per-candidate token-mean, w=1/G",
                "lora_b_max_delta": 1e-4,
                "zero_change_alarm": False,
                "skipped": False,
                "reason": None,
            },
            {
                "step": 2,
                "timestamp_utc": "2026-08-25T00:25:00+00:00",
                "loss": None,
                "mean_reward": 0.0,
                "pass_rate": 0.0,
                "rollout_rewards": [{"pass": False, "total_reward": 0.0}],
                "per_candidate_losses": [{"loss_i": None, "n_tokens": 0}],
                "loss_reduction": "per-candidate token-mean, w=1/G [skipped: no loss computed this step]",
                "lora_b_max_delta": 1e-4,
                "zero_change_alarm": True,
                "skipped": True,
                "reason": "repair_sft_queued",
            },
        ],
    )
    (run / "step_000002_adapter").mkdir()
    (run / "step_000002_adapter" / "adapter_config.json").write_text("{}")

    snap = snapshot(run, tmp_path, steps=3)
    assert snap["newest_checkpoint"] == "step_000002_adapter"
    assert snap["zero_change_alarm"] is True
    assert len(snap["steps"]) == 2
    s1, s2 = snap["steps"]
    # every loss value
    assert s1["loss"] == -0.01 and s1["loss_recomputed"] == -0.01000001
    # the reduction
    assert "per-candidate token-mean" in s1["loss_reduction"]
    assert "skipped" in s2["loss_reduction"]
    # all rollout rewards
    assert [r["pass"] for r in s1["rollout_rewards"]] == [True, False]
    # alarm propagates
    assert s2["zero_change_alarm"] is True


def test_snapshot_empty_run_dir(tmp_path: Path) -> None:
    snap = snapshot(None, tmp_path)
    assert snap["trainer_alive"] is False
    assert snap["steps"] == []


# ---------------------------------------------------------------------------
# (b) run/log discovery must match the DEPLOYED ASI2 naming (the watchdog
# relaunch path writes outputs/grpo-27b-selfeval-<ts> and
# logs/grpo_27b_selfeval/grpo_train_<ts>.log, NOT the legacy sapo-27b-ai-*
# / sapo_27b_ai names). A display tool that globs the wrong family silently
# shows "run: none" while the ASI2 trainer is live — the exact silent-stale
# class this tool must not have.
# ---------------------------------------------------------------------------


def test_newest_run_dir_finds_deployed_asi2_selfeval_naming(tmp_path: Path) -> None:
    outputs = tmp_path / "outputs"
    asi2_run = outputs / "grpo-27b-selfeval-20260825T090000"
    asi2_run.mkdir(parents=True)
    (asi2_run / "grpo_step_metrics.jsonl").write_text('{"step": 1, "loss": -0.1}\n')
    legacy_run = outputs / "sapo-27b-ai-20260824T000000"
    legacy_run.mkdir(parents=True)
    (legacy_run / "grpo_step_metrics.jsonl").write_text('{"step": 9}\n')
    assert newest_run_dir(tmp_path) == asi2_run


def test_newest_train_log_finds_deployed_asi2_logdir(tmp_path: Path) -> None:
    (tmp_path / "logs" / "grpo_27b_selfeval").mkdir(parents=True)
    deployed = tmp_path / "logs" / "grpo_27b_selfeval" / "grpo_train_20260825T090000.log"
    deployed.write_text('{"stage": "boot"}\n')
    (tmp_path / "logs" / "sapo_27b_ai").mkdir(parents=True)
    legacy = tmp_path / "logs" / "sapo_27b_ai" / "grpo_train_20260824T000000.log"
    legacy.write_text('{"stage": "boot"}\n')
    assert newest_train_log(tmp_path, None) == deployed


def test_newest_run_dir_returns_newest_even_without_metrics_file(tmp_path: Path) -> None:
    """A freshly-launched run (trainer still loading, no grpo_step_metrics.jsonl
    yet) must be the selected run. Filtering it out silently displays the
    PREVIOUS run as current — stale-run selection. The honest display shows
    the booting run with empty steps."""
    outputs = tmp_path / "outputs"
    old_run = outputs / "grpo-27b-selfeval-20260825T080000"
    old_run.mkdir(parents=True)
    (old_run / "grpo_step_metrics.jsonl").write_text('{"step": 42, "loss": 0.1}\n')
    booting_run = outputs / "grpo-27b-selfeval-20260825T090000"
    booting_run.mkdir(parents=True)  # newest, but NO metrics file yet
    assert newest_run_dir(tmp_path) == booting_run
    snap = snapshot(None, tmp_path)
    assert snap["run_dir"] == str(booting_run)
    assert snap["steps"] == []  # honest: no steps yet, not the old run's steps


# ---------------------------------------------------------------------------
# (c) torn/corrupt metrics line: a bad line must NEVER silently truncate the
# displayed tail (a mid-append torn write was the whole point of the drift
# watcher's per-line tolerance; the snapshot tool aborts the entire read).
# ---------------------------------------------------------------------------


def test_snapshot_tolerates_corrupt_metrics_line_in_middle(tmp_path: Path) -> None:
    run = tmp_path / "grpo-27b-selfeval-20260825T090000"
    run.mkdir()
    _write_records(
        run,
        [
            {"step": 1, "loss": -0.01},
            {"step": 2},  # stands in for the torn line — replaced below
            {"step": 3, "loss": -0.03},
        ],
    )
    # simulate a torn mid-append line between step 1 and step 3
    lines = (run / "grpo_step_metrics.jsonl").read_text().splitlines()
    lines[1] = '{"step": 2, "loss": -0.02'  # truncated JSON
    (run / "grpo_step_metrics.jsonl").write_text("\n".join(lines) + "\n")
    snap = snapshot(run, tmp_path, steps=3)
    # step 3 MUST still be displayed — a bad line must not hide later steps
    assert [s["step"] for s in snap["steps"]] == [1, 3]


# ---------------------------------------------------------------------------
# code-review wave (2026-08-26) findings
# ---------------------------------------------------------------------------


def test_snapshot_tolerates_stage_less_log(tmp_path: Path) -> None:
    """Finder A/F12: last_stage_line raised UnboundLocalError on a log with no
    stage line (booting run) — killing the whole snapshot display."""
    run = tmp_path / "grpo-27b-selfeval-20260826T000000"
    run.mkdir()
    (run / "grpo_step_metrics.jsonl").write_text('{"step": 1, "loss": -0.1}\n')
    (tmp_path / "logs" / "grpo_27b_selfeval").mkdir(parents=True)
    (tmp_path / "logs" / "grpo_27b_selfeval" / "grpo_train_20260826T000000.log").write_text(
        "plain boot line without stage markers\n", encoding="utf-8"
    )
    snap = snapshot(run, tmp_path)
    assert snap["train_log_tail_stage"] is None  # no crash, honest None


def test_zero_change_alarm_reflects_entire_history(tmp_path: Path) -> None:
    """Finder B/F13: the header alarm only scanned the displayed tail window —
    an alarm older than the window silently vanished from the header."""
    run = tmp_path / "grpo-27b-selfeval-20260826T000000"
    run.mkdir()
    _write_records(
        run,
        [
            {"step": 1, "zero_change_alarm": True, "loss": -0.1},
            {"step": 2, "zero_change_alarm": False, "loss": -0.2},
            {"step": 3, "zero_change_alarm": False, "loss": -0.3},
        ],
    )
    snap = snapshot(run, tmp_path, steps=2)  # tail window = steps 2-3
    assert snap["zero_change_alarm"] is True  # step 1's alarm still visible


def test_train_log_matched_to_run_dir(tmp_path: Path) -> None:
    """Finder B/F14: the train log was selected globally across naming
    families — an explicit run could show ANOTHER run's log tail stage."""
    (tmp_path / "logs" / "grpo_27b_selfeval").mkdir(parents=True)
    (tmp_path / "logs" / "grpo_27b_selfeval" / "grpo_train_20260826T010000.log").write_text(
        '{"stage": "step_begin"}\n', encoding="utf-8"
    )
    (tmp_path / "logs" / "sapo_27b_ai").mkdir(parents=True)
    (tmp_path / "logs" / "sapo_27b_ai" / "grpo_train_20260825T230000.log").write_text(
        '{"stage": "old_run"}\n', encoding="utf-8"
    )
    run = tmp_path / "grpo-27b-selfeval-20260826T010000"
    run.mkdir()
    (run / "grpo_step_metrics.jsonl").write_text('{"step": 1}\n')
    # the newest global log IS the matching one here; the important case:
    # an EXPLICIT older run must not inherit the newer run's log
    old_run = tmp_path / "grpo-27b-selfeval-20260825T230000"
    old_run.mkdir()
    (old_run / "grpo_step_metrics.jsonl").write_text('{"step": 9}\n')
    snap = snapshot(old_run, tmp_path)
    assert snap["train_log"] is not None
    assert "20260825T230000" in snap["train_log"]  # matched, not the 010000 log
    assert snap["train_log_tail_stage"] == '{"stage": "old_run"}'


def test_drift_verdict_matched_to_run_dir(tmp_path: Path) -> None:
    """F15 (code-review wave): the drift verdict came from the globally
    newest-mtime adapter_delta_*.json — a booting run displayed the previous
    run's verdict. The file matching the displayed run's ts must win."""
    run = tmp_path / "grpo-27b-selfeval-20260826T020000"
    run.mkdir()
    (run / "grpo_step_metrics.jsonl").write_text('{"step": 1}\n')
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    # a NEWER-mtime delta file from an OLDER run
    stale = outputs / "adapter_delta_20260825T230000.json"
    stale.write_text('{"verdict": "active", "max_abs_diff": 0.001}\n')
    import os as _os

    old_ts = 1_000_000_000
    _os.utime(stale, (old_ts, old_ts))
    # the DISPLAYED run's delta file (older mtime)
    mine = outputs / "adapter_delta_20260826T020000.json"
    mine.write_text('{"verdict": "inert", "max_abs_diff": 0.0}\n')
    _os.utime(mine, (old_ts - 10, old_ts - 10))
    snap = snapshot(run, tmp_path)
    assert snap["drift"] is not None
    assert snap["drift"]["file"] == "adapter_delta_20260826T020000.json"
    assert snap["drift"]["verdict"] == "inert"


# ---------------------------------------------------------------------------
# bug-hunter wave (2026-09-01): silent-swallow scan of snapshot()
# ---------------------------------------------------------------------------


def test_drift_watch_torn_line_does_not_wipe_display(tmp_path: Path) -> None:
    """The metrics tail already tolerates a torn mid-append line, but the
    drift.jsonl display read was ALL-OR-NOTHING: one torn line made the whole
    drift_watch block vanish from the display (the same lie class — the
    watcher's latest verdict silently disappears). Per-line tolerance +
    a skip counter must keep the last GOOD record visible."""
    run = tmp_path / "grpo-27b-selfeval-20260826T030000"
    run.mkdir()
    (run / "grpo_step_metrics.jsonl").write_text('{"step": 1}\n')
    (run / "drift.jsonl").write_text(
        '{"verdict": "active", "max_abs_diff": 0.001}\n'
        '{"verdict": "inert", "max_abs_diff": 0.0'  # torn mid-append tail
    )
    snap = snapshot(run, tmp_path)
    # the last GOOD record must survive the torn tail line
    assert snap["drift_watch"] is not None
    assert snap["drift_watch"]["verdict"] == "active"
    # and the skip must be VISIBLE (not silent)
    assert snap.get("drift_watch_lines_skipped") == 1


def test_drift_watch_corrupt_line_in_middle_keeps_later_records(tmp_path: Path) -> None:
    """Same per-line rule as the metrics read: a corrupt middle line must not
    hide LATER drift records."""
    run = tmp_path / "grpo-27b-selfeval-20260826T030000"
    run.mkdir()
    (run / "grpo_step_metrics.jsonl").write_text('{"step": 1}\n')
    (run / "drift.jsonl").write_text(
        '{"verdict": "active", "max_abs_diff": 0.001}\n'
        "{garbage\n"
        '{"verdict": "active2", "max_abs_diff": 0.0005}\n'
    )
    snap = snapshot(run, tmp_path)
    assert snap["drift_watch"] is not None
    assert snap["drift_watch"]["max_abs_diff"] == 0.0005
    assert snap.get("drift_watch_lines_skipped") == 1


def test_metrics_read_oserror_is_surfaced_not_silent(tmp_path: Path) -> None:
    """If the metrics file EXISTS but cannot be READ (e.g. permission /
    IO error), the snapshot must say so — an empty step list with no marker
    is the 'trainer alive, zero steps, reason hidden' lie."""
    run = tmp_path / "grpo-27b-selfeval-20260826T030000"
    run.mkdir()
    # a DIRECTORY named grpo_step_metrics.jsonl: exists() is True but
    # open() raises IsADirectoryError (an OSError) — previously swallowed
    blocker = run / "grpo_step_metrics.jsonl"
    blocker.mkdir()
    (blocker / "stub").write_text("")
    snap = snapshot(run, tmp_path)
    assert snap["steps"] == []
    assert snap.get("metrics_read_error")  # surfaced, not silent


def test_corrupt_drift_delta_file_is_surfaced_not_silent(tmp_path: Path) -> None:
    """A corrupt adapter_delta_<ts>.json silently dropped the drift verdict
    (display showed 'no drift' while the file was unreadable). The read
    failure must be surfaced as drift_read_error."""
    run = tmp_path / "grpo-27b-selfeval-20260826T030000"
    run.mkdir()
    (run / "grpo_step_metrics.jsonl").write_text('{"step": 1}\n')
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    (outputs / "adapter_delta_20260826T030000.json").write_text("{not json")
    snap = snapshot(run, tmp_path)
    assert snap.get("drift") is None  # still no verdict to display
    assert snap.get("drift_read_error")  # but the failure is VISIBLE


def test_render_text_shows_read_errors(tmp_path: Path) -> None:
    """The text display must surface the read-error markers (the JSON output
    carrying them is not enough — the chat display renders text)."""
    from scripts.sapo_status_snapshot import render_text

    run = tmp_path / "grpo-27b-selfeval-20260826T030000"
    run.mkdir()
    blocker = run / "grpo_step_metrics.jsonl"
    blocker.mkdir()
    (blocker / "stub").write_text("")
    snap = snapshot(run, tmp_path)
    text = render_text(snap)
    assert "metrics_read_error" in text or "unreadable" in text
