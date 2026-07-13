from __future__ import annotations

from types import SimpleNamespace

import torch

from training.agent_trajectory_rollout import (
    Trajectory,
    _execute_tool,
    _extract_candidate_source,
    _render_chat,
    assistant_logprob_over_trajectory,
    summarize_trajectory_behavior,
)


class _FakeTokenizer:
    pad_token_id = 0
    eos_token_id = 1

    def __call__(
        self,
        text: str,
        *,
        return_tensors: str = "pt",
        truncation: bool = True,
        max_length: int | None = None,
    ) -> dict[str, torch.Tensor]:
        token_ids = [2 + (ord(char) % 61) for char in text]
        if max_length is not None:
            token_ids = token_ids[-max_length:]
        if not token_ids:
            token_ids = [self.eos_token_id]
        input_ids = torch.tensor([token_ids], dtype=torch.long)
        attention_mask = torch.ones_like(input_ids)
        return {"input_ids": input_ids, "attention_mask": attention_mask}


class _FakeModel:
    def __call__(self, *, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> SimpleNamespace:
        del attention_mask
        batch_size, seq_len = input_ids.shape
        vocab_size = 128
        logits = torch.zeros(batch_size, seq_len, vocab_size, dtype=torch.float32)
        return SimpleNamespace(logits=logits)


class _RejectingChatTemplateTokenizer(_FakeTokenizer):
    def apply_chat_template(
        self, messages, *, tokenize: bool, add_generation_prompt: bool, **kwargs
    ) -> str:
        del messages, tokenize, add_generation_prompt, kwargs
        raise RuntimeError("No user query found in messages.")


def test_assistant_logprob_over_trajectory_replays_turn_history() -> None:
    trajectory = Trajectory(
        task_id="software_off_by_one_bugfix",
        user_prompt="Fix the candidate by using tools before finalizing.",
        candidate_filename="candidate.py",
        final_candidate="def fix():\n    return 1\n",
        full_token_ids=[],
        assistant_spans=[],
        turns=[
            {
                "assistant": '{"tool": "read_file", "path": "candidate.py"}',
                "tool": "read_file",
                "observation": "candidate.py:\n```python\npass\n```",
            },
            {
                "assistant": '{"tool": "final_answer", "content": "def fix():\\n    return 1\\n"}',
                "tool": "final_answer",
                "observation": "final_answer accepted.",
            },
        ],
        test_runs=0,
        terminated="final_answer",
    )

    log_prob, token_count = assistant_logprob_over_trajectory(
        _FakeModel(),
        _FakeTokenizer(),
        trajectory=trajectory,
        device=torch.device("cpu"),
        logit_clip=50.0,
        max_seq_length=4096,
    )

    expected = -torch.log(torch.tensor(128.0)) * token_count.float()
    assert token_count.item() > 0
    assert torch.isclose(log_prob, expected)


def test_summarize_trajectory_behavior_tracks_agent_hygiene() -> None:
    trajectory = Trajectory(
        task_id="software_off_by_one_bugfix",
        user_prompt="Fix the candidate by using tools before finalizing.",
        candidate_filename="candidate.py",
        final_candidate="def fix():\n    return 1\n",
        full_token_ids=[],
        assistant_spans=[],
        turns=[
            {
                "assistant": '{"tool": "read_file", "path": "candidate.py"}',
                "tool": "read_file",
                "observation": "candidate.py:\n```python\npass\n```",
            },
            {
                "assistant": '{"tool": "think", "content": "Need a minimal repair."}',
                "tool": "think",
                "observation": "think recorded",
            },
            {
                "assistant": '{"tool": "write_file", "path": "candidate.py", "content": "def fix():\\n    return 1\\n"}',
                "tool": "write_file",
                "observation": "write_file ok",
            },
            {
                "assistant": '{"tool": "run_tests"}',
                "tool": "run_tests",
                "observation": "run_tests run=1: passed=True",
            },
            {
                "assistant": '{"tool": "final_answer", "content": "def fix():\\n    return 1\\n"}',
                "tool": "final_answer",
                "observation": "final_answer accepted.",
            },
        ],
        test_runs=1,
        terminated="final_answer",
    )

    summary = summarize_trajectory_behavior(trajectory)

    assert summary["turn_count"] == 5
    assert summary["read_before_write"] is True
    assert summary["tests_before_final"] is True
    assert summary["think_calls"] == 1
    assert summary["tool_counts"]["think"] == 1
    assert summary["no_tool_turns"] == 0
    assert summary["final_answer_calls"] == 1
    assert summary["run_tests_before_write_calls"] == 0
    assert summary["repeated_read_calls"] == 0
    assert summary["made_progress"] is True


def test_summarize_trajectory_behavior_flags_read_test_loop_without_writes() -> None:
    trajectory = Trajectory(
        task_id="software_loop",
        user_prompt="Fix the candidate.",
        candidate_filename="candidate.py",
        final_candidate="",
        full_token_ids=[],
        assistant_spans=[],
        turns=[
            {
                "assistant": '{"tool": "read_file", "path": "candidate.py"}',
                "tool": "read_file",
                "observation": "file",
            },
            {
                "assistant": '{"tool": "run_tests"}',
                "tool": "run_tests",
                "observation": "write first",
            },
            {
                "assistant": '{"tool": "read_file", "path": "candidate.py"}',
                "tool": "read_file",
                "observation": "file",
            },
            {
                "assistant": '{"tool": "run_tests"}',
                "tool": "run_tests",
                "observation": "write first",
            },
        ],
        test_runs=0,
        terminated="turn_budget",
    )

    summary = summarize_trajectory_behavior(trajectory)

    assert summary["write_calls"] == 0
    assert summary["final_answer_calls"] == 0
    assert summary["run_tests_before_write_calls"] == 2
    assert summary["repeated_read_calls"] == 1
    assert summary["made_progress"] is False


def test_render_chat_falls_back_when_model_template_rejects_tool_history() -> None:
    rendered = _render_chat(
        _RejectingChatTemplateTokenizer(),
        [
            {"role": "system", "content": "system rules"},
            {"role": "user", "content": "fix the issue"},
            {"role": "assistant", "content": '{"tool": "read_file", "path": "candidate.py"}'},
            {"role": "user", "content": "[tool_observation]\nfile contents"},
        ],
        add_generation_prompt=True,
    )

    assert "SYSTEM: system rules" in rendered
    assert "USER: fix the issue" in rendered
    assert rendered.endswith("ASSISTANT:")


def test_tool_observations_nudge_agent_to_write_before_testing(tmp_path) -> None:
    candidate = tmp_path / "candidate.py"
    candidate.write_text("def fix():\n    return 0\n", encoding="utf-8")
    state = {
        "test_runs": 0,
        "max_test_runs": 1,
        "last_candidate_source": "",
        "test_harness": object(),
    }
    task = {"task_dir": tmp_path}

    read_observation, terminal = _execute_tool(
        {"tool": "read_file", "path": "candidate.py"},
        task=task,
        workspace=tmp_path / "workspace",
        candidate_filename="candidate.py",
        state=state,
    )
    test_observation, _ = _execute_tool(
        {"tool": "run_tests"},
        task=task,
        workspace=tmp_path / "workspace",
        candidate_filename="candidate.py",
        state=state,
    )

    assert terminal is False
    assert "Next action hint: call write_file" in read_observation
    assert "write the candidate first with write_file" in test_observation
    assert "Next action hint: call write_file" in test_observation


def test_extract_candidate_source_recovers_fenced_or_plain_python() -> None:
    fenced = "Here is the patch:\n```python\ndef fix():\n    return 1\n```"
    plain = "def fix():\n    return 2\n"

    assert _extract_candidate_source(fenced) == "def fix():\n    return 1"
    assert _extract_candidate_source(plain) == "def fix():\n    return 2"
    assert _extract_candidate_source("I should inspect first.") == ""
