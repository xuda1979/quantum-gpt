# GRPO V2 Iteration - 2026-03-31

## What changed

- Upgraded [training/grpo_trainer.py](../training/grpo_trainer.py) from a pseudo-GRPO top-half weighted CE loop to a more faithful completion-only GRPO update.
- Added length-normalized completion log-prob updates with explicit KL regularization against the sampled policy.
- Added dense verifier-aware reward shaping:
  - pass reward
  - syntax/parse reward
  - interface-match reward
  - verifier partial credit based on structured test-detail budget
- Added an adaptive curriculum that prioritizes:
  - quantum tasks
  - tasks with low EMA reward
  - tasks with low visit count via an uncertainty bonus

## Why this matters

- The previous trainer only learned from binary pass/fail and did not actually use the `grpo_loss()` path.
- The new trainer can learn from near-miss candidates instead of only full passes.
- The adaptive curriculum gives us a concrete innovation to report beyond plain SFT and plain GRPO.

## Validation

- `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile training/grpo_utils.py training/grpo_trainer.py scripts/render_quantum_generalization_commands.py`
- `python3 -m pytest -q tests/test_grpo_utils.py`
  - result: `5 passed`
- Regenerated:
  - [artifacts/quantum-generalization-command-sheet.txt](../artifacts/quantum-generalization-command-sheet.txt)

## Next remote step

- Run the GRPO-v2 command from the refreshed command sheet on `ai2` starting from the current OmniCoder SFT adapter, then score on the strict unseen clean holdout.
