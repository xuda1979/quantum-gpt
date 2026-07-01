# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Huanxin

- Codex-skill rule: always use the repo-local Codex Huanxin skill docs plus `scripts/` wrappers for Huanxin work. Do not bypass them with unmanaged browser actions, OpenClaw gateway state, manual paste/upload, or undocumented shell shortcuts.
- Training environment input rule: every Huanxin training launch or training-control action requires an explicit user-provided environment name in the current user message. Do not infer the training target from notes, daemons, defaults, old choices, or available wrappers.
- Robust Huanxin wrappers should be environment-agnostic and take `--env <env-name>`, for example `scripts/huanxin_env_shell.sh`, `scripts/huanxin_training_job.sh`, `scripts/launch_huanxin_agentic_grpo.sh`, `scripts/show_huanxin_agentic_grpo_status.sh`, and `scripts/watch_huanxin_checkpoints_to_s3.sh`.
- Default remote target for current training-style environments: `/root/work/quantum-gpt`; verify it exists in the user-provided environment before launch.
- Train-dev route: `https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=AI`
- User-required rule: from 2026-04-26 onward, do not use the old ai2 environment for training. All training work must target the Huanxin `AI` train-dev environment URL above.
- Login rule: before any Huanxin shell, sync, or training action, explicitly verify that the browser/session is logged in to the exact `AI` train-dev environment. If login/auth is stale, repair or login first; do not assume an old daemon or ai2 session is valid.
- Preferred remote target for `AI`: `/root/software/quantum-gpt` (`~/software/quantum-gpt` on the root user account)
- Historical ai2 remote target/source: `/root/root/work/quantum-gpt`; keep it because models/projects may need to be migrated from ai2 to `AI`.
- Available training environment: `AI`
- Deprecated training environments: `ai1`, `ai2`, and `ai3` for training. Only use old ai1/ai2/ai3 helpers for historical inspection, migration, or explicit debugging, not new training runs.
- Default training environment: `AI`
- Default next-round base model: `Qwen/Qwen3.6-27B`; use `models/Qwen3.6-27B` under `/root/software/quantum-gpt` for SFT, GRPO, PPO, DPO, eval, and adapter export unless the user explicitly chooses another base for a specific comparison.
- Migration source environment: `ai2` for old project/model artifacts only; do not launch new training there.
- Browser helpers live under `browser-automation/`
- This repo is meant to be driven directly by Codex. Do not depend on OpenClaw-managed skills or `~/.openclaw` state for normal Huanxin or S3 operations.
- If the live browser profile is locked, clone it first and automate against `/tmp/huanxin-profile-copy`
- Do not kill the Huanxin browser daemon or otherwise discard the authenticated browser session unless explicitly instructed. The human's manual webshell use overrides this: if `.huanxin_manual_mode` exists, local automation must be stopped or blocked even if that means terminating local daemon/browser-control processes.
- Manual use lock: when `.huanxin_manual_mode` exists, do not run any Huanxin browser automation, shell wrappers, Safari keepalive, profile repair, or browser probes. This is active when the human is using the Huanxin `AI` webshell manually and protects typed input from refresh/reconnect loss.
- Manual mode helper: `scripts/huanxin_manual_mode.sh --manual-on` (alias `--enable`), `--kill-local`, `--status`, `--manual-off` (alias `--disable`), `--disable-automation`, and `--enable-automation`.
- Automation is disabled by default. `--manual-off`/`--disable` only removes the manual lock and does not allow browser automation. Only `--enable-automation` creates `.huanxin_automation_enabled`; use it only when the human explicitly wants Codex/browser automation to control Huanxin again.
- If the `AI` webshell is slow, interrupted, or repeatedly refreshing, first run `scripts/huanxin_manual_mode.sh --manual-on` locally and verify `scripts/huanxin_manual_mode.sh --status` shows no matching processes before touching Huanxin again.

Common commands:

```bash
node browser-automation/huanxin_probe.js
./scripts/huanxin_safari_keepalive.sh
./scripts/huanxin_safari_keepalive.sh --refresh
./scripts/huanxin_safari_keepalive_loop.sh --once
./scripts/install_huanxin_safari_keepalive_agent.sh --status
./scripts/huanxin_status.sh
./scripts/huanxin_manual_mode.sh --status
./scripts/huanxin_manual_mode.sh --enable
./scripts/push_to_s3.sh --dry-run scripts skills
./scripts/ai_sync_from_s3.sh --dry-run
./scripts/ai_shell.sh "pwd && whoami"
./scripts/ai_job.sh ps
./scripts/ai_launch_quantum_sft.sh
./scripts/ai_push_results_to_s3.sh --dry-run outputs reports
node browser-automation/huanxin_inspect.js
node browser-automation/huanxin_open_env.js AI
node browser-automation/huanxin_mouse_paste.js '<url>' --click-text '<visible text>' --paste-file '<file>' --replace
```

Cloned-profile pattern:

```bash
rm -rf /tmp/huanxin-profile-copy
mkdir -p /tmp/huanxin-profile-copy
rsync -a --delete --exclude 'Singleton*' --exclude 'LOCK' --exclude 'lockfile' browser-automation/profile/ /tmp/huanxin-profile-copy/
HUANXIN_PROFILE_DIR=/tmp/huanxin-profile-copy node browser-automation/huanxin_probe.js
```

Rule: always pass local validation before browser-side paste into Huanxin.
Rule: always verify/login to the `AI` train-dev environment before Huanxin-side shell, sync, or training work.

Session rule:

- There are two distinct Huanxin sessions to track:
  1. the human Safari `#/train-dev` session
  2. the browser-automation profile used by Playwright/daemon shell control
- Do not conflate them. The Safari session can be healthy while the browser-automation profile is expired.
- The canonical no-new-page keepalive path is `bash scripts/huanxin_safari_keepalive.sh --refresh`.
- It only reuses the existing Safari Huanxin `#/train-dev` tab if present; it does not open a new page.
- Use it periodically to keep the already-open Safari session warm and to avoid repeating blind login/debug loops.
- The durable automatic path is the per-user LaunchAgent installed by `bash scripts/install_huanxin_safari_keepalive_agent.sh --install`.
- Check the LaunchAgent with `bash scripts/install_huanxin_safari_keepalive_agent.sh --status`.
- For one-command diagnosis, use `bash scripts/huanxin_status.sh`.
- Huanxin shell wrappers now default to daemon mode. This is deliberate: it keeps one warm browser session instead of repeatedly relaunching standalone automation.
- The daemon shell path now self-heals from the existing Safari `#/train-dev` session if Chromium hits Keycloak login during startup.
- The stable default is still on-demand daemon startup plus Safari-backed self-heal, but it must be pointed at the `AI` environment for training.
- Browser-profile repair now runs on an isolated Chromium copy and only syncs back to `browser-automation/profile/` after the exact `#/train-dev` app surface is confirmed, so failed repair attempts should no longer poison the stored base profile.
- There is an optional ai2 daemon LaunchAgent helper in `scripts/install_huanxin_ai2_daemon_agent.sh`, but it is historical/debug-only for this workspace now. Do not use it for new training.
- Background callback-driven profile repair from the Safari keepalive is disabled by default. Enable it only with `HUANXIN_BACKGROUND_PROFILE_REPAIR=1` if you are explicitly testing repair automation.
- Standalone shell fallback is disabled by default. Only set `HUANXIN_ALLOW_STANDALONE_FALLBACK=1` for explicit recovery/debugging.
- The manual loop remains available as a fallback: `bash scripts/huanxin_safari_keepalive_loop.sh`.
- If Apple Events are unavailable, `scripts/huanxin_safari_keepalive.sh` now prints structured JSON instead of failing silently.
- Safari helper failures from inside the sandbox are not authoritative. Re-check outside the sandbox before treating Safari itself as broken.
- 2026-05-13 manual-mode incident: a separate Codex thread repeatedly launched `scripts/huanxin_shell.sh AI` poll commands with standalone Playwright/Chrome, causing the human's `AI` webshell to refresh/reconnect and lose typed input. Keep `.huanxin_manual_mode` in place until manual Huanxin use is finished.
- Suspected remote load from that incident: a remote `run_qwen36_rag_ab_eval.py` job and Qwen36 RAG/no-RAG proxy stack may still be running on `AI`. Once the manual webshell is stable, the minimum remote cleanup is:
  `pkill -f 'run_qwen36_rag_ab_eval.py' || true`
  Optional resource cleanup, only if the human wants model serving stopped too:
  `pkill -f 'serve_qwen36_rag_codex_proxy.py|serve_qwen36_norag_codex_proxy.py|start_qwen36_rag_vllm_ascend_backend.sh|vllm' || true`

## INER S3

- Alternate Huanxin S3-compatible endpoint: `https://iner.aihuanxin.cn`
- Access key id: `OXF5ar4y`
- Secret key location: `skills/iner-s3-transfer/SKILL.md`; do not duplicate it into other notes or final answers.
- This is now the only active S3 relay for this workspace.
- Default bucket: `jtdlp-21b4208dde424e96b159362ef49c9c96`
- Default destination for this repo: `jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt`
- For the `AI` environment, INER is the intended relay for local <-> S3 <-> `AI` and for ai2 -> S3 -> `AI` migration.
- Default helpers: `scripts/upload_quantum_gpt_to_iner_s3.sh`, `scripts/push_to_s3.sh`, `scripts/pull_from_s3.sh`
- Broad upload rule: run `scripts/upload_quantum_gpt_to_iner_s3.sh --dry-run` first, then run `scripts/upload_quantum_gpt_to_iner_s3.sh` only after the dry-run file set is acceptable.
- If probing manually, use an isolated `RCLONE_CONFIG` under `/tmp` and include `--s3-no-check-bucket` for listing/copy checks when bucket probing fails.
- 2026-05-15 verification: bucket-specific operations against `iner:jtdlp-21b4208dde424e96b159362ef49c9c96/...` now work.
- Verified object write: `/Users/daxu/Downloads/rclone-current-linux-arm64.zip` uploaded to `iner:jtdlp-21b4208dde424e96b159362ef49c9c96/rclone-current-linux-arm64.zip`.
- Important nuance: `rclone lsd iner:` may still fail because the endpoint root serves HTML instead of S3 XML. Do not use bucket discovery as the health check; always target the bucket path explicitly.
