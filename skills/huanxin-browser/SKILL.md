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
