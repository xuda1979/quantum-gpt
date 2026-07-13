# MEMORY.md

## Stable Decisions

- Training execution policy clarified `2026-07-10`:
  - **All training runs must be submitted as training jobs (e.g. ASI1/ASI2/ASI3 launch scripts via the Huanxin job-submission flow), never run directly on the environment's own NPU.** The local/box NPU is not to be used for training anymore.
  - This applies to RL+distill orchestrator runs, LoRA SFT, GRPO, and any other training. Eval/inference may still use local resources where appropriate.
  - Rationale: keeps the shared NPU box free for serving/eval and gives each training run a clean, queued, observable lifecycle.
  - Practical effect: the Phase 5 ablation sweep (per-artifact scoring plan) and the science-distill iter-1 runs must all go through the launcher job-submission path, not a foreground `bash` on the NPU host.

- DR-GRPO trainer integration completed `2026-07-09`:
  - `training/grpo_trainer.py` now wires in BOTH DR terms when the
    `doubly_robust_quantum_grpo` plugin is enabled: (1) the DPO pair
    loss via `compute_dr_pair_loss()` and (2) the PPO-side variance
    correction `psi * E[(r-1)*A]` via `compute_dr_variance_correction()`.
  - Previously only term (1) was wired; term (2) was defined in
    `dr_pair_loss.py` but never called. This was a real paper-vs-impl
    gap — "doubly robust" needs both terms.
  - Both terms are no-ops when the plugin is absent or hyperparams are
    zero, so base GRPO is unchanged. Step records now carry
    `dr_variance_correction_value` and `dr_psi` fields.
  - Tests: `tests/test_doubly_robust_quantum_grpo.py` (20 tests) all
    pass; 30 pass across DR + GRPO metrics suites.
- Huanxin webshell daemon transport caveat `2026-07-09`:
  - `scripts/ai_shell.sh` reports "Using daemon transport" but shell
    stdout is intermittently NOT captured back through the
    browser-automation transport. When this happens, remote state
    (DR-GRPO run status, eval JSONs, training logs) cannot be
    refreshed locally. Needs transport debug or an SSH fallback.
- Local eval gap-analysis toolchain works `2026-07-09`:
  - `python3 -m evals.subsystem.dataset_gap recommend --eval <scorecard.json>
    --model adapter` produces concrete "add 3-5 examples for <task>"
    recommendations on the local 25-task scorecards.
  - The 44-task / 495-task holdout eval JSONs live on remote and the
    one pulled copy (`evals/runs/iter2-pull/eval-27b-...json`) is
    CORRUPTED (truncated to 2179 bytes by an incomplete S3 download).
    Re-pull needed before full-holdout gap analysis.

- Codex GLM5.2 routing clarified on `2026-07-07`:
  - when invoking Codex with `--model glm5.2` or `-m glm5.2`, use the Huanxin GLM5.2 URL and API key in the Claude setting, not yunwu
  - the local wrapper `/Users/daxu/homebrew/bin/codex` should force profile `yunwu-claude`, start/use the `127.0.0.1:18105` Huanxin GLM5.2 proxy, override `model_providers.yunwu_claude.base_url` to that proxy, and use `HUANXIN_GLM52_API_KEY`
  - generated Codex configs should put `glm5.2` in the Claude provider/profile slot with Huanxin GLM5.2 URL/key; do not represent `glm5.2` as a normal yunwu model alias

- Two-stage training direction clarified on `2026-06-30`:
  - current phase is model code ability: quantum code generation, general software engineering, RAG-assisted API correctness, executable tests, SFT/trajectory cloning, then GRPO/RLVR on code verifiers
  - later phase is quantum-computing scientific capability: select 1000 important/classic papers, generate progressive paper-grounded QA/code/research-direction data, distill with SFT, then run mixed distillation + RL while preserving code replay
  - durable roadmap: `docs/two-stage-training-roadmap-2026-06-30.md`

- INER S3 routing changed on `2026-05-15`:
  - treat `https://iner.aihuanxin.cn` bucket `jtdlp-21b4208dde424e96b159362ef49c9c96` as the only active S3 relay for this workspace
  - default project root is `iner:jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt`
  - direct bucket-specific `rclone copyto` / `lsf` operations are now verified working
  - root-level `rclone lsd iner:` may still fail because the endpoint root serves HTML instead of S3 XML, so future probes should target the explicit bucket path
- Local release path added on `2026-04-30`:
  - the user-facing CPU-only local version should use a quantized Qwen3.6 GGUF model served through `llama.cpp` with `--n-gpu-layers 0`
  - full local testing on a 16 GB Mac proved `Qwen3.6-27B-Q4_K_M.gguf` can load CPU-only but is functionally too slow even for tiny generation
  - default local model is now the practical CPU target: `unsloth/Qwen3.6-35B-A3B-GGUF` / `Qwen3.6-35B-A3B-UD-IQ2_XXS.gguf`
  - optional higher-quality 27B/35B quantizations remain available through installer flags, but they should not be the no-GPU/NPU default
  - one-command install path is `scripts/install_qwen36_rag_local.sh`; smoke mode avoids the huge model download but still validates doc fetch and RAG index build
- Model policy changed on `2026-04-27`:
  - use `Qwen/Qwen3.6-27B` as the base model for the next round of fine-tuning
  - all new SFT and reinforcement-learning runs should default to local/remote path `models/Qwen3.6-27B`
  - keep Qwen2.5 and OmniCoder references as historical baselines or explicit comparison lanes, not as default training bases
- Huanxin training target changed on `2026-04-26`:
  - do not use the old `ai2` environment for new training runs
  - all new training must target the Huanxin `AI` train-dev environment:
    `https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=AI`
  - before any Huanxin shell, sync, or training action, verify/login to that exact `AI` environment
  - if auth is stale, repair or login first; do not assume an old ai2 daemon/session is valid
  - `TOOLS.md`, `AGENTS.md`, `PROJECT.md`, Huanxin skills, and the generic Huanxin browser/shell helpers were updated to prefer `AI`
- Huanxin auth authorization clarified on `2026-06-01`:
  - the user authorizes Codex to perform Huanxin auth/login and session repair for this workspace through the repo Huanxin skill workflow when needed for Huanxin work
  - do not store secrets or auth material: no passwords, SMS codes, cookies, bearer tokens, credential-bearing callback URLs, browser profiles, or private auth state in memory, docs, logs, final answers, or skill bodies
  - preserve the existing manual-mode and automation-disabled-by-default protections; authorization to log in is not authorization to disrupt a manually used Huanxin webshell
- Huanxin environment policy changed on `2026-04-04`:
  - both `ai1` and `ai2` are valid R&D targets for this workspace
  - `ai2` remains the default path, but `ai1` may be used when it provides better capacity or parallelism
  - do not kill the Huanxin browser daemon or otherwise discard the authenticated browser session unless explicitly instructed
  - keep the Huanxin environment in regular use with lightweight checks so the login session does not expire from inactivity
- The next high-value model transition is `Tesslate/OmniCoder-9B`, but it is not runnable on the current text-only SFT path yet.
- The real OmniCoder blocker is local trainer/runtime compatibility:
  - `training/qwen_sft_peft.py` rejects `model_type=qwen3_5`
  - the next required engineering step is a processor-aware smoke / SFT path
- For qualitative report recovery, the fetch helper is not the main suspect; the bigger issue was writer-side exposure of partially written JSON.
- `scripts/run_base_vs_adapter_eval.py` should keep using atomic write semantics for report output so watchers never fetch half-written reports.
- OmniCoder transition status changed on `2026-03-27`:
  - the trainer and smoke path now use capability checks instead of hard-rejecting `qwen3_5` by name
  - the required bootstrap runtime is `transformers 4.57.1` or newer
  - `ai2` cannot fetch `Tesslate/OmniCoder-9B` from Hugging Face directly, so model transfer must go through the local snapshot + S3 relay path
  - the local verified snapshot now exists at `models/OmniCoder-9B`
- OmniCoder transition status changed again on `2026-03-29`:
  - `transformers 5.4.0` on `ai2` is sufficient for the local OmniCoder snapshot to pass the processor-aware smoke path
  - a real OmniCoder 9B 1-NPU fine-tuning smoke now completes on `ai2`
  - a real OmniCoder 9B 2-NPU distributed smoke also completes on `ai2` when pinned to free devices `6,7`
  - a larger 20-step semantic-v4 OmniCoder 9B run also completes on `ai2` on 2 free NPUs with `final_eval.loss ~= 0.373` and `final_eval.perplexity ~= 1.452`
  - the remaining OmniCoder blocker is not trainer correctness; it is the shared-cluster resource state for 8 free NPUs because foreign `paper_aligned_pretrain.py` jobs occupy NPUs `0-5`

- Delivery status changed on `2026-03-30`:
  - the current OmniCoder 9B adapter clears the workspace delivery gate on ai2
  - fixed benchmark: `evals/benchmarks/delivery_pass1_v1.txt`
  - metric: pass@1 on 10 tasks, single generation, no manual repair
  - confirmed result: `9/10` passed (`90%`)
  - remaining known miss: `software_parser_regression_tests` due generated `SyntaxError`
- ai2 workspace path rule:
  - the only valid work folder for this project on ai2 is `/root/root/work/quantum-gpt`
  - default all ai2 shell commands, sync targets, provider launches, eval runs, and training paths to that directory
  - do not drift to other similar-looking paths such as `/root/work/...`
- Quantum-gate evaluation changed again on `2026-03-30`:
  - the hard OmniCoder continuation adapter looked flat at `6/12` only under `--max-new-tokens 192`
  - the dominant blocker was inference truncation on the harder quantum tasks, not SFT quality alone
  - rerunning the same adapter on ai2 at `--max-new-tokens 384` raised the effective quantum-only gate result to `11/12`
  - a targeted rerun of the final stabilizer miss at `--max-new-tokens 512` passed, so the practical quantum-only gate ceiling is `12/12` under the corrected inference budget
  - `scripts/run_hf_pass1_eval.py` now has a `--token-budget-preset quantum_heavy` option that maps to `512`
  - the manifest-driven default is now packaged into the quantum-heavy run dirs via `token_budget_preset: "quantum_heavy"`
  - with the hard continuation adapter plus corrected budget, the broader mixed `delivery_pass1_v1` gate also clears cleanly; scorecard showed `25/25` over the full suite, which implies `10/10` on the overridden delivery tasks
  - the corrected budget alone is not enough: base OmniCoder still sits at the old effective `4/10` on the quantum-heavy gate, while the hard continuation adapter clears it
  - the full `delivery_pass1_quantum_v2` run now also clears directly using only the manifest-driven default on ai2, with no explicit token override in the launch command
- Next-iteration data/RL path changed on `2026-03-30`:
  - the old `template-v2.jsonl` corpus is now explicitly too small for leadership review; it only had `460` total rows
  - the new balanced large corpus is `data/generated/omnicoder-template-large-v1` with `2208` train and `552` held-out eval rows
  - the new quantum-only corpus is `data/generated/omnicoder-quantum-large-v1` with `1536` train and `504` held-out eval rows
  - both large corpora use `holdout_policy: split_family_disjoint_v1`, which keeps train/eval prompt families disjoint and guarantees zero train/eval `example_id` overlap
  - `training/grpo_trainer.py` is now the concrete RL next-step path: it supports `--adapter-init`, `--benchmark-file`, `--domain-filter`, OmniCoder-compatible text backend loading, and richer task-aware prompts
  - user clarification: the evaluation dataset must never show up in training; treat this as a stricter task/source-level holdout requirement, not just different `example_id`s
  - consequence: the newly built large template corpora are larger and cleaner, but they are still interim because they reuse the same underlying task ids across train/eval
  - the first strict unseen-eval corpus that satisfies the user’s clarified rule is `data/generated/omnicoder-generalization-holdout-v1` with `1440` train and `504` eval rows
  - that corpus uses `holdout_policy: task_disjoint_v1` and has zero overlap at both the `example_id` and `task_id` levels
  - the current source-task inventory is still small, especially for quantum (`12` total tasks), so future quantum-only unseen evaluation will require new source tasks or a more aggressive holdout split
  - the strict quantum-only unseen corpus is `data/generated/omnicoder-quantum-generalization-holdout-v1` with `1024` train and `504` eval rows
  - its fixed unseen benchmark is `evals/benchmarks/quantum_generalization_holdout_v1.txt`
  - local Qwen SFT smoke on the strict quantum corpus reached real first-loss computation, so the stricter dataset format is consumable by the existing SFT path even though the CPU backward/save tail was too slow to finish during this turn
  - `evals/runner/prepare_prompts.py` now supports `--token-budget-preset`, so future quantum-heavy eval runs can be generated with the correct manifest budget directly instead of manual post-editing
  - the next blocked step for the unseen-holdout baseline is ai2 browser/shell transport reliability, not dataset or run-dir packaging
  - `scripts/render_quantum_generalization_commands.py` now produces a concrete strict-iteration runbook, and the rendered artifact is `artifacts/quantum-generalization-command-sheet.txt`
  - a serious eval leak was fixed on `2026-03-30`: `evals/runner/prepare_prompts.py` had been embedding task reference candidates into prompts; reference candidates are now excluded by default and only re-enabled with `--include-reference-candidate`
  - the first honest local baseline on the strict unseen quantum benchmark is `0/4` for `models/Qwen2.5-1.5B-Instruct` on `evals/runs/qwen25-quantum-generalization-holdout-clean-local`
  - candidate cleanup for local HF pass@1 evals is now centralized in `evals/runner/candidate_sanitize.py`, and `scripts/run_hf_pass1_eval.py` normalizes the written candidate files again before scoring
  - after that cleanup hardening, the honest local unseen Qwen baseline still stays at `0/4`; the earlier `SyntaxError` on `quantum_phase_estimation_circuit` downgrades into a real API-shape failure, so the remaining misses are model generalization failures rather than markdown-tail contamination
  - the override-only summary artifact for that corrected baseline is `reports/qwen25_quantum_generalization_holdout_clean_local_override_summary.json`
  - the clean canonical OmniCoder unseen run dir is `evals/runs/omnicoder-quantum-generalization-holdout-v1-clean`
  - `scripts/render_quantum_generalization_commands.py` and `artifacts/quantum-generalization-command-sheet.txt` now default to the clean unseen run dir, not the old leaky one
  - `scripts/verify_holdout_dataset.py` is the new integrity gate for leadership-facing corpus claims; it checks count thresholds, duplicate `example_id`s, and cross-split overlap on `example_id`, `task_id`, and `prompt_family`
  - verified integrity artifacts now exist for both strict holdout corpora:
    - `reports/omnicoder_quantum_generalization_holdout_v1_integrity.json`
    - `reports/omnicoder_generalization_holdout_v1_integrity.json`
  - both reports pass the `>=500 eval rows` requirement and confirm zero train/eval overlap at the `example_id`, `task_id`, and `prompt_family` levels
  - protocol fairness for the current strict quantum headline is now explicit: the Qwen clean baseline and the OmniCoder 8-NPU adapter run use the same 4 override tasks, `prompt_version=v2`, `prompt_style=repair_focused`, `include_reference_candidate=false`, and manifest-driven `token_budget_preset: "quantum_heavy"`
  - as of `2026-04-10`, the missing OmniCoder 9B base result on that same strict protocol is no longer a vague TODO; a fresh ai2 base-eval attempt proved the remaining blocker is model restoration plus Huanxin transport stability
  - later on `2026-04-10`, the blocker moved forward again: direct ai2 daemon probes confirmed `models/OmniCoder-9B` is now restored on ai2 with `model.safetensors`, `config.json`, and about `18G` of payload
  - the fresh base strict-holdout rerun still failed, but now for a more precise reason: ai2 is evaluating with `/usr/bin/python3` and `transformers==4.44.0`, which is too old to recognize `qwen3_5`; the next needed step is a Qwen3.5-capable runtime upgrade on ai2, not another snapshot restore
  - do not describe the current `0/4 -> 2/4` report headline as a full same-model base-vs-adapter comparison yet; it is a protocol-matched clean-baseline-vs-adapter result, with the same-model OmniCoder base line still blocked on ai2 runtime compatibility
  - ai2 browser-shell transport was fixed on `2026-03-31`; the old diagnosis of “generic browser unreliability” is now too weak
  - the real launcher fix is in `browser-automation/huanxin_browser_launch.js`: use the full Chrome-for-Testing binary and support Darwin fallback away from the crashing Playwright headless-shell path
  - `browser-automation/huanxin_shell_exec.js` now reports `login_required` explicitly and retries `Shell终端` activation through transient Huanxin spinner overlays
  - a real end-to-end ai2 shell command now succeeds again through `./scripts/ai2_shell.sh`
- Gemma local runtime gating changed on `2026-04-09`:
  - the canonical local interpreter probe is now `python3 scripts/resolve_python_interpreter.py --min-version 3.10`
  - `scripts/run_autonomous_rd_cycle.py` now records a concrete `gemma_local_python_gate` with candidate interpreter evidence and an install command when no suitable interpreter exists
  - the current local machine still only exposes `/usr/bin/python3` at `3.9.6`; no `python3.10+` was found in the standard Homebrew prefixes
  - Homebrew itself is present at `/Users/daxu/homebrew/bin/brew`, so the next local runtime step is concretely `brew install python@3.11` before retrying Gemma smoke
- Gemma local runtime gating changed again on `2026-04-10`:
  - the repo-local offline bootstrap path now works: `.local-python/cpython-3.11.15/bin/python3.11` is a verified CPython 3.11.15 + OpenSSL 3.6.1 interpreter built from cached local artifacts
  - `scripts/run_autonomous_rd_cycle.py` now exposes a separate `gemma_runtime_bootstrap` stage before `gemma_smoke`, so the controller distinguishes runtime install failures from backend preflight failures
  - the fresh `reports/autonomous_rd_cycle_gemma4-26b-a4b-it_2026-04-10_state.json` state shows `local_eval_gate` and `holdout_integrity` passed, `gemma_local_python_gate` passed, and the current blocker moved forward to `gemma_runtime_bootstrap`
  - a second 2026-04-10 experiment narrowed this further: the stable wheel stack from `training/requirements-huanxin-cpu.txt` installs successfully on the py311 environment, but `transformers==4.57.1` still fails Gemma at `runtime_compat`
  - the current precise Gemma blocker is therefore no longer “missing Python >=3.10” or “generic py311 wheel bootstrap”; it is obtaining a newer-than-4.57.1 Transformers source/runtime that actually recognizes `gemma4`, and that source-fetch path is still failing on the local machine/network path
