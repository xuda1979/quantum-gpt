#!/usr/bin/env python3
"""SAPO training-math WATCH — one continuous-mode cycle (training-math auditor).

Read-only box access via the daemon /exec transport (ASI3 by default). One
cycle:
  1. Find the newest `outputs/sapo-27b-ai-*` run dir on the box.
  2. Pull any NEW grpo_step_metrics.jsonl records since the local cache
     (chunked base64 + fold -w 100; the daemon caps ~4KB per /exec output and
     wraps long lines — per-record fetches with a two-halves fallback).
  3. Re-audit the FULL local cache with scripts/sapo_math_audit_step_records.py
     (auto mode: instrumented when the records carry the 2026-08-25 fields,
     legacy otherwise — the RunningMAD scale chain needs record continuity).
  4. Escalation signals: harness exit 2 (identity violation), or
     zero_change_alarm == true on a record with step > 1 (the 0-change
     adapter case; step-1 trust-region rejects legitimately fire it).
  5. Persist state to tmp/math-watch/state.json; print a compact summary and
     ESCALATE lines for the caller to relay.

Exit: 0 = waiting/clean, 2 = escalation-worthy finding(s).
Run dir pinning: RUN_DIR env (box path) overrides auto-discovery.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

QG_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(QG_ROOT))

from scripts.sapo_math_audit_step_records import (  # noqa: E402
    Finding,
    audit_jsonl,
)

DAEMON_URL = os.environ.get("MATH_WATCH_DAEMON_URL", "http://127.0.0.1:19005/exec")
BOX_ROOT = "/root/work/software/quantum-gpt"
STATE_DIR = QG_ROOT / "tmp" / "math-watch"
STATE_PATH = STATE_DIR / "state.json"


def run_remote(command: str, wait_ms: int = 120000) -> str:
    """One /exec call; returns the command's stdout (empty on failure).

    Retries transient transport failures (connection drops, bad JSON) up to
    3 times with a short backoff — the daemon occasionally resets the socket.
    """
    import time as _time

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            body = json.dumps({"command": command, "waitMs": wait_ms}).encode()
            req = urllib.request.Request(
                DAEMON_URL, data=body, headers={"Content-Type": "application/json"}
            )
            resp = json.loads(
                urllib.request.urlopen(req, timeout=wait_ms / 1000 + 60).read().decode()
            )
            if not resp.get("commandOk"):
                return ""
            return resp.get("output") or ""
        except Exception as exc:  # noqa: BLE001 — transport-level retry
            last_error = exc
            _time.sleep(3 * (attempt + 1))
    print(f"WARN: daemon transport failed after retries: {last_error}")
    return ""


def newest_run_dir() -> str | None:
    out = run_remote(f"ls -d {BOX_ROOT}/outputs/sapo-27b-ai-* 2>/dev/null | sort | tail -1")
    path = out.strip().splitlines()[-1].strip() if out.strip() else ""
    return path or None


CHUNK_BYTES = 1200  # base64 of 1200 bytes = 1600 chars, safely under the ~4KB /exec cap


def fetch_record(run_dir: str, n: int) -> str | None:
    """Fetch record line n (1-based); None on failure.

    The daemon caps /exec output at ~4KB and wraps long lines, so records
    (up to ~6KB with the 2026-08-25 fields) are pulled in byte chunks and
    reassembled; the full-record single fetch is attempted first.
    """
    src = f"{run_dir}/grpo_step_metrics.jsonl"
    cmd = f"sed -n '{n}p' {src} | base64 -w0 | fold -w 100"
    out = run_remote(cmd)
    if out:
        try:
            raw = base64.b64decode("".join(out.splitlines())).decode()
            json.loads(raw)
            return raw
        except Exception:
            pass
    parts: list[str] = []
    for offset in range(1, 16001, CHUNK_BYTES):
        chunk_cmd = (
            f"sed -n '{n}p' {src} | tail -c +{offset} | head -c {CHUNK_BYTES} "
            f"| base64 -w0 | fold -w 100"
        )
        out_chunk = run_remote(chunk_cmd)
        if not out_chunk:
            break
        try:
            parts.append(base64.b64decode("".join(out_chunk.splitlines())).decode())
        except Exception:
            return None
        candidate = "".join(parts)
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            continue
    return None


def record_count(run_dir: str) -> int:
    out = run_remote(f"wc -l < {run_dir}/grpo_step_metrics.jsonl")
    try:
        return int(out.strip().split()[-1])
    except (ValueError, IndexError):
        return -1


def load_state() -> dict:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"run_dir": None, "last_count": 0, "escalated": []}


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=1), encoding="utf-8")


def main() -> int:
    pinned = os.environ.get("RUN_DIR")
    run_dir = pinned or newest_run_dir()
    if not run_dir:
        print("WAITING: no sapo run dir on the box yet")
        return 0
    state = load_state()
    if state.get("run_dir") != run_dir:
        # New run: reset the cache and state.
        state = {"run_dir": run_dir, "last_count": 0, "escalated": []}
        run_name = run_dir.rsplit("/", 1)[-1]
        cache = STATE_DIR / f"{run_name}.jsonl"
        if cache.exists():
            cache.unlink()
        print(f"NEW RUN: {run_name}")
    run_name = run_dir.rsplit("/", 1)[-1]
    cache = STATE_DIR / f"{run_name}.jsonl"
    count = record_count(run_dir)
    if count < 0:
        save_state(state)
        print(f"CHECK FAILED: cannot read record count for {run_name}")
        return 0
    if count <= state.get("last_count", 0):
        print(f"IDLE: {run_name} at {count} records (no growth)")
        return 0
    # Pull the new records.
    new_records: list[dict] = []
    for n in range(state.get("last_count", 0) + 1, count + 1):
        raw = fetch_record(run_dir, n)
        if raw is None:
            print(f"PULL FAILED at record {n} — will retry next cycle")
            break
        new_records.append(json.loads(raw))
    if not new_records:
        return 0
    with open(cache, "a", encoding="utf-8") as fh:
        for rec in new_records:
            fh.write(json.dumps(rec) + "\n")
    state["last_count"] = state.get("last_count", 0) + len(new_records)
    # Auto mode: instrumented when ANY cached record carries the 2026-08-25
    # fields (skipped records legitimately lack per_candidate_losses, so the
    # newest record alone is not a reliable probe).
    all_records = []
    for line in cache.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                all_records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    mode = (
        "instrumented"
        if any("per_candidate_losses" in r or "loss_breakdown" in r for r in all_records)
        else "legacy"
    )
    findings, n_error, n_note = audit_jsonl(
        cache, mode=mode, tau_pos=1.0, tau_neg=1.05, kl_coeff=0.01, advantage_clip=2.5
    )
    escalations: list[Finding] = []
    for f in findings:
        if f.severity == "ERROR":
            key = f"{f.step}:{f.check}"
            if key not in state["escalated"]:
                escalations.append(f)
                state["escalated"].append(key)
    # Zero-change alarm on step > 1 (the 0-change adapter case).
    for rec in new_records:
        step = int(rec.get("step", -1))
        if bool(rec.get("zero_change_alarm")) and step > 1:
            key = f"{step}:zero_change_alarm"
            if key not in state["escalated"]:
                escalations.append(
                    Finding(
                        step,
                        "zero_change_alarm",
                        "ERROR",
                        f"ZERO-CHANGE ALARM on step {step} (lora_b_max_delta {rec.get('lora_b_max_delta')}, "
                        f"trust_region_violated {rec.get('trust_region_violated')}) — adapter byte-identical to base",
                    )
                )
                state["escalated"].append(key)
    save_state(state)
    print(
        f"AUDIT: {run_name} step<= {new_records[0].get('step', '?')}..{new_records[-1].get('step', '?')} "
        f"mode={mode} errors={n_error} notes={n_note} new={len(new_records)} total={state['last_count']}"
    )
    for f in escalations:
        print(f"ESCALATE: {f.render()}")
    return 2 if escalations else 0


if __name__ == "__main__":
    sys.exit(main())
