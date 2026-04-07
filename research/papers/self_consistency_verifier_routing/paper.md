# Self-Consistency Verifier Routing for Code SFT and GRPO

## Core Idea

Bias training toward completions that would survive a cheap internal self-consistency check before they ever reach the external verifier, then reinforce candidates whose verifier, syntax, and interface signals agree.

## Why It Matters

- GRPO already samples multiple candidates per task, but weak reward spread can leave good candidates under-weighted
- A small self-consistency routing bias is implementable with the current plugin hooks
- The method is removable by flag and does not require changing the core trainer loop first

## Initial Implementation

- Add a short SFT system instruction that teaches "draft a few candidate approaches mentally, then emit the one most likely to satisfy tests"
- Add a matching GRPO prompt suffix that favors verifier-aligned candidate routing
- Slightly upweight tasks with richer interface and behavior structure, where candidate selection matters most
- Blend a conservative self-consistency score into GRPO reward using existing verifier, syntax, interface, and pass signals
- Optional use through `--research-methods self_consistency_verifier_routing`
