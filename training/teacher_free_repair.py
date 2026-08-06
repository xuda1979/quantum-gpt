"""Teacher-free (no-reference) self-repair for FV-GSPO.

Implements the "无教师自修复" (teacher-free self-repair) rollout from
`Teacher-Free-FV-GSPO-Final-Plan-ZH.docx`:

    * 仅使用基础模型、当前适配器与历史已验收适配器  -- the policy model itself, no
      separate teacher/reference model.
    * 失败代码和真实错误日志直接触发新一轮 rollout -- failing code plus the real
      harness error logs trigger a new repair rollout.
    * self_repair 最多两轮 -- default 2 repair rounds.

The repair feed is constructed from the exact test failures/details returned by
the hidden-test harness for the failing candidateched. Because no reference
solution is injected, the repair prompt is strictly a function of the public
task statement, the policy's own failing output, and the real error logs --
matching the plan's constraint that tests.py / reference answers are never
revealed to the candidate process.

The caller provides ``verify(code) -> dict`` (a harness runner returning a dict
with at least ``bool(result["passed"])`` and ``result["details"]``) plus an
optional ``repair_fn(model_text_exchange) -> str`` so the module is usable both
standalone (policy model loaded locally) and in unit tests with a fake model.

Only repairs that independently pass the verify gate replace the original
candidate; otherwise the original failing code wins so the group's GROPO
relative-advantage signal remains well-defined (the failed code is the behavior
samples, and the repair is what the policy learned to fix).
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

DEFAULT_MAX_ROUNDS = 2

_SYSTEM = (
    "You are a careful coding assistant. Given a failing quantum/coding "
    "program and the exact test-harness errors, produce the smallest corrected "
    "program that passes the hidden tests. Do not use any reference solution."
)


def build_repair_prompt(
    task_prompt: str,
    failing_code: str,
    failures: list[str],
    *,
    interface_lines: list[str] | None = None,
    behavior_hints: list[str] | None = None,
    max_failure_lines: int = 8,
) -> str:
    """Build the teacher-free repair prompt (no reference model, no tests.py).

    Args:
        task_prompt: The original task instruction given to the policy.
        failing_code: The policy's own failing candidate.
        failures: Exact failure/error strings from the harness run.
        interface_lines, behavior_hints: Optional task-side interface / behavior
            requirements (public, already visible to the candidate).
        max_failure_lines: Cap on how many error lines are shown to keep the
            repair rollout within the completion budget.
    """
    parts = [
        "The program below fails its hidden test harness. Fix it with the "
        "smallest correction so it passes.",
        "TASK:\n" + task_prompt.strip(),
        "FAILING PROGRAM:\n```python\n" + failing_code.strip() + "\n```",
    ]
    if interface_lines:
        parts.append("Required interface:\n" + "\n".join(f"- {line}" for line in interface_lines))
    if behavior_hints:
        parts.append(
            "Behavioral requirements:\n" + "\n".join(f"- {line}" for line in behavior_hints)
        )
    if failures:
        shown = [str(f) for f in failures][:max_failure_lines]
        parts.append("EXACT TEST FAILURES:\n- " + "\n- ".join(shown))
    parts.append("Return only the corrected Python code inside a ```python code block.")
    return "\n\n".join(parts)


def extract_code(response: str) -> str:
    """Extract the corrected Python code from a model completion."""
    if "```python" in response:
        rest = response.split("```python", 1)[1]
        return rest.split("```", 1)[0].strip()
    if "```" in response:
        parts = response.split("```")
        if len(parts) > 2:
            return parts[1].strip()
    return response.strip()


def _classify_failure(details: list[str]) -> str:
    """Coarse failure class for diagnostics (reused for repair accounting)."""
    text = " ".join(str(d) for d in details)
    if "SyntaxError" in text:
        return "syntax_error"
    if any(marker in text for marker in ("ImportError", "ModuleNotFoundError")):
        return "import_error"
    if "TimeoutError" in text or "timed out" in text:
        return "timeout"
    if any(
        re.search(rf"\b{kw}\b", text)
        for kw in ("NameError", "TypeError", "ValueError", "AttributeError", "KeyError")
    ):
        return "runtime_error"
    if any(re.search(r"\bAssert\w*\b", text) for _ in [0]) and "Assert" in text:
        return "assertion"
    return "other"


def teacher_free_self_repair(
    *,
    task_prompt: str,
    failing_code: str,
    correctness: dict[str, Any],
    repair: Callable[[str], str],
    verify: Callable[[str], dict[str, Any]],
    max_rounds: int = DEFAULT_MAX_ROUNDS,
    interface_lines: list[str] | None = None,
    behavior_hints: list[str] | None = None,
) -> dict[str, Any]:
    """Run teacher-free self-repair, returning the best verified candidate.

    Args:
        task_prompt: Original task instruction.
        failing_code: Original failing candidate (behavior sample).
        correctness: The harness result dict for ``failing_code``. Must contain
            ``bool(correctness["passed"])`` and ``correctness["details"]``.
        repair: Callable(repaired_prompt_text) -> repaired code string. Uses the
            policy model itself (no teacher/reference), matching the plan.
        verify: Callable(code) -> result dict with ``bool(result["passed"])`` and
            ``result["details"]`` (list of failure strings).
        max_rounds: Max repair rounds (plan default 2).

    Returns:
        dict with keys:
            - "code": the best candidate (original if no repair passed).
            - "passed": bool.
            - "best_round": int (0 = no repair accepted).
            - "details": verifier details for the best candidate.
            - "attempted": list of per-round {round, passed, failures, code_iter}.
    """
    orig_passed = bool(correctness.get("passed"))
    orig_details = [
        str(d) for d in (correctness.get("details") or []) if isinstance(correctness, dict)
    ]
    if orig_passed:
        # Nothing to repair.
        return {
            "code": failing_code,
            "passed": True,
            "best_round": 0,
            "details": orig_details,
            "attempted": [],
        }

    best_code = failing_code
    best_passed = False
    best_details = orig_details
    best_round = 0
    attempted: list[dict[str, Any]] = []

    failures = orig_details
    working_code = failing_code
    for rnd in range(1, max_rounds + 1):
        prompt_text = build_repair_prompt(
            task_prompt,
            working_code,
            failures,
            interface_lines=interface_lines,
            behavior_hints=behavior_hints,
        )
        try:
            candidate = repair(prompt_text)
        except Exception as exc:  # noqa: BLE001 - a repair op must not kill the step
            attempted.append(
                {"round": rnd, "passed": False, "failures": [str(exc)], "code_iter": 0}
            )
            break
        candidate = (candidate or "").strip()
        if not candidate or candidate == working_code.strip():
            submitted = working_code if candidate == working_code.strip() else candidate
        else:
            submitted = candidate
        result = verify(submitted)
        passed = bool(result.get("passed")) if isinstance(result, dict) else False
        det = [str(d) for d in (result.get("details") or [])] if isinstance(result, dict) else []
        attempted.append(
            {
                "round": rnd,
                "passed": passed,
                "failures": det,
                "code_iter": 1 if candidate else 0,
                "failure_class": _classify_failure(det) if not passed else None,
            }
        )
        if passed:
            best_code = submitted
            best_passed = True
            best_details = det
            best_round = rnd
            break
        # Teacher-free: real error logs from this round feed the next rollout.
        failures = det
        working_code = submitted

    return {
        "code": best_code,
        "passed": best_passed,
        "best_round": best_round,
        "details": best_details,
        "attempted": attempted,
    }
