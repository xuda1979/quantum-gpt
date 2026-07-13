"""Candidate post-processing helpers for local pass@1 evals."""

from __future__ import annotations

import ast


def _strip_think_block(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("<think>") and "</think>" in stripped:
        return stripped.split("</think>", 1)[1].lstrip()
    return stripped


def _extract_leading_fenced_block(text: str) -> str:
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if not lines:
        return text
    body: list[str] = []
    for line in lines[1:]:
        if line.strip().startswith("```"):
            break
        body.append(line)
    return "\n".join(body).strip()


def _remove_standalone_fence_lines(text: str) -> str:
    lines = [line for line in text.splitlines() if not line.strip().startswith("```")]
    return "\n".join(lines).strip()


def _strip_known_terminal_markers(text: str) -> str:
    stripped = text.strip()
    terminal_markers = (
        "<|im_end|>",
        "<|endoftext|>",
    )
    changed = True
    while changed and stripped:
        changed = False
        for marker in terminal_markers:
            if stripped.endswith(marker):
                stripped = stripped[: -len(marker)].rstrip()
                changed = True
    return stripped


def _longest_parseable_python_prefix(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    try:
        ast.parse(stripped)
        return stripped
    except SyntaxError:
        pass

    lines = stripped.splitlines()
    for end in range(len(lines), 0, -1):
        candidate = "\n".join(lines[:end]).rstrip()
        if not candidate:
            continue
        try:
            ast.parse(candidate)
        except SyntaxError:
            continue
        return candidate
    return stripped


def sanitize_candidate_text(text: str) -> str:
    stripped = _strip_think_block(text)
    if stripped.startswith("```"):
        stripped = _extract_leading_fenced_block(stripped)
    elif "```" in stripped:
        stripped = stripped.split("```", 1)[0].rstrip()
    stripped = _remove_standalone_fence_lines(stripped)
    stripped = _strip_known_terminal_markers(stripped)
    stripped = _longest_parseable_python_prefix(stripped)
    return stripped + ("\n" if stripped else "")
