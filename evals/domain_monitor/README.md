# Domain Performance Monitor (industrial-standard eval monitoring)
Purpose: track the adapter's performance drift across the sciences relevant to quantum-computing
coding (math, coding/SE, physics, QIS) as training evolves — NOT just the heldout pass@1.
Coordinator contract (all domain agents MUST build into this structure):
- Each domain: `evals/domain_monitor/domains/<domain>/manifest.json` (list of benchmark task ids
  drawn from existing evals/benchmarks/*.txt) + a `run.py` that, given (base_model_path,
  adapter_path, device), evaluates and writes:
- Shared output: `evals/domain_monitor/results/<adapter_name>/<domain>_<date>.json`
- A single cross-domain runner assembles per-domain JSONs into a time-series drift summary.
- TDD: each domain ships a local unit test (pytest tests/test_domain_<domain>.py) validating its
  manifest points at existing benchmark ids and its runner parses real eval JSONs.
- THEORY OF CHANGE: a domain-performance drift curve (math/coding/physics over adapter checkpoints)
  + a regression GATE = industrial-standard measurement that catches silent domain regressions even
  when the frozen 18-task holdout pass@1 is flat.
See AGENT_BRIEFS.md written by the coordinator when all 5 domain agents land.
