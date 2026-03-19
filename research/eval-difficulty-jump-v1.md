# Eval Difficulty Jump v1

## Why this note exists

The hosted baseline (`openai/gpt-5.4`) now passes the full 16-task local harness, including the two adversarial additions:

- `quantum_stabilizer_tableau_update_repair`
- `software_patch_application_conflict_resolver`

That result is useful because it cleanly rules out infrastructure as the bottleneck. The harness is stable, the run packaging works, scoring is durable, and the tasks are executable. The problem is now eval sharpness.

If the project keeps expanding the current task family with more single-file, fully self-contained repairs, we will mostly measure whether the model can solve short unit-test puzzles. That is not the same thing as measuring whether a future Qwen fine-tune preserves real software-engineering ability while improving on quantum work.

This note defines the next difficulty jump explicitly so future cycles can build against a stable target instead of drifting.

## Diagnosis from the 16-task result

The current tasks are strong enough to validate:

- basic code generation
- local bug repair
- short-horizon state updates
- symbolic quantum logic on small objects
- multi-constraint function behavior

They are not yet strong enough to separate a strong hosted model because they still share three forgiving properties:

1. **Everything important is visible in one file.**
   The model rarely has to preserve behavior across modules, call boundaries, or helper contracts.
2. **Naive rewrites are often acceptable.**
   If a model ignores the intended local-edit spirit and rewrites the whole function cleanly, tests usually still pass.
3. **Context windows stay shallow.**
   The model can reason about the whole task at once without tracking hidden coupling or deferred consequences.

So the next step should not be "more tasks" in the abstract. It should be a controlled move toward tasks where brute-force rewriting and isolated local reasoning stop being enough.

## Design rule for the next batch

Every new task in the next batch should satisfy **at least two** of these properties:

1. **Multi-file dependency** — correctness depends on preserving behavior across more than one module.
2. **Interface preservation pressure** — tests punish unnecessary rewrites that break signatures, field names, helper usage, or serialization shape.
3. **Hidden coupling** — one change must remain consistent with logic validated somewhere else.
4. **Patch-style editing** — the problem is framed as a constrained repair to existing code, not greenfield synthesis.
5. **Behavioral round-trip invariants** — encode/decode, serialize/deserialize, apply/replay, or summarize/reconstruct paths must stay mutually consistent.
6. **Quantum-software crossover** — quantum logic is embedded inside ordinary engineering concerns like manifests, adapters, normalization layers, or experiment records.

If a proposed task has only one of those properties, it is probably still too easy.

## Recommended next task family

The next batch should move from single-file candidate generation toward **mini-repository repair tasks**. Keep them tiny and CPU-cheap, but let each task contain 2-4 files with one real dependency edge.

That keeps the harness realistic without turning it into a heavyweight benchmark.

## First two concrete tasks to implement

### 1. Quantum: `quantum_tableau_patch_bundle_repair`

**Shape**

Create a tiny package with files like:

- `tableau_ops.py`
- `io_format.py`
- `tests.py`

The candidate must repair a bug in tableau/sign updates while preserving a serialized interchange format used by another helper.

**Core pressure**

- multi-step Clifford-style sign/axis reasoning
- round-trip serialization invariants
- interface preservation between update logic and I/O helpers
- patch-style repair instead of total rewrite

**Why this is a better jump**

The current stabilizer task proves the model can fix local symbolic logic. This next task asks whether it can do that **without** breaking the surrounding software contract. That is much closer to the project goal of preserving software-engineering ability while improving quantum skill.

**Suggested test constraints**

- H / S / SDG conjugation remains correct on signed Pauli literals
- unsupported operators still raise the documented error
- `serialize_tableau(parse_tableau(x))` is stable on canonical inputs
- repair must preserve exported function names and the expected serialized field order
- tests should import through the public API path, not only direct internals

### 2. Software: `software_multifile_patch_conflict_repair`

**Shape**

Create a tiny package with files like:

- `patch_engine.py`
- `reporting.py`
- `models.py`
- `tests.py`

The candidate repairs conflict handling in the patch engine, but the reporting layer expects a specific conflict schema and deterministic ordering.

**Core pressure**

- stateful patch application
- conflict classification and deduplication
- hidden coupling between engine output and reporting expectations
- punishment for casual full rewrites that change schema shape

**Why this is a better jump**

The current single-file patch resolver checks local invariants well, but it still lets the model solve the whole task as a self-contained function puzzle. A multi-file version makes engineering discipline visible: preserving contracts, not just computing the right internal state.

**Suggested test constraints**

- duplicate patch ids remain idempotent
- version progression remains monotonic
- conflict entries preserve stable ordering
- reporting helpers still render the exact documented summary shape
- inputs remain immutable
- exported dataclass or dict schema remains backward compatible

## What not to do next

Avoid these near-term traps:

- adding many more single-function algorithm tasks
- making tasks longer without adding real coupling
- hiding requirements only in prose while tests stay loose
- introducing external dependencies or heavyweight frameworks
- building a giant benchmark before the next difficulty jump is validated

Those moves will burn time without improving discriminative power.

## Success criterion for difficulty jump v1

This next batch is successful if **either** of these happens:

1. the hosted baseline records at least one meaningful failure on the new multi-file tasks, or
2. the hosted baseline still passes, but the failure surface becomes much more informative because the tasks now probe contract preservation rather than isolated puzzle solving.

A perfect score on a stronger task family is still informative. What matters is that the benchmark is now testing the right thing.

## Smallest next experiment

Implement exactly **one** task first, not both.

Recommended order:

1. `software_multifile_patch_conflict_repair`
2. `quantum_tableau_patch_bundle_repair`

Reason: the software task is easier to package into a tiny multi-file harness and will exercise the missing benchmark capability fastest: contract-preserving repair across modules.

## Decision

The next eval-expansion cycle should stop broad task-count growth and instead add the first **mini-repo multi-file repair task**, starting with `software_multifile_patch_conflict_repair`.
