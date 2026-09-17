"""B-329: Prompt format normalization for train/eval consistency.

The eval harness imports the candidate as a standalone module and calls
specific function names declared in the task's ``candidate.py`` stub.
The training rollout prompt must instruct the model to implement those
exact function signatures so the train-time generation and eval-time
scoring share the same expectations.

This module provides ``normalize_prompt`` which:
1. Ensures a ``Required interface`` section is present (added if missing,
   preserved if already there).
2. Replaces the overly-restrictive output contract ("Stop immediately
   after the final required Python statement") with one that allows
   complete multi-function implementations.
3. Is deterministic — the same ``task_prompt`` + ``required_interface``
   always produces the same output, so train and eval prompts are
   byte-identical.
"""

from __future__ import annotations

import re

# The old output contract that suppressed valid multi-function solutions.
# We match the full "Output contract:" block and replace it.
_RESTRICTIVE_OUTPUT_CONTRACT_RE = re.compile(
    r"Output contract:\n" r"(?:- .+\n?)+",
    flags=re.MULTILINE,
)

# Canonical output contract that allows complete implementations.
_CANONICAL_OUTPUT_CONTRACT = (
    "Output contract:\n"
    "- Return complete, executable Python code.\n"
    "- Implement every function in the required interface with the exact name and signature.\n"
    '- You may include helper functions, imports, and a ``if __name__ == "__main__"`` guard.\n'
    "- Do not add explanations, tests, or demo code outside the implementation."
)

# Header for the required interface section.
_INTERFACE_HEADER = "Required interface:"


def normalize_prompt(
    task_prompt: str,
    *,
    required_interface: list[str] | None = None,
) -> str:
    """Normalize a task prompt for train/eval consistency.

    Parameters
    ----------
    task_prompt:
        The raw task prompt from ``task.json`` (``meta["task_prompt"]``).
    required_interface:
        List of function signature strings extracted from the candidate stub
        (e.g. ``["def solve(graph: list) -> int", "def main()"]``).

    Returns
    -------
    str
        The normalized prompt, identical for train and eval given the same
        inputs.
    """
    if not task_prompt:
        task_prompt = ""

    normalized = task_prompt

    # --- Step 1: Ensure required interface section is present ---
    has_interface = _INTERFACE_HEADER in normalized
    interface_lines = required_interface or []

    if not has_interface and interface_lines:
        # Append the interface section
        interface_block = (
            _INTERFACE_HEADER + "\n" + "\n".join(f"- {line}" for line in interface_lines)
        )
        normalized = normalized.rstrip() + "\n\n" + interface_block

    # --- Step 2: Replace restrictive output contract ---
    normalized = _RESTRICTIVE_OUTPUT_CONTRACT_RE.sub(_CANONICAL_OUTPUT_CONTRACT, normalized)

    # If no output contract was present at all, append the canonical one
    if "Output contract:" not in normalized:
        normalized = normalized.rstrip() + "\n\n" + _CANONICAL_OUTPUT_CONTRACT

    return normalized
