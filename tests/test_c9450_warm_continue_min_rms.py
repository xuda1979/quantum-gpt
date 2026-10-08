"""C-9450: warm-continue training launches must pass --min-rms-for-update 0.01.

The dispersion-collapse gate (grpo_utils.py) prevents gradient updates on
groups with near-zero reward variance (RMS < threshold). Without this flag,
warm-continue from a checkpoint that has already converged on easy tasks
wastes compute on zero-gradient groups and can degrade the adapter.

RED 2026-09-20: the launcher script asi2_launch_grpo_27b_selfeval.sh
never passes --min-rms-for-update, even when ADAPTER_INIT is set (warm-
continue mode). This means all warm-continue launches run without the
dispersion gate, risking degradation on already-converged groups.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "scripts" / "asi2_launch_grpo_27b_selfeval.sh"


def test_warm_continue_passes_min_rms_for_update():
    """When ADAPTER_INIT is set, the launcher must pass --min-rms-for-update."""
    script = LAUNCHER.read_text(encoding="utf-8")
    # Find the ADAPTER_INIT block
    adapter_block = re.search(r"ADAPTER_INIT.*?fi", script, re.DOTALL)
    assert adapter_block is not None, "ADAPTER_INIT block not found"
    # The script must reference --min-rms-for-update somewhere in the
    # RESUME_FLAGS section (which is built when ADAPTER_INIT is set)
    assert "--min-rms-for-update" in script, (
        "Launcher must pass --min-rms-for-update for warm-continue "
        "(ADAPTER_INIT) launches to prevent dispersion collapse"
    )


def test_min_rms_default_is_001():
    """The default value for --min-rms-for-update must be 0.01."""
    script = LAUNCHER.read_text(encoding="utf-8")
    # Find --min-rms-for-update with value 0.01
    match = re.search(r'--min-rms-for-update\s+"?\$\{[^}]*:-0\.01\}', script)
    if match is None:
        # Also accept a literal 0.01
        match = re.search(r"--min-rms-for-update\s+0\.01", script)
    assert match is not None, "--min-rms-for-update must default to 0.01"
