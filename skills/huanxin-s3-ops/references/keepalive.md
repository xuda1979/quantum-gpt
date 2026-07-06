# Huanxin Login and Keepalive

Use this reference when the human asks to keep Huanxin alive, regularly login,
refresh auth, or prevent a train-dev environment session from going cold.

## Principles

- Keep the exact train-dev URL from the current repo's `TOOLS.md` as the source
  of truth.
- Prefer a warm browser daemon, Safari keepalive, or repo wrapper over repeated
  standalone browser launches.
- Do not stop an existing daemon, kill a browser profile, or unload a
  LaunchAgent unless the human explicitly asks.
- If auth is stale, try the repo repair or SSO refresh path first; ask for
  manual headed login only when automated recovery fails.
- Leave evidence: status output, health JSON, refreshed URL, or a successful
  remote `pwd && date` command.

## Discovery

Inspect available helpers:

```bash
find scripts launchd browser-automation -maxdepth 2 -type f 2>/dev/null \
  | grep -E 'huanxin|keepalive|daemon|login|repair|shell|s3'
```

Then read `TOOLS.md` and the relevant helper scripts before acting.

## Common Status Checks

```bash
bash scripts/huanxin_status.sh
bash scripts/huanxin_shell.sh <env-name> "date; pwd"
```

If browser automation is delegated to another workspace, read that workspace's
Huanxin browser and S3 skills/scripts for daemon ports and repair commands.
Do not copy its pool IDs, project IDs, S3 roots, or remote paths into the
current workspace.

## One-Shot Keepalive

When a repo provides a keepalive helper:

```bash
bash scripts/huanxin_safari_keepalive_loop.sh --once
```

If only a direct shell wrapper exists, use a harmless remote command as the
keepalive proof:

```bash
bash scripts/huanxin_shell.sh <env-name> "date; cd <remote-root> && pwd"
```

## Persistent Keepalive

When a repo provides LaunchAgent installers, prefer status before install:

```bash
bash scripts/install_huanxin_safari_keepalive_agent.sh --status
bash scripts/install_huanxin_ai2_daemon_agent.sh --status
```

Install only when the human wants persistent local keepalive:

```bash
bash scripts/install_huanxin_safari_keepalive_agent.sh --install
```

For workspaces without LaunchAgent installers, a foreground loop can be used
only while Codex is actively working:

```bash
HUANXIN_KEEPALIVE_INTERVAL_SEC=240 \
bash scripts/huanxin_safari_keepalive_loop.sh
```

Do not leave ad hoc loops running forever unless the user asked for that.

## Manual Login Recovery

Use manual login only after automated repair fails:

```bash
node browser-automation/huanxin_login.js
```

Tell the human exactly which URL/environment needs login and wait for them to
complete it. Afterward, re-run the status check and a harmless shell command.
