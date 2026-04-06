# Copyright 2024 The Qwen2.5-Coder-7B-Instruct Authors and The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the evaluate module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from evaluate import compile_python_code, main


def test_compile_python_code() -> None:
    """Test the compile_python_code function."""
    assert compile_python_code("print('Hello, world!')")
    assert not compile_python_code("print 'Hello, world!'")


@patch("transformers.AutoModelForCausalLM")
@patch("transformers.AutoTokenizer")
@patch("evaluate.load_jsonl")
def test_main(
    mock_load_jsonl: MagicMock,
    mock_auto_tokenizer: MagicMock,
    mock_auto_model_for_causal_lm: MagicMock,
    tmp_path: str,
) -> None:
    """Test the main function of the evaluate script."""
    mock_load_jsonl.return_value = [{"prompt": "Prompt"}]
    mock_tokenizer_instance = MagicMock()
    mock_tokenizer_instance.return_value = MagicMock(input_ids=[[1, 2, 3]])
    mock_tokenizer_instance.decode.return_value = "print('Hello, world!')"
    mock_auto_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
    mock_model_instance = MagicMock()
    mock_model_instance.generate.return_value = [[1, 2, 3, 4, 5]]
    mock_auto_model_for_causal_lm.from_pretrained.return_value = mock_model_instance

    args = [
        "evaluate.py",
        "--model_dir",
        "mock_model_dir",
        "--eval_file",
        "mock_eval_file",
        "--result_file",
        str(tmp_path / "results.jsonl"),
    ]
    with patch("sys.argv", args):
        main()

    assert (tmp_path / "results.jsonl").exists()
