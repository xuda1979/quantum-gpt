# Verifier-Guided Near-Miss Repair Curriculum for Quantum Code Generalization

## Core Idea

Use verifier and failure structure to bias both SFT and GRPO toward repairable near-miss cases instead of treating all failures as equally uninformative.

## Why It Matters

- More information-bearing samples for RL
- Better use of strict unseen tasks where pass/fail is sparse
- Easy leadership story: the model learns from almost-correct solutions, not only perfect references

## Initial Implementation

- Prompt-level repair emphasis
- Mild task-weight bias toward structured tasks with richer behavior hints
- Optional use in both SFT and GRPO through `--research-methods verifier_guided_repair_curriculum`
