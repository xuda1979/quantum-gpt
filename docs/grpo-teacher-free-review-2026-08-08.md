# Critical Review — Teacher-Free-FV-GSPO-Final-Plan-ZH.docx

Date: 2026-08-08
Reviewer: codex review pass (this document exists because the plan is NOT to be
treated as infallible — "不是 bible". It is a design intent with some numbers
that need engineering judgment.)

Scope: this review covers `Teacher-Free-FV-GSPO-Final-Plan-ZH.docx` (v1.0,
2026-08-05) and how the implementation should (and should not) follow it.

------------------------------------------------------------------------------
## 1. What the plan gets right (keep — these are sound)

* **Teacher-free self-repair is the right direction.** Driving a failing
  candidate plus its *real* execution error logs into a fresh rollout from the
  policy model itself — with no separate teacher/reference model — is achievable
  with only base + adapter checkpoints. Already landed (`teacher_free_repair.py`
  + trainer wiring, commit `d9ffaf6`).
* **Pass-dominant (tiered) reward.** Making *every* passing candidate outrank
  *every* failing candidate is the single most important safeguard against the
  policy gaming efficiency rewards by deleting necessary computation. Keep the
  hard tier.
* **LOO (leave-one-out) advantages without per-group std normalization.** The
  plan correctly forbids normalizing by each group's own reward std (which would
  destroy relative ordering across groups and inject noise).
* **Judge role lag.** A new accepted adapter should not simultaneously become
  its own judge; judge must trail at least one version. Sound anti-drift measure.
* **Cluster-aware down-weighting of duplicate code.** Down-weighting near-duplicate
  candidates protects structural diversity innovaion.
* **Frozen policy_old + exact behavior logprob.** GSPO ratio correctness depends
  on it.
* **Staged rollout (table 42)**: start with judge weight 0, hidden tests primary,
  self-repair <= 2 rounds, existing GSPO/KL/breakers on; enable K=4 / 2 epochs /
  adaptive KL only after the probe is stable. This staging is wise.

------------------------------------------------------------------------------
## 2. What the plan gets WRONG / needs correction (do NOT blindly follow)

### 2.1 Cluster-adjusted advantage formula (table 22) is under-specified & biased
The literal text: `candidate.advantage /= size(candidate.cluster)`.

Problems:
* It says divide by `size(candidate.cluster)` but does not define the size
  domain. If "size" is the cluster cardinality **in the whole task pool**, then
  a task that shares a cluster with many other tasks gets a flat penalty computed
  per task, not per candidate, which is fine; but if it is per-batch candidate
  count, the sum of advantages changes and the group's variance is distorted.
* Dividing advantage by cluster size **after** LOO is applied is only well-posed
  if the cluster penalty is a density weight per candidate. It must be applied
  BEFORE any group-relative clip, and it interacts badly with the clip range if
  applied to already-large advantages.

Implementation decision (deviation): `cluster_adjusted_advantages` treats the
cluster size as a **per-batch** topical density and divides the already-computed
LOO advantage by the batch-local cluster cardinality (min 1). Exact duplicate
code in the same group collapses in weight. This preserves the plan's *intent*
(protect diversity) while keeping the math well-defined and boundedasiacea.

### 2.2 Reward hyperparameters on the pass tier are loose
Table 16: `R_i = 1.00 + 0.03*E + 0.02*D` for passing candidates.
* 0.03*E + 0.02*D puts E and D on the same tier but the plan earlier says
  efficiency (E) and diversity (D) should only *distinguish* passing candidates,
  which the implementation does. Fine.
* The plan gives no units or normalization for E and D; implementation clamps
  them to [0,1] so the pass tier always stays in [1.00, 1.05] and the invariant
  is stable.

### 2.3 "Judge weight 0.05" conflicts with "judge start at weight 0"
Table 16 gives failing-candidate reward a 0.05 judge weight, while table 42 says
start with judge weight **0** and only enable dimensions that pass an AUC>=0.85
calibration gate (SS 4.4). These are contradictory-ish unless read as "0.05 max
once calibrated". Implementation: judge weight is 0 until `judge_calibrated`,
then it joins at 0.05 (semantic weight drops 0.70 -> 0.65). This is the
reconciling reading and is what we implement.

### 2.4 V ambiguity — "semantic progress" vs "pass-with-frontier"
The routing tables use `max(V)>=0.30` and `reward_range>=0.10` to decide
"partial_repair_rl" vs "self_repair", but never define `V` for routing vs the
`V` used in reward. A single V_i (0..1 semantic progress) is assumed. That is
reasonable; we keep one semantic score fed into both reward and routing.

### 2.5 The plan over-relies on a single "24-step probe" gate
"Checkpoint gate can auto-accept/reject/rollback/rotate roles" and "24-step
probe with no severe breaker" are listed as hard gates, but 24 steps is far too
few to establish statistical significance for pass@1 deltas at G=8 on ~1k tasks.
We treat these as *smoke* gates (no catastrophic breaker, healthy frontier
yield), not as proof of convergence.

### 2.6 Async / infra reality vs. the docx
The docx is written as if one continuous single-machine loop. Real ASI3 runs are
launched, polled, and may preempt. The implementation and the operations scripts
must remain resumable and checkpoint-tolerant; the plan's "自动 checkpoint gate"
must not depend on a single long-lived process.

------------------------------------------------------------------------------
## 3. Review conclusion / what we actually implement (this pass)
Implemented now (training/grpo_utils.py, tests/test_teacher_free_helpers.py):
  * tiered_teacher_free_reward  — pass-dominant reward, judge-off-by-default,
                                  judge joins at 0.05 only when calibrated.
  * cluster_adjusted_advantages — per-batch cluster-density down-weight.
  * teacher_free_route          — frontier / partial / mastered / self-repair /
                                  quarantine routing (self-repair routing is the
                                  hook for the already-landed repair rollout).
Self-repair core itself already landed (commit d9ffaf6).

Deferred to the trainer/ops layer (next passes, coordinated with the live
ASI3 run): K=4 group accumulation, two-round minibatch, and the automatic
checkpoint gate — these live in `grpo_trainer.py` / launcher layer and are being
handled by the training-operations workstreams; they are not duplicated here.

------------------------------------------------------------------------------
## 4. Source / change declaration
Base: FV-GSPO Implementation Reference (2026-08-05), implemented/validated/staged.
Deviations from the literal docx text are called out in section 2 and are
*intent-preserving, numerically safer* edits, not feature removals.
