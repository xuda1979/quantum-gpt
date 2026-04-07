# Uncertainty-Triggered Repair Replay for SFT and GRPO

## Core Idea

When a task looks uncertain or hard, replay it with an explicit repair-first bias instead of treating it like a generic sample.

## Why It Matters

- Hard examples carry more learning signal than easy ones
- Near-miss repairs are especially valuable for code tasks
- The same policy can help both SFT and GRPO without changing the base trainer

## Initial Implementation

- Infer hardness from task metadata such as difficulty, category, detail budget, and interface complexity
- Add a short repair-first system prompt for hard SFT records
- Upweight hard tasks during GRPO sampling
- Give a small bonus to near-miss GRPO rewards so repairable failures stay informative
- Optional use through `--research-methods uncertainty_triggered_repair_replay`

