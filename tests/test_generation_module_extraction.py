"""Architect lane #26: generation/fence-EOS module extraction identity pins.

The rollout lane's greedy-augmentation work builds on the new
``training/generation.py`` home; these pins guarantee the extraction was
behavior-identical: every name the trainer (and its suites) used before must
resolve to the SAME object in its new home, with spot-check behavior through
both module paths. The full behavioral contract stays with the existing suites
(test_grpo_trainer_generation_stop.py et al.) — this file only pins the
extraction wiring.
"""

from __future__ import annotations

import inspect

from training import generation, grpo_trainer

MOVED_NAMES = (
    "extract_code",
    "has_closed_code_fence",
    "StopAfterClosedCodeFence",
    "build_generation_diagnostics",
    "configured_eos_token_ids",
    "append_fence_stop_markers",
)


def test_trainer_reexports_generation_names_as_same_objects() -> None:
    """Re-export identity: a test/suite that does ``grpo_trainer.extract_code``
    must get the same object as ``training.generation.extract_code`` — a copy
    would silently fork behavior."""
    for name in MOVED_NAMES:
        assert getattr(grpo_trainer, name) is getattr(generation, name), name


def test_generation_module_defines_all_moved_names() -> None:
    for name in MOVED_NAMES:
        assert hasattr(generation, name)


def test_fence_open_re_constant_shared() -> None:
    assert generation._CODE_FENCE_OPEN_RE is grpo_trainer._CODE_FENCE_OPEN_RE


def test_extract_code_behavior_identical_through_both_paths() -> None:
    samples = [
        ("```python\nprint(1)\n```\ntrailing prose", "print(1)"),
        ("```Python\nx = 1\n```", "x = 1"),
        ("```python3\nx = 1\n```", "x = 1"),
        ("``` python \nx = 1\n```", "x = 1"),
        ("no fence here", "no fence here"),
        ("```\nx = 1\n```", "x = 1"),
    ]
    for text, expected in samples:
        assert generation.extract_code(text) == expected, text
        assert grpo_trainer.extract_code(text) == expected, text


def test_has_closed_code_fence_behavior() -> None:
    assert generation.has_closed_code_fence("```python\nx=1\n```")
    assert not generation.has_closed_code_fence("```python\nx=1")
    assert not generation.has_closed_code_fence("prose backticks ```")


def test_generation_module_is_py39_compile_safe() -> None:
    """The moved module must stay deployable in the canonical py3.9 venv: no
    py3.10-only zip keyword, and it pairs via the compat single home."""
    src = inspect.getsource(generation)
    assert "zip(..., strict=" not in src
    assert "from training.compat import strict_zip" in src
    assert "from __future__ import annotations" in src
