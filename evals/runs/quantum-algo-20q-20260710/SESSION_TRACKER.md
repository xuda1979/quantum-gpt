# Session Tracker — 20 Quantum Algorithm Coding Problems × Multi-Model Eval

**Run dir:** `evals/runs/quantum-algo-20q-20260710/`
**Started:** 2026-07-10 (Asia/Shanghai)
**Owner:** Claude Code session (this conversation)

## R&D Method (one-pass record)

### Goal
Create **20 new quantum-algorithm coding problems** that require a **full Python program with a `main()` function** that **calculates and prints** a concrete numerical / structural result. Generate code from each available base + adapter model, document all generated code in this run, then evaluate (execute) every candidate against a deterministic reference test.

### Models (3 accessible in this environment)
The phrase "27 B / 35 B adapters and base models" maps to the three Huanxin-served backends already exercised in the `qaoa-maxcut-5cycle-20260709` run:

| short name | role | endpoint | api env var |
|---|---|---|---|
| `glm5.2` | frontier base (teacher) | `http://127.0.0.1:18105/v1/responses` (OpenAI Responses API) | `HUANXIN_GLM52_API_KEY` |
| `deepseek-v4-pro` | frontier base (teacher) | `https://aihuanxin.cn/qdlake/trans/model-subscribe/63/...` (chat completions) | `HUANXIN_DEEPSEEK_V4_PRO_API_KEY` |
| `qwen3.6-27b-rag` | **27 B Qwen3.6 + RAG adapter** (the quantum-intelligence MCP backend) | `QUANTUM_INTELLIGENCE_URL` | `QUANTUM_INTELLIGENCE_API_KEY` |

(Claude itself is routed through `ANTHROPIC_BASE_URL=http://127.0.0.1:57388` and is not used as a candidate here.)

### Pipeline (per problem)
1. Write `prompts/quantum_<id>.txt` — Chinese/English prompt demanding **full code + `def main()` + prints a number/result**.
2. Write `reference/quantum_<id>.py` — golden solution with `main()`.
3. Write `tests/quantum_<id>_test.py` (or inline in tracker) — runs reference as subprocess, asserts key printed numbers.
4. Generate `candidates/<model>/quantum_<id>.py` for each of the 3 models.
5. Execute each candidate in the project venv, capture stdout + exit code, compare to expected.
6. Tabulate pass/fail in `SUMMARY.md` and paste every candidate into `CODE_DOCUMENTATION.md`.

### Tools / env
- Project venv `.venv/bin/python3` has qiskit, numpy, networkx, qiskit-algorithms, qiskit-optimization.
- Secrets via `source ~/.codex/secrets/quantum-intelligence.env` (already exported into the shell env of this session).
- Reference: prior script `/tmp/gen_qaoa_candidates.py` (read for endpoint patterns).

### Status
- [x] Plan locked
- [x] 20 problems written (prompts + reference + tests) — `logs/reference_check.txt` shows 20/20 reference solutions pass.
- [x] Generation script written and run for all 3 models (glm5.2, deepseek-v4-pro, qwen3.6-27b-rag)
- [x] Execution + scoring — `logs/evaluation_results.json` and `SUMMARY.md` written.
- [x] Documentation file `CODE_DOCUMENTATION.md` populated with all 60 candidate sources
- [x] `SUMMARY.md` final table

### Final results (2026-07-10)
- **deepseek-v4-pro:** 13/20 PASS (best)
- **glm5.2:** 6/20 PASS (many EXITs due to prose mixed into code)
- **qwen3.6-27b-rag:** 0/20 — **service down (HTTP 503 "no healthy upstream") for the entire session**; all 20 candidates are error stubs. Re-run `/tmp/regen_failed.py` once the service recovers.
- Overall: 19/60 (31.7%), or 19/40 (47.5%) excluding the qwen-rag outage.

(Update this checklist as the session progresses; if the session dies, the next session can resume from the unchecked items above.)

### Resumption notes (if session dies mid-run)
1. Run dir is `evals/runs/quantum-algo-20q-20260710/`.
2. Problems are defined in `PROBLEMS.json` (id, title, expected_substrings).
3. Prompts in `prompts/<id>.txt`, references in `reference/<id>.py`.
4. Use `/tmp/verify_references2.py` to re-check references (writes `logs/reference_check.txt`).
5. Use `/tmp/gen_candidates.py` to generate candidates. Sources secrets from `~/.codex/secrets/quantum-intelligence.env` and the shell env vars `HUANXIN_GLM52_API_KEY`, `HUANXIN_DEEPSEEK_V4_PRO_API_KEY`.
6. Use `/tmp/regen_failed.py` to retry only failed candidates (with longer timeouts).
7. Use `/tmp/evaluate_candidates.py` to execute each candidate and produce `SUMMARY.md`.

### User session notes
- 2026-07-10: "If training is needed, always submit a training job; don't use the local NPU environment." (Acknowledged — not relevant to this eval-only session.)

