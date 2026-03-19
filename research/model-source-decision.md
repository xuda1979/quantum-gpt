# Model Source Decision

## Why this note exists

The project has been treating two different questions as if they were already the same:

1. what model family/size we want to center the R&D program on
2. what exact checkpoint source we can honestly fetch and use right now

Those are no longer interchangeable.

## Current evidence

### Research target preference

The project still prefers the smallest practical Qwen-family instruct checkpoint for quantum + software-engineering work.

### Publicly verified source check

A fresh public Hugging Face API search from this machine shows:

- no canonical result for `Qwen3.5-1.5B-Instruct`
- canonical public results for `Qwen/Qwen2.5-1.5B-Instruct`
- canonical public results for `Qwen/Qwen3-1.7B`

This matters because the previously frozen identifier `Qwen/Qwen3.5-1.5B-Instruct` is still not a verified public artifact source from this machine.

## Decision split

### Layer 1 — research intent

Keep the project intent unchanged:

- smallest practical Qwen-family instruct model
- preserve software-engineering capability as first-class
- keep the Huanxin fine-tuning path as the remote execution target

### Layer 2 — execution source

Do **not** keep assuming `Qwen/Qwen3.5-1.5B-Instruct` is a settled executable source.

There are now only three honest execution-source states:

1. **Exact Qwen 3.5 source provided**
   - someone provides a real local or authenticated source for the intended checkpoint
   - then the existing verifier + Huanxin handoff path applies

2. **Public-source fallback approved**
   - if the project allows proceeding with the closest verified public small Qwen instruct checkpoint, the concrete current candidate is:
   - `Qwen/Qwen2.5-1.5B-Instruct`

3. **Family-refresh alternative approved**
   - if the project prefers staying closer to current public Qwen generation naming rather than the older 2.5 checkpoint, the concrete public small candidate is:
   - `Qwen/Qwen3-1.7B`
   - this increases size a bit versus 1.5B, so it is not the cheapest CPU-first path

## Recommended default unless new artifacts appear

The most practical default is:

- keep **research intent** centered on the smallest practical Qwen-family coding target
- keep the **strict Qwen 3.5 checkpoint** path blocked until a real source exists
- treat `Qwen/Qwen2.5-1.5B-Instruct` as the current best **publicly verified fallback source** if an execution decision must be made without new credentials or artifacts

Why this is the least bad option:

- it preserves the 1.5B size band
- it is already publicly discoverable from this machine
- it avoids pretending an unavailable artifact is still operationally ready
- it is closer to the current CPU-first constraints than moving up to 1.7B

## What not to do

- do not silently relabel Qwen 2.5 work as Qwen 3.5 work
- do not claim fine-tuning readiness on an unverified checkpoint source
- do not keep retrying the same unauthenticated Qwen 3.5 fetch path without any new auth or local snapshot

## Smallest next unblocker

Choose one of these explicitly:

1. provide a real `Qwen/Qwen3.5-1.5B-Instruct` source
2. approve `Qwen/Qwen2.5-1.5B-Instruct` as the executable public fallback
3. approve `Qwen/Qwen3-1.7B` if family freshness matters more than size parity

## Source-audit artifact

Before any local snapshot acquisition or Huanxin handoff, record the chosen
execution source with a machine-local metadata audit:

```bash
python3 training/audit_model_source.py \
  --model-id Qwen/Qwen2.5-1.5B-Instruct \
  --expected-family-substring qwen \
  --out artifacts/model-source-audit-qwen25.json
```

or, for the alternate public family-refresh option:

```bash
python3 training/audit_model_source.py \
  --model-id Qwen/Qwen3-1.7B \
  --expected-family-substring qwen \
  --out artifacts/model-source-audit-qwen3-1p7b.json
```

This does not prove weight accessibility by itself, but it does stop the project
from making source claims with no attached artifact at all. The resulting JSON
is the right thing to cite in memory notes and handoff docs before any snapshot
verification or remote transfer step.

For the public branches, the default one-command local acquisition helpers are:

```bash
python3 training/acquire_public_qwen_snapshot.py --target qwen25
python3 training/acquire_public_qwen_snapshot.py --target qwen3-1.7b
```

If you want to validate the exact branch-specific audit + remote-handoff plan
without downloading multi-GB weights yet, use the new preflight mode:

```bash
python3 training/acquire_public_qwen_snapshot.py --target qwen25 --dry-run
python3 training/acquire_public_qwen_snapshot.py --target qwen3-1.7b --dry-run

# if the public metadata API is transiently slow from this machine:
python3 training/acquire_public_qwen_snapshot.py --target qwen25 --dry-run --hf-timeout-seconds 60
python3 training/acquire_public_qwen_snapshot.py --target qwen3-1.7b --dry-run --hf-timeout-seconds 60
```

These helpers chain source audit -> local snapshot download -> offline snapshot
verification, and they now also emit branch-specific handoff metadata. After a
successful local acquisition, they can also render a branch-specific Huanxin
command sheet via `--render-remote-commands`, so the next remote paste/run step
is tied to the verified remote local-path target rather than reconstructed by
hand. The dry run stops after the source audit, writes a durable preflight
manifest distinct from the real post-download handoff manifest, and if
`--render-remote-commands` is included it also renders the branch-specific
remote command sheet path into that preflight manifest. This still does not
claim local snapshot acquisition or any Huanxin transfer progress.

For the public family-refresh branch, the concrete command-level handoff note is:

- `research/qwen3-public-alternative-handoff.md`
