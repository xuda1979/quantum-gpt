"""C-9122: grader-runtime preflight -- fail-closed qiskit check in the EXACT
interpreter the self-eval grader exec_modules task tests in.

RED first 2026-09-18: no harness/grader_runtime_preflight.py existed.
Root cause (C-9122): run sapo-27b-ai-sapo-27b-ai-20260915T1010 died ERR99999
at 2026-09-16T08:36:44Z -- ModuleNotFoundError: No module named 'qiskit'
(from qiskit.quantum_info import Statevector) raised via spec.loader
.exec_module in the self-eval grader path. The trainer spawns the grader
subprocess with sys.executable
(training/grpo_trainer.py::_run_harness_subprocess ->
evals/runner/single_candidate_eval.py, which exec_module()s the task
tests.py), so whichever python3 resolves at launcher start time IS the
grader runtime -- and nothing verified it, so any C-9058-gated relaunch
re-crashes the same way. Contract under test:
  - the probe runs the EXACT failing import (from qiskit.quantum_info
    import Statevector) in the EXACT interpreter passed in -- argv[0] IS
    that interpreter, never a bare "python3" by hope;
  - success is claimed ONLY on rc==0 AND a machine-checkable marker line
    naming qiskit's version (a bare rc==0 with no marker fails closed);
  - require_grader_runtime() raises GraderRuntimeError naming the
    interpreter and the missing import on EVERY not-ok outcome
    (rc!=0, marker missing, interpreter unspawnable);
  - all I/O injected via runner(argv)->(rc, stdout, stderr); the suite
    never spawns a real interpreter (quantum SDKs are absent from every
    Mac test interpreter).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import grader_runtime_preflight as G  # noqa: E402
import pytest  # noqa: E402

INTERP = "/usr/local/python3.11.14/bin/python3"


def _ok_runner(qiskit_version="2.4.1"):
    def runner(argv):
        line = json.dumps({"marker": G.MARKER, "qiskit": qiskit_version, "python": "3.11.14"})
        return 0, line + "\n", ""

    return runner


def _missing_runner():
    def runner(argv):
        return 1, "", "Traceback ... ModuleNotFoundError: No module named 'qiskit'"

    return runner


def test_probe_targets_exact_interpreter_and_exact_import():
    """argv[0] IS the named interpreter; the snippet IS the failing import."""
    argv = G.probe_command(INTERP)
    assert argv[0] == INTERP, "probe must run the EXACT interpreter, not PATH python3"
    assert argv[1] == "-c"
    assert G.GRADER_IMPORT == "from qiskit.quantum_info import Statevector"
    assert G.GRADER_IMPORT in argv[2]
    # probe_runtime passes the same argv verbatim to the runner
    seen = {}

    def runner(argv):
        seen["argv"] = argv
        return 0, json.dumps({"marker": G.MARKER, "qiskit": "2.4.1"}), ""

    G.probe_runtime(INTERP, runner=runner)
    assert seen["argv"] == argv


def test_require_fails_closed_on_module_not_found():
    """The C-9122 crash signature -> GraderRuntimeError BEFORE any launch."""
    doc = G.probe_runtime(INTERP, runner=_missing_runner())
    assert doc["ok"] is False
    assert doc["reason"] == "qiskit_import_failed"
    assert doc["rc"] == 1
    assert "qiskit" in doc["stderr_tail"]
    with pytest.raises(G.GraderRuntimeError) as ei:
        G.require_grader_runtime(INTERP, runner=_missing_runner())
    msg = str(ei.value)
    assert INTERP in msg, "error must name the exact interpreter"
    assert G.GRADER_IMPORT in msg, "error must name the exact failing import"


def test_require_passes_when_import_resolves():
    doc = G.require_grader_runtime(INTERP, runner=_ok_runner())
    assert doc["ok"] is True
    assert doc["interp"] == INTERP
    assert doc["qiskit_version"] == "2.4.1"
    assert doc["artifact"] == "grader_runtime_probe"


def test_fail_closed_on_rc0_without_marker():
    """A bare rc==0 proves nothing -- the marker must be present."""
    doc = G.probe_runtime(INTERP, runner=lambda argv: (0, "hello", ""))
    assert doc["ok"] is False
    assert doc["reason"] == "marker_missing_on_rc0"
    with pytest.raises(G.GraderRuntimeError):
        G.require_grader_runtime(INTERP, runner=lambda argv: (0, "hello", ""))


def test_fail_closed_when_interpreter_unspawnable():
    def boom(argv):
        raise FileNotFoundError(2, "No such file or directory", INTERP)

    doc = G.probe_runtime(INTERP, runner=boom)
    assert doc["ok"] is False
    assert doc["reason"] == "interpreter_spawn_failed"
    with pytest.raises(G.GraderRuntimeError):
        G.require_grader_runtime(INTERP, runner=boom)


# ---------------------------------------------------------------------------
# Launcher wiring (C-9122 fixer leg, 2026-09-18): the probe is worthless
# unless the relaunch launchers actually run it fail-closed BEFORE exec-ing
# the trainer. The ASI3 entrypoint (scripts/asi3_launch_grpo_direct.sh -- the
# launcher that produced crashed run sapo-27b-ai-*) delegates by default to
# scripts/asi2_launch_grpo_27b_selfeval.sh, so gating THAT file gates the
# ASI3 relaunch path; these tests pin the whole chain.

REPO = Path(__file__).resolve().parents[2]
ASI2_LAUNCHER = REPO / "scripts" / "asi2_launch_grpo_27b_selfeval.sh"
ASI3_LAUNCHER = REPO / "scripts" / "asi3_launch_grpo_direct.sh"


def test_asi2_relaunch_launcher_probes_failclosed_before_trainer_exec():
    text = ASI2_LAUNCHER.read_text(encoding="utf-8")
    hook_idx = text.find("harness/grader_runtime_preflight.py")
    assert hook_idx != -1, "relaunch launcher must run the C-9122 grader-runtime probe"
    assert "--interpreter" in text, "probe must name the EXACT trainer interpreter"
    assert '"$TRAINER_PY"' in text, "trainer interpreter must be named, not bare python3"
    # fail-closed: probe failure refuses to launch (non-zero exit), not advisory
    refusal_idx = text.find("C-9122 FAIL-CLOSED", hook_idx)
    assert refusal_idx != -1, "probe failure must log a C-9122 FAIL-CLOSED refusal"
    exit_idx = text.find("exit 3", refusal_idx)
    assert exit_idx != -1 and exit_idx - refusal_idx < 400, "refusal must exit non-zero"
    # the balanced-layers trainer exec runs under the PROBED interpreter
    # (grader subprocess inherits the trainer's sys.executable)
    exec_idx = text.find('"$TRAINER_PY" training/grpo_trainer.py')
    assert exec_idx != -1, "trainer must exec under the probed interpreter"
    assert exec_idx > hook_idx, "no trainer exec may precede the probe"
    torchrun_idx = text.find("torchrun --nproc_per_node=")
    assert torchrun_idx == -1 or torchrun_idx > hook_idx, (
        "torchrun branch must also follow the probe"
    )


def test_asi3_entrypoint_delegates_to_the_gated_launcher():
    text = ASI3_LAUNCHER.read_text(encoding="utf-8")
    assert "ASI3_SAPO_LAUNCHER:-$ROOT_DIR/scripts/asi2_launch_grpo_27b_selfeval.sh" in text, (
        "ASI3 relaunch entrypoint (owner of crashed run sapo-27b-ai-*) must "
        "default to the C-9122-gated launcher"
    )
