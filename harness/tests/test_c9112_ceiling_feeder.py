"""C-9112: c9038_ceiling feeder -- bank the C-9094-schema ceiling artifact
Mac-side PRE-LEG so the c9071 window gate stops listing c9038_ceiling
unmet (dep-cycle split from C-9038 by C-9101).

Fail-closed contract under test:
  - harness/state/preflights/C-9038_ceiling.json exists with the exact
    gate schema (artifact==ceiling, max_new_tokens int>0, proven_pass,
    runner relpath, 64-hex sha pin, mtime pin);
  - pins describe the CURRENT runner bytes on disk (B-223: never edited
    to match; the file is the C-0024 freeze-manifest runner);
  - the gate checker resolves the LIVE artifact and a full evaluate()
    over synthetic dirs drops the key;
  - proven_pass is REPRODUCIBLE Mac-side: at the banked floor, the
    canonical runner generate() path (real tokenizer prompt render +
    cap semantics + sanitize + single_candidate_eval grader) passes on
    the recorded known-long-correct fixture, whose measured token count
    fits under the floor.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))
import asi2_window_preflight_gate as G  # noqa: E402
import pytest

ART = ROOT / "harness/state/preflights/C-9038_ceiling.json"
RUNNER_REL = "scripts/run_asi2_base_adapter_rubric_eval.py"


def _doc():
    return json.loads(ART.read_text())


def _runner_module():
    spec = importlib.util.spec_from_file_location("c9112_canon_runner", ROOT / RUNNER_REL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_ceiling_artifact_exists_with_gate_schema():
    doc = _doc()
    assert doc.get("artifact") == "ceiling"
    cap = doc.get("max_new_tokens")
    assert isinstance(cap, int) and not isinstance(cap, bool) and cap > 0
    assert doc.get("proven_pass") is True
    rel = doc.get("runner")
    assert isinstance(rel, str) and rel.strip()
    sha = doc.get("runner_sha256")
    assert isinstance(sha, str) and len(sha) == 64
    assert isinstance(doc.get("runner_mtime"), (int, float))


def test_ceiling_pins_match_current_runner_b223():
    doc = _doc()
    path = ROOT / doc["runner"]
    assert path.is_file(), path
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    assert got.lower() == doc["runner_sha256"].lower()
    assert abs(path.stat().st_mtime - float(doc["runner_mtime"])) <= 1e-6
    # the runner must be the C-0024 freeze-manifest bytes, never edited
    assert doc["runner"] == RUNNER_REL


def test_gate_checker_resolves_live_artifact_and_drops_key(tmp_path):
    doc = _doc()
    assert G._check_c9038(doc, dict(runner_root=str(ROOT))) is None
    # full evaluate() over synthetic dirs: window fresh + other two
    # preflights well-formed + the LIVE ceiling artifact -> key dropped
    import time as _t

    ts = _t.strftime("%Y-%m-%dT%H:%M:%SZ", _t.gmtime())
    (tmp_path / "c9061").mkdir()
    (tmp_path / "c9061" / "window_open.json").write_text(
        json.dumps(dict(artifact="window_open", generated_utc=ts, bar=dict(pid=1)))
    )
    (tmp_path / "preflights").mkdir()
    (tmp_path / "preflights" / "C-9066_sdk_positive_control.json").write_text(
        json.dumps(
            dict(
                artifact="sdk_positive_control",
                ok=True,
                utc=ts,
                interpreters=[dict(qiskit=True, pennylane=True, cirq=True, control_rc=0)],
            )
        )
    )
    (tmp_path / "preflights" / "C-9051_parity.json").write_text(
        json.dumps(dict(artifact="parity", verdict="PARITY-OK", runner_sha256=dict([("a", "b")])))
    )
    (tmp_path / "preflights" / "C-9038_ceiling.json").write_text(json.dumps(doc))
    ctx = G.make_ctx(
        tmp_path / "c9061",
        tmp_path / "preflights",
        tmp_path / "c9071",
        tmp_path / "state",
        runner_root=str(ROOT),
        clock=lambda: _t.time(),
    )
    verdict, _art, detail = G.evaluate(ctx)
    assert "c9038_ceiling" not in detail["unmet"], detail["unmet"]
    assert verdict == "GO"


@pytest.mark.timeout(300)
def test_pass_at_floor_reproducible_through_canonical_runner(tmp_path):
    doc = _doc()
    floor = doc["max_new_tokens"]
    fixture_rel = doc["fixture"]
    fixture_tokens = doc["fixture_tokens"]
    assert isinstance(fixture_tokens, int) and 0 < fixture_tokens <= floor
    task_dir = ROOT / fixture_rel
    meta = json.loads((task_dir / "task.json").read_text())
    runner = _runner_module()
    import glob as _g

    from transformers import AutoTokenizer

    snaps = _g.glob(
        str(Path.home() / ".cache/huggingface/hub/models--Qwen--Qwen2.5-0.5B-Instruct/snapshots/*")
    )
    assert snaps, "no local Qwen tokenizer snapshot"
    tok = AutoTokenizer.from_pretrained(snaps[0], local_files_only=True)

    class StubBackend:
        pass

    backend = StubBackend()
    backend.text_backend = tok
    backend.render_backend = tok

    solution_ids = tok((task_dir / "candidate.py").read_text(), add_special_tokens=False)[
        "input_ids"
    ]
    assert len(solution_ids) == fixture_tokens

    class StubModel:
        # real greedy-generate cap semantics: at most max_new_tokens NEW ids
        def generate(self, **kw):
            budget = int(kw["max_new_tokens"])
            full = kw["input_ids"][0].tolist() + solution_ids[:budget]
            import torch

            return torch.tensor([full])

    prompt = runner.build_prompt(task_dir, meta)
    # C-9038: generate() now returns (code, truncated); the proof also
    # pins that the longest known-correct fixture fits the floor WITHOUT
    # hitting the cap.
    code, truncated = runner.generate(StubModel(), backend, prompt, "cpu", floor)
    assert truncated is False, "the longest known-correct reference must fit the floor uncapped"
    result = runner.run_single_file_test(
        task_dir, meta, code, tmp_path / "candidate_fixture.py", 120
    )
    assert result["passed"] is True, result["details"]
