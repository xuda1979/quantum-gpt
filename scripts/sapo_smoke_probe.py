#!/usr/bin/env python3
"""SAPO promotion-leg smoke probe (Research Audit T2, 2026-08-27).

The full 18-task promotion leg is expensive and the run-5 step-26 class
(0/18: GREEDY temp-0 decoding collapsed into unparseable prompt-echoes while
the trainer's SAMPLED rollouts looked healthy) showed that a greedy-only
probe pass is a trap. This probe measures the checkpoint on a small task set
in BOTH modes BEFORE the full leg:

  - Pass@1  (greedy, temperature 0):  1 candidate per task; task parses?
  - Pass@K=4 (sampled, temperature 0.6): K=4 candidates per task; task
    counts as passed if ANY of the K candidates parses.

REFUSAL GATE: if the GREEDY syntax rate < 0.6 the full promotion leg is
BLOCKED (no full leg on a greedy-fragile adapter). Sampled Pass@K=4 is
reported informationally alongside.

Usage (box, NPU; mirrors the promotion-leg COMMON flags):
  python3 scripts/sapo_smoke_probe.py \
    --ckpt outputs/<run>/step_<N>_adapter \
    --base-model /root/work/filestorage/Qwen3.6-27B \
    --device npu --device-map balanced-layers --npu-max-memory-gib 54 \
    --task-id-file evals/benchmarks/sapo_smoke_probe_v1_3.txt \
    --greedy-k 1 --sample-k 4 --sample-temperature 0.6 \
    --greedy-syntax-min 0.6 \
    --run-name sapo-smoke-<label>-<utcts> --out /tmp/smoke_<label>.json

Exit code 0 = CLEAR (leg allowed), 3 = BLOCKED (refusal gate fired).
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.adapter_probe_checked import (  # noqa: E402
    _apply_adapter_checked,
)
from scripts.run_hf_pass1_eval import (  # noqa: E402
    generate_candidate,
    load_text_backend,
    render_prompt,
)

# ─────────────────────────────────────────────────────────────────────────────
# Pure logic (hermetic, TDD-locked in tests/test_sapo_smoke_probe.py)
# ─────────────────────────────────────────────────────────────────────────────


def candidate_parses(text: str) -> bool:
    """True if the generated text is parseable Python (the probe's syntax
    gate — the run-5 s26 failure class was prompt-echoes with Unicode math
    that ast.parse rejects)."""
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False


def syntax_rate(parseable: list[bool]) -> float:
    """Fraction of parseable candidates (greedy Pass@1 over the task set)."""
    if not parseable:
        return 0.0
    return sum(1 for ok in parseable if ok) / len(parseable)


def pass_at_k_estimator(n: int, c: int, k: int) -> float:
    """Unbiased pass@k (Chen et al., Codex 2021):
    pass@k = 1 - C(n-c, k) / C(n, k), with n samples and c correct.

    Exact on synthetic pass sets; degenerates to "any of k correct" when
    k == n (the probe's default n=k=4) and stays unbiased when n > k.
    """
    if n <= 0 or k <= 0 or c < 0:
        return 0.0
    if c == 0:
        return 0.0
    if k >= n:
        return 1.0
    from math import comb

    return 1.0 - comb(n - c, k) / comb(n, k)


def pass_at_k(task_results: list[list[bool]], k: int | None = None) -> float:
    """Sampled Pass@K over the task set using the unbiased estimator.

    Each task contributes (n=len(samples), c=parseable count); the metric is
    the mean over tasks of the estimator at k (default: k == n per task).
    """
    if not task_results:
        return 0.0
    total = 0.0
    for samples in task_results:
        n = len(samples)
        c = sum(1 for ok in samples if ok)
        total += pass_at_k_estimator(n, c, k if k is not None else n)
    return total / len(task_results)


def gate_verdict(
    greedy_rate: float, min_rate: float = 0.6, measured_tasks: int | None = None
) -> str:
    """Refusal gate: greedy syntax rate below min_rate (or no evidence at
    all) → BLOCKED; the full promotion leg must not run on a greedy-fragile
    adapter. The boundary is inclusive: rate >= min_rate clears."""
    if measured_tasks is not None and measured_tasks <= 0:
        return "BLOCKED"  # no evidence is never a silent CLEAR
    return "CLEAR" if greedy_rate >= min_rate else "BLOCKED"


# ─────────────────────────────────────────────────────────────────────────────
# Probe driver (box only — loads the real model + adapter)
# ─────────────────────────────────────────────────────────────────────────────


def _load_task_ids(path: Path) -> list[str]:
    ids: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            ids.append(line)
    return ids


def offline_probe(candidates_dir: Path, task_ids: list[str], sample_k: int = 4) -> dict:
    """Run the probe OFFLINE on cached candidate files (no model load).

    Layout expected per task ``<id>``:
      <id>.py          — greedy (temp 0) candidate
      <id>__k0..k<K>.py — the K sampled (temp 0.6) candidates
    Any missing greedy file makes the task count as not parseable; missing
    sampled files are treated as non-parseable draws.
    """
    greedy_results: list[bool] = []
    sampled_results: list[list[bool]] = []
    per_task: dict[str, dict] = {}
    for task_id in task_ids:
        greedy_path = candidates_dir / f"{task_id}.py"
        greedy_ok = greedy_path.exists() and candidate_parses(
            greedy_path.read_text(encoding="utf-8")
        )
        greedy_results.append(greedy_ok)
        sampled_oks: list[bool] = []
        for i in range(sample_k):
            p = candidates_dir / f"{task_id}__k{i}.py"
            sampled_oks.append(p.exists() and candidate_parses(p.read_text(encoding="utf-8")))
        sampled_results.append(sampled_oks)
        per_task[task_id] = {
            "greedy_parseable": greedy_ok,
            "sampled_parseable": sum(1 for ok in sampled_oks if ok),
            "sampled_k": sample_k,
        }
    greedy_rate = syntax_rate(greedy_results)
    sampled_rate = pass_at_k(sampled_results, k=sample_k)
    verdict = gate_verdict(greedy_rate, min_rate=0.6, measured_tasks=len(task_ids))
    return {
        "ckpt": str(candidates_dir),
        "offline": True,
        "task_ids": task_ids,
        "greedy": {"mode": "temp0", "k": 1, "syntax_rate": greedy_rate, "per_task": per_task},
        "sampled": {"mode": "temp0.6", "k": sample_k, "pass_at_k": sampled_rate},
        "gate": {"min_greedy_syntax_rate": 0.6, "verdict": verdict},
    }


def probe(  # noqa: PLR0913
    ckpt: Path,
    base_model_path: Path,
    *,
    task_id_file: Path,
    device: str = "npu",
    device_map: str = "balanced-layers",
    npu_max_memory_gib: int = 54,
    max_new_tokens: int = 192,
    greedy_k: int = 1,
    sample_k: int = 4,
    sample_temperature: float = 0.6,
    greedy_syntax_min: float = 0.6,
    run_dir: Path,
) -> dict:
    """Measure greedy Pass@1 and sampled Pass@K on the task set and apply
    the refusal gate. Returns the full evidence record."""
    from scripts.run_hf_pass1_eval import load_model

    task_ids = _load_task_ids(task_id_file)
    system_prompt = (run_dir / "SYSTEM_PROMPT.txt").read_text(encoding="utf-8")
    backend = load_text_backend(base_model_path)

    print(
        json.dumps({"stage": "probe_load_start", "ckpt": str(ckpt)}, ensure_ascii=False), flush=True
    )
    base = load_model(
        base_model_path,
        device,
        device_map=device_map,
        npu_max_memory_gib=npu_max_memory_gib,
    )
    merged = _apply_adapter_checked(base, ckpt)
    print(json.dumps({"stage": "probe_load_done"}, ensure_ascii=False), flush=True)

    greedy_results: list[bool] = []
    sampled_results: list[list[bool]] = []
    per_task: dict[str, dict] = {}
    for task_id in task_ids:
        prompt_path = run_dir / "prompts" / f"{task_id}.txt"
        user_prompt = prompt_path.read_text(encoding="utf-8")
        render_prompt(backend, system_prompt=system_prompt, user_prompt=user_prompt)

        # Greedy Pass@1 (temperature 0 → do_sample=False).
        greedy_text = generate_candidate(
            merged,
            backend,
            system_prompt,
            user_prompt,
            max_new_tokens=max_new_tokens,
            temperature=0.0,
            device=device,
        )
        greedy_ok = candidate_parses(greedy_text)
        greedy_results.append(greedy_ok)

        # Sampled Pass@K (temperature 0.6 → do_sample=True, K draws).
        sampled_oks: list[bool] = []
        for _ in range(sample_k):
            text = generate_candidate(
                merged,
                backend,
                system_prompt,
                user_prompt,
                max_new_tokens=max_new_tokens,
                temperature=sample_temperature,
                device=device,
            )
            sampled_oks.append(candidate_parses(text))
        sampled_results.append(sampled_oks)

        per_task[task_id] = {
            "greedy_parseable": greedy_ok,
            "greedy_chars": len(greedy_text),
            "sampled_parseable": sum(1 for ok in sampled_oks if ok),
            "sampled_k": sample_k,
        }
        print(
            json.dumps(
                {
                    "stage": "probe_task",
                    "task_id": task_id,
                    "greedy_ok": greedy_ok,
                    "sampled_ok": any(sampled_oks),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    greedy_rate = syntax_rate(greedy_results)
    sampled_rate = pass_at_k(sampled_results)
    verdict = gate_verdict(greedy_rate, min_rate=greedy_syntax_min, measured_tasks=len(task_ids))

    record = {
        "ckpt": str(ckpt),
        "task_ids": task_ids,
        "greedy": {
            "mode": "temp0",
            "k": greedy_k,
            "syntax_rate": greedy_rate,
            "per_task": per_task,
        },
        "sampled": {"mode": f"temp{sample_temperature}", "k": sample_k, "pass_at_k": sampled_rate},
        "gate": {"min_greedy_syntax_rate": greedy_syntax_min, "verdict": verdict},
    }
    return record


def main() -> int:
    parser = argparse.ArgumentParser(
        description="SAPO promotion-leg smoke probe (Pass@1 + Pass@K=4, refusal gate)"
    )
    parser.add_argument("--ckpt", type=Path, default=None)
    parser.add_argument("--base-model", type=Path, default=None)
    parser.add_argument("--device", default="npu")
    parser.add_argument("--device-map", default="balanced-layers")
    parser.add_argument("--npu-max-memory-gib", type=int, default=54)
    parser.add_argument("--max-new-tokens", type=int, default=192)
    parser.add_argument("--task-id-file", type=Path, required=True)
    parser.add_argument("--greedy-k", type=int, default=1)
    parser.add_argument("--sample-k", type=int, default=4)
    parser.add_argument("--sample-temperature", type=float, default=0.6)
    parser.add_argument("--greedy-syntax-min", type=float, default=0.6)
    parser.add_argument("--run-name", type=str, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--offline",
        type=Path,
        default=None,
        help="Run on cached candidate files (no model load): dir with "
        "<task>.py (greedy) + <task>__k0..k<K>.py (sampled).",
    )
    args = parser.parse_args()

    run_dir = ROOT / "evals" / "runs" / args.run_name
    if args.offline is not None:
        task_ids = _load_task_ids(args.task_id_file)
        record = offline_probe(args.offline, task_ids, sample_k=args.sample_k)
        args.out.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        print(
            json.dumps(
                {"stage": "probe_done_offline", "record_path": str(args.out), **record["gate"]},
                ensure_ascii=False,
            ),
            flush=True,
        )
        return 0 if record["gate"]["verdict"] == "CLEAR" else 3
    if args.ckpt is None or args.base_model is None:
        parser.error("--ckpt and --base-model are required unless --offline is given")
    record = probe(
        args.ckpt,
        args.base_model,
        task_id_file=args.task_id_file,
        device=args.device,
        device_map=args.device_map,
        npu_max_memory_gib=args.npu_max_memory_gib,
        max_new_tokens=args.max_new_tokens,
        greedy_k=args.greedy_k,
        sample_k=args.sample_k,
        sample_temperature=args.sample_temperature,
        greedy_syntax_min=args.greedy_syntax_min,
        run_dir=run_dir,
    )
    args.out.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        json.dumps(
            {"stage": "probe_done", "record_path": str(args.out), **record["gate"]},
            ensure_ascii=False,
        ),
        flush=True,
    )
    return 0 if record["gate"]["verdict"] == "CLEAR" else 3


if __name__ == "__main__":
    raise SystemExit(main())
