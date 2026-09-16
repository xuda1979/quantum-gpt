import importlib.util
import re
from pathlib import Path

# C-0002: the staged fail-closed leg launcher must be importable and its two
# regexes must work. RED 2026-09-16: module referenced an undefined name DL
# at module level (VERSIONS_RX) and in the adapter-step regex -> NameError on
# import, so the launcher could never run (py_compile alone cannot catch it).

LAUNCHER = Path(__file__).resolve().parents[2] / "tmp" / "c0002_launch_leg.py"


def _load():
    spec = importlib.util.spec_from_file_location("c0002_launch_leg", LAUNCHER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_module_imports_and_version_regex_accepts_known_sdks():
    mod = _load()
    for line in ("2.5.2 0.45.1 1.7.0", "2.4.1 0.44.0 1.3.2"):
        assert re.match(mod.VERSIONS_RX, line), line


def test_version_regex_rejects_error_line():
    mod = _load()
    assert not re.match(mod.VERSIONS_RX, "ModuleNotFoundError: No module named qiskit")


def test_adapter_step_extraction():
    mod = _load()
    m = mod.re.search(
        mod.ADAPTER_STEP_RX, "/x/outputs/sapo-27b-ai-20260915T1010/step_000100_adapter"
    )
    assert m and m.group(1) == "100"
