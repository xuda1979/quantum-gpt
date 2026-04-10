from __future__ import annotations

import sys

import pytest
import torch

from training import grpo_trainer, qwen_sft_peft


class TinySelectiveModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.router = torch.nn.Linear(4, 4)
        self.experts = torch.nn.ModuleDict(
            {
                "expert0": torch.nn.Linear(4, 4),
                "expert1": torch.nn.Linear(4, 4),
            }
        )


def test_apply_selective_training_controls_router_only() -> None:
    model = TinySelectiveModel()

    summary = qwen_sft_peft.apply_selective_training_controls(
        model,
        trainable_param_regex=[r"^router\."],
    )
    _params, names, count = qwen_sft_peft.collect_trainable_parameters(model)

    assert summary["initial_trainable_count"] == 6
    assert summary["final_trainable_count"] == 2
    assert summary["trainable_regex_match_count"] == 2
    assert summary["frozen_by_regex_count"] == 0
    assert count > 0
    assert names == ["router.weight", "router.bias"]


def test_apply_selective_training_controls_selected_expert_with_freeze() -> None:
    model = TinySelectiveModel()

    summary = qwen_sft_peft.apply_selective_training_controls(
        model,
        trainable_param_regex=[r"^experts\.expert1\."],
        freeze_param_regex=[r"bias$"],
    )
    _params, names, _count = qwen_sft_peft.collect_trainable_parameters(model)

    assert summary["initial_trainable_count"] == 6
    assert summary["final_trainable_count"] == 1
    assert summary["trainable_regex_match_count"] == 2
    assert summary["frozen_by_regex_count"] == 1
    assert names == ["experts.expert1.weight"]


def test_apply_selective_training_controls_errors_for_no_regex_match() -> None:
    model = TinySelectiveModel()
    with pytest.raises(SystemExit, match="No trainable parameters matched --trainable-param-regex"):
        qwen_sft_peft.apply_selective_training_controls(
            model,
            trainable_param_regex=[r"^does_not_exist\."],
        )


def test_collect_trainable_parameters_errors_for_all_frozen() -> None:
    model = TinySelectiveModel()
    for parameter in model.parameters():
        parameter.requires_grad = False

    with pytest.raises(SystemExit, match="No trainable parameters found"):
        qwen_sft_peft.collect_trainable_parameters(model)


def test_qwen_parse_args_accepts_selective_training_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "qwen_sft_peft.py",
            "--model-name",
            "models/Qwen2.5-1.5B-Instruct",
            "--train-file",
            "data/seed/train.jsonl",
            "--output-dir",
            "outputs/smoke",
            "--trainable-param-regex",
            "^router\\.",
            "^experts\\.expert1\\.",
            "--freeze-param-regex",
            "bias$",
        ],
    )

    args = qwen_sft_peft.parse_args()

    assert args.trainable_param_regex == [r"^router\.", r"^experts\.expert1\."]
    assert args.freeze_param_regex == [r"bias$"]


def test_grpo_parse_args_accepts_selective_training_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "grpo_trainer.py",
            "--model-name",
            "models/Qwen2.5-1.5B-Instruct",
            "--trainable-param-regex",
            "^router\\.",
            "--freeze-param-regex",
            "bias$",
        ],
    )

    args = grpo_trainer.parse_args()

    assert args.trainable_param_regex == [r"^router\."]
    assert args.freeze_param_regex == [r"bias$"]
