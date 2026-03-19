# Qwen 2.5 Public Fallback Handoff

## Purpose

This note exists for the case where the project explicitly decides to use the
smallest currently verified public execution checkpoint instead of waiting for a
real source for `Qwen/Qwen3.5-1.5B-Instruct`.

It does **not** change the project target by itself.

It only answers a narrower operational question:

- if the source decision is made in favor of the public 1.5B fallback,
  what is the exact next command sequence from local verification to Huanxin
  remote smoke?

Current fallback candidate:

- `Qwen/Qwen2.5-1.5B-Instruct`

## When to use this note

Use this note only if one of these becomes true:

1. the project explicitly approves `Qwen/Qwen2.5-1.5B-Instruct` as the
   executable fallback checkpoint
2. no real Qwen 3.5 source appears, and execution continuity is more valuable
   than waiting on an unavailable artifact

## Preconditions

Before any remote transfer or remote training claim:

1. local eval gate is green
2. any changed Python files compile locally
3. Huanxin `ai2` shell access is currently usable
4. the model source decision has been made explicitly

## 1. Re-run the mandatory local gate

```bash
python3 evals/runner/run_eval.py
python3 -m py_compile training/huanxin_cpu_smoke.py training/qwen_sft_peft.py training/verify_qwen_snapshot.py
```

Only continue if all checks pass.

## 2. Record the chosen public source as an artifact

Before downloading anything, attach one lightweight machine-local source audit:

```bash
python3 training/audit_model_source.py \
  --model-id Qwen/Qwen2.5-1.5B-Instruct \
  --expected-family-substring qwen \
  --out artifacts/model-source-audit-qwen25.json
```

This does not download weights. It just freezes the exact execution-source claim
into a JSON artifact before the snapshot step.

## 3. Acquire the public fallback snapshot locally

Preferred pattern: download locally first, then transfer the verified local
snapshot into Huanxin instead of relying on repeated remote HF fetches.

Default one-command path:

```bash
python3 training/acquire_public_qwen_snapshot.py --target qwen25
```

If you also want the matching branch-specific remote command sheet rendered as
soon as local verification succeeds:

```bash
python3 training/acquire_public_qwen_snapshot.py --target qwen25 --render-remote-commands
```

If you want a no-download preflight first, use:

```bash
python3 training/acquire_public_qwen_snapshot.py --target qwen25 --dry-run
```

If the public metadata API is transiently slow from this machine, retry with a
longer audit timeout instead of treating that as a source-decision signal:

```bash
python3 training/acquire_public_qwen_snapshot.py --target qwen25 --dry-run --hf-timeout-seconds 60
```

That dry run confirms the source audit still resolves, prints the intended
remote model directory, handoff note, and manifest paths, and writes a durable
preflight manifest at `artifacts/qwen25-local-snapshot-preflight.json` without
downloading weights or claiming snapshot acquisition. If `--render-remote-commands`
is also included, the dry run now renders the branch-specific remote command
sheet too and records its path in the same preflight manifest.

This helper:

- records `artifacts/model-source-audit-qwen25.json`
- downloads the local snapshot with `huggingface_hub`
- immediately runs `training/verify_qwen_snapshot.py` with the correct expected substring
- on a real acquisition, writes a durable handoff manifest at `artifacts/qwen25-local-snapshot-handoff.json` with the verified local snapshot path plus the intended remote model directory
- can optionally render a branch-specific Huanxin command sheet with `--render-remote-commands`, producing `artifacts/huanxin-bootstrap/20260316T143522Z/REMOTE_BOOTSTRAP_COMMANDS-Qwen2.5-1.5B-Instruct.sh`

Equivalent manual acquisition approach if needed:

```bash
python3 - <<'PY'
from huggingface_hub import snapshot_download
path = snapshot_download("Qwen/Qwen2.5-1.5B-Instruct")
print(path)
PY
```

## 4. Verify the local snapshot before transfer

Use the existing offline verifier, but with the expected substring adjusted for
Qwen 2.5:

```bash
python3 training/verify_qwen_snapshot.py /path/to/Qwen2.5-1.5B-Instruct \
  --expected-substring Qwen2.5-1.5B-Instruct
```

Required outcome:

- `status: ok`
- tokenizer files present
- model weights present, either as shard files or a valid weight index file
- `config.json` metadata identifies a Qwen-family architecture
- expected `Qwen2.5-1.5B-Instruct` substring is found in path or metadata

If this fails, stop.

## 5. Remote target layout

Place the verified snapshot under:

```text
/root/root/work/quantum-gpt/models/Qwen2.5-1.5B-Instruct
```

Reason:

- keeps the remote smoke path explicit
- avoids dependency on remote anonymous model resolution
- preserves parity with the existing Qwen 3.5 handoff structure

## 6. Minimum remote files needed

Transfer only the audited bootstrap code plus the verified snapshot:

- `training/requirements-huanxin-cpu.txt`
- `training/huanxin_cpu_smoke.py`
- `training/qwen_sft_peft.py`
- `data/seed/splits-auto-seed/train.jsonl`
- `data/seed/splits-auto-seed/val.jsonl`
- `models/Qwen2.5-1.5B-Instruct/`

## 7. First remote tokenizer smoke against the transferred local path

```bash
cd /root/root/work/quantum-gpt
python3 training/huanxin_cpu_smoke.py \
  --model-name /root/root/work/quantum-gpt/models/Qwen2.5-1.5B-Instruct \
  --dataset data/seed/splits-auto-seed/train.jsonl
```

Success criteria:

- imports succeed
- dataset loads
- tokenizer loads from the transferred local snapshot path
- the script prints a structured JSON summary with `status: ok`

That is the first honest proof that the public fallback path is operational.

## 8. Optional remote full-model smoke

Only if tokenizer smoke passes:

```bash
cd /root/root/work/quantum-gpt
python3 training/huanxin_cpu_smoke.py \
  --model-name /root/root/work/quantum-gpt/models/Qwen2.5-1.5B-Instruct \
  --dataset data/seed/splits-auto-seed/train.jsonl \
  --load-model
```

If this fails, the blocker becomes model-load compatibility or resource limits,
not source acquisition.

## 9. First minimal PEFT startup smoke

Only if full model load passes:

```bash
cd /root/root/work/quantum-gpt
python3 training/qwen_sft_peft.py \
  --model-name /root/root/work/quantum-gpt/models/Qwen2.5-1.5B-Instruct \
  --train-file data/seed/splits-auto-seed/train.jsonl \
  --eval-file data/seed/splits-auto-seed/val.jsonl \
  --output-dir outputs/qwen25-1p5b-peft-smoke \
  --device cpu \
  --max-steps 1 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 1
```

## What counts as success

A real state change would be:

1. explicit source decision made
2. local Qwen 2.5 snapshot acquired and verified
3. snapshot transferred into `ai2`
4. tokenizer smoke succeeds from the remote local path

Anything short of that is still preparation.

## What not to do

Do not:

- relabel Qwen 2.5 work as Qwen 3.5 work
- claim that this fallback is already approved if it is not
- skip local verification just because the checkpoint is public
- claim remote training progress before local-path tokenizer smoke succeeds
