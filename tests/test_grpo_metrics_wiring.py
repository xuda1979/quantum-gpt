from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_grpo_trainer_uses_shared_metric_helpers() -> None:
    text = (ROOT / "training/grpo_trainer.py").read_text(encoding="utf-8")
    assert "from training.grpo_utils import (  # noqa: E402" in text
    assert "append_grpo_metric," in text
    assert "append_grpo_metric_jsonl," in text
    assert "build_grpo_metrics_payload," in text
    assert "build_grpo_step_record," in text
    assert 'grpo_step_metrics.jsonl' in text
    assert "append_grpo_metric_jsonl(step_metrics_path, record)" in text
    assert "def _build_grpo_metric_record(" not in text
    assert "def append_grpo_metric(" not in text
    assert "def build_grpo_step_record(" not in text
    assert "def build_grpo_metrics_payload(" not in text
