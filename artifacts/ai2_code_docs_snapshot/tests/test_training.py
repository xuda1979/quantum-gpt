# Copyright 2024 The Qwen2.5-Coder-7B-Instruct Authors and The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the training scripts."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from train_peft import main as peft_main
from train_sft import main as sft_main


@patch("train_sft.Trainer")
@patch("train_sft.AutoModelForCausalLM")
@patch("train_sft.AutoTokenizer")
@patch("train_sft.load_jsonl")
def test_sft_main(
    mock_load_jsonl: MagicMock,
    mock_auto_tokenizer: MagicMock,
    mock_auto_model_for_causal_lm: MagicMock,
    mock_trainer: MagicMock,
    tmp_path: str,
) -> None:
    """Test the main function of the SFT training script."""
    mock_load_jsonl.return_value = [{"prompt": "Prompt", "code": "Code"}]
    mock_tokenizer_instance = MagicMock()
    mock_auto_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
    mock_model_instance = MagicMock()
    mock_model_instance.tp_size = 1
    mock_auto_model_for_causal_lm.from_pretrained.return_value = mock_model_instance
    mock_trainer_instance = MagicMock()
    mock_trainer.return_value = mock_trainer_instance

    args = [
        "train_sft.py",
        "--model_name",
        "mock_model_name",
        "--train_file",
        "mock_train_file",
        "--output_dir",
        str(tmp_path),
        "--mock-model",
    ]
    with patch("sys.argv", args):
        with patch("pathlib.Path.exists", return_value=True):
            sft_main()

    mock_trainer_instance.train.assert_called_once()
    mock_trainer_instance.save_model.assert_called_once()


@patch("train_peft.Trainer")
@patch("train_peft.DataCollatorForLanguageModeling")
@patch("train_peft.prepare_model_for_kbit_training")
@patch("train_peft.LoraConfig")
@patch("train_peft.get_peft_model")
@patch("train_peft.AutoModelForCausalLM")
@patch("train_peft.AutoTokenizer")
@patch("train_peft.load_jsonl")
def test_peft_main(
    mock_load_jsonl: MagicMock,
    mock_auto_tokenizer: MagicMock,
    mock_auto_model_for_causal_lm: MagicMock,
    mock_get_peft_model: MagicMock,
    mock_lora_config: MagicMock,
    mock_prepare_model: MagicMock,
    mock_data_collator: MagicMock,
    mock_trainer: MagicMock,
    tmp_path: str,
) -> None:
    """Test the main function of the PEFT training script."""
    mock_load_jsonl.return_value = [{"prompt": "Prompt", "code": "Code"}]
    mock_tokenizer_instance = MagicMock()
    mock_auto_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
    mock_model_instance = MagicMock()
    mock_model_instance.tp_size = 1
    mock_auto_model_for_causal_lm.from_pretrained.return_value = mock_model_instance
    mock_peft_model_instance = MagicMock()
    mock_get_peft_model.return_value = mock_peft_model_instance
    mock_trainer_instance = MagicMock()
    mock_trainer.return_value = mock_trainer_instance

    args = [
        "train_peft.py",
        "--model_name",
        "mock_model_name",
        "--train_file",
        "mock_train_file",
        "--output_dir",
        str(tmp_path),
        "--mock-model",
    ]
    with patch("sys.argv", args):
        with patch("pathlib.Path.exists", return_value=True):
            peft_main()

    mock_trainer_instance.train.assert_called_once()
    mock_trainer_instance.save_model.assert_called_once()
