# Clause-Aware Verifier Reward for Code RL

## Core Idea

Promote verifier feedback from a flat failure-count signal into a clause-level behavioral reward based on whether individual requirements appear satisfied.

## Why It Matters

- Produces more reward spread inside a small GRPO group
- Gives partial credit for satisfying some behaviors even when the final answer still fails
- Targets the current RL bottleneck directly: low-signal skipped steps

## Initial Implementation

- Derive coarse clause coverage from behavior hints and failure details
- Blend clause reward into the existing total reward conservatively
- Optional use through `--research-methods clause_aware_verifier_reward`
