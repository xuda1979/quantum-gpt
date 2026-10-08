"""B-093 - cron_doctor logs "patched" whether or not it patched.

Root cause at the line (scripts/session_keeper.sh, cron_doctor):

    grep -q "claude_headless.env" "$f" || \\
      sed -i '' '...' "$f" 2>/dev/null && \\
      echo "...patched $f" >> "$LOG"

Bash binds `&&` and `||` at EQUAL precedence, left-associatively, so this parses
as `( grep || sed ) && echo`. The `echo` is therefore NOT attached to the `sed`:
it fires whenever `grep` SUCCEEDS - i.e. precisely when the file was ALREADY
patched and `sed` never ran. Measured live at filing: 19 job files, 19/19 already
carrying the marker, 19 "patched" lines logged, 0 files modified. The intended
semantics would have logged ZERO.

Class: a counterfeit action log in the same production instrument as B-089 - a
reader concludes production cron config was repaired 19 times.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "session_keeper.sh"
SCRIPT_TEXT = SCRIPT.read_text(encoding="utf-8")


def _cron_doctor_body() -> str:
    start = SCRIPT_TEXT.index("cron_doctor()")
    end = SCRIPT_TEXT.index(chr(10) + "}" + chr(10), start)
    return SCRIPT_TEXT[start:end]


def _run_cron_doctor(tmp_path):
    """Run cron_doctor in a subshell against a FAKE jobs dir; return (log, jobs)."""
    import os as _os
    import subprocess as _sp

    jobs = tmp_path / "jobs"
    marked = jobs / "job_marked" / "run.sh"
    unmarked = jobs / "job_unmarked" / "run.sh"
    marked.parent.mkdir(parents=True)
    unmarked.parent.mkdir(parents=True)
    marked.write_text(
        "# already has it\nsource /Users/daxu/.claude-mcp-cron/claude_headless.env\n",
        encoding="utf-8",
    )
    unmarked.write_text("#!/bin/bash\necho hi\ndone\n", encoding="utf-8")

    klog = tmp_path / "keeper.log"
    harness = tmp_path / "cron_harness.sh"
    harness.write_text(
        "#!/bin/bash\n"
        "set -u\n"
        "export SK_CRON_JOBS_DIR=" + repr(str(jobs)) + "\n"
        "export SK_KEEPER_LOG=" + repr(str(klog)) + "\n"
        "source " + str(SCRIPT) + " --source-only >/dev/null 2>&1\n"
        "cron_doctor\n"
        "exit 0\n",
        encoding="utf-8",
    )
    harness.chmod(0o755)
    env = _os.environ.copy()
    env["SK_CRON_JOBS_DIR"] = str(jobs)
    env["SK_KEEPER_LOG"] = str(klog)
    _sp.run(
        ["bash", str(harness)], cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=30
    )
    text = klog.read_text(encoding="utf-8") if klog.exists() else ""
    return text, marked, unmarked


def test_cron_doctor_reports_exactly_one_patch_and_only_for_the_unmarked_file(tmp_path):
    """BEHAVIOURAL: the counterfeit-log bug measured directly.

    Pre-fix the operator expression is `( grep || sed ) && echo`, so the echo
    fires for the MARKED file (where grep succeeds and sed never runs). The
    observed live signature was 19 files / 19 marked / 19 "patched" / 0 modified.
    Post-fix, exactly ONE line is reported and it names the UNMARKED file.
    """
    text, marked, unmarked = _run_cron_doctor(tmp_path)
    patched_lines = [ln for ln in text.splitlines() if "patched " in ln]

    assert (
        marked.read_text(encoding="utf-8").count("claude_headless.env") == 1
    ), "the already-marked file must not be re-patched"
    assert (
        "claude_headless.env" in unmarked.read_text(encoding="utf-8").split("fi")[0]
    ), "the unmarked file SHOULD have been patched - otherwise this test proves nothing"
    assert len(patched_lines) == 1, (
        "expected exactly ONE 'patched' report (for the unmarked file), got "
        + str(len(patched_lines))
        + ": "
        + str(patched_lines)
        + " - a report that "
        "does not correspond to a real patch is a counterfeit action log (B-093)."
    )
    assert (
        "job_unmarked" in patched_lines[0]
    ), "the single report must name the file that was ACTUALLY patched"
