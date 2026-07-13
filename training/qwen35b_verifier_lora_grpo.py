import ast
import gc
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    import torch_npu  # noqa: F401
except Exception:
    torch_npu = None

MODEL = os.environ.get("QG_MODEL", "/root/work/filestorage/Qwen3.6-35B-A3B-W8A8")
OUT = Path(
    os.environ.get(
        "QG_OUT", "/workspace/quantum-gpt/outputs/q36-35b-a3b-verifier-lora-grpo-live-0604"
    )
)
OUT.mkdir(parents=True, exist_ok=True)

STEPS = int(os.environ.get("QG_STEPS", "200000"))
SAVE_SECONDS = int(os.environ.get("QG_SAVE_SECONDS", "3600"))
MAX_NEW = int(os.environ.get("QG_MAX_NEW_TOKENS", "32"))
MAX_LEN = int(os.environ.get("QG_MAX_LEN", "256"))
LR = float(os.environ.get("QG_LR", "1e-5"))
RANK = int(os.environ.get("QG_LORA_RANK", "192"))
ALPHA = int(os.environ.get("QG_LORA_ALPHA", "384"))

TASKS = [
    {
        "id": "qaoa_maxcut",
        "prompt": (
            "Return Python code only. Implement def maxcut_energy(edges, bits): "
            "for QAOA MaxCut. Include asserts for a triangle graph."
        ),
        "required": ["def maxcut_energy", "assert", "return"],
        "tests": [
            ("maxcut_energy([(0,1),(1,2),(0,2)], [0,1,0])", 2),
            ("maxcut_energy([(0,1)], [1,1])", 0),
        ],
    },
    {
        "id": "phase_bits",
        "prompt": (
            "Return Python code only. Implement def phase_from_bits(bits): "
            "convert measured phase bits to a fraction. Include asserts."
        ),
        "required": ["def phase_from_bits", "assert", "return"],
        "tests": [
            ("phase_from_bits('100')", 0.5),
            ("phase_from_bits('001')", 0.125),
        ],
    },
    {
        "id": "safe_shell",
        "prompt": (
            "Return Python code only. Implement def is_safe_command(cmd): allow pytest, "
            "python -m pytest, npm test; reject rm -rf and secrets."
        ),
        "required": ["def is_safe_command", "return", "rm -rf"],
        "tests": [
            ("is_safe_command('pytest -q')", True),
            ("is_safe_command('rm -rf /')", False),
            ("is_safe_command('cat .env')", False),
        ],
    },
]


def extract_code(text: str) -> str:
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.S | re.I)
    return (match.group(1) if match else text).strip()


def verifier_reward(task: dict, answer: str) -> tuple[float, dict]:
    code = extract_code(answer)
    dims = {"syntax": 0.0, "unit_tests": 0.0, "task_requirements": 0.0, "safety": 1.0, "style": 0.0}
    reasons = []
    try:
        ast.parse(code)
        dims["syntax"] = 1.0
    except Exception as exc:
        reasons.append(f"syntax_fail:{str(exc)[:100]}")
        return -0.4, {
            "dimensions": dims,
            "reasons": reasons,
            "code": code[:600],
            "reward_type": "rlvr_python_unit_tests_v1",
        }

    req_hits = sum(1 for req in task["required"] if req.lower() in code.lower())
    dims["task_requirements"] = req_hits / max(1, len(task["required"]))
    unsafe = ["os.system", "subprocess", "eval(", "exec(", "open('.env", 'open(".env']
    if any(item in code.lower() for item in unsafe):
        dims["safety"] = 0.0
        reasons.append("unsafe_api")

    namespace = {}
    try:
        safe_builtins = {
            "len": len,
            "range": range,
            "sum": sum,
            "int": int,
            "float": float,
            "str": str,
            "list": list,
            "tuple": tuple,
            "enumerate": enumerate,
            "zip": zip,
            "all": all,
            "any": any,
            "abs": abs,
            "ValueError": ValueError,
            "TypeError": TypeError,
        }
        exec(code, {"__builtins__": safe_builtins}, namespace)
        passed = 0
        for expr, expected in task["tests"]:
            got = eval(expr, {"__builtins__": {}}, namespace)
            passed += int(got == expected)
        dims["unit_tests"] = passed / len(task["tests"])
    except Exception as exc:
        reasons.append(f"exec_fail:{str(exc)[:120]}")

    dims["style"] = 1.0 if "def " in code and "return" in code and len(code) < 3000 else 0.0
    total = (
        0.20 * dims["syntax"]
        + 0.40 * dims["unit_tests"]
        + 0.15 * dims["task_requirements"]
        + 0.15 * dims["safety"]
        + 0.10 * dims["style"]
    )
    if dims["unit_tests"] == 1.0 and dims["safety"] == 1.0:
        total = min(1.0, total + 0.10)
    return max(-1.0, min(1.0, total)), {
        "dimensions": dims,
        "reasons": reasons,
        "code": code[:800],
        "reward_type": "rlvr_python_unit_tests_v1",
    }


def log_json(obj: dict, filename: str = "training.log") -> None:
    with open(OUT / filename, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(obj, ensure_ascii=False) + "\n")


def main() -> None:
    npu_count = torch.npu.device_count() if hasattr(torch, "npu") else 0
    max_memory = {
        i: os.environ.get("QG_MAX_MEMORY_PER_NPU", "54GiB") for i in range(max(npu_count, 1))
    }
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL,
        local_files_only=True,
        trust_remote_code=True,
        dtype=torch.bfloat16,
        device_map="auto",
        max_memory=max_memory,
        low_cpu_mem_usage=True,
    )
    model.config.use_cache = False
    model = get_peft_model(
        model,
        LoraConfig(
            r=RANK,
            lora_alpha=ALPHA,
            lora_dropout=0.0,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "v_proj"],
        ),
    )
    trainable = sum(param.numel() for param in model.parameters() if param.requires_grad)
    optimizer = torch.optim.AdamW(
        [param for param in model.parameters() if param.requires_grad], lr=LR
    )
    first_device = next(
        (param.device for param in model.parameters() if param.device.type != "meta"),
        torch.device("npu:0"),
    )
    model.train()
    log_json(
        {
            "stage": "load_complete",
            "trainable_parameters": trainable,
            "reward_type": "rlvr_python_unit_tests_v1",
        }
    )
    last_save = 0.0

    for step in range(1, STEPS + 1):
        task = TASKS[step % len(TASKS)]
        enc = tokenizer(task["prompt"], return_tensors="pt", truncation=True, max_length=MAX_LEN)
        enc = {key: value.to(first_device) for key, value in enc.items()}
        with torch.no_grad():
            gen = model.generate(
                **enc,
                max_new_tokens=MAX_NEW,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id,
                use_cache=False,
            )
        answer = tokenizer.decode(gen[0][enc["input_ids"].shape[1] :], skip_special_tokens=True)
        reward, judge = verifier_reward(task, answer)
        full = tokenizer(
            task["prompt"] + "\n" + answer,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_LEN + MAX_NEW,
        )
        full = {key: value.to(first_device) for key, value in full.items()}
        out = model(**full, labels=full["input_ids"].clone())
        loss = out.loss * (1.0 - float(reward))
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(
            [param for param in model.parameters() if param.requires_grad], 1.0
        )
        optimizer.step()
        record = {
            "step": step,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "mean_reward": reward,
            "pass_rate": 1.0 if reward >= 0.85 else 0.0,
            "loss": float(loss.detach().float().cpu()),
            "model": "Qwen3.6-35B-A3B-W8A8",
            "training_mode": "single_process_8npu_sharded_lora_grpo",
            "reward_type": "rlvr_python_unit_tests_v1",
            "task_id": task["id"],
            "trainable_parameters": trainable,
            "reward_judge": judge,
            "sample": answer[:240],
        }
        log_json(record, "grpo_step_metrics.jsonl")
        log_json({"stage": "grpo_step", "record": record})
        live = {
            "status": "running",
            "planned_steps": STEPS,
            "recorded_steps": step,
            "last_record": record,
            "summary": {
                "latest_reward": reward,
                "latest_pass_rate": record["pass_rate"],
                "latest_loss": record["loss"],
            },
            "alerts": [],
        }
        now = time.time()
        if step == 1 or now - last_save >= SAVE_SECONDS:
            ckpt = OUT / f"checkpoint-step-{step:06d}"
            ckpt.mkdir(exist_ok=True)
            model.save_pretrained(ckpt)
            tokenizer.save_pretrained(ckpt)
            checkpoint = {
                "step": step,
                "checkpoint_dir": str(ckpt),
                "timestamp_utc": record["timestamp_utc"],
            }
            (OUT / "latest_checkpoint.json").write_text(json.dumps(checkpoint, indent=2) + "\n")
            live["latest_checkpoint"] = checkpoint
            last_save = now
        (OUT / "live_status.json").write_text(json.dumps(live, ensure_ascii=False, indent=2) + "\n")
        gc.collect()
        if hasattr(torch, "npu"):
            torch.npu.empty_cache()


if __name__ == "__main__":
    main()
