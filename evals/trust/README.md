# Trustable Evaluation Subsystem (`evals/trust/`)

A rigorous, comprehensive, and 100%-trustable evaluation harness for
quantum-gpt adapters and base models. This subsystem is designed so that
**every reported number is cryptographically traceable to a reproducible
artifact**, and any claim that cannot be backed by evidence is refused at
publish time.

## Design pillars

1. **Provenance & integrity** — every artifact (task, prompt, candidate
   code, test result, model checkpoint) is SHA-256 hashed and recorded in
   an append-only SQLite ledger. Tampering with any artifact after the
   fact invalidates the chain.
2. **Reproducibility-first** — each run records a full reproduction
   recipe (environment, Python version, dependency hashes, seed, model
   hash, prompt template hash). `quantum_eval reproduce` re-runs the
   exact recipe and asserts bit-equal scoring.
3. **Hermetic scoring** — tests are executed in a per-task sandbox with
   frozen `PYTHONPATH`, no host site-packages leakage, optional network
   block, and a fixed seed. The same candidate + test pair always yields
   the same verdict.
4. **Dual verdict** — every sample gets both a *deterministic* program
   verdict (from `tests.py`) and an LLM-judge verdict (only when a
   rubric is present). Disagreements are surfaced, never silently
   averaged.
5. **Evidence→claim auditing** — the `audit` subcommand cross-checks
   every numeric claim in a human report (e.g. `RUN_SUMMARY.md`) against
   the ledger. Unbacked claims block publication.
6. **Task-suite pinning** — a `suite.lock.json` pins the exact task set
   + per-task hashes used by a run. No silent task edits between
   iterations.

## Layout

```
evals/trust/
├── README.md                  this file
├── SKILL.md                   Claude Code skill definition
├── core/
│   ├── __init__.py
│   ├── ledger.py              SQLite provenance ledger
│   ├── hashing.py             canonical hashing helpers
│   ├── schema.py              SQL schema + migrations
│   ├── suite.py               task suite discovery + locking
│   ├── sandbox.py             hermetic test execution
│   ├── scoring.py             deterministic scoring + pass@k
│   ├── judge.py               optional LLM rubric judge
│   ├── repro.py               reproduction recipe builder
│   └── audit.py               evidence→claim auditor
├── cli/
│   ├── __init__.py
│   └── main.py                `quantum_eval` entrypoint
├── skills/
│   └── trust_eval.md          human-facing skill prompt
├── templates/
│   ├── suite.lock.json        example suite lock
│   └── report.md.tmpl         report template (audit-checked)
└── tests/
    └── test_*.py              self-tests (proves the harness itself)
```

## Quickstart

```bash
# One-time: pin the task suite for this iteration
python -m evals.trust.cli.main suite-init \
    --tasks evals/tasks/quantum \
    --out evals/trust/suite.lock.json

# Run a model against the pinned suite
python -m evals.trust.cli.main run \
    --suite evals/trust/suite.lock.json \
    --model-base models/Qwen2.5-1.5B-Instruct \
    --adapter adapters/iter3 \
    --k 5 --temperature 0.2 \
    --out evals/trust/runs/iter3-<timestamp>/

# Verify a published run (re-check every hash, re-score every sample)
python -m evals.trust.cli.main verify \
    --run evals/trust/runs/iter3-<timestamp>/

# Audit a human-written report against the ledger
python -m evals.trust.cli.main audit \
    --run evals/trust/runs/iter3-<timestamp>/ \
    --report evals/RUN_SUMMARY.md

# Reproduce a run from its recipe
python -m evals.trust.cli.main reproduce \
    --run evals/trust/runs/iter3-<timestamp>/
```

## Why this is trustable

- **No floating numbers.** Every `pass_at_1` in every report is joined
  to a `sample` row that has a `test_stdout_hash`, a `candidate_code_hash`,
  and a `tests_py_hash`. If any of those hashes do not match the
  on-disk artifact, `verify` fails.
- **No silent edits.** The `suite.lock.json` is content-addressed; if
  anyone edits a `tests.py` after a run, `verify` reports the suite as
  broken and pinpoints the offending task.
- **No hallucinated claims.** The auditor parses Markdown reports for
  numeric claims (e.g. "24/26 passed"), resolves them to ledger rows,
  and refuses to publish if any claim is unbacked.
- **No nondeterminism.** Scoring runs with `PYTHONHASHSEED=0`,
  `PYTHONPATH` restricted to the sandbox, and a per-task temp dir. The
  same candidate + test pair yields the same verdict on any machine.
