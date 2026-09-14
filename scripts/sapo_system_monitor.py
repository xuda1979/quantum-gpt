#!/usr/bin/env python3
"""sapo_system_monitor.py — durable small monitor for the live SAPO training +
eval. Polls every `scan` seconds and writes a status line + LOUD alerts to
logs/sapo_system_monitor.log, so the FIRST sign of a failure class is caught
early (lr-bleed, entropy, stall, checkpoint stagnation, eval verdicts).

Probes the training container (20653) and eval container (19004) over the
daemon /exec transport. Session-independent: run with nohup.

Usage: nohup python3 scripts/sapo_system_monitor.py [scan_s] >/dev/null 2>&1 &
"""
import argparse, json, os, re, time, urllib.request

RUN = "/root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260913T233607Z"
BP = RUN + "/grpo_step_metrics.jsonl"
TRAIN, EVAL = "20653", "19004"
CFG_LR = 2.5e-05
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs", "sapo_system_monitor.log")


def post(port, cmd, timeout=90):
    payload = json.dumps({"command": cmd}).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{port}/exec", data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            o = r.read().decode("utf-8", "replace")
        d = json.loads(o)
        return (d.get("output", d) if not isinstance(d.get("output"), dict)
                else d["output"].get("output", ""))
    except Exception as e:
        return f"__ERR__{e}"


def last_step():
    """Return dict with step/lr/entropy/rew/viol or None on probe failure."""
    cmd = ("python3 -c \"import json; lines=[l for l in open('" + BP +
           "') if l.strip()]; d=json.loads(lines[-1]); print(json.dumps({"
           "'step':d.get('step'),'lr':d.get('lr'),'entropy':d.get('entropy_mean'),"
           "'rew':d.get('mean_reward'),'viol':d.get('trust_region_violation_count')"
           "}))\"")
    out = post(TRAIN, cmd).strip()
    if out.startswith("__ERR__"):
        return None
    try:
        return json.loads(out.splitlines()[-1])
    except Exception:
        return None


def ckpt_count():
    try:
        return int(post(TRAIN, f"ls -d {RUN}/step_*_adapter 2>/dev/null | wc -l").strip().splitlines()[-1])
    except Exception:
        return -1


def eval_status():
    o = post(EVAL, "ps -eo args --no-headers | grep -F run_asi2_base_adapter_rubric_eval | grep -v grep | head -1")
    scoring = ""
    if "rubric_eval" in o:
        m = re.search(r"--adapter\s+\S+/(step_\d+_adapter)", o)
        scoring = f" scoring={m.group(1) if m else '(?)'}"
    done = post(EVAL, "ls -t /root/work/software/quantum-gpt/outputs/reeval_latest_*.json 2>/dev/null | head -4")
    sl = [b.split("/")[-1].replace("reeval_latest_", "s").replace("reeval_", "")
          for b in done.strip().splitlines()[:4]]
    return "eval:[%s]%s" % (",".join(sl), scoring)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("scan", nargs="?", type=int, default=120)
    scan = ap.parse_args().scan
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    last_ck = -1
    while True:
        try:
            st = last_step(); ck = ckpt_count()
            alerts = []
            if st and st.get("lr") is not None and st["lr"] < CFG_LR:
                alerts.append(f"LR_BLEED lr={st['lr']}<cfg{CFG_LR}")
            if st and st.get("viol"):
                alerts.append(f"TRUST_VIOL x{st['viol']}")
            if ck > last_ck:
                last_ck = ck
            line = (f"{time.strftime('%H:%M:%SZ', time.gmtime())} step={st and st.get('step')} "
                    f"lr={st and st.get('lr')} ent={st and st.get('entropy')} ckpts={ck} "
                    f"{eval_status()}" + (" | ALERT " + "; ".join(alerts) if alerts else ""))
            with open(LOG, "a") as f:
                f.write(line + "\n")
        except Exception as e:
            with open(LOG, "a") as f:
                f.write(f"{time.strftime('%H:%M:%SZ', time.gmtime())} MONITOR_ERR {e}\n")
        time.sleep(scan)


if __name__ == "__main__":
    main()
