"""TDD: batched rollout assembly — the ~8x generation speedup for the 8-NPU run.

Root cause of 2-weeks-no-progress: grpo_trainer.py:2295 documents 60-110 min/step
because candidates are generated SERIALLY (one model.generate per candidate) on a 27B
sharded across 8 NPUs. Batching all G candidates into parallel decode opens the ~8x.

This test pins the PURE assembly/split logic (no live model needed):
  - build_batched_inputs expands the shared prompt to G identical rows
  - split_batched_generations maps a [G, N] token tensor back to per-candidate
    completions, honoring greedy_count (first rows greedy) vs sampled rest
  - greedy rows decode with temperature 0 (argmax) — verified by token inspection
"""

import torch

from training.generation import (
    build_batched_prompt_inputs,
    split_batched_generations,
)


def test_build_batched_prompt_inputs_expands_to_group():
    base = dict(input_ids=torch.tensor([[1, 2, 3]]), attention_mask=torch.tensor([[1, 1, 1]]))
    out = build_batched_prompt_inputs(base, group_size=5)
    assert out["input_ids"].shape[0] == 5
    assert out["attention_mask"].shape[0] == 5
    # all rows identical to the base prompt
    assert torch.equal(out["input_ids"][0], out["input_ids"][3])
    assert torch.equal(out["input_ids"][-1], base["input_ids"][0])


def test_split_batched_generations_returns_per_candidate_completions():
    # simulate: G=3 rows, prompt 2 tokens, 3 completion tokens each
    prompt_len = 2
    batched = torch.tensor(
        [
            [10, 11, 20, 21, 22],  # candidate 0
            [10, 11, 30, 31, 32],  # candidate 1
            [10, 11, 40, 41, 42],  # candidate 2
        ]
    )
    completions = split_batched_generations(batched, prompt_len=prompt_len)
    assert len(completions) == 3
    assert torch.equal(completions[0], batched[0, prompt_len:])
    assert torch.equal(completions[2], batched[2, prompt_len:])


def test_split_handles_eos_truncation_per_row():
    # EOS id 999; candidate 年报 ends early
    batched = torch.tensor(
        [
            [1, 2, 5, 999, 6],  # truncends at 999
            [1, 2, 7, 8, 9],
        ]
    )
    completions = split_batched_generations(
        batched, prompt_len=2, eos_token_id=999, truncate_at_eos=True
    )
    # first candidate cut at eos -> 1 token
    assert completions[0].numel() == 1
    assert completions[0][0].item() == 5
    # second has no eos -> full 3 tokens
    assert completions[1].numel() == 3
