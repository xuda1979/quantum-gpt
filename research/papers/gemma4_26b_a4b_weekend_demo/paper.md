# Gemma 4 26B-A4B MoE Weekend Demo Report

## Executive Summary

This report records the decision to abandon the local and Huanxin `Gemma 4 31B-it` path and switch the weekend demo path to the officially published `google/gemma-4-26B-A4B-it` checkpoint instead. The reason is practical, not cosmetic:

- the `31B` path consumed too much local disk and transfer time
- the weekend demo needs a smaller MoE checkpoint with a cleaner expert-tuning story
- the `26B-A4B` checkpoint is a better fit for expert-specific fine-tuning (`ESFT`) and LoRA-on-MoE experimentation
- the workspace already has a validated local -> S3 -> ai2 handoff path, so the most credible next move is to switch targets, not keep forcing the abandoned `31B` route

Primary source references used for this switch:

- Official Google announcement for Gemma 4 on April 2, 2026:
  - https://blog.google/technology/developers/gemma-4/
- Official Hugging Face model source for the new target:
  - https://huggingface.co/google/gemma-4-26B-A4B-it

One important research-hygiene note:

- the Anthropic `SGTM` claim that was raised during planning was verified against Anthropic’s own December 8, 2025 release and does **not** describe a “generalized trajectory modeling planner” in the way it was quoted to us
- we therefore do **not** present that claim as a factual basis for this report
- instead, we use the useful part of the idea honestly: keep explicit trajectory records for promising, blocked, and fallback R&D lanes so the autonomous loop does not stall or blur evidence across them

## Data

### Current in-repo data assets

The current demo path already has usable supervised and evaluation corpora:

- train:
  - `data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl`
- eval:
  - `data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl`
- manifest:
  - `data/generated/omnicoder-quantum-generalization-holdout-v1/manifest.json`
- benchmark:
  - `evals/benchmarks/quantum_generalization_holdout_v1.txt`

These assets are suitable for a first Gemma 4 MoE demo because:

- they are already wired into the controller and timeboxed launchers
- the holdout policy is stricter than our older corpus splits
- the repo already records the integrity expectation that train/eval must remain task-disjoint and prompt-family-disjoint

### Weekend-demo data additions

For the weekend demo we should add a smaller, more curated “leadership-safe” slice on top of the existing corpus:

- `100-200` high-quality quantum-programming and scientific reasoning examples
- short-to-medium length prompts that the model can complete reliably under finite demo latency
- explicitly reviewed examples where the final answer is unambiguous enough for verifier-based analysis

The recommended composition is:

- `40-60%` quantum coding tasks
- `20-30%` scientific QA and derivation tasks
- `20-30%` interface-constrained coding tasks that make failure analysis easier

### Raw paper corpus status

On `2026-04-08`, we explicitly checked the currently reachable paper-storage surfaces:

- local `paper/`:
  - found one real source document:
    - `paper/quantum-coding-llm-rnd.tex`
- S3 `paper/`:
  - only `2` objects
  - total size about `103KB`
  - this is not a large raw-paper corpus
- S3 `data/`:
  - contains many generated JSONL corpora
  - these are useful training sets, but they are not the same as the claimed raw-paper archive
- ai2:
  - live paper-directory inspection was attempted
  - the current blocker is not login itself but the ai2 browser daemon being down during this turn

So the honest current state is:

- we have already restored the paper-to-dataset tooling
- we have verified one local source-paper path end to end
- we have **not yet** confirmed the larger stored quantum-paper archive the user expects

### Restored paper-to-SFT tooling

The repo now again contains a direct document-prep path:

- `tools/pdf_to_sft.py`
- `tools/prepare_pdf_dataset.py`
- `scripts/build_paper_sft_dataset.py`

This path has already been validated locally:

- `python3 scripts/build_paper_sft_dataset.py paper/quantum-coding-llm-rnd.tex --output-dir data/generated/quantum-paper-smoke-v1 --dataset-name quantum_paper_smoke`
- produced:
  - `data/generated/quantum-paper-smoke-v1/messages/quantum_paper_smoke_messages_train.jsonl`
  - `data/generated/quantum-paper-smoke-v1/messages/quantum_paper_smoke_messages_valid.jsonl`
- current verified row counts:
  - train: `4`
  - valid: `1`

### Trajectory data

The user requested we use “old model trajectories as nourishment” for the next model. That idea is reasonable here, with one practical constraint:

- we should use prior verified model and agent traces from this workspace as **synthetic supervision**, not as a substitute for evaluation

For this repo, that means:

- keep using prior OmniCoder and autonomous-cycle outputs as a source of high-value action traces
- convert only the cleanest traces into structured records for model fine-tuning or for controller-side decision support
- never mix evaluation tasks into training trajectories

### Data risk controls

Leadership questions about data quality should be answerable directly:

- Are train and eval separated?
  - yes, by policy and by existing integrity checks
- Is the weekend demo overfit to a tiny hand-picked set?
  - not if the curated `100-200` examples are treated as a demo-acceleration subset layered on top of the existing holdout-backed corpus
- Are we using synthetic trajectories recklessly?
  - no, because we keep synthetic trajectories as a supplement, not the sole data source

## Algorithm

### Target model

The active target for this report is:

- `google/gemma-4-26B-A4B-it`

This is the preferred demo target over `google/gemma-4-31B-it` because:

- it is smaller and therefore easier to download, relay, and reload
- it is explicitly a MoE-flavored checkpoint, making expert-specific tuning a first-class rather than awkward path
- it aligns better with a weekend-demo constraint where time-to-first-working-run matters more than chasing the absolute largest checkpoint

### Recommended algorithmic strategy

The recommended strategy is the user’s proposed order, with one practical refinement:

1. First-choice path: raw-paper router warmup plus curated expert refinement
2. Second-choice path: direct ESFT on selected experts
3. Fastest contingency path: router-only or router-plus-expert LoRA-MoE

For raw quantum papers specifically, the important method choice is:

- do **not** treat uncurated raw paper chunks as if they were already ideal instruction-response supervision for full-model SFT
- do use them as domain-adaptation fuel for:
  - router warmup
  - expert selection analysis
  - lightweight LoRA-MoE adaptation on router / gate-heavy paths
- then use the stricter curated QA / coding corpora for the narrower expert-refinement step

### Two-stage expert locking

This is the most defendable weekend-demo algorithm if the module names and runtime support cooperate:

- Stage 1:
  - freeze experts
  - tune router / gating components on raw paper-derived domain text so quantum data learns which experts to activate
- Stage 2:
  - inspect routing frequencies on the curated dataset
  - select the top-`K` experts
  - freeze the rest
  - fine-tune only the chosen experts at a higher learning rate

Why this is recommended:

- it reduces destructive interference across the whole MoE
- it gives us a concrete story for why the demo model improved
- it keeps the fine-tuned parameter budget small enough for a fast iteration

### Direct ESFT

If the runtime exposes expert modules cleanly, direct ESFT is the next most practical option:

- run a small analysis pass to see which experts are activated most on the quantum subset
- fine-tune only those experts and the minimum routing layers necessary to keep behavior stable

This is attractive because:

- it is closer to the model’s actual sparse computation pattern
- it often gives a better accuracy-to-updated-parameter ratio than uniform fine-tuning

### LoRA-MoE contingency

If expert-only parameter freezing turns out too brittle for the current weekend timeline, the lowest-risk contingency is:

- LoRA on router-related linear layers
- optionally LoRA on expert internal projections once the expert module names are verified

Suggested initial LoRA settings:

- `r=8`
- `lora_alpha=32`
- `BF16`
- no `QLoRA` for the demo path unless memory pressure becomes absolute

The stack now supports regex-based LoRA module targeting, which makes these weekend-demo variants realistic:

- router-only LoRA
- one-router-plus-selected-expert LoRA
- future manifest-driven ESFT once real expert names are inspected on the downloaded checkpoint

### What we are not doing

We are not claiming the following before evidence exists:

- that Anthropic’s `SGTM` release directly provides our trajectory controller
- that `31B` remains the best target under the weekend deadline
- that full-parameter MoE fine-tuning is necessary for this demo

## Compute

### Local compute

The local Mac remains the control plane:

- code editing
- local validation
- model download initiation
- S3 relay orchestration
- Huanxin job launch and monitoring

The critical local constraint is disk and transfer time. That is the operational reason to abandon `31B` and prefer `26B-A4B`.

### Huanxin compute

The actual training target remains `ai2` on Huanxin.

Current verified constraints:

- ai2 shell access works when the browser daemon is healthy
- direct public model downloads from ai2 can fail because of remote DNS reachability
- therefore the robust path is still:
  - local download
  - S3 relay
  - ai2 sync

### Precision and runtime choices

For the weekend demo:

- use `BF16`
- avoid `QLoRA/4-bit` unless there is a hard memory blocker
- prefer smaller parameter updates over more aggressive compression

### Capacity-aware fallbacks

The repo already has a real fallback lane:

- `OmniCoder-9B` continuation from the strongest verified adapter

This remains important because:

- it prevents idle compute when Gemma handoff or runtime work is blocked
- it gives leadership a live “progress continues” story even if the Gemma MoE line is still stabilizing

## R&D Architecture

### Control plane

The intended R&D architecture for the demo is:

1. local code and validation
2. local model acquisition
3. S3 relay
4. ai2 sync
5. ai2 training
6. result pullback and reporting

This architecture is already partially implemented in the repo via:

- `training/acquire_public_qwen_snapshot.py`
- `scripts/relay_model_snapshot_to_s3.sh`
- `scripts/ai2_sync_model_from_s3.sh`
- `scripts/run_autonomous_rd_cycle.py`

### Trajectory architecture

The autonomous loop should keep three explicit lanes:

- primary lane:
  - `Gemma 4 26B-A4B-it` MoE tuning
- blocked lane:
  - any Gemma runtime / transport blocker
- fallback lane:
  - `OmniCoder-9B` continuation on ai2

This matters because leadership will ask:

- “If Gemma stalls, are we dead in the water?”

The correct answer should be:

- no, because the fallback lane is already explicit in the controller

### Expert-tuning architecture

The repo should treat expert-specific tuning as a subsystem, not an ad hoc launch flag.

Minimum subsystem pieces:

- expert/router module inspection
- router-only tuning option
- expert-frequency analysis on the quantum subset
- selected-expert fine-tuning mode
- LoRA-MoE fallback when full expert updates are too risky

### Reporting architecture

Every iteration should produce:

- machine-readable state
- leadership-readable report
- command sheet
- blocker summary
- next-step recommendation

This is how we avoid “it probably worked” style ambiguity before the demo.

The repo now includes a concrete inspection entrypoint for this:

- `training/inspect_moe_target_modules.py --model-name models/gemma-4-26B-A4B-it`

This is meant to answer the exact pre-demo question:

- “What are the real router and expert layer names in the downloaded checkpoint, and which suffixes should LoRA / ESFT target?”

## Results Analysis

### What is already true

- the repo already has a working autonomous-cycle controller
- the fallback OmniCoder lane is implemented and launchable
- Gemma text-preprocessor and text-forward preflight work has advanced materially
- the old `31B` route proved the handoff pattern, but not the practicality of finishing in time for a demo
- on `2026-04-08`, the `26B-A4B` source audit succeeded through `https://hf-mirror.com` after the direct `huggingface.co` API path timed out from the local Mac
- the local `26B-A4B` snapshot is now materially in flight:
  - `config.json`
  - `processor_config.json`
  - `tokenizer.json`
  - `model.safetensors.index.json`
  - two live `.incomplete` shard downloads
- the indexed weight total for this checkpoint is about `48.1GB`
- the autonomous controller now records this as a real in-flight acquisition stage rather than a vague blocker
- the S3 relay has been launched in parallel so completed files can move upstream without waiting for the final shard to finish
- the local quality gate is currently green for this iteration:
  - `python3 evals/runner/run_eval.py` -> `26/26 passed`
- the strict holdout-integrity gate is also green for this iteration:
  - `python3 scripts/verify_holdout_dataset.py ... --min-eval-count 500 --require-task-disjoint --require-prompt-family-disjoint` -> `ok: true`
- the refreshed controller state now shows:
  - `current_stage: gemma_snapshot_acquire`
  - `observed_weight_progress_percent: 4.0%`
  - `fallback_ready: true`
- the training stack now supports regex-based LoRA module targeting, which is the minimum practical control needed for router-only or expert-specific weekend-demo experiments
- the training stack now also supports regex-based trainable-parameter filtering:
  - `--trainable-param-regex`
  - `--freeze-param-regex`
  - this makes router-only warmup, expert-only continuation, and bounded ESFT-style refinement materially easier to run without full-parameter updates
- the MoE inspection path now emits a full-name target manifest, not only suffix guesses:
  - router modules are recorded with exact names
  - expert modules are grouped by expert index
  - the autonomous controller now records a machine-readable `moe_expert_routing_prep` block so leadership can see the post-download expert-selection path before a remote run exists
- the paper warmup path is now backed by real local artifacts instead of a placeholder:
  - local paper corpus now includes:
    - `paper/quantum-coding-llm-rnd.tex`
    - `paper/novel_rl_algorithms.tex`
  - the router-warmup dataset was rebuilt from `paper/` and now yields:
    - `42` train examples
    - `5` valid examples
  - the leadership-ready command artifact now exists:
    - `artifacts/gemma4-26b-a4b-paper-router-command-sheet.txt`
- the GRPO path also had a real preflight bug fixed while this Gemma iteration was running, so the fallback RL lane is less fragile than before
- the local `26B-A4B` acquisition later advanced materially:
  - local footprint reached about `14G`
  - the live missing shard reached about `12G`
  - local verify still correctly fails because `model-00001-of-00002.safetensors` is not finished yet
- the Huanxin connection path also moved from vague “daemon issues” to a much more specific state:
  - ai2 shell execution through the preserved session was verified once end-to-end on the exact ai2 environment URL
  - the supervised LaunchAgent path is now installed
  - a one-time Safari-SSO browser-profile repair succeeded and synced the repaired profile back to the base browser copy
  - the remaining Huanxin work is now narrowly the supervised daemon bootstrap path, not generic login uncertainty

### Why abandoning 31B is justified

The decision to abandon the `31B` path is justified by concrete operational evidence:

- large local transfer cost
- repeated time spent on a target that is too expensive relative to the weekend deadline
- no leadership value in keeping a larger but slower target if a smaller MoE checkpoint can tell a stronger expert-tuning story

### Current main risks for the 26B path

- runtime support for Gemma 4 MoE in the exact local/ai2 stack
- correct identification of router/expert module names
- clean ai2 sync and post-sync verification
- the time needed to finish both weight shards and promote a verified snapshot onto ai2
- avoiding a “paper plan only” outcome without one real fine-tuning run

### Why ESFT / LoRA-MoE is still the right risk posture

For the weekend demo, leadership should care more about:

- a believable narrow improvement
- a small number of controllable updated parameters
- a clear explanation for what changed

than about:

- the biggest possible checkpoint
- the most aggressive full-model tuning story

That is why ESFT / route-lock / LoRA-MoE is the right risk posture here.

## Next R&D Plan

### Immediate

1. keep the existing ai2 `31B` snapshot in place because ai2 has enough space and deleting it is not needed for the demo path
2. keep the repo control plane default target on `google/gemma-4-26B-A4B-it`
3. finish the live local `26B-A4B` snapshot
4. continue the already-running S3 relay until the snapshot verifies cleanly
5. sync the verified snapshot into ai2
6. verify the ai2 copy before any Gemma-specific training claim

### After the model lands

1. inspect MoE module names on the real checkpoint
2. verify router and expert layer naming before any LoRA injection
3. record a router/expert target manifest with full module names, not only suffix guesses
4. run a router-only LoRA smoke using regex-based module targeting
5. if stable, collect routing-frequency evidence and launch the first bounded ESFT-style demo run

### Demo-readiness checklist

- checkpoint verified locally
- checkpoint verified on ai2
- module names inspected and recorded
- one successful training smoke
- one leadership-facing result summary
- one clear fallback story if Gemma MoE underperforms

### Leadership Q&A readiness

This report is meant to answer the typical leadership concerns directly:

- Why switch off 31B now?
  - because the weekend deadline makes smaller-MoE throughput more valuable than larger-checkpoint ambition
- Why MoE-specific tuning instead of generic SFT only?
  - because it aligns with the model’s structure and keeps the updated parameter budget smaller
- What if Gemma fails?
  - the OmniCoder fallback lane remains live
- What is the next irreversible step?
  - complete the local `26B-A4B` snapshot, verify it, and promote the verified copy through S3 into ai2
