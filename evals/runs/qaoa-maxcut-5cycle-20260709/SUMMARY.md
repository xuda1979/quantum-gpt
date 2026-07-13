# QAOA Max-Cut 5-cycle — Multi-Model Eval (2026-07-09)

## Task

`quantum_qaoa_maxcut_5cycle` — Write a complete, runnable Python + Qiskit program that:
- Builds a 5-vertex undirected cycle graph with edges (0,1),(1,2),(2,3),(3,4),(4,0)
- Solves Max-Cut with QAOA using `StatevectorSampler`, `COBYLA`, and `MinimumEigenOptimizer`
- Prints the binary solution, the two vertex sets, and the max-cut value

The 5-cycle has optimal cut value **4** (10 optimal bitstrings out of 32).

## Models evaluated

All three Huanxin-served base models accessible from this workstation. No locally
trained LoRA adapter weights are available — every adapter training job in
`outputs/` either failed on ASI1 or has `latest_checkpoint: None`, so the
"adapter" row below is the RAG-augmented qwen3.6-27b service
(`qwen3.6-27b-rag`, the quantum-intelligence MCP backend).

| Model | Role | Pass | Failure category | Notes |
|---|---|---|---|---|
| `glm5.2` | base | ✅ PASS | — | cut=4 (optimum). Built QP via `networkx` + `QuadraticProgram`, reps=2. |
| `deepseek-v4-pro` | base | ❌ FAIL | dependency | `from qiskit_algorithms import QAOA, MinimumEigenOptimizer` — `MinimumEigenOptimizer` lives in `qiskit_optimization.algorithms`, not `qiskit_algorithms`. ImportError on line 1. |
| `qwen3.6-27b-rag` | RAG adapter | ❌ FAIL | assertion | Output is retrieved IBM Quantum documentation prose, not runnable code. RAG retrieval dominated the response. |

## Per-model artifacts

- `glm5.2/candidates/quantum_qaoa_maxcut_5cycle.py` — passes
- `deepseek-v4-pro/candidates/quantum_qaoa_maxcut_5cycle.py` — ImportError
- `qwen3.6-27b-rag/candidates/quantum_qaoa_maxcut_5cycle.py` — non-code output
- `generation-log.json` — model call timings and output sizes
- `<model>/scorecard.json` — full per-model scorecard

## Reference solution

`evals/tasks/quantum/qaoa_maxcut_5cycle/candidate.py` — passes 5/5 runs (deterministic optimum).

## How to reproduce

```bash
# Regenerate candidates
source ~/.codex/secrets/quantum-intelligence.env
.venv/bin/python3 /tmp/gen_qaoa_candidates.py

# Score each model
for m in glm5.2 deepseek-v4-pro qwen3.6-27b-rag; do
  .venv/bin/python3 evals/runner/run_eval.py \
    --candidate-map evals/runs/qaoa-maxcut-5cycle-20260709/$m/candidate-map.json
done
```
