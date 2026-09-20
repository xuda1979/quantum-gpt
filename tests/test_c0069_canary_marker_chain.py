"""Card C-0069: Mac-local canary rehearsal of the fail-closed marker chain.

The pinned tests (tests/test_eval_failclosed_probe.py,
tests/test_qg_smoke_gate_lora_v2.py) lock each link with FAKES. This file
runs the REAL producer end to end on a tiny random-init GPT-2 + a real peft
LoRA adapter saved to disk -- no fakes, no box, no network -- and pins the
full chain a goal verdict depends on:

  positive leg : live adapter -> rc 0, adapter_applied + adapter_probe_differs
                 stage events on stdout, BOTH hyphenated gate tokens
  zero control : inert (all-zero lora_B) adapter -> rc != 0, NO markers
  gate         : harness_lib.check_gate("eval-failclosed") passes the
                 positive stdout and SUPPRESSES the zero stdout, marker-less
                 text, the byte-identical contradiction, unknown gates
  composer     : holdout_verdict._marker_check accepts true env markers with
                 a corroborating log; rejects marker envs missing/false and
                 an uncorroborated log, citing gate-safe underscore names
  smoke gate   : qg_smoke_gate_lora_v2.decide SMOKE_PASS / SMOKE_FAIL shapes
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

try:
    import torch  # noqa: F401
    import transformers  # noqa: F401
    from peft import LoraConfig, get_peft_model  # noqa: F401
    from tokenizers import Tokenizer
    from tokenizers import models as tok_models
    from tokenizers import pre_tokenizers as tok_pretok
    from transformers import GPT2Config, GPT2LMHeadModel, PreTrainedTokenizerFast

    from harness import harness_lib
    from scripts import holdout_verdict, qg_smoke_gate_lora_v2

    DEPS_OK = True
except Exception:  # pragma: no cover - plain-python3 suite host
    DEPS_OK = False

pytestmark = pytest.mark.skipif(
    not DEPS_OK,
    reason="requires torch/transformers/peft/tokenizers and repo script modules",
)

# WordLevel vocab as (token, id) pairs: kept brace-free for heredoc writing.
VOCAB_PAIRS = [
    ("<pad>", 0),
    ("<unk>", 1),
    ("<bos>", 2),
    ("<eos>", 3),
    ("def", 4),
    ("solve", 5),
    ("return", 6),
    (":", 7),
    ("(", 8),
    (")", 9),
]
VOCAB = dict(VOCAB_PAIRS)
APPLIED = "adapter-applied"
PROBE_DIFFERS = "adapter-probe-differs"
LB = chr(123) + chr(123)  # jinja open, brace-free
RB = chr(125) + chr(125)  # jinja close, brace-free


def _save_tiny_base(base_dir):
    """Random-init 1-layer GPT-2 + tiny WordLevel tokenizer, fully offline."""
    base_dir.mkdir(parents=True, exist_ok=True)
    config = GPT2Config(
        vocab_size=32,
        n_positions=16,
        n_embd=16,
        n_layer=1,
        n_head=2,
        bos_token_id=2,
        eos_token_id=3,
        pad_token_id=0,
    )
    GPT2LMHeadModel(config).save_pretrained(base_dir)
    word = tok_models.WordLevel(vocab=VOCAB, unk_token="<unk>")
    tok = Tokenizer(word)
    tok.pre_tokenizer = tok_pretok.Whitespace()
    fast = PreTrainedTokenizerFast(
        tokenizer_object=tok,
        unk_token="<unk>",
        pad_token="<pad>",
        bos_token="<bos>",
        eos_token="<eos>",
    )
    fast.chat_template = "Q: " + LB + " messages[-1]['content'] " + RB + "\nA:"
    fast.save_pretrained(base_dir)


def _save_adapter(base_dir, adapter_dir, nonzero):
    """Real peft LoRA on the tiny base; lora_B zeroed unless nonzero=True."""
    model = GPT2LMHeadModel.from_pretrained(str(base_dir))
    lora = LoraConfig(
        r=2,
        lora_alpha=4,
        lora_dropout=0.0,
        target_modules=["c_attn"],
        bias="none",
        task_type="CAUSAL_LM",
    )
    merged = get_peft_model(model, lora)
    if nonzero:
        with torch.no_grad():
            for name, param in merged.named_parameters():
                if "lora_B" in name:
                    param.fill_(0.05)
    adapter_dir.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(adapter_dir)


def _run_probe(base_dir, adapter_dir, timeout=240):
    """Run the real producer subprocess on cpu; return (rc, stdout, stderr)."""
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "eval_failclosed_probe.py"),
        "--base-model",
        str(base_dir),
        "--adapter",
        str(adapter_dir),
        "--device",
        "cpu",
        "--device-map",
        "",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


@pytest.fixture(scope="module")
def tiny_base(tmp_path_factory):
    base_dir = tmp_path_factory.mktemp("c0069") / "base"
    _save_tiny_base(base_dir)
    return base_dir


# ---------------------------------------------------------------- producer
def test_positive_canary_fires_both_markers(tiny_base, tmp_path):
    adapter = tmp_path / "adapter_live"
    _save_adapter(tiny_base, adapter, nonzero=True)
    rc, out, err = _run_probe(tiny_base, adapter)
    assert rc == 0, "producer rc=%d stderr=%s" % (rc, err[-800:])
    assert '"stage": "adapter_applied"' in out
    assert '"stage": "adapter_probe_differs"' in out
    assert APPLIED in out and PROBE_DIFFERS in out


def test_zero_adapter_fails_closed_without_markers(tiny_base, tmp_path):
    adapter = tmp_path / "adapter_zero"
    _save_adapter(tiny_base, adapter, nonzero=False)
    rc, out, err = _run_probe(tiny_base, adapter)
    assert rc != 0, f"inert adapter must not pass: stdout={out} stderr={err[-400:]}"
    assert APPLIED not in out
    assert PROBE_DIFFERS not in out


# -------------------------------------------------------------------- gate
def test_gate_passes_positive_and_suppresses_all_failures(tiny_base, tmp_path):
    adapter = tmp_path / "adapter_live"
    _save_adapter(tiny_base, adapter, nonzero=True)
    rc, out, _err = _run_probe(tiny_base, adapter)
    assert rc == 0 and PROBE_DIFFERS in out

    ok, reason = harness_lib.check_gate("eval-failclosed", out)
    assert ok, "gate must pass a real positive leg: " + reason

    rc0, zero_out, _err0 = _run_probe(tiny_base, tmp_path / "adapter_zero")
    assert rc0 != 0
    ok, _r = harness_lib.check_gate("eval-failclosed", zero_out)
    assert not ok, "gate must suppress an inert-adapter leg log"

    ok, _r = harness_lib.check_gate("eval-failclosed", "no markers here")
    assert not ok, "gate must suppress marker-less text"

    ok, _r = harness_lib.check_gate(
        "eval-failclosed", APPLIED + " " + PROBE_DIFFERS + " byte-identical"
    )
    assert not ok, "gate must suppress the byte-identical contradiction"

    ok, reason = harness_lib.check_gate("no-such-gate", "anything")
    assert not ok and "unknown gate" in reason


# ---------------------------------------------------------------- composer
def test_composer_marker_check_accepts_and_rejects(tmp_path):
    log = tmp_path / "leg.log"
    log.write_text("stage line\nLEG_FAILCLOSED " + APPLIED + " " + PROBE_DIFFERS + "\n")
    env = dict(adapter_applied_marker=True, adapter_probe_differs_marker=True)
    holdout_verdict._marker_check(env, "canary_leg", log)  # must not reject

    with pytest.raises(holdout_verdict.VerdictRejected) as exc_missing:
        holdout_verdict._marker_check(dict(), "canary_leg", log)
    assert "adapter_applied_marker" in str(exc_missing.value)

    log_bad = tmp_path / "leg_uncorroborated.log"
    log_bad.write_text("nothing to see\n")
    with pytest.raises(holdout_verdict.VerdictRejected) as exc_uncorr:
        holdout_verdict._marker_check(env, "canary_leg", log_bad)
    assert "adapter_applied" in str(exc_uncorr.value)  # gate-safe underscore name
    assert APPLIED not in str(exc_uncorr.value)  # never the hyphenated token


# --------------------------------------------------------------- smoke gate
def test_smoke_gate_pass_and_fail_shapes():
    gate = qg_smoke_gate_lora_v2
    good = dict(
        adapter_applied_marker="ADAPTER_APPLIED",
        adapter_dir="/tmp/adapter",
        tasks=[
            dict(task_id="t1", probe_differs=True),
            dict(task_id="t2", probe_differs=False),
            dict(task_id="t3", probe_differs=False),
        ],
    )
    verdict, reasons = gate.decide(good)
    assert verdict == gate.SMOKE_PASS and reasons == []

    bad = dict(adapter_applied_marker=None, adapter_dir="", tasks=[])
    verdict, reasons = gate.decide(bad)
    assert verdict == gate.SMOKE_FAIL
    assert any("marker" in r for r in reasons)
    assert any("adapter_dir" in r for r in reasons)

    verdict, reasons = gate.decide("not a dict")
    assert verdict == gate.SMOKE_FAIL

    zero_diff = dict(good, tasks=[dict(task_id=t, probe_differs=False) for t in "abc"])
    verdict, reasons = gate.decide(zero_diff)
    assert verdict == gate.SMOKE_FAIL
    assert any("0/3" in r for r in reasons)


def test_positive_stdout_is_self_consistent_json_stage_markers(tiny_base, tmp_path):
    """The stage events must be parseable JSON lines (runner contract)."""
    adapter = tmp_path / "adapter_live"
    _save_adapter(tiny_base, adapter, nonzero=True)
    rc, out, _err = _run_probe(tiny_base, adapter)
    assert rc == 0
    stages = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith(chr(123)):
            stages.append(json.loads(line)["stage"])
    assert "adapter_applied" in stages
    assert "adapter_probe_differs" in stages
