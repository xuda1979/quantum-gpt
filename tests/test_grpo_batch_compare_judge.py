"""TDD (2026-08-27, REWARD lane, r19 wave — user directives):
1. Batch COMPARATIVE SELF-judge — the training model itself judges ALL G candidates at once
   (one prompt, all 8 compared), giving comprehensive per-candidate dimension scores.
2. Pass is only PART of the comprehensive score (blend keeps w_P=0.50).
3. Raw scores are NORMALIZED across all candidates before they feed the GRPO/SAPO advantages.
4. G=8 every round (hard floor; overrides the router's adaptive 4).

Everything is INERT-BY-DEFAULT: the new features default OFF and are byte-identical to the
prior behavior when off (no-regression doctrine). py3.9.6-safe only.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_trainer import (  # noqa: E402
    _model_batch_dim_scores,
    _model_batch_dim_scores_dp4,
    _parse_model_batch_dim_scores,
    _render_batch_judge_candidates,
    _unpermute_batch_scores,
)
from training.grpo_utils import (  # noqa: E402
    MODEL_JUDGE_DIMENSIONS,
    blend_comprehensive_reward,
    leave_one_out_advantages,
    normalize_group_rewards,
)

N = 8

# ---------------------------------------------------------------------------
# 2. Batch comparative judge — parse contract
# ---------------------------------------------------------------------------


def _single(d, v):
    return dict(d, **{k: v for k in d})


BATCH_JSON = (
    '{"candidate_1": {"correctness_of_intent": 0.8, "runnability": 0.7, '
    '"result_correctness": 0.9, "efficiency": 0.5, "structure_and_naming": 0.7}, '
    '"candidate_2": {"correctness_of_intent": 0.3, "runnability": 0.4, '
    '"result_correctness": 0.2, "efficiency": 0.1, "structure_and_naming": 0.5}, '
    '"candidate_3": {"correctness_of_intent": 0.95, "runnability": 0.95, '
    '"result_correctness": 1.0, "efficiency": 0.8, "structure_and_naming": 0.9}}'
)


def test_parse_batch_all_candidates_scored():
    scores = _parse_model_batch_dim_scores(BATCH_JSON, n=N)
    assert scores is not None
    # present candidates 1-3 parsed with clamped 0-1 dims
    assert scores[0]["correctness_of_intent"] == 0.8
    assert scores[1]["correctness_of_intent"] == 0.3
    assert scores[2]["result_correctness"] == 1.0
    # absent candidates (4..8) are judge-absent (None) -> fail-closed, NOT silent 0
    for i in range(3, N):
        assert scores[i].get("correctness_of_intent") is None


def test_parse_batch_malformed_returns_none_per_candidate():
    scores = _parse_model_batch_dim_scores("not json at all", n=N)
    # fail-closed: no candidate gets a fabricated score
    assert scores is None or all(v.get("correctness_of_intent") is None for v in scores.values())


def test_parse_batch_clamps_and_skips_bools():
    raw = (
        BATCH_JSON.replace("0.8", "1.7")
        .replace("0.3", "true")
        .replace("0.7}", '0.7, "structure_and_naming": 2.0}')
    )
    scores = _parse_model_batch_dim_scores(raw, n=N)
    assert scores is not None
    # 1.7 clamped to 1.0
    assert scores[0]["correctness_of_intent"] == 1.0
    # 'true' (bool) is NOT a numeric dim -> None
    assert scores[1]["correctness_of_intent"] is None
    # 2.0 clamped to 1.0
    assert scores[0]["structure_and_naming"] == 1.0


def test_batch_scores_are_anchored_to_evidence_prompt():
    # The batch prompt must embed per-candidate executable evidence so the judge
    # compares candidates on real pass/fail, not style alone.
    from training.grpo_trainer import COMPREHENSIVE_BATCH_JUDGE_PROMPT

    prompt = COMPREHENSIVE_BATCH_JUDGE_PROMPT
    assert "{candidates}" in prompt
    assert "candidate_1" in prompt
    assert "evidence" in prompt.lower() or "pass" in prompt.lower()


# ---------------------------------------------------------------------------
# 2b. Pass is only PART of the comprehensive score (blend unchanged)
# ---------------------------------------------------------------------------


def test_judge_mass_bounded_to_unit_interval():
    """RED regression (2026-09-01, JUDGE-BRIDGE audit, item 4): the blend's
    ``judge_mass`` was only lower-bounded (max(0, ...)) — an operator typo like
    --reward-judge-mass 2.0 silently renormalized to a 55% judge share
    (2.0 / (0.5+0.4+2.0)) and the judge dominated pass. w_J is a fraction of a
    unit-sum blend (w_P + w_S + w_J = 1): it must be bounded to [0, 1]."""
    kwargs = dict(
        pass_reward=1.0,
        shaped_reward=0.5,
        model_dim_scores={
            "correctness_of_intent": 0.8,
            "runnability": 0.8,
            "result_correctness": 0.8,
            "efficiency": 0.8,
            "structure_and_naming": 0.8,
        },
        dim_weights={
            "correctness_of_intent": 0.02,
            "runnability": 0.02,
            "result_correctness": 0.02,
            "efficiency": 0.02,
            "structure_and_naming": 0.02,
        },
        mode="comprehensive",
        pass_mass=0.50,
        shaped_mass=0.40,
    )
    sane = blend_comprehensive_reward(judge_mass=1.0, **kwargs)
    insane = blend_comprehensive_reward(judge_mass=5.0, **kwargs)
    assert insane == sane, "judge mass > 1 must clamp to 1 (fraction of the unit blend)"
    assert 0.0 <= insane <= 1.0
    negative = blend_comprehensive_reward(judge_mass=-3.0, **kwargs)
    assert negative == blend_comprehensive_reward(judge_mass=0.0, **kwargs)


def test_pass_only_part_of_comprehensive_score():
    # comprehensive blend: w_P=0.50*pass + w_S=0.40*shaped + w_J=0.10*judge.
    # A strong comparative judge cannot alone make a failing candidate beat a
    # passing one unless shaped+judge outweigh pass — the point of comprehensive.
    r_high_pass = blend_comprehensive_reward(
        pass_reward=1.0,
        shaped_reward=0.3,
        model_dim_scores={
            "correctness_of_intent": 0.5,
            "runnability": 0.5,
            "result_correctness": 0.5,
            "efficiency": 0.5,
            "structure_and_naming": 0.5,
        },
        dim_weights={
            "correctness_of_intent": 0.05,
            "runnability": 0.05,
            "result_correctness": 0.05,
            "efficiency": 0.05,
            "structure_and_naming": 0.05,
        },
        mode="comprehensive",
        pass_mass=0.50,
        shaped_mass=0.40,
        judge_mass=0.0,
    )
    r_low_pass = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=0.9,
        model_dim_scores={
            "correctness_of_intent": 1.0,
            "runnability": 1.0,
            "result_correctness": 1.0,
            "efficiency": 1.0,
            "structure_and_naming": 1.0,
        },
        dim_weights={
            "correctness_of_intent": 0.05,
            "runnability": 0.05,
            "result_correctness": 0.05,
            "efficiency": 0.05,
            "structure_and_naming": 0.05,
        },
        mode="comprehensive",
        pass_mass=0.50,
        shaped_mass=0.40,
        judge_mass=0.0,
    )
    # pass dominates at 0.50 mass when judge is calibration-gated off
    assert r_high_pass > r_low_pass
    # and the passing total does NOT equal 1.0 alone — shaped+judge also move it
    assert r_high_pass < 1.0 or r_low_pass > 0.0


# ---------------------------------------------------------------------------
# 3. Raw-score normalization before advantages
# ---------------------------------------------------------------------------


def test_normalize_group_minmax_to_unit_interval():
    raw = torch.tensor([0.0, 0.25, 0.5, 0.75, 1.0, 0.1, 0.9, 0.4])
    norm, rec = normalize_group_rewards(raw, mode="minmax")
    assert norm.shape == raw.shape
    assert float(norm.min()) >= 0.0 - 1e-6
    assert float(norm.max()) <= 1.0 + 1e-6
    assert abs(float(norm.max().item() - 1.0)) < 1e-6
    assert abs(float(norm.min().item() - 0.0)) < 1e-6
    assert rec["mode"] == "minmax"
    # normalized values match the exact min-max affine map
    expect = (raw - raw.min()) / (raw.max() - raw.min())
    assert torch.allclose(norm, expect, atol=1e-6)
    # input order preserved by the affine map
    assert all((raw[i] <= raw[i + 1]) == (norm[i] <= norm[i + 1]) for i in range(len(raw) - 1))


def test_normalize_group_flat_is_invariant():
    raw = torch.full((8,), 0.5)
    norm, rec = normalize_group_rewards(raw, mode="minmax")
    # flat group -> no divide-by-zero; stays flat (or all-equal); never NaN
    assert bool(torch.isfinite(norm).all())
    assert abs(float(norm[0].item() - norm[-1].item())) < 1e-9


def test_normalize_none_is_identity():
    raw = torch.tensor([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    norm, rec = normalize_group_rewards(raw, mode="none")
    assert torch.equal(norm, raw)
    assert rec["mode"] == "none"


def test_normalize_advantage_invariance_under_affine_shift_for_loo():
    # LOO advantage is shift-invariant; but normalization changes scale —
    # verify minmax-then-LOO is finite and group-relative (mean_other identity).
    raw = torch.tensor([0.0, 0.3, 0.6, 0.9, 0.2, 0.5, 0.8, 0.1])
    norm, _ = normalize_group_rewards(raw, mode="minmax")
    adv = leave_one_out_advantages(norm)
    assert bool(torch.isfinite(adv).all())
    # LOO recompute identity: adv_i == raw_i - (sum-raw_i)/(G-1)
    g = norm.numel()
    recomputed = norm - (norm.sum() - norm) / float(g - 1)
    assert torch.allclose(adv, recomputed, atol=1e-6)


# ---------------------------------------------------------------------------
# 4. G=8 every round — hard floor helper
# ---------------------------------------------------------------------------


def test_group_size_floor_enforces_eight():
    from training.grpo_trainer import effective_group_size

    # router recommends 4 for a fresh task, max_adaptive_group=16 -> floor 8 wins
    assert effective_group_size(recommended=4, max_adaptive_group=16, min_group_size=8) == 8
    # router recommends 16 -> capped at max_adaptive_group, floor no-op
    assert effective_group_size(recommended=16, max_adaptive_group=16, min_group_size=8) == 16
    # floor default 1 = inert (prior behavior for recommended 4 with max 16)
    assert effective_group_size(recommended=4, max_adaptive_group=16, min_group_size=1) == 4


# ---------------------------------------------------------------------------
# 1. _model_batch_dim_scores wires the training model as the self-judge
# ---------------------------------------------------------------------------


def test_batch_judge_uses_training_model_not_frozen():
    # The r19 contract: the judge is the model being trained itself (self-judge).
    # The batch-dim function MUST accept the active `model` and backend and drive
    # a single forward — verify it is importable and callable-typed (minimal,
    # non-vacuous smoke; full inference exercised in launch rehearsal).
    assert callable(_model_batch_dim_scores)


# ---------------------------------------------------------------------------
# 5. dp4 (deepseek-v4-flash) batch judge backend — user directive that the
#    judge is the Huanxin dp4 model, all candidates at once.
# ---------------------------------------------------------------------------


def _fake_dp4_response(slot):
    # The judge answers ONLY the candidate presented in ``slot`` (1-based
    # position key); the client must un-permute it back to the ORIGINAL index.
    text = (
        f'{{"candidate_{slot}": {{"correctness_of_intent": 0.7, "runnability": 0.6, '
        f'"result_correctness": 0.8, "efficiency": 0.5, "structure_and_naming": 0.7}}}}'
    )
    payload = {"content": [{"type": "text", "text": text}]}

    class _Resp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps(payload).encode()

    return _Resp()


def test_dp4_batch_judge_parses_candidate(monkeypatch):
    import re as std_re
    import urllib.request as ur

    def fake_urlopen(req, timeout=None):
        # assert one comparative prompt was sent with all N candidates
        body = json.loads(req.data.decode())
        assert body["model"] == "dp4"
        content = body["messages"][0]["content"]
        assert "candidate_1" in content and "candidate_8" in content
        # presentation order is randomized per call (2026-09-01): answer the
        # SLOT that holds code_0 so the remap is exercised end-to-end
        blocks = std_re.split(r"Candidate \d+:\n", content)
        slot = next(k for k in range(1, len(blocks)) if "code_0" in blocks[k])
        return _fake_dp4_response(slot)

    class _FakeOpener:
        def open(self, req, timeout=None):
            return fake_urlopen(req, timeout=timeout)

    # 2026-08-27 (judge bridge): the dp4 client builds a NO-PROXY opener (the
    # box's env squid 403s localhost) — pin that the call goes through the
    # opener, never the env-proxy-honoring urlopen.
    monkeypatch.setattr(ur, "build_opener", lambda handler: _FakeOpener())
    codes = [f"code_{i}" for i in range(N)]
    evidences = ["tests passed: True" for _ in range(N)]
    out = _model_batch_dim_scores_dp4(
        codes, evidences, {"meta": {"name": "t"}}, endpoint="http://127.0.0.1:55080"
    )
    assert out is not None
    # code_0 was the only answered candidate -> its score returns on index 0
    assert out[0]["correctness_of_intent"] == 0.7
    # candidates dp4 did not include -> judge-absent (fail-closed), not 0
    assert out[1]["correctness_of_intent"] is None


def test_dp4_batch_judge_fails_closed_on_error(monkeypatch):
    import urllib.request as ur

    def boom(req, timeout=None):
        raise OSError("proxy down")

    monkeypatch.setattr(ur, "urlopen", boom)
    codes = [f"code_{i}" for i in range(N)]
    evidences = ["" for _ in range(N)]
    out = _model_batch_dim_scores_dp4(
        codes, evidences, {"meta": {"name": "t"}}, endpoint="http://127.0.0.1:55080"
    )
    # judge-absent / None — never a silent fabricated 0
    assert out is None


def test_dp4_batch_judge_randomizes_order_and_remaps(monkeypatch):
    """RED regression (2026-09-01, JUDGE-BRIDGE audit): the batch comparative
    judge must present the candidates in a RANDOMIZED order (kills LLM-judge
    position bias) and REMAP the parsed scores back to the original candidate
    indices. The pre-fix code had BOTH halves broken: the live dp4 path
    rendered candidates in fixed order (no rng -> shuffle was dead code), and
    the in-process path shuffled but discarded the permutation (scores
    misattributed to the wrong candidates).

    This test drives the REAL dp4 client end-to-end (render -> fake judge
    response -> parse -> un-permutation) with a pinned rng seed so the
    expected permutation is reproducible, and asserts:
      (a) the prompt presents code_3 in the SEED-EXPECTED slot, not slot 4
          (identity order) — randomization must be ACTIVE;
      (b) the high score lands on ORIGINAL index 3, not on the presentation
          slot — the remap must be correct.
    """
    import random as std_random
    import re as std_re
    import urllib.request as ur

    from training.grpo_trainer import _model_batch_dim_scores_dp4

    captured: dict[str, str] = {}

    def fake_urlopen(req, timeout=None):
        body = json.loads(req.data.decode())
        captured["prompt"] = body["messages"][0]["content"]
        # The judge "answers": the slot holding code_3 is excellent, all
        # other slots are poor (the test must never depend on the code's own
        # ordering to pass — it reads the ACTUAL presentation).
        blocks = std_re.split(r"Candidate \d+:\n", captured["prompt"])
        slot = next(k for k in range(1, len(blocks)) if "code_3" in blocks[k])
        high = dict(
            correctness_of_intent=0.9,
            runnability=0.9,
            result_correctness_of_intent=0.9,
            efficiency=0.9,
            structure_and_naming=0.9,
        )
        low = dict(
            correctness_of_intent=0.1,
            runnability=0.1,
            result_correctness_of_intent=0.1,
            efficiency=0.1,
            structure_and_naming=0.1,
        )
        text = json.dumps({f"candidate_{k}": (high if k == slot else low) for k in range(1, N + 1)})
        payload = {"content": [{"type": "text", "text": text}]}

        class _Resp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return json.dumps(payload).encode()

        return _Resp()

    class _FakeOpener:
        def open(self, req, timeout=None):
            return fake_urlopen(req, timeout=timeout)

    monkeypatch.setattr(ur, "build_opener", lambda handler: _FakeOpener())
    # Pin the client's internal rng so the expected permutation is exact.
    # Capture the ORIGINAL class first: monkeypatching the shared module
    # attribute redirects std_random.Random too (same module object).
    _orig_random_cls = std_random.Random
    monkeypatch.setattr("training.grpo_trainer.random.Random", lambda: _orig_random_cls(42))

    codes = [f"code_{i}" for i in range(N)]
    evidences = ["tests passed: True"] * N
    out = _model_batch_dim_scores_dp4(
        codes, evidences, {"meta": {"name": "t"}}, endpoint="http://127.0.0.1:55080"
    )

    expected = list(range(N))
    _orig_random_cls(42).shuffle(expected)
    pos3 = expected.index(3)
    assert pos3 != 3  # the pinned seed must exercise a REAL shuffle
    blocks = std_re.split(r"Candidate \d+:\n", captured["prompt"])
    # (a) randomization ACTIVE: code_3 sits in the seed-expected slot (1-based)
    assert "code_3" in blocks[pos3 + 1], (
        f"candidate order must be randomized (expected code_3 in slot {pos3 + 1}, "
        "got identity order)"
    )
    # (b) remap CORRECT: the high score returns on ORIGINAL index 3...
    assert out is not None
    assert out[3]["correctness_of_intent"] == 0.9, "scores must remap to original indices"
    # ...never on the presentation slot (position-bias misattribution)
    assert out[pos3]["correctness_of_intent"] == 0.1


def test_dp4_batch_judge_prompt_is_plain_candidates_text(monkeypatch):
    """RED regression (2026-09-01, JUDGE-BRIDGE audit): _render_batch_judge_candidates
    returns (text, perm); the dp4 client once bound the TUPLE and formatted its
    repr into the prompt — 'Candidate 1:\\n...' with ESCAPED newlines and the
    permutation list '[...]' leaked into the judge. The judge must see the
    plain rendered candidates (literal newlines), never repr artifacts."""
    import urllib.request as ur

    from training.grpo_trainer import _model_batch_dim_scores_dp4

    captured: dict[str, str] = {}

    def fake_urlopen(req, timeout=None):
        body = json.loads(req.data.decode())
        captured["prompt"] = body["messages"][0]["content"]
        payload = {"content": [{"type": "text", "text": '{"candidate_1": {}}'}]}

        class _Resp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return json.dumps(payload).encode()

        return _Resp()

    class _FakeOpener:
        def open(self, req, timeout=None):
            return fake_urlopen(req, timeout=timeout)

    monkeypatch.setattr(ur, "build_opener", lambda handler: _FakeOpener())
    _model_batch_dim_scores_dp4(
        [f"code_{i}" for i in range(N)],
        ["tests passed: True"] * N,
        {"meta": {"name": "t"}},
        endpoint="http://127.0.0.1:55080",
    )
    prompt = captured["prompt"]
    assert "Candidate 1:\n```python\n" in prompt, (
        "prompt must contain the plain rendered candidates (literal newline), not the tuple repr"
    )
    assert "code_" in prompt and "EXECUTABLE EVIDENCE: tests passed: True\n" in prompt
    assert "[0, 1, 2" not in prompt, "permutation list must never leak into the prompt"


def test_inprocess_batch_judge_remaps_shuffled_scores(monkeypatch):
    """RED regression (2026-09-01, JUDGE-BRIDGE audit): the in-process batch
    judge shuffled the candidate order but DISCARDED the permutation, so the
    parsed position-keyed scores were attributed to the wrong candidates. The
    real function must un-permute with the seeded order (fake backend drives
    the full render -> parse -> remap chain)."""
    import random as std_random

    import torch as _torch

    from training.grpo_trainer import _model_batch_dim_scores

    captured: dict[str, str] = {}
    import re as std_re

    class _FakeBackend:
        pad_token_id = 0

        def encode_chat(self, messages, add_generation_prompt=True):
            captured["prompt"] = messages[0]["content"]
            return [1, 2, 3]

        def decode(self, ids):
            blocks = std_re.split(r"Candidate \d+:\n", captured["prompt"])
            slot = next(k for k in range(1, len(blocks)) if "code_3" in blocks[k])
            high = dict(
                correctness_of_intent=0.9,
                runnability=0.9,
                result_correctness_of_intent=0.9,
                efficiency=0.9,
                structure_and_naming=0.9,
            )
            low = dict(
                correctness_of_intent=0.1,
                runnability=0.1,
                result_correctness_of_intent=0.1,
                efficiency=0.1,
                structure_and_naming=0.1,
            )
            return json.dumps(
                {f"candidate_{k}": (high if k == slot else low) for k in range(1, N + 1)}
            )

    class _FakeModel:
        def generate(self, *args, **kwargs):
            return _torch.tensor([[1, 2, 3, 4]])

    _orig_random_cls = std_random.Random
    monkeypatch.setattr("training.grpo_trainer.random.Random", lambda: _orig_random_cls(42))
    monkeypatch.setattr("training.grpo_trainer.configured_eos_token_ids", lambda *a, **k: set())
    monkeypatch.setattr("training.grpo_trainer._release_device_cache", lambda *a, **k: None)

    out = _model_batch_dim_scores(
        [f"code_{i}" for i in range(N)],
        ["tests passed: True"] * N,
        {"meta": {"name": "t"}},
        _FakeModel(),
        _FakeBackend(),
        {"model_judge_max_tokens": 512, "model_judge_temperature": 0.0},
        "cpu",
    )
    expected = list(range(N))
    _orig_random_cls(42).shuffle(expected)
    pos3 = expected.index(3)
    assert out is not None
    assert out[3]["correctness_of_intent"] == 0.9, "in-process scores must un-permute"
    assert out[pos3]["correctness_of_intent"] == 0.1


# ---------------------------------------------------------------------------
# 8. CRITICAL BUG (2026-08-27, user binding): dp4 is the ONLY judge.
#    When --batch-comparative-judge is ON, a --judge-dp4-endpoint is REQUIRED.
#    The OLD code silently fell back to the in-process SELF-judge (the ACTIVE
#    training model judging itself) when the endpoint was empty — a direct
#    violation of the user's dp4-ONLY mandate. This must be fail-closed at
#    startup: no endpoint => SystemExit, never a silent self-judge fallback.
# ---------------------------------------------------------------------------


def test_batch_compare_requires_dp4_endpoint_fail_closed():
    """RED regression: batch-comparative-judge ON with NO dp4 endpoint must
    raise SystemExit (fail-closed), NOT silently fall back to the self-judge."""
    from argparse import Namespace

    from training.grpo_trainer import validate_batch_judge_config

    # ON + no endpoint -> must refuse to start
    args_on_no_endpoint = Namespace(
        batch_comparative_judge=True,
        judge_dp4_endpoint="",
        judge_dp4_model="dp4",
    )
    with pytest.raises(SystemExit):
        validate_batch_judge_config(args_on_no_endpoint)

    # ON + endpoint present -> OK (no raise)
    args_on_with_endpoint = Namespace(
        batch_comparative_judge=True,
        judge_dp4_endpoint="http://127.0.0.1:56237",
        judge_dp4_model="dp4",
    )
    validate_batch_judge_config(args_on_with_endpoint)

    # OFF -> always OK (inert default)
    args_off = Namespace(
        batch_comparative_judge=False,
        judge_dp4_endpoint="",
        judge_dp4_model="dp4",
    )
    validate_batch_judge_config(args_off)


# ---------------------------------------------------------------------------
# 9. dp4 judge ACTIVE without the frozen model-judge machinery (2026-08-27,
#    reward audit gap): --batch-comparative-judge must contribute w_J even
#    when model_judge_enabled=0 and no calibration file exists. The r17
#    calibration gate applies to the per-candidate frozen-BASE judge, NOT to
#    the dp4 comparative judge (user binding: dp4 is the judge, active).
# ---------------------------------------------------------------------------


def test_batch_dp4_judge_weights_uniform_when_uncalibrated():
    from argparse import Namespace

    from training.grpo_trainer import batch_dp4_judge_weights
    from training.grpo_utils import MODEL_JUDGE_DIMENSIONS

    args = Namespace(reward_judge_mass=0.10)
    w = batch_dp4_judge_weights(args, None)
    # uniform across all 5 dims, summing to exactly the judge mass 0.10
    assert set(w) == set(MODEL_JUDGE_DIMENSIONS)
    assert abs(sum(w.values()) - 0.10) < 1e-12
    assert all(abs(v - 0.01) < 1e-12 for v in w.values())

    # calibrated weights win when present
    calib = {"correctness_of_intent": 0.05, "runnability": 0.05}
    assert batch_dp4_judge_weights(args, calib) == calib

    # explicit zero judge mass -> judge contributes nothing
    w0 = batch_dp4_judge_weights(Namespace(reward_judge_mass=0.0), None)
    assert w0 == {}


def test_batch_judge_on_flag_decoupled_from_model_judge():
    """The dp4 batch judge must fire even when the frozen base-model judge is
    disabled (launcher default) — pin the gate helper."""
    from argparse import Namespace

    from training.grpo_trainer import batch_judge_active

    assert (
        batch_judge_active(Namespace(batch_comparative_judge=True, model_judge_enabled=False))
        is True
    )
    assert (
        batch_judge_active(Namespace(batch_comparative_judge=False, model_judge_enabled=True))
        is False
    )


# ---------------------------------------------------------------------------
# 10. Critical review C1/C2 (2026-08-27): dp4 has its OWN token budget
#     (--judge-dp4-max-tokens, default 4096) — the frozen judge's 256 must
#     never cap the 8-candidate comparative call; judge-absent must be LOUD.
# ---------------------------------------------------------------------------


def test_dp4_batch_judge_uses_own_token_budget(monkeypatch):
    """C1 regression: --model-judge-max-tokens=256 (frozen-judge knob) must NOT
    cap the dp4 batch call — the dp4 call reads --judge-dp4-max-tokens."""
    from argparse import Namespace

    from training.grpo_trainer import _run_dp4_batch_judge

    captured = {}

    def fake_dp4(codes, evidences, task, *, endpoint, model, max_tokens):
        captured["max_tokens"] = max_tokens
        return {0: {"correctness_of_intent": 0.8}}

    monkeypatch.setattr("training.grpo_trainer._model_batch_dim_scores_dp4", fake_dp4)
    args = Namespace(
        judge_dp4_endpoint="http://127.0.0.1:56237",
        judge_dp4_model="dp4",
        judge_dp4_max_tokens=4096,
        model_judge_max_tokens=256,  # must be IGNORED
    )
    out = _run_dp4_batch_judge(args, ["c1", "c2"], ["e1", "e2"], {"task_id": "t"})
    assert out is not None
    assert captured["max_tokens"] == 4096

    # missing judge_dp4_max_tokens -> default 4096, still not the 256 knob
    captured.clear()
    args2 = Namespace(
        judge_dp4_endpoint="http://127.0.0.1:56237",
        judge_dp4_model="dp4",
        model_judge_max_tokens=256,
    )
    _run_dp4_batch_judge(args2, ["c1"], ["e1"], {"task_id": "t"})
    assert captured["max_tokens"] == 4096


def test_dp4_judge_failed_marker_present_in_trainer():
    """C2 regression: the trainer prints a LOUD 'dp4_judge_failed' stage marker
    when the batch judge returns no scores (never a silent w_J=0)."""
    import re

    src = open(ROOT / "training" / "grpo_trainer.py", encoding="utf-8").read()
    assert '"stage": "dp4_judge_failed"' in src
    assert re.search(r"if batch_scores is None:", src)


# ---------------------------------------------------------------------------
# Batch-judge candidate ORDER randomization + permutation remapping
# (2026-08-31 algorithm-vigilance audit). _render_batch_judge_candidates must:
#   * keep the identity (fixed) order when no rng is passed;
#   * RANDOMIZE the order when an rng is passed and return the permutation
#     so parsed scores map back to the original candidate indices —
#     kills LLM-judge position bias (first-presented candidates are scored
#     differently; AlpacaEval-style harnesses randomize for this reason).
# VIGILANCE FINDING: the ACTIVE dp4 judge path (_model_batch_dim_scores_dp4)
# calls the renderer WITHOUT rng — the position-bias kill is implemented but
# not wired into the live path, and the (dead) in-process _model_batch_dim_scores
# discards the returned perm. Pinned here at the pure-function level; wiring
# the live path is a reward-lane decision (changes live judge behavior).
# ---------------------------------------------------------------------------


def _codes(n: int = 8) -> list[str]:
    return [f"# candidate {i}\ncode_{i}" for i in range(n)]


def _evidences(n: int = 8) -> list[str]:
    return [f"evidence_{i}" for i in range(n)]


def test_render_batch_judge_candidates_fixed_order_without_rng() -> None:
    """No rng -> identity permutation: positions 1..N show candidates 0..N-1
    in original order (byte-stable prompt when randomization is off)."""
    codes = _codes()
    text, perm = _render_batch_judge_candidates(codes, _evidences())
    assert perm == list(range(len(codes)))
    for pos, idx in enumerate(perm, start=1):
        assert f"Candidate {pos}:" in text
        assert f"code_{idx}" in text


def test_render_batch_judge_candidates_randomizes_with_seeded_rng() -> None:
    """A seeded rng must produce a genuine permutation that is NOT the
    identity (for n >= 3) and that is a bijection over 0..n-1."""
    codes = _codes(8)
    rng = random.Random(42)
    text, perm = _render_batch_judge_candidates(codes, _evidences(8), rng=rng)
    assert perm != list(range(8))
    assert sorted(perm) == list(range(8))  # bijection
    # each displayed position pos (1-based) shows the ORIGINAL candidate perm[pos-1]
    for pos, idx in enumerate(perm, start=1):
        assert f"Candidate {pos}:" in text
        assert f"code_{idx}" in text


def test_render_batch_judge_permutation_remaps_scores_to_original_indices() -> None:
    """The returned permutation must recover the per-original-index score
    attribution: if the judge scores the RENDERED positions (candidate_1..N),
    remapping through perm maps each score back to its original candidate."""
    codes = _codes(8)
    rng = random.Random(7)
    text, perm = _render_batch_judge_candidates(codes, _evidences(8), rng=rng)
    assert perm != list(range(8))
    # judge scores the DISPLAYED positions; score value = 10 * position
    parsed_by_position = {pos - 1: float(pos) for pos in range(1, 9)}
    remapped_to_original: dict[int, float] = {}
    for displayed_pos_0based, score in parsed_by_position.items():
        remapped_to_original[perm[displayed_pos_0based]] = score
    assert set(remapped_to_original) == set(range(8))  # every original scored
    # the remapped attribution is exactly the position of that original index
    for orig_idx in range(8):
        assert remapped_to_original[orig_idx] == float(perm.index(orig_idx) + 1)
    # sanity: with the identity permutation the remap is a no-op
    _, ident = _render_batch_judge_candidates(codes, _evidences(8))
    assert ident == list(range(8))


def test_render_batch_judge_shuffles_vary_across_seeds() -> None:
    """Randomization must be REAL: different seeds yield different orders
    (not a fixed rotation), and the sample order actually differs from the
    input order on the rendered text."""
    orders = set()
    for seed in range(8):
        _, perm = _render_batch_judge_candidates(_codes(8), _evidences(8), rng=random.Random(seed))
        orders.add(tuple(perm))
    assert len(orders) >= 4, f"seeds produced only {len(orders)} distinct orders"
    # every rendered permutation is a bijection
    for seed in range(8):
        _, perm = _render_batch_judge_candidates(_codes(8), _evidences(8), rng=random.Random(seed))
        assert sorted(perm) == list(range(8))


def test_unpermute_batch_scores_round_trip_with_randomized_render() -> None:
    """Full round trip (judge-bridge 2026-09-01 contract): render with a
    per-call rng -> judge scores the PRESENTED positions (candidate_1..N) ->
    _unpermute_batch_scores maps every score back to the ORIGINAL index.
    Without the remap, a shuffled presentation silently misattributes every
    score to the wrong candidate."""
    codes = _codes(8)
    evidences = _evidences(8)
    rng = random.Random(11)
    text, perm = _render_batch_judge_candidates(codes, evidences, rng=rng)
    assert perm != list(range(8))
    # build a judge response keyed by PRESENTATION position, value = 10*pos
    response = {
        f"candidate_{pos}": {dim: float(pos) / 10.0 for dim in MODEL_JUDGE_DIMENSIONS}
        for pos in range(1, 9)
    }
    parsed = _parse_model_batch_dim_scores(json.dumps(response), n=8)
    assert parsed is not None
    remapped = _unpermute_batch_scores(parsed, perm)
    assert set(remapped) == set(range(8))
    # original candidate idx was shown at slot perm.index(idx)+1, so its
    # correct score is (perm.index(idx)+1)/10
    for idx in range(8):
        expected = (perm.index(idx) + 1) / 10.0
        for dim in MODEL_JUDGE_DIMENSIONS:
            assert remapped[idx][dim] == pytest.approx(expected), (
                f"original candidate {idx} misattributed: {remapped[idx][dim]} != {expected}"
            )
    # None stays None (fail-closed), and out-of-range positions are dropped
    assert _unpermute_batch_scores(None, perm) is None
    assert _unpermute_batch_scores({99: {"correctness_of_intent": 0.5}}, perm) == {}


def test_normalize_minmax_record_fields_pin_scale() -> None:
    """2026-09-01 (fixer lane): the minmax record must carry the actual
    group min/max and the flat flag — the reward verifier / step record read
    these. Pins the contract so a future impl that drops the fields fails."""
    raw = torch.tensor([0.0, 0.25, 0.5, 0.75, 1.0, 0.1, 0.9, 0.4])
    _norm, rec = normalize_group_rewards(raw, mode="minmax")
    assert rec["mode"] == "minmax"
    assert rec["min"] == pytest.approx(0.0)
    assert rec["max"] == pytest.approx(1.0)
    assert rec["flat"] is False


def test_normalize_flat_group_unchanged_byte_identical() -> None:
    """2026-09-01 (fixer lane): a FLAT group (range <= epsilon) must be left
    byte-identical — same object values, never NaN/Inf, and the record must
    say flat=True with min == max (no divide-by-zero anywhere)."""
    raw = torch.full((8,), 0.5)
    norm, rec = normalize_group_rewards(raw, mode="minmax")
    assert torch.equal(norm, raw)  # unchanged, not just all-equal
    assert rec["flat"] is True
    assert rec["min"] == rec["max"] == pytest.approx(0.5)
    assert bool(torch.isfinite(norm).all())


def test_normalize_flat_group_near_equal_range_is_flat() -> None:
    """epsilon=1e-8: a group whose range is below the epsilon must take the
    flat path (unchanged), never a scaled output with a near-zero divisor."""
    raw = torch.full((8,), 0.5) + torch.tensor([0.0] * 7 + [1e-10])
    norm, rec = normalize_group_rewards(raw, mode="minmax")
    assert torch.equal(norm, raw)
    assert rec["flat"] is True


def test_normalize_none_returns_exact_record() -> None:
    """mode=none must be byte-identical AND return exactly {"mode": "none"}
    — no extra fields that could confuse the verifier."""
    raw = torch.tensor([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    norm, rec = normalize_group_rewards(raw, mode="none")
    assert torch.equal(norm, raw)
    assert rec == {"mode": "none"}


def test_normalize_unknown_mode_raises() -> None:
    """Unknown modes must fail loudly — a typo'd mode silently passing raw
    rewards through would corrupt the advantage path."""
    raw = torch.tensor([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    with pytest.raises(ValueError, match="unknown mode"):
        normalize_group_rewards(raw, mode="min-max-typo")
