
set -e
cd /root/work/quantum-gpt
mkdir -p /root/work/quantum-gpt/outputs/ibm_baseline_c10610
echo "[battery] start $(date -u +%Y-%m-%dT%H:%M:%SZ)" > /root/work/quantum-gpt/outputs/ibm_baseline_c10610/battery.log

if [ ! -f /root/work/quantum-gpt/outputs/ibm_baseline_c10610/base_qhe/ibm_eval_qhe_completion_base.json ]; then
  python3 harness/scripts/c10609_ibm_qiskit_humaneval_eval.py \
    --base-model /root/work/filestorage/Qwen3.8-27B \
    --style qhe_completion \
    --out-dir /root/work/quantum-gpt/outputs/ibm_baseline_c10610/base_qhe \
    $( [ -f /root/work/quantum-gpt/outputs/ibm_baseline_c10610/base_qhe/journal.jsonl ] && echo --resume-journal /root/work/quantum-gpt/outputs/ibm_baseline_c10610/base_qhe/journal.jsonl ) \
    >> /root/work/quantum-gpt/outputs/ibm_baseline_c10610/battery.log 2>&1
fi
echo "[battery] run1 base_qhe done $(date -u +%H:%M:%SZ)" >> /root/work/quantum-gpt/outputs/ibm_baseline_c10610/battery.log

if [ ! -f /root/work/quantum-gpt/outputs/ibm_baseline_c10610/base_hard/ibm_eval_hard_instruction_base.json ]; then
  python3 harness/scripts/c10609_ibm_qiskit_humaneval_eval.py \
    --base-model /root/work/filestorage/Qwen3.8-27B \
    --style hard_instruction \
    --out-dir /root/work/quantum-gpt/outputs/ibm_baseline_c10610/base_hard \
    $( [ -f /root/work/quantum-gpt/outputs/ibm_baseline_c10610/base_hard/journal.jsonl ] && echo --resume-journal /root/work/quantum-gpt/outputs/ibm_baseline_c10610/base_hard/journal.jsonl ) \
    >> /root/work/quantum-gpt/outputs/ibm_baseline_c10610/battery.log 2>&1
fi
echo "[battery] run2 base_hard done $(date -u +%H:%M:%SZ)" >> /root/work/quantum-gpt/outputs/ibm_baseline_c10610/battery.log

if [ ! -f /root/work/quantum-gpt/outputs/ibm_baseline_c10610/champ_qhe/ibm_eval_qhe_completion_adapter.json ]; then
  python3 harness/scripts/c10609_ibm_qiskit_humaneval_eval.py \
    --base-model /root/work/filestorage/Qwen3.8-27B \
    --adapter /root/work/quantum-gpt/outputs/sft-27b-q38-v22-resume-20261023T081500Z/checkpoints/step-1941/adapter \
    --style qhe_completion \
    --out-dir /root/work/quantum-gpt/outputs/ibm_baseline_c10610/champ_qhe \
    $( [ -f /root/work/quantum-gpt/outputs/ibm_baseline_c10610/champ_qhe/journal.jsonl ] && echo --resume-journal /root/work/quantum-gpt/outputs/ibm_baseline_c10610/champ_qhe/journal.jsonl ) \
    >> /root/work/quantum-gpt/outputs/ibm_baseline_c10610/battery.log 2>&1
fi
echo "[battery] run3 champ_qhe done $(date -u +%H:%M:%SZ)" >> /root/work/quantum-gpt/outputs/ibm_baseline_c10610/battery.log

if [ ! -f /root/work/quantum-gpt/outputs/ibm_baseline_c10610/champ_hard/ibm_eval_hard_instruction_adapter.json ]; then
  python3 harness/scripts/c10609_ibm_qiskit_humaneval_eval.py \
    --base-model /root/work/filestorage/Qwen3.8-27B \
    --adapter /root/work/quantum-gpt/outputs/sft-27b-q38-v22-resume-20261023T081500Z/checkpoints/step-1941/adapter \
    --style hard_instruction \
    --out-dir /root/work/quantum-gpt/outputs/ibm_baseline_c10610/champ_hard \
    $( [ -f /root/work/quantum-gpt/outputs/ibm_baseline_c10610/champ_hard/journal.jsonl ] && echo --resume-journal /root/work/quantum-gpt/outputs/ibm_baseline_c10610/champ_hard/journal.jsonl ) \
    >> /root/work/quantum-gpt/outputs/ibm_baseline_c10610/battery.log 2>&1
fi
echo "[battery] run4 champ_hard done $(date -u +%H:%M:%SZ)" >> /root/work/quantum-gpt/outputs/ibm_baseline_c10610/battery.log
echo BATTERY_DONE > /root/work/quantum-gpt/outputs/ibm_baseline_c10610/DONE
