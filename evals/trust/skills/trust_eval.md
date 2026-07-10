# Trust-eval skill prompt (human-facing)

When the user asks for a **rigorous, trustable, comprehensive, or
auditable** evaluation, follow this protocol exactly.

## Protocol

1. **Pin the suite.** Run `suite-init` against the task root and commit
   the resulting `suite.lock.json` to git. This is the contract between
   dataset curation and evaluation for this iteration.

2. **Run base and adapter.** Use `run` with the same `--suite`, `--k`,
   `--temperature`, `--seed`, and `--max-new-tokens` for both. Record
   the `run_hash` of each.

3. **Verify both runs.** `verify` must return exit 0 for both. If it
   fails, do not proceed — investigate the cause (tampered tests,
   candidate hash mismatch, or verdict drift) and fix it.

4. **Compare.** `compare --base ... --adapter ...` shows the delta,
   fixed tasks, and broken tasks. Record these.

5. **Write the report.** Use `report` to generate the scaffold, then
   edit the prose sections. Every numeric claim must be one of:
   `N/M passed`, `pass@1 = X`, `pass@k = X`, `n_tasks: N`, or
   `delta = +X%` — these are the patterns the auditor recognises.

6. **Audit before publishing.** `audit --run ... --report ...` must
   return exit 0. If it returns exit 1, fix the report (or re-run the
   evaluation) until every claim is backed.

7. **Offer reproduction.** Include the `run_hash` and the
   `reproduce` command in the report so a third party can verify.

## Anti-patterns

- Do **not** hand-edit a `summary.json` or `REPORT.md` numeric field.
  Re-run the evaluation if the number is wrong.
- Do **not** edit `tests.py` after a suite is locked. Create a new
  suite lock and re-run.
- Do **not** average the LLM judge with the deterministic judge. If
  they disagree, surface the disagreement in the report.
- Do **not** publish a report that has not passed `audit`.
- Do **not** trust a run whose `verify` failed, even if the numbers
  look right.

## Self-test

Before trusting any result, run:

```bash
PYTHONPATH=. python -m pytest evals/trust/tests/ -v
```

All 30 tests must pass. If any fails, the harness is broken.
