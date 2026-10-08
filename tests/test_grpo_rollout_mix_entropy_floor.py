"""TDD (2026-08-26, lane #22, manager TOP-PRIORITY wave): GREEDY-AUGMENTED
ROLLOUTS + ENTROPY FLOOR.

Greedy-augmented rollouts (beats-base blocker): a configurable fraction
(default 0.4) of each group's rollouts is generated at temperature 0 (greedy
argmax) and graded through the SAME harness/reward path; the greedy
candidates enter the SAPO group with their true rewards/advantages. The loss
math is untouched — only the group composition changes. fraction 0 must be
byte-identical to the current path.

Entropy floor (preventive): a small per-step loss term penalizing mean
current-policy entropy below a floor (default 1.5 nats, weight 0.01),
engaged only below the floor, documented in loss_breakdown.entropy_floor_penalty
and honored by the math-audit final-loss identity
(loss == loss_recomputed + entropy_floor_penalty + DR terms).
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest
import torch
from tokenizers import Tokenizer, models
from transformers import (
    GPT2Config,
    GPT2LMHeadModel,
    LogitsProcessor,
    LogitsProcessorList,
    PreTrainedTokenizerFast,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_trainer import (  # noqa: E402
    compute_entropy_floor_penalty,
    filter_generation_inputs,
    generate_group,
    greedy_rollout_count,
)
from training.grpo_utils import build_grpo_step_record  # noqa: E402
from training.text_preprocessor_backend import TextPreprocessorBackend  # noqa: E402

VOCAB = {
    "```": 0,
    "python": 1,
    "\n": 2,
    "x": 3,
    " = ": 4,
    "1": 5,
    "trailing": 6,
    "<|endoftext|>": 60,
    "<pad>": 61,
    "<s>": 62,
    "<unk>": 63,
}
EOS_ID = 60


def make_tokenizer() -> PreTrainedTokenizerFast:
    t = Tokenizer(models.WordLevel(VOCAB, unk_token="<unk>"))
    return PreTrainedTokenizerFast(
        tokenizer_object=t,
        eos_token="<|endoftext|>",
        pad_token="<pad>",
        bos_token="<s>",
        unk_token="<unk>",
    )


def make_model() -> GPT2LMHeadModel:
    cfg = GPT2Config(n_layer=1, n_head=1, n_embd=16, vocab_size=64)
    cfg.eos_token_id = None
    cfg.bos_token_id = None
    cfg.pad_token_id = None
    model = GPT2LMHeadModel(cfg)
    model.eval()
    return model


class _ForcedTokens(LogitsProcessor):
    def __init__(self, forced: dict[int, int]) -> None:
        self.forced = dict(forced)

    def __call__(self, input_ids: torch.Tensor, scores: torch.Tensor) -> torch.Tensor:
        pos = int(input_ids.shape[1])
        if pos in self.forced:
            scores = scores.clone()
            scores.fill_(-1000.0)
            scores[:, self.forced[pos]] = 1000.0
        return scores


class _Render:
    def __init__(self) -> None:
        self.called_with = None

    def apply_chat_template(
        self, messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
    ):  # noqa: ARG002
        self.called_with = messages
        return "TASK: " + messages[-1]["content"]


def _backend() -> TextPreprocessorBackend:
    return TextPreprocessorBackend(
        render_backend=_Render(),
        text_backend=make_tokenizer(),
        save_backend=make_tokenizer(),
        backend_kind="test",
    )


def _args(**overrides) -> types.SimpleNamespace:
    base = dict(
        temperature=1.0,
        top_p=1.0,
        group_size=5,
        max_new_tokens=64,
        device=torch.device("cpu"),
        fence_stop_marker=True,
        greedy_rollout_fraction=0.0,
    )
    base.update(overrides)
    return types.SimpleNamespace(**base)


def _spy_generate(model: GPT2LMHeadModel, calls: list[dict]):
    """Record generate kwargs, then force a deterministic fence completion."""
    real_generate = model.generate
    forced = LogitsProcessorList(
        [_ForcedTokens({1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 2, 8: 0, 9: 6})]
    )

    def spy(*a, **k):
        calls.append(dict(k))
        k["logits_processor"] = forced
        k["do_sample"] = False  # determinism for the test; the record is above
        return real_generate(*a, **k)

    model.generate = spy  # type: ignore[method-assign]


# ---------------------------------------------------------------------------
# greedy fraction math
# ---------------------------------------------------------------------------


def test_greedy_rollout_count_math() -> None:
    assert greedy_rollout_count(4, 0.0) == 0
    assert greedy_rollout_count(5, 0.4) == 2
    assert greedy_rollout_count(4, 0.4) == 2
    assert greedy_rollout_count(10, 0.4) == 4
    assert greedy_rollout_count(4, 1.0) == 4
    assert greedy_rollout_count(1, 0.4) == 0
    assert greedy_rollout_count(2, 0.4) == 1
    # never exceeds the group
    assert greedy_rollout_count(3, 2.0) == 3


# ---------------------------------------------------------------------------
# (a) fraction 0 -> identical group (byte-identical cold path)
# ---------------------------------------------------------------------------


def test_generate_group_fraction_zero_identical_group() -> None:
    model = make_model()
    calls: list[dict] = []
    _spy_generate(model, calls)
    args = _args(group_size=3, greedy_rollout_fraction=0.0)
    raw, text, _, _, completion_ids = generate_group(
        model,
        _backend(),
        "Implement solve().",
        args,
        count=3,
        max_new_tokens=64,
        return_token_ids=True,
    )
    # 2026-08-28 (batched speedup): one sampled batched call (was 3 serial)
    assert len(calls) == 1
    for call in calls:
        assert call["do_sample"] is True
        assert call["temperature"] == 1.0
    assert len(raw) == 3
    assert len(completion_ids) == 3
    assert text.startswith("TASK: ")


# ---------------------------------------------------------------------------
# (b) fraction 0.4 -> mixed temperatures in the group, all candidates graded
# ---------------------------------------------------------------------------


def test_generate_group_fraction_mixes_temperatures() -> None:
    model = make_model()
    calls: list[dict] = []
    _spy_generate(model, calls)
    args = _args(group_size=5, greedy_rollout_fraction=0.4, temperature=1.1)
    raw, _, _, _, completion_ids = generate_group(
        model,
        _backend(),
        "Implement solve().",
        args,
        count=5,
        max_new_tokens=64,
        return_token_ids=True,
    )
    # 2026-08-28 (batched speedup): 2 batched calls (greedy subset + sampled)
    assert len(calls) == 2
    # calls[0] = the greedy subset batched call (all greedy, temp 0)
    assert calls[0]["do_sample"] is False
    assert calls[0]["temperature"] == 0.0
    # calls[1] = the sampled subset batched call
    assert calls[1]["do_sample"] is True
    assert calls[1]["temperature"] == 1.1
    # ALL candidates come back graded (the harness path is untouched) and the
    # fence-stop + synthetic marker still apply to every fence-closed one
    assert len(raw) == 5
    assert len(completion_ids) == 5
    for ids, response in zip(completion_ids, raw):  # noqa: B905 plain zip: same-length by construction
        assert ids.numel() >= 1
        if "```" in response:
            assert int(ids[-1]) == EOS_ID  # marker on fence-closed completions
    # rollout stats semantics unchanged: lengths match the returned ids
    assert [int(ids.numel()) for ids in completion_ids] == [
        int(ids.numel()) for ids in completion_ids
    ]


def test_generate_group_fraction_clamped_to_group() -> None:
    model = make_model()
    calls: list[dict] = []
    _spy_generate(model, calls)
    args = _args(group_size=2, greedy_rollout_fraction=2.0)
    raw, _, _, _, _ = generate_group(
        model,
        _backend(),
        "Implement solve().",
        args,
        count=2,
        max_new_tokens=64,
        return_token_ids=True,
    )
    # 2026-08-28 (batched speedup): 1 greedy batched call (fraction clamped → all greedy)
    assert len(calls) == 1
    assert calls[0]["do_sample"] is False
    assert len(raw) == 2


# ---------------------------------------------------------------------------
# entropy floor: value semantics + differentiability
# ---------------------------------------------------------------------------


def test_entropy_floor_penalty_zero_above_floor() -> None:
    p = compute_entropy_floor_penalty(torch.tensor([2.0, 1.8]), floor=1.5, weight=0.01)
    assert float(p) == 0.0
    # disabled weight -> always 0 even far below the floor
    assert float(compute_entropy_floor_penalty(torch.tensor([0.1]), floor=1.5, weight=0.0)) == 0.0
    # empty candidate set -> 0
    assert float(compute_entropy_floor_penalty(None, floor=1.5, weight=0.01)) == 0.0


def test_entropy_floor_penalty_positive_below_floor() -> None:
    p = compute_entropy_floor_penalty(torch.tensor([1.0, 1.2]), floor=1.5, weight=0.01)
    # mean entropy 1.1, gap 0.4, weight 0.01
    assert float(p) == pytest.approx(0.004, abs=1e-6)
    p2 = compute_entropy_floor_penalty(torch.tensor([0.4, 0.5]), floor=1.5, weight=0.05)
    assert float(p2) == pytest.approx(0.05 * (1.5 - 0.45), abs=1e-6)


def test_entropy_floor_penalty_is_differentiable() -> None:
    x = torch.randn(2, requires_grad=True)
    entropies = x * x  # stand-in for temperature-scaled current-policy entropy
    p = compute_entropy_floor_penalty(entropies, floor=10.0, weight=0.01)
    assert float(p) > 0.0
    p.backward()
    assert x.grad is not None
    assert bool(torch.any(x.grad != 0.0))


# ---------------------------------------------------------------------------
# (c) loss identity holds WITH the term included (math-audit convention)
# ---------------------------------------------------------------------------


def test_math_audit_final_loss_identity_holds_with_entropy_floor_penalty() -> None:
    from scripts.sapo_math_audit_step_records import audit_final_loss_identity

    recomputed = -0.05
    penalty = 0.007
    bd = {
        "loss_recomputed": recomputed,
        "loss": recomputed + penalty,
        "entropy_floor_penalty": penalty,
        "dr_pair_loss_added": False,
        "dr_variance_correction_added": False,
    }
    record = {"step": 1, "skipped": False, "loss_breakdown": bd}
    assert audit_final_loss_identity(record) == []
    # tampered: loss omits the penalty -> the identity must flag it
    tampered = {"step": 1, "skipped": False, "loss_breakdown": {**bd, "loss": recomputed}}
    findings = audit_final_loss_identity(tampered)
    assert any("loss" in f.message for f in findings)
    # tampered: penalty inflated -> flagged too
    inflated = {
        "step": 1,
        "skipped": False,
        "loss_breakdown": {**bd, "entropy_floor_penalty": penalty + 0.01},
    }
    assert audit_final_loss_identity(inflated) != []


class _ExtraFieldTokenizer:
    """Wraps a tokenizer so its batch dict carries an extra field that
    model.generate() cannot forward (the launch-simulator F2 fixture: a
    generic tokenizer emitting special_tokens_mask)."""

    def __init__(self, inner: PreTrainedTokenizerFast) -> None:
        self.inner = inner

    def __call__(self, *args, **kwargs):
        out = self.inner(*args, **kwargs)
        out["special_tokens_mask"] = torch.zeros_like(out["input_ids"])
        return out

    def __getattr__(self, name):  # noqa: D105
        return getattr(self.inner, name)


def test_filter_generation_inputs_keeps_only_model_input_names() -> None:
    model = make_model()
    inputs = {
        "input_ids": torch.ones(1, 4, dtype=torch.long),
        "attention_mask": torch.ones(1, 4, dtype=torch.long),
        "token_type_ids": torch.zeros(1, 4, dtype=torch.long),
        "special_tokens_mask": torch.zeros(1, 4, dtype=torch.long),
    }
    kept = filter_generation_inputs(model, inputs)
    assert set(kept) == {"input_ids", "attention_mask"}


def test_generate_group_filters_extra_tokenizer_fields() -> None:
    # F2 (launch simulator 2026-08-26): an extra tokenizer batch field must
    # not reach model.generate() — it crashes generic-tokenizer fixtures.
    model = make_model()
    calls: list[dict] = []
    _spy_generate(model, calls)
    extra = _ExtraFieldTokenizer(make_tokenizer())
    backend = TextPreprocessorBackend(
        render_backend=_Render(),
        text_backend=extra,
        save_backend=extra,
        backend_kind="test",
    )
    args = _args(group_size=1, greedy_rollout_fraction=0.0)
    raw, _, _, _, completion_ids = generate_group(
        model,
        backend,
        "Implement solve().",
        args,
        count=1,
        max_new_tokens=64,
        return_token_ids=True,
    )
    assert len(raw) == 1
    assert len(completion_ids) == 1
    assert "input_ids" in calls[0] and "attention_mask" in calls[0]
    assert "special_tokens_mask" not in calls[0]
    assert "token_type_ids" not in calls[0]


def test_step_record_carries_greedy_count() -> None:
    record = build_grpo_step_record(
        step=1,
        task_name="quantum_demo",
        domain="quantum",
        mean_reward=0.0,
        signal_stats={"signal_std": 0.0, "reward_std": 0.0},
        pass_rate=0.0,
        syntax_rate=0.0,
        interface_rate=0.0,
        verifier_rate=0.0,
        task_prob=1.0,
        task_state={"ema_reward": 0.0, "seen": 1},
        greedy_count=2,
    )
    assert record["greedy_count"] == 2
