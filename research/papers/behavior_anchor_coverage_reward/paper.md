# Behavior-Anchor Coverage Reward for Low-Signal Code GRPO

## Core Idea

Add a cheap partial-credit reward for candidates that contain the right behavioral
anchors from the task description even when they still fail tests.

Behavioral anchors are lightweight tokens derived from:

- task `behavior_hints`
- required interface symbol names

The method is intentionally conservative and removable:

- prompt hint: preserve required behavioral anchors
- mild task-weight boost on anchor-rich tasks
- bounded reward blend through `--research-methods behavior_anchor_coverage_reward`

## Why It Matters Here

The current local evidence says the main GRPO bottleneck is still weak reward
spread inside small groups:

- all-fail groups can collapse to near-identical reward
- skipped updates then dominate the run
- the best current mitigations are still adaptive temperature, larger group size,
  and cheap auxiliary rewards such as brevity

Existing plugin rewards already help, but there is still no direct reward for
“the candidate is talking in the right operational vocabulary” unless that
signal leaks indirectly through interface or verifier details.

This method targets the gap between:

- exact interface correctness
- final behavioral correctness

## Reward Shape

1. Extract normalized anchor tokens from behavior hints.
2. Add a small number of interface symbol-name anchors.
3. Extract normalized code tokens from the candidate.
4. Compute anchor coverage as matched anchors / total anchors.
5. Blend a small bounded bonus into `total_reward`.

Initial conservative blend:

- `behavior_anchor_reward = coverage`
- `behavior_anchor_bonus = 0.08 * behavior_anchor_reward`
- `total_reward = min(1.0, 0.94 * base_total + behavior_anchor_bonus)`

## Success Criterion

This direction is only worth keeping if it creates new reward variance on
representative near-miss groups beyond the current interface / syntax /
verifier / brevity stack.

## Fast-Abandon Rule

Drop this method quickly if either condition holds:

1. local mixed-candidate tests show little or no `signal_std` gain
2. the reward mostly duplicates `interface_reward` or the existing
   `clause_aware_verifier_reward`

That is the intended operating discipline for this paper: low-cost trial, fast
exit if weak.
