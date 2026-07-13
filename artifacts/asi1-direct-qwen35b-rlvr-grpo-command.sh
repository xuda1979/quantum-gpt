set -euo pipefail
cd /workspace
if [ ! -d /workspace/quantum-gpt ]; then mkdir -p /workspace/quantum-gpt; fi
cd /workspace/quantum-gpt
if command -v rclone >/dev/null 2>&1 && [ -s /tmp/iner-rclone.conf ]; then
  rclone sync iner:jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt /workspace/quantum-gpt --config /tmp/iner-rclone.conf --s3-no-check-bucket --exclude 'outputs/**' --exclude 'models/**' --exclude 'artifacts/**' --exclude 'memory/**' --exclude 'logs/**' --exclude 'browser-automation/profile/**' --progress || true
fi
python3 -m py_compile training/qwen35b_benchmark_rlvr_grpo.py
bash -n scripts/launch_qwen36_35b_a3b_direct_rlvr_grpo_asi1.sh
python3 - <<'PY'
import tempfile
from pathlib import Path
import training.qwen35b_benchmark_rlvr_grpo as t
t.ROOT=Path.cwd(); t.TASK_ROOTS=[Path('evals/tasks/quantum'),Path('evals/tasks/software')]; t.HOLDOUT_BENCHMARKS=[Path('evals/benchmarks/quantum_generalization_holdout_v1.txt'),Path('evals/benchmarks/quantum_generalization_holdout_v2_hard.txt')]; t.OUT=Path(tempfile.mkdtemp(prefix='qg_task_prelaunch_')); t.TRAIN_DOMAINS={'quantum','software'}; t.PROMPT_VARIANTS_PER_TASK=4
tasks=t.load_tasks(); hold=t.load_holdout_ids(t.HOLDOUT_BENCHMARKS); ids={t.normalize_task_id(str(x['meta']['id'])) for x in tasks}
assert not ids & hold, sorted(ids & hold)
assert len(tasks) >= 100, len(tasks)
for task in tasks[:8]:
    assert 'tests.py' not in t.build_prompt(task)
    score, judge=t.score_candidate(task, task['candidate'])
    assert judge['dimensions']['hidden_verifier'] == 1.0, task['id']
print({'tasks': len(tasks), 'seed': len({x['meta']['id'] for x in tasks}), 'reward': t.REWARD_VERSION})
PY
export QG_STEPS=200000
export QG_SAVE_SECONDS=3600
export QG_GROUP_SIZE=2
export QG_MAX_NEW_TOKENS=384
export QG_MAX_LEN=2048
export QG_LORA_RANK=768
export QG_LORA_ALPHA=1536
export QG_LORA_TARGET_MODULES=q_proj,v_proj
export QG_MIN_TRAINABLE_PARAMETERS=90000000
export QG_MAX_TRAINABLE_PARAMETERS=140000000
exec bash scripts/launch_qwen36_35b_a3b_direct_rlvr_grpo_asi1.sh
