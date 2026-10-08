"""TDD RED->GREEN: configured_suppress_token_ids + rollout_suppress_logits_processor
must exist in training.generation (C-9433).

The functions are imported by grpo_trainer.py (commit b3404fe) but were never
defined in generation.py, causing 52 collection errors across the test suite.
"""

from __future__ import annotations

from training import generation


def test_configured_suppress_token_ids_exists() -> None:
    assert hasattr(generation, "configured_suppress_token_ids")


def test_rollout_suppress_logits_processor_exists() -> None:
    assert hasattr(generation, "rollout_suppress_logits_processor")


def test_configured_suppress_returns_set() -> None:
    """With a model whose EOS list includes its own bos/pad, suppression must
    return the bos/pad id but keep the genuine chat EOS sampleable."""
    import types

    model = types.SimpleNamespace(
        generation_config=types.SimpleNamespace(
            eos_token_id=[248046, 248044],
            bos_token_id=248044,
            pad_token_id=248044,
        ),
    )
    tokenizer = types.SimpleNamespace(eos_token_id=None)
    stop = generation.configured_eos_token_ids(model, tokenizer)
    suppress = generation.configured_suppress_token_ids(model, tokenizer, stop_eos_ids=stop)
    assert isinstance(suppress, set)
    assert 248044 in suppress
    assert 248046 not in suppress


def test_configured_suppress_empty_when_only_eos_is_bos() -> None:
    """If suppressing would empty the stop set, return empty."""
    import types

    model = types.SimpleNamespace(
        generation_config=types.SimpleNamespace(
            eos_token_id=[248044],
            bos_token_id=248044,
            pad_token_id=248044,
        ),
    )
    tokenizer = types.SimpleNamespace(eos_token_id=None)
    stop = generation.configured_eos_token_ids(model, tokenizer)
    suppress = generation.configured_suppress_token_ids(model, tokenizer, stop_eos_ids=stop)
    assert suppress == set()


def test_rollout_suppress_logits_processor_returns_callable() -> None:
    """rollout_suppress_logits_processor must return a logits processor."""
    proc = generation.rollout_suppress_logits_processor({248044})
    assert proc is not None
    if isinstance(proc, list):
        assert len(proc) > 0
        assert all(callable(p) for p in proc)
    else:
        assert callable(proc)


def test_rollout_suppress_logits_processor_empty_returns_none() -> None:
    """Empty suppress set should yield no processor."""
    proc = generation.rollout_suppress_logits_processor(set())
    assert proc is None or proc == []
