# Verifier-gated LLM-generated tasks for SAPO

The existing SAPO optimizer, frontier routing, shaped rewards, repair queue and trust-region code remain unchanged. This opt-in experiment adds a **fail-closed input quality contract** to prevent ambiguous or stale LLM-generated tasks from silently entering expensive training.

## Admission in an isolated execution environment

**Security:** The verifier executes arbitrary generated `tests.py` and reference Python. Run only in a disposable OS/container sandbox with no network, credentials, devices, host mounts, or host write access. Subprocess timeouts are not sandboxing.

Every accepted task under `--tasks-dir/<domain>/<task_id>/` must contain `task.json`, `tests.py` exposing `run_tests(path) -> {"passed": bool}`, and a reference Python file named by `task.json["reference_file"]`. An opt-in legacy `--allow-candidate-reference` switch allows `candidate.py` as reference. Reference programs are for offline verification / SFT only; they are never appended to SAPO prompts by this patch.

```bash
python scripts/verify_sapo_tasks.py \
  --tasks-dir evals/tasks \
  --ids-file evals/benchmarks/my_training_tasks.txt \
  --holdout-file evals/benchmarks/my_holdout.txt \
  --manifest-out outputs/task_admission/verified.json \
  --report-out outputs/task_admission/rejections.json \
  --replay-out outputs/task_admission/verified_sft.jsonl \
  --strict --sandbox-acknowledged
```

The verifier requires two successful executions of the reference, rejection of a mutated reference and an empty candidate, deduplicates normalized prompts and IDs, checks holdout prompt/ID collisions, and pins SHA-256 digests of the task contract, tests and reference. Tasks that lack verifiable evidence are rejected instead of guessed correct. A single mutation is a *weak negative control*, not proof that all possible incorrect solutions fail; add task-specific quantum invariants and randomized hidden tests before high-stakes promotion.

## SAPO integration

```bash
python training/grpo_trainer.py \
  --model-name models/Qwen3.6-27B \
  --loss-mode sapo --device npu \
  --tasks-dir evals/tasks \
  --benchmark-file evals/benchmarks/my_training_tasks.txt \
  --verified-task-manifest outputs/task_admission/verified.json \
  --output-dir outputs/sapo-verified-canary \
  --grpo-steps 5
```

The manifest is opt-in for backwards compatibility. When provided, the trainer rejects any requested task missing from the approved manifest, checks hashes **before model loading**, and checks the selected task **again immediately before each rollout**. Changing reference, tests, prompt or metadata requires re-verification. Task IDs in the manifest are not silently added to training: the selected benchmark/task directory defines the workload. The verified SFT JSONL can be used by the existing SFT stage under a separately recorded experiment contract; this patch does not silently mix objectives.

## Required quality gates

1. Run `pytest -q tests/test_task_admission.py` and existing affected trainer smoke tests.
2. Run verifier in sandbox on the selected generated tasks, investigate rejected examples, inspect counts and holdout checks.
3. Run a tiny model load → rollout → score → update → save/reload cycle under `--verified-task-manifest`.
4. Compare held-out executable quantum Pass@1 and general-coding retention against the same checkpoint and compute budget. **No improvement claim is implied by admission tests.**

No remote NPU experiment or model benchmark has been run as part of this source change.