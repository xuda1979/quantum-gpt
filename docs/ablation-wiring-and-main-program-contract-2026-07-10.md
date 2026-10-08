# Ablation Launcher Wiring + `main()`-Program Question Contract — Session Record

**Date:** 2026-07-10
**Status:** Implementation complete; locally verified; NPU launch pending.
**Author:** session lead (claude code)
**Related plans:**
- `docs/per-artifact-scoring-rd-plan-2026-07-08.md` (the ablation R&D plan; Phase 4 + 5 updated this session)
- `docs/rl-verifier-coding-rd-session-2026-07-09.md` (the RL-with-verifier loop; this session adds machine-enforcement to its question-shape rule)
- `docs/rl-distill-iteration-process-2026-07.md` (the parent RL+distill iteration process)

---

## 1. Objective

Two independent changes were completed in this session, both unblocking the
next NPU ablation sweep:

1. **Finish the per-artifact reward-weighted distillation ablation wiring**
   across all three student launchers (ASI1/27B, ASI2/35B, ASI3/35B), so a
   single env var selects one of six presets (A–F) and the run auto-stops
   after a fixed round budget. This is Phase 4 of the per-artifact scoring
   plan; Phase 5 (the NPU sweep) is now launch-ready.

2. **Make the "full program with `main()`" question contract
   machine-enforced**, not just prompt-enforced. Generated coding-domain
   questions must ask the answerer to write a complete runnable Python
   program (with a `def main():` entry point, the `if __name__ ==
   "__main__": main()` guard, and a `print(...)` of a concrete computed
   result) — not an isolated function or a snippet. The teacher gate now
   returns a `requires_full_program` boolean and rejects questions that
   fail this check.

---

## 2. Method

### 2.1 Ablation launcher wiring (ASI1 + ASI2 + ASI3)

Each of the three launchers
(`scripts/asi{1,2,3}_launch_rl_distill_*_2npu.sh`) now supports two new env
vars, expanded at heredoc-write time into the orchestrator + run config:

| Env var | Values | Effect |
|---------|--------|--------|
| `ABLATION_PRESET` | `A_legacy` (default), `B_rw_nll`, `C_kl_gate`, `D_partial_up`, `E_full`, `F_full_no_up` | Maps to a triple of trainer flags: `--reward-weighted-nll`, `--per-artifact-kl-gate`, `--partial-credit-upweight <w>` |
| `PIPELINE_MAX_ROUNDS` | `0` (default = unbounded), or e.g. `20` | Orchestrator auto-stops after N rounds (ablation budget) |

The preset→flags mapping (identical in all three launchers):

| Preset | `--reward-weighted-nll` | `--per-artifact-kl-gate` | `--partial-credit-upweight` |
|--------|:---:|:---:|:---:|
| `A_legacy` | off | off | 0.0 |
| `B_rw_nll` | on | off | 0.0 |
| `C_kl_gate` | off | on | 0.0 |
| `D_partial_up` | off | off | 0.5 |
| `E_full` | on | on | 0.5 |
| `F_full_no_up` | on | on | 0.0 |

Each launcher:
1. Parses `ABLATION_PRESET` into `ABLATION_RW_NLL` / `ABLATION_KL_GATE` /
   `ABLATION_PARTIAL_UP` via a `case` statement.
2. Records `ablation_preset` + per-flag booleans + the upweight in
   `run_config.json`.
3. Builds an `ABLATION_ARGS` array in the trainer heredoc and appends it to
   the `training/qwen_sft_peft_kl.py` invocation.
4. Records `pipeline_max_rounds` in `run_config.json` and breaks the
   orchestrator `while true` loop when `\$ROUND >= $PIPELINE_MAX_ROUNDS`
   (only when the cap is > 0).

### 2.2 `main()`-program question contract (pipeline-side enforcement)

Three prompt surfaces in `scripts/rl_distill_pipeline.py` were already
updated (prior session) to *ask* for full programs:
`SYSTEM_PROMPT_STUDENT_QGEN`, `SYSTEM_PROMPT_TEACHER_QGATE`, and
`SYSTEM_PROMPT_STUDENT`. This session adds **machine enforcement** so a
question that only asks for an isolated function is rejected even if the
student model proposes one:

1. **`TEACHER_QGATE_PROMPT_TEMPLATE`** (coding domain) now includes a
   `requires_full_program` field in its JSON schema, with the rule:
   > `requires_full_program` is true only if the question asks the
   > answerer to write a COMPLETE runnable Python program structured
   > around a `def main():` entry point (called under
   > `if __name__ == "__main__":`) that computes and prints a concrete
   > numeric/symbolic result. It is false if the question only asks for
   > an isolated function, a snippet, a class, or a fill-in-the-blank.

2. **`student_propose_question`** (coding-domain user prompt) now
   explicitly instructs the student to ask for full code with a `main()`
   that calculates something concrete, not an isolated function.

3. **Acceptance logic** in the resample loop: a coding-domain question is
   now accepted only if `is_valid AND is_answerable AND is_non_trivial AND
   requires_full_program`. A failure on `requires_full_program` increments
   a new `qgate_coding_not_full_program` stat and triggers a resample
   (up to `max_resamples_per_question`).

4. **Sample metadata**: `qgate_requires_full_program` is recorded in each
   accepted sample's metadata, alongside the existing `qgate_is_*` fields.

The science domain is deliberately untouched — it has its own
`requires_code` rejection (science questions must NOT ask for code).

---

## 3. Files changed this session

| File | Change |
|------|--------|
| `scripts/asi1_launch_rl_distill_27b_2npu.sh` | `ABLATION_PRESET` + `PIPELINE_MAX_ROUNDS` knobs; run_config fields; trainer `ABLATION_ARGS`; orchestrator round-cap break |
| `scripts/asi2_launch_rl_distill_35b_2npu.sh` | same as ASI1 |
| `scripts/asi3_launch_rl_distill_35b_2npu.sh` | same as ASI1 |
| `scripts/rl_distill_pipeline.py` | `TEACHER_QGATE_PROMPT_TEMPLATE` gains `requires_full_program`; `student_propose_question` coding user prompt requires full program with `main()`; acceptance logic rejects `requires_full_program=false` in coding domain (new `qgate_coding_not_full_program` stat); `qgate_requires_full_program` recorded in sample metadata |
| `tests/test_rl_distill_pipeline.py` | Updated mock gate dicts to include `requires_full_program: True`; added metadata assertion; new test `test_coding_qgate_rejects_isolated_function` locking in the rejection path |
| `docs/per-artifact-scoring-rd-plan-2026-07-08.md` | Phase 4 marked ✅ launcher wiring done (dated status note); Phase 5 now has copy-pasteable launch commands for the 4-preset sweep (A→B→D→E, 20 rounds each) |

---

## 4. Verification

- **Syntax:** all three launchers pass `bash -n`; `rl_distill_pipeline.py`
  passes `ast.parse`.
- **Render test:** all 6 `ABLATION_PRESET` values produce the expected
  `run_config.json` fields + trainer-arg combos. The `PIPELINE_MAX_ROUNDS`
  break condition renders correctly for both `0` (unbounded) and `20`
  (auto-stop).
- **Unit tests:** 90 tests pass across
  `test_rl_distill_pipeline.py` (36), `test_qwen_sft_peft_kl_loss.py` (50
  ablation loss-path tests — Phase 3 gate), `test_artifact_scoring.py`,
  and `test_qwen_sft_peft_trainable_controls.py`. The new
  `test_coding_qgate_rejects_isolated_function` confirms a question
  passing `is_valid/is_answerable/is_non_trivial` but with
  `requires_full_program=false` is rejected (3 resamples →
  `qgate_exhausted`, `qgate_coding_not_full_program=3`).

---

## 5. Status & next step

| Item | Status |
|------|--------|
| Ablation launcher wiring (ASI1/2/3) | ✅ done, locally verified |
| `PIPELINE_MAX_ROUNDS` round-cap (ASI1/2/3) | ✅ done, locally verified |
| `main()`-program question contract — prompt-level | ✅ done (prior session) |
| `main()`-program question contract — gate enforcement | ✅ done this session, tested |
| Per-artifact ablation Phase 3 (trainer loss unit tests) | ✅ 50 tests pass |
| Per-artifact ablation Phase 5 (NPU sweep: A/B/D/E, 20 rounds each) | ⏳ not started — unblocked, needs the Huanxin ASI1 box (~68h NPU time) |

**Next action (NPU-side):** launch preset A on ASI1 as the legacy control,
then B, D, E. Per the 2026-07-10 training-execution policy (recorded in
`MEMORY.md`), **all training runs must be submitted as ASI1 jobs via
`scripts/submit_asi1_shell_task.sh --submit`, never run directly on the
environment's own NPU.** The exact submission commands are in Phase 5 of
`docs/per-artifact-scoring-rd-plan-2026-07-08.md`. Each submitted job
auto-stops at round 20 and writes per-round eval JSON every 2 rounds; the
decision is round-20 `pass@1` with a monotonic-improvement guard on
rounds 2–18.

**In-flight risk to watch:** the `requires_full_program` gate is stricter,
so early rounds may see higher `qgate_coding_not_full_program` rejection
rates until the student model adapts its question proposals. Monitor the
stat in the pipeline log; if >50% rejection persists past round 5, consider
relaxing the gate wording or adding an `improved_question` rewrite path
that upgrades an isolated-function question to a full-program question
before rejection.
