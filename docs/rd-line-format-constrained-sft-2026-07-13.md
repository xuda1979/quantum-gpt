# Track N6 — Output-Format-Constrained SFT (formatter-LoRA)

**Owner:** subagent track (loop 2026-07-13)
**Status:** design + scaffold
**Target students:** Qwen3.6-27B (ASI1), Qwen3.6-35B-A3B (ASI2/3)
**Constraint:** post-training only; no architecture change.

## Problem (from 2026-07-09 verified eval)

On the gold-standard `quantum_qaoa_maxcut_5cycle` 56-task scorecard:
- `qwen3.6-27b-rag` FAILS — output is doc prose, not code.
- `deepseek-v4-pro` FAILS — `ImportError`, wrong module path.

Both failures are *format / API-hygiene*, not reasoning. The model knows the
algorithm; it just doesn't emit a runnable `main()` program per
`docs/task-design-conventions.md`.

## Idea (post-training only)

Train a **tiny formatter LoRA** with a single objective: convert any
assistant turn that contains a code block into the canonical form

```
<one-line natural-language summary>
```python
#!/usr/bin/env python3
import sys, json
def main(): ...
if __name__ == "__main__": main()
```
```

Data source: programmatically reformat existing SFT rows in
`data/generated/glm52_soft_distill_sft_iter2/` (and iter-3 when ready) into
the canonical form, then create *negative* versions (prose-only, missing
`main()`, missing `if __name__` guard) and pair them as
chosen/rejected for a 1-epoch DPO pass on top of the SFT adapter.

This is a **format-only** objective — by construction it cannot hurt
reasoning, and it directly closes the `qwen36-27b-rag` failure mode.

## Scaffold plan (this track produces)

1. `docs/rd-line-format-constrained-sft-2026-07-13.md` — full design doc.
2. `scripts/prepare_format_dpo_pairs.py` — reformat SFT rows into canonical
   form + synthesize negatives. Outputs JSONL ready for DPO trainer.
3. `configs/dpo/qwen36_formatter_dpo_v1.json` — DPO config with strict
   `chosen_signals`/`rejected_signals` for format only.
4. `tests/test_prepare_format_dpo_pairs.py` — unit tests asserting every
   chosen row has `def main()`, `if __name__ == "__main__"`, and a fenced
   python block; every rejected row violates exactly one of those.

## Success metric

On the 56-task QAOA scorecard, the formatter-LoRA-on-base (no other adapter)
must pass ≥ 50/56 with **zero "output is doc prose" failures**. Currently
baseline is 48/56 with at least 1 prose failure. Risk to general coding
benchmark must be < 0.5% (measured on `evals/benchmarks/quantum_generalization_holdout_v2_hard.txt`).

## Out of scope

- Touching model weights outside LoRA.
- Any NPU run. This track produces code + config + tests only.
- Modifying `training/qwen_sft_peft_kl.py` (owned by the distillation session).
