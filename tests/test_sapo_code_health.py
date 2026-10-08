"""QA/code-health lane: source-hygiene pins for training/ internals.

Each test here is a regression pin for a "silent lie" class found in the
2026-08-31 rolling QA sweep:

1. ``Sequence`` is used in three module-level signatures of
   ``training.grpo_trainer`` but never imported — ``typing.get_type_hints``
   raises NameError for anyone introspecting the trainer.
2. ``_clamp01`` was defined TWICE in ``training.grpo_utils`` (L831 dead, L1553
   live). A second definition silently shadowed the first; editing the dead
   copy would have no effect.
3. ``training.grpo_trainer`` re-exported ``split_batched_generations`` and
   ``FRONTIER_RL`` without any user — dead re-exports that pyflakes flags as
   unused imports. (The re-exports pinned by
   test_generation_module_extraction.py are deliberately kept.)
"""

from __future__ import annotations

import inspect
import re
import typing

from training import grpo_trainer, grpo_utils


def test_trainer_signatures_resolve_sequence_type_hints() -> None:
    """``Sequence[str]`` annotations in the batch-dim scorer signatures must
    resolve in the trainer's module namespace — introspection
    (typing.get_type_hints) is used by tooling and by the holdout eval lane's
    signature matchers.

    A probe function (exec'd into the trainer's module namespace, mirroring
    the real signatures' string-annotation resolution) checks the binding,
    because the real functions' ``dict[int, dict[str, float | None]] | None``
    return annotations cannot be evaluated on py3.9 (PEP 604 at runtime) and
    would mask the Sequence check with an unrelated TypeError."""
    from collections.abc import Sequence as _Sequence

    probe_src = (
        "from __future__ import annotations\n"
        "def _sapo_code_health_probe(codes: Sequence[str], evidences: Sequence[str])"
        " -> dict[str, object]:\n"
        "    return {}\n"
    )
    ns: dict = {}
    exec(compile(probe_src, "<sapo-code-health-probe>", "exec"), grpo_trainer.__dict__, ns)
    hints = typing.get_type_hints(ns["_sapo_code_health_probe"])
    assert hints["codes"].__origin__ is _Sequence
    assert hints["evidences"].__origin__ is _Sequence

    # The probe only matters if the real signatures actually use Sequence.
    src = inspect.getsource(grpo_trainer)
    for name in ("_model_batch_dim_scores", "_model_batch_dim_scores_dp4", "_run_dp4_batch_judge"):
        m = re.search(rf"def {name}\(.*?\)(?: -> .*?)?:", src, re.S)
        assert m is not None, name
        assert "Sequence[str]" in m.group(0), name


def test_grpo_utils_defines_clamp01_exactly_once() -> None:
    """Two definitions of ``_clamp01`` (the second shadowing the first) is a
    silent-lie trap: edits to the dead copy silently do nothing. Exactly one
    definition may exist."""
    src = inspect.getsource(grpo_utils)
    defs = re.findall(r"^def _clamp01\(", src, re.MULTILINE)
    assert len(defs) == 1, f"expected exactly one _clamp01 definition, found {len(defs)}"


def test_grpo_trainer_drops_unused_reexports() -> None:
    """``split_batched_generations`` lives in training.generation and
    ``FRONTIER_RL`` in training.grpo_utils; grpo_trainer re-exported them with
    no consumer. Dead re-exports invite drift (someone patches the copy in the
    wrong home). The pinned re-exports (extract_code, has_closed_code_fence,
    ...) are covered by test_generation_module_extraction.py and stay."""
    assert not hasattr(grpo_trainer, "split_batched_generations")
    assert not hasattr(grpo_trainer, "FRONTIER_RL")
