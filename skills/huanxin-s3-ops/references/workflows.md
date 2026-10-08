# Workflow Recipes

Use the repo's helper scripts first. The exact script names, environments, S3 roots, and remote roots must come from `TOOLS.md`.

## Health Check

```bash
bash scripts/huanxin_status.sh
node browser-automation/huanxin_probe.js
```

Before the first remote shell, sync, or training action, verify that the session is logged in to the exact train-dev environment URL recorded in `TOOLS.md`. Use the probe or environment-open helper for that check. If auth is stale, repair/login first.

If a daemon reports `EADDRINUSE`, check the port health endpoint and process table before retrying. If the port is closed but startup still reports it in use, record the exact wrapper failure and use the repo's repair/login flow; do not kill browser profiles unless the human explicitly approves.

## Run A Remote Command

```bash
bash scripts/huanxin_shell.sh <env-name> "cd /root/work/project && pwd && whoami"
```

Prefer the generic shell wrapper over lower-level browser commands. Treat the command as connected only when the wrapper returns fresh output for the current command. If the project writes a connection-status artifact, use it for dashboards and follow-up status checks.

If the wrapper reports a daemon `getShellVisitUrl` / `wss://.../kunlun/null` failure and then succeeds through a documented standalone fallback, record both facts:

- command channel: connected through fallback
- daemon terminal endpoint: degraded Huanxin backend/API condition

Do not collapse those into a single "Huanxin is broken" or "everything is healthy" status.

## Local -> S3

```bash
bash scripts/push_to_s3.sh --dry-run scripts skills
bash scripts/push_to_s3.sh scripts skills
```

Push only the paths you need unless the workspace explicitly wants a broad sync.

## S3 -> Huanxin

```bash
bash scripts/<active-env>_sync_from_s3.sh --dry-run
bash scripts/<active-env>_sync_from_s3.sh

# Use the sync helper for the active environment in TOOLS.md.
```

Use the env-specific helper that matches the target environment.

## Huanxin -> S3

```bash
bash scripts/<env>_push_results_to_s3.sh --dry-run outputs reports models
bash scripts/<env>_push_results_to_s3.sh outputs reports models

# Use the push-results helper for the active environment in TOOLS.md.
```

Remote uploads often need `--s3-no-check-bucket`. The helper should own that detail.

## New S3 Endpoint Probe

Before a broad upload to a newly provided S3-compatible endpoint:

```bash
RCLONE_CONFIG=/tmp/project-s3.conf rclone lsd <remote>: --max-depth 1
RCLONE_CONFIG=/tmp/project-s3.conf rclone copyto /tmp/probe.txt <remote>:<bucket-or-prefix>/__probe__/probe.txt --s3-no-check-bucket
RCLONE_CONFIG=/tmp/project-s3.conf rclone lsf <remote>:<bucket-or-prefix>/__probe__ --s3-no-check-bucket
```

If the endpoint returns HTML, `405 Method Not Allowed` on `PutObject`, or XML parse errors from an HTML body, it is not currently a working S3 API URL for rclone. Stop and ask for the S3 API endpoint or bucket mapping; do not retry a full project upload.

## Huanxin Env -> Huanxin Env Migration

Use this when an old environment still contains models or project files that must be moved to the active environment.

1. Verify source environment shell access:
   ```bash
   bash scripts/huanxin_shell.sh <source-env> "pwd; echo \$HOME; test -d <source-root> && du -sh <source-root>"
   ```
2. Verify active target environment shell access and root:
   ```bash
   bash scripts/huanxin_shell.sh <active-env> "mkdir -p <target-root>; cd <target-root>; pwd"
   ```
3. Probe S3 with a tiny file.
4. Push source paths from the source env to S3 with the source helper or a migration helper.
5. Sync S3 into the active env target root.
6. Verify models with remote `find`, `du`, and required config/weight checks.

Do not delete source-env files after migration unless the human explicitly asks.

## S3 -> Local

```bash
bash scripts/pull_from_s3.sh --dry-run reports
bash scripts/pull_from_s3.sh reports
```

## Recommended End-To-End Pattern

1. Validate locally.
2. Verify/login to the exact Huanxin train-dev environment from `TOOLS.md`.
3. Probe the configured S3 relay if it is new or recently changed.
4. `push_to_s3.sh` the changed code or assets.
5. Run the env-specific S3 -> Huanxin sync helper that matches `TOOLS.md`.
6. Run the remote command with `huanxin_shell.sh`.
7. Push results back with the matching `*_push_results_to_s3.sh`.
8. Pull results locally with `pull_from_s3.sh`.

## Failure Handling

- If the Huanxin shell wrapper fails, check the workspace status helper first.
- If auth is stale, use the repo's repair or login path before retrying any remote action.
- If an S3 upload from Huanxin fails on bucket checks, use the repo helper instead of raw `rclone`.
- If an S3 endpoint returns an HTML app page, `405` on `PutObject`, or XML parse errors on HTML, treat the endpoint URL as wrong for S3 API use.
- If a workspace has inconsistent remote roots, trust the current helper script defaults over old notes.
