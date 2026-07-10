---
name: trust-eval
description: Use when the user asks for rigorous, trustable, comprehensive, or auditable evaluation of quantum-gpt adapters or base models. Use when verification, reproducibility, evidence-backed claims, or tamper detection are required. Use when the user wants to audit a report, verify a run, or reproduce results. Do NOT use for casual smoke tests — this skill is the strict, evidence-backed path.
---

# Trustable Evaluation (`evals/trust/`)

Use this skill when the user requires **100%-trustable** evaluation:
every reported number must be cryptographically traceable to a
reproducible artifact, and any unbacked claim must block publication.

## When to use

- The user asks for "rigorous", "trustable", "comprehensive",
  "auditable", "verifiable", or "100% trustable" evaluation.
- The user wants to verify that a published report matches the
  underlying data.
- The user wants to reproduce an evaluation run.
- The user wants to detect tampering with task definitions, candidates,
  or test files after a run.
- The user wants to compare two runs (base vs adapter) with regression
  detection and provenance.
- The user is preparing a deliverable, paper, or release report where
  evaluation numbers must be defensible.

## When NOT to use

- Quick smoke tests during active development (use `evals/runner/`
  instead — it's lighter weight).
- Generation-only runs where scoring is not yet needed.
- Tasks that have no `tests.py` (the trustable harness requires a
  deterministic program test).

## Core guarantees

1. **Provenance**: every artifact (task, prompt, candidate, test,
   verdict) is SHA-256 hashed and recorded in an append-only SQLite
   ledger.
2. **Reproducibility**: every run records a full reproduction recipe
   (env, Python version, git commit, dependency hashes, seed, model
   hash). `reproduce` re-builds the recipe and asserts equality.
3. **Hermetic scoring**: tests run in a per-task sandbox with frozen
   `PYTHONHASHSEED=0`, no host site-packages leakage, optional network
   block. Same candidate + test → same verdict on any machine.
4. **Dual verdict**: every sample gets a deterministic program verdict
   (from `tests.py`) and, if a rubric is present, an LLM-judge verdict.
   Disagreements are surfaced, never silently averaged.
5. **Evidence→claim auditing**: `audit` parses Markdown reports for
   numeric claims (`N/M passed`, `pass@1 = X`, `n_tasks: N`,
   `delta = +X%`) and cross-checks each against the ledger. Unbacked
   claims block publication (exit 1).
6. **Task-suite pinning**: `suite.lock.json` pins the exact task set +
   per-task hashes. `verify` detects any post-run edit to `tests.py`,
   `task.json`, or `candidate.py`.

## Standard workflow

```bash
# 0. (one-time per iteration) pin the task suite
python -m evals.trust.cli.main suite-init \
    --tasks evals/tasks/quantum \
    --out evals/trust/suite.lock.json \
    --notes "iter-3 quantum holdout"

# 1. run the base model
python -m evals.trust.cli.main run \
    --suite evals/trust/suite.lock.json \
    --out evals/trust/runs/iter3-base-<stamp>/ \
    --exec-command "bash scripts/gen_base.sh" \
    --model-label qwen25-1p5b-base --k 5 --temperature 0.2 \
    --seed 42 --max-new-tokens 512

# 2. run the adapter
python -m evals.trust.cli.main run \
    --suite evals/trust/suite.lock.json \
    --out evals/trust/runs/iter3-adapter-<stamp>/ \
    --exec-command "bash scripts/gen_adapter.sh" \
    --model-label qwen25-1p5b-iter3 --k 5 --temperature 0.2 \
    --seed 42 --max-new-tokens 512

# 3. verify both runs (re-check every hash, re-score every sample)
python -m evals.trust.cli.main verify --run evals/trust/runs/iter3-base-<stamp>/
python -m evals.trust.cli.main verify --run evals/trust/runs/iter3-adapter-<stamp>/

# 4. compare
python -m evals.trust.cli.main compare \
    --base evals/trust/runs/iter3-base-<stamp>/ \
    --adapter evals/trust/runs/iter3-adapter-<stamp>/

# 5. write the human report, then audit it
$EDITOR evals/trust/runs/iter3-adapter-<stamp>/REPORT.md
python -m evals.trust.cli.main audit \
    --run evals/trust/runs/iter3-adapter-<stamp>/ \
    --report evals/trust/runs/iter3-adapter-<stamp>/REPORT.md

# 6. (optional) reproduce from the recipe
python -m evals.trust.cli.main reproduce --run evals/trust/runs/iter3-adapter-<stamp>/
```

## Hard rules

- **Never publish a number you cannot back.** If `audit` returns exit
  1, the report is unbacked. Fix the report or fix the run; do not
  override.
- **Never edit a task's `tests.py` after a suite is locked.** If you
  need to change a test, create a new suite lock and re-run. The old
  lock's `verify` will fail by design.
- **Never score outside the sandbox.** The sandbox's hermetic guarantees
  are the foundation of cross-machine reproducibility.
- **Never silently average the LLM judge with the deterministic
  judge.** Disagreements must be surfaced in the report.
- **Always record the git commit in the recipe.** `reproduce` checks
  that the on-disk state matches the recorded commit.

## Self-tests

The harness is proven correct by its own test suite. Run before
trusting any result:

```bash
PYTHONPATH=. python -m pytest evals/trust/tests/test_core.py -v
```

If any self-test fails, the harness itself is broken and no evaluation
result can be trusted. Fix the harness first.

## Failure modes and what to do

- `suite-verify` fails: a task's `tests.py` or `task.json` was edited
  after locking. Either restore the file or create a new suite lock.
- `verify` reports "candidate_code_hash mismatch": the `candidate_code`
  in the ledger was edited. Re-run the affected sample.
- `verify` reports "verdict drift": re-scoring gave a different result
  than the ledger. Investigate nondeterminism in the test (e.g.
  non-deterministic float comparison, time-dependent assertions).
- `audit` reports unbacked claims: the human report disagrees with the
  ledger. Either the report is wrong (fix it) or the run is wrong
  (re-run).
- `reproduce` reports recipe drift: the on-disk environment changed
  since the run. Either restore the environment or accept that the run
  is not bit-reproducible (and note this in the report).

## Layout reference

See `evals/trust/README.md` for the full directory layout and design
rationale.
