#!/usr/bin/env bash
set -euo pipefail

echo __ASI1_DIRECT_SELFJUDGE_RLVR_BOOT__

ROOT="${QG_ROOT:-/workspace/quantum-gpt}"
cd "$ROOT"

python3 -m py_compile training/qwen35b_benchmark_rlvr_grpo.py
bash -n scripts/launch_qwen36_35b_a3b_direct_rlvr_grpo_asi1.sh

python3 - <<'PY'
import tempfile
from pathlib import Path
import training.qwen35b_benchmark_rlvr_grpo as t

assert t.REWARD_VERSION == "quantum_software_rlvr_professional_self_judge_hidden_v5", t.REWARD_VERSION
assert "model_self_judge" in t.REWARD_WEIGHTS
assert set(t.SELF_JUDGE_DIMENSIONS) == {
    "grammar_correctness",
    "algorithmic_correctness",
    "quantum_correctness",
    "code_length_structure",
    "robustness",
    "interface_compliance",
    "safety",
}

t.ROOT = Path.cwd()
t.TASK_ROOTS = [Path("evals/tasks/quantum"), Path("evals/tasks/software")]
t.HOLDOUT_BENCHMARKS = [
    Path("evals/benchmarks/quantum_generalization_holdout_v1.txt"),
    Path("evals/benchmarks/quantum_generalization_holdout_v2_hard.txt"),
    Path("evals/benchmarks/agentic_software_engineering_holdout_v1.txt"),
    Path("evals/benchmarks/gemma4_quantum_generalization_holdout_v1.txt"),
]
t.OUT = Path(tempfile.mkdtemp(prefix="qg_task_prelaunch_"))
t.TRAIN_DOMAINS = {"quantum", "software"}
t.PROMPT_VARIANTS_PER_TASK = 4

tasks = t.load_tasks()
hold = t.load_holdout_ids(t.HOLDOUT_BENCHMARKS)
ids = {t.normalize_task_id(str(task["meta"]["id"])) for task in tasks}
assert not ids & hold, sorted(ids & hold)
assert len(tasks) >= 100, len(tasks)
for task in tasks[:8]:
    prompt = t.build_prompt(task)
    assert "tests.py" not in prompt
    if task.get("domain") == "quantum":
        assert "Professional quantum-algorithm coding requirements" in prompt
    scores = {name: 1.0 for name in t.SELF_JUDGE_DIMENSIONS}
    _score, judge = t.score_candidate(task, task["candidate"], self_judge_scores=scores)
    assert judge["dimensions"]["hidden_verifier"] == 1.0, task["id"]
    assert judge["dimensions"]["model_self_judge"] == 1.0, task["id"]

print({
    "tasks": len(tasks),
    "seed": len({task["meta"]["id"] for task in tasks}),
    "reward": t.REWARD_VERSION,
    "self_judge_dimensions": list(t.SELF_JUDGE_DIMENSIONS),
})
PY

export QG_MODEL="${QG_MODEL:-/root/work/filestorage/Qwen3.6-35B-A3B}"
export ASCEND_RT_VISIBLE_DEVICES="${ASCEND_RT_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"
export QG_STEPS="${QG_STEPS:-200000}"
export QG_SAVE_SECONDS="${QG_SAVE_SECONDS:-3600}"
export QG_GROUP_SIZE="${QG_GROUP_SIZE:-2}"
export QG_MAX_NEW_TOKENS="${QG_MAX_NEW_TOKENS:-384}"
export QG_MAX_LEN="${QG_MAX_LEN:-2048}"
export QG_SELF_JUDGE_ENABLED="${QG_SELF_JUDGE_ENABLED:-1}"
export QG_SELF_JUDGE_MAX_NEW_TOKENS="${QG_SELF_JUDGE_MAX_NEW_TOKENS:-192}"
export QG_SELF_JUDGE_MAX_LEN="${QG_SELF_JUDGE_MAX_LEN:-3072}"
export QG_LORA_RANK="${QG_LORA_RANK:-768}"
export QG_LORA_ALPHA="${QG_LORA_ALPHA:-1536}"
export QG_LORA_TARGET_MODULES="${QG_LORA_TARGET_MODULES:-q_proj,v_proj}"
export QG_MIN_TRAINABLE_PARAMETERS="${QG_MIN_TRAINABLE_PARAMETERS:-90000000}"
export QG_MAX_TRAINABLE_PARAMETERS="${QG_MAX_TRAINABLE_PARAMETERS:-140000000}"

exec bash scripts/launch_qwen36_35b_a3b_direct_rlvr_grpo_asi1.sh
