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
"""Tests for the crawler module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from crawler import QuantumDataCollector


@pytest.fixture
def collector() -> QuantumDataCollector:
    """Return a QuantumDataCollector instance."""
    return QuantumDataCollector(min_code_lines=1)


@patch("requests.get")
def test_collect_qiskit_textbook(mock_get: MagicMock, collector: QuantumDataCollector) -> None:
    """Test the collect_qiskit_textbook method."""
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <section>
            <h1>Title</h1>
            <p>Description</p>
            <pre><code>from qiskit import QuantumCircuit</code></pre>
        </section>
    </html>
    """
    mock_get.return_value = mock_response

    collector.collect_qiskit_textbook(["http://example.com"])
    assert len(collector.records) == 1
    assert collector.records[0].prompt == "Title\n\nDescription"
    assert collector.records[0].code == "from qiskit import QuantumCircuit"


@patch("requests.get")
def test_collect_github_files(mock_get: MagicMock, collector: QuantumDataCollector) -> None:
    """Test the collect_github_files method."""
    mock_response = MagicMock()
    mock_response.text = "from qiskit import QuantumCircuit"
    mock_get.return_value = mock_response

    collector.collect_github_files([{"url": "http://example.com", "prompt": "Prompt"}])
    assert len(collector.records) == 1
    assert collector.records[0].prompt == "Prompt"
    assert collector.records[0].code == "from qiskit import QuantumCircuit"


@patch("requests.get")
def test_collect_stackexchange(mock_get: MagicMock, collector: QuantumDataCollector) -> None:
    """Test the collect_stackexchange method."""
    mock_question_response = MagicMock()
    mock_question_response.json.return_value = {
        "items": [
            {
                "question_id": 1,
                "title": "Title",
                "body": "<p>Body</p>",
            }
        ]
    }
    mock_answer_response = MagicMock()
    mock_answer_response.json.return_value = {
        "items": [
            {
                "body": "<pre><code>from qiskit import QuantumCircuit</code></pre>",
            }
        ]
    }
    mock_get.side_effect = [mock_question_response, mock_answer_response]

    collector.collect_stackexchange(tags=["quantum-computing"], max_questions=1, answers_per_question=1)
    assert len(collector.records) == 1
    assert collector.records[0].prompt == "Title\n\nBody"
    assert collector.records[0].code == "from qiskit import QuantumCircuit"
