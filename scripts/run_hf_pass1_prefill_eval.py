#!/usr/bin/env python3
"""Run HF generation from pre-tokenized prompts to bypass remote tokenizer skew."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.runtime_overlay import configure_runtime_overlay_from_env

configure_runtime_overlay_from_env()

import torch
from transformers import AutoConfig, AutoModelForCausalLM

from scripts.run_hf_pass1_eval import TOKEN_BUDGET_PRESETS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--prefill-json", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--max-new-tokens", type=int, default=192)
    parser.add_argument(
        "--token-budget-preset",
        choices=sorted(TOKEN_BUDGET_PRESETS),
        default=None,
    )
    return parser.parse_args()


def load_model(model_path: Path, device: str):
    AutoConfig.from_pretrained(str(model_path), trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        torch_dtype="auto",
    ).to(device)
    generation_config = getattr(model, "generation_config", None)
    if generation_config is not None:
        generation_config.do_sample = False
        generation_config.temperature = 1.0
        generation_config.top_p = 1.0
        generation_config.top_k = 50
    model.eval()
    return model


def main() -> int:
    args = parse_args()
    if args.token_budget_preset is not None:
        args.max_new_tokens = TOKEN_BUDGET_PRESETS[args.token_budget_preset]

    payload = json.loads(args.prefill_json.read_text(encoding="utf-8"))
    pad_token_id = payload.get("pad_token_id") or payload.get("eos_token_id")
    if pad_token_id is None:
        raise SystemExit("prefill payload is missing both pad_token_id and eos_token_id")

    print(
        json.dumps(
            {
                "stage": "load_base_start",
                "model": str(args.base_model),
                "device": args.device,
                "records": len(payload.get("records", [])),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    model = load_model(args.base_model, args.device)
    print(json.dumps({"stage": "load_base_done"}, ensure_ascii=False), flush=True)

    started_at = time.time()
    outputs: list[dict[str, object]] = []
    for index, record in enumerate(payload.get("records", []), start=1):
        print(
            json.dumps(
                {"stage": "generate", "index": index, "total": len(payload["records"]), "task_id": record["task_id"]},
                ensure_ascii=False,
            ),
            flush=True,
        )
        input_ids = torch.tensor([record["input_ids"]], dtype=torch.long, device=args.device)
        attention_mask = torch.tensor([record["attention_mask"]], dtype=torch.long, device=args.device)
        with torch.inference_mode():
            generated = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                pad_token_id=int(pad_token_id),
            )
        prompt_len = input_ids.shape[1]
        outputs.append(
            {
                "task_id": record["task_id"],
                "candidate_file": record["candidate_file"],
                "completion_ids": generated[0][prompt_len:].tolist(),
            }
        )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(
            {
                "base_model": str(args.base_model),
                "prefill_json": str(args.prefill_json),
                "device": args.device,
                "max_new_tokens": args.max_new_tokens,
                "duration_seconds": time.time() - started_at,
                "outputs": outputs,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"stage": "done", "output_json": str(args.output_json)}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
