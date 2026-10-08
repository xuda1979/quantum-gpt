"""Tests for ``resolve_gradient_checkpointing_reentrant``.

Locks in the fix for the ASI3 / Qwen3.6-35B-A3B failure:

    RuntimeError: Function MmBackward0 returned an invalid gradient at
    index 1 - expected device meta but got npu:0

which is raised when ``gradient_checkpointing_enable`` runs with the
default ``use_reentrant=True`` on Ascend NPU + accelerate ``device_map``
+ ``low_cpu_mem_usage=True``. The helper must return ``False`` (force
non-reentrant) in exactly that case, ``True``/``False`` when the env
override is set, and ``None`` (let transformers pick its default)
otherwise.
"""

from __future__ import annotations

from training.qwen_sft_peft import resolve_gradient_checkpointing_reentrant


def test_npu_with_device_map_defaults_to_non_reentrant() -> None:
    """The actual ASI3 failure mode: NPU + balanced-layers device_map."""
    assert (
        resolve_gradient_checkpointing_reentrant(device="npu", has_device_map=True, env={}) is False
    )


def test_npu_without_device_map_returns_none() -> None:
    """DDP path (device_map={"": "npu:{rank}"}) still goes through the same
    code branch but every param lives on one device, so the reentrant fix is
    not strictly required — leave it to transformers' default."""
    assert (
        resolve_gradient_checkpointing_reentrant(device="npu", has_device_map=False, env={}) is None
    )


def test_cpu_returns_none() -> None:
    assert (
        resolve_gradient_checkpointing_reentrant(device="cpu", has_device_map=True, env={}) is None
    )


def test_cuda_returns_none() -> None:
    assert (
        resolve_gradient_checkpointing_reentrant(device="cuda", has_device_map=True, env={}) is None
    )


def test_env_force_reentrant() -> None:
    assert (
        resolve_gradient_checkpointing_reentrant(
            device="npu",
            has_device_map=True,
            env={"QWEN_SFT_GRADIENT_CHECKPOINTING_REENTRANT": "1"},
        )
        is True
    )


def test_env_force_non_reentrant() -> None:
    """Explicit opt-out should win even on cuda without device_map."""
    assert (
        resolve_gradient_checkpointing_reentrant(
            device="cuda",
            has_device_map=False,
            env={"QWEN_SFT_GRADIENT_CHECKPOINTING_REENTRANT": "0"},
        )
        is False
    )


def test_env_whitespace_is_stripped() -> None:
    assert (
        resolve_gradient_checkpointing_reentrant(
            device="npu",
            has_device_map=True,
            env={"QWEN_SFT_GRADIENT_CHECKPOINTING_REENTRANT": "  0  "},
        )
        is False
    )


def test_env_invalid_value_falls_through_to_auto() -> None:
    """Garbage values should not crash — they should fall through to the
    auto rule (NPU + device_map -> False)."""
    assert (
        resolve_gradient_checkpointing_reentrant(
            device="npu",
            has_device_map=True,
            env={"QWEN_SFT_GRADIENT_CHECKPOINTING_REENTRANT": "banana"},
        )
        is False
    )
    # And on cuda + no device_map, garbage should fall through to None.
    assert (
        resolve_gradient_checkpointing_reentrant(
            device="cuda",
            has_device_map=False,
            env={"QWEN_SFT_GRADIENT_CHECKPOINTING_REENTRANT": "banana"},
        )
        is None
    )
