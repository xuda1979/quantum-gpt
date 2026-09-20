"""Work review + productivity + system health for harness standup reports."""

from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from pathlib import Path


def _repo_root():
    return Path(os.environ.get("QGH_REPO", Path(__file__).resolve().parent.parent))


def _state_dir():
    return Path(os.environ.get("QGH_STATE_DIR", _repo_root() / "harness" / "state"))


def _run(cmd, cwd=None, timeout=10):
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, cwd=cwd or str(_repo_root()), timeout=timeout
        )
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def _fleet_health():
    boxes = {"ASI1": 20646, "ASI2": 19004, "ASI3": 20653}
    results = {}
    for name, port in boxes.items():
        try:
            r = urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=3)
            d = json.loads(r.read())
            results[name] = {
                "ready": d.get("ready"),
                "state": d.get("startupState"),
                "uptime": d.get("uptime"),
                "busy": d.get("busy"),
                "cmd": d.get("commandCount"),
            }
        except Exception:
            results[name] = {
                "ready": False,
                "state": "UNREACHABLE",
                "uptime": 0,
                "busy": False,
                "cmd": 0,
            }
    return results


def _keeper_status():
    try:
        return json.loads(Path("/tmp/session_keeper_state.json").read_text())
    except Exception:
        return {"status": "MISSING"}


def _system_load():
    return _run(["uptime"])


def _worker_count():
    try:
        r = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
        return sum(
            1
            for l in r.stdout.splitlines()
            if "claude" in l and "cmri" in l and "GLM" in l and "--print" in l and "grep" not in l
        )
    except Exception:
        return 0


def _training_status():
    status = {"running": False, "step": None, "reward": None, "last_run": None, "verdict": None}
    try:
        r = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
        for line in r.stdout.splitlines():
            if "grpo_trainer" in line and "grep" not in line:
                status["running"] = True
                break
    except Exception:
        pass
    repo = _repo_root()
    metrics_files = sorted(
        repo.glob("outputs/*/grpo_step_metrics.jsonl"), key=os.path.getmtime, reverse=True
    )
    if metrics_files:
        status["last_run"] = metrics_files[0].parent.name
        try:
            lines = metrics_files[0].read_text(errors="replace").strip().splitlines()
            if lines:
                last = json.loads(lines[-1])
                status["step"] = last.get("step")
                status["reward"] = last.get("mean_reward") or last.get("reward_mean")
        except Exception:
            pass
    for vf in sorted(repo.glob("outputs/*verdict*.json"), key=os.path.getmtime, reverse=True):
        try:
            d = json.loads(vf.read_text())
            status["verdict"] = {
                "file": vf.name,
                "pass_adapter": d.get("pass_adapter", d.get("adapter_pass")),
                "pass_base": d.get("pass_base", d.get("base_pass")),
                "beats_base": d.get("beats_base"),
                "superseded": d.get("superseded", False),
                "gains": d.get("gains", []),
                "losses": d.get("losses", []),
            }
            break
        except Exception:
            pass
    return status


def _suite_status():
    repo = _repo_root()
    logs = repo / ".sapo-loop" / "logs"
    if not logs.exists():
        return {"status": "no logs dir"}
    files = sorted(logs.glob("full_suite_315_*.txt"), key=os.path.getmtime, reverse=True)
    if not files:
        return {"status": "no suite runs"}
    content = files[0].read_text(errors="replace")
    chunks = [l for l in content.splitlines() if "TESTSUITE_COUNTS" in l]
    total_line = [l for l in content.splitlines() if l.startswith("TOTAL")]
    if total_line:
        return {"status": "COMPLETE", "result": total_line[0][:150]}
    if chunks:
        tp = sum(int(c.split("passed=")[1].split()[0]) for c in chunks)
        tf = sum(int(c.split("failed=")[1].split()[0]) for c in chunks)
        return {"status": "RUNNING", "chunks": len(chunks), "passed": tp, "failed": tf}
    return {"status": "STARTED"}


def _events_analysis():
    ef = _state_dir() / "EVENTS.jsonl"
    done = bounce = dispatch = fail = 0
    if ef.exists():
        for line in ef.read_text(errors="replace").splitlines()[-200:]:
            try:
                ev = json.loads(line)
                k = ev.get("kind", "")
                if k == "dispatched":
                    dispatch += 1
                elif k == "done":
                    done += 1
                elif k == "bounce":
                    bounce += 1
                elif "fail" in k or "dead" in k:
                    fail += 1
            except Exception:
                pass
    return {"dispatch": dispatch, "done": done, "bounce": bounce, "fail": fail}


def render_work_review(state_dir=None, repo_root=None):
    repo = Path(repo_root) if repo_root else _repo_root()
    Path(state_dir) if state_dir else _state_dir()
    L = []

    # === SYSTEM HEALTH ===
    L.append("### SYSTEM HEALTH")
    fleet = _fleet_health()
    ready_count = sum(1 for v in fleet.values() if v.get("ready"))
    for name in ["ASI1", "ASI2", "ASI3"]:
        v = fleet.get(name, {})
        ut = v.get("uptime", 0)
        L.append(
            f"- {name}: ready={v.get('ready')} state={v.get('state')} uptime={ut}s ({ut // 60}min) busy={v.get('busy')} cmd={v.get('cmd')}"
        )
    L.append(f"- Fleet: {ready_count}/3 ready")
    keeper = _keeper_status()
    L.append(
        f"- Keeper: status={keeper.get('status')} auth={keeper.get('headless_auth')} daemons={keeper.get('daemons')}"
    )
    load = _system_load()
    if load:
        L.append(f"- System: {load}")
    workers = _worker_count()
    L.append(f"- Workers: {workers} alive (cmri GLM-5.2)")
    L.append("")

    # === TRAINING STATUS ===
    L.append("### TRAINING STATUS")
    ts = _training_status()
    if ts.get("running"):
        L.append(f"- Status: RUNNING (step={ts.get('step')} reward={ts.get('reward')})")
    else:
        L.append("- Status: NOT RUNNING")
    if ts.get("last_run"):
        L.append(
            f"- Last run: {ts.get('last_run')} (step={ts.get('step')} reward={ts.get('reward')})"
        )
    v = ts.get("verdict")
    if v:
        L.append(
            f"- Last verdict: {v.get('file')} adapter={v.get('pass_adapter')} base={v.get('pass_base')} beats_base={v.get('beats_base')} superseded={v.get('superseded')}"
        )
        if v.get("gains"):
            L.append(f"- Gains: {v.get('gains')}")
        if v.get("losses"):
            L.append(f"- Losses: {v.get('losses')}")
    L.append("")

    # === EVAL STATUS ===
    L.append("### EVAL STATUS (path to 18/18)")
    v = ts.get("verdict") if ts.get("verdict") else None
    if v:
        pa = v.get("pass_adapter", "?")
        try:
            pa_num = int(str(pa).split("/")[0])
            L.append(f"- Current: adapter {pa}/18 vs base {v.get('pass_base')}/18")
            L.append(f"- Need: {18 - pa_num} more task passes to reach 18/18")
        except Exception:
            L.append(f"- Current: adapter={pa} base={v.get('pass_base')}")
        if v.get("superseded"):
            L.append("- WARNING: verdict is SUPERSEDED — need canonical re-run with SHA pins")
    else:
        L.append("- No verdicts found")
    L.append("")

    # === PRODUCTIVITY ===
    L.append("### PRODUCTIVITY")
    ev = _events_analysis()
    total = ev["dispatch"] + ev["done"] + ev["bounce"] + ev["fail"]
    waste = f"{(ev['bounce'] + ev['fail']) * 100 // total}%" if total > 0 else "?"
    L.append(
        f"- Dispatched: {ev['dispatch']} | Done: {ev['done']} | Bounce: {ev['bounce']} | Fail: {ev['fail']} | Waste: {waste}"
    )
    if ev["dispatch"] > 0 and ev["done"] == 0:
        L.append("- CRITICAL: 0% completion rate — workers are not producing results")
    elif ev["dispatch"] > 0 and ev["done"] < ev["dispatch"] // 2:
        L.append(f"- WARNING: low completion ({ev['done'] * 100 // ev['dispatch']}%)")
    L.append("")

    # === WORK REVIEW ===
    L.append("### RECENT COMMITS (last 5)")
    commits = _run(["git", "log", "--oneline", "-5"], cwd=str(repo)).splitlines()
    for c in commits:
        L.append(f"- {c}")
    if not commits:
        L.append("- (none)")
    L.append("")

    # === TEST SUITE ===
    L.append("### TEST SUITE")
    suite = _suite_status()
    if suite.get("status") == "COMPLETE":
        L.append(f"- Status: COMPLETE — {suite.get('result')}")
    elif suite.get("status") == "RUNNING":
        L.append(
            f"- Status: RUNNING — {suite.get('chunks')}/27 chunks, {suite.get('passed')}P/{suite.get('failed')}F"
        )
    else:
        L.append(f"- Status: {suite.get('status')}")
    L.append("")

    # === CRITICAL SELF-REVIEW ===
    L.append("### CRITICAL SELF-REVIEW")
    issues = []
    if ready_count < 3:
        issues.append(f"Fleet degraded: only {ready_count}/3 boxes ready")
    if keeper.get("headless_auth") == "failed":
        issues.append("Keeper auth failed — may affect daemon management")
    if not ts.get("running"):
        issues.append("Training NOT RUNNING — no progress toward 18/18")
    if v and v.get("superseded"):
        issues.append("Latest verdict SUPERSEDED — need canonical eval")
    if ev["dispatch"] > 0 and ev["done"] == 0:
        issues.append("0% worker completion — workers not producing")
    if workers == 0:
        issues.append("No workers alive")
    if not issues:
        issues.append("All systems nominal")
    for issue in issues:
        L.append(f"- {issue}")
    L.append("")

    # === NEXT ACTIONS ===
    L.append("### NEXT ACTIONS")
    if not ts.get("running"):
        L.append("- Launch warm-continue training with --min-rms-for-update 0.01")
    if v and v.get("superseded"):
        L.append("- Run canonical 18-task eval with SHA-pinned scorer")
    if ev["dispatch"] > 0 and ev["done"] == 0:
        L.append("- Fix worker completion: verify API access, check worker logs")
    if not issues or issues == ["All systems nominal"]:
        L.append("- Proceed with next training/eval leg")
    L.append("")
    return chr(10).join(L)
