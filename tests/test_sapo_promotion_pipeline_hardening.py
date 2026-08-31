"""QA sweep 2026-08-24: no silent-fallback path may remain around the
adapter-merge fix in the SAPO promotion/eval chain.

The 2026-08-24 fix closed the base-vs-base tie class (peft silently skipping
SAPO-namespace adapter keys). These tests harden the surrounding chain so a
wrong measurement can never again be consumed silently:

1. ``_remap_sapo_keys`` must cover EVERY text-only-namespace key (embed_tokens
   / lm_head / norm / any non-layer key), not just ``.layers.*``, and both the
   two- and three-segment peft prefixes.
2. After ``set_peft_model_state_dict`` every on-disk tensor must be live in
   the loaded model; a partial load (dropped tensors) must be reported, not
   silently run as a partial merge.
3. "Adapter is inert" must be PROVABLE from the checkpoint: only LoRA tensors
   with zero lora_B qualify. Non-LoRA tensors (modules_to_save / full-weight
   saves) and empty checkpoints must fail closed — a zero-loaded model with a
   nonzero non-LoRA checkpoint is a silent base run.
4. ``_adapter_effectively_zero`` must compare against base at the parameter
   level (identity of tensors), not just scan names containing ``lora_B``.
5. ``_probe_differs`` must compare first-step logits (any live delta changes
   them) instead of greedy token lists only (a weak-but-real delta can keep
   the first 8 greedy tokens identical -> false fail-closed).
6. ``decide_sapo_promotion_gate.load_run`` must refuse scorecards whose
   candidates were never produced by the runner (missing generation log,
   truncated log, or candidate hash mismatch) — placeholder or stale
   candidates must never be consumed as a valid promotion leg.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import torch

from scripts.decide_sapo_promotion_gate import EXPECTED_TASKS, load_run
from scripts.run_hf_pass1_eval import (
    _adapter_effectively_zero,
    _missing_loaded_tensors,
    _probe_differs,
    _remap_sapo_keys,
    _state_inert,
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Key-namespace remap covers non-layer keys and both peft prefix shapes
# ─────────────────────────────────────────────────────────────────────────────


def test_remap_covers_embed_and_lm_head_keys() -> None:
    """embed_tokens / lm_head / norm keys need the same language_model insert.

    The full multimodal model keeps every language-model weight under
    ``model.model.language_model.*``; a text-only-namespace key that is NOT
    remapped is silently dropped by peft again -> partial (or zero) merge.
    """
    keys = [
        "base_model.model.model.embed_tokens.lora_A.weight",
        "base_model.model.model.lm_head.lora_B.weight",
        "base_model.model.model.layers.0.mlp.gate_proj.lora_B.weight",
        "base_model.model.model.norm.weight",
        "base_model.model.model.language_model.layers.5.mlp.up_proj.lora_A.weight",
    ]
    remapped = _remap_sapo_keys(keys)
    assert "base_model.model.model.language_model.embed_tokens.lora_A.weight" in remapped
    assert "base_model.model.model.language_model.lm_head.lora_B.weight" in remapped
    assert "base_model.model.model.language_model.layers.0.mlp.gate_proj.lora_B.weight" in remapped
    assert "base_model.model.model.language_model.norm.weight" in remapped
    # warm-namespace keys (already contain language_model) are untouched
    assert keys[-1] in remapped


def test_remap_handles_two_segment_peft_prefix() -> None:
    """Variants without the extra ``model.`` segment must also be remapped."""
    assert _remap_sapo_keys(["base_model.model.layers.0.mlp.gate_proj.lora_A.weight"]) == [
        "base_model.model.language_model.layers.0.mlp.gate_proj.lora_A.weight"
    ]
    assert _remap_sapo_keys(["base_model.model.embed_tokens.lora_A.weight"]) == [
        "base_model.model.language_model.embed_tokens.lora_A.weight"
    ]
    # non-adapter keys (never a SAPO namespace) stay untouched
    unrelated = ["model.layers.0.mlp.gate_proj.weight"]
    assert _remap_sapo_keys(unrelated) == unrelated


# ─────────────────────────────────────────────────────────────────────────────
# 2. Partial loads after set_peft_model_state_dict must be reported
# ─────────────────────────────────────────────────────────────────────────────


def _module_with_params(names: list[str]) -> torch.nn.Module:
    module = torch.nn.Module()
    for name in names:
        module._parameters[name] = torch.nn.Parameter(torch.ones(2, 2))
    return module


def test_missing_loaded_tensors_detects_partial_load() -> None:
    """A tensor absent from the loaded model must be reported, never silent."""
    model = _module_with_params(
        [
            "base_model.model.model.language_model.layers.0.mlp.gate_proj.lora_B.default.weight",
            "base_model.model.model.language_model.layers.0.mlp.gate_proj.lora_A.default.weight",
        ]
    )
    state = {
        "base_model.model.model.language_model.layers.0.mlp.gate_proj.lora_B.weight": torch.ones(
            2, 2
        ),
        "base_model.model.model.language_model.layers.0.mlp.gate_proj.lora_A.weight": torch.ones(
            2, 2
        ),
    }
    assert _missing_loaded_tensors(model, state) == []

    # a key that set_peft_model_state_dict silently dropped must surface
    state["base_model.model.model.language_model.embed_tokens.lora_B.weight"] = torch.ones(2, 2)
    missing = _missing_loaded_tensors(model, state)
    assert missing == ["model.model.language_model.embed_tokens.lora_B.weight"]


def test_missing_loaded_tensors_normalizes_peft_default_segment() -> None:
    """On-disk keys (no ``.default``) must match in-model names (with it)."""
    model = _module_with_params(
        ["base_model.model.layers.0.self_attn.q_proj.lora_A.default.weight"]
    )
    state = {
        "base_model.model.layers.0.self_attn.q_proj.lora_A.weight": torch.ones(2, 2),
        "base_model.model.layers.0.self_attn.q_proj.lora_A.default.weight": torch.ones(2, 2),
    }
    # both spellings name the SAME logical tensor -> neither is missing
    assert _missing_loaded_tensors(model, state) == []
    # a different module path that never loaded IS missing
    state["base_model.model.layers.1.self_attn.q_proj.lora_A.weight"] = torch.ones(2, 2)
    assert _missing_loaded_tensors(model, state) == [
        "model.layers.1.self_attn.q_proj.lora_A.weight"
    ]


# ─────────────────────────────────────────────────────────────────────────────
# 3. Inertness must be provable from the checkpoint
# ─────────────────────────────────────────────────────────────────────────────


def test_state_inert_requires_lora_only_with_zero_b() -> None:
    zero_b = {"base_model.model.model.layers.0.mlp.gate_proj.lora_B.weight": torch.zeros(2, 2)}
    assert _state_inert(zero_b)  # genuinely inert LoRA

    nonzero_a = {
        "base_model.model.model.layers.0.mlp.gate_proj.lora_A.weight": torch.ones(2, 2),
        "base_model.model.model.layers.0.mlp.gate_proj.lora_B.weight": torch.zeros(2, 2),
    }
    assert _state_inert(nonzero_a)  # A-only delta is identity while B stays zero

    nonzero_b = {"base_model.model.model.layers.0.mlp.gate_proj.lora_B.weight": torch.ones(2, 2)}
    assert not _state_inert(nonzero_b)

    modules_to_save = {
        "base_model.model.model.language_model.embed_tokens.weight": torch.ones(2, 2)
    }
    assert not _state_inert(modules_to_save)  # non-LoRA tensor: cannot prove inert

    assert not _state_inert({})  # empty checkpoint: fail closed


# ─────────────────────────────────────────────────────────────────────────────
# 4. Model-level "effectively zero" comparison against base
# ─────────────────────────────────────────────────────────────────────────────


def test_adapter_effectively_zero_compares_all_params_vs_base() -> None:
    base = torch.nn.Module()
    base.linear = torch.nn.Linear(4, 4)
    merged = torch.nn.Module()
    merged.wrapped = base  # shares the SAME parameter objects as base
    merged._parameters["lora_B.default.weight"] = torch.nn.Parameter(torch.zeros(2, 2))
    assert _adapter_effectively_zero(merged, base)

    # a non-lora_B delta (modules_to_save-style weight) is NOT zero
    merged._parameters["lm_head_delta.default.weight"] = torch.nn.Parameter(torch.ones(2, 2))
    assert not _adapter_effectively_zero(merged, base)

    # nonzero lora_A with zero lora_B stays base-identical
    merged._parameters.pop("lm_head_delta.default.weight")
    merged._parameters["lora_A.default.weight"] = torch.nn.Parameter(torch.ones(2, 2))
    assert _adapter_effectively_zero(merged, base)

    # nonzero lora_B is a real delta
    merged._parameters["lora_B.default.weight"] = torch.nn.Parameter(torch.ones(2, 2))
    assert not _adapter_effectively_zero(merged, base)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Probe compares first-step logits, not just greedy tokens
# ─────────────────────────────────────────────────────────────────────────────


class _FakeGenerationOutput:
    def __init__(self, sequences: torch.Tensor, scores: list[torch.Tensor] | None):
        self.sequences = sequences
        self.scores = scores


class _FakeModel:
    def __init__(self, scores: list[torch.Tensor], sequences: torch.Tensor):
        self._scores = scores
        self._sequences = sequences

    def parameters(self):
        return iter([torch.zeros(1)])

    def generate(self, **kwargs):
        return _FakeGenerationOutput(self._sequences, self._scores)


class _FakeTokenizer:
    eos_token_id = 2

    def __call__(self, text: str, return_tensors: str = "pt"):
        return {
            "input_ids": torch.tensor([[1, 2, 3]]),
            "attention_mask": torch.tensor([[1, 1, 1]]),
        }


class _FakeRenderBackend:
    def apply_chat_template(self, messages, **kwargs):
        return "probe"


class _FakeBackend:
    render_backend = _FakeRenderBackend()
    text_backend = _FakeTokenizer()


def test_probe_differs_catches_logit_delta_with_identical_tokens() -> None:
    """Greedy tokens can stay identical for a weak-but-real delta; logits cannot."""
    vocab = 16
    base_scores = torch.zeros(1, 1, vocab)
    adapter_scores = torch.zeros(1, 1, vocab)
    adapter_scores[0, 0, 3] = 0.5  # different logits, same argmax (token 0)
    sequences = torch.zeros(1, 11, dtype=torch.long)
    base = _FakeModel([base_scores], sequences)
    adapter = _FakeModel([adapter_scores], sequences)
    # 2026-08-25 (test-update wave): _probe_differs signature is
    # (base, adapter, probe, backend) — backend is the 4th positional param.
    assert _probe_differs(base, adapter, "def solve():\n    return ", _FakeBackend())


def test_probe_differs_returns_false_when_logits_identical() -> None:
    vocab = 16
    scores = torch.zeros(1, 1, vocab)
    sequences = torch.zeros(1, 11, dtype=torch.long)
    assert not _probe_differs(
        _FakeModel([scores], sequences),
        _FakeModel([scores], sequences),
        "probe",
        _FakeBackend(),
    )


# ─────────────────────────────────────────────────────────────────────────────
# 6. decide gate must refuse scorecards the runner did not produce
# ─────────────────────────────────────────────────────────────────────────────


def _promotion_run_dir(
    tmp_path: Path,
    name: str,
    log_entries: list[dict] | None = None,
) -> Path:
    run_dir = tmp_path / name
    run_dir.mkdir()
    task_ids = [f"task-{index:02d}" for index in range(EXPECTED_TASKS)]
    manifest = {
        "tasks": [
            {
                "id": task_id,
                "prompt_file": f"prompts/{task_id}.txt",
                "candidate_file": f"candidates/{task_id}.py",
            }
            for task_id in task_ids
        ]
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    digest = "a" * 64
    results = [
        {
            "id": task_id,
            "source": "override",
            "candidate_sha256": digest,
            "passed": False,
            "failure_category": "assertion",
            "details": [],
        }
        for task_id in task_ids
    ]
    scorecard = {"schema_version": "eval-scorecard-v2", "results": results}
    (run_dir / "scorecard.json").write_text(json.dumps(scorecard), encoding="utf-8")
    if log_entries is not None:
        (run_dir / "hf-pass1-generation-log.json").write_text(
            json.dumps({"tasks": log_entries}), encoding="utf-8"
        )
    return run_dir


def test_load_run_requires_runner_generation_log(tmp_path: Path) -> None:
    run_dir = _promotion_run_dir(tmp_path, "no-log")
    with pytest.raises(SystemExit, match="hf-pass1-generation-log"):
        load_run(run_dir)


def test_load_run_rejects_truncated_generation_log(tmp_path: Path) -> None:
    digest = "a" * 64
    log_entries = [
        {"task_id": f"task-{index:02d}", "candidate_sha256": digest}
        for index in range(EXPECTED_TASKS - 1)
    ]
    run_dir = _promotion_run_dir(tmp_path, "truncated-log", log_entries=log_entries)
    with pytest.raises(SystemExit, match="generation log"):
        load_run(run_dir)


def test_load_run_rejects_candidate_hash_mismatch(tmp_path: Path) -> None:
    digest = "a" * 64
    log_entries = [
        {"task_id": f"task-{index:02d}", "candidate_sha256": digest}
        for index in range(EXPECTED_TASKS)
    ]
    run_dir = _promotion_run_dir(tmp_path, "hash-mismatch", log_entries=log_entries)
    scorecard_path = run_dir / "scorecard.json"
    scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
    scorecard["results"][3]["candidate_sha256"] = "b" * 64
    scorecard_path.write_text(json.dumps(scorecard), encoding="utf-8")
    with pytest.raises(SystemExit, match="candidate hash mismatch"):
        load_run(run_dir)


def test_load_run_accepts_matching_generation_log(tmp_path: Path) -> None:
    digest = "a" * 64
    log_entries = [
        {"task_id": f"task-{index:02d}", "candidate_sha256": digest}
        for index in range(EXPECTED_TASKS)
    ]
    run_dir = _promotion_run_dir(tmp_path, "matching", log_entries=log_entries)
    loaded = load_run(run_dir)
    assert len(loaded["results"]) == EXPECTED_TASKS
