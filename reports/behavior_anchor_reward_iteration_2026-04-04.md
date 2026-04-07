# Behavior-Anchor Reward Iteration - 2026-04-04

## Objective

Test a cheap verifier-adjacent reward signal that can increase GRPO reward spread
 on near-miss code groups without touching trainer internals first.

## Implemented Method

- paper:
  - `research/papers/behavior_anchor_coverage_reward/paper.md`
- plugin:
  - `research/papers/behavior_anchor_coverage_reward/code/plugin.py`
- flag:
  - `--research-methods behavior_anchor_coverage_reward`

Method summary:

- derive anchor tokens from `behavior_hints`
- add a small amount of interface-name anchor coverage
- reward candidates that contain more of the task’s behavioral vocabulary
- keep the blend bounded and conservative

This is intentionally a low-risk filter step. If it fails to create new reward
spread beyond the current stack, it should be abandoned quickly.

## Local Validation

### Tests

```bash
python3 -m pytest -q tests/test_research_plugins.py
PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile \
  research/papers/behavior_anchor_coverage_reward/code/plugin.py
```

Observed:

- `tests/test_research_plugins.py` -> `4 passed`
- plugin compile -> pass

### Synthetic Near-Miss Signal Probe

Compared three candidates with identical baseline reward but different anchor
coverage on a bit-flip error-detection task pattern.

Observed local result:

```python
{
  "baseline_signal_std": 0.0,
  "anchor_signal_std": 0.009977749548852444,
  "clause_signal_std": 0.0,
  "combo_signal_std": 0.008979967795312405,
  "anchor_rewards": [0.6, 0.5, 0.3],
  "anchor_totals": [0.3112, 0.3032, 0.2872],
  "clause_totals": [0.252, 0.252, 0.252]
}
```

## Interpretation

The method passed the first keep/drop gate:

- baseline reward stayed flat
- the existing clause-aware reward also stayed flat on this probe
- behavior-anchor coverage created non-zero spread

This does **not** prove end-to-end training improvement yet. It only proves the
method is not obviously redundant on the first local signal check.

## Keep / Drop Decision

Current decision: **keep for the next small-smoke research pass**

Reason:

- it adds measurable local variance with minimal implementation risk
- it is removable
- it does not require trainer surgery

Fast-drop condition:

- if a real GRPO smoke still shows little change in skipped-step behavior or if
  the reward mostly tracks interface-only structure, stop using it

## Next Stronger Direction

If plugin-only reward shaping plateaus, the next higher-upside method is:

- `failure_bucket_diversity_routing`

Rationale:

- the current real bottleneck is still flat within-group signal
- group-level diversity over verifier failure buckets attacks that more directly
- but it requires a new group hook in the trainer, so it is the second-stage
  move rather than the first low-risk one
