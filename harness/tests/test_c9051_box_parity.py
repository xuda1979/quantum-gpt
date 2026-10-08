"""C-9051: pre-window box parity checker -- Mac-side, fail-closed.

RED first 2026-09-18: no box parity artifact producer existed. The C-9071
window gate binds c9051_parity_ok to EXACTLY
harness/state/preflights/C-9051_parity.json
(artifact==parity, verdict==PARITY-OK, runner_sha256 non-empty path->pin
object; harness/state/c9071/CONTRACT.md), and B-163 precedent says a
landed-Mac-fix / stale-box-launcher mismatch silently wastes a
console-gated ASI2 window. This suite pins the checker that measures the
BOX-SIDE runner/composer against the Mac canonical invariants:

  - box runner --max-new-tokens default == the C-9038 ceiling read from
    the CEILING ARTIFACT (never hardcoded; fixture uses a non-1536 value
    to prove the artifact is the source of truth);
  - box composer carries scorer_shas + holdout_sha256 emission (grep
    evidence, not claims);
  - B-223: any box-side long-lived runner/keeper process that started
    BEFORE its script mtime is named stale (stale code never reloads);
    absent process evidence is itself a named drift -- fail closed;
  - unmeasurable inputs NEVER raise: they return PARITY-DRIFT with a
    named drift item so the gate stays SKIP for a NAMED reason;
  - the produced PARITY-OK artifact satisfies the live gate checker
    (_check_c9051) and the malformed variants stay unmet fail-closed.

Snapshot layout under test (produced by the card's paced box fetch):
  <snapshot>/box/scripts/...           box-side file bytes, repo-relative
  <snapshot>/box_proc.json             measured box process evidence
Fixture bytes live in tmp_path only -- the suite never writes live
harness state.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))

import c9051_box_parity as parity  # noqa: E402
from asi2_window_preflight_gate import _check_c9051  # noqa: E402

# Non-canonical ceiling on purpose: proves the checker READS the ceiling
# artifact instead of hardcoding 1536.
CEILING = 2048
RUNNER_REL = "scripts/run_asi2_base_adapter_rubric_eval.py"
COMPOSER_REL = "scripts/holdout_verdict.py"

RUNNER_BOX_BYTES = (
    "import argparse\n"
    "def build():\n"
    '    parser.add_argument("--max-new-tokens", type=int, default=%d)\n'
    "    return parser\n" % CEILING
).encode()
RUNNER_BOX_STALE_BYTES = (
    b"import argparse\n"
    b"def build():\n"
    b'    parser.add_argument("--max-new-tokens", type=int, default=384)\n'
    b"    return parser\n"
)
COMPOSER_BOX_BYTES = (
    b"def compute_sha_pins():\n"
    b"    return holdout_sha, scorer_shas\n"
    b"doc['holdout_sha256'] = holdout_sha\n"
    b"doc['scorer_shas'] = scorer_shas\n"
)
COMPOSER_BOX_NO_PINS = b"def compute_sha_pins():\n    return None\n"


def _ceiling_artifact(root):
    p = root / "harness/state/preflights/C-9038_ceiling.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    doc = dict(
        artifact="ceiling",
        max_new_tokens=CEILING,
        proven_pass=True,
        runner=RUNNER_REL,
        runner_sha256="0" * 64,
        runner_mtime=1.0,
    )
    p.write_text(json.dumps(doc))
    return p


def _snapshot(
    root, runner=RUNNER_BOX_BYTES, composer=COMPOSER_BOX_BYTES, proc=None, with_proc=True
):
    snap = root / "snapshot"
    (snap / "box" / "scripts").mkdir(parents=True, exist_ok=True)
    (snap / "box" / RUNNER_REL).write_bytes(runner)
    (snap / "box" / COMPOSER_REL).write_bytes(composer)
    if with_proc:
        script = snap / "box" / RUNNER_REL
        row = dict(
            source="exec:20646/ASI1",
            pid=4242,
            etimes_s=5,
            cmdline="python3 " + RUNNER_REL,
            script=RUNNER_REL,
            script_mtime=script.stat().st_mtime,
            sampled_epoch=script.stat().st_mtime + 100,
        )
        rows = proc if proc is not None else [row]
        (snap / "box_proc.json").write_text(json.dumps(rows))
    return snap


def _run(root, snap):
    return parity.check_parity(
        mac_root=root,
        snapshot_dir=snap,
        ceiling_path=root / "harness/state/preflights/C-9038_ceiling.json",
    )


# ----------------------------------------------------------------- OK path


def test_parity_ok_fixture(tmp_path):
    root = tmp_path
    _ceiling_artifact(root)
    snap = _snapshot(root)
    art = _run(root, snap)
    assert art["artifact"] == "parity"
    assert art["verdict"] == "PARITY-OK", art["drift"]
    assert art["drift"] == []
    assert art["runner_default_max_new_tokens"] == CEILING
    assert art["composer_emits"]["scorer_shas"] is True
    assert art["composer_emits"]["holdout_sha256"] is True
    pins = art["runner_sha256"]
    assert isinstance(pins, dict) and pins, "sha pins must be non-empty"
    assert RUNNER_REL in pins and len(pins[RUNNER_REL]) == 64
    assert COMPOSER_REL in pins and len(pins[COMPOSER_REL]) == 64


def test_ok_artifact_passes_live_gate_checker(tmp_path):
    root = tmp_path
    _ceiling_artifact(root)
    art = _run(root, _snapshot(root))
    verdict = _check_c9051(art)
    assert verdict is None, verdict


# -------------------------------------------------------------- drift paths


def test_drift_runner_default_below_ceiling(tmp_path):
    root = tmp_path
    _ceiling_artifact(root)
    art = _run(root, _snapshot(root, runner=RUNNER_BOX_STALE_BYTES))
    assert art["verdict"] == "PARITY-DRIFT"
    assert any("runner_default_below_ceiling" in d for d in art["drift"])
    assert _check_c9051(art) == "verdict_not_PARITY-OK"


def test_drift_composer_missing_pins(tmp_path):
    root = tmp_path
    _ceiling_artifact(root)
    art = _run(root, _snapshot(root, composer=COMPOSER_BOX_NO_PINS))
    assert art["verdict"] == "PARITY-DRIFT"
    assert "composer_scorer_shas_missing" in art["drift"]
    assert "composer_holdout_sha_missing" in art["drift"]


def test_drift_b223_stale_process_named(tmp_path):
    root = tmp_path
    _ceiling_artifact(root)
    snap = _snapshot(root)
    script = snap / "box" / COMPOSER_REL
    stale = dict(
        source="exec:20646/ASI1",
        pid=77,
        etimes_s=10000,
        cmdline="python3 " + COMPOSER_REL,
        script=COMPOSER_REL,
        script_mtime=script.stat().st_mtime,
        sampled_epoch=script.stat().st_mtime + 100,
    )
    (snap / "box_proc.json").write_text(json.dumps([stale]))
    art = _run(root, snap)
    assert art["verdict"] == "PARITY-DRIFT"
    assert any("b223_stale_process" in d for d in art["drift"]), art["drift"]


def test_drift_proc_evidence_missing_failclosed(tmp_path):
    root = tmp_path
    _ceiling_artifact(root)
    snap = _snapshot(root, with_proc=False)
    art = _run(root, snap)
    assert art["verdict"] == "PARITY-DRIFT"
    assert "box_proc_evidence_missing" in art["drift"]


def test_drift_snapshot_missing_never_raises(tmp_path):
    root = tmp_path
    _ceiling_artifact(root)
    art = _run(root, root / "does_not_exist")
    assert art["verdict"] == "PARITY-DRIFT"
    assert any("snapshot" in d for d in art["drift"]), art["drift"]
    assert _check_c9051(art) == "verdict_not_PARITY-OK"


# ------------------------------------------------------------ gate binding


def test_gate_binds_exact_filename():
    import asi2_window_preflight_gate as gate

    names = [fname for _, fname, _ in gate.PREFLIGHTS]
    assert "C-9051_parity.json" in names


def test_gate_malformed_reasons_still_named():
    assert _check_c9051(dict(artifact="parity")) == "verdict_not_PARITY-OK"
    two = dict(artifact="parity", verdict="PARITY-OK")
    assert _check_c9051(two) == "sha_pins_missing"
    three = dict(verdict="PARITY-OK", runner_sha256=dict(a="b"))
    assert _check_c9051(three) == "artifact_mismatch"


# ------------------------------------------------------------- CLI banking


def test_main_writes_artifact_at_bound_schema(tmp_path):
    root = tmp_path
    _ceiling_artifact(root)
    snap = _snapshot(root)
    out = root / "C-9051_parity.json"
    rc = parity.main(
        [
            "--mac-root",
            str(root),
            "--snapshot-dir",
            str(snap),
            "--ceiling",
            str(root / "harness/state/preflights/C-9038_ceiling.json"),
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    art = json.loads(out.read_text())
    assert art["artifact"] == "parity"
    assert _check_c9051(art) is None


def test_main_ceiling_value_override_is_not_read_as_path(tmp_path):
    # The --help metavar "--ceiling CEILING" invites a bare number, but
    # main() used the string as the ceiling-artifact PATH: "--ceiling 1536"
    # raised ceiling_artifact_unreadable:FileNotFoundError and silently
    # dropped the box-default-vs-ceiling comparison (2026-09-19 live
    # re-verify trap). A bare integer is a ceiling VALUE; a path stays a
    # path (the pinned semantics of the banking test above).
    root = tmp_path
    _ceiling_artifact(root)
    snap = _snapshot(root)  # box runner default == fixture CEILING (2048)
    out = root / "C-9051_parity.json"
    rc = parity.main(
        [
            "--mac-root",
            str(root),
            "--snapshot-dir",
            str(snap),
            "--ceiling",
            "1536",
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    art = json.loads(out.read_text())
    assert not any(d.startswith("ceiling_artifact_unreadable") for d in art["drift"]), art["drift"]
    assert art["ceiling_max_new_tokens"] == 1536
    # the VALUE actually gates: fixture box default 2048 exceeds it
    assert any(d == "runner_default_mismatch:2048>1536" for d in art["drift"]), art["drift"]


# --- Mac canonical side of the acceptance (2026-09-19 re-verification) ----
# Acceptance: "max_new_tokens default equals the C-9038 ceiling" and
# "composer emits scorer_shas + holdout_sha256 (grep evidence, not
# claims)". The box mirrors the Mac canonical bytes, so the canonical
# tree itself must satisfy both before any box fetch can reach PARITY-OK
# (2026-09-19: canonical runner still defaulted 384 < ceiling 1536 while
# the ceiling artifact proves 384 cannot reach 18/18 -- max passing
# reference alone is 1087 tokens).


def _live(rel):
    p = ROOT / rel
    assert p.is_file(), "missing canonical file: " + rel
    return p.read_text()


def test_mac_canonical_runner_default_equals_c9038_ceiling():
    ceiling_doc = json.loads((ROOT / "harness/state/preflights/C-9038_ceiling.json").read_text())
    assert ceiling_doc["artifact"] == "ceiling"
    ceiling = ceiling_doc["max_new_tokens"]
    assert isinstance(ceiling, int) and ceiling > 0
    default = parity._runner_default(_live(parity.RUNNER_REL))
    assert default is not None, "canonical runner has no --max-new-tokens default"
    assert default == ceiling, (
        "canonical runner default "
        + str(default)
        + " != C-9038 ceiling "
        + str(ceiling)
        + " (B-163: a bare/default box invocation burns the window at 384)"
    )


def test_mac_canonical_composer_emits_scorer_and_holdout_shas():
    text = _live(parity.COMPOSER_REL)
    assert "scorer_shas" in text, "canonical composer missing scorer_shas"
    assert "holdout_sha256" in text, "canonical composer missing holdout_sha256"
