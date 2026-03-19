# Huanxin Browser Automation

Use this skill to run commands on the Huanxin cloud platform (https://aihuanxin.cn) from the local machine.

## Your Environment Assignment

**This agent uses ai2.** Do not use ai1 (reserved for the ALPHAQUBIT agent).

Remote workdir on ai2: `/root/root/work/quantum-gpt`

## Default Operating Pattern

- Use `scripts/ai2_shell.sh "<cmd>"` as the default shell entrypoint. It enables copy-profile mode automatically and avoids profile-lock churn.
- Use `skills/s3-transfer/SKILL.md` for file and code movement. Prefer S3 relay for transferring files between local and ai2; use direct shell commands for control-plane work and small inspections.
- For any multi-step remote change, validate locally first, then use the S3 helper scripts for transfer, then use `scripts/ai2_shell.sh` for the control-plane command on ai2.

## How to Run Commands on ai2

**`huanxin_shell_exec.js` is your shell.** There is no SSH. There is no other way to run commands on ai2. This script opens the webshell in a headless browser and executes commands for you. Use it like this:

```bash
node browser-automation/huanxin_shell_exec.js ai2 --command "ls -la /root/root/work/quantum-gpt"
node browser-automation/huanxin_shell_exec.js ai2 --command "cd /root/root/work/quantum-gpt && python3 train.py"
node browser-automation/huanxin_shell_exec.js ai2 --command "nvidia-smi"
```

The script outputs JSON with `{ ok, before, after }` showing terminal content before and after your command. A screenshot is saved to `browser-automation/huanxin-shell-ai2.png`.

**This IS your direct shell access to ai2. Just run the command above.**

When working inside this repo, prefer the wrapper:

```bash
scripts/ai2_shell.sh "cd /root/root/work/quantum-gpt && ls -la"
```

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
| `huanxin_probe.js` | Check auth state. Outputs JSON with `state` field. |
| `huanxin_login.js` | Open headed browser for manual login. Saves session to profile. |
| `huanxin_inspect.js` | Inspect train-dev page for editor/terminal/shell controls. |
| `huanxin_open_env.js <env>` | Open a named dev environment (e.g. `ai2`). |
| `huanxin_shell_exec.js <env> --command "<cmd>"` | Execute a shell command in an environment's webshell. |
| `huanxin_shell_sync.js` | Sync files to/from an environment shell. |
| `huanxin_dual_exec.js` | Execute commands on two environments in parallel. |
| `huanxin_mouse_paste.js` | Click a control by text and paste file content. |
| `huanxin_profile.js` | Profile directory management (used by other scripts). |

## Profile Handling

The persistent profile is at `browser-automation/profile/`. If it's locked by another browser instance, clone it:

```bash
HUANXIN_PROFILE_COPY_NAME=quantum-rnd node browser-automation/huanxin_probe.js
```

Or manually:

```bash
HUANXIN_PROFILE_DIR=/tmp/huanxin-profile-quantum-rnd node browser-automation/huanxin_probe.js
```

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
3. Use `scripts/ai2_shell.sh` for remote commands, inspections, and launch steps.
4. If a transfer is large or risky, run the helper with `--dry-run` first.

## State Values from Probe

| State | Meaning |
|-------|---------|
| `login_required` | Session expired. Run `huanxin_login.js` to re-authenticate. |
| `train_surface_or_project_page` | Authenticated, on the training page. |
| `authenticated_surface_ready` | Authenticated, editor/terminal detected. |
| `spa_loading` | Page loading, retry after a few seconds. |

## Safety Rules

- Only use **ai2**. ai1 belongs to the ALPHAQUBIT agent.
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
