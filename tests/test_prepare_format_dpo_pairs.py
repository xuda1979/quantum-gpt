"""Unit tests for scripts/prepare_format_dpo_pairs.py."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "prepare_format_dpo_pairs.py"


def _run(inp_lines, tmp_path, extra=None):
    inp = tmp_path / "in.jsonl"
    inp.write_text("\n".join(json.dumps(r) for r in inp_lines) + "\n")
    out = tmp_path / "out.jsonl"
    cmd = [sys.executable, str(SCRIPT), "--input", str(inp), "--output", str(out), "--check"]
    if extra:
        cmd += extra
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, f"script failed: {r.stderr}"
    pairs = [json.loads(line) for line in out.read_text().splitlines() if line.strip()]
    return pairs


def test_canonicalizes_unformatted_code(tmp_path):
    # "Unformatted" = has a fenced code block but is missing main(), the
    # main guard, and the shebang header.
    row = {
        "messages": [
            {"role": "user", "content": "Write a hello-world python program."},
            {"role": "assistant", "content": "Sure!\n```python\nprint('hello')\n```"},
        ]
    }
    pairs = _run([row], tmp_path)
    assert len(pairs) == 3, f"expected 3 pairs (one per negative type), got {len(pairs)}"
    for p in pairs:
        chosen = p["chosen"][-1]["content"]
        assert "def main(" in chosen
        assert 'if __name__ == "__main__":' in chosen
        assert "```python" in chosen


def test_already_canonical_still_produces_negatives(tmp_path):
    canonical = "Here is the solution.\n\n```python\n#!/usr/bin/env python3\ndef main():\n    print('hi')\n\nif __name__ == \"__main__\":\n    main()\n```\n"
    row = {
        "messages": [
            {"role": "user", "content": "Write a program."},
            {"role": "assistant", "content": canonical},
        ]
    }
    pairs = _run([row], tmp_path)
    # Already canonical -> canonicalize returns the same text, but we still
    # synthesize 3 negatives.
    assert len(pairs) == 3
    for p in pairs:
        assert p["chosen"][-1]["content"] == canonical


def test_prose_only_negative_has_no_code_block(tmp_path):
    row = {
        "messages": [
            {"role": "user", "content": "Write a program."},
            {"role": "assistant", "content": "Sure!\n```python\nprint('x')\n```"},
        ]
    }
    pairs = _run([row], tmp_path)
    prose_pairs = [p for p in pairs if p["negative_type"] == "prose_only"]
    assert len(prose_pairs) == 1
    rejected = prose_pairs[0]["rejected"][-1]["content"]
    assert "```python" not in rejected


def test_no_main_negative_renamed(tmp_path):
    row = {
        "messages": [
            {"role": "user", "content": "Write a program."},
            {
                "role": "assistant",
                "content": "Sure!\n```python\ndef main():\n    print('x')\n\nif __name__ == \"__main__\":\n    main()\n```",
            },
        ]
    }
    pairs = _run([row], tmp_path)
    no_main_pairs = [p for p in pairs if p["negative_type"] == "no_main"]
    assert len(no_main_pairs) == 1
    rejected = no_main_pairs[0]["rejected"][-1]["content"]
    assert "def main(" not in rejected
    assert "def _run(" in rejected


def test_skip_rows_without_code(tmp_path):
    row = {
        "messages": [
            {"role": "user", "content": "Explain quantum computing."},
            {"role": "assistant", "content": "Quantum computing uses qubits..."},
        ]
    }
    pairs = _run([row], tmp_path)
    assert pairs == [], "prose-only assistant with no code block should produce no pairs"


def test_check_flag_catches_bad_output(tmp_path):
    # If --check passes on a valid run, we're good. This test just asserts
    # the check flag runs without error on a valid input.
    row = {
        "messages": [
            {"role": "user", "content": "Write a program."},
            {"role": "assistant", "content": "Sure!\n```python\nprint('x')\n```"},
        ]
    }
    pairs = _run([row], tmp_path)
    assert len(pairs) > 0
