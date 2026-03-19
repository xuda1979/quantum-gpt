# Seed Dataset Artifacts

This directory holds the first dataset-v0 corpus derived directly from the local eval tasks.

## Files

- `build_seed_dataset.py` — materializes the current seed JSONL file from `evals/tasks/**`
- `convert_to_chat.py` — converts `dataset-v0` JSONL into a simple chat-style SFT format
- `create_splits.py` — deterministically partitions dataset or chat JSONL into train/val/test files plus a manifest, with optional tiny-corpus balancing by `domain` or `task_type` and an `--auto-policy` mode that picks a default policy from corpus composition
- `audit_splits.py` — audits a split manifest for empty splits, duplicate ids, domain/task-type/category/difficulty skew, optional missing-coverage gaps, and ratio drift
- `grow_mock_corpus.py` — expands the tiny seed corpus into a larger deterministic mock corpus for split/audit stress tests
- `recommend_split_policy.py` — inspects corpus size/composition and suggests a default split policy plus `create_splits.py` flags
- `train.jsonl` — generated dataset-v0 examples
- `train-chat.jsonl` — generated chat-style SFT examples
- `splits/` — generated train/val/test JSONL files and split manifest

For repair/refactor items, the builder keeps the gold `response` separate from a deliberately imperfect `broken_candidate` or `original_file` artifact. That separation matters; otherwise the dataset would accidentally teach the model that the broken input is already correct.

## Why this exists

The eval harness already contains small, executable tasks spanning both quantum and software-engineering work.
Instead of inventing a separate data format in the abstract, this builder turns those existing tasks into a tiny but real supervised-data artifact.

That makes the project more coherent:

- eval curation and dataset curation share source artifacts
- example metadata stays aligned with task ids and categories
- future schema changes can be propagated by regenerating from source tasks

## Usage

From the workspace root:

```bash
python3 data/seed/build_seed_dataset.py
python3 data/seed/convert_to_chat.py
python3 data/seed/create_splits.py
python3 data/seed/create_splits.py --auto-policy
python3 data/seed/audit_splits.py
python3 data/seed/grow_mock_corpus.py
python3 data/seed/recommend_split_policy.py --emit-flags
# tiny-corpus balancing example:
python3 data/seed/create_splits.py --balance-key domain --min-per-balance-group 1
python3 data/seed/audit_splits.py --manifest data/seed/splits/manifest.json --warn-missing-coverage
# larger mock-corpus stress test:
python3 data/seed/grow_mock_corpus.py --copies-per-example 4
python3 data/seed/create_splits.py --input data/seed/mock-train-chat.jsonl --output-dir data/seed/mock-splits
python3 data/seed/audit_splits.py --manifest data/seed/mock-splits/manifest.json
```

The first command regenerates `train.jsonl` from the eval task source files and validates:

- required common fields exist
- `schema_version == "dataset-v0"`
- `domain` is `quantum` or `software`
- `instruction` and `response` are non-empty
- `artifacts` is a JSON object
- `example_id` values are unique within the output file

The second command converts `train.jsonl` into `train-chat.jsonl`, a lightweight chat-SFT format with:

- a fixed system prompt oriented toward careful code generation
- a user message containing the instruction plus inline artifacts
- metadata preserved for filtering by domain, category, task type, difficulty, framework, and source provenance

The third command deterministically partitions an input JSONL file (default: `train-chat.jsonl`) into `splits/train.jsonl`, `splits/val.jsonl`, and `splits/test.jsonl`, then writes `splits/manifest.json` containing:

- the input path and source schema
- the deterministic seed and requested ratios
- optional balancing settings (`balance_key`, `min_per_balance_group`)
- per-split counts, domain/task-type/category/difficulty summaries, and example id lists
- an explicit record of which ids landed in which split so collisions are easy to audit

By default, `create_splits.py` uses simple stable hash assignment by `example_id`. For tiny corpora, that can produce skewed holdouts. Optional balancing lets you spread examples more evenly within each `domain` or `task_type` group.

If you pass `--auto-policy`, the splitter consults the same recommendation logic described below and records the chosen policy in the manifest. Explicit `--balance-key` arguments still win over auto-selection, which is the right default: automation should suggest, not silently override.

If you do not want to decide that manually every time, `create_splits.py --auto-policy` runs the same lightweight recommendation logic as `recommend_split_policy.py` and applies the suggested balancing mode automatically. Explicit `--balance-key` / `--min-per-balance-group` flags still win conceptually, so the script rejects mixing them with `--auto-policy` to keep runs unambiguous.

`audit_splits.py` reads a generated `manifest.json` and reports:

- empty train/val/test splits
- duplicate example ids within or across splits
- domain, task-type, category, or difficulty concentration inside each split
- optional missing-coverage gaps where a split lacks a group value present elsewhere in the corpus
- drift between requested split ratios and actual realized split sizes

The audit defaults are intentionally simple heuristics rather than hard failures. At this stage the goal is visibility: the manifest should make skew obvious before the corpus is large enough for leakage or holdout quality problems to become subtle.

`grow_mock_corpus.py` exists for one narrow purpose: the real seed corpus is too small to tell whether the split and audit tooling behaves sensibly once counts rise above toy scale. The utility clones each source example into deterministic variants with new `example_id` values and provenance metadata (`source_example_id`, `mock_variant_index`, `mock_variant_tag`). That gives the repo a cheap stress-test corpus for split bookkeeping without pretending synthetic duplicates are real training data.

## Current scope

The generated file contains the six current seed eval tasks:

- Bell pair construction
- Measurement mapping bug repair
- Superdense coding encode/decode
- Off-by-one bug fix
- Parser regression tests
- Duplicate-logic refactor

This is intentionally tiny. The point is to prove the data path, not to pretend six examples are enough for training.

Because the corpus is tiny, split tradeoffs are unavoidable. Plain hash splitting can create domain-skewed validation/test sets. With `--balance-key domain --min-per-balance-group 1`, the current 6-example corpus produces a deterministic `2/2/2` split where each split contains one quantum and one software example.

That result is not a bug. It is the consequence of enforcing minimum domain coverage across three splits when only three examples exist per domain. In other words: if each split must contain at least one quantum and one software example, the entire corpus gets consumed evenly.

That tradeoff is acceptable at this stage. Right now the splitter's main job is split bookkeeping, leakage prevention, and explicit coverage control for tiny datasets. As the corpus grows, the same utility can preserve stable assignment while allowing more ratio-faithful splits.

## Mock scaling for split-policy checks

`grow_mock_corpus.py` exists to stress-test the split/audit pipeline before real data volume catches up. It clones each source example into deterministic numbered variants with fresh `example_id`s and provenance metadata, making it useful for tooling experiments but not for real training.

Example workflow:

```bash
python3 data/seed/grow_mock_corpus.py --copies-per-example 4
python3 data/seed/create_splits.py --input data/seed/mock-train-chat.jsonl --output-dir data/seed/mock-splits
python3 data/seed/audit_splits.py --manifest data/seed/mock-splits/manifest.json
python3 data/seed/create_splits.py --input data/seed/mock-train-chat.jsonl --output-dir data/seed/mock-balanced-domain --balance-key domain --min-per-balance-group 1
python3 data/seed/audit_splits.py --manifest data/seed/mock-balanced-domain/manifest.json
python3 data/seed/create_splits.py --input data/seed/mock-train-chat.jsonl --output-dir data/seed/mock-balanced-task-type --balance-key task_type --min-per-balance-group 1
python3 data/seed/audit_splits.py --manifest data/seed/mock-balanced-task-type/manifest.json
```

Current 24-example mock-corpus observation:

- plain hash split: best raw ratio fit after domain balancing is disabled, but the test split collapses to all `repair` tasks and domain skew remains visible
- domain-balanced split: preserves the nominal 16/4/4 ratio almost perfectly, but still leaves software-heavy holdouts because balancing only constrains domain placement, not category/task-type mix
- task-type-balanced split: keeps the 16/4/4 ratio and reduces the worst task-type collapse, but it still allows domain skew in small holdouts

My current take: once the corpus is moderately larger, task-type balancing is a better default than domain balancing for this project because software-engineering capability is a first-class goal and catastrophic holdout collapse by task family is more misleading than mild domain imbalance. Domain balancing still matters for tiny corpora and should remain an explicit option, not the only policy.

## Policy recommendation helper

`recommend_split_policy.py` is a thin helper layer over the observations above. It does not replace `create_splits.py`; it just inspects corpus size and group counts, then suggests a sane default policy:

- tiny corpora or corpora without enough examples per domain to cover train/val/test → recommend `--balance-key domain --min-per-balance-group 1`
- larger corpora where every task type can appear across all three splits → recommend `--balance-key task_type --min-per-balance-group 1`
- intermediate corpora with sparse task types → recommend plain hash splitting to avoid over-constraining the split

Example:

```bash
python3 data/seed/recommend_split_policy.py --input data/seed/train-chat.jsonl --emit-flags
python3 data/seed/recommend_split_policy.py --input data/seed/mock-train-chat.jsonl --emit-flags
```

Current behavior:

- on the 6-example seed corpus, the helper recommends domain balancing
- on the 24-example mock corpus, it recommends task-type balancing
- `create_splits.py --auto-policy` now applies those same recommendations directly and records the chosen policy plus rationale in `manifest.json`

Latest seed-corpus observation after the corpus grew to 8 examples:

- `create_splits.py --auto-policy` still recommends domain balancing because the corpus is below the tiny-corpus threshold
- the richer audit now reports domain/task-type/category/difficulty summaries plus optional missing-coverage warnings
- that audit exposed the important limitation of domain-only balancing: the current `4/2/2` split preserves quantum/software presence but still collapses task-type and category coverage in holdouts

That is useful signal, not failure. It means the split tooling is now measuring the project-relevant risk more honestly: preserving software-engineering capability requires protecting task-family coverage too, not just quantum/software top-level balance.

That matches the empirical split-policy comparison above, which is the point: the recommendation layer is only useful if it encodes observed behavior rather than hand-wavy preference.
