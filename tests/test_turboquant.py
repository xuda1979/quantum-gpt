from __future__ import annotations

import torch

from training.turboquant import (
    TurboQuantCache,
    TurboQuantConfig,
    TurboQuantKVCache,
    build_turboquant_cache,
    build_turboquant_config,
    create_turboquant_cache,
    turboquant_dequantize,
    turboquant_quantize,
)


def _sample_states(batch: int = 2, seq: int = 3, dim: int = 8) -> tuple[torch.Tensor, torch.Tensor]:
    key = torch.arange(batch * 2 * seq * dim, dtype=torch.float32).reshape(batch, 2, seq, dim) / 31.0
    value = torch.flip(key, dims=(-1,)) * 0.5
    return key, value


def test_cache_builders_expose_expected_aliases() -> None:
    config = build_turboquant_config(nbits=4, residual_length=2, rotation="none", compute_dtype="float32")
    cache = build_turboquant_cache(config=config)
    cache2 = create_turboquant_cache(cache_config=config)
    assert isinstance(config, TurboQuantConfig)
    assert isinstance(cache, TurboQuantCache)
    assert isinstance(cache2, TurboQuantKVCache)


def test_quantize_dequantize_shape_dtype_and_seed_determinism() -> None:
    source, _ = _sample_states(batch=1, seq=4)
    config = TurboQuantConfig(
        nbits=4,
        secondary_nbits=1,
        group_size=4,
        rotation="random_hadamard",
        seed=2026,
        compute_dtype=torch.float32,
    )
    first = turboquant_quantize(source, config, stream="key")
    second = turboquant_quantize(source, config, stream="key")
    restored = turboquant_dequantize(first)

    assert restored.shape == source.shape
    assert restored.dtype == source.dtype
    assert torch.equal(first.primary, second.primary)
    assert torch.allclose(first.primary_scale, second.primary_scale)


def test_cache_update_tracks_sequence_and_residual_window() -> None:
    cache = TurboQuantCache(
        config=TurboQuantConfig(
            nbits=4,
            secondary_nbits=1,
            residual_length=2,
            group_size=4,
            rotation="none",
            compute_dtype=torch.float32,
        )
    )
    key_a, value_a = _sample_states(seq=3)
    key_b, value_b = _sample_states(seq=2)

    full_a_k, full_a_v = cache.update(key_a, value_a, layer_idx=0)
    full_b_k, full_b_v = cache.update(key_b, value_b, layer_idx=0)

    assert full_a_k.shape[-2] == 3
    assert full_a_v.shape[-2] == 3
    assert full_b_k.shape[-2] == 5
    assert full_b_v.shape[-2] == 5
    assert cache.get_seq_length(0) == 5
    assert isinstance(cache.key_cache[0], torch.Tensor)
    assert cache.key_cache[0].shape[-2] == 2
    assert cache.value_cache[0].shape[-2] == 2
    assert cache._quantized_key_cache[0] is not None
    assert cache._quantized_value_cache[0] is not None


def test_cache_reorder_crop_and_select_keep_shapes_consistent() -> None:
    cache = TurboQuantCache(
        config=TurboQuantConfig(
            nbits=4,
            secondary_nbits=1,
            residual_length=2,
            group_size=4,
            rotation="none",
            compute_dtype=torch.float32,
        )
    )
    key_a, value_a = _sample_states(batch=2, seq=4)
    key_b, value_b = _sample_states(batch=2, seq=2)
    cache.update(key_a, value_a, layer_idx=0)
    cache.update(key_b, value_b, layer_idx=0)

    cache.reorder_cache(torch.tensor([1, 0]))
    materialized_k, materialized_v = cache._materialize_layer(0)
    assert materialized_k.shape == (2, 2, 6, 8)
    assert materialized_v.shape == (2, 2, 6, 8)

    cache.crop(4)
    assert cache.get_seq_length(0) == 4

    cache.batch_select_indices(torch.tensor([1]))
    materialized_k, _ = cache._materialize_layer(0)
    assert materialized_k.shape == (1, 2, 4, 8)
