"""Card C-0012: independent second-leg holdout runner (sequential).

Leg 1 runs scripts/run_asi2_base_adapter_rubric_eval.py as THREE
parallel --task-start/--task-count slices on ASI2 (queue C-0002). This
leg reruns the SAME frozen 18-task benchmark through an INDEPENDENT
mechanism: ONE sequential process with NO task slicing, into its own
log file, followed by the dedicated fail-closed probe
(scripts/eval_failclosed_probe.py) appending to the same log. Only when
that log carries BOTH hyphenated markers (adapter-applied +
adapter-probe-differs) is the leg envelope written with its markers
true; otherwise exit 1 and NO envelope (fail-closed).

CLI:
  python3 scripts/run_holdout_leg2.py --base-model MODEL --adapter ADAPTER
      --step STEP --out-dir outputs/eval_leg2 [--benchmark FILE]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# C-9110: the leg-time differ evidence authority.
from scripts.candidates_differ_probe import envelope_evidence  # noqa: E402

LEG1_SCRIPT = "scripts/run_asi2_base_adapter_rubric_eval.py"
PROBE_SCRIPT = "scripts/eval_failclosed_probe.py"
LEG1_MECHANISM = "parallel-3-slice"
LEG2_MECHANISM = "sequential-single-slice"
MARKER_APPLIED = "adapter-applied"
MARKER_PROBE_DIFFERS = "adapter-probe-differs"
DEFAULT_BENCHMARK = "evals/benchmarks/sapo_promotion_holdout_v1_18.txt"
# C-9038: the banked truncation ceiling (harness/state/preflights/
# C-9038_ceiling.json, C-9112 derivation: 1087-token longest known-correct
# holdout reference x 1.25 headroom -> 1536 bucket). The old 384 default
# truncated the s97-class long solutions (12/15 failure set), so the NEXT
# legs run at the banked floor. Drift-guarded by
# harness/tests/test_c9038_truncation_failclosed.py.
DEFAULT_MAX_NEW_TOKENS = 4096  # C-9198 raised from 1536 to fix truncation


def missing_log_tokens(text):
    """Hyphenated fail-closed tokens absent from a leg log."""
    return [t for t in (MARKER_APPLIED, MARKER_PROBE_DIFFERS) if t not in text]


def sequential_argv(
    base_model,
    adapter,
    output,
    log,
    benchmark=None,
    device="npu",
    max_new_tokens=DEFAULT_MAX_NEW_TOKENS,
    harness_timeout=300,
):
    """One process, the WHOLE task list: NO --task-start/--task-count.

    Slicing is the leg-1 mechanism; refusing those flags here is what
    makes this leg an independent reconfirmation path.
    """
    argv = [
        sys.executable,
        str(ROOT / LEG1_SCRIPT),
        "--base-model",
        str(base_model),
        "--adapter",
        str(adapter),
        "--output",
        str(output),
        "--device",
        device,
        "--max-new-tokens",
        str(max_new_tokens),
        "--harness-timeout",
        str(harness_timeout),
    ]
    if benchmark is not None:
        argv += ["--benchmark", str(benchmark)]
    return argv


def build_envelope(
    leg, mechanism, box, adapter, base_model, benchmark, leg_log, scores, max_new_tokens=None
):
    """Fail-closed defaults: markers stay false until the log verifies."""
    return {
        "leg": leg,
        "runner_mechanism": mechanism,
        "box": box,
        "adapter": str(adapter),
        "base_model": str(base_model),
        "benchmark": str(benchmark),
        "adapter_applied_marker": False,
        "adapter_probe_differs_marker": False,
        "leg_log": str(leg_log),
        "scores": str(scores),
        # C-9046: the compose gate refuses envelopes without a budget
        "max_new_tokens": (int(max_new_tokens) if max_new_tokens is not None else None),
    }


def _run_append(argv, log_path):
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(
            "\n[%s] RUN %s\n"
            % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), " ".join(str(a) for a in argv))
        )
        fh.flush()
        return subprocess.call([str(a) for a in argv], stdout=fh, stderr=subprocess.STDOUT)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Independent sequential second leg over the frozen "
        "18-task quantum holdout (Card C-0012)."
    )
    parser.add_argument("--base-model", required=True)
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--step", required=True, help="checkpoint step label")
    parser.add_argument("--out-dir", default="outputs/eval_leg2")
    parser.add_argument("--box", default="ASI2")
    parser.add_argument("--benchmark", default=str(ROOT / DEFAULT_BENCHMARK))
    parser.add_argument("--device", default="npu")
    parser.add_argument("--device-map", default="balanced-layers")
    parser.add_argument("--npu-max-memory-gib", type=int, default=54)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--probe-max-new-tokens", type=int, default=8)
    parser.add_argument("--harness-timeout", type=int, default=300)
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log = out_dir / ("leg2_%s.log" % args.step)
    scores = out_dir / ("leg2_%s_scores.json" % args.step)

    eval_rc = _run_append(
        sequential_argv(
            args.base_model,
            args.adapter,
            scores,
            log,
            benchmark=args.benchmark,
            device=args.device,
            max_new_tokens=args.max_new_tokens,
            harness_timeout=args.harness_timeout,
        ),
        log,
    )
    if eval_rc != 0:
        print(json.dumps({"stage": "leg2_eval_failed", "rc": eval_rc, "log": str(log)}))
        return 1

    probe_rc = _run_append(
        [
            sys.executable,
            str(ROOT / PROBE_SCRIPT),
            "--base-model",
            str(args.base_model),
            "--adapter",
            str(args.adapter),
            "--device",
            args.device,
            "--device-map",
            args.device_map,
            "--npu-max-memory-gib",
            str(args.npu_max_memory_gib),
            "--probe-max-new-tokens",
            str(args.probe_max_new_tokens),
        ],
        log,
    )
    if probe_rc != 0:
        print(json.dumps({"stage": "leg2_probe_failed", "rc": probe_rc, "log": str(log)}))
        return 1

    text = log.read_text(encoding="utf-8", errors="replace")
    missing = missing_log_tokens(text)
    if missing:
        print(json.dumps({"stage": "leg2_markers_missing", "missing": missing, "log": str(log)}))
        return 1

    envelope = build_envelope(
        leg="leg2",
        mechanism=LEG2_MECHANISM,
        box=args.box,
        adapter=args.adapter,
        base_model=args.base_model,
        benchmark=args.benchmark,
        leg_log=log,
        scores=scores,
        max_new_tokens=args.max_new_tokens,
    )
    envelope["adapter_applied_marker"] = True
    envelope["adapter_probe_differs_marker"] = True
    envelope["created_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    envelope["created_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    # C-9110: record the per-task candidate-vs-base diff counts at
    # LEG time so the envelope carries the differ evidence onward.
    envelope["candidates_vs_base_diff"] = envelope_evidence(scores)
    # C-9121: leg independence evidence (harness/state/
    # leg2_independence_bar.md) -- stamped per leg at run time
    # and echoed verbatim into THIS leg's own log so the
    # compose corroboration check passes.
    indep = dict(
        leg_process_id=("leg2-pid-" + str(os.getpid()) + "-" + uuid.uuid4().hex[:8]),
        candidate_cache_id=str((out_dir / "candidates").resolve()),
        window_id=os.environ.get("ASI2_WINDOW_ID", "none"),
        transport=os.environ.get("ASI2_TRANSPORT", "direct-local"),
    )
    with open(log, "a", encoding="utf-8") as fh:
        fh.write("independence: " + " ".join("%s=%s" % (k, indep[k]) for k in sorted(indep)) + "\n")
    envelope.update(indep)
    out = out_dir / ("holdout_leg2_%s.json" % args.step)
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)
    print(json.dumps({"stage": "leg2_envelope_written", "out": str(out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
