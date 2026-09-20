"""C-9094: c9071 window-gate artifact contract -- bind every SKIP unmet
key to its producing card + exact artifact path + required schema.

RED first 2026-09-18: harness/state/c9071/CONTRACT.md did not exist and
the C-9066/C-9051/C-9038 acceptance never named the gate artifact
paths/schema (C-9066 even banks probes under harness/state/probes/), so
green work could land off-path forever and the gate stayed SKIP
(EVENTS 04:48:42Z: all three keys artifact_missing). Contract under test:
  - CONTRACT.md carries one row per PREFLIGHTS key naming the producing
    card, the exact artifact filename, and the required schema fields;
  - the documented path EQUALS the gate PREFLIGHTS tuple filename under
    the gate DEFAULT preflight dir harness/state/preflights (the c9071
    dir holds only the gate own verdict artifacts);
  - dropping a WELL-FORMED synthetic artifact AT THE DOCUMENTED PATH
    resolves that unmet key (the gate opens when owners comply);
  - every malformed variant (wrong/missing field) stays UNMET with the
    gate named reason -- fail-closed in BOTH directions.
Filenames are taken FROM the contract doc; artifact bytes live in tmp_path
only -- the suite never writes live harness state.
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))
import asi2_window_preflight_gate as G  # noqa: E402

CONTRACT = ROOT / "harness" / "state" / "c9071" / "CONTRACT.md"
DEFAULT_PREFLIGHT_DIR = "harness/state/preflights"

# gate unmet key -> producing card (the ownership half of the contract)
PRODUCER = dict(
    c9066_sdk_positive_control="C-9066",
    c9051_parity_ok="C-9051",
    c9038_ceiling="C-9038",
)

ROW_RE = re.compile(
    r"^\|\s*(C-[0-9][0-9][0-9][0-9])\s*\|\s*(\w+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$"
)


def _contract_rows():
    """key -> (card, documented path, schema-cell text)."""
    rows = dict()
    for line in CONTRACT.read_text().splitlines():
        m = ROW_RE.match(line.strip())
        if m:
            rows[m.group(2)] = (m.group(1), m.group(3), m.group(4))
    return rows


def _write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")
    return path


def _sdk_ok():
    return dict(
        card="C-9066",
        artifact="sdk_positive_control",
        ok=True,
        utc="2027-01-15T07:59:00Z",
        interpreters=[
            dict(
                interpreter="/usr/bin/python3", qiskit=True, pennylane=True, cirq=True, control_rc=0
            )
        ],
    )


def _parity_ok():
    return dict(
        card="C-9051",
        artifact="parity",
        verdict="PARITY-OK",
        runner_sha256=dict([("evals/foo.py", "a" * 64)]),
    )


def _ceiling_ok(tmp):
    """Well-formed ceiling artifact pinning a REAL runner file sha+mtime."""
    mtime = 1_799_999_940.0
    runner = tmp / "box" / "run_asi2_base_adapter_rubric_eval.py"
    runner.parent.mkdir(parents=True, exist_ok=True)
    runner.write_text("# canonical runner\n")
    os.utime(runner, (mtime, mtime))
    sha = hashlib.sha256(runner.read_bytes()).hexdigest()
    return dict(
        card="C-9038",
        artifact="ceiling",
        max_new_tokens=384,
        proven_pass=True,
        runner="box/run_asi2_base_adapter_rubric_eval.py",
        runner_sha256=sha,
        runner_mtime=mtime,
    )


def _well_formed(key, tmp):
    if key == "c9066_sdk_positive_control":
        return _sdk_ok()
    if key == "c9051_parity_ok":
        return _parity_ok()
    return _ceiling_ok(tmp)


def _malformed(tmp):
    """key -> list of (bad artifact, expected unmet reason). The named
    reasons are the gate own vocabulary (checkers in the gate module)."""
    sdk = _sdk_ok()
    par = _parity_ok()
    ceil = _ceiling_ok(tmp)
    return dict(
        c9066_sdk_positive_control=[
            (dict(sdk, ok=False), "ok_not_true"),
            (
                dict(
                    sdk,
                    interpreters=[
                        dict(
                            interpreter="/usr/bin/python3",
                            qiskit=True,
                            pennylane=True,
                            cirq=True,
                            control_rc=1,
                        )
                    ],
                ),
                "interpreter_control_failed",
            ),
            (dict(sdk, artifact="sdk_diagnostic"), "artifact_mismatch"),
        ],
        c9051_parity_ok=[
            (dict(par, verdict="PARITY-DRIFT"), "verdict_not_PARITY-OK"),
            (dict(par, runner_sha256=dict()), "sha_pins_missing"),
        ],
        c9038_ceiling=[
            (dict(ceil, max_new_tokens=0), "ceiling_missing"),
            (dict(ceil, proven_pass=False), "not_proven"),
        ],
    )


def _ctx(tmp):
    return G.make_ctx(
        window_dir=str(tmp / "c9061"),
        preflight_dir=str(tmp / "preflights"),
        gate_dir=str(tmp / "c9071"),
        state_dir=str(tmp / "state"),
        runner_root=str(tmp),
        clock=lambda: 1_800_000_000.0,
    )


# ------------------------------------------------------------ doc binding


def test_contract_doc_exists_and_binds_every_gate_key():
    assert CONTRACT.is_file(), "missing " + str(CONTRACT)
    rows = _contract_rows()
    for key, fname, _check in G.PREFLIGHTS:
        assert key in rows, "no contract row for " + key
        card, doc_path, _schema = rows[key]
        assert card == PRODUCER[key], (key, card)
        assert doc_path.endswith("/" + fname), (key, doc_path, fname)
        assert DEFAULT_PREFLIGHT_DIR + "/" in doc_path + "/", (key, doc_path)


def test_contract_schema_cell_names_required_fields():
    rows = _contract_rows()
    must_name = dict(
        c9066_sdk_positive_control=("sdk_positive_control", "ok", "interpreters", "control_rc"),
        c9051_parity_ok=("parity", "PARITY-OK", "runner_sha256"),
        c9038_ceiling=("ceiling", "max_new_tokens", "proven_pass", "runner_sha256", "runner_mtime"),
    )
    for key, _fname, _check in G.PREFLIGHTS:
        _card, _p, schema = rows[key]
        for token in must_name[key]:
            assert token in schema, (key, token, schema)


# --------------------------------------------- behavior AT the documented path


def test_well_formed_artifact_at_documented_path_resolves_key(tmp_path):
    rows = _contract_rows()
    for key, fname, _check in G.PREFLIGHTS:
        _card, doc_path, _schema = rows[key]
        assert Path(doc_path).name == fname, (key, doc_path)
        doc = _well_formed(key, tmp_path)
        _write(tmp_path / "preflights" / fname, doc)
        _verdict, _art, detail = G.evaluate(_ctx(tmp_path))
        assert key not in detail["unmet"], (key, detail["unmet"])


def test_malformed_artifact_at_documented_path_stays_unmet(tmp_path):
    _contract_rows()
    bad_by_key = _malformed(tmp_path)
    for key, fname, _check in G.PREFLIGHTS:
        for bad, reason in bad_by_key[key]:
            _write(tmp_path / "preflights" / fname, bad)
            _verdict, _art, detail = G.evaluate(_ctx(tmp_path))
            assert detail["unmet"].get(key) == reason, (key, reason, detail["unmet"])


def test_c9038_sha_drift_at_documented_path_stays_unmet(tmp_path):
    """B-223 half of the ceiling contract: pins must match the CURRENT file."""
    rows = _contract_rows()
    _card, _p, _s = rows["c9038_ceiling"]
    art = _ceiling_ok(tmp_path)
    art["runner_sha256"] = "a" * 64  # real file, wrong pin
    _write(tmp_path / "preflights" / "C-9038_ceiling.json", art)
    _verdict, _art, detail = G.evaluate(_ctx(tmp_path))
    assert detail["unmet"]["c9038_ceiling"] == "runner_sha_drift", detail["unmet"]


# --------------------------------------------------- writer attribution C-9103
# Every SKIP/GO artifact must stamp the writing process (pid + ps lstart) so
# B-223 staleness is checkable from the artifact ALONE: a consumer compares
# writer.lstart against the gate-file mtime and refuses verdicts authored by
# pre-edit code. Injection via ctx keeps the asserts hermetic.


def test_gate_artifact_stamps_injected_writer_pid_and_lstart(tmp_path):
    ctx = _ctx(tmp_path)
    ctx["writer_pid"] = 4242
    ctx["writer_lstart"] = "2026-09-18T10:12:48Z"
    _verdict, art_path, _detail = G.evaluate(ctx)
    payload = json.loads(Path(art_path).read_text())
    w = payload.get("writer")
    assert isinstance(w, dict), "gate artifact carries no writer stamp"
    assert w.get("pid") == 4242, w
    assert w.get("lstart") == "2026-09-18T10:12:48Z", w


def test_gate_artifact_writer_stamp_defaults_to_live_process(tmp_path):
    import time as _t

    _verdict, art_path, _detail = G.evaluate(_ctx(tmp_path))
    w = json.loads(Path(art_path).read_text())["writer"]
    assert w.get("pid") == os.getpid(), w
    ts = G._parse_iso(w.get("lstart"))
    assert ts is not None, w
    assert 0 <= _t.time() - ts < 86400, w  # started within the last 24h
