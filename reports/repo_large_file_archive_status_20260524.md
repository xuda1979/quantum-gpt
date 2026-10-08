# Repo Large-File Archive Status - 2026-05-24

## Scope

Archived local large-file candidates from `/Users/daxu/software/quantum-gpt`:

- `outputs`
- `artifacts/runtime-bundles`
- `artifacts/quantum-rag`
- `artifacts/branch-switch-backups`
- `artifacts/downloads`

## Verified Complete

- User removed `.git/objects/pack/tmp_pack_*`; follow-up check showed zero remaining temp packs.
- INER S3 per-directory upload was verified earlier for the five paths.
- A single recovery archive was also created locally:
  - `/tmp/quantum-gpt-large-local-archive-20260524.tar.gz`
  - size: `702.022 MiB`
  - SHA256: `e1fe68fc290518be96f03c85a6c1998f8821f62de2869135b150b5d5c9a7ba9f`
- The single archive was uploaded and verified in INER S3:
  - `iner:jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt-archives/quantum-gpt-large-local-archive-20260524.tar.gz`
  - verified size: `702.022 MiB`

## Huanxin / ASI1 Status

- ASI1 is the active user-named environment for this cleanup.
- `/root/work` is full on ASI1, so archive materialization must use `/workspace`.
- Added wrapper: `scripts/submit_asi1_archive_materialize_task.sh`.
- The wrapper now does a fast `https://iner.aihuanxin.cn` HEAD preflight before attempting the 702 MiB download, so future retries fail quickly if ASI1 cannot reach INER.
- Submitted task:
  - name: `asi1-archive-0524`
  - id: `dt-cacb462b3a974cc5a3dc5973e0d59a73`
  - target: `/workspace/quantum-gpt-archive/20260524`
- Result: failed before download completion. The pod reached `/workspace` and printed `__ASI1_ARCHIVE_MATERIALIZE_START__`, then `curl` timed out connecting to `https://iner.aihuanxin.cn` on all retries.
- A tiny shell-sync probe also hung before opening the ASI1 shell, so browser-shell base64 transfer is not currently a reliable substitute for the large archive.
- Fast retry after adding the HEAD preflight:
  - name: `asi1-archive-fast`
  - id: `dt-32a7d49390144ae1b1e7311a74469257`
  - status: failed in `00:00:09`
  - log: `curl: (28) Connection timeout after 8000 ms`
  - conclusion: ASI1 task pods currently cannot reach `https://iner.aihuanxin.cn`, so INER S3 materialization from ASI1 is blocked before the archive download begins.
- ASI1 dev-shell follow-up:
  - command: `HUANXIN_WAIT_MS=60000 bash scripts/huanxin_env_shell.sh --env ASI1 "printf '__ASI1_DEV_SHELL_OK__\\n'; python3 -c 'import socket; s=socket.create_connection((\"iner.aihuanxin.cn\",443),8); print(\"__INER_443_TCP_OK__\"); s.close()'"`
  - result: shell reached ASI1 and printed `__ASI1_DEV_SHELL_OK__`, but Python raised `TimeoutError: timed out` while opening `iner.aihuanxin.cn:443`
  - conclusion: ASI1 dev shell and ASI1 task pods both currently cannot reach the INER S3 endpoint, so archive materialization is blocked by ASI1-to-INER network reachability rather than by the task wrapper alone.
- Existing no-egress alternatives were inspected:
  - the embedded task-payload pattern is only practical for small artifacts such as wheel files; the local task launcher reads specs with an 8 MiB buffer, while the archive would be about 936 MiB after base64 encoding
  - browser-shell sync is not a viable substitute for the archive because the helper is small-transfer oriented and the earlier tiny ASI1 sync probe hung
- 2026-05-25 follow-up:
  - repeated ASI1 dev-shell TCP probe still timed out on `iner.aihuanxin.cn:443`
  - `browser-automation/huanxin_shell_sync.js` remained unreliable for ASI1 today and failed into an auth/login state while trying a tiny payload
  - added `scripts/huanxin_upload_small_file.sh` for bounded one-file control-plane uploads through `scripts/huanxin_env_shell.sh`
  - validated the new helper locally with `bash -n scripts/huanxin_upload_small_file.sh` and `python3 -m pytest tests/test_huanxin_upload_small_file.py`
  - proved the helper end to end on ASI1 by uploading a 38-byte smoke file to `/workspace/quantum-gpt-archive/probes/upload-helper-20260525/smoke.txt`; remote SHA256 matched local SHA256
  - conclusion: ASI1 has a verified no-INER control-plane path for tiny files, but the 702 MiB archive still needs ASI1-to-INER egress, another Huanxin-managed ingress, or a purpose-built resumable chunk uploader with remote SHA verification

## Local Deletion Decision

Do not remove the local copies yet. S3 is verified, but the Huanxin-side copy is not verified. The safe deletion gate is:

1. ASI1 downloads the archive.
2. ASI1 SHA256 matches `e1fe68fc290518be96f03c85a6c1998f8821f62de2869135b150b5d5c9a7ba9f`.
3. ASI1 extracts the archive under `/workspace/quantum-gpt-archive/20260524/extracted`.
4. ASI1 file count and `du -sh` match the local/S3 archive scope.

After that, move the local candidates to Trash with `/usr/bin/trash`, not permanent deletion.
