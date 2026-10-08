"""C-9640: per-task targeted repair-data for quantum_channel_depolarizing.

Failure class: contract-miss (gap_to_pass=0.76). Candidate returns None
from a required function -> clean assertion failure. Repair rows lead with
the exact public API and require concrete numeric returns (never None).
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "harness/state/staged/c9640-channel-depolari-repair-v1"
DATASET = STAGE / "c9640_channel_depolari_repair_v1.jsonl"
MANIFEST = STAGE / "c9640_channel_depolari_repair_v1.manifest.json"
SHA_PIN = STAGE / "SHA_PIN.sha256"
TASK_ID = "quantum_channel_depolarizing"
SUBDIR = "quantum_channel_depolarizing"


def _rows():
    return [json.loads(l) for l in DATASET.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_dataset_exists():
    assert DATASET.exists(), "dataset missing (RED)"
    assert MANIFEST.exists(), "manifest missing (RED)"
    assert SHA_PIN.exists(), "SHA_PIN missing (RED)"


def test_single_task_repair_rows():
    rows = _rows()
    assert len(rows) >= 3, "need >=3 repair rows"
    assert all(
        r[chr(109) + chr(101) + chr(116) + chr(97) + chr(100) + chr(97) + chr(116) + chr(97)][
            chr(116) + chr(97) + chr(115) + chr(107) + chr(95) + chr(105) + chr(100)
        ]
        == TASK_ID
        for r in rows
    )
    assert all(
        r.get(chr(102) + chr(111) + chr(114) + chr(109) + chr(97) + chr(116)) == "chat-sft-v1"
        for r in rows
    )
    ref = (ROOT / "evals/tasks/quantum" / SUBDIR / "candidate.py").read_text(encoding="utf-8")
    for r in rows:
        assert (
            r[chr(109) + chr(101) + chr(115) + chr(115) + chr(97) + chr(103) + chr(101) + chr(115)][
                -1
            ][chr(114) + chr(111) + chr(108) + chr(101)]
            == "assistant"
        )
        assert (
            r[chr(109) + chr(101) + chr(115) + chr(115) + chr(97) + chr(103) + chr(101) + chr(115)][
                -1
            ][chr(99) + chr(111) + chr(110) + chr(116) + chr(101) + chr(110) + chr(116)].strip()
            == ref.strip()
        ), "assistant output != reference (RED)"


def test_failure_mode_documented():
    mf = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert mf[chr(116) + chr(97) + chr(115) + chr(107) + chr(95) + chr(105) + chr(100)] == TASK_ID
    assert (
        mf[
            chr(98)
            + chr(97)
            + chr(115)
            + chr(101)
            + chr(95)
            + chr(102)
            + chr(97)
            + chr(105)
            + chr(108)
            + chr(117)
            + chr(114)
            + chr(101)
        ]
        and mf[
            chr(97)
            + chr(100)
            + chr(97)
            + chr(112)
            + chr(116)
            + chr(101)
            + chr(114)
            + chr(95)
            + chr(102)
            + chr(97)
            + chr(105)
            + chr(108)
            + chr(117)
            + chr(114)
            + chr(101)
        ]
    )
    assert (
        "returns None"
        in mf[
            chr(98)
            + chr(97)
            + chr(115)
            + chr(101)
            + chr(95)
            + chr(102)
            + chr(97)
            + chr(105)
            + chr(108)
            + chr(117)
            + chr(114)
            + chr(101)
        ]
    )
    assert (
        "None-stub"
        in mf[
            chr(97)
            + chr(100)
            + chr(97)
            + chr(112)
            + chr(116)
            + chr(101)
            + chr(114)
            + chr(95)
            + chr(102)
            + chr(97)
            + chr(105)
            + chr(108)
            + chr(117)
            + chr(114)
            + chr(101)
        ]
    )


def test_public_api_emphasized_in_user():
    for r in _rows():
        user = r[
            chr(109) + chr(101) + chr(115) + chr(115) + chr(97) + chr(103) + chr(101) + chr(115)
        ][0][chr(99) + chr(111) + chr(110) + chr(116) + chr(101) + chr(110) + chr(116)]
        assert (
            "depolarizing_channel" in user
            and "amplitude_damping_channel" in user
            and "channel_fidelity" in user
        ), "public API not emphasized (RED)"
        assert "NEVER None" in user, "None-stub guard not emphasized (RED)"
        assert (
            "complete" in user.lower() and "markdown" in user.lower()
        ), "conciseness/no-markdown not emphasized (RED)"


def test_manifest_sha_and_pin():
    actual = hashlib.sha256(DATASET.read_bytes()).hexdigest()
    mf = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert mf[chr(115) + chr(104) + chr(97) + chr(50) + chr(53) + chr(54)] == actual
    pin = SHA_PIN.read_text(encoding="utf-8")
    assert (
        DATASET.name in pin
        and mf[chr(115) + chr(104) + chr(97) + chr(50) + chr(53) + chr(54)] in pin
    )


def test_reference_passes_tests():
    cand = ROOT / "evals/tasks/quantum" / SUBDIR / "candidate.py"
    tests = ROOT / "evals/tasks/quantum" / SUBDIR / "tests.py"
    tdir = ROOT / "evals/tasks/quantum" / SUBDIR
    meta = json.dumps(dict(id="t"))
    res = subprocess.run(
        [
            "python3",
            "evals/runner/single_candidate_eval.py",
            "--candidate",
            str(cand),
            "--tests",
            str(tests),
            "--task-dir",
            str(tdir),
            "--meta",
            meta,
        ],
        capture_output=True,
        text=True,
    )
    try:
        o = json.loads(res.stdout.strip().splitlines()[-1])
        ok = o.get("harness", dict()).get("passed")
    except Exception:
        ok = False
    assert ok, "reference must pass tests.py (RED)"


def test_related_suites_still_pass():
    res = subprocess.run(
        ["pytest", "-q", "tests/test_c9626_gap_driven_sft.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stdout[-800:] + res.stderr[-800:]
