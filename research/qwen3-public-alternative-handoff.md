# Qwen 3 1.7B Public Alternative Handoff

## Purpose

This note exists for the case where the project wants a publicly verified Qwen 3 family checkpoint now, without pretending that `Qwen/Qwen3.5-1.5B-Instruct` is currently obtainable from this machine.

It does **not** silently replace the project target.

It only defines the exact operational path if the project explicitly approves:

- `Qwen/Qwen3-1.7B`

as the executable checkpoint for the next remote Huanxin step.

## Why this path exists

Compared with the Qwen 2.5 public fallback:

- it stays in the Qwen 3 family
- it is publicly resolvable from this machine
- it is slightly larger than the 1.5B fallback, so it is not the cheapest CPU-first option

Compared with the strict Qwen 3.5 path:

- it is an actually auditable public source right now
- it avoids repeated fake progress on an unverified artifact id

## Preconditions

Before any remote transfer or remote training claim:

1. local eval gate is green
2. any changed Python files compile locally
3. Huanxin `ai2` shell access is currently usable
4. the model-source decision explicitly approves `Qwen/Qwen3-1.7B`

## 1. Re-run the mandatory local gate

```bash
python3 evals/runner/run_eval.py
python3 -m py_compile training/audit_model_source.py training/huanxin_cpu_smoke.py training/qwen_sft_peft.py training/verify_qwen_snapshot.py
```

Only continue if all checks pass.

## 2. Freeze the execution-source claim as an artifact

```bash
python3 training/audit_model_source.py \
  --model-id Qwen/Qwen3-1.7B \
  --expected-family-substring qwen \
  --out artifacts/model-source-audit-qwen3-1p7b.json
```

The expected current truth from this machine is:

- `status: ok`
- `resolved_id: Qwen/Qwen3-1.7B`
- `gated: false`
- `private: false`
- `config_model_type: qwen3`
- `config_architectures` containing `Qwen3ForCausalLM`

## 3. Acquire the snapshot locally

Preferred pattern: download locally first, then transfer the verified local snapshot into Huanxin.

Default one-command path:

```bash
python3 training/acquire_public_qwen_snapshot.py --target qwen3-1.7b
```

If you also want the matching branch-specific remote command sheet rendered as
soon as local verification succeeds:

```bash
python3 training/acquire_public_qwen_snapshot.py --target qwen3-1.7b --render-remote-commands
```

If you want a no-download preflight first, use:

```bash
python3 training/acquire_public_qwen_snapshot.py --target qwen3-1.7b --dry-run
```

If the public metadata API is transiently slow from this machine, retry with a
longer audit timeout instead of treating that as a model-source decision:

```bash
python3 training/acquire_public_qwen_snapshot.py --target qwen3-1.7b --dry-run --hf-timeout-seconds 60
```

That dry run confirms the source audit still resolves, prints the intended
remote model directory, handoff note, and manifest paths, and writes a durable
preflight manifest at `artifacts/qwen3-1p7b-local-snapshot-preflight.json`
without downloading weights or claiming snapshot acquisition. If
`--render-remote-commands` is also included, the dry run now renders the
branch-specific remote command sheet too and records its path in the same
preflight manifest.

This helper:

- records `artifacts/model-source-audit-qwen3-1p7b.json`
- downloads the local snapshot with `huggingface_hub`
- immediately runs `training/verify_qwen_snapshot.py` with the correct expected substring
- on a real acquisition, writes a durable handoff manifest at `artifacts/qwen3-1p7b-local-snapshot-handoff.json` with the verified local snapshot path plus the intended remote model directory
- can optionally render a branch-specific Huanxin command sheet with `--render-remote-commands`, producing `artifacts/huanxin-bootstrap/20260316T143522Z/REMOTE_BOOTSTRAP_COMMANDS-Qwen3-1.7B.sh`

Equivalent manual acquisition path if needed:

```bash
python3 - <<'PY'
from huggingface_hub import snapshot_download
path = snapshot_download("Qwen/Qwen3-1.7B")
print(path)
PY
```

## 4. Verify the local snapshot before transfer

```bash
python3 training/verify_qwen_snapshot.py /path/to/Qwen3-1.7B \
  --expected-substring Qwen3-1.7B
```

Required outcome:

- `status: ok`
- tokenizer files present
- model weights present, either as shard files or a valid weight index file
- `config.json` metadata identifies a Qwen-family architecture
- expected `Qwen3-1.7B` substring is found in path or metadata

If this fails, stop.

## 5. Remote target layout

Place the verified snapshot under:

```text
/root/root/work/quantum-gpt/models/Qwen3-1.7B
```

## 6. Minimum remote files needed

Transfer only the audited bootstrap code plus the verified snapshot:

- `training/requirements-huanxin-cpu.txt`
- `training/huanxin_cpu_smoke.py`
- `training/qwen_sft_peft.py`
- `data/seed/splits-auto-seed/train.jsonl`
- `data/seed/splits-auto-seed/val.jsonl`
- `models/Qwen3-1.7B/`

## 7. First remote tokenizer smoke against the transferred local path

```bash
cd /root/root/work/quantum-gpt
python3 training/huanxin_cpu_smoke.py \
  --model-name /root/root/work/quantum-gpt/models/Qwen3-1.7B \
  --dataset data/seed/splits-auto-seed/train.jsonl
```

Success criteria:

- imports succeed
- dataset loads
- tokenizer loads from the transferred local snapshot path
- the script prints a structured JSON summary with `status: ok`

## 8. Optional remote full-model smoke

Only if tokenizer smoke passes:

```bash
cd /root/root/work/quantum-gpt
python3 training/huanxin_cpu_smoke.py \
  --model-name /root/root/work/quantum-gpt/models/Qwen3-1.7B \
  --dataset data/seed/splits-auto-seed/train.jsonl \
  --load-model
```

## 9. First minimal PEFT startup smoke

Only if full model load passes:

```bash
cd /root/root/work/quantum-gpt
python3 training/qwen_sft_peft.py \
  --model-name /root/root/work/quantum-gpt/models/Qwen3-1.7B \
  --train-file data/seed/splits-auto-seed/train.jsonl \
  --eval-file data/seed/splits-auto-seed/val.jsonl \
  --output-dir outputs/qwen3-1p7b-peft-smoke \
  --device cpu \
  --max-steps 1 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 1
```

## What counts as success

A real state change would be:

1. explicit approval of `Qwen/Qwen3-1.7B` as the executable checkpoint
2. local snapshot acquired and verified
3. snapshot transferred into `ai2`
4. tokenizer smoke succeeds from the remote local path

Anything short of that is still preparation.

## What not to do

Do not:

- relabel Qwen 3 1.7B work as Qwen 3.5 work
- skip local verification just because the source is public
- claim remote fine-tuning progress before remote local-path tokenizer smoke succeeds
