# S3 Transfer Skill

Use this skill to transfer files between your **local machine**, **S3 storage**, and the **Huanxin remote server (ai2)** via rclone. S3 acts as the central hub — all transfers route through it.

## Current Reality Check

- Confirmed working: **local -> S3**, **ai2 -> read/list from S3**, and **ai2 -> S3 writes**.
- Important nuance: remote writes on ai2 must include `--s3-no-check-bucket`, otherwise `rclone` tries `CreateBucket` on the existing bucket and fails with `AccessDenied`.
- Practical implication: use the helper scripts in this repo for remote uploads instead of hand-rolled `rclone copy` commands without the S3 flag.

## Default Helper Entry Points

- Local -> S3: `scripts/push_to_s3.sh`
- S3 -> ai2: `scripts/ai2_sync_from_s3.sh`
- ai2 -> S3: `scripts/ai2_push_results_to_s3.sh`

Each transfer helper should be treated as the default path before falling back to raw `rclone` or browser-shell copy/paste.

## Architecture

```
┌──────────────┐           ┌──────────────────────┐           ┌──────────────────┐
│    Local      │           │         S3           │           │  Huanxin ai2     │
│  (this mac)   │  push ──► │  quantum-qwen25-     │ ◄── pull  │  /root/root/work/│
│               │ ◄── pull  │  coder-main          │  push ──► │  quantum-gpt     │
└──────────────┘           └──────────────────────┘           └──────────────────┘
```

There is **no direct connection** between local and Huanxin. Everything goes through S3.

## Key Paths

| Location | Path |
|----------|------|
| **S3 root** | `nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main` |
| **Huanxin ai2** | `/root/root/work/quantum-gpt` |
| **Local (this workspace)** | Project root (current working directory) |

For brevity, the S3 root is referred to as `$S3` below:
```
S3=nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main
```

## Prerequisites

- **rclone** configured with remote name `nm-aihuanxin` (both locally and on ai2)
- Huanxin browser automation for running commands on ai2 (see `skills/huanxin-browser/SKILL.md`)

### Verify rclone is working

```bash
# Local
rclone lsd nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/

# On ai2
node browser-automation/huanxin_shell_exec.js ai2 --command "rclone lsd nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/"
```

---

## Transfer Operations

### Local → S3 (Push Code Up)

```bash
scripts/push_to_s3.sh
scripts/push_to_s3.sh --dry-run
```

### S3 → Local (Pull Results Down)

```bash
# Pull specific folders
rclone copy nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main/outputs \
    ./outputs --progress

# Pull models
rclone copy nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main/models \
    ./models --progress
```

### S3 → Huanxin ai2 (Pull Code to Server)

Run these via the Huanxin browser shell:

```bash
# Full sync via helper
scripts/ai2_sync_from_s3.sh

# Preview remote sync first
scripts/ai2_sync_from_s3.sh --dry-run
```

### Huanxin ai2 → S3 (Push Results from Server)

Status: supported, but keep `--s3-no-check-bucket` on remote write commands.

```bash
# Default result sync
scripts/ai2_push_results_to_s3.sh

# Push selected paths only
scripts/ai2_push_results_to_s3.sh outputs models

# Preview remote upload first
scripts/ai2_push_results_to_s3.sh --dry-run outputs models
```

---

## Common Workflows

### Workflow A: Local Edit → Remote Train → Pull Results

1. **Push code to S3:**
   ```bash
   rclone copy . nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main \
       --exclude ".git/**" --exclude "__pycache__/**" --progress
   ```
2. **Pull & train on ai2:**
   ```bash
   node browser-automation/huanxin_shell_exec.js ai2 --command \
       "cd /root/root/work/quantum-gpt && rclone sync nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main . --progress && python3 train.py"
   ```
3. **Push results from ai2 to S3:**
   ```bash
   node browser-automation/huanxin_shell_exec.js ai2 --command \
       "cd /root/root/work/quantum-gpt && rclone copy outputs nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main/outputs --s3-no-check-bucket --progress"
   ```
4. **Pull results locally:**
   ```bash
   rclone copy nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main/outputs ./outputs --progress
   ```

### Workflow B: Browse What's on S3

```bash
# List top-level contents
rclone lsd nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main/

# List files in a subfolder
rclone ls nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main/outputs/

# Check total size
rclone size nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main/
```

---

## Useful rclone Flags

| Flag | Purpose |
|------|---------|
| `--progress` | Show transfer progress |
| `--dry-run` | Preview what would transfer (no changes) |
| `--transfers N` | Parallel transfers (default 4, use 8 for speed) |
| `--exclude "pattern"` | Skip matching files |
| `--include "pattern"` | Only include matching files |
| `--bandwidth 10M` | Limit bandwidth |
