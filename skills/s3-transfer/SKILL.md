---
name: s3-transfer
description: Debug repo-specific S3 helper and rclone edge cases. Use huanxin-s3-ops for normal end-to-end Huanxin workflows.
---

# S3 Transfer Debugging

Use this file only for repo-specific S3 relay details, helper-script behavior, and `rclone` edge cases.

Do not use this as the default skill for everyday local <-> S3 <-> Huanxin movement. The canonical entrypoint for normal transfer workflows is `skills/huanxin-s3-ops/SKILL.md`.

## Use This Only When

- a repo S3 helper is failing or behaving unexpectedly
- you need the exact `rclone` nuance behind a helper script
- you need to debug remote upload edge cases such as bucket-check failures
- you need to inspect include/exclude behavior for this repo's sync policy

## Default Stance

- Prefer the repo helpers over raw `rclone`.
- Prefer `skills/huanxin-s3-ops/SKILL.md` for normal operations.
- Treat S3 as the data plane between local disk and Huanxin.
- Before any remote-side sync or training step, verify/login to the active Huanxin environment described in `TOOLS.md`; do not assume old ai1/ai2 sessions are valid.
- Use `--dry-run` first for large or risky transfers.

## Main Helper Entry Points

- `scripts/push_to_s3.sh`
- `scripts/pull_from_s3.sh`
- `scripts/ai1_sync_from_s3.sh`
- `scripts/ai2_sync_from_s3.sh`
- `scripts/ai1_push_results_to_s3.sh`
- `scripts/ai2_push_results_to_s3.sh`

## Repo-Specific Nuances

### Remote Uploads

- Remote writes may require `--s3-no-check-bucket`.
- If a raw `rclone copy` from Huanxin fails on bucket checks, switch back to the repo helper.

### Sync Scope

- The default helpers are intentionally code-first.
- Bulky artifacts such as models, outputs, logs, screenshots, and memory files are commonly excluded unless explicitly requested.

### Verification

- Trust concrete sync markers, log tails, and destination listings over assumptions.
- If local notes and helper defaults disagree, trust the current helper script implementation.
- If the endpoint returns HTML, XML parse errors from HTML, or `405 Method Not Allowed` for object writes, treat that as an endpoint/bucket-mapping blocker and stop broad uploads.

## Success Standard

A successful debugging step should produce one of:

- a passing helper invocation
- a dry-run showing the expected file set
- a concrete diagnosis naming the exact helper or `rclone` flag causing the issue
