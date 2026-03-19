# Qwen 3.5 Verified Snapshot Handoff

## Purpose

The current project blocker is not Huanxin shell reachability anymore. It is acquisition of the exact local snapshot for:

- `Qwen/Qwen3.5-1.5B-Instruct`

This note turns that blocker into an exact handoff sequence once a real local snapshot directory exists.

## Preconditions

Do not start this sequence unless all of the following are true:

1. local eval gate is green
2. the provided local snapshot directory passes `training/verify_qwen_snapshot.py`
3. Huanxin `ai2` shell access is currently usable from this machine

## 1. Verify the local snapshot honestly

Run:

```bash
python3 training/verify_qwen_snapshot.py /path/to/Qwen3.5-1.5B-Instruct
```

Required outcome:

- `status: ok`
- tokenizer files present
- model weights present, either as concrete shard files or a valid weight index file
- `config.json` metadata identifies a Qwen-family architecture
- expected `Qwen3.5-1.5B-Instruct` substring is found in path or metadata

If this fails, stop. Do not transfer a maybe-model into Huanxin.

## 2. Re-run the mandatory local gate before transfer

Even if the snapshot is valid, do not skip the project gate:

```bash
python3 evals/runner/run_eval.py
python3 -m py_compile training/verify_qwen_snapshot.py training/huanxin_cpu_smoke.py training/qwen_sft_peft.py
```

Only continue if all checks pass.

## 3. Remote target layout

Place the verified snapshot under:

```text
/root/root/work/quantum-gpt/models/Qwen3.5-1.5B-Instruct
```

Reason:

- keeps the remote smoke path explicit
- avoids depending on remote HF resolution once a real local snapshot exists
- preserves a stable model path for later PEFT smoke commands

## 4. Transfer rule

Transfer only the validated snapshot and the already-audited bootstrap code needed to use it.

Minimum required remote files:

- `training/huanxin_cpu_smoke.py`
- `training/qwen_sft_peft.py`
- `training/requirements-huanxin-cpu.txt`
- `data/seed/splits-auto-seed/train.jsonl`
- `data/seed/splits-auto-seed/val.jsonl`
- verified snapshot directory under `models/Qwen3.5-1.5B-Instruct`

Do not claim progress from a partial or guessed transfer.

## 5. First remote smoke against the transferred local path

After transfer, run this in `ai2`:

```bash
cd /root/root/work/quantum-gpt
python3 training/huanxin_cpu_smoke.py \
  --model-name /root/root/work/quantum-gpt/models/Qwen3.5-1.5B-Instruct \
  --dataset data/seed/splits-auto-seed/train.jsonl
```

Success means:

- imports work
- dataset loads
- tokenizer loads from the transferred local snapshot path

That is the first honest proof that the acquisition blocker is cleared.

## 6. Optional remote full-model smoke

Only if tokenizer smoke passes:

```bash
cd /root/root/work/quantum-gpt
python3 training/huanxin_cpu_smoke.py \
  --model-name /root/root/work/quantum-gpt/models/Qwen3.5-1.5B-Instruct \
  --dataset data/seed/splits-auto-seed/train.jsonl \
  --load-model
```

If this fails, record the exact error. That would narrow the blocker to model-load compatibility or resource limits, not artifact acquisition.

## 7. First minimal PEFT startup smoke

Only if the model-load smoke passes:

```bash
cd /root/root/work/quantum-gpt
python3 training/qwen_sft_peft.py \
  --model-name /root/root/work/quantum-gpt/models/Qwen3.5-1.5B-Instruct \
  --train-file data/seed/splits-auto-seed/train.jsonl \
  --eval-file data/seed/splits-auto-seed/val.jsonl \
  --output-dir outputs/qwen35-1p5b-peft-smoke \
  --device cpu \
  --max-steps 1 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 1
```

That is the first command that deserves to be called a training-loop smoke.

## What counts as success

A real blocker transition would look like this:

1. local snapshot verified
2. snapshot transferred to `ai2`
3. tokenizer smoke succeeds from the local remote path

Anything short of that is still pre-unblocker work.

## What not to do

Do not:

- retry anonymous remote Hugging Face resolution again
- silently replace the target with Qwen 2.5
- call a directory valid just because its name contains `Qwen3.5`
- claim remote fine-tuning progress before the local-path tokenizer smoke succeeds
