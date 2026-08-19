#!/usr/bin/env python3
"""Structured logging + trend reporting for ASI2 RL training rounds.

PURPOSE
-------
Give every RL round a single machine+human-readable record so we can, at any
moment, tell whether the model is improving and quickly spot bugs.

Two artifacts are maintained at the repo root (next to this script's parent):

  training_rl_registry.jsonl   -- one JSON object per round (append / upsert)
  reports/rl_training_rounds.md -- rendered human trend report (is it improving?)

USAGE
-----
  # Append/upsert a round from its ASI2 output dir (reads run_config + metrics):
  python3 scripts/rl_round_logger.py record \
      --round  grpo-27b-selfeval-20260818T072721 \
      --out-dir /root/work/software/quantum-gpt/outputs/grpo-27b-selfeval-20260818T072721 \
      [--eval-json outputs/reeval_latest_...json] \
      [--verdict noop] [--note "..."]

  # Regenerate the human trend report (and a JSON summary) from the registry:
  python3 scripts/rl_round_logger.py report

  # Print the registry (compact, chronological):
  python3 scripts/rl_round_logger.py list
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "training_rl_registry.jsonl"
REPORT_MD = ROOT / "reports" / "rl_training_rounds.md"
REPORT_JSON = ROOT / "reports" / "rl_training_rounds.json"


def now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _read_registry() -> list[dict]:
    if not REGISTRY.exists():
        return []
    rows = []
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"[warn] skipping malformed registry line: {e}", file=sys.stderr)
    return rows


def _write_registry(rows: list[dict]) -> None:
    rows.sort(key=lambda r: r.get("round", ""))
    with REGISTRY.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")


def _load_metrics(out_dir: Path) -> dict:
    """Summarize grpo_step_metrics.jsonl into compact round stats."""
    mfile = out_dir / "grpo_step_metrics.jsonl"
    stat = {
        "steps": 0,
        "first_ts": None,
        "last_ts": None,
        "mean_reward_first": None,
        "mean_reward_last": None,
        "max_pass_rate": None,
        "last_pass_rate": None,
        "final_loss": None,
        "seq_kl_last": None,
        "clip_high_mean": None,
        "entropy_last": None,
        "breaker_trips": [],
        "last_best_code": None,
    }
    if not mfile.exists():
        return stat
    steps = []
    for line in mfile.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            steps.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not steps:
        return stat
    stat["steps"] = len(steps)
    ts = [s.get("timestamp_utc") for s in steps if s.get("timestamp_utc")]
    stat["first_ts"] = ts[0] if ts else None
    stat["last_ts"] = ts[-1] if ts else None
    stat["mean_reward_first"] = steps[0].get("mean_reward")
    stat["mean_reward_last"] = steps[-1].get("mean_reward")
    pr = [s.get("pass_rate", 0) or 0 for s in steps]
    stat["max_pass_rate"] = max(pr) if pr else None
    stat["last_pass_rate"] = pr[-1] if pr else None
    losses = [s.get("loss") for s in steps if s.get("loss") is not None]
    stat["final_loss"] = losses[-1] if losses else None
    sk = [s.get("seq_kl") for s in steps if s.get("seq_kl") is not None]
    stat["seq_kl_last"] = sk[-1] if sk else None
    ch = [s.get("clip_high_fraction", 0) or 0 for s in steps]
    stat["clip_high_mean"] = (sum(ch) / len(ch)) if ch else None
    ent = [s.get("entropy_mean") for s in steps if s.get("entropy_mean") is not None]
    stat["entropy_last"] = ent[-1] if ent else None
    trips = set()
    for s in steps:
        for t in s.get("breaker_trips", []) or []:
            trips.add(t.get("breaker", "unknown"))
    stat["breaker_trips"] = sorted(trips)
    return stat


def _load_config(out_dir: Path) -> dict:
    cfg = out_dir / "run_config.json"
    if not cfg.exists():
        return {}
    try:
        return json.loads(cfg.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_eval_summary(eval_json: str | None) -> dict:
    """Extract base vs adapter pass@1 / rubric / heldout CE from an eval result."""
    if not eval_json:
        return {}
    p = Path(eval_json)
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        s = d.get("summary", {})
        h = d.get("heldout_sft_eval", {})
        return {
            "eval_source": str(p),
            "eval_created_at": d.get("created_at_utc"),
            "base": {
                "pass_at_1": s.get("base", {}).get("pass_at_1"),
                "overall": s.get("base", {}).get("scores", {}).get("overall"),
                "heldout_loss": h.get("base", {}).get("loss"),
            },
            "adapter": {
                "pass_at_1": s.get("adapter", {}).get("pass_at_1"),
                "overall": s.get("adapter", {}).get("scores", {}).get("overall"),
                "heldout_loss": h.get("adapter", {}).get("loss"),
            },
        }
    except Exception:
        return {}


def _verdict(eval_sum: dict, stats: dict) -> str:
    """Classify round effectiveness from eval + training signal."""
    b, a = eval_sum.get("base", {}), eval_sum.get("adapter", {})
    if b and a:
        same_p = b.get("pass_at_1") == a.get("pass_at_1")
        same_o = round(b.get("overall", 0) or 0, 4) == round(a.get("overall", 0) or 0, 4)
        if same_p and same_o:
            return "NO_OP (adapter==base)"
        try:
            bp = int(str(b.get("pass_at_1", "0")).split("/")[0])
            ap = int(str(a.get("pass_at_1", "0")).split("/")[0])
        except Exception:
            bp = ap = None
        if bp is not None and ap is not None:
            if ap > bp:
                return "IMPROVED"
            if ap < bp:
                return "REGRESSED"
        # pass equal but rubric moved
        bo = b.get("overall", 0) or 0
        ao = a.get("overall", 0) or 0
        if ao > bo + 0.01:
            return "IMPROVED(rubric)"
        if ao < bo - 0.01:
            return "REGRESSED(rubric)"
        return "NO_OP (adapter==base)"
    # no eval yet
    fl = stats.get("final_loss")
    if stats.get("steps", 0) >= 10 and fl is not None and abs(fl or 0) < 1e-4:
        return "PENDING-EVAL (tiny-loss risk)"
    return "PENDING-EVAL"


def cmd_record(args) -> int:
    out_dir = Path(args.out_dir)
    stats = _load_metrics(out_dir)
    config = _load_config(out_dir)
    eval_sum = _load_eval_summary(args.eval_json)
    verdict = args.verdict if args.verdict else _verdict(eval_sum, stats)

    round_id = args.round or out_dir.name
    rec = {
        "round": round_id,
        "recorded_utc": now_utc(),
        "run_dirs": [str(out_dir)],
        "output_dir": str(out_dir),
        "adapter_dir": str(out_dir / "adapter"),
        "has_adapter": (out_dir / "adapter").is_dir(),
        "config": {
            "grpo_steps": config.get("grpo_steps"),
            "lr": config.get("lr"),
            "loss_mode": config.get("loss_mode"),
            "gspo_clip_low": config.get("gspo_clip_low"),
            "gspo_clip_high": config.get("gspo_clip_high"),
            "group_size": config.get("group_size"),
            "max_adaptive_group": config.get("max_adaptive_group"),
            "kl_coeff": config.get("kl_coeff"),
            "inner_epochs": config.get("inner_epochs"),
            "repair_converted_jsonl": config.get("repair_converted_jsonl"),
            "circuit_breaker_window": config.get("circuit_breaker_window"),
        },
        "metrics": stats,
        "eval": eval_sum,
        "verdict": verdict,
        "note": args.note,
    }

    rows = [r for r in _read_registry() if r.get("round") != round_id]
    rows.append(rec)
    _write_registry(rows)
    print(json.dumps(rec, indent=2))
    return 0


def _fmt(x, nd=4):
    if x is None:
        return "—"
    if isinstance(x, bool):
        return str(x)
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x)


def cmd_report(args) -> int:
    rows = _read_registry()
    rows.sort(key=lambda r: r.get("round", ""))
    lines = []
    lines.append("# RL Training Rounds — Performance & Health Log (ASI2)\n")
    lines.append(f"_Auto-generated by `scripts/rl_round_logger.py report` — {now_utc()} UTC._\n")
    lines.append(
        "Each row = one training round. `adapter vs base` eval = same held-out 12 tasks "
        "(8 quantum + 4 software). A healthy round must (a) run, and (b) make the adapter "
        "**differ from and beat** base. `NO_OP` = adapter functionally equals base (bug / "
        "ineffective signal — investigate before continuing).\n"
    )
    lines.append(
        "| round | steps | end(UTC) | rew↑ | maxP@1 | final loss | seq_kl | clipH | adapter | base P@1 | ada P@1 | base CE | ada CE | verdict |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        m = r.get("metrics", {})
        e = r.get("eval", {})
        b, a = e.get("base", {}), e.get("adapter", {})
        c = r.get("config", {})
        clip = ""
        if c.get("gspo_clip_low") is not None:
            clip = f"{_fmt(c.get('gspo_clip_low'),4)}/{_fmt(c.get('gspo_clip_high'),4)}"
        lines.append(
            "| {round} | {steps} | {ts} | {rw} | {mpr} | {loss} | {sk} | {clip} | {ad} | {bp} | {ap} | {bc} | {ac} | {v} |".format(
                round=r["round"].replace("grpo-27b-selfeval-", "gs-"),
                steps=m.get("steps", "—"),
                ts=(m.get("last_ts") or "")[11:19] if m.get("last_ts") else "—",
                rw=_fmt(m.get("mean_reward_last")),
                mpr=_fmt(m.get("max_pass_rate"), 3),
                loss=_fmt(m.get("final_loss"), 6),
                sk=_fmt(m.get("seq_kl_last")),
                clip=clip or "—",
                ad="Y" if r.get("has_adapter") else "n",
                bp=_fmt(b.get("pass_at_1"), 0) if b else "—",
                ap=_fmt(a.get("pass_at_1"), 0) if a else "—",
                bc=_fmt(b.get("heldout_loss"), 5) if b else "—",
                ac=_fmt(a.get("heldout_loss"), 5) if a else "—",
                v=r.get("verdict", "—"),
            )
        )
    lines.append("")
    # Detailed per-round notes
    lines.append("## Per-round detail\n")
    for r in rows:
        m = r.get("metrics", {})
        e = r.get("eval", {})
        c = r.get("config", {})
        lines.append(f"### {r['round']}  `{r.get('verdict')}`")
        lines.append(f"- recorded: {r.get('recorded_utc')}")
        lines.append(
            f"- steps: {m.get('steps')} (first {m.get('first_ts')} → last {m.get('last_ts')})"
        )
        lines.append(
            f"- mean_reward: {_fmt(m.get('mean_reward_first'))} → {_fmt(m.get('mean_reward_last'))}; max_pass_rate {_fmt(m.get('max_pass_rate'),3)}; entropy_last {_fmt(m.get('entropy_last'),2)}"
        )
        lines.append(
            f"- final_loss: {_fmt(m.get('final_loss'),6)}; seq_kl_last: {_fmt(m.get('seq_kl_last'))}; clip_high_mean: {_fmt(m.get('clip_high_mean'),3)}"
        )
        lines.append(f"- breaker_trips: {m.get('breaker_trips') or 'none'}")
        blew = []
        for k, v in c.items():
            if v is not None:
                blew.append(f"{k}={v}")
        lines.append(f"- config: {', '.join(blew) if blew else '—'}")
        if e:
            b, a = e.get("base", {}), e.get("adapter", {})
            lines.append(
                f"- eval({e.get('eval_source','')}): base P@1 {b.get('pass_at_1')} / ada P@1 {a.get('pass_at_1')}; base CE {_fmt(b.get('heldout_loss'),5)} / ada CE {_fmt(a.get('heldout_loss'),5)}"
            )
        if r.get("note"):
            lines.append(f"- note: {r['note']}")
        lines.append("")
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    # JSON aggregate
    REPORT_JSON.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"wrote {REPORT_MD} ({len(rows)} rounds)")
    print(f"wrote {REPORT_JSON}")
    return 0


def cmd_list(args) -> int:
    for r in _read_registry():
        print(json.dumps(r, sort_keys=True))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    rp = sub.add_parser("record", help="append/upsert one round into the registry")
    rp.add_argument("--round", default=None)
    rp.add_argument("--out-dir", required=True)
    rp.add_argument("--eval-json", default=None)
    rp.add_argument("--verdict", default=None)
    rp.add_argument("--note", default=None)
    rp.set_defaults(func=cmd_record)
    sub.add_parser("report", help="render trend markdown + json").set_defaults(func=cmd_report)
    sub.add_parser("list", help="print registry").set_defaults(func=cmd_list)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
