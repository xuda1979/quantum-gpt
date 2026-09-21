#!/usr/bin/env python3
"""Fail-closed holdout-leg marker computation (QG harness card C-9432).

C-9378 shipped run_holdout_leg1.py/run_holdout_leg2.py with the markers
unconditionally set to True after the probe subprocess returned 0. That is a
hardcoded fabrication: a probe that printed its banner but never actually
applied the adapter (or whose generation never diverged) would still be
marked pass.

Accepted-downstream truth (holdout_verdict.py) consumes only the envelope
booleans adapter_applied_marker / adapter_probe_differs_marker, so the
leg scripts MUST derive them from the probe actual structured evidence and
NOT from bare success codes or raw token substrings.

The fail-closed probe (eval_failclosed_probe.py) emits structured JSON stage
events into ITS OWN log (the leg log via _run_append):
  - {"stage": "adapter_applied", "adapter": <path>}   (only after
    the checked apply loads the adapter file and applies it; fails closed
    otherwise)
  - {"stage": "adapter_probe_differs", "adapter": <path>}   (only after
    the base-vs-adapter generation/logit probe is observed to differ)

This module turns a set of probe stage events into the two envelope markers,
fail-closed: every stage must be present AND its adapter field must match
the adapter the leg actually dispatched. Nothing is ever assumed True.
"""

from __future__ import annotations

import json
from pathlib import Path

STAGE_APPLIED = "adapter_applied"
STAGE_PROBE_DIFFERS = "adapter_probe_differs"


def _stage_events(text):
    """Return {stage: [adapter str, ...]} parsed from the log JSON lines.

    Only parses single-line JSON objects carrying a literal "stage" key so
    prose/log noise cannot fabricate a marker by accident.
    """
    events = {}
    for line in text.splitlines():
        line = line.strip()
        if not (line.startswith("{") and line.endswith("}")):
            continue
        try:
            obj = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(obj, dict):
            continue
        stage = obj.get("stage")
        if not isinstance(stage, str) or not stage:
            continue
        adapter = obj.get("adapter")
        if not isinstance(adapter, str):
            adapter = ""
        events.setdefault(stage, []).append(adapter)
    return events


def compute_holdout_markers(text, adapter):
    """Derive (adapter_applied, adapter_probe_differs) from probe stage events.

    Both markers are booleans, fail-closed (never assumed True):
      - adapter_applied       is True ONLY if the adapter file exists AND the
                               checked-apply stage event for that same adapter
                               appears in the probe log.
      - adapter_probe_differs is True ONLY if the probe-differs stage event for
                               that same adapter appears in the log.

    adapter may be a Path or str; the stage adapter field is compared as its
    string form so the match is exact against what the leg dispatched.
    """
    expected = str(adapter)
    events = _stage_events(text)

    applied_stages = events.get(STAGE_APPLIED, [])
    probe_stages = events.get(STAGE_PROBE_DIFFERS, [])

    # PEFT LoRA adapters are saved as a DIRECTORY (adapter_config.json +
    # adapter_model.safetensors), so existence accepts file or dir; fail-closed
    # keeps requiring the adapter to actually EXIST on disk.
    adapter_exists = bool(adapter) and Path(adapter).exists()

    adapter_applied = adapter_exists and expected in applied_stages
    adapter_probe_differs = bool(probe_stages) and expected in probe_stages
    return adapter_applied, adapter_probe_differs


def marker_from_text(text, marker_token, adapter):
    """Back-compat: marker from a hyphenated banner token plus stage evidence.

    Retained for callers that only carry the banner tokens; delegates the real
    truth to compute_holdout_markers so behaviour stays fail-closed.
    """
    applied, differs = compute_holdout_markers(text, adapter)
    if marker_token == "adapter-applied":
        return applied
    if marker_token == "adapter-probe-differs":
        return differs
    return False
