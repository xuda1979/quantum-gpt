from types import SimpleNamespace

from training.qwen_sft_peft import build_balanced_npu_layer_device_map


def _language_layer_devices(device_map: dict[str, str], count: int) -> list[str]:
    return [device_map[f"model.language_model.layers.{index}"] for index in range(count)]


def test_eight_npu_map_uses_every_visible_device() -> None:
    config = SimpleNamespace(text_config=SimpleNamespace(num_hidden_layers=64))

    device_map = build_balanced_npu_layer_device_map(config, list(range(8)))
    layer_devices = _language_layer_devices(device_map, 64)

    assert set(layer_devices) == {f"npu:{index}" for index in range(8)}
    assert [layer_devices.count(f"npu:{index}") for index in range(8)] == [8] * 8


def test_four_npu_map_preserves_measured_qwen36_balance() -> None:
    config = SimpleNamespace(text_config=SimpleNamespace(num_hidden_layers=64))

    device_map = build_balanced_npu_layer_device_map(config, list(range(4)))
    layer_devices = _language_layer_devices(device_map, 64)

    assert [layer_devices.count(f"npu:{index}") for index in range(4)] == [13, 18, 18, 15]


def test_cpu_offload_places_only_trailing_fraction_on_cpu() -> None:
    config = SimpleNamespace(text_config=SimpleNamespace(num_hidden_layers=20))

    device_map = build_balanced_npu_layer_device_map(config, [0, 1], cpu_offload_fraction=0.25)
    layer_devices = _language_layer_devices(device_map, 20)

    assert layer_devices[-5:] == ["cpu"] * 5
    assert set(layer_devices[:-5]) == {"npu:0", "npu:1"}
