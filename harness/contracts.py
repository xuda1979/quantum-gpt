#!/usr/bin/env python3
"""contracts.py — THE single source of truth for harness invariants.

Every lane rule, gate rule, and fail-closed invariant lives HERE as data.
Gates import this module; prose docs are GENERATED from it (never hand-edited).

Meta-principle: rules that live only in prose drift from enforcement.
If you must change a rule: change it here, run the generator, commit both.

Usage:
    python3 harness/contracts.py dump            # JSON of all contracts
    python3 harness/contracts.py generate        # regenerate lanes/*.md docs
    python3 harness/contracts.py check --file X  # gate: file obeying contracts
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LANES_DIR = REPO / "harness" / "lanes"
GENERATED_MARKER = "<!-- GENERATED from harness/contracts.py — DO NOT EDIT -->"

# ---------------------------------------------------------------------------
# THE CONTRACTS. Keys are stable IDs referenced by gates and tests.
# Each contract: description (the rule in one sentence), applies_to (lane),
# enforced_by (scripts), data (machine-checkable form of the rule).
# ---------------------------------------------------------------------------
CONTRACTS: dict[str, dict] = {
    "eval_leg_fail_closed": {
        "description": "A leg without adapter-applied AND adapter-probe-differs markers is VOID — never score it.",
        "applies_to": "evaluator",
        "enforced_by": ["acceptance_gate.py", "eval_watcher.py"],
        "data": {"required_markers": ["adapter_applied", "probe_differs"], "void_if_missing": True},
    },
    "eval_never_on_trainer_npu": {
        "description": "Eval never runs on the trainer's NPUs.",
        "applies_to": "evaluator",
        "enforced_by": ["eval_watcher.py"],
        "data": {"forbidden_boxes": ["ASI3"], "allowed_boxes": ["ASI1", "ASI2"]},
    },
    "eval_three_parallel_slices": {
        "description": "Use 3 parallel task slices on ASI2 for holdout eval.",
        "applies_to": "evaluator",
        "enforced_by": ["eval_watcher.py"],
        "data": {"n_slices": 3, "box": "ASI2"},
    },
    "eval_verdict_location": {
        "description": "Verdicts land in outputs/verdict_*.json (repo) and on the checkpoint bus.",
        "applies_to": "evaluator",
        "enforced_by": ["eval_watcher.py"],
        "data": {"repo_glob": "outputs/verdict_*.json", "bus_name": "verdict.json"},
    },
    "eval_readonly_training_code": {
        "description": "Evaluator reads training artifacts; NEVER edits training code.",
        "applies_to": "evaluator",
        "enforced_by": ["review checklist"],
        "data": {"forbidden_write_globs": ["training/*.py", "scripts/run_holdout_leg1.py"]},
    },
    "launch_detached_setsid": {
        "description": "Training launches detached (setsid + nohup), never in-line in a card.",
        "applies_to": "trainer_ops",
        "enforced_by": ["launch_training.py", "auto_launch_training.py"],
        "data": {"detached": True, "mechanism": "setsid", "hard_cap_min": 90},
    },
    "boot_verify_after_launch": {
        "description": "Every training launch is boot-verified (process alive + probe file written).",
        "applies_to": "trainer_ops",
        "enforced_by": ["boot_verify_training.py"],
        "data": {"require_alive": True, "probe": "harness/state/probes/train.json"},
    },
    "checkpoint_bus_manifest": {
        "description": "Trainer publishes each completed checkpoint to the NAS bus via manifest.json.",
        "applies_to": "trainer_ops",
        "enforced_by": ["checkpoint_publisher.py", "eval_watcher.py"],
        "data": {
            "bus_root": "/root/work/ckpt_bus",
            "manifest_name": "manifest.json",
            "adapter_dir": "adapter/",
            "complete_marker": "adapter/adapter_config.json",
            "stage_local": True,
        },
    },
    "probe_after_every_change": {
        "description": "No claimed fix without a probe: every change lands with a deterministic probe artifact.",
        "applies_to": "all",
        "enforced_by": ["tdd.py"],
        "data": {"require_probe": True},
    },
    "no_training_without_compile_gate": {
        "description": "Training never launches until the on-box tree compiles (py_compile sweep).",
        "applies_to": "trainer_ops",
        "enforced_by": ["launch_training.py"],
        "data": {"gate": "py_compile sweep of training/*.py", "blocking": True},
    },
    "box_ports_fixed": {
        "description": "Box daemon ports are pinned in ONE config; scripts must import them, never re-declare.",
        "applies_to": "all",
        "enforced_by": ["harness_config.py", "lint_gate.py"],
        "data": {"ports": {"ASI1": 20646, "ASI2": 19004, "ASI3": 20653}},
    },
    "py39_runtime_safe": {
        "description": "Box-shipped code is py3.9-safe only (no zip strict=, no X|Y unions at runtime, no match).",
        "applies_to": "qa_steward",
        "enforced_by": ["lint_gate.py"],
        "data": {"forbidden_patterns": ["strict=", "match ", " | None"]},
    },
}

# ---------------------------------------------------------------------------
# Lane metadata: authority + scope lines for the generated role cards.
# ---------------------------------------------------------------------------
LANES: dict[str, dict] = {
    "evaluator": {
        "authority": "run + verify holdout eval legs; read training artifacts; NEVER edit training code.",
        "role": "EVALUATOR",
    },
    "trainer_ops": {
        "authority": "launch/monitor GRPO training on ASI3; publish checkpoints to the bus.",
        "role": "TRAINER-OPS",
    },
    "qa_steward": {
        "authority": "code hygiene on files NOT in an active launch path; every behavior change TDD-protected.",
        "role": "QA-STEWARD",
    },
    "planner": {
        "authority": "decompose the objective into cards; read state; NEVER implement.",
        "role": "PLANNER",
    },
    "fixer": {
        "authority": "implement fixes from cards; rejected by the gate => rework; never guess.",
        "role": "FIXER",
    },
    "data_miner": {
        "authority": "mine failure classes from artifacts; NEVER train, NEVER edit the trainer.",
        "role": "DATA-MINER",
    },
    "reviewer": {
        "authority": "review diffs for contract violations; read-only on code.",
        "role": "REVIEWER",
    },
    "deploy_integrity": {
        "authority": "verify tree == bundle == box (per-file sha256 from the MANIFEST list, never globs).",
        "role": "DEPLOY-INTEGRITY",
    },
}


def contract_ids_for_lane(lane: str) -> list[str]:
    """IDs of contracts that apply to a lane. <5 lines."""
    return [k for k, v in CONTRACTS.items() if v.get("applies_to") == lane or v.get("applies_to") == "all"]


def render_lane_md(lane_id: str) -> str:
    """Render one generated role card from contracts data."""
    meta = LANES[lane_id]
    lines = [GENERATED_MARKER, f"# {meta['role']} — role card", f"Authority: {meta['authority']}", ""]
    ids = contract_ids_for_lane(lane_id)
    if not ids:
        return "\n".join(lines).rstrip() + "\n"
    lines.append("Invariants (from harness/contracts.py):")
    for cid in ids:
        c = CONTRACTS[cid]
        lines.append(f"- [{cid}] {c['description']}")
        lines.append(f"  - enforced by: {', '.join(c.get('enforced_by', []))}")
    return "\n".join(lines).rstrip() + "\n"


LANE_FILES = {  # lane_id -> canonical doc filename (historical hyphenated names)
    "evaluator": "evaluator.md",
    "trainer_ops": "trainer-ops.md",
    "qa_steward": "qa-steward.md",
    "planner": "planner.md",
    "fixer": "fixer.md",
    "data_miner": "data-miner.md",
    "reviewer": "reviewer.md",
    "deploy_integrity": "deploy-integrity.md",
}


def generate_docs() -> list[str]:
    """Regenerate all lane docs. Returns written paths."""
    LANES_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for lane_id in LANES:
        path = LANES_DIR / LANE_FILES[lane_id]
        path.write_text(render_lane_md(lane_id))
        written.append(str(path))
    return written


def check_file(path: str) -> tuple[bool, list[str]]:
    """Gate: check a box-shipped py file against runtime-safety contracts."""
    text = Path(path).read_text()
    violations = []
    pats = CONTRACTS["py39_runtime_safe"]["data"]["forbidden_patterns"]
    for pat in pats:
        if pat == "strict=":
            hits = [i + 1 for i, line in enumerate(text.splitlines()) if re.search(r"zip\([^)]*strict=", line)]
            violations += [f"{path}:{n}: py39-unsafe zip(strict=)" for n in hits]
        elif pat == " | None":
            hits = [i + 1 for i, line in enumerate(text.splitlines()) if re.search(r"\w+ \| None", line) and not line.strip().startswith("#")]
            violations += [f"{path}:{n}: py39-unsafe X | None annotation" for n in hits]
    return not violations, violations


def main() -> None:
    """Dispatch. <10 lines."""
    ap = argparse.ArgumentParser(description="Contracts: single source of truth")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("dump")
    sub.add_parser("generate")
    p_check = sub.add_parser("check")
    p_check.add_argument("--file", required=True)
    args = ap.parse_args()
    if args.cmd == "dump":
        print(json.dumps(CONTRACTS, indent=2))
    elif args.cmd == "generate":
        for p in generate_docs():
            print(f"WROTE {p}")
    elif args.cmd == "check":
        ok, violations = check_file(args.file)
        print("PASS" if ok else "FAIL")
        for v in violations:
            print(f"  - {v}")
        sys.exit(0 if ok else 1)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
