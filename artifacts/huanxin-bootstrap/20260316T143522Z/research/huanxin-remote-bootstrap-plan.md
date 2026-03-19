# Huanxin Remote Bootstrap Plan for Qwen3.5-1.5B

## Purpose

Turn the now-verified Huanxin shell path into a concrete fine-tuning bootstrap path for the project without pretending that training is already configured.

This note starts from facts that are now verified:

- local eval gate passes before remote actions
- validated workspace payload can be moved into `/root/root/work/quantum-gpt`
- the Huanxin `ai2` environment exposes a usable root shell
- remote `python3` and `pip3` are available
- the synced project can run `python3 evals/runner/run_eval.py` remotely and still pass `19/19`

So the next problem is no longer auth, transfer, or basic shell viability. The next problem is training bootstrap.

## Target

Bootstrap the smallest practical remote fine-tuning path for **Qwen3.5-1.5B-Instruct** while preserving software-engineering capability as a first-class objective.

Because the current repo is eval-heavy and does not yet contain an actual training stack, the bootstrap must be explicit about what is missing.

## What is already true

### Local gate

Required command before every remote code transfer or training attempt:

```bash
python3 evals/runner/run_eval.py
```

If files changed in a cycle, run any additional relevant local tests too.

### Remote gate

The following command is already verified to work inside Huanxin `ai2`:

```bash
cd /root/root/work/quantum-gpt
python3 evals/runner/run_eval.py
```

That means the remote workspace is not just present; it is executable enough to validate the current eval harness.

## Minimum bootstrap deliverables

The next remote fine-tuning phase should not start with a blind `pip install` spree. It should produce four durable artifacts first:

1. **training environment manifest**
   - exact remote Python version
   - exact package install commands
   - whether CUDA / torch GPU is present in Huanxin
   - whether PEFT / Transformers / datasets can install cleanly

2. **training dataset seed artifact**
   - a small JSONL seed split built from the current eval-derived task schema
   - must preserve both `quantum` and `software` examples
   - should be explicitly suitable for supervised fine-tuning conversion

3. **training script scaffold**
   - one script or notebook-free CLI path for a first SFT run
   - should target Qwen3.5-1.5B-Instruct
   - should start with LoRA/PEFT assumptions, not full-model fine-tuning

4. **remote smoke command**
   - a no-ambiguity command that proves the stack imports and starts
   - for example: dataset load, tokenizer load, one forward pass, or `--max_steps 1`

## Recommended bootstrap sequence

### Phase 1: remote environment inspection

Run these inside `/root/root/work/quantum-gpt`:

```bash
python3 --version
pip3 --version
python3 - <<'PY'
import os
import platform
print(platform.platform())
print(platform.machine())
PY
python3 - <<'PY'
try:
    import torch
    print('torch', torch.__version__)
    print('cuda_available', torch.cuda.is_available())
    if torch.cuda.is_available():
        print('cuda_device_count', torch.cuda.device_count())
        print('device_name', torch.cuda.get_device_name(0))
except Exception as exc:
    print('torch_import_error', repr(exc))
PY
```

This determines whether the Huanxin path is a real training path or only a remote CPU shell.

### Phase 2: package bootstrap

If torch/accelerate/transformers are not already present, create a minimal requirements file or explicit install block for:

- `torch`
- `transformers`
- `peft`
- `datasets`
- `accelerate`
- `sentencepiece` if needed by the tokenizer path

Do this only after capturing the environment manifest.

### Phase 3: seed training corpus

Create a tiny seed corpus derived from the eval/data schema already documented in:

- `research/dataset-schema-v0.md`

The first version should be intentionally small and balanced across both project goals:

- quantum tasks
- software-engineering tasks

A bad first training artifact would be quantum-only data. That would violate the stated project objective.

### Phase 4: remote training smoke

The first remote training success criterion should be modest:

- tokenizer loads
- model loads
- dataset loads
- training loop starts
- optionally completes `max_steps=1`

That is enough to prove the path is real.

### Phase 5: only then attempt a real fine-tuning run

Once the smoke path is real, define:

- batch size
n- gradient accumulation
- max sequence length
- LoRA rank / alpha / target modules
- checkpoint output path
- eval cadence

## Current blocker

There is still **no training stack in the repo yet**.

Concretely missing from the validated workspace payload:

- a seed training dataset file under `data/`
- a remote package manifest such as `requirements.txt`
- a fine-tuning entrypoint script
- a verified model-loading smoke test for Qwen3.5-1.5B-Instruct in Huanxin

So the project is now blocked on training bootstrap artifacts, not on remote connectivity.

## Smallest next unblocker

The smallest honest next step is:

1. inspect remote torch/CUDA/package state inside Huanxin
2. write down the exact result
3. create the first minimal training bootstrap artifact locally
4. validate locally where possible
5. sync only that validated bootstrap artifact to `/root/root/work/quantum-gpt`
6. run a remote import/smoke command

## Decision rule

Do not claim fine-tuning progress until at least one of these has actually happened remotely:

- Qwen tokenizer/model imports successfully
- training dataset loads successfully
- a training loop starts successfully

Until then, progress should be described as **remote bootstrap and fine-tuning readiness**, not training.
