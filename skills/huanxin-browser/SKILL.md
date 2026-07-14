---
name: huanxin-browser
description: Debug low-level Huanxin browser automation failures in this repo. Use only when wrapper-based Huanxin flows fail; otherwise use huanxin-s3-ops.
---

# Huanxin Browser Debugging

Use this file only for repo-specific, low-level debugging of the Huanxin browser control plane.

Do not use this as the default skill for everyday Huanxin work. The canonical entrypoint for normal local <-> S3 <-> Huanxin operations is `skills/huanxin-s3-ops/SKILL.md`.

## Use This Only When

- `scripts/huanxin_shell.sh AI` or the active environment wrapper from `TOOLS.md` is failing
- you need to inspect auth drift, daemon health, browser profile locks, or Safari repair flow
- you need to debug the raw `browser-automation/` scripts directly

## Default Stance

- Prefer the wrapper scripts first.
- Prefer `skills/huanxin-s3-ops/SKILL.md` for normal operations.
- Do not ask the human for the Huanxin URL if it already exists in `TOOLS.md` or the repo helpers.
- In this workspace, the user has authorized Codex to perform Huanxin auth/login and session repair through the Huanxin skill workflow when needed. Keep auth material ephemeral: never store passwords, SMS codes, cookies, bearer tokens, credential-bearing callback URLs, browser profiles, or private auth state in memory, docs, logs, final answers, or skill bodies.
- Always verify the active page is logged in to the exact train-dev environment URL from `TOOLS.md` before treating browser automation as ready.
- Do not kill the daemon or discard the authenticated browser profile unless explicitly instructed.
- Manual webshell protection overrides normal daemon preservation. If `.huanxin_manual_mode` exists or the human reports refresh/lost input, do not run probes, keepalive, repair, daemon, or shell helpers; use `scripts/huanxin_manual_mode.sh --manual-on` / `--kill-local` and local process inspection only.
- Browser automation is disabled by default. Only `scripts/huanxin_manual_mode.sh --enable-automation` should create `.huanxin_automation_enabled`, and only after the human explicitly wants Codex to control Huanxin again.

## Main Debug Entry Points

- `bash scripts/huanxin_status.sh`
- `node browser-automation/huanxin_probe.js`
- `node browser-automation/huanxin_shell_exec.js AI --command "<cmd>"`
- `bash scripts/repair_huanxin_browser_profile.sh`
- `bash scripts/huanxin_safari_keepalive.sh --refresh`

## Debug Focus Areas

### Auth State

- Probe only when the wrapper path is failing or auth state is unclear.
- If the wrapper works, treat that as the authoritative success signal even if a cold probe drifts.

### Daemon State

- The shell wrappers prefer daemon mode. That is the intended steady state.
- Check daemon readiness before attempting raw browser-script surgery.
- If daemon `/health` shows `busy=true` with stuck pending requests or stale `.processing.json` IPC files, inspect log/IPC state before enqueuing more shell requests.
- If shell-open evidence shows `getShellVisitUrl` failure or websocket target `.../kunlun/null`, stop treating it like a normal reconnect bug and classify it as a platform shell-endpoint blocker.

### Profile Locking

- If the main profile is locked, use a copied profile path when debugging standalone flows.
- Avoid poisoning the base profile during repair attempts.

### Safari Repair Path

- Use the repo's Safari-backed repair helper if the workspace relies on Safari as the canonical auth source.
- Prefer repair over inventing new login paths.

## Success Standard

A successful debugging step should produce one of:

- health JSON
- probe JSON
- wrapper output proving recovery
- a concrete diagnosis naming the exact failing helper, profile state, or auth step

## Error 170022 "获取shell终端信息失败" — Platform Shell Terminal Outage

**Root cause:** The Huanxin platform's `getShellVisitUrl` API
(`/kunlun/web/develop/v1/getShellVisitUrl`) returns `{code:170022}` when the
platform-side shell terminal service is down. The browser daemon connects
fine, but no terminal URL is returned, so the WebSocket falls back to
`wss://aihuanxin.cn/kunlun/null` (404).

**This is NOT a local issue — cannot be fixed from our side.** It is a
platform-side outage affecting all pods (ASI1/ASI2/ASI3).

**HOWEVER:** Before classifying it as a platform outage, **always try
starting the environment from the Huanxin UI first.** The environments
may simply be stopped/stale, and starting them from the UI resolves the
error. Do NOT assume platform outage without first attempting to start
the environments.

**Resolution (2026-07-14):** User started ASI1/ASI2/ASI3 from the Huanxin
UI, and the shell terminal service began working immediately. The error
was stale/stopped environments, not a platform outage.

## Environment Setup — Fresh Container Package Installation

When a Huanxin container is freshly restarted, the Python packages are
reset. The following packages must be reinstalled before training can run:

1. **peft** — from `/root/work/filestorage/py_deps/peft` (copy to site-packages)
   or `/root/work/quantum-gpt/tools/wheels/peft-0.14.0-py3-none-any.whl`
2. **accelerate** — from `/root/work/filestorage/py_deps/accelerate` (copy to site-packages)
   or `/root/work/quantum-gpt/tools/wheels/accelerate-1.4.0-py3-none-any.whl`
3. **transformers 5.6.0** — from
   `/root/work/software/quantum-gpt/vendor/transformers-560-aarch64-py311/transformers-5.6.0-py3-none-any.whl`
   (default container has 4.57.1 which lacks qwen3_5 module)
4. **huggingface_hub 1.22.0** — from
   `/root/work/software/quantum-gpt/vendor/transformers-560-aarch64-py311/huggingface_hub-1.22.0-py3-none-any.whl`
5. **NPU modeling patch** — `python3 scripts/patch_qwen3_5_npu_modeling.py`

**Automated setup:** `scripts/setup_asi_training_env.sh` does all of the
above in one shot. Run it on the NPU box after each container restart.

**After installing packages, save the environment image from the Huanxin UI**
so the setup persists across restarts.

## NPU Configuration — Single-NPU Boxes

**Each ASI environment has only 1 NPU** (ASI1: NPU ID 2, ASI2: NPU ID 3,
ASI3: NPU ID 7). Training scripts that hardcode `--nproc_per_node=4` will
fail with "Invalid device ID" / "open device N failed, runtime result =
107001".

**Required settings for single-NPU training:**
- `NPROC=1` (not 4)
- Do NOT set `ASCEND_RT_VISIBLE_DEVICES` (let torch_npu auto-detect; setting
  it to the NPU ID like "2" breaks detection because the local index is 0)
- `MAX_LENGTH=256` or less (27B model OOMs at 512 on a single 60GB NPU)
- `MASTER_PORT` must be unique across concurrent runs (use 29615+ range)

**Qwen3.6-27B memory:** ~56GB at max_length=256 with LoRA rank 16, gradient
checkpointing, batch size 1. Fits on a single 60GB NPU but barely.

## Shell Command Output Extraction

The `huanxin_env_shell.sh` wrapper returns a JSON payload with `after.rowText`
containing the terminal output. To extract just the command output:

```python
import json, re
# Parse the JSON, extract after.rowText, filter between __OC_*_START__ and __OC_*_END__ markers
```

Or use `/tmp/extract_huanxin_output.py` helper (created 2026-07-14).

## File Upload to NPU Boxes

The NPU boxes have no rclone and no direct internet (pip proxy times out).
To upload files from local:

1. **Base64 method:** Encode the file as base64, send via shell command,
   decode on the NPU box. Works for files up to ~10KB (base64 ~13KB).
   ```bash
   B64=$(base64 -i local_file.sh | tr -d '\n')
   bash scripts/huanxin_env_shell.sh --env ASI1 "echo -n '$B64' | base64 -d > /remote/path/file.sh"
   ```
2. **S3 relay:** Upload to S3 locally (rclone), then download on the NPU box.
   But the NPU box needs rclone installed and S3 credentials configured.
