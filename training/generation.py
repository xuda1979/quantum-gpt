"""Single home for rollout generation/fence-EOS mechanics (architect lane #26).

Extracted from ``training/grpo_trainer.py`` on 2026-08-26, behavior-identical
(zero-change extraction — ``tests/test_generation_module_extraction.py`` pins
the re-export identity; the behavioral contract stays with the existing
trainer suites). The rollout lane's greedy-augmentation work builds on this
module boundary.

Ownership boundary: anything that turns sampled tokens into a completion —
fence recognition, fence/EOS stopping, stop-marker augmentation, EOS
resolution, termination diagnostics — lives here. The trainer's generation
CALL sites (model.generate wiring, prompt building, budgets) stay in
grpo_trainer.py; if a site needs a new stop/diagnostic mechanic it imports it
from here. Cross-boundary changes need the architect lane's sign-off.
"""

from __future__ import annotations

# ruff: noqa: UP038  # (X | Y) isinstance is py3.10-only; runs under the py3.9 .venv
import re
from typing import Any

import torch
from transformers import StoppingCriteria

from training.compat import strict_zip


def extract_code(response: str) -> str:
    # 2026-08-26 (r10): extract from the SAME fence opener the stop criterion
    # recognizes (IGNORECASE, whitespace-tolerant, any language tag). The
    # old prefix split leaked the tag for "```Python" and versioned tags
    # ("```python3\n" extracted "3\ncode"); the bare-"```" branches below
    # keep the same-line legacy forms working.
    opening = _CODE_FENCE_OPEN_RE.search(response)
    if opening is not None:
        tail = response[opening.end() :]
        close = tail.find("```")
        return (tail[:close] if close >= 0 else tail).strip()
    if "```python" in response:
        parts = response.split("```python")
        if len(parts) > 1:
            return parts[1].split("```")[0].strip()
    if "```" in response:
        parts = response.split("```")
        if len(parts) > 2:
            return parts[1].strip()
    return response.strip()


# 2026-08-25 (generation-efficiency): fast tokenizers insert spaces on
# decode ("``` python \n"), so the fence-open marker must tolerate whitespace
# around the optional language tag — the strict form never matched the
# space-inserted decode and the closing-fence stop never fired.
# 2026-08-26 (r10): the tag is ANY word (python3, qsharp, ...) — a versioned
# tag after the newline is a well-formed fence and must open one. The
# newline requirement stays CONSERVATIVE: a same-line opener ("```python
# x=1") is not a fence (no false stop on prose backticks); that class is
# surfaced by the cap_run_with_fence_opener diagnostic instead.
_CODE_FENCE_OPEN_RE = re.compile(r"```[^\S\r\n]*[A-Za-z0-9_+.-]*[^\S\r\n]*\r?\n", re.IGNORECASE)


def has_closed_code_fence(text: str) -> bool:
    """Return true only after a Markdown code fence has been closed."""
    opening = _CODE_FENCE_OPEN_RE.search(text)
    return opening is not None and text.find("```", opening.end()) >= 0


def truncate_at_closing_fence(text: str) -> str:
    """Cut a completion at its closing fence (exclusive of trailing prose).

    2026-09-01 (Lane A closure): the transformers decode path stops generation
    AT the closing fence via ``StopAfterClosedCodeFence`` (the primary
    stopper, §5.9) — its completions never contain prose past the fence. The
    vLLM rollout path decodes text through an external server that stops only
    on EOS or the token cap, so a model that never samples EOS (run-6 S1-S5
    eos_termination_rate 0.0) returns fence-closed completions WITH trailing
    prose. Truncating vLLM texts here restores distribution parity with the
    transformers path (same reward view, same token budget, same
    fence-close-as-termination training target after the EOS marker).

    Returns the text unchanged when no closing fence exists (the caller's
    EOS/truncation backstops apply, exactly as in the decode path).
    """
    opening = _CODE_FENCE_OPEN_RE.search(text)
    if opening is None:
        return text
    close = text.find("```", opening.end())
    if close < 0:
        return text
    return text[: close + 3]


class StopAfterClosedCodeFence(StoppingCriteria):
    """Stop fenced answers at their closing fence instead of trailing prose."""

    def __init__(self, tokenizer: Any, *, prompt_length: int) -> None:
        self.tokenizer = tokenizer
        self.prompt_length = int(prompt_length)

    # 2026-08-26 (r10, debug-lane follow-up 3): decode only the last TAIL
    # tokens per step — a closing fence, when generated, is always at the
    # end of the current completion. Full-decode happens only when the tail
    # contains a backtick run (to confirm an opening fence exists earlier).
    # The old full-decode-per-step was O(N^2) per completion (a 2048-cap run
    # paid ~4.2M decode-tokens; ~minutes of CPU per 64-candidate step).
    _TAIL_TOKENS = 16

    def __call__(
        self,
        input_ids: torch.LongTensor,
        scores: torch.FloatTensor | None,
        **kwargs: Any,
    ) -> torch.BoolTensor:
        decisions = []
        for row in input_ids:
            completion = row[self.prompt_length :]
            if completion.numel() == 0:
                decisions.append(False)
                continue
            tail_text = self.tokenizer.decode(
                completion[-self._TAIL_TOKENS :], skip_special_tokens=True
            )
            if "```" not in tail_text:
                decisions.append(False)
                continue
            decisions.append(
                has_closed_code_fence(self.tokenizer.decode(completion, skip_special_tokens=True))
            )
        return torch.tensor(decisions, dtype=torch.bool, device=input_ids.device)


def build_generation_diagnostics(
    *,
    raw_responses: list[str],
    codes: list[str],
    completion_token_ids: list[torch.Tensor],
    max_new_tokens: int,
    eos_token_ids: set[int] | None = None,
) -> dict[str, Any]:
    """Return privacy-safe rollout length and termination diagnostics.

    Persisting these aggregate/length fields makes cap saturation actionable
    without logging generated source code. A completion at the hard cap that
    did not end in EOS is a true truncation; extracted/raw character counts
    expose fenced-code or trailing-prose overhead.
    """
    lengths = [int(ids.numel()) for ids in completion_token_ids]
    eos_ids = {int(token_id) for token_id in (eos_token_ids or set())}
    # 2026-08-26 (r10) + 2026-08-31 (QA lane, stop-identity fix): the three
    # stop reasons partition the completion set exactly once per completion —
    # eos_terminated (ends in a NATURAL EOS id: the model emitted the end
    # token), fence_terminated (the raw text closed a code fence), and
    # truncated (hit the cap without either). The r10 synthetic fence-stop
    # marker leaves an EOS id at the END of fence-closed completions as the
    # fence-close training target; that marker is a FENCE-class event, not a
    # natural EOS — counting it as eos_terminated double-counted every
    # fence-stopped completion (eos+fence+truncated == 2) and made
    # eos_termination_rate unable to reveal "the model never samples EOS"
    # (the run-6 diagnostic the rates were built for). Fence-closed
    # completions are therefore labeled by their fence class only.
    eos_terminated = [
        bool(
            ids.numel()
            and int(ids.reshape(-1)[-1].item()) in eos_ids
            and not has_closed_code_fence(response)
        )
        for ids, response in strict_zip(completion_token_ids, raw_responses)
    ]
    fence_terminated = [has_closed_code_fence(response) for response in raw_responses]
    count = len(lengths)
    # A completion that reaches the cap but ends in EOS is a natural end, not a
    # truncation (2026-08-24 data-efficiency finding 3): counting it as cut
    # inflated truncation_rate and pushed healthy groups toward skip/repair.
    # A completion that closes its fence AT the cap is likewise complete
    # (2026-08-26 debug-lane follow-up 2) — the fence-stop just fired at the
    # boundary.
    truncated = [
        bool(length >= max_new_tokens and not terminated and not fenced)
        for length, terminated, fenced in strict_zip(lengths, eos_terminated, fence_terminated)
    ]
    # 2026-08-26 (r10): a cap-run whose raw text contains ANY fence opener
    # (same-line "```python x=1" or an unhandled tag form) is the
    # fence-stop-regression class — the stop regex missed a fence the
    # extraction still sees. Observed live in run-6 S1 (2048-cap completion
    # with a fenced region, 323/5459 chars). Monitoring flags this rate.
    cap_run_with_fence_opener = [
        bool(truncated[i] and "```" in raw_responses[i]) for i in range(count)
    ]
    return {
        "completion_token_lengths": lengths,
        "eos_terminated": eos_terminated,
        "eos_termination_rate": (float(sum(eos_terminated) / count) if count else 0.0),
        "fence_terminated": fence_terminated,
        "fence_termination_rate": (float(sum(fence_terminated) / count) if count else 0.0),
        "truncated": truncated,
        "truncation_rate": float(sum(truncated) / count) if count else 0.0,
        "cap_run_with_fence_opener": cap_run_with_fence_opener,
        "cap_run_with_fence_opener_rate": (
            float(sum(cap_run_with_fence_opener) / count) if count else 0.0
        ),
        "raw_response_chars": [len(response) for response in raw_responses],
        "extracted_code_chars": [len(code) for code in codes],
    }


def configured_eos_token_ids(model: Any, tokenizer: Any = None) -> set[int]:
    """Resolve scalar or list EOS IDs from the loaded generation contract.

    2026-08-25 (generation-efficiency): the base model's config can omit
    eos_token_id while the TOKENIZER defines it — without the tokenizer
    fallback, ``generate`` never stopped on EOS (every step ran the full
    max-new-tokens cap) and ``eos_termination_rate`` was a permanent 0.0
    measurement artifact. The union of model + tokenizer ids is returned;
    ``tokenizer=None`` preserves the legacy model-only behavior.
    """
    value: Any = None
    for source in (getattr(model, "generation_config", None), getattr(model, "config", None)):
        candidate = getattr(source, "eos_token_id", None)
        if candidate is not None:
            value = candidate
            break
    ids: set[int] = set()
    if tokenizer is not None:
        tok_eos = getattr(tokenizer, "eos_token_id", None)
        if tok_eos is not None:
            ids.add(int(tok_eos))
    if value is None:
        return ids
    if isinstance(value, (list, tuple, set)):
        ids |= {int(token_id) for token_id in value}
    else:
        ids.add(int(value))
    return ids


def append_fence_stop_markers(
    completion_token_ids: list[torch.Tensor],
    raw_responses: list[str],
    stop_eos_ids: set[int],
    *,
    tokenizer: Any = None,
) -> tuple[list[torch.Tensor], list[bool]]:
    """Append the canonical stop token to fence-stopped completions.

    2026-08-26 (r10, lane #22): the fence StoppingCriteria cuts generation at
    the closing fence, so EOS is NEVER sampled by the model and the
    fence-close position has no training target — run-6 S1-S5 all sat at
    eos_termination_rate 0.0 and 25-50% of candidates still hit the cap. The
    marker appends the resolved EOS id after every fence-closed, non-EOS-
    terminated completion, giving the fence-close position the real
    end-token target: the model learns to terminate after the closing fence.

    Both log-prob passes (rollout old-policy and the train pass) consume the
    SAME augmented ids, so the importance ratio stays exact; the train-pass
    sequence cap drops the marker together with the completion tail when it
    cuts. ``raw_responses`` are the decoded texts (the harness view stays
    unchanged — the marker is never decoded into them).

    Returns ``(augmented_ids, fence_stopped)`` where ``fence_stopped[i]`` is
    True exactly when the completion received the marker.
    """
    if not stop_eos_ids:
        return list(completion_token_ids), [False] * len(completion_token_ids)
    tokenizer_eos = getattr(tokenizer, "eos_token_id", None)
    if tokenizer_eos is not None and int(tokenizer_eos) in stop_eos_ids:
        preferred = int(tokenizer_eos)
    else:
        preferred = min(sorted(stop_eos_ids))
    augmented: list[torch.Tensor] = []
    fence_stopped: list[bool] = []
    for ids, response in strict_zip(completion_token_ids, raw_responses):
        ids = ids.detach().cpu()
        last = int(ids.reshape(-1)[-1].item()) if ids.numel() else None
        if has_closed_code_fence(response) and last not in stop_eos_ids:
            augmented.append(torch.cat([ids, torch.tensor([preferred], dtype=ids.dtype)]))
            fence_stopped.append(True)
        else:
            augmented.append(ids)
            fence_stopped.append(False)
    return augmented, fence_stopped


def build_batched_prompt_inputs(base_inputs: dict, *, group_size: int) -> dict:
    """Expand a single-prompt input batch to ``group_size`` identical rows.

    2026-08-28 (architect, root-cause of 2-week no-progress): rollouts were
    generated SERIALLY (one model.generate per candidate) on a 27B sharded
    across 8 NPUs — grpo_trainer.py:2295 documents 60-110 min/step. Batching
    all G candidates into ONE generate call lets the 8 devices decode them in
    parallel (~8x). The GRPO rollout prompt is shared by the whole group, so
    expansion is a pure repeat of the input rows.
    """
    return {
        k: v.repeat(group_size, *([1] * (v.ndim - 1))) if isinstance(v, torch.Tensor) else v
        for k, v in base_inputs.items()
    }


def split_batched_generations(
    batched: torch.Tensor,
    *,
    prompt_len: int,
    eos_token_id: int | None = None,
    truncate_at_eos: bool = False,
) -> list[torch.Tensor]:
    """Split a batched generate output (rows = candidates) into per-candidate
    completion token tensors, optionally truncating each row at the first EOS."""
    completions = []
    for row in batched:
        comp = row[prompt_len:]
        if truncate_at_eos and eos_token_id is not None and eos_token_id in comp:
            comp = comp[: int((comp == eos_token_id).nonzero()[0])]
        completions.append(comp)
    return completions
