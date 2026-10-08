# Plateau root-cause analysis — why 3/18 for 16 days (C-9722 input, 2026-09-24)

## Method (per reviewer recommendation: verify learning signal, execution path before optimizer choice)

### 1. Learning signal per step: EXHAUSTED (measured, live run 114532Z)
- 21-step loss curve on quantum_finetune_verified_chat_sft_dedup_1k:
  steps 1-10 mean loss 0.0098, steps 11-21 mean loss 0.0308 — flat, no downward trend.
- The 1000-example dataset has been trained over MANY times (6 epochs x dozens of
  resume runs since 2026-09-08). The model has memorized it.
- Conclusion: additional SFT steps on this data produce ZERO useful learning.
  (Matches reviewer: "running more steps" is not the answer.)

### 2. Failure taxonomy of the 15 failing holdout tasks (real eval, shard step-40 leg)
- 11 of 15 = INTERFACE-CONTRACT failures: model ignores the prompt's
  "Required public API" signatures and invents its own function names
  (e.g. writes qaoa_maxcut_cost_function instead of required maxcut_cost;
  scorer: "candidate_none_graded_fail / AttributeError: module 'candidate'
  has no attribute 'maxcut_cost'").
- 4 of 15 = behavioral/other failures.
- The prompt DOES contain the required signatures (verified by building the
  prompt locally). The SFT data teaches a DIFFERENT format ("complete
  standalone script", 172 mentions; zero mentions of "Required public API")
  => the fine-tune actively teaches the model to ignore eval-format contracts.
- Base model fails the same way (3/18) => this is a prompt-format-following
  problem, not quantum competence, and current SFT does not fix it.

### 3. Execution-path bug: eval environment lacks quantum libraries (4/18 unreachable)
- Holdout tasks requiring external libs: pennylane_vqe_h2 (pennylane),
  pennylane_qml_iris_classification (pennylane), cirq_qaoa_line (cirq),
  braket_bell_state (braket), qiskit_qft_entangled (qiskit)  [5 tasks; qiskit also missing]
- ASI1/ASI2 eval env: /usr/local/python3.11.13 has ONLY numpy.
  venv qwen27b-quantum-work/.venv: accelerate/peft only. NO qiskit/cirq/pennylane/braket.
- These tasks fail with "import failed: No module named ..." — a PERFECT model
  would still fail them in this environment. ~22-28% of the benchmark is
  unreachable due to environment, not model.
- Fix: install the frozen-lib set into the eval env (pip install pennylane
  cirq qiskit amazon-braket or a pinned freeze), then re-run the leg.

## Prescriptions (in order, cheapest evidence first)
1. EXECUTION-PATH: install missing quantum libs in the eval env; re-run the
   3/18 checkpoint leg. Expected: +up to 4-5 tasks free (environment fix, no training).
2. LEARNING-SIGNAL: stop grinding steps on the memorized 1k dataset. Build
   format-adherence SFT data: NEW tasks (non-holdout topics), same prompt
   template as the eval ("Required public API (signatures and docstrings
   only)"), verified solutions. Teaches: read the signatures, implement
   EXACTLY them. This is the "simplified baseline" the reviewer recommends.
3. Only after 1+2, re-measure per-step learning signal (loss trend on NEW
   data) before considering optimizer/hyperparameter changes.

## What this analysis does NOT claim
- No single root cause is claimed for the historical 40-step SAPO run — its
  reward-starvation/judging-disabled records predate this evidence chain
  (reward starvation documented in .sapo-loop records; not re-verified here).
- No lr change or optimizer swap is prescribed on current evidence.

## Addendum (2026-09-24, later): task-generation design decision (C-9762)

User proposal: stop training on fixed quantum coding problems; let the judge
create a random quantum computing coding problem at each step.

RATIFIED DESIGN (split by role):
- MEASUREMENT (the 18-task frozen holdout): NEVER generated, never trained
  on. Fixed so pass counts stay comparable across runs (goal, sha pins
  b40ca7f2, C-9668 scorer freeze). Regenerating it would make 18/18
  meaningless and leak.
- TRAINING: YES to fresh tasks — that is the fix for root cause #1
  (memorized 1k set, flat loss, zero learning signal). But:
  * LLM/judge may write problem TEXT only; ground truth is PROGRAMMATIC:
    simulator/reference computes the expected result; tests are executable;
    reference passes; >=2 mutants per task must FAIL (mutation check
    prevents degenerate pass-everything tests).
  * Rewards in RL are execution-verified ONLY. No judge-graded rewards —
    documented past failure modes: reward starvation, disabled judging,
    judge gameability.
  * Prompts use the eval-identical "Required public API (signatures and
    docstrings only)" template (attacks interface-contract failures, 11/15).
  * Topic families mirror holdout COVERAGE (QAOA/QPE/stabilizer/channels/
    QFT/...) without duplicating the 18 instances; automated anti-leakage
    diff (id + semantic) before any training use.
  * Seeded and archived per batch (reproducibility). Generate in batches,
    verify once, reuse within epoch; per-step sampling is for RL rollouts.
- ROLL-OUT: (1) C-9754 static format-adherence batch first; (2) C-9762
  generator (>=30 families, mutation-checked); (3) per-batch sampler when
  GRPO returns. Evaluation environment now has pennylane/cirq/qiskit/braket
  (C-9753) so generated tasks may use them, pinned per
  evals/requirements-eval.txt.
