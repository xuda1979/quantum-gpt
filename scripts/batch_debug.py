#!/usr/bin/env python3
"""Debug batched generation slicing on ASI2 (2 samples, 64 tokens)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_100_reeval import load_examples, load_model, select_subset, setup_ascend  # noqa: E402

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

torch = setup_ascend("0,1,2,3")
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

examples, sel = (
    load_examples(
        "/root/work/quantum-gpt/data/generated/quantum_dedup_1k_glm52_soft_distill_v3/eval_sft_questions_code.jsonl",
        0,
    ),
    None,
)
_, sel = select_subset(examples, 2)
tok = AutoTokenizer.from_pretrained("/root/work/filestorage/Qwen3.8-27B", trust_remote_code=True)
model = load_model(tok, "base", torch, AutoModelForCausalLM)

print(
    f"padding_side={tok.padding_side} pad_id={tok.pad_token_id} eos_id={tok.eos_token_id} "
    f"pad={tok.pad_token!r} eos={tok.eos_token!r}",
    flush=True,
)

tok.padding_side = "right"
if tok.pad_token_id is None:
    tok.pad_token_id = tok.eos_token_id

prompts = []
for ex in sel:
    msgs = [m for m in ex["messages"] if m["role"] in ("system", "user")]
    prompts.append(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True))
enc = tok(prompts, return_tensors="pt", padding=True)
print(
    "prompt lens:",
    enc["input_ids"].shape[1],
    [
        int((enc["input_ids"][i] != tok.pad_token_id).sum())
        for i in range(enc["input_ids"].shape[0])
    ],
    flush=True,
)
inputs = {k: v.to(model.get_input_embeddings().weight.device) for k, v in enc.items()}
with torch.no_grad():
    out = model.generate(
        **inputs, max_new_tokens=64, pad_token_id=tok.pad_token_id, do_sample=False
    )
print("out shape:", out.shape, flush=True)
for i in range(out.shape[0]):
    full = tok.decode(out[i], skip_special_tokens=False)
    n_in = inputs["input_ids"].shape[1]
    sliced = tok.decode(out[i][n_in:], skip_special_tokens=True)
    print(f"--- row {i}")
    print("  n_in:", n_in, "out_len:", out.shape[1])
    print("  full[-160:]:", repr(full[-160:]))
    print("  sliced:", repr(sliced[:160]))
