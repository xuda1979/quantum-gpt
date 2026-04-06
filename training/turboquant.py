from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Optional

import torch
import torch.nn.functional as F
from transformers.cache_utils import DynamicCache


def _normalize_dtype(value: Any) -> torch.dtype:
    if isinstance(value, torch.dtype):
        return value
    if isinstance(value, str):
        name = value.replace("torch.", "")
        dtype = getattr(torch, name, None)
        if isinstance(dtype, torch.dtype):
            return dtype
    return torch.float16


def _resolve_group_size(config: "TurboQuantConfig") -> int:
    return max(1, int(config.group_size or config.q_group_size or 64))


def _resolve_axis(axis: int, ndim: int) -> int:
    if ndim <= 0:
        return -1
    if axis in (0, -1, ndim - 1):
        return ndim - 1
    if ndim >= 2 and axis in (1, -2, ndim - 2):
        return ndim - 2
    if -ndim <= axis < ndim:
        return axis % ndim
    return ndim - 1


def _next_power_of_two(value: int) -> int:
    if value <= 1:
        return 1
    return 1 << (value - 1).bit_length()


def _hadamard_last_dim(tensor: torch.Tensor) -> torch.Tensor:
    width = tensor.shape[-1]
    if width == 0:
        return tensor
    target = _next_power_of_two(width)
    if target != width:
        tensor = F.pad(tensor, (0, target - width))
    original_shape = tensor.shape
    output = tensor.reshape(-1, target)
    step = 1
    while step < target:
        output = output.reshape(-1, target // (2 * step), 2, step)
        left = output[:, :, 0, :]
        right = output[:, :, 1, :]
        output = torch.cat((left + right, left - right), dim=-1)
        step *= 2
    output = output / math.sqrt(target)
    return output.reshape(*original_shape[:-1], target)


def _rotation_signs(width: int, seed: int, device: torch.device) -> torch.Tensor:
    generator = torch.Generator(device="cpu")
    generator.manual_seed(int(seed))
    signs = torch.randint(0, 2, (width,), generator=generator, dtype=torch.int8)
    signs = signs.to(device=device)
    return torch.where(signs == 0, -torch.ones_like(signs), torch.ones_like(signs)).to(torch.float32)


def _canonical_rotation(mode: str) -> str:
    normalized = str(mode or "none").strip().lower()
    if normalized in {"none"}:
        return "none"
    if normalized in {"hadamard"}:
        return "hadamard"
    if normalized in {"random_hadamard", "hadamard_or_random", "random"}:
        return "random_hadamard"
    raise ValueError(f"Unsupported TurboQuant rotation mode: {mode}")


def _apply_rotation(
    tensor: torch.Tensor,
    *,
    mode: str,
    seed: int,
) -> tuple[torch.Tensor, int]:
    canonical = _canonical_rotation(mode)
    if canonical == "none":
        return tensor, tensor.shape[-1]
    width = tensor.shape[-1]
    target = _next_power_of_two(width)
    rotated = tensor
    if target != width:
        rotated = F.pad(rotated, (0, target - width))
    if canonical == "random_hadamard":
        rotated = rotated * _rotation_signs(target, seed=seed, device=rotated.device).to(rotated.dtype)
    return _hadamard_last_dim(rotated), target


def _inverse_rotation(
    tensor: torch.Tensor,
    *,
    mode: str,
    seed: int,
) -> torch.Tensor:
    canonical = _canonical_rotation(mode)
    if canonical == "none":
        return tensor
    restored = _hadamard_last_dim(tensor)
    if canonical == "random_hadamard":
        restored = restored * _rotation_signs(restored.shape[-1], seed=seed, device=restored.device).to(restored.dtype)
    return restored


def _quantize_symmetric(groups: torch.Tensor, nbits: int) -> tuple[torch.Tensor, torch.Tensor]:
    if nbits not in {1, 2, 4, 8}:
        raise ValueError(f"TurboQuant currently supports nbits in {{1, 2, 4, 8}}, got {nbits}.")
    if nbits == 1:
        scale = groups.abs().amax(dim=-1, keepdim=True).clamp_min(1e-6)
        quantized = torch.where(groups >= 0, torch.ones_like(groups), -torch.ones_like(groups))
        return quantized.to(torch.int8), scale
    qmax = (1 << (nbits - 1)) - 1
    scale = (groups.abs().amax(dim=-1, keepdim=True) / max(qmax, 1)).clamp_min(1e-6)
    quantized = torch.round(groups / scale).clamp(-qmax, qmax)
    return quantized.to(torch.int8), scale


@dataclass
class _QuantizedSlice:
    primary: torch.Tensor
    primary_scale: torch.Tensor
    secondary: Optional[torch.Tensor]
    secondary_scale: Optional[torch.Tensor]
    original_shape: tuple[int, ...]
    axis: int
    pad_last_dim: int
    rotated_last_dim: int
    nbits: int
    secondary_nbits: int
    group_size: int
    rotation: str
    seed: int
    restore_dtype: torch.dtype

    def dequantize(self) -> torch.Tensor:
        tensor = self.primary.to(self.primary_scale.dtype) * self.primary_scale
        if self.secondary is not None and self.secondary_scale is not None:
            tensor = tensor + self.secondary.to(self.secondary_scale.dtype) * self.secondary_scale
        tensor = tensor.reshape(*self.original_shape[:-1], self.rotated_last_dim)
        tensor = _inverse_rotation(tensor, mode=self.rotation, seed=self.seed)
        if self.pad_last_dim:
            tensor = tensor[..., : self.original_shape[-1]]
        tensor = tensor.movedim(-1, self.axis)
        return tensor.to(self.restore_dtype)

    def index_select(self, indices: torch.Tensor) -> "_QuantizedSlice":
        device_indices = indices.to(self.primary.device)
        secondary = None if self.secondary is None else self.secondary.index_select(0, device_indices)
        secondary_scale = (
            None if self.secondary_scale is None else self.secondary_scale.index_select(0, device_indices)
        )
        return _QuantizedSlice(
            primary=self.primary.index_select(0, device_indices),
            primary_scale=self.primary_scale.index_select(0, device_indices),
            secondary=secondary,
            secondary_scale=secondary_scale,
            original_shape=(int(indices.numel()), *self.original_shape[1:]),
            axis=self.axis,
            pad_last_dim=self.pad_last_dim,
            rotated_last_dim=self.rotated_last_dim,
            nbits=self.nbits,
            secondary_nbits=self.secondary_nbits,
            group_size=self.group_size,
            rotation=self.rotation,
            seed=self.seed,
            restore_dtype=self.restore_dtype,
        )

    def repeat_interleave(self, repeats: int) -> "_QuantizedSlice":
        secondary = None if self.secondary is None else self.secondary.repeat_interleave(repeats, dim=0)
        secondary_scale = (
            None if self.secondary_scale is None else self.secondary_scale.repeat_interleave(repeats, dim=0)
        )
        return _QuantizedSlice(
            primary=self.primary.repeat_interleave(repeats, dim=0),
            primary_scale=self.primary_scale.repeat_interleave(repeats, dim=0),
            secondary=secondary,
            secondary_scale=secondary_scale,
            original_shape=(self.original_shape[0] * repeats, *self.original_shape[1:]),
            axis=self.axis,
            pad_last_dim=self.pad_last_dim,
            rotated_last_dim=self.rotated_last_dim,
            nbits=self.nbits,
            secondary_nbits=self.secondary_nbits,
            group_size=self.group_size,
            rotation=self.rotation,
            seed=self.seed,
            restore_dtype=self.restore_dtype,
        )


TurboQuantTensor = _QuantizedSlice


@dataclass
class TurboQuantConfig:
    backend: str = "turboquant"
    nbits: int = 4
    secondary_nbits: int = 1
    group_size: int = 64
    q_group_size: int = 64
    residual_length: int = 128
    axis_key: int = 0
    axis_value: int = 0
    rotation: str = "hadamard"
    seed: int = 0
    device: str = "cpu"
    compute_dtype: Any = torch.float16

    def __post_init__(self) -> None:
        self.nbits = int(self.nbits)
        self.secondary_nbits = int(self.secondary_nbits)
        self.group_size = int(self.group_size or self.q_group_size or 64)
        self.q_group_size = int(self.q_group_size or self.group_size or 64)
        self.residual_length = max(0, int(self.residual_length))
        self.seed = int(self.seed)
        self.rotation = _canonical_rotation(self.rotation)
        self.compute_dtype = _normalize_dtype(self.compute_dtype)


TurboQuantCacheConfig = TurboQuantConfig


def turboquant_quantize(
    tensor: torch.Tensor,
    config: TurboQuantConfig,
    *,
    layer_idx: int = 0,
    stream: str = "key",
) -> TurboQuantTensor:
    helper = TurboQuantCache(config=config)
    axis_hint = config.axis_key if stream == "key" else config.axis_value
    packed = helper._quantize_tensor(tensor, axis_hint=axis_hint, seed_offset=layer_idx + (0 if stream == "key" else 10_000))
    if packed is None:
        raise ValueError("Cannot quantize an empty tensor.")
    return packed


def turboquant_dequantize(packed: TurboQuantTensor) -> torch.Tensor:
    return packed.dequantize()


class TurboQuantCache(DynamicCache):
    """Experimental TurboQuant-style cache with pure PyTorch KV compression."""

    def __init__(
        self,
        config: Optional[TurboQuantConfig] = None,
        cache_config: Optional[TurboQuantConfig] = None,
        model: Any = None,
        device: Any = None,
        compute_dtype: Any = None,
    ) -> None:
        super().__init__()
        self._seen_tokens = 0
        self.key_cache: list[Any] = []
        self.value_cache: list[Any] = []
        self.config = cache_config or config or TurboQuantConfig()
        if compute_dtype is not None:
            self.config.compute_dtype = _normalize_dtype(compute_dtype)
        if device is not None:
            self.config.device = str(device)
        if model is not None and getattr(model, "dtype", None) is not None and compute_dtype is None:
            self.config.compute_dtype = _normalize_dtype(model.dtype)
        self._quantized_key_cache: list[_QuantizedSlice | None] = []
        self._quantized_value_cache: list[_QuantizedSlice | None] = []
        self._layer_lengths: list[int] = []

    def _ensure_layer(self, layer_idx: int) -> None:
        while len(self.key_cache) <= layer_idx:
            self.key_cache.append([])
            self.value_cache.append([])
            self._quantized_key_cache.append(None)
            self._quantized_value_cache.append(None)
            self._layer_lengths.append(0)

    def _quantize_tensor(
        self,
        tensor: torch.Tensor,
        *,
        axis_hint: int,
        seed_offset: int = 0,
    ) -> _QuantizedSlice | None:
        if tensor.numel() == 0 or tensor.shape[-2] == 0:
            return None
        axis = _resolve_axis(axis_hint, tensor.ndim)
        work = tensor.movedim(axis, -1).to(self.config.compute_dtype)
        work, rotated_last_dim = _apply_rotation(work, mode=self.config.rotation, seed=self.config.seed + seed_offset)
        original_shape = tuple(tensor.movedim(axis, -1).shape)
        group_size = _resolve_group_size(self.config)
        pad_last_dim = rotated_last_dim - original_shape[-1]
        padded_last_dim = rotated_last_dim
        if padded_last_dim % group_size != 0:
            extra_pad = (-padded_last_dim) % group_size
            work = F.pad(work, (0, extra_pad))
            padded_last_dim += extra_pad
        grouped = work.reshape(*work.shape[:-1], padded_last_dim // group_size, group_size)
        primary, primary_scale = _quantize_symmetric(grouped, self.config.nbits)
        secondary = None
        secondary_scale = None
        if self.config.secondary_nbits > 0:
            reconstructed = primary.to(primary_scale.dtype) * primary_scale
            residual = grouped - reconstructed
            secondary, secondary_scale = _quantize_symmetric(residual, self.config.secondary_nbits)
        return _QuantizedSlice(
            primary=primary,
            primary_scale=primary_scale,
            secondary=secondary,
            secondary_scale=secondary_scale,
            original_shape=original_shape,
            axis=axis,
            pad_last_dim=pad_last_dim,
            rotated_last_dim=rotated_last_dim,
            nbits=self.config.nbits,
            secondary_nbits=self.config.secondary_nbits,
            group_size=group_size,
            rotation=self.config.rotation,
            seed=self.config.seed + seed_offset,
            restore_dtype=tensor.dtype,
        )

    def _split_prefix_and_residual(self, tensor: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        residual_length = self.config.residual_length
        total = tensor.shape[-2]
        if residual_length <= 0:
            empty = tensor[..., :0, :].contiguous()
            return tensor.contiguous(), empty
        if total <= residual_length:
            empty = tensor[..., :0, :].contiguous()
            return empty, tensor.contiguous()
        split = total - residual_length
        return tensor[..., :split, :].contiguous(), tensor[..., split:, :].contiguous()

    def _compose_full(
        self,
        quantized: _QuantizedSlice | None,
        residual: Any,
        current: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        pieces: list[torch.Tensor] = []
        if quantized is not None:
            restored = quantized.dequantize()
            if current is not None:
                restored = restored.to(current.device, dtype=current.dtype)
            pieces.append(restored)
        if isinstance(residual, torch.Tensor) and residual.numel() > 0:
            if current is not None:
                residual = residual.to(current.device, dtype=current.dtype)
            pieces.append(residual)
        if current is not None and current.numel() > 0:
            pieces.append(current)
        if not pieces:
            if current is not None:
                return current
            return torch.zeros(0, dtype=self.config.compute_dtype)
        if len(pieces) == 1:
            return pieces[0].contiguous()
        return torch.cat(pieces, dim=-2).contiguous()

    def _materialize_layer(self, layer_idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        self._ensure_layer(layer_idx)
        return (
            self._compose_full(self._quantized_key_cache[layer_idx], self.key_cache[layer_idx]),
            self._compose_full(self._quantized_value_cache[layer_idx], self.value_cache[layer_idx]),
        )

    def _set_layer_from_full(self, layer_idx: int, key_states: torch.Tensor, value_states: torch.Tensor) -> None:
        self._ensure_layer(layer_idx)
        key_prefix, key_residual = self._split_prefix_and_residual(key_states)
        value_prefix, value_residual = self._split_prefix_and_residual(value_states)
        self._quantized_key_cache[layer_idx] = self._quantize_tensor(
            key_prefix,
            axis_hint=self.config.axis_key,
            seed_offset=layer_idx,
        )
        self._quantized_value_cache[layer_idx] = self._quantize_tensor(
            value_prefix,
            axis_hint=self.config.axis_value,
            seed_offset=layer_idx + 10_000,
        )
        self.key_cache[layer_idx] = key_residual
        self.value_cache[layer_idx] = value_residual
        self._layer_lengths[layer_idx] = key_states.shape[-2]

    def update(
        self,
        key_states: torch.Tensor,
        value_states: torch.Tensor,
        layer_idx: int,
        cache_kwargs: Optional[dict[str, Any]] = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        del cache_kwargs
        if layer_idx == 0:
            self._seen_tokens += key_states.shape[-2]
        self._ensure_layer(layer_idx)
        full_keys = self._compose_full(self._quantized_key_cache[layer_idx], self.key_cache[layer_idx], key_states)
        full_values = self._compose_full(self._quantized_value_cache[layer_idx], self.value_cache[layer_idx], value_states)
        self._set_layer_from_full(layer_idx, full_keys, full_values)
        return full_keys, full_values

    def get_seq_length(self, layer_idx: Optional[int] = 0) -> int:
        target_layer = 0 if layer_idx is None else int(layer_idx)
        if target_layer < 0 or target_layer >= len(self._layer_lengths):
            return 0
        return int(self._layer_lengths[target_layer])

    def get_max_cache_shape(self) -> Optional[int]:
        return None

    def reorder_cache(self, beam_idx: torch.LongTensor) -> None:
        for layer_idx in range(len(self.key_cache)):
            if isinstance(self.key_cache[layer_idx], torch.Tensor) and self.key_cache[layer_idx].numel() > 0:
                device_indices = beam_idx.to(self.key_cache[layer_idx].device)
                self.key_cache[layer_idx] = self.key_cache[layer_idx].index_select(0, device_indices)
                self.value_cache[layer_idx] = self.value_cache[layer_idx].index_select(0, device_indices)
            if self._quantized_key_cache[layer_idx] is not None:
                self._quantized_key_cache[layer_idx] = self._quantized_key_cache[layer_idx].index_select(beam_idx)
            if self._quantized_value_cache[layer_idx] is not None:
                self._quantized_value_cache[layer_idx] = self._quantized_value_cache[layer_idx].index_select(beam_idx)

    def crop(self, max_length: int) -> None:
        current_length = self.get_seq_length()
        if max_length < 0:
            max_length = current_length - abs(max_length)
        if current_length <= max_length:
            return
        max_length = max(0, int(max_length))
        self._seen_tokens = max_length
        for layer_idx in range(len(self.key_cache)):
            if self._layer_lengths[layer_idx] == 0:
                continue
            full_keys, full_values = self._materialize_layer(layer_idx)
            self._set_layer_from_full(layer_idx, full_keys[..., :max_length, :], full_values[..., :max_length, :])

    def batch_repeat_interleave(self, repeats: int) -> None:
        for layer_idx in range(len(self.key_cache)):
            if isinstance(self.key_cache[layer_idx], torch.Tensor) and self.key_cache[layer_idx].numel() > 0:
                self.key_cache[layer_idx] = self.key_cache[layer_idx].repeat_interleave(repeats, dim=0)
                self.value_cache[layer_idx] = self.value_cache[layer_idx].repeat_interleave(repeats, dim=0)
            if self._quantized_key_cache[layer_idx] is not None:
                self._quantized_key_cache[layer_idx] = self._quantized_key_cache[layer_idx].repeat_interleave(repeats)
            if self._quantized_value_cache[layer_idx] is not None:
                self._quantized_value_cache[layer_idx] = self._quantized_value_cache[layer_idx].repeat_interleave(repeats)

    def batch_select_indices(self, indices: torch.Tensor) -> None:
        for layer_idx in range(len(self.key_cache)):
            if isinstance(self.key_cache[layer_idx], torch.Tensor) and self.key_cache[layer_idx].numel() > 0:
                device_indices = indices.to(self.key_cache[layer_idx].device)
                self.key_cache[layer_idx] = self.key_cache[layer_idx].index_select(0, device_indices)
                self.value_cache[layer_idx] = self.value_cache[layer_idx].index_select(0, device_indices)
            if self._quantized_key_cache[layer_idx] is not None:
                self._quantized_key_cache[layer_idx] = self._quantized_key_cache[layer_idx].index_select(indices)
            if self._quantized_value_cache[layer_idx] is not None:
                self._quantized_value_cache[layer_idx] = self._quantized_value_cache[layer_idx].index_select(indices)

    def batch_split(self, full_batch_size: int, split_size: int, num_hidden_layers: int = None) -> list["TurboQuantCache"]:
        del full_batch_size, num_hidden_layers
        if len(self.key_cache) == 0:
            return []
        batch_size = 0
        for layer_idx in range(len(self.key_cache)):
            full_keys, _ = self._materialize_layer(layer_idx)
            if full_keys.ndim == 4:
                batch_size = full_keys.shape[0]
                break
        splits: list[TurboQuantCache] = []
        for start in range(0, batch_size, split_size):
            split_cache = TurboQuantCache(config=TurboQuantConfig(**self.config.__dict__.copy()))
            split_cache._seen_tokens = self._seen_tokens
            for layer_idx in range(len(self.key_cache)):
                if self._layer_lengths[layer_idx] == 0:
                    split_cache._ensure_layer(layer_idx)
                    continue
                full_keys, full_values = self._materialize_layer(layer_idx)
                split_cache._set_layer_from_full(
                    layer_idx,
                    full_keys[start : start + split_size].contiguous(),
                    full_values[start : start + split_size].contiguous(),
                )
            splits.append(split_cache)
        return splits

    @classmethod
    def from_batch_splits(
        cls,
        splits: list["TurboQuantCache"],
        num_hidden_layers: int = None,
    ) -> "TurboQuantCache":
        del num_hidden_layers
        if not splits:
            return cls()
        cache = cls(config=TurboQuantConfig(**splits[0].config.__dict__.copy()))
        cache._seen_tokens = splits[0]._seen_tokens
        max_layers = max(len(split.key_cache) for split in splits)
        for layer_idx in range(max_layers):
            layer_keys: list[torch.Tensor] = []
            layer_values: list[torch.Tensor] = []
            for split in splits:
                if layer_idx >= len(split.key_cache) or split.get_seq_length(layer_idx) == 0:
                    continue
                full_keys, full_values = split._materialize_layer(layer_idx)
                layer_keys.append(full_keys)
                layer_values.append(full_values)
            cache._ensure_layer(layer_idx)
            if layer_keys:
                cache._set_layer_from_full(
                    layer_idx,
                    torch.cat(layer_keys, dim=0).contiguous(),
                    torch.cat(layer_values, dim=0).contiguous(),
                )
        return cache


TurboQuantKVCache = TurboQuantCache


def build_turboquant_config(**kwargs: Any) -> TurboQuantConfig:
    return TurboQuantConfig(**kwargs)


def build_turboquant_cache(
    config: Optional[TurboQuantConfig] = None,
    cache_config: Optional[TurboQuantConfig] = None,
    **kwargs: Any,
) -> TurboQuantCache:
    return TurboQuantCache(config=config, cache_config=cache_config, **kwargs)


def create_turboquant_cache(
    config: Optional[TurboQuantConfig] = None,
    cache_config: Optional[TurboQuantConfig] = None,
    **kwargs: Any,
) -> TurboQuantCache:
    return build_turboquant_cache(config=config, cache_config=cache_config, **kwargs)
