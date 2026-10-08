"""Multi-turn agent trajectory rollout for agentic RL on coding tasks.

Anthropic publicly describes training Claude on multi-turn *agent trajectories*
inside a sandboxed environment (read/write files, run shell, run tests) with an
*outcome-verifiable* reward at the end. We replicate that recipe here:

- Each trajectory begins with the same task prompt the existing GRPO trainer uses.
- The model can call four tools, emitted as JSON objects inside its assistant
  turn:
    {"tool": "read_file",    "path": "..."}                # candidate file only
    {"tool": "write_file",   "path": "...", "content": "..."}
    {"tool": "run_python",   "code": "..."}                # 5 second sandbox
    {"tool": "run_tests"}                                  # runs tests.py
    {"tool": "final_answer", "content": "..."}             # terminates
- Tool observations are appended to the conversation as a `user` message
  prefixed with `[tool:<name>]`.
- The trajectory ends when the model emits `final_answer`, when the turn budget
  is exhausted, or when a tool call fails three times in a row.
- The trainer treats the *final candidate file contents* as the answer and
  scores it with the existing reward harness (`evaluate_candidate`).

The rollout also returns the assistant-token spans for each turn so the trainer
can compute the policy log-prob over assistant tokens only (observations are
not the model's output).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import torch

TOOL_RE = re.compile(
    r"\{[^{}]*?\"tool\"\s*:\s*\"(?P<name>read_file|write_file|run_python|run_tests|think|final_answer)\"[^{}]*?\}",
    re.DOTALL,
)
FENCED_CODE_RE = re.compile(r"```(?:python)?\s*(?P<code>.*?)```", re.DOTALL | re.IGNORECASE)


AGENT_SYSTEM_PROMPT = (
    "You are an autonomous coding agent operating in a sandboxed workspace. "
    "You can use these tools by emitting a single JSON object on its own line:\n"
    '  {"tool": "read_file", "path": "<path>"}\n'
    '  {"tool": "write_file", "path": "<path>", "content": "<python source>"}\n'
    '  {"tool": "run_python", "code": "<python source>"}\n'
    '  {"tool": "run_tests"}\n'
    '  {"tool": "think", "content": "<short scratchpad>"}\n'
    '  {"tool": "final_answer", "content": "<final python source>"}\n'
    "Rules:\n"
    "  - Only the candidate file is readable. tests.py is hidden.\n"
    "  - Always read the candidate file first, then write your patched version before running tests.\n"
    "  - Use think sparingly when the next edit depends on careful tool-output analysis.\n"
    "  - You may run tests at most 3 times. Each run returns pass/fail counts only.\n"
    "  - Once you are confident, emit final_answer with the complete candidate source.\n"
    "  - If a tool reports that a candidate is missing, your next action should be write_file.\n"
    "  - Keep tool arguments JSON-parseable; do not wrap them in code fences."
)


@dataclass
class AssistantSpan:
    """Half-open [start, end) indices into the trajectory's flat token sequence."""

    start: int
    end: int


@dataclass
class Trajectory:
    task_id: str
    user_prompt: str
    candidate_filename: str
    final_candidate: str
    full_token_ids: list[int]
    assistant_spans: list[AssistantSpan]
    turns: list[dict[str, Any]] = field(default_factory=list)
    test_runs: int = 0
    terminated: str = "ok"


def summarize_trajectory_behavior(trajectory: Trajectory) -> dict[str, Any]:
    tool_counts: dict[str, int] = {}
    read_seen = False
    write_seen = False
    tests_seen = False
    read_before_write = False
    tests_before_final = False
    no_tool_turns = 0
    assistant_chars = 0
    observation_chars = 0
    run_tests_before_write_calls = 0
    repeated_read_calls = 0

    for turn in trajectory.turns:
        assistant_chars += len(str(turn.get("assistant") or ""))
        observation_chars += len(str(turn.get("observation") or ""))
        tool_name = turn.get("tool")
        if tool_name is None:
            no_tool_turns += 1
            continue
        tool_name = str(tool_name)
        tool_counts[tool_name] = int(tool_counts.get(tool_name, 0)) + 1
        if tool_name == "read_file":
            if read_seen and not write_seen:
                repeated_read_calls += 1
            read_seen = True
        elif tool_name == "write_file":
            if read_seen:
                read_before_write = True
            write_seen = True
        elif tool_name == "run_tests":
            if not write_seen:
                run_tests_before_write_calls += 1
            tests_seen = True
        elif tool_name == "final_answer":
            if tests_seen:
                tests_before_final = True

    return {
        "turn_count": len(trajectory.turns),
        "tool_counts": dict(sorted(tool_counts.items())),
        "assistant_chars": assistant_chars,
        "observation_chars": observation_chars,
        "read_before_write": read_before_write if write_seen else read_seen,
        "tests_before_final": tests_before_final
        if trajectory.terminated == "final_answer"
        else tests_seen,
        "no_tool_turns": no_tool_turns,
        "think_calls": int(tool_counts.get("think", 0)),
        "write_calls": int(tool_counts.get("write_file", 0)),
        "final_answer_calls": int(tool_counts.get("final_answer", 0)),
        "read_calls": int(tool_counts.get("read_file", 0)),
        "test_calls": int(tool_counts.get("run_tests", 0)),
        "run_tests_before_write_calls": run_tests_before_write_calls,
        "repeated_read_calls": repeated_read_calls,
        "made_progress": write_seen or int(tool_counts.get("final_answer", 0)) > 0,
    }


def _safe_json_loads(text: str) -> dict[str, Any] | None:
    try:
        return json.loads(text)
    except Exception:
        return None


def _extract_tool_call(assistant_text: str) -> dict[str, Any] | None:
    """Find the first valid tool-call JSON object in the assistant turn."""
    for match in TOOL_RE.finditer(assistant_text):
        payload = _safe_json_loads(match.group(0))
        if payload and "tool" in payload:
            return payload
    # Fallback: try the longest balanced { ... } block.
    depth = 0
    start = -1
    for idx, ch in enumerate(assistant_text):
        if ch == "{":
            if depth == 0:
                start = idx
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start >= 0:
                payload = _safe_json_loads(assistant_text[start : idx + 1])
                if payload and "tool" in payload:
                    return payload
    return None


def _extract_candidate_source(assistant_text: str) -> str:
    """Recover plain/fenced Python when the model forgets the JSON tool wrapper."""
    fenced = list(FENCED_CODE_RE.finditer(assistant_text))
    if fenced:
        code = fenced[-1].group("code").strip()
        if code:
            return code
    stripped = assistant_text.strip()
    if not stripped:
        return ""
    code_markers = (
        "def ",
        "class ",
        "import ",
        "from ",
        "#",
    )
    lines = stripped.splitlines()
    if any(line.lstrip().startswith(code_markers) for line in lines):
        return stripped
    return ""


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    head = text[: max_chars // 2]
    tail = text[-max_chars // 2 :]
    return f"{head}\n...[truncated {len(text) - max_chars} chars]...\n{tail}"


def _normalize_think_content(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    collapsed = " ".join(value.strip().split())
    if len(collapsed) <= 400:
        return collapsed
    return collapsed[:397] + "..."


def _next_action_hint(state: dict[str, Any], candidate_filename: str) -> str:
    if not state.get("read_seen"):
        return f"Next action hint: call read_file on {candidate_filename}."
    if not state.get("write_seen"):
        return (
            "Next action hint: call write_file with the full patched candidate source. "
            "Do not run tests again until you have written a candidate."
        )
    if not state.get("test_runs"):
        return "Next action hint: call run_tests once on the written candidate."
    return (
        "Next action hint: if tests failed, call write_file with a revised full candidate; "
        "otherwise call final_answer with the full candidate source."
    )


def _run_python_subprocess(code: str, timeout_seconds: float = 5.0) -> tuple[int, str]:
    """Run untrusted code in a subprocess with a hard timeout. Stdout+stderr merged."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(code)
        script_path = fh.name
    try:
        result = subprocess.run(
            [sys.executable, "-I", script_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return result.returncode, (result.stdout or "") + (result.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, f"<timeout after {timeout_seconds:.1f}s>"
    except Exception as exc:  # pragma: no cover - defensive
        return 1, f"{type(exc).__name__}: {exc}"
    finally:
        Path(script_path).unlink(missing_ok=True)


def _execute_tool(
    payload: dict[str, Any],
    *,
    task: dict[str, Any],
    workspace: Path,
    candidate_filename: str,
    state: dict[str, Any],
) -> tuple[str, bool]:
    """Run one tool call. Returns (observation_text, is_terminal)."""
    name = payload.get("tool")
    if name == "read_file":
        path = str(payload.get("path", "")).strip()
        if not path or Path(path).name != candidate_filename:
            return (
                f"read_file error: only {candidate_filename} is readable (got {path!r}).",
                False,
            )
        candidate_path = Path(task["task_dir"]) / candidate_filename
        if not candidate_path.exists():
            return f"read_file error: {candidate_filename} does not exist for this task.", False
        state["read_seen"] = True
        return (
            f"{candidate_filename}:\n```python\n{candidate_path.read_text(encoding='utf-8')}\n```\n"
            f"{_next_action_hint(state, candidate_filename)}"
        ), False

    if name == "write_file":
        path = str(payload.get("path", "")).strip()
        content = payload.get("content")
        if Path(path).name != candidate_filename or not isinstance(content, str):
            return (
                f"write_file error: only {candidate_filename} is writable; content must be a string.",
                False,
            )
        target = workspace / candidate_filename
        target.write_text(content, encoding="utf-8")
        state["last_candidate_source"] = content
        state["write_seen"] = True
        return (
            f"write_file ok: wrote {len(content)} characters to {candidate_filename}. "
            f"{_next_action_hint(state, candidate_filename)}"
        ), False

    if name == "run_python":
        code = payload.get("code")
        if not isinstance(code, str):
            return "run_python error: 'code' must be a string.", False
        rc, output = _run_python_subprocess(code)
        return f"run_python rc={rc}:\n{_truncate(output, 1200)}", False

    if name == "run_tests":
        if state.get("test_runs", 0) >= state.get("max_test_runs", 3):
            return "run_tests error: test budget exhausted for this trajectory.", False
        candidate_path = workspace / candidate_filename
        if not candidate_path.exists():
            return (
                "run_tests error: write the candidate first with write_file. "
                f"{_next_action_hint(state, candidate_filename)}"
            ), False
        state["test_runs"] = state.get("test_runs", 0) + 1
        try:
            harness = state["test_harness"]
            result = harness.run_tests(str(candidate_path))
            if isinstance(result, dict):
                passed = bool(result.get("passed"))
                detail = result.get("details") or []
                detail_text = "; ".join(str(d) for d in detail[:5])
                return (
                    f"run_tests run={state['test_runs']}: passed={passed} "
                    f"details={_truncate(detail_text, 400)} "
                    f"{_next_action_hint(state, candidate_filename)}",
                    False,
                )
            return (
                f"run_tests run={state['test_runs']}: harness returned {type(result).__name__}",
                False,
            )
        except Exception as exc:
            return f"run_tests error: {type(exc).__name__}: {exc}", False

    if name == "think":
        content = _normalize_think_content(payload.get("content"))
        if not content:
            return "think error: 'content' must be a non-empty string.", False
        state["think_calls"] = int(state.get("think_calls", 0)) + 1
        return (
            "think recorded: use this scratchpad to plan the next tool call, then continue with a concrete action.",
            False,
        )

    if name == "final_answer":
        content = payload.get("content")
        if isinstance(content, str) and content.strip():
            state["last_candidate_source"] = content
            state["write_seen"] = True
            return "final_answer accepted.", True
        # If the agent forgot to attach content, fall back to whatever it last wrote.
        if state.get("last_candidate_source"):
            return "final_answer accepted (using last written candidate).", True
        return "final_answer error: no candidate source available; write_file first.", False

    return f"unknown tool: {name!r}", False


def _fallback_render_chat(
    messages: Sequence[dict[str, str]], *, add_generation_prompt: bool
) -> str:
    rendered = "\n\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
    if add_generation_prompt:
        rendered += "\n\nASSISTANT:"
    return rendered


def _render_chat(
    tokenizer, messages: Sequence[dict[str, str]], *, add_generation_prompt: bool
) -> str:
    if hasattr(tokenizer, "apply_chat_template"):
        try:
            return tokenizer.apply_chat_template(
                list(messages),
                tokenize=False,
                add_generation_prompt=add_generation_prompt,
                enable_thinking=False,
            )
        except TypeError:
            try:
                return tokenizer.apply_chat_template(
                    list(messages),
                    tokenize=False,
                    add_generation_prompt=add_generation_prompt,
                )
            except Exception:
                return _fallback_render_chat(messages, add_generation_prompt=add_generation_prompt)
        except Exception:
            return _fallback_render_chat(messages, add_generation_prompt=add_generation_prompt)
    return _fallback_render_chat(messages, add_generation_prompt=add_generation_prompt)


def rollout_trajectory(
    model,
    tokenizer,
    *,
    task: dict[str, Any],
    test_harness,
    user_prompt: str,
    device,
    max_turns: int = 8,
    max_new_tokens: int = 384,
    max_seq_length: int = 4096,
    temperature: float = 0.8,
    candidate_filename: str = "candidate.py",
    max_test_runs: int = 3,
) -> Trajectory:
    """Run a single agent trajectory. Returns full token sequence + assistant spans."""
    with tempfile.TemporaryDirectory(prefix="agent_ws_") as ws_dir:
        workspace = Path(ws_dir)
        messages: list[dict[str, str]] = [
            {"role": "system", "content": AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        state: dict[str, Any] = {
            "test_runs": 0,
            "max_test_runs": max_test_runs,
            "last_candidate_source": "",
            "test_harness": test_harness,
            "think_calls": 0,
        }
        turns: list[dict[str, Any]] = []
        assistant_spans: list[AssistantSpan] = []

        # Start with the rendered system+user prompt as a non-assistant prefix.
        prefix_text = _render_chat(tokenizer, messages, add_generation_prompt=True)
        full_ids = tokenizer(prefix_text, add_special_tokens=False, return_tensors=None)[
            "input_ids"
        ]

        consecutive_tool_failures = 0
        terminated = "turn_budget"
        for turn_idx in range(max_turns):
            # Generate one assistant turn.
            input_tensor = torch.tensor([full_ids], device=device)
            attention_mask = torch.ones_like(input_tensor)
            with torch.no_grad():
                outputs = model.generate(
                    input_ids=input_tensor,
                    attention_mask=attention_mask,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=temperature,
                    pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
                )
            gen_ids = outputs[0, input_tensor.shape[1] :].tolist()
            # Strip trailing EOS so the span only covers real assistant tokens.
            eos_id = tokenizer.eos_token_id
            if gen_ids and eos_id is not None and gen_ids[-1] == eos_id:
                gen_ids = gen_ids[:-1]
            assistant_text = tokenizer.decode(gen_ids, skip_special_tokens=True)
            span_start = len(full_ids)
            full_ids.extend(gen_ids)
            span_end = len(full_ids)
            assistant_spans.append(AssistantSpan(start=span_start, end=span_end))

            payload = _extract_tool_call(assistant_text)
            if payload is None:
                recovered_source = _extract_candidate_source(assistant_text)
                if recovered_source:
                    state["last_candidate_source"] = recovered_source
                    state["write_seen"] = True
                    payload = {
                        "tool": "write_file",
                        "path": candidate_filename,
                        "content": recovered_source,
                    }
                    observation = (
                        "write_file recovered: assistant emitted plain Python instead of JSON; "
                        f"wrote {len(recovered_source)} characters to {candidate_filename}. "
                        f"{_next_action_hint(state, candidate_filename)}"
                    )
                    turns.append(
                        {
                            "assistant": assistant_text,
                            "tool": "write_file",
                            "observation": observation,
                            "recovered_tool": True,
                        }
                    )
                    (workspace / candidate_filename).write_text(recovered_source, encoding="utf-8")
                    consecutive_tool_failures = 0
                else:
                    consecutive_tool_failures += 1
                    observation = (
                        "tool error: no JSON tool call or Python candidate found in your turn. "
                        "Emit write_file with the full candidate source."
                    )
                    if consecutive_tool_failures >= 3:
                        terminated = "no_tool_call"
                        turns.append(
                            {
                                "assistant": assistant_text,
                                "tool": None,
                                "observation": observation,
                            }
                        )
                        break
            else:
                consecutive_tool_failures = 0
                observation, is_terminal = _execute_tool(
                    payload,
                    task=task,
                    workspace=workspace,
                    candidate_filename=candidate_filename,
                    state=state,
                )
                turns.append(
                    {
                        "assistant": assistant_text,
                        "tool": payload.get("tool"),
                        "observation": observation,
                    }
                )
                if is_terminal:
                    terminated = "final_answer"
                    break

            # Append a "tool" observation as a user turn and reopen an assistant prompt.
            messages_after = list(messages) + [
                {"role": "assistant", "content": assistant_text},
                {"role": "user", "content": f"[tool_observation]\n{observation}"},
            ]
            full_rendered = _render_chat(tokenizer, messages_after, add_generation_prompt=True)
            full_ids = tokenizer(full_rendered, add_special_tokens=False, return_tensors=None)[
                "input_ids"
            ]
            messages = messages_after  # keep building

            # Sequence length guard.
            if len(full_ids) >= max_seq_length:
                terminated = "context_overflow"
                break
        else:
            terminated = "turn_budget"

        final_candidate = state.get("last_candidate_source", "") or ""
        return Trajectory(
            task_id=task.get("task_id") or task["task_dir"].name,
            user_prompt=user_prompt,
            candidate_filename=candidate_filename,
            final_candidate=final_candidate,
            full_token_ids=full_ids,
            assistant_spans=assistant_spans,
            turns=turns,
            test_runs=state.get("test_runs", 0),
            terminated=terminated,
        )


def assistant_logprob_over_trajectory(
    model,
    tokenizer,
    *,
    trajectory: Trajectory,
    device,
    logit_clip: float,
    max_seq_length: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Sum log-probability over assistant turns by replaying the trajectory.

    This is more robust than relying on cached token offsets because the full
    chat template can shift token positions once tool observations are appended.
    """
    if not trajectory.turns:
        return torch.tensor(0.0, device=device), torch.tensor(0, device=device)
    messages: list[dict[str, str]] = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": trajectory.user_prompt},
    ]
    total_log_prob = torch.tensor(0.0, device=device)
    total_token_count = torch.tensor(0, device=device)
    for turn in trajectory.turns:
        assistant_text = str(turn.get("assistant") or "")
        if not assistant_text.strip():
            continue
        prompt_text = _render_chat(tokenizer, messages, add_generation_prompt=True)
        prompt_inputs = tokenizer(
            prompt_text,
            return_tensors="pt",
            truncation=True,
            max_length=max_seq_length,
        )
        full_inputs = tokenizer(
            prompt_text + assistant_text,
            return_tensors="pt",
            truncation=True,
            max_length=max_seq_length,
        )
        full_inputs = {name: tensor.to(device) for name, tensor in full_inputs.items()}
        prompt_len = min(
            prompt_inputs["input_ids"].shape[1],
            full_inputs["input_ids"].shape[1],
        )

        outputs = model(**full_inputs)
        logits = outputs.logits[:, :-1, :]
        if logit_clip and logit_clip > 0:
            logits = logits.clamp(-logit_clip, logit_clip)
        targets = full_inputs["input_ids"][:, 1:]
        token_log_prob_chunks = []
        # Avoid materializing the full [batch, seq, vocab] log-softmax tensor.
        # On Qwen3.6-27B this can exceed 60 GB Ascend cards during RL replay.
        for start in range(0, logits.shape[1], 64):
            end = min(start + 64, logits.shape[1])
            logits_chunk = logits[:, start:end, :]
            targets_chunk = targets[:, start:end]
            selected_logits = (
                logits_chunk.gather(-1, targets_chunk.unsqueeze(-1)).squeeze(-1).float()
            )
            normalizer = torch.logsumexp(logits_chunk.float(), dim=-1)
            token_log_prob_chunks.append(selected_logits - normalizer)
        token_log_probs = torch.cat(token_log_prob_chunks, dim=-1)

        completion_mask = torch.zeros_like(targets, dtype=torch.bool)
        completion_start = max(prompt_len - 1, 0)
        completion_mask[:, completion_start:] = True
        attention_mask = full_inputs.get("attention_mask")
        if attention_mask is not None:
            completion_mask &= attention_mask[:, 1:].bool()
        token_count = completion_mask.sum()
        if token_count.item() > 0:
            total_log_prob = total_log_prob + token_log_probs.masked_select(completion_mask).sum()
            total_token_count = total_token_count + token_count

        messages.append({"role": "assistant", "content": assistant_text})
        observation = str(turn.get("observation") or "")
        if observation:
            messages.append({"role": "user", "content": f"[tool_observation]\n{observation}"})
    return total_log_prob, total_token_count


__all__ = [
    "AGENT_SYSTEM_PROMPT",
    "AssistantSpan",
    "Trajectory",
    "assistant_logprob_over_trajectory",
    "rollout_trajectory",
    "summarize_trajectory_behavior",
]
