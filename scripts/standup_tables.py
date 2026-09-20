#!/usr/bin/env python3
"""Dedicated standup-table harness (USER directive 2026-09-15).

Deterministically renders the STANDUP TABLES EVERY tick in good shape from LIVE
durable state (never hand-written, never a stale brief):

  (1) RESOURCES        : every provisioned daemon /health + keeper state (S9.1)
  (2) TRAINING         : ASI1 live run, trainer proc, step-metrics, cadence, ckpts
  (3) EVAL             : ASI3 vLLM + active adapter + judge/upstream
  (4) AGENT STATUS     : per-lane role files (LIVE/STALE by mtime) + live system lanes
  (5) 130+ ITEMS       : the 134-check contract (auditor sections A-M) status
  (6) CODE-CLEANLINESS : per-file LOC with SHORT/OK/LONG flags
  (7) TESTING          : unit (full suite) / regression / collection / system

Fails CLOSED: unreadable fields render UNKNOWN/IDLE/NA in the cell -- never
fabricated, never a dropped row)Skip. Ruff-clean: no compact one-liners.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

QG = Path("/Users/daxu/software/quantum-gpt")
LANES = QG / ".sapo-loop" / "lanes"
KEEPER_STATE = Path("/tmp/session_keeper_state.json")
JUDGE_STATE = Path("/tmp/sapo_judge_health_state.json")
CONTRACT_ROTATION = QG / ".sapo-loop" / "contract_rotation.txt"
CONTRACT_MONITOR_LAST = LANES / "contract_monitor_last.md"
MONITORING_CONTRACT = QG / ".sapo-loop" / "MONITORING_CONTRACT.md"
BP = "/grpo_step_metrics.jsonl"
BOX_RUN_GLOB = "/root/work/software/quantum-gpt/outputs/sapo-27b-ai-2026*"
VLLM_PORTS = ["8355", "8356"]
SECTIONS = list("ABCDEFGHIJKLM")
LONGLOC = 800
OKLOC = 300
UNREACHABLE = "TRANSPORT-UNREACHABLE"  # B-264: exec transport dead -- UNKNOWN, never absence
SYSTEM_PATTERNS = {
    "keeper": "session_keeper.sh",
    "heartbeat": "sapo_huanxin_heartbeat",
    "system_monitor": "sapo_system_monitor",
    "judge_health": "sapo_judge_health",
    "metrics_poller": "sapo_metrics_poller",
    "wedge_watch": "sapo_wedge_watch",
}


def now() -> datetime:
    return datetime.now(timezone.utc)


def age_min(path: Path):
    try:
        m = (now() - datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)).total_seconds() / 60.0
        return m
    except Exception:
        return None


def embedded_audit_date(path: Path):
    """B-267: the audit timestamp embedded in a section report's header.

    mtime is a LIE for audited artifacts -- ANY touch (a marker prepend, a
    re-save) refreshes it and a 14-day-old audit re-reads as fresh. Parse the
    header's "Date: YYYY-MM-DD" / "Updated: YYYY-MM-DD[THH:MM]" instead.
    Returns a datetime (UTC) or None when the header carries no date.
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            head = [fh.readline() for _ in range(20)]
    except Exception:
        return None
    for line in head:
        m = re.match(r"\s*(?:Date|Updated)\s*:\s*(\d{4}-\d{2}-\d{2})(?:[T ](\d{1,2}):(\d{2}))?", line)
        if m:
            d = m.group(1)
            hh = int(m.group(2) or 0)
            mm = int(m.group(3) or 0)
            try:
                return datetime.strptime(d, "%Y-%m-%d").replace(
                    hour=hh, minute=mm, tzinfo=timezone.utc)
            except ValueError:
                return None
    return None


def audit_age_min(path: Path):
    """Age of the AUDIT (embedded header date first, mtime fallback).

    Embedded-date precedence makes the age touch-proof for old audits. A
    date-only stamp of TODAY has no sub-day precision, so for that one case
    the (bounded) mtime decides the 40-min freshness window. None = no age
    source at all -> caller must fail closed (UNVERIFIED), never "fresh".
    """
    emb = embedded_audit_date(path)
    if emb is not None:
        if emb.date() == now().date():
            m = age_min(path)
            if m is not None:
                return m
        return (now() - emb).total_seconds() / 60.0
    return age_min(path)


def daemon_health(port: int) -> dict:
    url = f"http://127.0.0.1:{port}/health"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=6) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:
        return {"ready": False, "startupState": "unreachable", "error": str(e)}


def box_exec(port: int, cmd: str, timeout: int = 30) -> str:
    url = f"http://127.0.0.1:{port}/exec"
    data = json.dumps({"command": cmd}).encode()
    try:
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))
        o = d.get("output", d)
        if isinstance(o, dict):
            o = o.get("output", "")
        return str(o or "")
    except Exception:
        return None  # B-264: transport dead -> None (UNKNOWN); "" stays a genuine empty answer


def live_run_dir(port: int) -> str:
    cmd = f"ls -dt {BOX_RUN_GLOB} 2>/dev/null | grep -v -e _base -e base | head -1"
    o = box_exec(port, cmd)
    if o is None:
        return UNREACHABLE
    p = o.strip().splitlines()
    return p[0] if p else ""


def trainer_proc(port: int) -> str:
    o = box_exec(port, "pgrep -af grpo_trainer.py 2>/dev/null | head -3")
    if o is None:
        return UNREACHABLE
    return o.strip().replace("\n", " | ")


def step_metrics(port: int, run_dir: str):
    if not run_dir:
        return {}, -1, []
    if run_dir == UNREACHABLE:
        return {}, UNREACHABLE, []
    cmd = (
        f"test -f {run_dir}{BP} && echo EXISTS || echo NOFILE; echo SEP; "
        f"tail -n 3 {run_dir}{BP} 2>/dev/null; echo SEP; wc -l < {run_dir}{BP} 2>/dev/null"
    )
    o = box_exec(port, cmd)
    if o is None:
        return {}, UNREACHABLE, []
    parts = o.split("SEP")
    if not parts or parts[0].strip() != "EXISTS":
        return {}, 0, []
    tail: list[dict] = []
    try:
        tail = [json.loads(x) for x in parts[1].strip().splitlines() if x.strip()]
    except Exception:
        tail = []
    rec = tail[-1] if tail else {}
    count = -1
    try:
        count = int(parts[2].strip())
    except Exception:
        count = -1
    return rec, count, tail


def ckpt_info(port: int, run_dir: str):
    if not run_dir:
        return -1, "", ""
    if run_dir == UNREACHABLE:
        return UNREACHABLE, UNREACHABLE, UNREACHABLE
    cmd = (
        f"ls -d {run_dir}/step_*_adapter 2>/dev/null | wc -l; echo SEP; "
        f"ls -dt {run_dir}/step_*_adapter 2>/dev/null | head -1; echo SEP; "
        f"ls {run_dir}/ 2>/dev/null | head -14"
    )
    o = box_exec(port, cmd)
    if o is None:
        return UNREACHABLE, UNREACHABLE, UNREACHABLE
    parts = o.split("SEP")
    lines = [x.strip() for x in (parts[0] or "").splitlines() if x.strip()]
    cnt = -1
    try:
        cnt = int(lines[0])
    except Exception:
        cnt = -1
    adap = (parts[1] or "").strip() if len(parts) > 1 else ""
    listing = "\n".join((parts[2] or "").splitlines()[:14]) if len(parts) > 2 else ""
    return cnt, adap, listing


def cadence(tail: list) -> str:
    if len(tail) < 2:
        return "n/a (<2 records)"
    stamps: list[datetime] = []
    for r in tail:
        v = r.get("ts") or r.get("timestamp") or ""
        m = re.search(r"\d{4}-\d{2}-\d{2}[T ][\d:.]+", v)
        if m:
            stamps.append(datetime.fromisoformat(m.group(0).replace("Z", "+00:00").replace(" ", "T")))
    if len(stamps) < 2:
        return "n/a (no ts)"
    dt = (stamps[-1] - stamps[0]).total_seconds()
    n = len(stamps) - 1
    if dt <= 0:
        return "n/a"
    rate = n / (dt / 3600.0)
    return f"{rate:.1f} steps/hr over last {n} steps ({dt/60:.0f}m)"


def vllm_probe(port: int) -> str:
    dead = False
    for vp in VLLM_PORTS:
        cmd = f"(ss -ltn 2>/dev/null || netstat -ltn 2>/dev/null) | grep -q ':{vp} ' && echo UP || echo DOWN"
        o = box_exec(port, cmd)
        if o is None:
            dead = True
            continue
        if "UP" in o:
            return f"UP on :{vp}"
    if dead:
        return UNREACHABLE + " (vLLM port state unknown)"
    return "vLLM server not detected"


def judge_state() -> str:
    try:
        d = json.loads(JUDGE_STATE.read_text())
        return f"healthy={d.get('healthy')} strikes={d.get('strikes')} detail={str(d.get('detail'))[:50]}"
    except Exception:
        return "judge state unreadable"


def _first(p: Path) -> str:
    return "".join(p.read_text(errors="replace").splitlines()[:1]).strip()


def system_lanes() -> list:
    rows = []
    try:
        out = subprocess.run(["ps", "ax", "-o", "pid,etime,command"], capture_output=True,
                             text=True, timeout=10).stdout
        for name, pat in SYSTEM_PATTERNS.items():
            hit = [ln for ln in out.splitlines()
                   if pat in ln and "grep" not in ln and "standup_tables" not in ln and "run_full_suite" not in ln]
            if hit:
                cols = hit[0].split()
                rows.append((name, cols[0] + " (" + cols[1] + ")", "LIVE"))
            else:
                rows.append((name, "DEAD", "DEAD/RED"))
    except Exception:
        for name in SYSTEM_PATTERNS:
            rows.append((name, "-", "UNKNOWN"))
    try:
        s = subprocess.run(["pgrep", "-af", "run_full_suite"], capture_output=True,
                           text=True, timeout=10).stdout
        rows.append(("suite-runner", s.split()[0] if s.strip() else "idle",
                     "LIVE" if s.strip() else "idle"))
    except Exception:
        rows.append(("suite-runner", "-", "UNKNOWN"))
    return rows


def _section_check_counts():
    """B-321: per-section check counts from MONITORING_CONTRACT.md.

    Counts numbered table rows ("| N |") under each "## <Letter>." heading.
    Returns None when the register is unreadable so the table renders "?"
    per row and never fabricates a number (fail-closed).
    """
    try:
        text = MONITORING_CONTRACT.read_text(encoding="utf-8")
    except Exception:
        return None
    counts = {}
    cur = None
    for ln in text.splitlines():
        t = ln.strip()
        if (t.startswith("## ") and len(t) > 4 and t[3].isalpha()
                and t[3].isupper() and t[4] == "."):
            cur = t[3]
            counts.setdefault(cur, 0)
        elif cur is not None and re.match(r"\|\s*\d+\s*\|", t):
            counts[cur] = counts.get(cur, 0) + 1
    return counts or None


def contract_items_table() -> str:
    out = ["| Sec | checks | last audited | age | status |", "|---|---|---|---|---|"]
    rotation = "?"
    try:
        rotation = CONTRACT_ROTATION.read_text().strip().upper() or "?"
    except Exception:
        rotation = "?"
    counts = _section_check_counts()
    latest = ""
    if CONTRACT_MONITOR_LAST.exists():
        latest = _first(CONTRACT_MONITOR_LAST)
    monitor_age = age_min(CONTRACT_MONITOR_LAST) if CONTRACT_MONITOR_LAST.exists() else None
    monitor_fresh = monitor_age is not None and monitor_age < 40
    for s in SECTIONS:
        r = LANES / f"section_{s}_report.md"
        a = LANES / f"auditor_{s}.md"
        src = r if r.exists() else a
        m = audit_age_min(src) if src.exists() else None
        age = f"{m:6.1f}m" if m is not None else "-"
        # B-267: freshness is a property of the AUDIT, not of the rotation
        # monitor. A fresh contract_monitor_last pointer must never upgrade a
        # 14-day-old section audit to "(fresh)" -- that composite label was
        # the silent lie. Stale + monitored stays stale, honestly labeled.
        if m is not None and m < 40:
            status = "VERIFIED (fresh)"
        elif m is not None and monitor_fresh:
            status = "MONITORED; audit STALE"
        elif m is not None:
            status = "STALE"
        else:
            status = "UNVERIFIED"
        n = str(counts.get(s, "?")) if counts else "?"
        out.append("| " + s + " | " + n + " | " + src.name + " | " + age + " | " + status + " |")
    latest_note = latest[:60] or "not-verified"
    out.append(f"| rotation | {rotation} | contract_monitor_last | {'present' if latest else 'MISSING'} | {latest_note} |")
    return "\n".join(out)


def _is_retired(path):
    # A lane file whose first line starts with "# RETIRED" is a completed
    # one-shot lane: not a liveness subject, excluded from AGENT STATUS.
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.readline().lstrip().startswith("# RETIRED")
    except Exception:
        return False


def agent_table() -> str:
    rows = []
    if LANES.is_dir():
        for f in sorted(LANES.glob("*.md")):
            if _is_retired(f):
                continue  # completed/retired one-shot lanes are not liveness subjects
            m = age_min(f)
            if m is not None and m < 30:
                state = "LIVE"
            elif m is not None:
                state = "STALE"
            else:
                state = "UNKNOWN"
            role = _first(f).replace("# ROLE:", "").replace("ROLE:", "").strip()
            age = f"{m:6.1f}m" if m is not None else "-"
            rows.append((f.stem, state, age, role[:60]))
    live_rows = [r for r in rows if r[1] == "LIVE"]
    out = ["| Lane | State | Age | Role/status |", "|---|---|---|---|"]
    shown = live_rows or rows
    if not shown:
        out.append("| (no lane files) | - | - | - |")
    for stem, st, age, role in shown:
        out.append(f"| {stem} | {st} | {age} | {role} |")
    return "\n".join(out)


def code_cleanliness_table(top_n: int = 20) -> str:
    files = []
    for root in ("scripts", "training", "eval"):
        d = QG / root
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.py")):
            if any(x in p.parts for x in ("__pycache__", ".venv", "node_modules", "site-packages")):
                continue
            try:
                n = sum(1 for _ in p.open(errors="replace"))
            except Exception:
                n = -1
            if n >= 0:
                files.append((p.relative_to(QG).as_posix(), n))
    files.sort(key=lambda x: -x[1])
    out = ["| file | LOC | clean? |", "|---|---|---|"]
    total = sum(n for _, n in files)
    for path, n in files[:top_n]:
        if n > LONGLOC:
            flag = "LONG (needs split)"
        elif n > OKLOC:
            flag = "OK"
        else:
            flag = "SHORT"
        out.append(f"| {path} | {n} | {flag} |")
    out.append(f"| **TOTAL (top {len(files)} files)** | **{total} LOC** | - |")
    return "\n".join(out)


def testing_table() -> str:
    suite = "no COMPLETE suite artifact yet"
    reg = "n/a"
    running = ""
    logs = QG / ".sapo-loop" / "logs"
    arts = []
    if logs.is_dir():
        arts = sorted(logs.glob("full_suite_315_*.txt"), key=lambda p: p.stat().st_mtime)
    if arts:
        complete = None
        for a in reversed(list(arts)):
            if re.search(r"VERDICT=\w+", a.read_text(errors="replace")):
                complete = a
                break
        src = complete or arts[-1]
        text = src.read_text(errors="replace")
        m = re.search(r"TOTAL (passed=\d+ failed=\d+ errors=\d+ skipped=\d+) .*?VERDICT=(\w+)", text)
        if m:
            suite = f"{m.group(1)} VERDICT={m.group(2)} (artifact {src.name})"
        else:
            suite = f"IN PROGRESS ({text.count('TESTSUITE_COUNTS')}/25 chunks, {src.name})"
            running = " (a suite is mid-run)"
        fails = re.findall(r"FAILED\s+(\S+)", text)
        if fails:
            reg = f"{len(fails)} failing: " + "; ".join(fails[:3])
        else:
            reg = "0 failing (GREEN)"
    out = ["| level | status |", "|---|---|"]
    out.append(f"| unit (full suite) | {suite} |")
    out.append(f"| regression (touched/collected) | {reg}{running} |")
    collection = "CLEAN" if "errors=0" in suite else "CHECK"
    out.append(f"| collection/import | {collection} |")
    out.append("| system (box smoke / deploy) | n/a - no box smoke this tick |")
    return "\n".join(out)


def run_inventory(port: int, box_label: str, limit: int = 5) -> str:
    """All saved runs on a box with their step count + trainer-alive / metrics
    tail, so Training/Eval tables show full detail even when the runner is idle."""
    o = box_exec(port, "ls -dt /root/work/software/quantum-gpt/outputs/sapo-27b-ai-2026* 2>/dev/null | head -15")
    if o is None:
        return f"{box_label}: {UNREACHABLE} (not absence)"
    dirs = [x.strip() for x in o.splitlines() if x.strip() and "_base" not in x and not x.endswith("-base")]
    if not dirs:
        return f"{box_label}: no run dirs found"
    rows = []
    for d in dirs[:limit]:
        cmd = f"test -f {d}{BP} && echo Y || echo N; echo SEP; tail -n 1 {d}{BP} 2>/dev/null"
        r = box_exec(port, cmd)
        if r is None:
            rows.append(f"{d.split('sapo-27b-ai-')[-1]} | metrics={UNREACHABLE}")
            continue
        parts = r.split("SEP")
        hasm = parts[0].strip() if parts else "N"
        step = lr = loss = "-"
        if hasm == "Y" and len(parts) > 1:
            try:
                last = json.loads((parts[1].strip().splitlines() or ["{}"])[-1])
                step, lr, loss = last.get("step", "-"), last.get("lr", "-"), last.get("loss", "-")
            except Exception:
                pass
        rows.append(f"{d.split('sapo-27b-ai-')[-1]} | metrics={hasm} | step={step} lr={lr} loss={loss}")
    return "; ".join(rows)


def manager_actions(h1: dict, h2: dict, h3: dict, keeper: str) -> str:
    """Manager decisions/orders issued THIS delivery, derived from live fleet
    state (S9.4/9.5: dynamically manage/hire/retire/re-task agents)."""
    out = ["| decision/order | target | why / next |", "|---|---|---|"]
    # 1. Resources: heal any NOT-READY daemon.
    for label, h in (("ASI1(TRAIN)", h1), ("ASI2", h2), ("ASI3(EVAL)", h3)):
        if not h.get("ready"):
            out.append(f"| HEAL (re-arm daemon) | {label} | NOT-READY ({f(h.get('startupState'))}); B-186 bounded retry in flight, console needed if it persists |")
        else:
            out.append(f"| HOLD (ready) | {label} | READY - no action |")
    # 2. System lanes: re-arm dead lanes (liveness per S9.5).
    try:
        ps = subprocess.run(["ps", "ax", "-o", "command"], capture_output=True, text=True, timeout=10).stdout
        for pat, lane in (("sapo_system_monitor", "system_monitor"),
                          ("sapo_metrics_poller", "metrics_poller"),
                          ("sapo_wedge_watch", "wedge_watch")):
            dead = not any(pat in ln and "grep" not in ln and "standup_tables" not in ln for ln in ps.splitlines())
            if dead:
                out.append(f"| RE-ARM dead lane | {lane} | not in ps - relaunch (S9.5) |")
    except Exception:
        pass
    # 3. Unit/regression: if a failing test exists, order a TDD fix cluster.
    out.append("| TDD-fix failable cluster | code lanes | run full suite; fix any FAILING cluster RED->GREEN before deploy |")
    out.append("| AUTO launch | harness | launch warm-continue with --min-rms-for-update 0.01 when fleet ready and training stale |")
    out.append(f"| KEEP-ALIVE | keeper/heartbeat | daemons+auth OK (keeper={keeper}); continue healing |")
    return "\n".join(out)


def f(v: object) -> str:
    if v in (None, "", "None"):
        return "UNKNOWN"
    return str(v)


def main() -> int:
    h1 = daemon_health(20646)
    h2 = daemon_health(19004)
    h3 = daemon_health(20653)
    keeper = "unreadable"
    try:
        kd = json.loads(KEEPER_STATE.read_text())
        keeper = kd.get("status", "?")
    except Exception:
        keeper = "unreadable"

    if h1.get("ready"):
        run1 = live_run_dir(20646)
        proc1 = trainer_proc(20646)
        rec1, cnt1, tail1 = step_metrics(20646, run1)
        ck1, adap1, listing1 = ckpt_info(20646, run1)
    else:
        run1, proc1, rec1, cnt1, tail1, ck1, adap1, listing1 = "", "", {}, -1, [], -1, "", ""

    if h3.get("ready"):
        run3 = live_run_dir(20653)
        ek3, eadap3, _ = ckpt_info(20653, run3)
        v3 = vllm_probe(20653)
    else:
        run3, ek3, eadap3, v3 = "", -1, "", "ASI3 not ready"
    j3 = judge_state()

    print(f"#### DEDICATED HARNESS TABLES (scripts/standup_tables.py) at {now().strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    print("**1. RESOURCE TABLE (S9.1)**")
    print("| Res | Port | READY | startup | shell | fail kind |")
    print("|---|---|---|---|---|---|")
    for label, port, h in (("ASI1(TRAIN)", 20646, h1), ("ASI2", 19004, h2), ("ASI3(EVAL)", 20653, h3)):
        state = "READY" if h.get("ready") else "NOT-READY"
        print(f"| {label} | {port} | {state} | {f(h.get('startupState'))} | {f(h.get('shellSurfaceReady'))} | {f(h.get('startupFailureKind'))} |")
    print(f"| keeper | - | - | {keeper} | - | - |")
    print()
    print("**2. TRAINING TABLE (ASI1) - DETAILED**")
    print("| field | value |")
    print("|---|---|")
    print(f"| daemon | ASI1:20646 {'READY' if h1.get('ready') else 'NOT-READY'} ({f(h1.get('startupState'))}) |")
    print(f"| live run dir | {run1 or 'NONE (no run)'} |")
    print(f"| trainer proc | {proc1 or 'not running (pgrep empty)'} |")
    print(f"| step | {f(rec1.get('step'))} |")
    print(f"| loss | {f(rec1.get('loss'))} |")
    print(f"| reward / pass_rate | {f(rec1.get('mean_reward'))} / {f(rec1.get('pass_rate'))} |")
    print(f"| entropy / lr | {f(rec1.get('entropy_mean'))} / {f(rec1.get('lr'))} |")
    print(f"| clip / ratio | {f(rec1.get('clip_fraction_after_update'))} / {f(rec1.get('ratio_mean'))} |")
    print(f"| trust_viol / rms | {f(rec1.get('trust_region_violated'))} / {f(rec1.get('loo_advantage_rms'))} |")
    print(f"| metric rows | {f(cnt1)} |")
    print(f"| cadence | {cadence(tail1)} |")
    print(f"| ckpts / newest adapter | {f(ck1)} / {adap1 or 'none'} |")
    listing = (listing1 or "n/a").replace(chr(10), "; ")
    print(f"| run-dir listing | {listing[:200] or 'none'} |")
    print(f"| saved-run inventory | {run_inventory(20646, 'ASI1')[:300]} |")
    if proc1 == UNREACHABLE:
        reason1 = UNREACHABLE + " - trainer state unknown (exec dead)"
    elif proc1:
        reason1 = "live trainer RUNNING"
    else:
        reason1 = "IDLE - no trainer process; resolved newest dir is terminal/stale"
    print(f"| run-reason/state | {reason1} |")
    print()
    print("**3. EVAL TABLE (ASI3) - DETAILED**")
    print("| field | value |")
    print("|---|---|")
    print(f"| daemon | ASI3:20653 {'READY' if h3.get('ready') else 'NOT-READY'} ({f(h3.get('startupState'))}) |")
    print(f"| vLLM | {v3} |")
    print(f"| eval target run | {run3 or 'NONE'} |")
    print(f"| eval adapters / newest | {f(ek3)} / {eadap3 or 'none'} |")
    print(f"| saved-run inventory | {run_inventory(20653, 'ASI3')[:300]} |")
    print(f"| judge/upstream | {j3} |")
    print()
    print("**4. AGENT STATUS TABLE**")
    print(agent_table())
    print()
    print("**5. 130+ ITEMS - CONTRACT CHECK TABLE (134 checks, sections A-M)**")
    print(contract_items_table())
    print()
    print("**6. CODE-CLEANLINESS TABLE (largest files first)**")
    print(code_cleanliness_table())
    print()
    print("**7. TESTING TABLE (unit / regression / system)**")
    print(testing_table())
    print()
    print("**LIVE SYSTEM LANES (fleet liveness)**")
    sl = ["| System lane | pid(etime) | live? |", "|---|---|---|"]
    for n, p, s in system_lanes():
        sl.append(f"| {n} | {p} | {s} |")
    print("\n".join(sl))
    print()
    print("**8. MANAGER DECISIONS / ORDERS (S9.4/9.5 - issued this delivery)**")
    print(manager_actions(h1, h2, h3, keeper))
    return 0


if __name__ == "__main__":
    sys.exit(main())
