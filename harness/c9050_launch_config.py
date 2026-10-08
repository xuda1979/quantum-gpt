"""C-9050: fail-closed resolver for the real Qwen3.8-27B training-leg launch config.

C-9004 (27B distillation training leg) bounced 3x; the only live scaffold was
a placeholder-model stub (C-9019: SomeOrg/some-model on cpu). This module is
the mechanical gate the card asks for: a launch config is only resolvable when

  - model_name resolves to the REAL Qwen3.8-27B snapshot (never a placeholder
    stub id, never the stale Qwen3.6-27B family), fail closed otherwise;
  - the run carries the eval_results.jsonl liveness contract written by
    training/grpo_trainer.py (the B-222 step-ladder instrument), fail closed
    when the config omits it or names a trainer that never produces it;
  - device pins to npu (C-9019 stub class).

eval_results_progress() is the post-launch half of acceptance 2: the run-dir
eval_results.jsonl must exist and advance >= min_steps with finite loss, or
the failure is NAMED (never a silent wedge).
"""

import json
import math
import os

CARD_ID = "C-9050"
REAL_27B_BASENAME = "Qwen3.8-27B"
STALE_27B_BASENAME = "Qwen3.6-27B"
# Keep in sync with harness/resource_probes.py STUB_MODEL_TOKENS (C-9019).
STUB_MODEL_TOKENS = ("someorg/", "some-model")
EVAL_RESULTS_FILENAME = "eval_results.jsonl"
LIVENESS_FIELD = "step"
# Only trainers that actually write eval_results.jsonl (grep EVAL_RESULTS_FILENAME).
EVAL_RESULTS_TRAINERS = ("training/grpo_trainer.py",)

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "state", "c9050", "launch_config.json"
)


class LaunchConfigError(RuntimeError):
    """Fail-closed refusal with a named reason (never a silent wedge)."""


def _fail(msg):
    raise LaunchConfigError(CARD_ID + " fail-closed: " + msg)


def launch_config_path():
    """Banked C-9050 launch config artifact."""
    return DEFAULT_CONFIG_PATH


def resolve_launch_config(cfg):
    """Validate a launch config dict; return a resolved copy or fail closed."""
    if not isinstance(cfg, dict):
        _fail("launch config not an object")
    model = cfg.get("model_name")
    if not isinstance(model, str) or not model.strip():
        _fail("model_name missing/empty")
    low = model.lower()
    for tok in STUB_MODEL_TOKENS:
        if tok in low:
            _fail("placeholder model_name=" + model + " (C-9019 stub signature)")
    if os.path.basename(model.rstrip("/")) != REAL_27B_BASENAME:
        _fail(
            "model_name does not resolve to the real "
            + REAL_27B_BASENAME
            + " snapshot (stale family "
            + STALE_27B_BASENAME
            + " or unknown id): "
            + model
        )
    if cfg.get("device") != "npu":
        _fail("device must be npu, got " + repr(cfg.get("device")))
    if cfg.get("eval_results_filename") != EVAL_RESULTS_FILENAME:
        _fail(
            "eval_results.jsonl liveness contract absent: config must pin"
            ' eval_results_filename="' + EVAL_RESULTS_FILENAME + '"'
        )
    if cfg.get("liveness_field") != LIVENESS_FIELD:
        _fail('liveness_field must be "' + LIVENESS_FIELD + '" (B-222 step ladder)')
    trainer = cfg.get("trainer")
    if trainer not in EVAL_RESULTS_TRAINERS:
        _fail(
            "trainer " + repr(trainer) + " does not write eval_results.jsonl;"
            " eval_results.jsonl writers: " + ", ".join(EVAL_RESULTS_TRAINERS)
        )
    resolved = dict(cfg)
    resolved["resolved_model_id"] = model
    return resolved


def resolve_launch_config_file(path):
    """Load + validate a launch config file, fail closed on absent/unparseable."""
    if not os.path.isfile(path):
        _fail("launch config absent: " + path)
    try:
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError) as e:
        _fail("launch config unparseable: " + path + ": " + repr(e))
    return resolve_launch_config(cfg)


def eval_results_progress(path, min_steps=2):
    """Acceptance 2: eval_results.jsonl exists and advances >= min_steps with
    finite loss. Returns a summary dict; every failure mode is NAMED."""
    if not os.path.isfile(path):
        _fail("eval_results.jsonl absent (no completed training-step evidence): " + path)
    rows = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError as e:
                _fail("eval_results.jsonl unparseable row %d: %r" % (lineno, e))
            if not isinstance(row, dict):
                _fail("eval_results.jsonl row %d not an object" % lineno)
            rows.append(row)
    if len(rows) < min_steps:
        _fail(
            "eval_results.jsonl advances only %d row(s), need >= %d steps" % (len(rows), min_steps)
        )
    losses = []
    for i, row in enumerate(rows[:min_steps], 1):
        loss = row.get("loss")
        if not isinstance(loss, (int, float)) or isinstance(loss, bool):
            _fail("eval_results.jsonl row %d has no finite loss field" % i)
        if math.isnan(loss) or math.isinf(loss):
            _fail("eval_results.jsonl row %d loss not finite: %r" % (i, loss))
        losses.append(loss)
    steps = [row.get(LIVENESS_FIELD) for row in rows[:min_steps]]
    return {"path": path, "steps_seen": len(rows), "first_steps": steps, "losses": losses}
