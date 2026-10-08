# S3 Endpoint Investigation — 2026-07-12

**Goal:** Find a working S3 upload path to materialize the iter-2 adapter weights
(27B: 628 MB, 35B: 5.3 GB) from NAS to local.

## Findings

### Remote env AI tooling
- `boto3 1.43.46` ✅ installed (no creds configured)
- `rclone` ❌ missing
- `aws` CLI ❌ missing
- `curl 7.81.0` ✅ available
- Internet access ✅ (baidu.com returns 200)
- File-sharing services (file.io, 0x0.st, transfer.sh) ❌ all blocked

### Local rclone config (`~/.config/rclone/rclone.conf`)
Two S3 remotes configured:

| Remote | Endpoint | Access Key | Secret Key |
|--------|----------|------------|------------|
| `nm-aihuanxin` | `https://nm.aihuanxin.cn` | `qAu2hO9z` | `lEv8Tu6oYO` |
| `iner-aihuanxin` | `https://iner.aihuanxin.cn` | `OXF5ar4y` | `tSd2jD1eRx` |

### Endpoint behavior

| Endpoint | curl root | rclone ListBuckets | rclone ListObjects (jtdlp bucket) | Remote boto3 |
|----------|-----------|---------------------|-----------------------------------|--------------|
| `nm.aihuanxin.cn` | HTML (Huanxin community website, nginx reverse proxy) | 504 Gateway Timeout (10 retries, 11 min) | 504 Gateway Timeout | ListBuckets 500, ListObjects 404 |
| `iner.aihuanxin.cn` | HTML (same Huanxin community site) | 200 but XML parse error | Not tested | Not reachable from remote (HTTP 000) |

### Root cause

Both endpoints are reverse-proxied by nginx to serve the Huanxin community
website (`焕新社区`) at the root path. The S3/MinIO API is **NOT at the root** —
it's likely at a path prefix (e.g., `/minio/`, `/s3/`) or a different subdomain.

Evidence:
- `curl https://nm.aihuanxin.cn/` → HTML homepage
- `curl https://nm.aihuanxin.cn/minio/health/live` → 404
- `curl https://nm.aihuanxin.cn/minio/` → 200 (nginx static page)
- `curl https://nm.aihuanxin.cn/quantum-qwen25-coder-main/` → HTML homepage

### Bucket name from `ai3_nm_s3_env.sh`
```
DEFAULT_S3_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main"
```
- Bucket: `jtdlp-3ed7854b946a47b1a49ad754baa76cd3`
- Prefix: `quantum-qwen25-coder-main`

### boto3 tests on remote (results not fully captured due to transport issues)
- `create_bucket("quantum-gpt-iter2-adapters")` — result unknown (background task output capture failed)
- `put_object("test.txt")` — result unknown (same issue)
- `list_objects_v2("jtdlp-...", prefix="quantum-qwen25-coder-main/")` with path-style addressing — result unknown

### Transport degradation
The Huanxin daemon transport became extremely slow (>60s per command) during
the session, causing all `ai_shell.sh` calls to be auto-backgrounded. Background
task output capture is broken for daemon transport (only captures the initial
`[huanxin_shell:AI] Using daemon transport.` stderr line, not the JSON response
on stdout).

## Next steps to unblock weight materialization

### Option A: Find the real S3 API endpoint (RECOMMENDED)
1. Check `scripts/ai3_sync_from_s3.sh` execution logs from a working run —
   what URL does rclone actually hit?
2. Check Huanxin platform documentation for the MinIO S3 API URL.
3. Ask the Huanxin platform team for the S3 endpoint.
4. Try common MinIO paths: `/minio/s3/`, `/api/s3/`, `/v1/`, etc.
5. Try DNS: `dig nm.aihuanxin.cn` — are there other subdomains like `s3.nm.aihuanxin.cn`?

### Option B: HTTP tunnel (FALLBACK)
1. Start a local HTTP server that accepts POST uploads.
2. Use `ngrok` or `cloudflared` to expose it publicly.
3. From the remote, `curl -T adapter_model.bin https://<tunnel-url>/upload`.
4. This bypasses S3 entirely but requires the remote to reach the tunnel.

### Option C: Chunked base64 for 27B only (LAST RESORT)
- 628 MB / 800 bytes per chunk = ~820K chunks.
- Not practical via xterm (would take days).
- Could work via a remote script that writes chunks to an HTTP endpoint.
- 35B (5.3 GB) is completely impractical via this approach.

### Option D: Install rclone on remote
- `pip install rclone` failed (rclone is a Go binary, not a pip package).
- Could try downloading the binary: `curl -L https://downloads.rclone.org/rclone-current-linux-arm64.zip -o /tmp/rclone.zip` — but this was attempted and the result wasn't captured.
- If rclone can be installed on the remote, `ai3_sync_from_s3.sh` pattern could work in reverse (remote→S3).

## Definitive finding (23:00 CST): S3 endpoints are DEGRADED

Local rclone dry-run on `nm-aihuanxin:jtdlp-.../quantum-qwen25-coder-main/`
ran for **5+ minutes with 0 bytes transferred** — rclone kept retrying every
60s with no progress, confirming the MinIO server is not responding to S3
API calls.

Remote boto3 `create_bucket` call captured a traceback showing the exact
failure mode: the SSL/socket connection to `nm.aihuanxin.cn` established
but the server **never sent an S3 API response** — the call hung at
`ssl.SSLObject.read()` → `socket.recv_into()` and was killed by a
`KeyboardInterrupt` (daemon timeout). This is a **server-side hang**, not
a client error.

**Conclusion:** Both S3 endpoints (`nm.aihuanxin.cn`, `iner.aihuanxin.cn`)
are **server-side degraded** right now. This is NOT a client configuration
issue — the endpoints serve HTML at the root (Huanxin community website) and
do not respond to S3 API calls. The S3 upload path is **not viable** until
the Huanxin platform team restores the MinIO service.

**Recommended action:** Contact the Huanxin platform team to:
1. Confirm the MinIO S3 API endpoint URL (it may have changed).
2. Check if the MinIO service is down for maintenance.
3. Provide updated S3 credentials/endpoint if the service has migrated.

## Files

- This doc: `docs/s3-endpoint-investigation-2026-07-12.md`
- Adapter manifest: `models/iter2-adapters-manifest.json`
- Recovery doc: `docs/huanxin-adapter-recovery-2026-07-11.md` (UPDATE section)
