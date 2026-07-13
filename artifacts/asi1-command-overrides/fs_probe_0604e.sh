set -euo pipefail
echo __ASI1_FS_PROBE_START__
pwd
whoami
python3 --version || true
for d in /workspace/quantum-gpt /root/software/quantum-gpt /root/work/quantum-gpt /root/work/filestorage/Qwen3.6-35B-A3B /root/work/filestorage/Qwen3.6-27B; do
  echo __PATH__ "$d"
  if [ -e "$d" ]; then
    ls -ld "$d"
    find "$d" -maxdepth 2 -type f \( -name agentic_grpo_trainer.py -o -name run_asi1_agentic_grpo_from_env.sh -o -name config.json \) | head -50
  else
    echo missing
  fi
done
python3 - <<'PY'
import importlib.util
for m in ['torch','torch_npu','transformers','peft','accelerate']:
    print(m, bool(importlib.util.find_spec(m)))
PY
echo __ASI1_FS_PROBE_DONE__
