# Huanxin Browser Automation

Use this skill to run commands on the Huanxin cloud platform (https://aihuanxin.cn) from the local machine.

Treat this file as local reference documentation for Codex. No OpenClaw runtime, managed skill install, or gateway session is required for the flow below.

## Your Environment Assignment

**This agent may use both ai1 and ai2.** Default to ai2 unless ai1 is the better fit for capacity or parallel work.

Remote workdir on Huanxin: `/root/root/work/quantum-gpt`

## Default Operating Pattern

- Run everything from this repo root.
- Use `./scripts/huanxin_shell.sh <ai1|ai2> "<cmd>"` as the generic shell entrypoint. It uses standalone browser execution by default unless you opt into daemon mode.
- Convenience wrappers: `./scripts/ai1_shell.sh "<cmd>"` and `./scripts/ai2_shell.sh "<cmd>"`.
- If you explicitly want daemon mode, set `HUANXIN_USE_DAEMON=1` before calling the shell wrapper.
- Use `skills/s3-transfer/SKILL.md` for file and code movement. Prefer S3 relay for transferring files between local and ai1/ai2; use direct shell commands for control-plane work and small inspections.
- For any multi-step remote change, validate locally first, then use the S3 helper scripts for transfer, then use the shell wrapper for the control-plane command on the chosen environment.

## Persistent Browser Daemon

The browser daemon launches the browser ONCE and keeps it alive. All subsequent shell commands route through the daemon via HTTP, avoiding the overhead of launching/closing the browser for each command.

The shell wrappers do not require the daemon by default. Use daemon mode only when you explicitly opt in.

Do not stop the daemon unless the user explicitly tells you to. Preserving the authenticated session matters more than reclaiming a background process.

Manual control (if needed):

```bash
# Check if daemon is running
curl -s http://127.0.0.1:19002/health

# Start daemon manually
HUANXIN_PROFILE_COPY_NAME=quantum-rnd node browser-automation/huanxin_browser_daemon.js ai2

# Stop daemon
curl -s -X POST http://127.0.0.1:19002/stop

# Or kill by PID
kill $(cat /tmp/huanxin-daemon-ai2.pid)
```

Daemon ports: ai1 → 19001, ai2 → 19002.

## How to Run Commands on ai1 / ai2

**`huanxin_shell_exec.js` is your shell.** There is no SSH. There is no other way to run commands on Huanxin. This script opens the webshell in a headless browser and executes commands for you. Use it like this:

```bash
node browser-automation/huanxin_shell_exec.js ai1 --command "ls -la /root/root/work/quantum-gpt"
node browser-automation/huanxin_shell_exec.js ai2 --command "ls -la /root/root/work/quantum-gpt"
node browser-automation/huanxin_shell_exec.js ai2 --command "cd /root/root/work/quantum-gpt && python3 train.py"
node browser-automation/huanxin_shell_exec.js ai2 --command "nvidia-smi"
```

The command output is returned in the `output` field of the JSON response (marker-based extraction). The `before`/`after` fields contain raw terminal text for debugging.

**This IS your direct shell access to Huanxin. Just run the command above.**

When working inside this repo, prefer the wrapper:

```bash
./scripts/huanxin_shell.sh ai2 "cd /root/root/work/quantum-gpt && ls -la"
```

## Long-Running Jobs (Training, Data Generation)

Training and data generation take minutes to hours. **Do NOT run them in the foreground.** Use this pattern:

```bash
# 1. Start job with a durable local handle
./scripts/ai2_job.sh start train-qwen /tmp/train.log "python3 train.py --epochs 10"

# 2. Check status later by job id
./scripts/ai2_job.sh status train-qwen-20260324T000000Z

# 3. Tail more log lines when needed
./scripts/ai2_job.sh logs train-qwen-20260324T000000Z 120

# 4. List known jobs for this workspace
./scripts/ai2_job.sh list
```

**Key rules for long jobs:**
- Always redirect stdout+stderr to a log file: `> /tmp/something.log 2>&1`
- Always use `nohup ... &` to detach from the shell
- Prefer `./scripts/ai2_job.sh` over raw `nohup` because the plain shell wrapper only returns terminal snapshots, not a durable job handle
- Do NOT try to run training in the foreground — the tool timeout will kill it

## Prerequisites

- **Node.js** and **Playwright** are already installed in `browser-automation/node_modules/`.
- The persistent Chromium profile at `browser-automation/profile/` holds authenticated session cookies.
- No additional installation is needed. Just run the scripts with `node`.

## If Shell Exec Fails (Auth Expired)

Only if `huanxin_shell_exec.js` fails with an auth error, run these recovery steps:

```bash
# 1. Check auth state
node browser-automation/huanxin_probe.js

# 2. If login_required, tell the user to run the headed login helper
#    (requires manual human login — you cannot do this yourself)
node browser-automation/huanxin_login.js
```

## Available Scripts

| Script | Purpose |
|--------|---------|
| `huanxin_browser_daemon.js <env>` | **Start persistent browser daemon.** Keeps browser alive between commands. Auto-started by shell wrappers. |
| `huanxin_probe.js` | Check auth state. Outputs JSON with `state` field. |
| `huanxin_login.js` | Open headed browser for manual login. Saves session to profile. |
| `huanxin_inspect.js` | Inspect train-dev page for editor/terminal/shell controls. |
| `huanxin_open_env.js <env>` | Open a named dev environment (e.g. `ai2`). |
| `huanxin_shell_exec.js <env> --command "<cmd>"` | Execute a shell command. Routes to daemon if running, else standalone. |
| `huanxin_shell_sync.js` | Sync files to/from an environment shell. |
| `huanxin_dual_exec.js` | Execute commands on two environments in parallel. |
| `huanxin_mouse_paste.js` | Click a control by text and paste file content. |
| `huanxin_profile.js` | Profile directory management (used by other scripts). |

## Profile Handling

The persistent profile is at `browser-automation/profile/`. The browser daemon copies the profile once at startup and reuses it for all commands, avoiding lock contention.

If the daemon is not running and you must use standalone mode, the profile copy is handled automatically (via `HUANXIN_PROFILE_COPY_NAME`).

All scripts now default to **headless mode**. To run headed (for debugging), set `HUANXIN_HEADLESS=0`.

## Operating Pattern

**For everyday work, just use `huanxin_shell_exec.js` directly.** No need to probe, inspect, or open separately.

```bash
node browser-automation/huanxin_shell_exec.js ai2 --command "<your command here>"
```

The script handles navigation, environment selection, and shell interaction automatically.

Only run `huanxin_probe.js` if shell_exec fails (to check if auth expired).

## Recommended Control Flow

1. Validate local changes first.
2. Move files with the S3 transfer helpers instead of browser-shell copy/paste.
3. Use `./scripts/ai2_shell.sh` for remote commands, inspections, and launch steps.
4. If a transfer is large or risky, run the helper with `--dry-run` first.

`./scripts/ai2_sync_from_s3.sh` and `./scripts/ai2_push_results_to_s3.sh` are dual-mode helpers:

- when run locally on this Mac, they route through `./scripts/ai2_shell.sh`
- when run inside `/root/root/work/quantum-gpt` on ai2, they execute `rclone` directly

That means Codex can drive the full loop from the local repo and the same helper scripts still work after you land inside the remote workspace.

## State Values from Probe

| State | Meaning |
|-------|---------|
| `login_required` | Session expired. Run `huanxin_login.js` to re-authenticate. |
| `train_surface_or_project_page` | Authenticated, on the training page. |
| `authenticated_surface_ready` | Authenticated, editor/terminal detected. |
| `spa_loading` | Page loading, retry after a few seconds. |

## Safety Rules

- Use ai1 or ai2 intentionally; prefer ai2 by default and use ai1 when it materially improves parallelism or capacity.
- Do not paste unvalidated code into the remote environment.
- Do not use browser-shell copy/paste or flattened terminal reads for bulk file transfer when S3 relay is available.
- Do not delete remote content unless explicitly instructed.
- Do not assume page structure is stable — inspect first, then act.
- If no editor/terminal target is detectable, stop and record the blocker.

## Proof Standard

A successful step should produce at least one of:
- Captured stdout/JSON from the scripts
- Screenshots in `browser-automation/`
- A memory note describing what was reached and what was done
