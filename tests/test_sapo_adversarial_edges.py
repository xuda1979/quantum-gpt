"""Adversarial edge cases on the SAPO critical path (2026-08-24 bug-hunt).

Empty candidates, zero-token completions, NaN advantages, EOS-only outputs:
each must degrade gracefully (no crash, no silent corruption) and the
flat-group gate must behave deterministically.

2026-09-01 (ADVERSARIAL-JUDGE lane): judge-reward path must not be gameable,
position-biased, or reward-collapsing — see the section at the bottom.
"""

from __future__ import annotations

import json
import random
import re
import types

import pytest
import torch

from training import grpo_trainer
from training.grpo_utils import (
    FRONTIER_RL,
    MODEL_JUDGE_DIMENSIONS,
    blend_comprehensive_reward,
    policy_update_signal_magnitude,
    should_queue_flat_all_fail,
)


class _FakeLogits:
    def __init__(self, logits: torch.Tensor) -> None:
        self.logits = logits


class _FakeModel:
    """Minimal model whose forward returns fixed logits of the caller's shape."""

    def __init__(self, vocab: int = 128, seq: int = 6) -> None:
        self._vocab = vocab
        self._seq = seq

    def __call__(self, **inputs):
        seq = inputs["input_ids"].shape[1]
        # [1, S, V]; content irrelevant for the zero-token branch
        return _FakeLogits(torch.zeros(1, seq, self._vocab))


def _token_ids(*ids: int) -> torch.Tensor:
    return torch.tensor([list(ids)], dtype=torch.long)


def test_zero_token_completion_returns_all_slots_for_every_call_mode() -> None:
    """The zero-token branch must return the same tuple shape as the normal
    path for all four call modes (the 2026-08-21 SAPO run-killer regression:
    a missing slot made the caller's unpack ValueError kill the run)."""
    model = _FakeModel()
    device = torch.device("cpu")
    prompt_ids = _token_ids(1, 2, 3)
    prompt_mask = torch.ones_like(prompt_ids)
    empty = _token_ids()  # no completion tokens at all

    # mode 1: plain
    r = grpo_trainer.compute_completion_log_prob(
        model,
        None,
        "p",
        "",
        device,
        64,
        50.0,
        prompt_token_ids=prompt_ids,
        prompt_attention_mask=prompt_mask,
        completion_token_ids=empty,
    )
    assert len(r) == 2
    # mode 2: entropy
    r = grpo_trainer.compute_completion_log_prob(
        model,
        None,
        "p",
        "",
        device,
        64,
        50.0,
        add_mm_token_type_ids=False,
        return_entropy=True,
        prompt_token_ids=prompt_ids,
        prompt_attention_mask=prompt_mask,
        completion_token_ids=empty,
    )
    assert len(r) == 3
    # mode 3: token log probs (SAPO train path)
    r = grpo_trainer.compute_completion_log_prob(
        model,
        None,
        "p",
        "",
        device,
        64,
        50.0,
        return_token_log_probs=True,
        prompt_token_ids=prompt_ids,
        prompt_attention_mask=prompt_mask,
        completion_token_ids=empty,
    )
    assert len(r) == 3
    # mode 4: entropy + token log probs (SAPO rollout path)
    r = grpo_trainer.compute_completion_log_prob(
        model,
        None,
        "p",
        "",
        device,
        64,
        50.0,
        return_entropy=True,
        return_token_log_probs=True,
        prompt_token_ids=prompt_ids,
        prompt_attention_mask=prompt_mask,
        completion_token_ids=empty,
    )
    assert len(r) == 4


def test_eos_only_completion_is_a_valid_one_token_action() -> None:
    """An EOS-only output (1 token) must not hit the zero branch: the log-prob
    of EOS is a well-defined one-token action and must be returned."""
    model = _FakeModel()
    prompt_ids = _token_ids(1, 2, 3)
    prompt_mask = torch.ones_like(prompt_ids)
    eos_only = _token_ids(99)  # one EOS token
    r = grpo_trainer.compute_completion_log_prob(
        model,
        None,
        "p",
        "",
        torch.device("cpu"),
        64,
        50.0,
        prompt_token_ids=prompt_ids,
        prompt_attention_mask=prompt_mask,
        completion_token_ids=eos_only,
    )
    seq_lp, token_count = r
    assert token_count.item() == 1
    assert torch.isfinite(seq_lp)


def test_nan_advantage_rms_collapses_to_flat_gate_safely() -> None:
    """A NaN LOO advantage RMS collapses to 0.0 via max(0.0, nan) -> the flat
    all-fail gate QUEUES the group to the repair lane (safe degradation; NaN
    comparisons must never let a corrupt batch into the optimizer). The
    trainer's non-finite loss/gradient guards are the second line of defense.
    """
    magnitude, kind = policy_update_signal_magnitude(
        advantage_mode="loo", signal_stats={}, loo_advantage_rms=float("nan")
    )
    assert kind == "loo_advantage_rms"
    assert magnitude == 0.0  # max(0.0, nan) == 0.0
    assert should_queue_flat_all_fail(
        all_fail=True, route=FRONTIER_RL, update_signal_magnitude=magnitude, threshold=0.05
    )
    # The loss guard: NaN loss is not finite -> trainer skips with zeroed grads.
    nan_loss = torch.tensor(float("nan"))
    assert not torch.isfinite(nan_loss)


def test_flat_gate_uses_clipped_loo_rms_not_component_std() -> None:
    """The flat-group gate must use the final clipped LOO advantage RMS (the
    signal that actually enters SAPO), not raw component dispersion."""
    magnitude, kind = policy_update_signal_magnitude(
        advantage_mode="loo",
        signal_stats={"signal_std": 0.9, "reward_std": 0.5},
        loo_advantage_rms=0.03,
    )
    assert kind == "loo_advantage_rms"
    assert magnitude == 0.03
    assert should_queue_flat_all_fail(
        all_fail=True, route=FRONTIER_RL, update_signal_magnitude=magnitude, threshold=0.05
    )


def test_empty_candidate_scores_zero_reward_path() -> None:
    """An empty candidate must score zero everywhere on the reward path (the
    08-23 SyntaxError-class fix: unparseable code is never a near-miss)."""
    from training.grpo_utils import build_reward_breakdown

    breakdown = build_reward_breakdown(
        code="",
        result={"passed": False, "details": ["ImportError: empty candidate"]},
        required_interface=["def solve()"],
        detail_budget=8,
        pass_weight=0.6,
        syntax_weight=0.1,
        interface_weight=0.15,
        verifier_weight=0.15,
    )
    assert breakdown["syntax_reward"] == 0.0
    assert breakdown["shaped_reward"] == 0.0
    assert breakdown["verifier_reward"] == 0.0  # crash -> no near-miss credit
    assert breakdown["pass_reward"] == 0.0


# ---------------------------------------------------------------------------
# ADVERSARIAL-JUDGE LANE (2026-09-01, lane #18 audit) — the judge-reward path
# must not be gameable, position-biased, or reward-collapsing:
#   item 1  position bias     : batch-judge candidate order randomized per call
#                               + permutation remaps scores to original indices
#   item 2  score parsing     : fail-closed (mass 0, never crash), clamped [0,1]
#   item 3  gaming resistance : prompt anchors on EXECUTABLE evidence
#   item 4  multi-signal      : judge dims blend with pass x shaped, mass bounded
# ---------------------------------------------------------------------------


def _identity_rng():
    """Deterministic rng stub: shuffle() is a no-op. Used where a test must
    pin the presentation order (identity) to assert fixed candidate slots."""

    class _IdentityRng:
        def shuffle(self, order):
            pass

    return _IdentityRng()


def _dim_scores(j: float):
    return {dim: j for dim in MODEL_JUDGE_DIMENSIONS}


_UNIFORM_JUDGE_WEIGHTS = {dim: 0.02 for dim in MODEL_JUDGE_DIMENSIONS}


def _judge_response_labeling_positions(n: int) -> str:
    """A judge response that scores PRESENTED position pos with pos/10.0 on
    every dimension — the labels follow the prompt's candidate_1..N numbering
    (presented order), NOT the original candidate indices."""
    return json.dumps({f"candidate_{pos}": _dim_scores(pos / 10.0) for pos in range(1, n + 1)})


def _presented_order(prompt: str, n: int) -> list[int]:
    """Recover which ORIGINAL candidate index was shown at each position."""
    order = []
    for pos in range(1, n + 1):
        m = re.search(rf"Candidate {pos}:\n```python\n#candidate_(\d+)\n```", prompt)
        assert m, f"prompt must present Candidate {pos}"
        order.append(int(m.group(1)))
    return order


# ── item 1: position bias ──────────────────────────────────────────────────


def test_render_batch_judge_candidates_shuffles_with_fixed_rng() -> None:
    """Item 1 (render): a fixed rng must yield a NON-identity presentation
    order and the rendered text must present codes in exactly that order
    (Candidate 1 == codes[perm[0]]), with the executable evidence attached."""
    codes = [f"#candidate_{i}" for i in range(8)]
    evidences = [f"tests passed: {i % 2 == 0}" for i in range(8)]
    rng = random.Random(20260901)
    text, perm = grpo_trainer._render_batch_judge_candidates(codes, evidences, rng=rng)
    assert perm != list(range(8)), "fixed rng must not yield identity order"
    assert sorted(perm) == list(range(8)), "permutation must cover every index"
    for pos, idx in enumerate(perm, start=1):
        assert f"Candidate {pos}:\n```python\n{codes[idx]}\n```" in text
        assert f"EXECUTABLE EVIDENCE: {evidences[idx]}\n" in text


class _FakeTok:
    pad_token_id = 0

    def apply_chat_template(self, messages, **kw):
        return torch.zeros((1, 4), dtype=torch.long)

    def decode(self, ids, **kw):
        return "decode-unused"


class _FakeGenModel:
    def generate(self, **kw):
        return torch.zeros((1, 8), dtype=torch.long)


def test_model_batch_dim_scores_remaps_scores_to_original_indices(monkeypatch) -> None:
    """Item 1: the in-process batch judge randomizes the presentation order,
    so position-keyed parsed scores MUST be remapped back to original
    candidate indices. Original index 0 must receive the score of the
    position where it was PRESENTED, not position 1's score. (RED 2026-09-01:
    the perm was dropped and every score landed on a random sibling; fixed by
    the judge-bridge lane, pinned here with the real render+parse+remap.)"""
    codes = [f"#candidate_{i}" for i in range(8)]
    evidences = [f"tests passed: {i % 2 == 0}" for i in range(8)]
    # pin the module-level random.Random so the function's internal per-call
    # rng is deterministic; the expected perm comes from the SAME seed.
    real_random_cls = random.Random
    seeded = real_random_cls(20260901)
    _, perm = grpo_trainer._render_batch_judge_candidates(codes, evidences, rng=seeded)
    assert perm != list(range(8))
    monkeypatch.setattr(grpo_trainer.random, "Random", lambda: real_random_cls(20260901))

    judge_response = _judge_response_labeling_positions(8)

    class _Tok(_FakeTok):
        def decode(self, ids, **kw):
            return judge_response

    backend = types.SimpleNamespace(tokenizer=_Tok())
    model = _FakeGenModel()
    monkeypatch.setattr(grpo_trainer, "configured_eos_token_ids", lambda *a, **k: [])
    args = types.SimpleNamespace(model_judge_max_tokens=64, model_judge_temperature=0.0)
    out = grpo_trainer._model_batch_dim_scores(
        codes,
        evidences,
        {"meta": {"description": "t"}},
        model,
        backend,
        args,
        torch.device("cpu"),
    )
    assert out is not None
    for pos, orig_idx in enumerate(perm):
        # original index orig_idx was presented at position pos+1
        assert out[orig_idx]["correctness"] == pytest.approx((pos + 1) / 10.0)


class _FakeHTTPResp:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _patch_dp4_opener(monkeypatch, capture, response_text):
    """Patch urllib so the dp4 client routes through a fake opener that
    captures the request and answers with ``response_text``."""
    import urllib.request as ur

    def fake_open(req, timeout=None):
        payload = json.loads(req.data.decode())
        capture["prompt"] = payload["messages"][0]["content"]
        body = json.dumps({"content": [{"type": "text", "text": response_text}]})
        resp = _FakeHTTPResp()
        resp.read = lambda: body.encode()
        return resp

    class _FakeOpener:
        def open(self, req, timeout=None):
            return fake_open(req, timeout=timeout)

    monkeypatch.setattr(ur, "build_opener", lambda handler: _FakeOpener())


def test_dp4_batch_judge_randomizes_and_remaps_scores(monkeypatch) -> None:
    """Item 1: the LIVE dp4 comparative judge must (a) present candidates in a
    randomized order (position bias killed — RED 2026-09-01: no rng at all,
    candidates presented in fixed order) and (b) remap the position-keyed
    scores back to original indices (RED: perm dropped -> misattribution)."""
    codes = [f"#candidate_{i}" for i in range(8)]
    evidences = [f"tests passed: {i % 2 == 0}" for i in range(8)]

    captured = {}
    _patch_dp4_opener(monkeypatch, captured, _judge_response_labeling_positions(8))
    out = grpo_trainer._model_batch_dim_scores_dp4(
        codes,
        evidences,
        {"meta": {"description": "t"}},
        endpoint="http://127.0.0.1:55080",
    )
    # the sent prompt presented a shuffled order (recovered from the prompt)
    perm = _presented_order(captured["prompt"], 8)
    assert perm != list(range(8))
    # scores remapped to ORIGINAL indices
    assert out is not None
    for pos, orig_idx in enumerate(perm):
        assert out[orig_idx]["correctness"] == pytest.approx((pos + 1) / 10.0)


def test_dp4_batch_judge_default_call_randomizes_order(monkeypatch) -> None:
    """Item 1 (RED 2026-09-01): the production default (no injected rng) must
    present a NON-identity order — three fresh calls must not all show the
    candidates in original order (P(identity^3) < 1e-14 for n=8)."""
    codes = [f"#candidate_{i}" for i in range(8)]
    evidences = ["e"] * 8
    captured = {"prompts": []}

    def fake_open(req, timeout=None):
        payload = json.loads(req.data.decode())
        captured["prompts"].append(payload["messages"][0]["content"])
        resp = _FakeHTTPResp()
        resp.read = lambda: json.dumps(
            {"content": [{"type": "text", "text": '{"candidate_1": {"correctness": 0.5}}'}]}
        ).encode()
        return resp

    import urllib.request as ur

    class _FakeOpener:
        def open(self, req, timeout=None):
            return fake_open(req, timeout=timeout)

    monkeypatch.setattr(ur, "build_opener", lambda handler: _FakeOpener())
    for _ in range(3):
        grpo_trainer._model_batch_dim_scores_dp4(
            codes, evidences, {"meta": {}}, endpoint="http://127.0.0.1:55080"
        )
    orders = [_presented_order(p, 8) for p in captured["prompts"]]
    assert any(o != list(range(8)) for o in orders)


# ── item 2: score parsing — fail-closed, never crash, clamped [0,1] ─────────


def test_judge_parsers_fail_closed_on_pathological_nesting() -> None:
    """Item 2(a) (RED 2026-09-01): an adversarial judge response with deeply
    nested braces must NOT crash the trainer. RecursionError escaped the
    JSONDecodeError/ValueError guard and propagated into the training loop;
    fail-closed = the whole response is unusable -> None (judge-absent)."""
    deep = '{"a":' * 2000 + "1" + "}" * 2000
    assert grpo_trainer._parse_model_dim_scores(deep) is None
    assert grpo_trainer._parse_model_batch_dim_scores(deep, n=2) is None
    # the self-eval score parser shares the crash class -> neutral default
    assert grpo_trainer._parse_self_eval_score(deep) == 0.5


def test_judge_parsers_clamp_out_of_range_and_missing_dims() -> None:
    """Item 2(b-d): out-of-range values clamp to [0,1] (2.0 -> 1.0,
    -1.0 -> 0.0); strings with braces survive as strings; missing dims ->
    None (judge-absent), never 0, never crash; a response with no usable
    numeric dim at all is None (whole batch unusable)."""
    raw = (
        '{"candidate_1": {"correctness": 2.0, "runnability": -1.0, '
        '"quality": 0.5, "note": "saw } and { inside"}, '
        '"candidate_2": {"correctness": "0.9"}}'
    )
    scores = grpo_trainer._parse_model_batch_dim_scores(raw, n=3)
    assert scores is not None
    assert scores[0]["correctness"] == 1.0
    assert scores[0]["runnability"] == 0.0
    assert scores[0]["quality"] == 0.5
    assert scores[0]["result_correctness"] is None  # missing dim -> absent
    assert scores[1]["correctness"] is None  # string value is not numeric
    assert scores[2]["correctness"] is None  # absent candidate fail-closed

    # no usable numeric dim anywhere -> whole response unusable
    assert (
        grpo_trainer._parse_model_batch_dim_scores(
            '{"candidate_1": {"correctness": "n/a"}, "candidate_2": {}}', n=2
        )
        is None
    )

    # per-candidate parser: same clamp + fail-closed
    pc = grpo_trainer._parse_model_dim_scores(
        '{"correctness": 2.0, "runnability": -1.0, "efficiency": "high"}'
    )
    assert pc["correctness"] == 1.0
    assert pc["runnability"] == 0.0
    assert pc["efficiency"] is None

    # Python's json accepts NaN/Infinity literals -> clamped, never crash
    nan_scores = grpo_trainer._parse_model_batch_dim_scores(
        '{"candidate_1": {"correctness": NaN, "quality": Infinity}}', n=1
    )
    assert nan_scores is not None
    assert nan_scores[0]["correctness"] == 0.0
    assert nan_scores[0]["quality"] == 1.0


# ── item 3: gaming resistance — the prompt anchors on executable evidence ───


def test_judge_prompts_anchor_on_executable_evidence() -> None:
    """Item 3: the batch prompt must bind the ranking to EXECUTABLE evidence —
    a passing candidate may not be scored below a failing one on the
    executable dimensions (the exact anchor phrase)."""
    prompt = grpo_trainer.COMPREHENSIVE_BATCH_JUDGE_PROMPT
    anchor = (
        "a candidate whose tests pass must not be scored below "
        "one whose tests fail on the executable dimensions"
    )
    assert anchor in prompt
    assert "EXECUTABLE EVIDENCE" in prompt
    # the per-candidate prompt carries the same authoritative-evidence anchor
    single = grpo_trainer.COMPREHENSIVE_JUDGE_PROMPT
    assert "authoritative anchor" in single
    assert "EXECUTABLE EVIDENCE (authoritative)" in single


# ── item 4: multi-signal — judge dims blend with pass x shaped ──────────────


def test_judge_blend_mass_bounded_and_sums_exactly() -> None:
    """Item 4: with the recommended masses (w_P=0.50, w_S=0.40, w_J=0.10) the
    comprehensive blend is EXACTLY (0.50P + 0.40S + 0.10J)/1.0 — the judge
    term is bounded by w_J and the masses sum to 1 (no renormalization drift,
    no double counting, no hidden judge-only path)."""
    cases = [
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 1.0),
        (0.5, 0.3, 0.7),
        (0.0, 0.0, 1.0),
        (1.0, 1.0, 1.0),
        (0.0, 0.9, 0.0),
    ]
    for p, s, j in cases:
        total = blend_comprehensive_reward(
            pass_reward=p,
            shaped_reward=s,
            model_dim_scores=_dim_scores(j),
            dim_weights=_UNIFORM_JUDGE_WEIGHTS,
            mode="comprehensive",
            pass_mass=0.50,
            shaped_mass=0.40,
            judge_mass=0.10,
        )
        assert total == pytest.approx(0.50 * p + 0.40 * s + 0.10 * j)


def test_judge_alone_cannot_decide_a_pass() -> None:
    """Item 4: with recommended masses the judge alone caps at w_J=0.10 — a
    P=0,S=0 candidate with a PERFECT judge score (J=1) scores 0.10, far below
    the 0.50 floor of a passing candidate (P=1,S=0,J=0). The judge moves the
    ranking within its mass; it can never decide a pass."""
    failing_max = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=0.0,
        model_dim_scores=_dim_scores(1.0),
        dim_weights=_UNIFORM_JUDGE_WEIGHTS,
        mode="comprehensive",
        pass_mass=0.50,
        shaped_mass=0.40,
        judge_mass=0.10,
    )
    passing_floor = blend_comprehensive_reward(
        pass_reward=1.0,
        shaped_reward=0.0,
        model_dim_scores=_dim_scores(0.0),
        dim_weights=_UNIFORM_JUDGE_WEIGHTS,
        mode="comprehensive",
        pass_mass=0.50,
        shaped_mass=0.40,
        judge_mass=0.10,
    )
    assert failing_max == pytest.approx(0.10)
    assert passing_floor == pytest.approx(0.50)
    assert passing_floor > failing_max


def test_judge_absent_renormalizes_over_pass_shaped() -> None:
    """Item 4 (calibration gate): no calibrated weights (dim_weights={}) ->
    the judge mass is exactly 0 and the masses renormalize over P+S:
    total == (0.50P + 0.40S)/0.90 — the judge cannot inject mass when the
    weights are absent."""
    for p, s in [(1.0, 0.0), (0.0, 0.9), (0.3, 0.6)]:
        total = blend_comprehensive_reward(
            pass_reward=p,
            shaped_reward=s,
            model_dim_scores=_dim_scores(1.0),
            dim_weights={},
            mode="comprehensive",
            pass_mass=0.50,
            shaped_mass=0.40,
            judge_mass=0.10,
        )
        assert total == pytest.approx((0.50 * p + 0.40 * s) / 0.90)


def test_runaway_judge_mass_cannot_invert_pass_hierarchy() -> None:
    """Item 4 (RED 2026-09-01): an adversarial --reward-judge-mass (10.0 with
    the recommended P/S masses) must NOT let the judge alone outrank a passing
    candidate: P=0,S=0,J=1 must stay BELOW P=1,S=0,J=0. Today the unbounded
    judge mass renormalizes to 10/10.9 -> 0.917 > 0.046 — the judge alone
    decides the ranking (reward-collapse). The blend must bound the judge
    mass so the executable-pass anchor is structurally enforced."""
    failing_max = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=0.0,
        model_dim_scores=_dim_scores(1.0),
        dim_weights=_UNIFORM_JUDGE_WEIGHTS,
        mode="comprehensive",
        pass_mass=0.50,
        shaped_mass=0.40,
        judge_mass=10.0,
    )
    passing_floor = blend_comprehensive_reward(
        pass_reward=1.0,
        shaped_reward=0.0,
        model_dim_scores=_dim_scores(0.0),
        dim_weights=_UNIFORM_JUDGE_WEIGHTS,
        mode="comprehensive",
        pass_mass=0.50,
        shaped_mass=0.40,
        judge_mass=10.0,
    )
    assert passing_floor > failing_max
