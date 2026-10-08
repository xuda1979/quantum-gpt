---
name: huanxin-s3-ops
description: Operate Huanxin train-dev environments with login checks, S3 relay sync, remote shell commands, migration, and training launch from this repo.
---

# Huanxin + S3 Ops

Use this skill when a workspace needs repeatable Huanxin login/session handling, S3 relay operations, project/model transfer, or remote training from a local repo.

It works best when the workspace contains repo-local helpers under `scripts/`, `browser-automation/`, and `TOOLS.md`. If a helper is missing, create the smallest project-local wrapper that follows this skill's contract rather than baking project-specific values into the skill.

This skill is meant to be shareable. Keep environment-specific values out of the skill body:

- canonical Huanxin URL
- S3 bucket or prefix
- S3 endpoint and credentials
- remote roots
- preferred env, such as `AI`
- source envs used only for migration, such as `ai2`
- browser profile paths
- daemon ports

Put those values in `TOOLS.md` or the repo-local helper scripts. Read [references/portability.md](references/portability.md) when adapting this skill to another workspace.

## Sharing This Skill

- Share the `skills/huanxin-s3-ops/` folder.
- The receiving workspace must define its real Huanxin URL, S3 root, remote paths, env defaults, and wrapper script names in `TOOLS.md` or repo-local helper scripts.
- Do not bake personal auth state, cookies, browser profiles, or private bucket details into this skill.
- Store secrets in project-local secret files or environment variables only when the human explicitly asks for that. Do not put secrets into final answers.

## Core Rules

- Read `TOOLS.md` first for the workspace-specific Huanxin URL, env naming, remote roots, and S3 root.
- When using this skill under `lean-software-engineering`, do not self-talk. Speak only for an important milestone, verified launch/result, exact blocker, or user decision; otherwise keep working silently.
- Use this Codex skill and the repo-local wrappers as the control contract for Huanxin work. Do not route normal Huanxin work through OpenClaw gateway state, unmanaged browser pokes, ad hoc paste/upload flows, or undocumented shell shortcuts.
- In this workspace, the user has authorized Codex to perform Huanxin auth/login and session repair through this skill workflow when needed for Huanxin work. This does not authorize storing secrets: never write passwords, SMS codes, cookies, bearer tokens, credential-bearing callback URLs, browser profiles, or private auth state into memory, docs, logs, final answers, or skill bodies.
- For every training launch or training-control action, ask the user to input the Huanxin training environment name unless they already provided it in the current user message. Do not infer it from `TOOLS.md`, old memory, current daemons, available wrappers, prior runs, repo defaults, or filename conventions.
- Once the human names a specific Huanxin environment for the current training action, use that exact environment only for that action. Record it in session memory with the date and command context, not as a timeless default.
- Treat S3 as the data plane and Huanxin as the execution plane.
- Always verify an authenticated login to the exact train-dev environment URL from `TOOLS.md` before shell, sync, or training work.
- If login/auth is stale, use the repo's login, keepalive, or repair flow first. Do not reuse an old daemon/session just because a wrapper exists.
- When a cold probe and a wrapper/repair path disagree, prefer the exact wrapper/repair result that actually reaches the train-dev surface; only treat auth as blocking when the real wrapper path also fails.
- For file movement, prefer the repo's sync helpers over manual `rclone` or browser paste.
- Validate locally before any remote mutation.
- Use `--dry-run` first for large or risky transfers.
- Do not kill the browser daemon, discard the authenticated profile, or delete remote content unless explicitly instructed.
- Manual webshell protection overrides normal Huanxin control-plane work. If `.huanxin_manual_mode` exists, or the human reports Huanxin refresh/lost input, do not run login probes, keepalive, repair, shell wrappers, or browser automation. Use local process inspection and `scripts/huanxin_manual_mode.sh --manual-on` / `--kill-local` only.
- Huanxin browser automation is disabled by default. Only `scripts/huanxin_manual_mode.sh --enable-automation` should create `.huanxin_automation_enabled`, and only after the human explicitly asks Codex to control Huanxin again.
- Do not use deprecated environments for new training, but preserve them as source environments when `TOOLS.md` says old projects or models must be migrated.
- For broad project/model transfer, prove the S3 API works with a tiny probe before starting the large copy.
- If daemon health shows `booting`, `busy=true`, or stuck pending IPC requests, inspect health/log/IPC evidence before queuing more shell requests.
- Keep the connection state precise. Distinguish `train-dev opened/authenticated`, `daemon terminal endpoint ready`, and `remote command channel verified`. Do not report "connected" unless a wrapper command returns fresh output with its run marker.
- If the daemon shell open fails because the platform returns no terminal URL, such as `getShellVisitUrl` failure or `wss://.../kunlun/null`, classify the daemon endpoint as degraded. Then use the project wrapper's documented fallback only if it records fresh command output; if that fallback succeeds, report "command channel connected via fallback" plus the daemon endpoint failure.
- Do not use direct backend RBAC-protected task-list or task-detail fetches as a status path when the user has said "don't use RBAC". Use the UI task list, the submit wrapper artifact, or an explicit browser-visible task detail path instead.
- Never use RBAC-protected backend paths for launch, status, or recovery when the human has said not to use RBAC. Treat `RBAC: access denied` as a hard stop for that route and switch immediately to a UI-visible path, wrapper artifact, or direct non-RBAC submission mechanism.
- Do not launch training unless checkpointing/resume behavior and live monitoring/eval signals are verified in the launcher or trainer path.

## Default Workflow

1. Inspect local notes and helper scripts:
   - `TOOLS.md`
   - `scripts/*huanxin*`
   - `scripts/*s3*`
   - `browser-automation/*`
2. Check Huanxin control-plane health:
   - `bash scripts/huanxin_status.sh`
   - auth probe or environment-open helper before the first remote action
   - if the target env is stopped, use the open/start helper to bring it up before shell or training work
   - repair/login if the current page is not the exact train-dev environment from `TOOLS.md`
3. Run remote commands through the shell wrapper:
   - `scripts/huanxin_shell.sh <env-name> "<cmd>"`
   - Require fresh marker evidence in the wrapper output before treating the command channel as connected.
   - If the wrapper writes a local connection-status artifact, treat it as supporting evidence only.
4. Check S3 relay health:
   - generate or locate the project-local rclone config without printing secrets
   - run a small list/probe command
   - for a new endpoint, upload only a tiny disposable probe file first
5. Move files through S3:
   - local -> S3
   - S3 -> Huanxin
   - Huanxin -> S3
   - S3 -> local
   - old Huanxin env -> S3 -> active Huanxin env
6. Verify the result with concrete command output, logs, remote listings, file counts, or fetched artifacts.

If the path is failing or ambiguous, branch using [references/scenario-matrix.md](references/scenario-matrix.md) instead of guessing.

## Preferred Entry Points

Use the workspace wrappers before lower-level tools:

- Generic shell: `scripts/huanxin_shell.sh <env-name> "<cmd>"`
- Environment-agnostic Codex wrappers when present, such as `scripts/huanxin_env_shell.sh --env <env-name>`, `scripts/huanxin_training_job.sh --env <env-name>`, and `scripts/launch_huanxin_agentic_grpo.sh --env <env-name>`
- Env shortcuts may exist for historical compatibility, but new robust docs and launch paths should not encode changing environment names into filenames.
- Local -> S3: `scripts/push_to_s3.sh`
- S3 -> local: `scripts/pull_from_s3.sh`
- S3 -> Huanxin: use the env-specific sync helper that matches `TOOLS.md`
- Huanxin -> S3: use the env-specific push-results helper that matches `TOOLS.md`
- Huanxin env -> Huanxin env migration: use a project-local migration helper if present; otherwise compose source-env push-results and target-env sync helpers
- Status and repair helpers when present: `scripts/huanxin_status.sh`, `scripts/repair_huanxin_browser_profile.sh`
- Open/start helpers when present: `browser-automation/huanxin_open_env.js`

Only drop to raw `node browser-automation/huanxin_shell_exec.js ...` or raw `rclone` when the wrappers are missing or clearly insufficient.

The shell wrapper should write a small local connection-status artifact after a successful remote command, if the project provides that feature. Status dashboards and later agents should read that artifact as evidence of command-channel health, while still preserving daemon endpoint failures as degraded infrastructure signals.

## ASI2 Lessons From 2026-06-09

- If Huanxin training-task submission fails with `code=151009` / `项目gpu空间配额不足`, do not keep retrying the task-submit route. Use the already-running dev environment shell if the target environment has allocated cards.
- For ASI2, the working command channel was:
  `HUANXIN_USE_DAEMON=0 HUANXIN_ALLOW_STANDALONE_FALLBACK=1 bash scripts/huanxin_env_shell.sh --env ASI2 "<cmd>"`
- Treat direct browser `fetch('/kunlun/web/develop/v1/detail?id=<env-id>')` from ad hoc terminal helpers as unreliable for ASI2; it returned `403 RBAC: access denied` even while the UI shell wrapper could execute commands.
- If the daemon or direct terminal endpoint is stale, bypass it with `HUANXIN_USE_DAEMON=0` before spending time repairing daemon state.
- Avoid large single remote commands through the shell wrapper; they can hit local argv limits or stale-output detection. For payloads larger than a short command, send a small base64 shell script or split the payload into chunks.
- INER S3 can upload from local successfully while ASI2 remote `rclone copy` from the same object may fail on `HeadObject` with `Forbidden`. If only a small dataset is missing, chunked shell injection is faster than debugging remote S3 permissions.
- Confirm ASI2 model paths before launching. On this run `/root/work/filestorage/Qwen3.6-35B-A3B` was absent, while `/root/work/filestorage/Qwen3.6-35B-A3B-W8A8` existed.
- Before declaring training started, verify the remote PID, log marker such as `__ASI2_DIRECT_BEFORE_TORCHRUN__`, and `npu-smi` process table. A `nohup` PID alone is not enough.

## ASI1 Lessons From 2026-06-14

- ASI1 has a dedicated 8-NPU environment under user control. Do not treat the submit drawer text `当前项目空间加速卡剩余/总量` or visible `超出项目空间配额` validation text as authoritative for ASI1 dev-environment capacity.
- For ASI1 task-submit helpers, use the project wrapper's explicit bypass such as `--ignore-project-quota-text` / `HUANXIN_IGNORE_PROJECT_QUOTA_TEXT=1` when the user has confirmed ASI1 capacity. Continue to honor hard API create failures, missing task IDs, or task-list absence as real blockers.
- If the human says "don't use RBAC", do not fall back to `fetch('/kunlun/web/task/v1/list')` or similar RBAC-guarded backend probes for task status. Stay on the visible UI path, submit artifact, or local log/marker path.
- For all-NPU ASI1 Qwen3.6-35B work, keep the launcher explicit: request 8 accelerator cards, set all 8 visible devices, and verify the rendered command contains `torchrun --nproc_per_node=8` before submission.
- Huanxin train-dev environments must keep doing real work or they may be terminated/reclaimed, and once terminated they can be hard to restart. When the user has assigned ASI1/AI capacity, keep a meaningful remote job, sync, monitor, eval, or lightweight verified activity running; do not leave the environment idle after setup.

## ASI1 Lessons From 2026-06-15

- The ASI1 `AI`/`ASI1` training lane is now using the dedicated resource group `研究院未来院专属资源组` with `个人资源组` semantics for launch routing. Do not let the generic public-group quota text block this lane.
- For the current verified-10k Qwen3.6-35B launch, use 5 accelerator cards and 5 visible devices (`0,1,2,3,4`) when the human has explicitly asked to use the available 5 NPUs.
- For this launch path, the remote working root is `/workspace`; the repo tree may need to be materialized there before launch.
- When the remote shell is alive but `/workspace` is empty, prefer a task submission that embeds the required code/data/runtime over relying on remote `rclone` pulls that can hit `Forbidden` on the INER relay.

## ASI1 Lessons From 2026-06-16

- The week-long delay on the verified-10k Qwen3.6-35B launch came from three avoidable assumptions: treating the empty ASI1 shell as usable when the terminal endpoint was actually degraded, chasing the wrong S3 object/root (`software/quantum-gpt/...` instead of the bucket root package), and repeatedly retrying a brittle UI selector path for the resource group instead of switching to the task submission route faster.
- The launcher must default to the exact verified 10k split, the correct `Qwen3.6-35B-A3B-W8A8` base path, and a tolerant resource-group picker that accepts the current page shape.
- When a submission path fails twice for the same page element or remote root, stop micro-fixing that layer and switch to the smallest alternate launch path immediately.

## Choosing The Training Environment

- Always ask the user for the training environment name before launching or controlling a training run, unless the current user message already contains the environment name.
- If `TOOLS.md` marks old environments as deprecated, do not use them for new training.
- Old environments may still be valid sources for migration. In that case, read from them, push the requested projects/models to S3, then restore into the active environment.
- Do not assume environment names share the same remote root or login route. Read the helper script defaults and `TOOLS.md`.
- In this workspace, prefer the currently active `AI` lane for new training unless the user explicitly requests a different env.
- If the chosen environment is not running, start it through the repo's open/start helper before shell or training work; do not ask the human to do the startup step manually.

## Required Checks Before Training

Before launching training, record concrete evidence for all of:

- local validation passed for the changed code or dataset
- active Huanxin environment login/open is verified and the environment is started if needed
- remote command channel is verified by a fresh wrapper command, unless the launch route is explicitly a no-shell training-task route
- active remote project root exists
- required code, datasets, and model directories exist in that remote root
- remote dependency probe is acceptable for the planned command
- if the plan involves S3 movement, the relay must first pass a tiny probe upload/list test

If any check fails, stop and document the exact failed command/output instead of launching a partial run.

## When To Load References

- Read [references/workflows.md](references/workflows.md) for concrete command recipes.
- Read [references/scenario-matrix.md](references/scenario-matrix.md) when auth, daemon, shell-open, S3, or training-launch state is ambiguous or failing.
- Read [references/keepalive.md](references/keepalive.md) when the user asks to keep Huanxin warm, install a keepalive loop/agent, or debug auth drift over time.
- Read [references/portability.md](references/portability.md) when packaging or adapting the skill for another repo.

## Success Standard

A successful step should leave at least one concrete artifact:

- shell JSON output
- sync log tail
- remote file listing
- fetched result file
- updated local note describing the exact state reached
