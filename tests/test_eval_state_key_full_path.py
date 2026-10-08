"""TDD: the eval loop's state entries must be keyed by the checkpoint's FULL
PATH, so the parallel-eval agent's done-filter can actually see them.

Defect (measured live 2026-09-11): the two scripts disagreed on the state key.
  * `scripts/asi2_loop_eval.sh` keyed its state entry by the BARE STEP NUMBER
    (`:326` `TS="$(basename "$SAPO_ADAPTER" | sed -E 's/step_0*([0-9]+)_adapter/\\1/')"`,
    then `update_state "$TS" ...`), with the adapter path sitting in the entry's
    `adapter` field. Verified in the live `reports/.sapo_parallel_eval_state_ASI3.json`:
    keys `'1' '15' '47' '64' '74' '79' '85'`, each with a full `adapter` path.
  * `scripts/sapo_parallel_eval_agent.sh` keys its done-filter by the FULL
    CHECKPOINT PATH (`:113` `KEY="$CK"` — the B-105 fix: a bare step number is
    identical across runs, so the same-named checkpoint of a different run was
    silently suppressed).

Consequence (the live symptom): the agent's `st.get(ck)` lookup NEVER matched a
leg verdict, so every scan re-fired an already-evaluated checkpoint — the endless
`step_000024_adapter` re-eval loop recorded in `.sapo-loop/STATUS.md`.

Which side moves: the EVAL LOOP. The full path is the correct identity — it is
the only key that distinguishes two runs' same-named checkpoints (the whole point
of B-105) and the eval loop ALREADY records that identity in the entry's `adapter`
field. Making the agent re-derive a key from `adapter` would move the ambiguity
back into the consumer instead of removing it. Keying is the writer's contract.

Fail-closed guarantee (the constraint that matters more than the waste): an
unmatched key must NEVER read as "done". A key that misses the lookup stays
PENDING and the leg re-fires. Re-evaluating a finished checkpoint costs one leg
(~1.4h); suppressing an unevaluated one is a silent coverage gap, so every
failure direction of this fix must resolve to EVALUATE.

Contract:
  E1  `checkpoint_identity` returns the checkpoint's full path — the same key the
      agent computes from its own listing — and never folds a path back to a
      bare step number.
  E2  Every state WRITE is handed that identity: `checkpoint_identity "$ADAPTER"`
      is the single definition, and no write is keyed by the leg's short name.
  E3  The loop does NOT read a verdict out of a legacy bare-step key (`'4'`)
      written by an older tree: a checkpoint with no entry under its own
      identity must still be evaluated.
  E4  Non-vacuity: a terminal verdict recorded under the checkpoint's own
      identity is recognised as a verdict, so the fix is not "always re-run".
  E5  Fail-closed on an unreadable state file: a corrupt state file is not a
      verdict — the checkpoint is still evaluated.
  E6  Agent side: an UNRECOGNISED key does not suppress; the checkpoint is fired.
  E7  Agent side, end to end: the key the WRITER produces is the key the AGENT's
      done-filter matches (this is the integration the defect broke).

Every case runs against COPIES in `tmp_path` with a stubbed box transport, so no
box is touched, no leg runs for real, and the live
`reports/.sapo_parallel_eval_state_*.json` is never written or read.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
LOOP = REPO / "scripts" / "asi2_loop_eval.sh"
AGENT = REPO / "scripts" / "sapo_parallel_eval_agent.sh"

RUN_LIVE = "/root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260909T104517Z"
CK = "step_000004_adapter"
CK_PATH = f"{RUN_LIVE}/{CK}"
CK_PATH_MESSY = f"{RUN_LIVE}//{CK}"

# A real terminal verdict, exactly as the live state file carries them.
DONE_ENTRY = {"status": "done", "verdict": "adapter differs from base", "adapter": CK_PATH}


def _env(**over):
    """A minimal environment; NOTHING inherited that could steer a box script."""
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": os.environ.get("HOME", "/tmp"),
        "DAEMON_PORT": "1",  # unroutable: any real /exec attempt fails fast
        "REMOTE_ROOT": "/root/work/software/quantum-gpt",
        "SAPO_EVAL_LIB_ONLY": "1",  # source the helpers, run no main flow
    }
    env.update(over)
    return env


# --------------------------------------------------------------------------
# E1/E2 — the identity the loop keys by
# --------------------------------------------------------------------------
@pytest.mark.skipif(not LOOP.exists(), reason="eval loop not present")
def test_E1_identity_is_the_full_checkpoint_path(tmp_path):
    """One identity for a checkpoint, in every spelling it arrives in.

    `checkpoint_identity` must return the full path — the SAME string the agent
    computes from its own listing (`CK`) — not a bare step number,
    which is identical across runs.
    """
    for arg in (CK_PATH, f"{CK_PATH}/", CK_PATH_MESSY):
        p = subprocess.run(
            [
                "env",
                "-i",
                *[f"{k}={v}" for k, v in _env().items()],
                "bash",
                "-c",
                f'source "{LOOP}"; checkpoint_identity "{arg}"',
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert p.stdout.strip() == CK_PATH, (
            f"checkpoint_identity({arg!r}) returned {p.stdout.strip()!r}; the identity must be the full "
            f"checkpoint path {CK_PATH!r} (the key the agent's done-filter looks up)"
        )
    # bare-basename fallback: no path was given, so the basename IS the identity
    p = subprocess.run(
        [
            "env",
            "-i",
            *[f"{k}={v}" for k, v in _env().items()],
            "bash",
            "-c",
            f'source "{LOOP}"; checkpoint_identity "{CK}"',
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert (
        p.stdout.strip() == CK
    ), f"a bare basename (no path to disambiguate) must still pass through: {p.stdout.strip()!r}"
    # degenerate inputs must not crash the identity (a crash here would take the
    # whole leg down, i.e. a checkpoint that is never evaluated at all)
    for arg in ("/", ""):
        p = subprocess.run(
            [
                "env",
                "-i",
                *[f"{k}={v}" for k, v in _env().items()],
                "bash",
                "-c",
                f'source "{LOOP}"; checkpoint_identity "{arg}"',
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert (
            p.returncode == 0
        ), f"checkpoint_identity({arg!r}) exited {p.returncode}: {p.stderr[-300:]}"


def _source(expr: str, **over):
    """Source the real loop (helpers only) and evaluate `expr` in its shell."""
    p = subprocess.run(
        [
            "env",
            "-i",
            *[f"{k}={v}" for k, v in _env(**over).items()],
            "bash",
            "-c",
            f'source "{LOOP}"; {expr}',
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return p.stdout, p.stderr


@pytest.mark.skipif(not LOOP.exists(), reason="eval loop not present")
def test_E2_identity_key_is_the_path_from_the_adapter_actually_evaluated(tmp_path):
    """The key used for every state WRITE is derived from the checkpoint path
    this leg evaluates — not from the leg's short name.

    Two halves, because the write itself needs a completed leg on the box:
      (a) the identity of the adapter the loop evaluates is the full path
          (driven through the real function, not a copy of its logic);
      (b) every state write in the loop is handed that identity — `$STATE_KEY`
          and never the short-name `$TS` (the defect), and `STATE_KEY` is
          defined from `checkpoint_identity "$ADAPTER"`.
    A reader (the parallel-eval agent) that keys by the full path then matches
    by construction, which is the contract this test pins.
    """
    out, _err = _source(f'checkpoint_identity "{CK_PATH}"')
    assert (
        out.strip() == CK_PATH
    ), f"the evaluated adapter's identity is not its full path: {out.strip()!r}"

    src = LOOP.read_text(encoding="utf-8")
    assert (
        'STATE_KEY="$(checkpoint_identity "$ADAPTER")"' in src
    ), "the state identity is not defined from the evaluated adapter's path"
    assert (
        "checkpoint_identity" in src.split("# ---------------- main flow")[0]
    ), "checkpoint_identity must be a helper, defined before the main flow"
    assert 'update_state "$TS"' not in src, (
        "a state write is still keyed by the bare step number — the agent's "
        "full-path done-filter can never match it (the live re-eval loop)"
    )
    writes = [
        ln.strip()
        for ln in src.splitlines()
        if "update_state " in ln and not ln.strip().startswith("#")
    ]
    assert writes, "no update_state call found — the detection below is vacuous"
    for ln in writes:
        assert 'update_state "$STATE_KEY"' in ln, (
            "a state write does not use the checkpoint identity:\n" + ln
        )


# --------------------------------------------------------------------------
# E3/E4/E5 — the loop's own done-filter, both directions
# --------------------------------------------------------------------------
@pytest.mark.skipif(not LOOP.exists(), reason="eval loop not present")
def test_E3_legacy_bare_step_key_is_not_a_verdict(tmp_path):
    """A verdict under the OLD bare-step key (`'4'`) is not evidence about this
    checkpoint. Fail-closed: the unmatched key re-evaluates."""
    state = tmp_path / "state.json"
    state.write_text(
        json.dumps({"4": {"status": "done", "verdict": "stale legacy key"}}), encoding="utf-8"
    )
    out, _err = _source(
        f'STATE_KEY="$(checkpoint_identity "{CK_PATH}")"; state_get "$STATE_KEY"',
        EVAL_STATE_FILE=str(state),
    )
    assert (
        "ALREADY_EVALUATED" not in out and out.strip() == ""
    ), f"a bare-step key was read as this checkpoint's verdict: {out!r}"


@pytest.mark.skipif(not LOOP.exists(), reason="eval loop not present")
def test_E4_full_path_key_is_recognised_as_a_verdict(tmp_path):
    """Non-vacuity: a terminal verdict under the checkpoint's OWN identity still
    short-circuits, so the fix is not "always re-run"."""
    state = tmp_path / "state.json"
    state.write_text(json.dumps({CK_PATH: DONE_ENTRY}), encoding="utf-8")
    out, err = _source(
        f'STATE_KEY="$(checkpoint_identity "{CK_PATH}")"; '
        'ST="$(state_get "$STATE_KEY")"; '
        'if [[ "$ST" == "done" || "$ST" == "inert" ]]; then say "ALREADY_EVALUATED $STATE_KEY"; fi',
        EVAL_STATE_FILE=str(state),
    )
    assert "ALREADY_EVALUATED" in out and CK_PATH in out, (
        "the checkpoint's own full-path verdict was not recognised — the leg "
        "would re-run a completed checkpoint:\n" + out + err
    )


@pytest.mark.skipif(not LOOP.exists(), reason="eval loop not present")
def test_E5_unreadable_state_is_not_a_verdict(tmp_path):
    """Fail-closed: a corrupt state file is not evidence of a completed eval."""
    state = tmp_path / "state.json"
    state.write_text("{not json at all", encoding="utf-8")
    out, _err = _source(
        f'STATE_KEY="$(checkpoint_identity "{CK_PATH}")"; state_get "$STATE_KEY"',
        EVAL_STATE_FILE=str(state),
    )
    assert (
        "ALREADY_EVALUATED" not in out and out.strip() == ""
    ), f"a corrupt state file was read as a verdict: {out!r}"


# --------------------------------------------------------------------------
# E6/E7 — the agent side (stubbed leg + stubbed box transport)
# --------------------------------------------------------------------------
STUB_EXEC = """\
import json, sys
cmd = " ".join(sys.argv[1:])
if "step_*_adapter" in cmd:
    out = "%s/%s"
elif "adapter_config.json" in cmd:
    out = "COMPLETE"
elif "test -d" in cmd:
    out = ""
else:
    out = ""
print(json.dumps({"ok": True, "commandOk": True, "commandStatus": 0, "output": out}))
"""

# Stub leg: records the state file + pin it was handed, lands NO verdict.
STUB_LEG = """\
#!/usr/bin/env bash
printf '%%s\\n' "${EVAL_STATE_FILE:-<unset>} ${SAPO_RUN_ADAPTER:-<unset>}" >> "%s"
exit 0
"""


def _sandbox(tmp_path: Path, state: dict):
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    script = repo / "scripts" / AGENT.name
    shutil.copy(AGENT, script)
    (repo / "scripts" / "asi3_exec.py").write_text(STUB_EXEC % (RUN_LIVE, CK), encoding="utf-8")
    calls = tmp_path / "leg-calls.txt"
    (repo / "scripts" / "asi2_loop_eval.sh").write_text(STUB_LEG % calls, encoding="utf-8")
    state_file = repo / "reports" / ".sapo_parallel_eval_state_ASI3.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state), encoding="utf-8")
    logs = tmp_path / "eval-logs"
    logs.mkdir()
    return script, state_file, logs, calls


def _run_agent(tmp_path, state, seconds=8):
    script, state_file, logs, calls = _sandbox(tmp_path, state)
    env = dict(os.environ)
    env["SAPO_EVAL_LOG_DIR"] = str(logs)
    env["PATH"] = str(Path(os.sys.executable).parent) + os.pathsep + env.get("PATH", "")
    p = subprocess.Popen(
        ["bash", str(script), "ASI3", "20653", RUN_LIVE, "60"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        start_new_session=True,
    )
    try:
        out = p.communicate(timeout=seconds)[0]
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            out = p.communicate(timeout=20)[0]
        except subprocess.TimeoutExpired:
            out = ""
        out += "\n<TIMEOUT>"
    return out, state_file, calls


@pytest.mark.skipif(not AGENT.exists(), reason="agent not present")
def test_E6_unrecognised_key_still_evaluates(tmp_path):
    """FAIL-CLOSED: a state entry the agent cannot match to this checkpoint must
    leave it PENDING. Suppressing on an unmatched key is a silent coverage gap —
    worse than re-evaluating."""
    out, _state, calls = _run_agent(
        tmp_path, {"4": {"status": "done", "verdict": "legacy bare-step key"}}
    )
    assert f"NEW checkpoint {CK}" in out, (
        "an unmatched key suppressed the checkpoint (silent skip of real eval "
        "work):\n" + out[-1500:]
    )
    assert calls.exists() and calls.read_text(encoding="utf-8").strip(), (
        "no leg was fired for the unmatched key:\n" + out[-1500:]
    )


@pytest.mark.skipif(not AGENT.exists(), reason="agent not present")
def test_E7_end_to_end_the_writer_key_is_what_the_agent_matches(tmp_path):
    """The integration the defect broke: the key the EVAL LOOP writes must be
    the key the AGENT's done-filter matches.

    The entry here is written under `checkpoint_identity`'s answer (E1 pins that
    function to the full path), matching the shape the loop now produces.
    """
    out, _state, calls = _run_agent(tmp_path, {CK_PATH: DONE_ENTRY})
    assert f"NEW checkpoint {CK}" not in out, (
        "the checkpoint's own full-path verdict was ignored — the agent "
        "re-fires an already-evaluated leg:\n" + out[-1500:]
    )
    assert not calls.exists() or not calls.read_text(encoding="utf-8").strip(), (
        "a leg was fired despite the checkpoint's own terminal verdict:\n"
        + (calls.read_text(encoding="utf-8") if calls.exists() else "")
    )
