# Pluginized Research Methods for Quantum Coding LLM Iteration

## Objective

Keep experimental methods removable while preserving a stable training path.

## Design

- Research papers live under `research/papers/<paper_id>/`
- Experimental code lives under `research/papers/<paper_id>/code/`
- Training entrypoints load optional methods by name through `training/research_plugins.py`
- Base training remains usable with no research methods enabled

## Why This Matters

- We can enable or disable research ideas by config
- Leadership can trace each claimed innovation to a specific paper/code folder
- Experimental methods do not have to stay welded into the base trainer forever

## Current Scope

- SFT hooks:
  - record/message augmentation
- GRPO hooks:
  - prompt augmentation
  - task-weight adjustment
  - reward-breakdown adjustment

## Next Step

Graduate stable ideas into shared training code only after repeated wins.
