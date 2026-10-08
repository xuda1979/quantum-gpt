"""C-0066: ASI3 LoRA-v2 train fire-on-ready watcher (training sibling of C-0051).

Covers the acceptance contract:
  1. ready=true AND exec round-trip OK -> fires the C-0039-preflighted relaunch
     EXACTLY ONCE, under a DEDICATED lock harness/state/locks/asi3-train.lock
     taken via harness_lib.acquire_lock (never the asi2-eval.lock).
  2. ready=false OR exec-dead -> NO fire, plus a named probe record in
     harness/state/probes/ (fail-closed, no retry storm).
  3. Idempotent across worker restarts: pid+cutoff state file, no duplicate
     fire, explicitly re-armable.
  4. Post-fire liveness = eval_results.jsonl step field advancing (B-222).
  5. Stale-code check = pid lstart vs file mtimes (B-223).
All probes are injected; no test touches the network.
"""

import json
import os
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))

import asi3_train_fire_on_ready as w  # noqa: E402


def fresh_env(tmp_path):
    """Isolated state/lock/probe paths so tests never touch live harness state."""
    state = tmp_path / "asi3_train_fire_state.json"
    lock = tmp_path / "asi3-train.lock"
    probes = tmp_path / "probes"
    probes.mkdir()
    return state, lock, probes


def ok_probes():
    return dict(ready=True, exec_ok=True)


def dead_probes(ready=False, exec_ok=False):
    return dict(ready=ready, exec_ok=exec_ok)


class Dispatcher:
    def __init__(self, lock_path=None):
        self.calls = []
        self.lock_seen_during_dispatch = None
        self.lock_path = lock_path

    def __call__(self, command):
        if self.lock_path is not None:
            self.lock_seen_during_dispatch = Path(self.lock_path).exists()
        self.calls.append(command)
        return dict(rc=0, stdout="launched", stderr="")


# --------------------------------------------------------------------------
# 1. fire path: exactly once, dedicated lock via harness_lib.acquire_lock
# --------------------------------------------------------------------------


def test_fire_once_on_ready_and_exec_ok(tmp_path):
    state, lock, probes = fresh_env(tmp_path)
    d = Dispatcher(lock_path=lock)
    st = w.load_or_init_state(str(state), pid=os.getpid(), cutoff_iso="2026-09-17T00:00:00Z")
    verdict, info = w.maybe_fire(
        state=st,
        state_path=str(state),
        lock_path=str(lock),
        probes_dir=str(probes),
        dispatch=d,
        **ok_probes(),
    )
    assert verdict == "FIRED"
    assert len(d.calls) == 1
    # fire command targets the C-0039-preflighted ASI3 launcher
    assert "qg_launch_lora_sft_fencefree_v2.sh" in d.calls[0]
    # the dedicated lock was HELD during dispatch (acquired, not stolen)
    assert d.lock_seen_during_dispatch is True
    assert info["lock_token"] is not None


def test_no_duplicate_fire_across_restart(tmp_path):
    state, lock, probes = fresh_env(tmp_path)
    d = Dispatcher()
    st = w.load_or_init_state(str(state), pid=os.getpid(), cutoff_iso="2026-09-17T00:00:00Z")
    w.maybe_fire(
        state=st,
        state_path=str(state),
        lock_path=str(lock),
        probes_dir=str(probes),
        dispatch=d,
        **ok_probes(),
    )
    # simulate a worker restart: fresh state loaded from disk under a NEW pid
    st2 = w.load_or_init_state(str(state), pid=os.getpid() + 1, cutoff_iso="2026-09-17T01:00:00Z")
    verdict, _ = w.maybe_fire(
        state=st2,
        state_path=str(state),
        lock_path=str(lock),
        probes_dir=str(probes),
        dispatch=d,
        **ok_probes(),
    )
    assert verdict == "ALREADY_FIRED"
    assert len(d.calls) == 1  # still exactly one dispatch ever


def test_rearm_allows_exactly_one_new_fire(tmp_path):
    state, lock, probes = fresh_env(tmp_path)
    d = Dispatcher()
    st = w.load_or_init_state(str(state), pid=os.getpid(), cutoff_iso="2026-09-17T00:00:00Z")
    w.maybe_fire(
        state=st,
        state_path=str(state),
        lock_path=str(lock),
        probes_dir=str(probes),
        dispatch=d,
        **ok_probes(),
    )
    st = w.rearm(str(state), pid=os.getpid())
    verdict, _ = w.maybe_fire(
        state=st,
        state_path=str(state),
        lock_path=str(lock),
        probes_dir=str(probes),
        dispatch=d,
        **ok_probes(),
    )
    assert verdict == "FIRED"
    assert len(d.calls) == 2  # one per armed window, never two per window


def test_lock_refused_means_no_fire(tmp_path):
    state, lock, probes = fresh_env(tmp_path)
    # a fresh lease held by a LIVE pid -> acquire_lock must refuse
    with open(lock, "w") as f:
        json.dump(dict(pid=os.getpid(), ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())), f)
    d = Dispatcher()
    st = w.load_or_init_state(str(state), pid=os.getpid(), cutoff_iso="2026-09-17T00:00:00Z")
    verdict, info = w.maybe_fire(
        state=st,
        state_path=str(state),
        lock_path=str(lock),
        probes_dir=str(probes),
        dispatch=d,
        **ok_probes(),
    )
    assert verdict == "LOCK_REFUSED"
    assert len(d.calls) == 0


def test_dedicated_lock_is_not_the_eval_lock():
    # C-0051 coordinates via asi2-eval.lock; C-0066 must use its OWN lock
    assert w.LOCK_PATH.name == "asi3-train.lock"
    assert w.LOCK_PATH.name != "asi2-eval.lock"


# --------------------------------------------------------------------------
# 2. fail-closed: ready=false or exec-dead -> no fire + named probe record
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "probes,reason",
    [
        (dead_probes(ready=False, exec_ok=False), "not_ready"),
        (dead_probes(ready=True, exec_ok=False), "exec_dead"),
    ],
)
def test_nofire_writes_named_probe_record(tmp_path, probes, reason):
    state, lock, probes_dir = fresh_env(tmp_path)
    d = Dispatcher()
    st = w.load_or_init_state(str(state), pid=os.getpid(), cutoff_iso="2026-09-17T00:00:00Z")
    verdict, _ = w.maybe_fire(
        state=st,
        state_path=str(state),
        lock_path=str(lock),
        probes_dir=str(probes_dir),
        dispatch=d,
        **probes,
    )
    assert verdict == "NOFIRE"
    assert len(d.calls) == 0
    records = list(probes_dir.glob("*.json"))
    assert len(records) == 1, "fail-closed NOFIRE must leave exactly one named probe record"
    rec = json.loads(records[0].read_text())
    assert rec["card"] == "C-0066"
    assert rec["reason"] == reason
    assert rec["fired"] is False


def test_nofire_no_retry_storm(tmp_path):
    state, lock, probes_dir = fresh_env(tmp_path)
    d = Dispatcher()
    st = w.load_or_init_state(str(state), pid=os.getpid(), cutoff_iso="2026-09-17T00:00:00Z")
    for _ in range(5):
        w.maybe_fire(
            state=st,
            state_path=str(state),
            lock_path=str(lock),
            probes_dir=str(probes_dir),
            dispatch=d,
            **dead_probes(),
        )
    assert len(d.calls) == 0
    assert (
        len(list(probes_dir.glob("*.json"))) == 1
    ), "repeated NOFIRE polls must update the SAME record, not spam probes/"


# --------------------------------------------------------------------------
# 3. post-fire liveness: eval_results.jsonl step field advancing (B-222)
# --------------------------------------------------------------------------


def test_liveness_is_eval_results_step_not_stdout(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    assert w.eval_step(str(run_dir)) is None  # no file -> unmeasured, not 0
    with open(run_dir / "eval_results.jsonl", "w") as f:
        f.write(json.dumps({"step": 3, "reward": 0.5}) + "\n")
        f.write(json.dumps({"step": 7, "reward": 0.6}) + "\n")
    assert w.eval_step(str(run_dir)) == 7
    assert w.liveness_advancing(str(run_dir), prev_step=3) is True
    assert w.liveness_advancing(str(run_dir), prev_step=7) is False


# --------------------------------------------------------------------------
# 4. stale-code check: pid lstart vs file mtimes (B-223)
# --------------------------------------------------------------------------


def test_stale_code_record_lstart_vs_mtimes():
    lstart_epoch = 1_000_000
    fresh = {
        "training/qwen_sft_peft.py": lstart_epoch - 100,
        "configs/sft/qwen38_fencefree_v2_lora.json": lstart_epoch - 1,
    }
    rec = w.stale_code_record(lstart_epoch, fresh)
    assert rec["stale"] is False
    drifted = dict(fresh)
    drifted["training/qwen_sft_peft.py"] = lstart_epoch + 500  # edited after start
    rec2 = w.stale_code_record(lstart_epoch, drifted)
    assert rec2["stale"] is True
    assert "training/qwen_sft_peft.py" in rec2["newer_than_process"]


# --------------------------------------------------------------------------
# 5. state file contract: pid + cutoff
# --------------------------------------------------------------------------


def test_state_file_has_pid_and_cutoff(tmp_path):
    state, lock, probes = fresh_env(tmp_path)
    w.load_or_init_state(str(state), pid=4242, cutoff_iso="2026-09-17T00:00:00Z")
    on_disk = json.loads(Path(state).read_text())
    assert on_disk["pid"] == 4242
    assert on_disk["cutoff"] == "2026-09-17T00:00:00Z"
    assert on_disk["fired"] is False
