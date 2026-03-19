# Public Model Source Check

## Purpose

Record the current public-internet evidence about the smallest practical Qwen checkpoint source, so the project does not keep targeting an unverified model identifier.

## Verified public checks

### Hugging Face public model API

Public search for `Qwen3.5-1.5B-Instruct` returned no canonical model results.

Public search for `Qwen2.5-1.5B-Instruct` returned a canonical Qwen model result:

- `Qwen/Qwen2.5-1.5B-Instruct`
- public page: <https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct>

### Direct tokenizer-config probes

- `Qwen/Qwen3.5-1.5B-Instruct` tokenizer-config path was not a reliable public retrieval target from this machine
- `Qwen/Qwen2.5-1.5B-Instruct` tokenizer-config path returned successfully

## Operational implication

The previously used identifier `Qwen/Qwen3.5-1.5B-Instruct` is not currently verified as a public canonical source.

A fresh public search from this machine also shows a canonical small Qwen 3 result in a nearby size band:

- `Qwen/Qwen3-1.7B`

That means the project should distinguish between two different things:

1. **research intention**
   - stay centered on the smallest practical Qwen family target for quantum + software engineering work

2. **publicly verified artifact source**
   - the smallest currently verified public source in this size class is `Qwen/Qwen2.5-1.5B-Instruct`
   - the currently verified public Qwen 3 family alternative is `Qwen/Qwen3-1.7B`

The project therefore has a real execution fork now, not a single implied public path.

## Decision pressure created by this check

There are now three honest paths:

### Path A — strict Qwen 3.5 requirement

If the project must remain specifically Qwen 3.5, then a non-public or otherwise separately verified source for that exact checkpoint is required before any local download / Huanxin training work can continue honestly.

### Path B — smallest practical public Qwen checkpoint

If the project can accept the smallest practical **publicly verified** Qwen checkpoint in this size band, then `Qwen/Qwen2.5-1.5B-Instruct` is the concrete next artifact source.

### Path C — public Qwen 3 family checkpoint

If the project wants to stay closer to the newer public Qwen generation naming and can tolerate a slightly larger checkpoint, then `Qwen/Qwen3-1.7B` is also a concrete public source.

## What this note does not do

- it does not silently change the project target on its own
- it does not claim training progress
- it does not claim that Qwen 2.5 is philosophically preferable; only that it is the currently verified public source

## Smallest next unblocker

Make the model-source decision explicit:

- either provide a real Qwen 3.5 source
- or proceed with `Qwen/Qwen2.5-1.5B-Instruct` as the smallest practical public checkpoint
- or proceed with `Qwen/Qwen3-1.7B` if staying in the public Qwen 3 family matters more than strict 1.5B size parity

If the choice is one of the public branches, the next command-level seam is already prepared:

- `python3 training/acquire_public_qwen_snapshot.py --target qwen25`
- `python3 training/acquire_public_qwen_snapshot.py --target qwen3-1.7b`

Use `--dry-run` first if you only want a no-download audit + handoff preflight.
