# Qwen 3.5 Acquisition Options

## Purpose

Turn the current artifact-access blocker into a short actionable decision list.

The frozen project target is still:

- `Qwen/Qwen3.5-1.5B-Instruct`

## Verified current state

- local eval gate is green
- `ai2` shell access is real
- remote bootstrap files and CPU smoke path exist
- remote progress is blocked specifically at tokenizer/model artifact access
- this local machine does **not** currently have a cached `Qwen/Qwen3.5-1.5B-Instruct` snapshot
- anonymous local fetch of the tested `Qwen/Qwen3.5-1.5B-Instruct` tokenizer config returns `401 Unauthorized`

## Acquisition options in priority order

### Option 1 — authenticated local Hugging Face download

Use an approved local auth context to fetch the exact model artifacts on this machine, then transfer them into `ai2`.

Why this is the best path:

- keeps the project target unchanged
- avoids depending on flaky remote egress from `ai2`
- fits the existing validated local-to-Huanxin transfer path

Success condition:

- a local directory exists containing the exact tokenizer/model files for `Qwen/Qwen3.5-1.5B-Instruct`

Then follow `research/qwen35-verified-snapshot-handoff.md` so the next step is explicit: verify the local snapshot, transfer it into `ai2` under `/root/root/work/quantum-gpt/models/Qwen3.5-1.5B-Instruct`, and run the tokenizer smoke against that remote local path.

### Option 2 — approved alternate source for the exact same artifact set

If direct HF auth is not the intended path, use another approved local source that yields the same model snapshot.

Requirements:

- exact same target model
- files acquired locally first
- transfer into `/root/root/work/quantum-gpt` by the validated browser-shell path

### Option 3 — user-provided local snapshot path

If a snapshot already exists elsewhere on the machine or another mounted path, point the project at it and transfer only what is needed.

This is the cheapest path if such a snapshot already exists.

Before transfer, verify the snapshot locally instead of guessing:

```bash
python3 training/verify_qwen_snapshot.py /path/to/Qwen3.5-1.5B-Instruct
```

A valid snapshot should contain:

- `config.json`
- tokenizer files such as `tokenizer.json` or `tokenizer_config.json`
- model weight files such as `model.safetensors` or an index file
- config metadata that actually identifies a Qwen-family architecture, not just a convenient directory name

Only after that local check passes should the snapshot be moved into `ai2` and used for remote smoke.

## What does not count as progress

- more retries of the same remote tokenizer load against the remote HF path
- silently swapping the project target to Qwen 2.5
- claiming training progress before tokenizer load succeeds from a real local or remote source

## Smallest next command-level milestone

1. obtain a real local directory for `Qwen/Qwen3.5-1.5B-Instruct`
2. verify it contains at least tokenizer/config files and the expected model artifacts
3. transfer it into `ai2`
4. rerun the remote smoke against the local directory path
5. only then attempt PEFT smoke/training
