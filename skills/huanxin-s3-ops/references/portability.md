# Portability Contract

This skill is designed to be shared across workspaces without leaking one workspace's Huanxin URL, S3 path, or browser-profile layout.

## What Must Stay Outside The Skill

Store these values in `TOOLS.md`, helper scripts, or local environment variables:

- canonical Huanxin train-dev URL
- valid environment names such as `AI`, `ai1`, or `ai2`
- default environment
- deprecated environments that must not be used for training
- remote workdir per environment
- S3 remote root or prefix
- S3 endpoint, access key id, and secret location
- browser profile path
- daemon ports
- wrapper script locations
- source environments used only for migration

## Minimal `TOOLS.md` Template

```md
## Huanxin

- Train-dev route: `https://...#/train-dev`
- Available environments: `AI`
- Default environment: `AI`
- Deprecated training environments: `ai1`, `ai2`
- Migration source environments: `ai2`
- Login rule: verify/login to the exact train-dev URL before shell, sync, or training
- Remote root AI: `/root/software/project`
- Remote root ai2: `/root/root/work/project`
- Generic shell wrapper: `scripts/huanxin_shell.sh`
- Status helper: `scripts/huanxin_status.sh`
- Profile repair helper: `scripts/repair_huanxin_browser_profile.sh`

## S3 Relay

- S3 root: `remote-name:bucket-or-prefix/project-root`
- S3 endpoint: `https://...`
- S3 secret location: project-local skill file or environment variable
- Local -> S3 helper: `scripts/push_to_s3.sh`
- S3 -> local helper: `scripts/pull_from_s3.sh`
- ai1 sync helper: `scripts/ai1_sync_from_s3.sh`
- active-env sync helper: `scripts/<env>_sync_from_s3.sh`
- ai1 push-back helper: `scripts/ai1_push_results_to_s3.sh`
- active-env push-back helper: `scripts/<env>_push_results_to_s3.sh`
```

## Recommended Script Contract

For a workspace to use this skill smoothly, the local repo should provide:

- one environment resolver, preferably `scripts/huanxin_env_config.py`, that returns train-dev URLs and daemon ports from either project defaults or a local JSON override
- one generic shell wrapper that accepts `<env> "<cmd>"`
- optional env-specific shortcuts
- one local push helper
- one local pull helper
- one per-env sync-from-S3 helper
- one per-env push-results-to-S3 helper
- one optional env-to-env migration helper for projects/models
- optional status or repair helpers
- optional S3 config helper that writes an isolated rclone config without printing secrets

Helpers should accept environment overrides for roots and remotes so the same scripts can serve multiple projects.

## Optional Environment Config File

For reusable projects, keep Huanxin environment details out of shell scripts. Use a project-local `.huanxin_envs.json` or point `HUANXIN_ENV_CONFIG_JSON` at another JSON file:

```json
{
  "train_dev_base_url": "https://.../kl-web?poolId=...&projectId=...#/train-dev",
  "envs": {
    "ASI1": {
      "env_id": "dl-...",
      "daemon_port": 20646
    },
    "research-a": {
      "train_dev_url": "https://...#/train-dev/environment/dl-...?name=research-a",
      "daemon_port": 20701
    }
  }
}
```

Wrappers should call the resolver instead of rebuilding URLs independently. This keeps shell access, status collection, task submission, and dashboards on one source of truth.

## Sharing Guidance

- Share the `skills/huanxin-s3-ops/` folder.
- Share wrapper scripts only if the receiving workspace does not already have equivalents.
- Do not publish personal cookies, profile directories, auth dumps, or private bucket credentials.
- If the receiving workspace uses different script names, update `TOOLS.md` there rather than cloning your personal notes into the skill.
- If a human asks to store an S3 secret in a project, store it only in a project-local secret/skill file and reference that path from `TOOLS.md`.
