"""Work review + productivity analysis for harness standup reports."""
from __future__ import annotations
import json, os, subprocess
from pathlib import Path

def _repo_root():
    return Path(os.environ.get("QGH_REPO", Path(__file__).resolve().parent.parent))

def _state_dir():
    return Path(os.environ.get("QGH_STATE_DIR", _repo_root() / "harness" / "state"))

def _run(cmd, cwd=None, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or str(_repo_root()), timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""

def render_work_review(state_dir=None, repo_root=None):
    repo = Path(repo_root) if repo_root else _repo_root()
    sd = Path(state_dir) if state_dir else _state_dir()
    L = []
    L.append("### RECENT COMMITS (last 5)")
    commits = _run(["git", "log", "--oneline", "-5"], cwd=str(repo)).splitlines()
    for c in commits: L.append(f"- {c}")
    if not commits: L.append("- (none)")
    L.append("")
    ef = sd / "EVENTS.jsonl"
    done = bounce = dispatch = fail = 0
    if ef.exists():
        for line in ef.read_text(errors="replace").splitlines()[-200:]:
            try:
                ev = json.loads(line)
                k = ev.get("kind", "")
                if k == "dispatched": dispatch += 1
                elif k == "done": done += 1
                elif k == "bounce": bounce += 1
                elif "fail" in k or "dead" in k: fail += 1
            except Exception: pass
    total = dispatch + done + bounce + fail
    waste = f"{(bounce + fail) * 100 // total}%" if total > 0 else "?"
    L.append("### PRODUCTIVITY (last 200 events)")
    L.append(f"- Dispatched: {dispatch} | Done: {done} | Bounce: {bounce} | Fail: {fail} | Waste: {waste}")
    if dispatch > 0 and done == 0:
        L.append("- WARNING: 0% completion rate - workers are dying. Check API access.")
    elif dispatch > 0 and done < dispatch // 2:
        L.append(f"- WARNING: low completion rate ({done * 100 // dispatch}%) - investigate worker deaths")
    L.append("")
    # SUITE STATUS
    logs = repo / ".sapo-loop" / "logs"
    suite_files = sorted(logs.glob("full_suite_315_*.txt"), key=os.path.getmtime, reverse=True) if logs.exists() else []
    if suite_files:
        latest = suite_files[0]
        content = latest.read_text(errors="replace")
        chunks = [l for l in content.splitlines() if "TESTSUITE_COUNTS" in l]
        total_line = [l for l in content.splitlines() if l.startswith("TOTAL")]
        if total_line:
            L.append(f"### TEST SUITE: COMPLETE - {total_line[0][:120]}")
        elif chunks:
            tp = sum(int(c.split("passed=")[1].split()[0]) for c in chunks)
            tf = sum(int(c.split("failed=")[1].split()[0]) for c in chunks)
            L.append(f"### TEST SUITE: RUNNING - {len(chunks)}/27 chunks, {tp}P/{tf}F so far")
        else:
            L.append("### TEST SUITE: STARTED (no results yet)")
    else:
        L.append("### TEST SUITE: not running")
    L.append("")
    # VERDICT STATUS
    outputs = repo / "outputs"
    verdicts = []
    if outputs.exists():
        for vf in sorted(outputs.glob("*verdict*.json"), key=os.path.getmtime, reverse=True):
            try:
                d = json.loads(vf.read_text())
                verdicts.append(d)
            except Exception: pass
            if len(verdicts) >= 3: break
    L.append("### EVAL VERDICT")
    if verdicts:
        v = verdicts[0]
        pa = v.get("pass_adapter", v.get("adapter_pass", "?"))
        pb = v.get("pass_base", v.get("base_pass", "?"))
        bb = v.get("beats_base", v.get("verdict", "?"))
        sup = v.get("superseded", False)
        gains = v.get("gains", [])
        L.append(f"- Latest: adapter={pa} base={pb} beats_base={bb} superseded={sup}")
        if gains: L.append(f"- Gains: {gains}")
        try:
            pa_num = int(str(pa).split("/")[0])
            L.append(f"- Path to 18/18: need {18 - pa_num} more task passes")
        except Exception:
            L.append(f"- Path to 18/18: adapter pass count unclear ({pa})")
    else:
        L.append("- No verdicts found")
    L.append("")
    # BLOCKERS
    L.append("### BLOCKERS")
    blockers = []
    if verdicts:
        v = verdicts[0]
        if v.get("superseded"): blockers.append("verdicts superseded - need canonical eval with SHA pins")
        if v.get("sha_pin_violation"): blockers.append(f"sha_pin: {v.get(chr(115)+chr(104)+chr(97)+chr(95)+chr(112)+chr(105)+chr(110)+chr(95)+chr(118)+chr(105)+chr(111)+chr(108)+chr(97)+chr(116)+chr(105)+chr(111)+chr(110))}")
    if dispatch > 0 and done == 0: blockers.append("workers dying - API access issue")
    if not blockers: blockers.append("none - ready to proceed")
    for b in blockers: L.append(f"- {b}")
    L.append("")
    # IMPROVEMENT OPPORTUNITIES
    L.append("### PRODUCTIVITY IMPROVEMENT")
    if dispatch > 0 and done == 0:
        L.append("- CRITICAL: 0% completion - fix worker API access first")
    elif waste != "?" and int(waste.rstrip(chr(37))) > 50:
        L.append(f"- HIGH WASTE ({waste}) - reduce bounce/fail rate")
    if not blockers or blockers == ["none - ready to proceed"]:
        L.append("- Launch warm-continue training to improve adapter")
        L.append("- Run canonical 18-task eval to get SHA-pinned verdict")
    L.append("")
    return chr(10).join(L)
