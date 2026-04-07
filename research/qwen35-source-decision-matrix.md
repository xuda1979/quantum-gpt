# Qwen 3.5 Source Decision and Fallback Execution Matrix

## Why this note exists

We now have two distinct facts in the workspace:

- the project target remains the smallest practical **Qwen 3.5** path
- the exact model id `Qwen/Qwen3.5-1.5B-Instruct` currently does **not** resolve anonymously from this machine

That means the next step should not be rediscovered every cycle. This note turns
that into a small execution matrix so the agent can move quickly without
misstating source availability.

## Current observed source states

### A. Exact target: `Qwen/Qwen3.5-1.5B-Instruct`

Observed local metadata result:

- `training/audit_model_source.py --model-id Qwen/Qwen3.5-1.5B-Instruct ...`
- result: **HTTP 401 Unauthorized**

Operational meaning:

- the exact target is **not anonymously fetchable** from this machine right now
- this is consistent with a gated/private/auth-required source state
- this is **not** proof that the model does not exist
- this is **not** enough to start remote training from HF on ai2

What would unblock this branch:

1. a valid authenticated local Hugging Face session/token that can access the target, or
2. an already-provided local snapshot directory for the exact target, or
3. an explicit project decision to use a public fallback for execution continuity

### B. Public fallback: `Qwen/Qwen2.5-1.5B-Instruct`

Observed state:

- local source audit resolves publicly
- acquisition helper already supports it
- verification helper already supports it
- remote bootstrap command rendering already supports it

Operational meaning:

- this is the **fastest executable branch** if the project chooses continuity over waiting
- it must still be described as a fallback, never as Qwen 3.5

### C. Public alternative: `Qwen/Qwen3-1.7B`

Observed state:

- local source audit resolves publicly
- acquisition helper already supports it
- verification helper already supports it
- remote bootstrap command rendering already supports it

Operational meaning:

- this is a second executable branch if Qwen-family recency matters more than exact size parity
- it is still **not** the frozen Qwen 3.5 target

## Decision matrix

Use the first row whose condition is true.

| Condition | Action | Honest status label |
| --- | --- | --- |
| Exact Qwen 3.5 snapshot is accessible locally with auth or provided as files | Verify it locally, then transfer and run remote smoke | exact-target path |
| Exact Qwen 3.5 remains inaccessible, but fallback execution is explicitly approved | Acquire verified local public fallback snapshot and transfer it | approved fallback path |
| Exact Qwen 3.5 inaccessible and fallback not yet approved | Do not claim model acquisition; record blocker and smallest unblocker | source-blocked |

## Minimal exact-target path once access exists

If the exact target becomes accessible, the next actions should be:

1. run local eval gate
2. download or receive the local snapshot
3. run `training/verify_qwen_snapshot.py <path> --expected-substring Qwen3.5-1.5B-Instruct`
4. transfer only the verified snapshot plus validated training files to ai2
5. run `training/huanxin_cpu_smoke.py --model-name <remote local path>`
6. only then attempt PEFT startup smoke

## Minimal fallback path once approved

If fallback execution is explicitly chosen, do exactly one of:

- `python3 training/acquire_public_qwen_snapshot.py --target qwen25 --render-remote-commands`
- `python3 training/acquire_public_qwen_snapshot.py --target qwen3-1.7b --render-remote-commands`

Then:

1. use the emitted handoff manifest
2. transfer the verified local snapshot to ai2
3. run remote tokenizer smoke against the transferred local path
4. only after that, run minimal PEFT startup smoke

## Anti-confusion rules

- 401 on the exact Qwen 3.5 source means **auth/source blocker**, not code blocker
- public fallback readiness means **execution continuity exists**, not that the project target changed
- remote progress only counts after smoke succeeds against a transferred local model path
- if no new access decision or artifact appears, the correct heartbeat response is to log the blocker and say `HEARTBEAT_OK`
