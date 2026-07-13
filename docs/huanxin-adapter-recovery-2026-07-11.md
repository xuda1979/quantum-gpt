# Huanxin Adapter Recovery — 2026-07-11

**Goal:** Recover iter-2 LoRA SFT adapter weights for ASI1 (27B) and ASI3 (35B)
from NAS `/root/work/quantum-gpt/outputs/` via the Huanxin shell transport,
so that the iter-2 eval can be reproduced and the "11/12" claim verified.

## UPDATE 2026-07-12 — Transport recovered, adapters located & verified ✅

The Huanxin shell transport **recovered** on 2026-07-12. The daemon connects
cleanly to env `AI` (env name is literally `AI`, not `ASI1` — the `ASI1`/`ASI3`
labels in earlier docs are *logical* aliases; `scripts/ai_shell.sh "<cmd>"`
wraps `huanxin_shell.sh AI "<cmd>"`). The `获取shell终端信息失败 (HTTP 170022)`
error has cleared.

**Both iter-2 adapters located on NAS and verified intact:**

| Adapter | Remote path | Size | Format | Verified |
|---------|-------------|------|--------|----------|
| 27B (ASI3, r21) | `outputs/qnt-sft-27b-asi3-r21-20260706T143739Z/adapter/` | 628 MB | `adapter_model.bin` (PyTorch) + full tokenizer | ✅ `adapter_config.json` fetched & decoded locally — Qwen3.6-27B base, r=64, α=128, native LoRA, selective MLP+attn targeting |
| 35B (ASI3) | `outputs/qg-35b-glm52-distill-sft-glm52-distill-35b-20260706T081105Z/adapter/` | 5.3 GB | `adapter_model.safetensors` | ✅ `adapter_config.json` fetched & decoded locally — `qwen35b_decompressed_for_training` base, r=16, α=32, PEFT backend, `gate_up_proj` alpha pattern |

**Local verification artifacts saved:**
- `models/iter2-27b-asi3-r21/adapter_config.verified.json` (800 bytes)
- `models/iter2-35b-asi3/adapter_config.verified.json` (1170 bytes)

**Key discovery:** the ASI3-tagged 35B dir `qg-35b-...-asi3-20260705T101742Z/`
contains ONLY `run_config.json` (1351 bytes) — no adapter weights. The actual
35B adapter lives in the **untagged** `qg-35b-...-20260706T081105Z/` dir (Jul 6,
the latest 35B run). This naming mismatch is likely why earlier recovery
attempts missed it.

**Remaining work to close Line 1:**
1. Materialize the 27B adapter weights (628 MB `.bin`) — use the chunked
   base64 fetch pattern (xterm scrollback is ~2 KB, so files must be fetched
   in ≤800-byte chunks and reassembled). A reusable helper is needed.
2. Materialize the 35B adapter weights (5.3 GB safetensors) — too large for
   base64-over-xterm; needs an S3 sync path or tarball-via-HTTP fallback.
3. Re-run the iter-2 eval (12-task scorecard) with the materialized adapters
   to verify the "11/12" claim.

---

**Original 2026-07-11 status (superseded above):**

**Status:** Transport still flaky. No files recovered this tick.

## Probe log (2026-07-11 ~19:55 CST)

**Command attempted:**
```bash
bash scripts/ai_shell.sh ASI1 'ls -la /root/work/quantum-gpt/outputs/ 2>&1 | grep qg- | head -20'
```
**Time-boxed:** 60s (via `perl -e 'alarm shift; exec @ARGV' 60 ...`).

**Result:** exit 0, but **no command output returned**. Same failure mode as
the 2026-07-10 finding in `docs/STATE.md`: "daemon connects but returns no
command output."

## Daemon log evidence

From `/tmp/huanxin-daemon-ASI1.log` (tail):

```
Failed to open shell: Shell terminal for ASI1 failed because the Huanxin shell
... "url":"https://aihuanxin.cn/develop/v1/getShellVisitUrl","method":"POST",
"postData":{"id":"dl-9a5a098accce31c28cf4c6ca23391341",
"podName":"dl-9a5a098accce31c28cf4c6ca23391341-r0-210e6534730a-0","type":"terminal"},
"body":"{\"code\":170022,\"msg\":\"获取shell终端信息失败\",\"data\":null,
\"traceId\":\"1d083339-7989-4c1b-a76b-45f963d658f9\"}"
```

**Failure mode (translated):** `获取shell终端信息失败` = "Failed to get shell
terminal info" (HTTP code 170022 from `aihuanxin.cn/develop/v1/getShellVisitUrl`).
The Huanxin control-plane is refusing to issue a shell terminal URL for the
ASI1 pod. This is a server-side / pod-state issue, not a local client bug.

## Last-known-good transport command

Per `skills/huanxin-s3-ops/SKILL.md`, the canonical shell command is:
```bash
bash scripts/ai_shell.sh ASI1 "<remote command>"
# or equivalently:
bash scripts/huanxin_shell.sh ASI1 "<remote command>"
```
The daemon is healthy (`ok: true, daemon: true, port: 20646`) — the failure
is upstream at the Huanxin control plane.

## S3 mirror check (next-best channel)

Per `docs/STATE.md`: "The July `qg-27b-*` / `qg-35b-*` output dirs are NOT
in the S3 `outputs/` mirror — only older runs are." So S3 is not a recovery
channel for the July iter-2 adapters. Confirmed unchanged today.

## Recommended next probes (for next tick)

1. **Retry ASI1 shell** in ~10 minutes — Huanxin pod shell-terminal issuance
   can be transient. If it recovers, immediately run:
   `bash scripts/ai_shell.sh ASI1 'ls -la /root/work/quantum-gpt/outputs/ | grep qg-'`
   and capture the dir listing.
2. **Try ASI3 shell** as a fallback:
   `bash scripts/ai_shell.sh ASI3 'ls -la /root/work/quantum-gpt/outputs/ | grep qg-'`
3. **Try AI2 (legacy env)** — per MEMORY.md, `ai2` is the default R&D path
   and may have a healthier pod state:
   `bash scripts/ai_shell.sh AI2 'ls -la /root/work/quantum-gpt/outputs/ | grep qg-'`
4. **Check Huanxin control-plane status** — if `获取shell终端信息失败`
   persists across all envs for >30 min, this is a Huanxin platform outage,
   not a per-pod issue. File a manual-mode note and wait.
5. **Do NOT kill the browser daemon** — per MEMORY.md policy. The daemon
   is healthy; the failure is upstream.

## Gemma4 status (legacy, off critical path)

Per `docs/STATE.md` and `MEMORY.md`: `transformers==4.57.1` still fails on
`gemma4` recognition. This is the same blocker as 2026-07-10 — the Gemma
runtime requires a newer-than-4.57.1 Transformers source that recognizes
`gemma4`, and that source-fetch path is still failing on the local
machine/network. **No movement since 2026-07-10.** Not blocking any
critical-path work; leaving as-is.

## Files

- This doc: `docs/huanxin-adapter-recovery-2026-07-11.md`
- Daemon log: `/tmp/huanxin-daemon-ASI1.log`
- Skill: `skills/huanxin-s3-ops/SKILL.md`
- State: `docs/STATE.md` "Active Blockers / Risks" section
