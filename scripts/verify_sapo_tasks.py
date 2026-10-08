#!/usr/bin/env python3
"""Build a hash-pinned task manifest from executable reference tasks.

SECURITY: only run in an isolated disposable container without secrets,
network, or host filesystem write access. Task tests execute arbitrary Python.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.task_admission import build_manifest, prompt_text


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tasks-dir", required=True, type=Path)
    p.add_argument("--manifest-out", required=True, type=Path)
    p.add_argument("--report-out", required=True, type=Path)
    p.add_argument("--holdout-file", type=Path)
    p.add_argument("--ids-file", type=Path)
    p.add_argument("--replay-out", type=Path)
    p.add_argument("--timeout-seconds", type=float, default=15.0)
    p.add_argument("--allow-candidate-reference", action="store_true")
    p.add_argument("--sandbox-acknowledged", action="store_true", required=True)
    p.add_argument("--strict", action="store_true")
    args = p.parse_args(argv)
    if args.timeout_seconds <= 0:
        p.error("--timeout-seconds must be positive")
    allowed = None
    if args.ids_file:
        allowed = {line.strip() for line in args.ids_file.read_text().splitlines()
                   if line.strip() and not line.lstrip().startswith("#")}
        if not allowed:
            p.error("Empty --ids-file")
    root = args.tasks_dir.resolve()
    manifest, report = build_manifest(
        root, timeout=args.timeout_seconds,
        allow_candidate_reference=args.allow_candidate_reference,
        holdout=args.holdout_file, allowed_ids=allowed,
    )
    missing = sorted(allowed - {task["id"] for task in manifest["tasks"]}) if allowed else []
    if missing:
        report["missing_or_rejected_requested_ids"] = missing
    for file, value in ((args.manifest_out, manifest), (args.report_out, report)):
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    if args.replay_out:
        args.replay_out.parent.mkdir(parents=True, exist_ok=True)
        with args.replay_out.open("w", encoding="utf-8") as stream:
            for item in manifest["tasks"]:
                folder = root / item["path"]
                meta = json.loads((folder / "task.json").read_text())
                response = (folder / item["reference_file"]).read_text()
                key = hashlib.sha256((item["id"] + item["reference_sha256"]).encode()).hexdigest()[:20]
                stream.write(json.dumps({
                    "format": "chat-sft-v1",
                    "example_id": "verified_" + key,
                    "messages": [
                        {"role": "user", "content": prompt_text(meta)},
                        {"role": "assistant", "content": response},
                    ],
                    "metadata": {
                        "task_id": item["id"], "domain": item["domain"],
                        "source": "verifier_admitted_reference",
                        "reference_sha256": item["reference_sha256"],
                    },
                }, ensure_ascii=False) + "\n")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["accepted"] > 0 and not missing and (not args.strict or report["rejected"] == 0) else 2


if __name__ == "__main__":
    raise SystemExit(main())
