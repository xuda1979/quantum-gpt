#!/usr/bin/env python3
"""Card C-9006: fail-closed envelope producer for the FULL 18-task leg-1.

Leg 1 is the FULL frozen 18-task quantum holdout through the
parallel-3-slice mechanism of scripts/run_asi2_base_adapter_rubric_eval.py
(THREE disjoint --task-start/--task-count slices). Until this card the
leg-1 envelope had NO producer: holdout_verdict._marker_check requires
adapter_applied_marker + adapter_probe_differs_marker true AND hyphenated
marker corroboration in the leg log, but only leg 2 could produce that.
This runner composes the leg the way run_holdout_leg2.py does:

  1. the THREE parallel slices of the FULL benchmark, appending to ONE leg
     log, each slice to its OWN scores file (parallel writers never share
     an output path);
  2. a fail-closed MERGE of the slice scores that refuses the envelope
     unless the union covers EXACTLY the frozen benchmark ids for BOTH
     models -- no duplicate, missing, or non-frozen record;
  3. the dedicated probe (scripts/eval_failclosed_probe.py) appending to
     the same log; and
  4. the marker gate: only when the leg log carries BOTH hyphenated
     markers (adapter-applied + adapter-probe-differs) is the leg envelope
     written with its markers true; otherwise exit 1 and NO envelope
     (fail-closed).

CLI:
  python3 scripts/run_holdout_leg1.py --base-model MODEL --adapter ADAPTER
      --step STEP --out-dir outputs/eval_leg1 [--benchmark FILE]
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
MARKER_APPLIED = "adapter-applied"
MARKER_PROBE_DIFFERS = "adapter-probe-differs"
DEFAULT_BENCHMARK = "evals/benchmarks/sapo_promotion_holdout_v1_18.txt"
N_SLICES = 3
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


def compute_slices(n_tasks, parts=N_SLICES):
    """Disjoint contiguous (start, count) slices covering ALL n_tasks.

    Raises ValueError on an empty task list: a full leg over zero tasks is
    not a leg.
    """
    if n_tasks <= 0:
        raise ValueError("full leg needs at least one task, got %r" % n_tasks)
    # Never dispatch a slice that selects no tasks (the evaluator refuses
    # empty slices): degenerate benchmarks get fewer, non-empty slices.
    parts = min(parts, n_tasks)
    base = n_tasks // parts
    rem = n_tasks % parts
    slices = []
    start = 0
    for i in range(parts):
        count = base + (1 if i < rem else 0)
        slices.append((start, count))
        start += count
    return slices


def slice_argv(
    base_model,
    adapter,
    output,
    log,
    benchmark,
    task_start,
    task_count,
    device="npu",
    max_new_tokens=DEFAULT_MAX_NEW_TOKENS,
    harness_timeout=300,
):
    """One --task-start/--task-count slice of the leg-1 mechanism.

    Slicing is what makes this leg DISTINCT from leg 2's sequential
    single-slice path (harness_lib requires distinct runner mechanisms).
    """
    return [
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
        "--benchmark",
        str(benchmark),
        "--task-start",
        str(task_start),
        "--task-count",
        str(task_count),
    ]


def build_envelope(
    leg, mechanism, box, adapter, base_model, benchmark, leg_log, scores, max_new_tokens=None
):
    """Fail-closed defaults: markers stay false until the log verifies."""
    return dict(
        leg=leg,
        runner_mechanism=mechanism,
        box=box,
        adapter=str(adapter),
        base_model=str(base_model),
        benchmark=str(benchmark),
        adapter_applied_marker=False,
        adapter_probe_differs_marker=False,
        leg_log=str(leg_log),
        scores=str(scores),
        # C-9046: the compose gate refuses envelopes without a budget
        max_new_tokens=(int(max_new_tokens) if max_new_tokens is not None else None),
    )


def load_benchmark_ids(path):
    """Task ids of the frozen benchmark (same parse as holdout_verdict)."""
    p = Path(path)
    if not p.is_file():
        raise ValueError("benchmark file missing: %s" % p)
    ids = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            ids.append(line.split()[0])
    if not ids:
        raise ValueError("benchmark file has no task ids: %s" % p)
    return ids


def merge_slice_scores(slice_paths, benchmark_ids):
    """Merge slice payloads; refuse unless coverage is EXACT.

    The verdict composer consumes ONE scores file whose records must cover
    every frozen task id for BOTH models with no duplicates and no
    non-frozen extras (holdout_verdict._passes_from_scores). A parallel
    slice set that clobbered, dropped, or doubled a record must fail the
    leg here, not inside the composer.
    """
    records = []
    seen = set()
    for path in slice_paths:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        rows = payload.get("records") if isinstance(payload, dict) else None
        if not isinstance(rows, list):
            raise ValueError("slice scores lacks a records list: %s" % path)
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("slice record not an object: %s" % path)
            key = (row.get("model"), row.get("task_id"))
            if key in seen:
                raise ValueError("duplicate record across slices: %r" % (key,))
            seen.add(key)
            records.append(row)
    expected = set()
    for tid in benchmark_ids:
        expected.add(("base", tid))
        expected.add(("adapter", tid))
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        raise ValueError("merged scores missing records: %s" % missing)
    if extra:
        raise ValueError("merged scores cover non-frozen tasks: %s" % extra)
    return dict(
        created_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        slices=[str(p) for p in slice_paths],
        benchmark_ids=list(benchmark_ids),
        records=records,
    )


def _echo(fh, tag, argv):
    fh.write(
        "[%s] %s %s\n"
        % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), tag, " ".join(str(a) for a in argv))
    )
    fh.flush()


def _run_parallel(argvs, log_path):
    """Run the slices CONCURRENTLY into one append-mode log (the mechanism).

    The fd is shared in O_APPEND mode, so per-line writes stay atomic.
    Returns the return codes in slice order.
    """
    with open(log_path, "a", encoding="utf-8") as fh:
        for i, argv in enumerate(argvs):
            _echo(fh, "SLICE%d" % i, argv)
        procs = [
            subprocess.Popen([str(a) for a in argv], stdout=fh, stderr=subprocess.STDOUT)
            for argv in argvs
        ]
        return [p.wait() for p in procs]


def _run_append(argv, log_path):
    with open(log_path, "a", encoding="utf-8") as fh:
        _echo(fh, "RUN", argv)
        return subprocess.call([str(a) for a in argv], stdout=fh, stderr=subprocess.STDOUT)


def _write_json(payload, out):
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Fail-closed FULL 18-task leg-1 runner over the "
        "parallel-3-slice mechanism (Card C-9006)."
    )
    parser.add_argument("--base-model", required=True)
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--step", required=True, help="checkpoint step label")
    parser.add_argument("--out-dir", default="outputs/eval_leg1")
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
    log = out_dir / ("leg1_%s.log" % args.step)
    scores = out_dir / ("leg1_%s_scores.json" % args.step)

    try:
        ids = load_benchmark_ids(args.benchmark)
        slices = compute_slices(len(ids))
    except ValueError as exc:
        print(json.dumps(dict(stage="leg1_benchmark_invalid", error=str(exc))), flush=True)
        return 1

    slice_paths = [
        out_dir / ("leg1_%s_slice%d_scores.json" % (args.step, i)) for i in range(len(slices))
    ]
    argvs = [
        slice_argv(
            args.base_model,
            args.adapter,
            slice_paths[i],
            log,
            args.benchmark,
            start,
            count,
            device=args.device,
            max_new_tokens=args.max_new_tokens,
            harness_timeout=args.harness_timeout,
        )
        for i, (start, count) in enumerate(slices)
    ]
    rcs = _run_parallel(argvs, log)
    bad = [(i, rc) for i, rc in enumerate(rcs) if rc != 0]
    if bad:
        print(json.dumps(dict(stage="leg1_eval_failed", slices=bad, log=str(log))), flush=True)
        return 1

    try:
        merged = merge_slice_scores(slice_paths, ids)
    except (ValueError, json.JSONDecodeError, OSError) as exc:
        print(json.dumps(dict(stage="leg1_merge_failed", error=str(exc))), flush=True)
        return 1
    _write_json(merged, scores)

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
        print(json.dumps(dict(stage="leg1_probe_failed", rc=probe_rc, log=str(log))), flush=True)
        return 1

    text = log.read_text(encoding="utf-8", errors="replace")
    missing = missing_log_tokens(text)
    if missing:
        print(
            json.dumps(dict(stage="leg1_markers_missing", missing=missing, log=str(log))),
            flush=True,
        )
        return 1

    envelope = build_envelope(
        leg="leg1",
        mechanism=LEG1_MECHANISM,
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
        leg_process_id=("leg1-pid-" + str(os.getpid()) + "-" + uuid.uuid4().hex[:8]),
        candidate_cache_id=str((out_dir / "candidates").resolve()),
        window_id=os.environ.get("ASI2_WINDOW_ID", "none"),
        transport=os.environ.get("ASI2_TRANSPORT", "direct-local"),
    )
    with open(log, "a", encoding="utf-8") as fh:
        fh.write("independence: " + " ".join("%s=%s" % (k, indep[k]) for k in sorted(indep)) + "\n")
    envelope.update(indep)
    out = out_dir / ("holdout_leg1_%s.json" % args.step)
    _write_json(envelope, out)
    print(json.dumps(dict(stage="leg1_envelope_written", out=str(out))), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
