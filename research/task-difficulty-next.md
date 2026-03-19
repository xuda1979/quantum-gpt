# Next Adversarial Task Batch

## Why this note

The current hosted baseline (`openai/gpt-5.4`) is still perfect on the 14-task seed harness. That is useful infrastructure validation, but it means the next bottleneck is task discriminativeness rather than execution plumbing.

This note locks the next task-design direction so the project does not drift into generic harness expansion.

## Current finding

The eval harness has improved steadily:

- 6 tasks -> too toy-like
- 10 tasks -> broader but still easy for a strong hosted model
- 12 tasks -> better category coverage, still perfect
- 14 tasks -> stacked invariants and multi-step repair logic, still awaiting the decisive miss

The pattern is clear: stronger backends are not being pressured enough by simple single-file synthesis tasks unless those tasks encode multiple interacting constraints.

## Design principle for the next batch

Do not add more tasks that are only:

- direct one-function synthesis
- shallow normalization
- obvious dictionary mapping
- single invariant checks

Instead, prioritize tasks with at least two of the following:

1. hidden edge-case interactions
2. stateful behavior over multiple events
3. repair under competing invariants
4. serialization / round-trip requirements
5. minimal-edit constraints expressed through tests
6. cross-field consistency requirements

## Recommended next two seed tasks

### 1. Quantum: stabilizer_tableau_update_repair

**Task shape**
- Provide a small broken implementation for updating Pauli-frame / stabilizer-like metadata after simple gates.
- Ask for a repair that preserves sign and axis updates under a restricted gate set.

**Why it matters**
- Forces symbolic quantum reasoning rather than only lookup-table synthesis.
- Still CPU-cheap and standard-library only.
- Likely to create subtle failure modes around commutation/sign handling.

**Expected pressure points**
- X/Z swap under H
- phase/sign flips under S and SDG
- invalid operator rejection
- invariants preserved across a short gate sequence, not just one-step mapping

### 2. Software: patch_application_conflict_resolver

**Task shape**
- Given a sequence of file edits or event-like patches, produce the final merged state plus a conflict summary.
- Tests should enforce ordering, idempotence on duplicate patch ids, and conflict detection when incompatible updates target the same key/version.

**Why it matters**
- Pressures multi-step stateful reasoning and bookkeeping.
- More realistic for software-engineering capability than another pure formatting task.
- Still small and locally testable.

**Expected pressure points**
- duplicate patch suppression
- version monotonicity
- conflict list ordering
- output immutability / no in-place mutation of inputs

## Success criterion

The next batch should not merely increase task count. It should increase the odds that:

- a strong hosted baseline shows at least one nontrivial miss, or
- failures become diagnostically meaningful enough to guide prompt/data redesign.

That is a better milestone than adding another handful of easy perfect-pass tasks.

## Decision

The next eval-expansion cycle should implement exactly these two adversarial tasks first, validate the reference candidates locally, and rerun the hosted baseline before any broader task expansion.
