#!/usr/bin/env python3
"""C-9122: grader-runtime preflight -- qiskit must import in the EXACT
interpreter the self-eval grader exec_modules task tests in, fail-closed
BEFORE any gated relaunch.

Root cause (C-9122): run sapo-27b-ai-sapo-27b-ai-20260915T1010 died
ERR99999 at 2026-09-16T08:36:44Z with ModuleNotFoundError: No module named
'qiskit' (from qiskit.quantum_info import Statevector) raised via
spec.loader.exec_module in the self-eval grader path. The trainer spawns
the grader subprocess with sys.executable
(training/grpo_trainer.py::_run_harness_subprocess ->
evals/runner/single_candidate_eval.py, which exec_module()s the task
tests.py), so whichever python3 resolves at launcher start time IS the
grader runtime. The launcher (scripts/asi2_launch_grpo_27b_selfeval.sh
`python3 training/grpo_trainer.py`) never verified that dep, so the
C-9058-gated relaunch would re-crash the same way.

Fix shape: probe_runtime() runs the exact failing import in a NAMED
interpreter (never PATH "python3" by hope); require_grader_runtime()
raises GraderRuntimeError unless the probe proves the import resolves
THERE. The relaunch launcher calls this before exec-ing the trainer and
passes its trainer interpreter as --interpreter.

CLI:
  python3 harness/grader_runtime_preflight.py --interpreter /path/to/python3 \
      [--artifact-out DIR_OR_FILE]
Exit 0 = import resolves there; exit 3 = fail-closed refusal.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

CARD_ID = "C-9122"
# The EXACT import that died at 2026-09-16T08:36:44Z inside exec_module.
GRADER_IMPORT = "from qiskit.quantum_info import Statevector"
MARKER = "c9122_grader_runtime_ok"
RC_OK, RC_FAIL = 0, 3

PROBE_SNIPPET = (
    GRADER_IMPORT + "\n"
    "import json as _json, qiskit, sys as _sys\n"
    "print(_json.dumps({'marker': '" + MARKER + "', "
    "'qiskit': qiskit.__version__, 'python': _sys.version.split()[0]}))\n"
)


class GraderRuntimeError(RuntimeError):
    """Fail-closed refusal: grader runtime cannot import the grader deps."""


def probe_command(interp: str) -> list[str]:
    """argv that runs the exact failing import in the EXACT interpreter."""
    return [str(interp), "-c", PROBE_SNIPPET]


def _default_runner(argv, timeout_s):
    cp = subprocess.run(argv, capture_output=True, text=True, timeout=timeout_s, check=False)
    return cp.returncode, cp.stdout, cp.stderr


def probe_runtime(interp, runner=None, timeout_s: float = 60.0) -> dict:
    """Probe doc: ok=True ONLY on rc==0 AND the marker line present.

    runner(argv) -> (rc, stdout, stderr); injectable so the suite never
    spawns a real interpreter.
    """
    runner = runner or (lambda argv, _t=timeout_s: _default_runner(argv, _t))
    argv = probe_command(interp)
    doc: dict = dict(card=CARD_ID, artifact="grader_runtime_probe", interp=str(interp))
    try:
        rc, out, err = runner(argv)
    except Exception as exc:  # noqa: BLE001 -- fail closed on ANY spawn failure
        doc.update(
            ok=False,
            reason="interpreter_spawn_failed",
            detail=type(exc).__name__ + ": " + str(exc)[:200],
        )
        return doc
    doc["rc"] = rc
    if rc == 0 and MARKER in out:
        parsed = None
        for line in reversed(out.strip().splitlines()):
            if MARKER in line:
                try:
                    parsed = json.loads(line)
                except Exception:  # noqa: BLE001
                    parsed = None
                break
        if parsed is None:
            doc.update(ok=False, reason="marker_line_unparsable")
            return doc
        doc.update(
            ok=True,
            reason=None,
            qiskit_version=parsed.get("qiskit"),
            python_version=parsed.get("python"),
            probe_argv=argv,
        )
        return doc
    if rc == 0:
        doc.update(ok=False, reason="marker_missing_on_rc0")
        return doc
    doc.update(ok=False, reason="qiskit_import_failed", stderr_tail=(err or "")[-400:])
    return doc


def require_grader_runtime(interp, runner=None, timeout_s: float = 60.0) -> dict:
    """Return the ok probe doc, or raise GraderRuntimeError BEFORE launch."""
    doc = probe_runtime(interp, runner=runner, timeout_s=timeout_s)
    if not doc.get("ok"):
        why = doc.get("reason") or "unknown"
        tail = doc.get("stderr_tail") or doc.get("detail") or ""
        raise GraderRuntimeError(
            CARD_ID
            + " fail-closed: grader runtime "
            + str(interp)
            + " cannot run the self-eval grader ("
            + why
            + "); requires '"
            + GRADER_IMPORT
            + "' to import in THAT interpreter. "
            + str(tail).strip()
        )
    return doc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=CARD_ID + " grader-runtime preflight")
    ap.add_argument(
        "--interpreter",
        required=True,
        help="the EXACT interpreter the trainer/grader will run under",
    )
    ap.add_argument(
        "--artifact-out", default=None, help="file path (or dir) for the probe artifact JSON"
    )
    args = ap.parse_args(argv)
    doc = probe_runtime(args.interpreter)
    out_path = None
    if args.artifact_out:
        p = Path(args.artifact_out)
        if p.is_dir() or str(args.artifact_out).endswith("/"):
            p = p / (CARD_ID + "_grader_runtime_probe.json")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
        out_path = str(p)
    print(json.dumps({k: v for k, v in doc.items() if k != "probe_argv"}))
    if out_path and doc.get("ok"):
        print(
            CARD_ID
            + ": OK qiskit=="
            + str(doc.get("qiskit_version"))
            + " in "
            + str(doc.get("interp"))
            + " -> "
            + out_path
        )
    elif out_path:
        print(
            CARD_ID + ": FAIL-CLOSED " + str(doc.get("reason")) + " -> " + out_path, file=sys.stderr
        )
    return RC_OK if doc.get("ok") else RC_FAIL


if __name__ == "__main__":
    sys.exit(main())
