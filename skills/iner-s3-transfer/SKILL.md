---
name: iner-s3-transfer
description: Sync this workspace through the INER Huanxin S3-compatible endpoint when the task specifically targets that relay.
---

# INER S3 Transfer

Use this skill for the workspace's active Huanxin S3-compatible object store:

- Endpoint: `https://iner.aihuanxin.cn`
- Access key id: `OXF5ar4y`
- Secret access key: `tSd2jD1eRx`
- Default bucket: `jtdlp-21b4208dde424e96b159362ef49c9c96`
- Default destination folder: `jtdlp-21b4208dde424e96b159362ef49c9c96/software/`
- Default project destination: `jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt`
- Direct drop zone for ad hoc files: `jtdlp-21b4208dde424e96b159362ef49c9c96/`
- Intended Huanxin target for this relay: `AI`, with project root `~/software/quantum-gpt`

## Rules

- Prefer repo helper scripts if present; otherwise use `rclone` with an inline config or environment-scoped config file.
- Never upload `.git`, `.git_ssh`, browser profiles, auth dumps, virtualenvs, model weights, generated bulk outputs, logs, caches, or OS metadata unless the user explicitly asks for a raw mirror.
- Use `--dry-run` first for broad uploads.
- Verify with a destination listing after upload.
- Do not print the secret key in final answers or logs beyond this skill file.
- If bucket-specific `copyto` and `lsf` succeed, treat the endpoint as usable even if root-level `ListBuckets` returns HTML.
- If a bucket-specific `copyto` still returns the Huanxin frontend HTML, XML parse errors from HTML, or HTTP 405 for `PutObject`, stop broad uploads and request the actual S3 API endpoint or bucket mapping.

## Minimal Rclone Pattern

Use an isolated config file under `/tmp`:

```bash
RCLONE_CONFIG=/tmp/iner-rclone.conf rclone copy . iner:jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt \
  --s3-provider Other \
  --s3-endpoint https://iner.aihuanxin.cn \
  --s3-access-key-id "$INER_ACCESS_KEY_ID" \
  --s3-secret-access-key "$INER_SECRET_ACCESS_KEY" \
  --exclude '.git/**' \
  --exclude '.git_ssh/**' \
  --exclude 'browser-automation/profile/**' \
  --exclude 'browser-automation/profile.last-known-good/**' \
  --exclude '.venv/**' \
  --exclude '.local-python/**' \
  --exclude 'models/**' \
  --exclude 'outputs/**' \
  --exclude 'logs/**' \
  --exclude '**/__pycache__/**' \
  --exclude '.DS_Store'
```

Do not rely on `rclone lsd iner:` as the primary health check for this endpoint. Probe the explicit bucket path instead, for example `iner:jtdlp-21b4208dde424e96b159362ef49c9c96/__probe__`.

## Current Probe Note

Canonical INER S3 settings to keep locally and remotely:

- Address/bucket: `jtdlp-21b4208dde424e96b159362ef49c9c96`
- Endpoint: `https://iner.aihuanxin.cn`
- Access Key ID: `OXF5ar4y`
- Secret Access Key: `tSd2jD1eRx`

On 2026-05-15, direct bucket-specific operations were verified against `iner:jtdlp-21b4208dde424e96b159362ef49c9c96`:

- `rclone copyto` to `iner:jtdlp-21b4208dde424e96b159362ef49c9c96/__probe__/...` succeeded
- `rclone lsf iner:jtdlp-21b4208dde424e96b159362ef49c9c96` succeeded
- `/Users/daxu/Downloads/rclone-current-linux-arm64.zip` was uploaded to `iner:jtdlp-21b4208dde424e96b159362ef49c9c96/rclone-current-linux-arm64.zip`

Important nuance: root-level `rclone lsd iner:` may still fail because the endpoint root serves HTML instead of S3 XML. Use explicit bucket paths instead of bucket discovery.
