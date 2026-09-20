"""Card C-0012: fail-closed verdict composer for the frozen 18-task
quantum holdout.

Consumes TWO leg envelopes (leg1 = parallel-3-slice on ASI2, leg2 =
sequential-single-slice via run_holdout_leg2.py - independent runner
paths) plus each leg's scores JSON and leg log, and emits the verdict
file ONLY when every fail-closed check passes:

  - both envelopes carry adapter_applied_marker AND
    adapter_probe_differs_marker == true, corroborated by the
    hyphenated tokens (adapter-applied / adapter-probe-differs) in each
    leg log - the harness eval-failclosed gate greps the same tokens
  - both legs cover EXACTLY the frozen task set (target 18/18 -> 18
    ids) and ran the SAME benchmark file
  - the two legs agree on every per-task adapter AND base pass
  - per-task base passes exist (the beats_base arithmetic input)
  - the legs ran DIFFERENT runner mechanisms (independent second leg)
  - Card C-9117 leg2 independence bar (harness/state/
    leg2_independence_bar.md): the pair evidences a DISTINCT leg
    process AND no shared candidate cache AND (distinct window OR
    distinct transport); each element must be non-empty in the
    envelope AND verbatim-corroborated by that leg's own log

Any rejection exits 1 with NO verdict file written (fail-closed, never
a partial pass). Honest sub-target counts still compose with
meets_goal false; harness goal_done stays the 18/18 gate.

CLI:
  python3 scripts/holdout_verdict.py --leg1 LEG1.json --leg2 LEG2.json
      --out outputs/verdict_<step>.json [--target 18/18]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Card C-0013 pin (harness/state/beats_base_metric.md): the beats_base
# comparison is NEVER re-implemented here. The pinned metric owns it and
# fails closed on a tie whose composite tiebreak inputs are missing.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from harness.beats_base import BeatsBaseError  # noqa: E402
from harness.beats_base import beats_base as pinned_beats_base  # noqa: E402
from scripts.verdict_holdout import composite as pinned_composite  # noqa: E402
from harness.harness_lib import is_qwen38_27b_model  # noqa: E402  # C-9119
from scripts.candidates_differ_probe import (  # noqa: E402
    CANDIDATE_BASE_MATCH_MAX_FRACTION,  # C-9110 stated bar
)

MARKER_APPLIED = "adapter-applied"
MARKER_PROBE_DIFFERS = "adapter-probe-differs"
# C-0040: rejection evidence cites these GATE-SAFE underscore names, never
# the hyphenated tokens themselves - the harness eval-failclosed gate
# (harness_lib.check_gate) greps result text for the hyphenated forms, so
# a BLOCKED compose quoting its own rejection must not carry a pass marker.
_MARKER_LOG_TOKENS = (
    (MARKER_APPLIED, "adapter_applied"),
    (MARKER_PROBE_DIFFERS, "adapter_probe_differs"),
)
DEFAULT_TARGET = "18/18"
# C-0049: per-task fail-closed grading. Contained-poison evidence (the
# C-0034 crash-class token in a leg record's details) is carried into
# the verdict's per_task entries as fail_closed; pass counting itself
# never changes.
POISON_TOKENS = ("candidate_none_graded_fail",)
# Card C-9038: truncation fail-closed scoring. A completion cut at the
# max_new_tokens cap can never bank a pass, and a record with NO usable
# truncation field is NOT-pass too -- UNKNOWN never silently reads as
# untruncated.
TRUNCATED_NOT_PASS = "truncated_output_not_pass"
TRUNCATION_INFO_MISSING_NOT_PASS = "truncation_info_missing_not_pass"
# Card C-9117: leg2 independence evidence. Every leg envelope carries
# these four fields; each leg log corroborates each declared value
# verbatim; the pair rules live in compose() (bar doc: INDEPENDENCE_BAR).
INDEPENDENCE_FIELDS = (
    "leg_process_id", "candidate_cache_id", "window_id", "transport")
INDEPENDENCE_BAR = "harness/state/leg2_independence_bar.md"


class VerdictRejected(Exception):
    """A fail-closed input check failed; no verdict file may be written."""


def _reject(msg):
    raise VerdictRejected(msg)


def _read_json(path, what):
    p = Path(path)
    if not p.is_file():
        _reject("%s missing: %s" % (what, p))
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        _reject("%s unparseable: %s (%s)" % (what, p, exc))


def load_benchmark_ids(path):
    p = Path(path)
    if not p.is_file():
        _reject("benchmark file missing: %s" % p)
    ids = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            ids.append(line.split()[0])
    if not ids:
        _reject("benchmark file has no task ids: %s" % p)
    return ids


def _marker_check(env, leg_name, log_path):
    for key in ("adapter_applied_marker", "adapter_probe_differs_marker"):
        if env.get(key) is not True:
            _reject("%s lacks %s=true" % (leg_name, key))
    log = Path(log_path)
    if not log.is_file():
        _reject("%s leg_log missing: %s" % (leg_name, log))
    text = log.read_text(encoding="utf-8", errors="replace")
    for token, gate_safe in _MARKER_LOG_TOKENS:
        if token not in text:
            _reject("%s leg_log lacks marker corroboration %s=true: %s"
                    % (leg_name, gate_safe, log))


def _independence_evidence(env, leg_name, log_path):
    """Card C-9117: per-field fail-closed independence evidence.

    Each INDEPENDENCE_FIELDS entry must be a non-empty string in the
    envelope (else verdict_composer_refused_independence_evidence_
    missing) AND appear verbatim in that leg's own log text (else
    verdict_composer_refused_independence_uncorroborated -- an
    uncorroborated claim is never a pass). Returns the stripped values
    for the pair-level rules in compose()."""
    text = Path(log_path).read_text(encoding="utf-8", errors="replace")
    evidence = dict()
    for field in INDEPENDENCE_FIELDS:
        value = env.get(field)
        if not isinstance(value, str) or not value.strip():
            _reject("verdict_composer_refused_independence_evidence_"
                    "missing: %s lacks %s (bar: %s)"
                    % (leg_name, field, INDEPENDENCE_BAR))
        if value.strip() not in text:
            _reject("verdict_composer_refused_independence_"
                    "uncorroborated: %s log lacks %s corroboration "
                    "(bar: %s)" % (leg_name, field, INDEPENDENCE_BAR))
        evidence[field] = value.strip()
    return evidence


def _passes_from_scores(scores, task_ids, leg_name):
    if not isinstance(scores, dict) or not isinstance(scores.get("records"), list):
        _reject("%s scores lacks a records list" % leg_name)
    adapter = {}
    base = {}
    records_by_model = {"adapter": [], "base": []}
    fail_marks = dict(adapter=dict(), base=dict())
    for rec in scores["records"]:
        if not isinstance(rec, dict):
            _reject("%s scores record is not an object" % leg_name)
        model = rec.get("model")
        tid = rec.get("task_id")
        passed = rec.get("passed")
        if (model not in ("adapter", "base") or not isinstance(tid, str)
                or not isinstance(passed, bool)):
            _reject("%s scores record malformed: %r" % (leg_name, rec))
        target = adapter if model == "adapter" else base
        if tid in target:
            _reject("%s scores duplicate record: %s/%s" % (leg_name, model, tid))
        # C-9038: truncation fail-closed. A cap-cut completion is NOT-pass
        # by construction; a record with no usable truncation field is
        # NOT-pass too (fail-closed UNKNOWN); both carry a fail mark into
        # the verdict's per_task entries. Pass counting never inflates.
        truncated = rec.get("truncated")
        if truncated is True:
            passed = False
            reason = TRUNCATED_NOT_PASS
        elif truncated is not False:
            passed = False
            reason = TRUNCATION_INFO_MISSING_NOT_PASS
        else:
            reason = None
        if reason is not None:
            marks = fail_marks[model]
            marks[tid] = marks.get(tid, []) + [reason]
        target[tid] = passed
        records_by_model[model].append(rec)
        # C-0049: carry contained-poison evidence so the verdict can mark
        # the task fail_closed; details stay optional (no new rejection).
        dets = rec.get("details")
        if isinstance(dets, list) and any(
                isinstance(d, str) and any(tok in d for tok in POISON_TOKENS)
                for d in dets):
            fail_marks[model][tid] = [str(d) for d in dets]
    expected = set(task_ids)
    for name, got in (("adapter", adapter), ("base", base)):
        missing = expected - set(got)
        extra = set(got) - expected
        if missing:
            if name == "base":
                _reject("beats_base arithmetic input missing: %s base "
                        "passes missing tasks: %s" % (leg_name, sorted(missing)))
            _reject("%s %s passes missing tasks: %s"
                    % (leg_name, name, sorted(missing)))
        if extra:
            _reject("%s %s passes cover non-frozen tasks: %s"
                    % (leg_name, name, sorted(extra)))
    return adapter, base, records_by_model, fail_marks


def _composite_of(records, total):
    """Composite tiebreak input, or None when no record is scored."""
    for rec in records:
        sc = rec.get("scores")
        ov = sc.get("overall") if isinstance(sc, dict) else None
        if isinstance(ov, (int, float)) and not isinstance(ov, bool):
            return pinned_composite(records, total)
    return None


def _resolve_model_identity(env, leg_name):
    """C-9119: prove the evaluated adapter is a Qwen3.8-27B adapter.

    Evidence chain (fail-closed at every link; a hole can never read as
    a pass -- each refusal lands in .violation as a named
    model_identity_violation reason):
      1. the leg envelope references a C-9089 checkpoint pin artifact
         (checkpoint_id + sha256 + inventory_path + base_model)
      2. the pin carries base_model (pre-C-9119 pins do not -> refuse)
      3. when the pinned checkpoint is locally readable, its
         adapter_config.json must exist and agree with the pin
         (base_model_name_or_path + sha256); an absent/unreadable
         adapter config refuses (C-9068 acceptance: fail closed)
      4. base_model_name_or_path must resolve to the Qwen3.8-27B family
      5. every C-9068 inventory entry carries base_model
    """
    import hashlib

    mi = dict(status="VIOLATED", base_model=None, sha256=None,
              checkpoint_id=None, pin_ref=None, violation=None)

    def refuse(reason):
        mi["violation"] = reason
        return mi

    ref = env.get("checkpoint_pin")
    if not ref:
        return refuse("model_identity_violation: checkpoint_pin_absent "
                      "(no C-9089 pin artifact referenced)")
    mi["pin_ref"] = str(ref)
    try:
        pin = json.loads(Path(ref).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return refuse("model_identity_violation: checkpoint_pin_unreadable "
                      "(%s)" % exc)
    if not isinstance(pin, dict):
        return refuse("model_identity_violation: checkpoint_pin_unreadable "
                      "(not an object)")
    mi["checkpoint_id"] = pin.get("checkpoint_id")
    base_model = pin.get("base_model")
    if not isinstance(base_model, str) or not base_model:
        return refuse("model_identity_violation: base_model_absent_in_pin "
                      "(pre-C-9119 pin schema)")
    mi["base_model"] = base_model
    pin_sha = pin.get("sha256")
    ckpt = pin.get("checkpoint_path")
    if isinstance(ckpt, str) and ckpt and Path(ckpt).is_dir():
        # the pinned checkpoint is locally reachable: verify it directly
        cfg = Path(ckpt) / "adapter_config.json"
        if not cfg.is_file():
            return refuse("model_identity_violation: adapter_config_absent "
                          "at pinned checkpoint %s" % ckpt)
        try:
            cfg_json = json.loads(cfg.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return refuse("model_identity_violation: adapter_config_"
                          "unreadable (%s)" % exc)
        cfg_base = (cfg_json.get("base_model_name_or_path")
                    if isinstance(cfg_json, dict) else None)
        if cfg_base != base_model:
            return refuse("model_identity_violation: adapter_config_pin_"
                          "disagreement (config=%r pin=%r)"
                          % (cfg_base, base_model))
        disk_sha = hashlib.sha256(cfg.read_bytes()).hexdigest()
        if isinstance(pin_sha, str) and pin_sha and disk_sha != pin_sha:
            return refuse("model_identity_violation: adapter_config_sha_"
                          "mismatch (tamper evidence)")
        mi["sha256"] = disk_sha
    elif isinstance(pin_sha, str) and pin_sha:
        # box-only checkpoint: the sha-pinned pin is the evidence
        mi["sha256"] = pin_sha
    else:
        return refuse("model_identity_violation: checkpoint_unreachable_"
                      "sha_absent (identity unproven)")
    if not is_qwen38_27b_model(base_model):
        return refuse("model_identity_violation: base_model_mismatch "
                      "(%r is not the Qwen3.8-27B family)" % base_model)
    inv_path = pin.get("inventory_path")
    if isinstance(inv_path, str) and inv_path:
        try:
            inv = json.loads(Path(inv_path).read_text(encoding="utf-8"))
            entries = inv.get("checkpoints") if isinstance(inv, dict) else None
            if not isinstance(entries, list):
                raise ValueError("checkpoints list absent")
            for entry in entries:
                ebm = entry.get("base_model") if isinstance(entry, dict) else None
                if not isinstance(ebm, str) or not ebm:
                    return refuse("model_identity_violation: inventory_entry_"
                                  "base_model_absent")
        except (OSError, ValueError) as exc:
            return refuse("model_identity_violation: inventory_unreadable "
                          "(%s)" % exc)
    mi["status"] = "PASS"
    return mi


def load_leg(path, total):
    env = _read_json(path, "leg envelope")
    if not isinstance(env, dict):
        _reject("leg envelope not an object: %s" % path)
    leg_name = str(env.get("leg") or Path(path).name)
    _marker_check(env, leg_name, env.get("leg_log"))
    # Card C-9117: independence evidence is fail-closed per leg, same
    # corroboration pattern as the markers above.
    independence = _independence_evidence(env, leg_name, env.get("leg_log"))
    # C-9046: budget parity. A cross-budget beats_base compares a
    # handicapped leg against a raised ceiling and can bank a FALSE goal
    # verdict, so every leg envelope MUST carry its max_new_tokens; an
    # envelope with no usable budget composes as UNKNOWN-refuse, never a
    # silent pass.
    budget = env.get("max_new_tokens")
    if (not isinstance(budget, int) or isinstance(budget, bool)
            or budget <= 0):
        _reject("verdict_composer_refused_budget_unknown: %s envelope "
                "lacks a usable max_new_tokens (fail-closed UNKNOWN, "
                "cross-budget compose refused)" % leg_name)
    if not env.get("benchmark"):
        _reject("%s envelope lacks its benchmark path" % leg_name)
    ids = load_benchmark_ids(env["benchmark"])
    if len(ids) != total:
        _reject("%s benchmark has %d tasks; target requires %d"
                % (leg_name, len(ids), total))
    scores = _read_json(env.get("scores"), "%s scores" % leg_name)
    adapter, base, records_by_model, fail_marks = _passes_from_scores(
        scores, ids, leg_name)
    composite_adapter = _composite_of(records_by_model["adapter"], len(ids))
    composite_base = _composite_of(records_by_model["base"], len(ids))
    # Card C-0033: a leg whose records carry NO scores.overall anywhere is
    # an EMPTY leg result. Refuse it even when pass-counts differ (the
    # pinned metric would decide on pass-count and never notice the gap).
    if composite_adapter is None or composite_base is None:
        _reject("verdict_composer_refused_empty: %s leg result has no "
                "composite inputs (scores.overall absent from every "
                "record)" % leg_name)
    return {
        "env": env,
        "path": str(path),
        "ids": ids,
        "adapter": adapter,
        "base": base,
        "mechanism": str(env.get("runner_mechanism") or "unknown"),
        "composite_adapter": composite_adapter,
        "composite_base": composite_base,
        "fail_marks": fail_marks,
        "budget": budget,
        "independence": independence,
        # C-9059: the recorded candidates-differ-from-base evidence (the
        # probe artifact scripts/candidates_differ_probe.py writes).
        # Evidence only -- never a compose gate; absent/malformed reads
        # as UNKNOWN so a hole can never masquerade as a pass.
        "candidates_differ": _load_candidates_differ(env, leg_name, path),
        # C-9119: proven (or refused) base-model identity for this leg.
        "model_identity": _resolve_model_identity(env, leg_name),
        # C-9110: the leg-time candidate-vs-base diff recording
        # (gate INPUT -- compose never recomputes the diff).
        "candidates_vs_base": _load_candidates_vs_base(
            env, leg_name, ids, env.get("scores")),
    }


def _load_candidates_differ(env, leg_name, leg_path):
    """C-9059: resolve this leg's candidates_differ artifact.

    Lookup order: the envelope's explicit candidates_differ_artifact ref,
    then a sibling of the leg envelope, then outputs/<leg>_candidates_
    differ.json relative to the compose cwd. Missing, unparseable, or
    malformed artifacts record status UNKNOWN with a reason -- the field
    is re-verifiable done_criteria evidence, never a silent pass and
    never a gate (C-9046 stays the only budget authority)."""
    candidates = []
    ref = env.get("candidates_differ_artifact")
    if ref:
        candidates.append(Path(ref))
    candidates.append(
        Path(leg_path).resolve().parent
        / ("%s_candidates_differ.json" % leg_name))
    candidates.append(
        Path.cwd() / "outputs"
        / ("%s_candidates_differ.json" % leg_name))
    art_path = next((c for c in candidates if c.is_file()), None)
    unknown = {
        "status": "UNKNOWN",
        "reason": "candidates_differ_artifact_absent",
        "n_checked": None,
        "base_source_sha": None,
        "ref": None,
    }
    if art_path is None:
        return unknown
    try:
        art = json.loads(art_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        unknown["reason"] = "candidates_differ_artifact_unparseable: %s" % exc
        unknown["ref"] = str(art_path)
        return unknown
    if (not isinstance(art, dict)
            or art.get("status") not in ("PASS", "FAIL", "UNKNOWN")):
        unknown["reason"] = "candidates_differ_artifact_malformed"
        unknown["ref"] = str(art_path)
        return unknown
    n_checked = art.get("n_checked")
    if not isinstance(n_checked, int) or isinstance(n_checked, bool):
        n_checked = None
    base_sha = art.get("base_source_sha")
    if not isinstance(base_sha, str):
        base_sha = None
    return {
        "status": str(art["status"]),
        "reason": (art.get("reason")
                   if isinstance(art.get("reason"), str) else None),
        "n_checked": n_checked,
        "base_source_sha": base_sha,
        "ref": str(art_path),
    }


def compute_sha_pins():
    """C-0031: hash the ACTUAL frozen bench + scorer-chain files on disk
    so the verdict carries evidence of which scorer produced it. The
    harness done-check (goal_done via sha_pin_violation) rejects verdicts
    whose embedded pins drift from the canonical manifest
    (evals/benchmarks/sapo_promotion_holdout_v1_18.sha256); a missing pin
    source rejects the compose (fail-closed, no verdict file)."""
    import hashlib

    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from evals.runner.holdout_freeze import BENCH_RELPATH, SCORER_CHAIN

    hashes = {}
    for rel in (BENCH_RELPATH,) + tuple(SCORER_CHAIN):
        p = root / rel
        if not p.is_file():
            _reject("sha pin source missing: %s" % rel)
        hashes[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return hashes[BENCH_RELPATH], dict(
        (rel, hashes[rel]) for rel in SCORER_CHAIN)


def _load_candidates_vs_base(env, leg_name, ids, scores_path):
    """C-9110: validate the per-task candidate-vs-base byte-diff counts
    RECORDED INTO the envelope at leg time (run_holdout_leg{1,2}.py
    via candidates_differ_probe.envelope_evidence). Compose never
    recomputes the diff; it checks the recording is usable and tied to
    THIS leg's scores file. Anything absent/malformed/tampered reads
    UNKNOWN with a named reason -- a hole can never read as a pass."""
    import hashlib

    ev = env.get("candidates_vs_base_diff")
    unknown = dict(status="UNKNOWN", reason=None, n_checked=0,
                   n_byte_match=0, matching_task_ids=[], per_task={},
                   evidence_source=None, scores_sha256=None,
                   match_max_fraction=CANDIDATE_BASE_MATCH_MAX_FRACTION)
    if not isinstance(ev, dict):
        unknown["reason"] = "candidates_vs_base_diff absent from envelope"
        return unknown
    if ev.get("status") != "MEASURED":
        unknown["reason"] = ("leg-time differ evidence status is %r, "
                             "not MEASURED" % (ev.get("status"),))
        return unknown
    per_task = ev.get("per_task")
    if not isinstance(per_task, dict) or set(per_task) != set(ids):
        unknown["reason"] = ("differ evidence per_task does not cover the "
                             "frozen task set exactly")
        return unknown
    n_checked = ev.get("n_checked")
    if (not isinstance(n_checked, int) or isinstance(n_checked, bool)
            or n_checked != len(ids)):
        unknown["reason"] = ("differ evidence n_checked %r != %d tasks"
                             % (n_checked, len(ids)))
        return unknown
    matching = ev.get("matching_task_ids")
    if (not isinstance(matching, list)
            or not all(isinstance(t, str) for t in matching)
            or set(matching) - set(ids)):
        unknown["reason"] = "differ evidence matching_task_ids malformed"
        return unknown
    stamped = ev.get("scores_sha256")
    scores_sha = None
    try:
        scores_sha = hashlib.sha256(
            Path(scores_path).read_bytes()).hexdigest()
    except OSError as exc:
        unknown["reason"] = ("scores file unreadable for the evidence "
                             "tie: %s" % exc)
        return unknown
    if stamped != scores_sha:
        unknown["reason"] = ("differ evidence scores_sha256 %r does not "
                             "match the leg scores file %s (tamper or "
                             "stale evidence)" % (stamped, scores_path))
        return unknown
    out = dict(ev)
    out.setdefault("match_max_fraction",
                   CANDIDATE_BASE_MATCH_MAX_FRACTION)
    return out


def candidates_differ_gate(leg_name, evidence):
    """C-9110: the done-criteria candidate-vs-base differ GATE. Refuses
    a leg whose candidate outputs byte-match base on MORE than the
    stated per-task threshold (CANDIDATE_BASE_MATCH_MAX_FRACTION of its
    checked tasks) -- a degenerate adapter echoing base can never bank a
    goal verdict. The refusal NAMES the matching task ids. UNKNOWN
    evidence refuses too (a hole is never a pass). Returns the PASS
    summary stamped into the verdict."""
    frac = CANDIDATE_BASE_MATCH_MAX_FRACTION
    if not isinstance(evidence, dict) or evidence.get("status") != "MEASURED":
        reason = (evidence.get("reason")
                  if isinstance(evidence, dict) else "absent")
        _reject("verdict_composer_refused_candidates_differ_unknown: %s "
                "carries no usable candidates-vs-base diff evidence "
                "(%s); compose refuses fail-closed" % (leg_name, reason))
    n = evidence["n_checked"]
    matching = sorted(evidence.get("matching_task_ids") or [])
    limit = int(n * frac)
    if len(matching) > limit:
        _reject("verdict_composer_refused_candidates_match_base: %s "
                "candidate outputs byte-match base on %d/%d checked "
                "tasks (stated per-task limit %d at max_fraction %s); "
                "matching tasks: %s"
                % (leg_name, len(matching), n, limit, frac, matching))
    return dict(status="PASS", n_checked=n, n_byte_match=len(matching),
                limit=limit, max_fraction=frac, matching_task_ids=matching)


def compose(leg1, leg2, target=DEFAULT_TARGET):
    parts = target.split("/", 1)
    if len(parts) != 2:
        _reject("malformed target: %r" % target)
    try:
        total = int(parts[0])
        if int(parts[1]) != total:
            _reject("target must be n/n: %r" % target)
    except ValueError:
        _reject("malformed target: %r" % target)
    if leg1["ids"] != leg2["ids"]:
        _reject("legs ran different benchmark task sets: %s vs %s"
                % (leg1["env"].get("benchmark"), leg2["env"].get("benchmark")))
    if leg1["mechanism"] == leg2["mechanism"]:
        _reject("legs used the same runner mechanism %r; the second leg "
                "is not an independent reconfirmation" % leg1["mechanism"])
    # Card C-9117 leg2 independence bar -- three pairwise refusals:
    # distinct leg process; no shared candidate cache; distinct window
    # OR distinct transport (same BOTH = one execution channel).
    i1, i2 = leg1["independence"], leg2["independence"]
    if i1["leg_process_id"] == i2["leg_process_id"]:
        _reject("verdict_composer_refused_not_distinct_process: both "
                "legs declare leg_process_id %r (bar: %s)"
                % (i1["leg_process_id"], INDEPENDENCE_BAR))
    if i1["candidate_cache_id"] == i2["candidate_cache_id"]:
        _reject("verdict_composer_refused_shared_candidate_cache: both "
                "legs declare candidate_cache_id %r (bar: %s)"
                % (i1["candidate_cache_id"], INDEPENDENCE_BAR))
    if (i1["window_id"] == i2["window_id"]
            and i1["transport"] == i2["transport"]):
        _reject("verdict_composer_refused_same_window_and_transport: "
                "both legs declare window_id %r transport %r (bar: %s)"
                % (i1["window_id"], i1["transport"], INDEPENDENCE_BAR))
    # C-9046: a cross-budget pair is refused outright -- the beats_base
    # arithmetic over legs run at different token ceilings is not a
    # like-for-like comparison.
    if leg1["budget"] != leg2["budget"]:
        _reject("verdict_composer_refused_budget_mismatch: leg1 "
                "max_new_tokens=%d != leg2 max_new_tokens=%d (C-9046 "
                "cross-budget compose refused)" %
                (leg1["budget"], leg2["budget"]))
    # C-9110: the done-criteria candidate-vs-base differ gate,
    # per leg, before any pass arithmetic runs.
    gate1 = candidates_differ_gate("leg1",
                                   leg1["candidates_vs_base"])
    gate2 = candidates_differ_gate("leg2",
                                   leg2["candidates_vs_base"])
    disagree = sorted(
        tid for tid in leg1["adapter"]
        if leg1["adapter"][tid] != leg2["adapter"][tid]
        or leg1["base"][tid] != leg2["base"][tid])
    if disagree:
        _reject("legs disagree on per-task pass: %s" % disagree)
    a_pass = sum(1 for v in leg1["adapter"].values() if v)
    b_pass = sum(1 for v in leg1["base"].values() if v)
    # Pinned metric (card C-0013): pass-count primary; composite tiebreak
    # on equal pass-counts (leg 1 supplies the composite inputs; the legs
    # already agree on every per-task pass); a tie with missing composite
    # inputs raises -> NO verdict file (fail-closed, metric #3).
    try:
        beats, rule = pinned_beats_base(
            "%d/%d" % (a_pass, total), "%d/%d" % (b_pass, total),
            composite_adapter=leg1["composite_adapter"],
            composite_base=leg1["composite_base"])
    except BeatsBaseError as exc:
        _reject("beats_base pinned metric refused: %s" % exc)
    beats_base = bool(beats)
    # C-0049: per-task fail-closed grading -- contained-poison evidence
    # from EITHER leg marks the task fail_closed in the verdict; pass
    # counting itself never changes.
    poison = dict()
    for leg in (leg1, leg2):
        for marks in leg["fail_marks"].values():
            for tid, reasons in marks.items():
                poison.setdefault(tid, []).extend(reasons)
    per_task = dict()
    for tid in leg1["adapter"]:
        entry = dict(
            adapter_pass=leg1["adapter"][tid],
            base_pass=leg1["base"][tid])
        if tid in poison:
            entry["fail_closed"] = True
            entry["fail_reason"] = poison[tid]
        per_task[tid] = entry
    holdout_sha, scorer_shas = compute_sha_pins()
    # C-0057 fire drill: the done-check (goal_done) refuses verdicts
    # without a truthy scorer_version tag (pre-sanitize verdicts can
    # never retire the goal) -- but the composer never emitted one, so
    # a REAL composed verdict could never satisfy the finish line even
    # at a perfect 18/18. Stamp a deterministic tag derived from the
    # pinned holdout sha; the sha-pin check separately guarantees the
    # pins match the canonical manifest, so the tag adds no bypass.
    scorer_version = "holdout-freeze-" + str(holdout_sha)[:12]
    # C-9119: base-model identity gate. The GOAL pins the model; the
    # legs' operator-typed base_model field is a claim, not evidence.
    # Both legs must carry a PROVEN Qwen3.8-27B identity and agree;
    # any refusal forces goal_done NO with the named reason stamped in
    # the verdict file (never a silent pass, never a hard reject: the
    # evidence still composes for audit).
    id1, id2 = leg1["model_identity"], leg2["model_identity"]
    identity_violation = id1["violation"] or id2["violation"]
    if identity_violation is None and id1["base_model"] != id2["base_model"]:
        identity_violation = ("model_identity_violation: leg_base_model_"
                              "disagreement (%r vs %r)"
                              % (id1["base_model"], id2["base_model"]))
    model_admissible = identity_violation is None
    return {
        "pass_adapter": "%d/%d" % (a_pass, total),
        "pass_base": "%d/%d" % (b_pass, total),
        "beats_base": beats_base,
        "scorer_version": scorer_version,
        "beats_base_rule": rule,
        "holdout_sha256": holdout_sha,
        "scorer_shas": scorer_shas,
        "composite_adapter": leg1["composite_adapter"],
        "composite_base": leg1["composite_base"],
        "meets_goal": ("%d/%d" % (a_pass, total)) == target and beats_base,
        # C-9119: model identity stamp + gate. goal_done YES is only
        # reachable when the identity is proven for THIS goal's model.
        "model_identity": id1,
        "model_admissible": model_admissible,
        "model_identity_violation": identity_violation,
        "goal_done": ("YES" if (model_admissible and
                                ("%d/%d" % (a_pass, total)) == target
                                and beats_base) else "NO"),
        "goal_target": target,
        "adapter_applied_marker": leg1["env"].get("adapter_applied_marker"),
        "adapter_probe_differs_marker": leg1["env"].get("adapter_probe_differs_marker"),
        "independent_second_leg": True,
        # C-9117: the enforced bar + each leg's recorded evidence, so
        # the done-check can audit independence without re-deriving it.
        "independence_bar": INDEPENDENCE_BAR,
        # C-9059: per-leg recorded candidates-differ-from-base evidence.
        # Absent artifact reads UNKNOWN; recording the probe never gates
        # the compose (the C-9046 budget refusal above is untouched).
        "candidates_differ_from_base": {
            "leg1": leg1["candidates_differ"],
            "leg2": leg2["candidates_differ"],
        },
        # C-9110: the mechanized differ-gate outcome per leg.
        "candidates_vs_base_gate": {"leg1": gate1, "leg2": gate2},
        "leg1": {
            "ref": leg1["path"],
            "runner_mechanism": leg1["mechanism"],
            "max_new_tokens": leg1["budget"],
            "box": leg1["env"].get("box"),
            "independence": leg1["independence"],
            "markers": {"adapter_applied": leg1["env"].get("adapter_applied_marker"),
                        "adapter_probe_differs": leg1["env"].get("adapter_probe_differs_marker")},
        },
        "leg2": {
            "ref": leg2["path"],
            "runner_mechanism": leg2["mechanism"],
            "max_new_tokens": leg2["budget"],
            "box": leg2["env"].get("box"),
            "independence": leg2["independence"],
            "markers": {"adapter_applied": leg2["env"].get("adapter_applied_marker"),
                        "adapter_probe_differs": leg2["env"].get("adapter_probe_differs_marker")},
        },
        "per_task": per_task,
        "composed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def write_verdict(verdict, out_path):
    """Atomic write; the verdict file appears whole or not at all."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    try:
        tmp.write_text(
            json.dumps(verdict, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
        tmp.replace(out)
    except Exception:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise
    return out


def compose_verdict(leg1_path, leg2_path, out_path, target=DEFAULT_TARGET):
    parts = target.split("/", 1)
    if len(parts) != 2:
        _reject("malformed target: %r" % target)
    try:
        total = int(parts[0])
        if int(parts[1]) != total:
            _reject("target must be n/n: %r" % target)
    except ValueError:
        _reject("malformed target: %r" % target)
    leg1 = load_leg(leg1_path, total)
    leg2 = load_leg(leg2_path, total)
    verdict = compose(leg1, leg2, target)
    write_verdict(verdict, out_path)
    return verdict


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Compose the fail-closed 18-task holdout verdict "
                    "from two independent legs (Card C-0012).")
    parser.add_argument("--leg1", required=True, help="leg1 envelope JSON")
    parser.add_argument("--leg2", required=True, help="leg2 envelope JSON")
    parser.add_argument("--out", required=True, help="verdict JSON to write")
    parser.add_argument("--target", default=DEFAULT_TARGET,
                        help="goal pass target, e.g. 18/18")
    args = parser.parse_args(argv)
    try:
        verdict = compose_verdict(args.leg1, args.leg2, args.out, args.target)
    except VerdictRejected as exc:
        print("VERDICT_REJECTED: %s" % exc, file=sys.stderr)
        return 1
    print(json.dumps({
        "stage": "verdict_written",
        "out": str(args.out),
        "pass_adapter": verdict["pass_adapter"],
        "beats_base": verdict["beats_base"],
        "meets_goal": verdict["meets_goal"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
