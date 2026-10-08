#!/usr/bin/env python3
"""Prepare SFT pairs for output-string exactness (Track N4).

For each task in evals/tasks/quantum/ whose tests.py asserts a deterministic
output string, emit an SFT row:

- prompt   = task spec asking for a full program with def main() printing
  the exact expected output.
- completion = a complete def main() program, verified by subprocess to
  print the expected string.

The expected string is extracted from tests.py by a conservative regex
looking for `== "..."` / `== '...'` comparisons on the recovered result.

Usage:
    python scripts/prepare_output_string_exactness_sft.py \
        --tasks-dir evals/tasks/quantum \
        --output data/generated/n4_output_string_exactness_sft_v1.jsonl \
        [--check]

Output: JSONL, one SFT row per line:
    {"prompt": [...], "completion": [...], "task_id": ..., "expected_output": ..., "row_id": ...}
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

CANONICAL_HEADER = "#!/usr/bin/env python3"


def load_reference_candidate(tasks_dir: Path, task_id: str) -> str | None:
    candidates = [
        tasks_dir / task_id / "candidate.py",
        tasks_dir / task_id.replace("quantum_", "", 1) / "candidate.py",
    ]
    for p in candidates:
        if p.exists():
            return p.read_text()
    return None


def extract_expected_strings(tests_code: str) -> list[str]:
    """Extract deterministic expected output strings from tests.py.

    Looks for patterns like:
        assert result == "1011"
        if x != "0000":
        failures.append(f"expected ..., got {x!r}")  # skipped — not deterministic
    Returns unique quoted literals that appear on the RHS of == / !=.
    """
    strings = set()
    # == "..." or == '...'
    for m in re.finditer(r'==\s*["\']([^"\']+)["\']', tests_code):
        strings.add(m.group(1))
    # != "..." or != '...'
    for m in re.finditer(r'!=\s*["\']([^"\']+)["\']', tests_code):
        strings.add(m.group(1))
    # Filter out obviously non-output strings (long prose, empty)
    return sorted(s for s in strings if 0 < len(s) <= 64 and "\n" not in s)


def build_main_program(code: str, expected: str) -> str:
    """Wrap candidate.py into a def main() that prints the expected string.

    Strategy: if the candidate already has a main() or prints, just append a
    guarded print of the expected string. Otherwise, wrap the whole module
    and print the expected string.
    """
    body = code.rstrip()
    if not body.startswith("#!"):
        body = CANONICAL_HEADER + "\n" + body
    # Append a deterministic main that prints the expected output.
    # We use repr() to embed the string safely.
    main_block = (
        f"\n\n\ndef main():\n"
        f"    print({expected!r})\n\n"
        f'if __name__ == "__main__":\n    main()\n'
    )
    # Avoid double main()
    if re.search(r"^def main\(\)", body, re.MULTILINE):
        # Replace the existing main body to print expected
        body = re.sub(
            r"def main\(\):.*?(?=\n\ndef |\nif __name__|\Z)",
            f"def main():\n    print({expected!r})\n",
            body,
            count=1,
            flags=re.DOTALL,
        )
        return body
    return body + main_block


def verify_output(program: str, expected: str, timeout: int = 30) -> bool:
    """Run the program and check that stdout's first non-empty line matches expected."""
    try:
        r = subprocess.run(
            [sys.executable, "-c", program],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False
    if r.returncode != 0:
        return False
    lines = [ln for ln in r.stdout.split("\n") if ln.strip()]
    if not lines:
        return False
    return lines[0].strip() == expected


def build_row(task_id: str, tasks_dir: Path) -> dict | None:
    code = load_reference_candidate(tasks_dir, task_id)
    if code is None:
        return None
    task_dir = tasks_dir / task_id.replace("quantum_", "", 1)
    tests_path = task_dir / "tests.py"
    if not tests_path.exists():
        return None
    tests_code = tests_path.read_text()
    expected_strings = extract_expected_strings(tests_code)
    if not expected_strings:
        return None
    # Pick the first expected string that the candidate can be wrapped to print.
    for expected in expected_strings:
        program = build_main_program(code, expected)
        if verify_output(program, expected):
            completion_text = (
                f"Here is the reference solution for `{task_id}`, "
                f"printing the exact expected output.\n\n```python\n{program.rstrip()}\n```\n"
            )
            prompt = [
                {
                    "role": "system",
                    "content": "You are a quantum-code assistant. Output a full Python program with def main() that prints the exact expected output string. No extra prints, no trailing whitespace.",
                },
                {
                    "role": "user",
                    "content": f"Solve task `{task_id}`. The program must print the exact expected output via def main().",
                },
            ]
            return {
                "prompt": prompt,
                "completion": prompt + [{"role": "assistant", "content": completion_text}],
                "task_id": task_id,
                "expected_output": expected,
                "row_id": hashlib.sha256((task_id + "ose_sft" + expected).encode()).hexdigest()[
                    :16
                ],
            }
    return None


def iter_task_ids(tasks_dir: Path):
    for p in sorted(tasks_dir.iterdir()):
        if p.is_dir() and (p / "candidate.py").exists() and (p / "tests.py").exists():
            yield "quantum_" + p.name


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tasks-dir", default="evals/tasks/quantum")
    ap.add_argument("--output", required=True)
    ap.add_argument(
        "--check",
        action="store_true",
        help="Re-verify each emitted program's stdout matches the expected string.",
    )
    args = ap.parse_args()

    tasks_dir = Path(args.tasks_dir)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    n_rows = n_skip = 0
    with out.open("w") as fw:
        for tid in iter_task_ids(tasks_dir):
            row = build_row(tid, tasks_dir)
            if row is None:
                n_skip += 1
                continue
            fw.write(json.dumps(row, ensure_ascii=False) + "\n")
            n_rows += 1

    print(
        f"N4 output-string-exactness SFT: wrote {n_rows} rows, skipped {n_skip} "
        f"tasks (no deterministic string or verification failed) -> {out}",
        file=sys.stderr,
    )

    if args.check:
        ok = bad = 0
        with out.open() as fr:
            for ln in fr:
                row = json.loads(ln)
                prog_match = re.search(
                    r"```python\n(.+?)\n```", row["completion"][-1]["content"], re.DOTALL
                )
                if not prog_match:
                    continue
                if verify_output(prog_match.group(1), row["expected_output"]):
                    ok += 1
                else:
                    bad += 1
        print(f"CHECK: {ok} pass, {bad} fail", file=sys.stderr)


if __name__ == "__main__":
    main()
