from __future__ import annotations

import inspect
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import scripts.run_base_vs_adapter_eval as run_base_vs_adapter_eval
import scripts.run_hf_pass1_eval as run_hf_pass1_eval
import scripts.serve_openai_chat_adapter as serve_openai_chat_adapter
import torch
import training.grpo_trainer as grpo_trainer
import training.huanxin_cpu_smoke as huanxin_cpu_smoke
import training.inspect_moe_target_modules as inspect_moe_target_modules
import training.qwen_sft_peft as qwen_sft_peft
from training.text_preprocessor_backend import (
    TextPreprocessorBackend,
    build_supervised_text_example,
    pad_supervised_text_batch,
)
from training.acquire_public_qwen_snapshot import PUBLIC_MODELS
from training.acquire_public_qwen_snapshot import candidate_hf_endpoints
from training.audit_model_source import resolve_model_info_url
from training.huanxin_cpu_smoke import runtime_autoconfig_requires_upgrade
from training.model_backend import build_runtime_upgrade_message, run_text_forward_preflight
from training.model_family_preflight import inference_backend_preflight_block
from training.qwen_sft_peft import resolve_lora_target_modules, trainer_backend_preflight_block
from training.verify_qwen_snapshot import collect_indexed_weight_shards, metadata_family_hit


class _FakeModel:
    def named_modules(self):
        return iter(
            [
                ("", object()),
                ("model.layers.0.self_attn.q_proj", object()),
                ("model.layers.0.self_attn.k_proj", object()),
                ("model.layers.0.self_attn.v_proj", object()),
                ("model.layers.0.self_attn.o_proj", object()),
                ("model.layers.0.mlp.gate_proj", object()),
                ("model.layers.0.mlp.up_proj", object()),
                ("model.layers.0.mlp.down_proj", object()),
                ("model.layers.0.block_sparse_moe.router", object()),
                ("model.layers.0.block_sparse_moe.experts.0.w1", object()),
                ("model.layers.0.block_sparse_moe.experts.1.w1", object()),
            ]
        )


class _FakeTokenizer:
    pad_token = "<pad>"
    eos_token = "</s>"

    def __call__(
        self,
        text: str,
        truncation: bool,
        max_length: int,
        padding: bool,
        return_attention_mask: bool,
    ) -> dict[str, list[int]]:
        del truncation, padding
        token_count = min(len(text.split()), max_length)
        payload = {"input_ids": list(range(1, token_count + 1))}
        if return_attention_mask:
            payload["attention_mask"] = [1] * token_count
        return payload

    def pad(self, features: list[dict[str, list[int]]], padding: bool, return_tensors: str) -> dict[str, torch.Tensor]:
        del padding, return_tensors
        max_len = max(len(item["input_ids"]) for item in features)
        input_rows = []
        mask_rows = []
        for item in features:
            pad_len = max_len - len(item["input_ids"])
            input_rows.append(item["input_ids"] + [0] * pad_len)
            mask_rows.append(item["attention_mask"] + [0] * pad_len)
        return {
            "input_ids": torch.tensor(input_rows, dtype=torch.long),
            "attention_mask": torch.tensor(mask_rows, dtype=torch.long),
        }


class _FakeProcessor:
    def __init__(self, tokenizer: _FakeTokenizer) -> None:
        self.tokenizer = tokenizer

    def apply_chat_template(self, messages: list[dict[str, str]], tokenize: bool, add_generation_prompt: bool) -> str:
        del tokenize, add_generation_prompt
        return " ".join(f"{message['role']}:{message['content']}" for message in messages)


class _FakeConditionalGenerationModel:
    def __init__(self) -> None:
        self.training = True
        self.seen_kwargs: dict[str, torch.Tensor] | None = None

    def eval(self):
        self.training = False
        return self

    def train(self, mode: bool = True):
        self.training = mode
        return self

    def __call__(self, **kwargs):
        self.seen_kwargs = kwargs
        loss = kwargs["input_ids"].float().mean() / 10.0
        return SimpleNamespace(loss=loss)


class _FakeParameter:
    def __init__(self, count: int) -> None:
        self._count = count

    def numel(self) -> int:
        return self._count


class _FakeModuleWithParameters:
    def __init__(self, *counts: int) -> None:
        self._params = [_FakeParameter(count) for count in counts]

    def parameters(self, recurse: bool = False):
        del recurse
        return iter(self._params)


def test_resolve_lora_target_modules_auto_discovers_common_projection_names() -> None:
    resolved = resolve_lora_target_modules(None, _FakeModel())
    assert resolved == ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def test_resolve_lora_target_modules_keeps_explicit_override() -> None:
    resolved = resolve_lora_target_modules(["attention_proj", "mlp_proj"], _FakeModel())
    assert resolved == ["attention_proj", "mlp_proj"]


def test_resolve_lora_target_modules_supports_full_name_regex_selection() -> None:
    resolved = resolve_lora_target_modules(
        None,
        _FakeModel(),
        [r"block_sparse_moe\.router$", r"experts\.1\."],
    )
    assert resolved == [
        "model.layers.0.block_sparse_moe.router",
        "model.layers.0.block_sparse_moe.experts.1.w1",
    ]


def test_inspect_moe_helpers_extract_expert_index_and_parameter_count() -> None:
    assert inspect_moe_target_modules.extract_expert_index("model.layers.0.block_sparse_moe.experts.17.w1") == "17"
    assert inspect_moe_target_modules.extract_expert_index("model.layers.0.router") is None
    assert inspect_moe_target_modules.module_parameter_count(_FakeModuleWithParameters(3, 5, 7)) == 15


def test_build_target_manifest_records_exact_router_and_expert_names() -> None:
    matched_details = [
        {
            "module_name": "model.layers.0.block_sparse_moe.router",
            "parameter_count": 128,
            "keyword_hits": ["router", "moe"],
            "expert_index": None,
        },
        {
            "module_name": "model.layers.0.block_sparse_moe.experts.0.w1",
            "parameter_count": 256,
            "keyword_hits": ["expert", "moe"],
            "expert_index": "0",
        },
        {
            "module_name": "model.layers.0.block_sparse_moe.experts.1.w1",
            "parameter_count": 256,
            "keyword_hits": ["expert", "moe"],
            "expert_index": "1",
        },
    ]

    manifest = inspect_moe_target_modules.build_target_manifest(
        "models/gemma-4-26B-A4B-it",
        matched_details,
        first_pass_expert_budget=4,
    )

    assert manifest["selection_mode"] == "structural-discovery-only"
    assert manifest["strategy"] == "router_warmup_then_frequency_guided_esft"
    assert manifest["router_module_names"] == ["model.layers.0.block_sparse_moe.router"]
    assert manifest["router_target_module_regex"] == [r"^model\.layers\.0\.block_sparse_moe\.router$"]
    assert manifest["expert_index_pool"] == ["0", "1"]
    assert manifest["expert_module_names_by_index"]["0"] == ["model.layers.0.block_sparse_moe.experts.0.w1"]


def test_metadata_family_hit_is_generic_not_qwen_only() -> None:
    assert metadata_family_hit("gemma4", ["Gemma4ForConditionalGeneration"], "gemma") is True
    assert metadata_family_hit("qwen3_5", ["Qwen3_5ForConditionalGeneration"], "gemma") is False


def test_runtime_upgrade_detection_matches_gemma4_unrecognized_architecture() -> None:
    exc = ValueError("Transformers does not recognize this architecture yet")
    assert runtime_autoconfig_requires_upgrade("gemma4", exc) is True


def test_trainer_backend_preflight_blocks_gemma4_conditional_generation_path() -> None:
    blocker = trainer_backend_preflight_block("gemma4", ["Gemma4ForConditionalGeneration"])
    assert blocker is not None
    assert "conditional-generation" in blocker
    assert "AutoModelForCausalLM" in blocker
    assert trainer_backend_preflight_block("qwen3_5", ["Qwen3_5ForConditionalGeneration"]) is None


def test_inference_backend_preflight_uses_inference_specific_wording() -> None:
    blocker = inference_backend_preflight_block("gemma4", ["Gemma4ForConditionalGeneration"])
    assert blocker is not None
    assert "serves and evaluates" in blocker
    assert "TaskType.CAUSAL_LM" not in blocker


def test_public_models_exposes_gemma4_targets() -> None:
    assert PUBLIC_MODELS["gemma4-e2b-it"]["model_id"] == "google/gemma-4-E2B-it"
    assert PUBLIC_MODELS["gemma4-e4b-it"]["expected_family_substring"] == "gemma"
    assert PUBLIC_MODELS["gemma4-26b-a4b-it"]["model_id"] == "google/gemma-4-26B-A4B-it"
    assert PUBLIC_MODELS["gemma4-31b-it"]["model_id"] == "google/gemma-4-31B-it"


def test_candidate_hf_endpoints_prefers_official_then_mirror() -> None:
    assert candidate_hf_endpoints() == ["https://huggingface.co", "https://hf-mirror.com"]


def test_candidate_hf_endpoints_deduplicates_explicit_mirror() -> None:
    assert candidate_hf_endpoints("https://hf-mirror.com/") == ["https://hf-mirror.com", "https://huggingface.co"]


def test_resolve_model_info_url_honors_endpoint_override() -> None:
    assert (
        resolve_model_info_url("google/gemma-4-26B-A4B-it", "https://hf-mirror.com/")
        == "https://hf-mirror.com/api/models/google/gemma-4-26B-A4B-it"
    )


def test_verify_snapshot_detects_missing_shards_from_weight_index(tmp_path: Path) -> None:
    snapshot_dir = tmp_path / "gemma-4-31B-it"
    snapshot_dir.mkdir()
    (snapshot_dir / "config.json").write_text(
        '{"model_type":"gemma4","architectures":["Gemma4ForConditionalGeneration"]}\n',
        encoding="utf-8",
    )
    (snapshot_dir / "tokenizer_config.json").write_text('{"tokenizer_class":"PreTrainedTokenizerFast"}\n', encoding="utf-8")
    (snapshot_dir / "processor_config.json").write_text("{}\n", encoding="utf-8")
    (snapshot_dir / "chat_template.jinja").write_text("{{ messages }}\n", encoding="utf-8")
    (snapshot_dir / "model.safetensors.index.json").write_text(
        '{"metadata":{"total_size":62546177752},"weight_map":{"a":"model-00001-of-00002.safetensors","b":"model-00002-of-00002.safetensors"}}\n',
        encoding="utf-8",
    )
    (snapshot_dir / "model-00001-of-00002.safetensors").write_bytes(b"partial")

    shards, missing = collect_indexed_weight_shards(snapshot_dir)
    assert shards == ["model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors"]
    assert missing == ["model-00002-of-00002.safetensors"]


def test_supervised_text_batch_preflight_masks_prompt_tokens() -> None:
    tokenizer = _FakeTokenizer()
    backend = TextPreprocessorBackend(
        render_backend=_FakeProcessor(tokenizer),
        text_backend=tokenizer,
        save_backend=tokenizer,
        backend_kind="processor.tokenizer",
    )
    record = {
        "example_id": "example-1",
        "messages": [
            {"role": "system", "content": "system prompt"},
            {"role": "user", "content": "solve task"},
            {"role": "assistant", "content": "final answer"},
        ],
    }

    example = build_supervised_text_example(record, backend, 128, train_on_completions_only=True)
    batch = pad_supervised_text_batch([example], backend.text_backend, torch)

    assert example["example_id"] == "example-1"
    assert example["prompt_token_count"] > 0
    assert list(batch["input_ids"].shape) == [1, len(example["input_ids"])]
    assert list(batch["labels"].shape) == [1, len(example["input_ids"])]
    assert torch.all(batch["labels"][0, : example["prompt_token_count"]] == -100)


def test_run_text_forward_preflight_returns_loss_and_restores_training_mode() -> None:
    tokenizer = _FakeTokenizer()
    backend = TextPreprocessorBackend(
        render_backend=_FakeProcessor(tokenizer),
        text_backend=tokenizer,
        save_backend=tokenizer,
        backend_kind="processor.tokenizer",
    )
    record = {
        "example_id": "example-2",
        "messages": [
            {"role": "user", "content": "debug circuit"},
            {"role": "assistant", "content": "fixed"},
        ],
    }
    example = build_supervised_text_example(record, backend, 128, train_on_completions_only=True)
    batch = pad_supervised_text_batch([example], backend.text_backend, torch)
    model = _FakeConditionalGenerationModel()

    result = run_text_forward_preflight(model, batch, torch_module=torch)

    assert result["model_class"] == "_FakeConditionalGenerationModel"
    assert result["input_ids_shape"] == [1, len(example["input_ids"])]
    assert result["labels_shape"] == [1, len(example["input_ids"])]
    assert result["loss"] > 0.0
    assert model.training is True
    assert model.seen_kwargs is not None


def test_huanxin_cpu_smoke_help_runs_as_script_entrypoint() -> None:
    root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [sys.executable, "training/huanxin_cpu_smoke.py", "--help"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0
    assert "--model-name" in completed.stdout


def test_grpo_trainer_uses_backend_preflight_and_saves_processor_backend() -> None:
    source = inspect.getsource(grpo_trainer)
    assert "trainer_backend_preflight_block" in source
    assert "run_text_forward_preflight" in source
    assert "text_preprocessor.save_backend.save_pretrained(adapter_dir)" in source


def test_huanxin_cpu_smoke_uses_shared_runtime_probe() -> None:
    source = inspect.getsource(huanxin_cpu_smoke)
    assert "probe_model_runtime_compat" in source
    assert "run_text_forward_preflight" in source
    assert "runtime_requires_qwen35_upgrade" not in source


def test_huanxin_cpu_smoke_loads_text_backend_before_gemma_backend_block() -> None:
    source = inspect.getsource(huanxin_cpu_smoke.main)
    assert source.index("text_preprocessor = load_text_preprocessor_backend") < source.index('summary["stage"] = "trainer_backend_preflight"')
    assert source.index('summary["stage"] = "text_batch_preflight"') < source.index('summary["stage"] = "trainer_backend_preflight"')


def test_qwen_sft_peft_loads_text_preprocessor_before_gemma_backend_block() -> None:
    source = inspect.getsource(qwen_sft_peft.main)
    assert source.index("text_preprocessor = load_text_preprocessor_backend") < source.index('"stage": "trainer_backend_preflight"')


def test_qwen_sft_peft_runs_text_forward_preflight_before_ddp_wrap() -> None:
    source = inspect.getsource(qwen_sft_peft.main)
    assert source.index('"stage": "text_forward_preflight"') < source.index('"stage": "ddp_wrapped"')


def test_grpo_trainer_runs_text_forward_preflight_before_ddp_wrap() -> None:
    source = inspect.getsource(grpo_trainer.main)
    assert source.index('"stage": "text_forward_preflight"') < source.index('"stage": "ddp_wrapped"')


def test_runtime_upgrade_message_includes_checkpoint_transformers_hint() -> None:
    message = build_runtime_upgrade_message(
        "models/gemma-4-E2B-it",
        {
            "config_model_type": "gemma4",
            "config_architectures": ["Gemma4ForConditionalGeneration"],
            "checkpoint_transformers_version": "5.5.0.dev0",
            "runtime_autoconfig_error": "Unknown model_type gemma4",
        },
    )
    assert "transformers_version=5.5.0.dev0" in message
    assert "conditional-generation" in message


def test_runtime_upgrade_message_mentions_python_floor_for_gemma4_source_path() -> None:
    message = build_runtime_upgrade_message(
        "models/gemma-4-26B-A4B-it",
        {
            "config_model_type": "gemma4",
            "config_architectures": ["Gemma4ForConditionalGeneration"],
            "checkpoint_transformers_version": "5.5.0.dev0",
            "runtime_autoconfig_error": "Unknown model_type gemma4",
            "python": "3.9.6",
        },
    )
    assert "Python is 3.9.6" in message
    assert "Python >=3.10" in message


def test_eval_and_serve_entrypoints_use_shared_causal_lm_preflight() -> None:
    assert "load_causal_lm_with_text_backend_preflight" in inspect.getsource(run_hf_pass1_eval)
    assert "load_causal_lm_with_text_backend_preflight" in inspect.getsource(run_base_vs_adapter_eval)
    assert "load_causal_lm_with_text_backend_preflight" in inspect.getsource(serve_openai_chat_adapter)
