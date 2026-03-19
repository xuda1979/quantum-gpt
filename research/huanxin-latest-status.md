# Huanxin Latest Status

## Snapshot

- Remote target: `/root/root/work/quantum-gpt`
- Preferred Huanxin env for this project: `ai2`
- Current authenticated-surface status: **usable shell reachability confirmed**
- Exact blocker: artifact acquisition for the frozen project target `Qwen/Qwen3.5-1.5B-Instruct`, not auth or shell access
- Latest remote reachability check: `HUANXIN_PROFILE_COPY_NAME=probe HUANXIN_HEADLESS=1 node browser-automation/huanxin_shell_exec.js ai2 --command 'cd /root/root/work/quantum-gpt && pwd && ls -1 | head'`
- Latest remote reachability result: exit code `0`, live root shell prompt, and repo contents visible under `/root/root/work/quantum-gpt`
- Latest audited bootstrap bundle: `artifacts/huanxin-bootstrap/20260316T143522Z`
- Latest exact remote command sheet: `artifacts/huanxin-bootstrap/20260316T143522Z/REMOTE_BOOTSTRAP_COMMANDS.sh`

## Why this file exists

The remote path has moved through several different blockers over the last two days. This note exists so the next cycle does not waste time re-diagnosing old failures.

## Current truth

The local gate is green:

- `python3 evals/runner/run_eval.py` passes `19/19`
- `python3 -m py_compile training/verify_qwen_snapshot.py training/huanxin_cpu_smoke.py training/qwen_sft_peft.py training/remote_net_probe.py training/remote_json_head.py` passes

The remote path is also real enough for the next honest post-acquisition step:

- Huanxin auth is usable from the current browser context
- `ai2` is reachable
- `/root/root/work/quantum-gpt` exists and is browsable from the remote shell
- the blocker is no longer project-page visibility, env existence, or shell availability

What remains blocked is exact model artifact access:

- this local machine still has no verified local snapshot for `Qwen/Qwen3.5-1.5B-Instruct`
- no `HF_TOKEN` or `HUGGINGFACE_HUB_TOKEN` is currently set locally
- the project should not silently downgrade to Qwen 2.5 just because it is easier to fetch

## Exact next step

Do not spend the next cycle rechecking shell reachability unless something breaks.

There are now two honest next-step modes:

### Mode 1 — strict target path

If the project is still waiting for the exact intended checkpoint, the smallest
honest unblocker is:

1. obtain a real local snapshot directory for `Qwen/Qwen3.5-1.5B-Instruct`
2. verify it locally with:

```bash
python3 training/verify_qwen_snapshot.py /path/to/Qwen3.5-1.5B-Instruct
```

3. rerun the mandatory local project gate
4. transfer the verified snapshot into:

```text
/root/root/work/quantum-gpt/models/Qwen3.5-1.5B-Instruct
```

5. run remote tokenizer smoke against that explicit local remote path

Detailed handoff note:

- `research/qwen35-verified-snapshot-handoff.md`

### Mode 2 — approved public execution branch

If the execution-source decision becomes explicit before a real Qwen 3.5 source
appears, do not improvise the handoff. Use the prepared one-command local
acquisition path for the approved branch:

```bash
python3 training/acquire_public_qwen_snapshot.py --target qwen25 --dry-run
python3 training/acquire_public_qwen_snapshot.py --target qwen3-1.7b --dry-run
```

Then, for the approved branch only, rerun without `--dry-run` and optionally
render the matching remote command sheet in the same step:

```bash
python3 training/acquire_public_qwen_snapshot.py --target <approved-target> --render-remote-commands
```

That command now produces three durable local artifacts to carry into the next
Huanxin step:

- source audit JSON (`artifacts/model-source-audit-*.json`)
- a preflight manifest on dry-run, or a handoff manifest with verified local snapshot path + intended remote model dir after a real acquisition
- branch-specific remote command sheet under `artifacts/huanxin-bootstrap/20260316T143522Z/`

Current branch-specific outputs are conditional, not guaranteed to already exist. The helpers write them only when the corresponding preflight or acquisition command actually runs successfully:

- `artifacts/qwen25-local-snapshot-preflight.json`
- `artifacts/qwen25-local-snapshot-handoff.json`
- `artifacts/qwen3-1p7b-local-snapshot-preflight.json`
- `artifacts/qwen3-1p7b-local-snapshot-handoff.json`
- `artifacts/huanxin-bootstrap/20260316T143522Z/REMOTE_BOOTSTRAP_COMMANDS-Qwen2.5-1.5B-Instruct.sh`
- `artifacts/huanxin-bootstrap/20260316T143522Z/REMOTE_BOOTSTRAP_COMMANDS-Qwen3-1.7B.sh`

Treat these as intended artifact paths to check for, not as proof that the branch has already completed local preflight/acquisition.

Branch-specific handoff notes:

- `research/qwen25-public-fallback-handoff.md`
- `research/qwen3-public-alternative-handoff.md`

## Operator rule

Do not claim remote fine-tuning progress before tokenizer smoke succeeds from a verified local snapshot path inside `ai2`.

At this point, shell access is not the story anymore. Artifact acquisition is.