"""Card C-10547: the box-side eval subprocess must inherit the pyenv_f1
overlay PYTHONPATH so the 5 env_blocked holdout tasks (pennylane_vqe_h2,
cirq_qaoa_line, braket_bell_state, qiskit_qft_entangled,
pennylane_qml_iris_classification) become measurable.

RED (this card): a holdout leg fired by scripts/run_holdout_leg1.py /
run_holdout_leg2.py scores those 5 tasks as "import failed: No module
named 'pennylane'|'cirq'|'braket'|'qiskit'" because the fork-safe
evaluator (evals/runner/single_candidate_eval.py) exec_modules the
candidate/tests in a FRESH interpreter whose default site-packages does
NOT contain the quantum libs (C-10400 measured drift; C-10434 proved
PYTHONPATH=/root/work/filestorage/pyenv_f1 overlay makes all 5 reference
candidates PASS).

CONTRACT (this card):
  1. single_candidate_eval must PREPEND the box overlay
     /root/work/filestorage/pyenv_f1 (when present) to sys.path at
     startup, so a candidate that imports pennylane/cirq/braket/qiskit
     loads in the overlay regardless of which dispatcher fired it.
  2. Overlay injection must be fail-safe: when the overlay is ABSENT the
     module still imports and runs (a namespace overlay dir is only
     prepended if it actually exists). Never fail a leg on overlay miss.
  3. The overlay path is only prepended when it points at a real
     directory (no fixture/fabrication).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
RUNNER = REPO / "evals" / "runner" / "single_candidate_eval.py"


def _load_runner():
    sys.path.insert(0, str(RUNNER.parent))  # single_candidate_eval imports candidate_sanitize
    try:
        spec = importlib.util.spec_from_file_location("c10547_runner", RUNNER)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        return mod
    finally:
        try:
            sys.path.remove(str(RUNNER.parent))
        except ValueError:
            pass


def test_overlay_path_constant_defined():
    mod = _load_runner()
    assert hasattr(mod, "BOX_OVERLAY_PYTHONPATH"), (
        "single_candidate_eval must define BOX_OVERLAY_PYTHONPATH for the "
        "box-side env overlay (/root/work/filestorage/pyenv_f1)."
    )
    assert str(mod.BOX_OVERLAY_PYTHONPATH).endswith("pyenv_f1")


def test_overlay_prepended_to_syspath_when_present(tmp_path):
    overlay = tmp_path / "overlay"
    overlay.mkdir()
    mod = _load_runner()
    mod.BOX_OVERLAY_PYTHONPATH = overlay
    orig = list(sys.path)
    try:
        mod._inject_box_overlay()
        assert str(overlay) in sys.path, (
            "overlay dir must be prepended to sys.path; got %r" % (sys.path[:3],)
        )
        assert sys.path[0] == str(overlay), "overlay must be first in sys.path"
    finally:
        sys.path[:] = orig


def test_overlay_absent_is_noop(tmp_path):
    missing = tmp_path / "no-such-overlay"
    mod = _load_runner()
    mod.BOX_OVERLAY_PYTHONPATH = missing
    orig = list(sys.path)
    try:
        mod._inject_box_overlay()  # must NOT raise on missing overlay
    finally:
        sys.path[:] = orig
    assert str(missing) not in sys.path, "absent overlay path must not enter sys.path"
