# Huanxin CPU Bootstrap Sequence

## Why this note exists

The current Huanxin path is no longer blocked by vague infrastructure questions. The state is concrete:

- local eval validation passes
- a minimal remote bootstrap payload exists
- the target Huanxin environment is known
- the environment is CPU-only ARM64 with `torch 2.5.1+cpu`
- the missing piece is a precise first command sequence once browser auth is refreshed

This note turns that into an explicit first remote sequence.

## Current remote facts

From `research/huanxin-remote-env-manifest.md`:

- Python `3.11.6`
- `aarch64`
- `torch 2.5.1+cpu`
- no CUDA
- no `transformers`
- no `accelerate`
- no `datasets`
- no `peft`
- no `trl`
- no `bitsandbytes`

This means the first honest target is **package install + tokenizer smoke**, not model training.

## Validated local artifacts to use

The minimal CPU bootstrap payload already exists locally in the workspace:

- `training/requirements-huanxin-cpu.txt`
- `training/huanxin_cpu_smoke.py`
- `training/qwen_sft_peft.py`
- `data/seed/train-chat.jsonl`
- `data/seed/splits-auto-seed/train.jsonl`
- `data/seed/splits-auto-seed/val.jsonl`

A paste-audited bundle containing these files was prepared under:

- `artifacts/huanxin-bootstrap/20260316T130651Z/`

## First remote command sequence

After browser auth is refreshed and the train-dev shell/editor surface is genuinely usable, paste only the bootstrap bundle and run exactly this sequence in `/root/root/work/quantum-gpt`.

### 1. Enter the repo root

```bash
cd /root/root/work/quantum-gpt
pwd
python3 --version
```

### 2. Install the minimal CPU bootstrap stack

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r training/requirements-huanxin-cpu.txt
```

If this fails, stop and record the exact package or wheel error. On this environment, compatibility failures are real information.

### 3. Run the tokenizer-and-dataset smoke test

Start with tokenizer only:

```bash
python3 training/huanxin_cpu_smoke.py \
  --model-name Qwen/Qwen3.5-1.5B-Instruct \
  --dataset data/seed/splits-auto-seed/train.jsonl
```

Success criteria:

- all required imports succeed
- dataset rows are read successfully
- tokenizer loads successfully
- script prints a structured JSON summary

### 4. Only if tokenizer smoke passes, try full model load

```bash
python3 training/huanxin_cpu_smoke.py \
  --model-name Qwen/Qwen3.5-1.5B-Instruct \
  --dataset data/seed/splits-auto-seed/train.jsonl \
  --load-model
```

This is still a smoke step, not a training run.

Success means:

- model weights can be resolved/downloaded
- the model object instantiates on the current CPU-only ARM64 host

Failure here is acceptable and informative.

## Decision rule after the smoke

### If package install fails

Record:

- exact failing package
- exact error text
- whether the issue is wheel availability, dependency conflict, or network/download failure

That becomes the blocker.

### If tokenizer load passes but full model load fails

That still counts as real progress.

It means:

- the remote Python package path is viable
- the dataset path is viable
- the next blocker is model-size or architecture compatibility, not basic environment setup

### If full model load passes

Then the next honest step is a very small PEFT startup smoke using `training/qwen_sft_peft.py`, for example `--max-steps 1` on CPU, with no claim that this is yet practical training throughput.

## Recommended next step after success

If both install and model smoke pass, the smallest next experiment should be:

```bash
python3 training/qwen_sft_peft.py \
  --model-name Qwen/Qwen3.5-1.5B-Instruct \
  --train-file data/seed/splits-auto-seed/train.jsonl \
  --eval-file data/seed/splits-auto-seed/val.jsonl \
  --output-dir outputs/qwen35-1p5b-peft-smoke \
  --device cpu \
  --max-steps 1 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 1
```

That is the first command that would deserve to be called a training-loop smoke.

## What not to claim yet

Do not claim:

- GPU fine-tuning readiness
- practical remote throughput
- successful Qwen fine-tuning
- scalable training configuration

until the remote shell actually runs the install and smoke sequence successfully.

## Bottom line

The next Huanxin move is now very specific:

1. refresh browser auth
2. paste the prepared CPU bootstrap bundle
3. run package install
4. run tokenizer smoke
5. optionally run full model-load smoke
6. only then consider a 1-step PEFT startup test
