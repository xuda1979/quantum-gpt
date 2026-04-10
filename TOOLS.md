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

- Train-dev route: `https://aihuanxin.cn/kunlun/kl-web?poolId=1&projectId=3ed7854b946a47b1a49ad754baa76cd3#/train-dev`
- User-required rule: use exactly the `#/train-dev` route above for Huanxin. Do not switch to alternate environment URLs or separate login pages unless explicitly instructed.
- Preferred remote target: `/root/root/work/quantum-gpt`
- Available environments: `ai1`, `ai2`
- Default environment: `ai2` unless `ai1` is a better fit for capacity or parallel work
- Browser helpers live under `browser-automation/`
- This repo is meant to be driven directly by Codex. Do not depend on OpenClaw-managed skills or `~/.openclaw` state for normal Huanxin or S3 operations.
- If the live browser profile is locked, clone it first and automate against `/tmp/huanxin-profile-copy`
- Do not kill the Huanxin browser daemon or otherwise discard the authenticated browser session unless explicitly instructed.

Common commands:

```bash
node browser-automation/huanxin_probe.js
./scripts/huanxin_shell.sh ai1 "pwd && whoami"
./scripts/ai2_shell.sh "pwd && whoami"
./scripts/huanxin_safari_keepalive.sh
./scripts/huanxin_safari_keepalive.sh --refresh
./scripts/huanxin_safari_keepalive_loop.sh --once
./scripts/install_huanxin_safari_keepalive_agent.sh --status
./scripts/huanxin_status.sh
./scripts/push_to_s3.sh --dry-run scripts skills
./scripts/ai2_shell.sh "rclone lsd nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/ | head"
node browser-automation/huanxin_inspect.js
node browser-automation/huanxin_open_env.js ai1
node browser-automation/huanxin_open_env.js ai2
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
- The stable default is still on-demand daemon startup plus Safari-backed self-heal.
- Browser-profile repair now runs on an isolated Chromium copy and only syncs back to `browser-automation/profile/` after the exact `#/train-dev` app surface is confirmed, so failed repair attempts should no longer poison the stored base profile.
- There is an optional ai2 daemon LaunchAgent helper in `scripts/install_huanxin_ai2_daemon_agent.sh`, but it is not the default path. Only opt into it explicitly with `HUANXIN_USE_DAEMON_AGENT=1` after validating it again.
- Background callback-driven profile repair from the Safari keepalive is disabled by default. Enable it only with `HUANXIN_BACKGROUND_PROFILE_REPAIR=1` if you are explicitly testing repair automation.
- Standalone shell fallback is disabled by default. Only set `HUANXIN_ALLOW_STANDALONE_FALLBACK=1` for explicit recovery/debugging.
- The manual loop remains available as a fallback: `bash scripts/huanxin_safari_keepalive_loop.sh`.
- If Apple Events are unavailable, `scripts/huanxin_safari_keepalive.sh` now prints structured JSON instead of failing silently.
- Safari helper failures from inside the sandbox are not authoritative. Re-check outside the sandbox before treating Safari itself as broken.
