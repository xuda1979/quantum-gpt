#!/usr/bin/env python3
"""Audit ChatML SFT rows for clean questions and pure code answers."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PYTHON_FRAMEWORKS = {
    "braket",
    "cirq",
    "dwave_ocean",
    "pennylane",
    "pytket",
    "qiskit",
    "qulacs",
    "qutip",
    "stim",
}

QUESTION_PATTERNS = {
    "markdown_fence": re.compile(r"```"),
    "assistant_role_tag": re.compile(r"(?i)\bassistant\s*:"),
    "answer_label": re.compile(r"(?i)\b(answer|solution|response|rationale)\s*:"),
    "xml_answer_or_code_tag": re.compile(r"(?is)<answer>|</answer>|<code>|</code>"),
    "chat_template_token": re.compile(r"<\|im_start\||<\|im_end\|>|<s>|</s>|\[/?INST\]"),
}

ASSISTANT_LITERAL_PATTERNS = {
    "markdown_fence": re.compile(r"```"),
    "assistant_role_tag": re.compile(r"(?i)\bassistant\s*:"),
    "rationale_label": re.compile(r"(?im)^\s*rationale\s*:"),
    "explanation_label": re.compile(r"(?im)^\s*explanation\s*:"),
    "solution_label": re.compile(r"(?im)^\s*solution\s*:"),
    "answer_label": re.compile(r"(?im)^\s*answer\s*:"),
    "chat_template_token": re.compile(r"<\|im_start\||<\|im_end\|>|\[/?INST\]"),
}

PURE_CODE_START = re.compile(
    r"^\s*("
    r"from\s+|import\s+|def\s+|class\s+|@|#|\"\"\"|'''|"
    r"[A-Z_][A-Z0-9_]*\s*=|[a-zA-Z_][\w]*\s*=|"
    r"OPENQASM\s+|namespace\s+|operation\s+|function\s+|"
    r"using\s+|let\s+|const\s+|//|/\*|program\s+|"
    r"circuit\s+|qubit\s+|bit\s+|include\s+"
    r")"
)

CODE_LINE = re.compile(
    r"^("
    r"import\b|from\b|def\b|class\b|if\b|elif\b|else:|for\b|while\b|try:|except\b|"
    r"finally:|with\b|return\b|assert\b|print\(|raise\b|@|"
    r"[A-Za-z_][\w.\[\](), ]*\s*=|[A-Za-z_][\w]*\(|"
    r"qc\.|np\.|qml\.|cirq\.|stim\.|"
    r"OPENQASM\b|include\b|qubit\b|bit\b|gate\b|operation\b|namespace\b|using\b|"
    r"let\b|mutable\b|set\b|return\b|//|#"
    r")"
)

PROSE_LINE = re.compile(
    r"^(Here|This|The|We|I|To|First|Next|Finally|Below|Sure|Of course)\b", re.IGNORECASE
)

NUMBER = re.compile(r"-?\d+\.?\d*(?:[eE][-+]?\d+)?")
PUNCT = re.compile(r"[^\w\s]")
WHITESPACE = re.compile(r"\s+")


def load_jsonl(path: Path) -> tuple[list[tuple[int, dict[str, Any]]], list[tuple[int, str]]]:
    rows: list[tuple[int, dict[str, Any]]] = []
    errors: list[tuple[int, str]] = []
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append((line_number, str(error)))
            continue
        if not isinstance(parsed, dict):
            errors.append((line_number, "row is not a JSON object"))
            continue
        rows.append((line_number, parsed))
    return rows, errors


def extract_messages(row: dict[str, Any]) -> tuple[str, str, str, list[str]]:
    system = ""
    user = ""
    assistant = ""
    roles: list[str] = []
    messages = row.get("messages", [])
    if not isinstance(messages, list):
        return system, user, assistant, roles
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        content = message.get("content", "")
        if isinstance(role, str):
            roles.append(role)
        if not isinstance(content, str):
            content = ""
        if role == "system" and not system:
            system = content
        elif role == "user" and not user:
            user = content
        elif role == "assistant" and not assistant:
            assistant = content
    return system, user, assistant, roles


def framework(row: dict[str, Any]) -> str:
    metadata = row.get("metadata")
    if isinstance(metadata, dict):
        value = metadata.get("framework", "unknown")
        if isinstance(value, str) and value:
            return value
    return "unknown"


def family(row: dict[str, Any]) -> str:
    metadata = row.get("metadata")
    if isinstance(metadata, dict):
        value = metadata.get("family", "unknown")
        if isinstance(value, str) and value:
            return value
    return "unknown"


def normalized_signature(row: dict[str, Any]) -> str:
    _, user, assistant, _ = extract_messages(row)
    text = (user + " || " + assistant).lower()
    text = NUMBER.sub(" <num> ", text)
    text = PUNCT.sub(" ", text)
    text = WHITESPACE.sub(" ", text).strip()
    return hashlib.blake2b(text.encode(), digest_size=16).hexdigest()


def digest(text: str) -> str:
    return hashlib.sha256(text.strip().encode()).hexdigest()


def assistant_purity_issues(code: str) -> list[tuple[str, int | None, str]]:
    issues: list[tuple[str, int | None, str]] = []
    for name, pattern in ASSISTANT_LITERAL_PATTERNS.items():
        if pattern.search(code):
            issues.append((name, None, snippet(code)))
    if code.strip() and not PURE_CODE_START.search(code):
        issues.append(("suspicious_non_code_start", None, snippet(code)))

    for line_number, line in enumerate(code.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            if re.match(
                r"^#{1,6}\s+(explanation|rationale|solution|answer)\b", stripped, re.IGNORECASE
            ):
                issues.append(("markdown_or_prose_heading", line_number, stripped[:180]))
            continue
        if stripped.startswith(("//", "/*", "*", '"""', "'''")):
            continue
        if CODE_LINE.match(stripped):
            continue
        if PROSE_LINE.match(stripped):
            issues.append(("natural_language_line", line_number, stripped[:180]))
    return issues


def question_cleanliness_issues(question: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not question.strip():
        issues.append(("empty_question", ""))
    if len(question.strip()) < 20:
        issues.append(("too_short", snippet(question)))
    for name, pattern in QUESTION_PATTERNS.items():
        if pattern.search(question):
            issues.append((name, snippet(question)))
    for line in question.splitlines():
        if line.startswith(("import ", "from ", "def ", "class ", "OPENQASM ", "namespace ")):
            issues.append(("question_contains_code_start", snippet(question)))
            break
    return issues


def snippet(text: str, max_length: int = 180) -> str:
    return text[:max_length].replace("\n", " ")


def build_report(train_file: Path, eval_file: Path | None) -> dict[str, Any]:
    rows, parse_errors = load_jsonl(train_file)
    eval_rows: list[tuple[int, dict[str, Any]]] = []
    eval_parse_errors: list[tuple[int, str]] = []
    if eval_file is not None:
        eval_rows, eval_parse_errors = load_jsonl(eval_file)

    schema_issues: list[tuple[int, str | None, str]] = []
    question_issues: dict[str, list[tuple[int, str | None, str]]] = defaultdict(list)
    assistant_issues: dict[str, list[tuple[int, str | None, int | None, str]]] = defaultdict(list)
    python_syntax_issues: list[tuple[int, str | None, str, str, int | None, str]] = []
    role_shapes: Counter[tuple[str, ...]] = Counter()
    frameworks: Counter[str] = Counter()
    families: Counter[str] = Counter()
    example_ids: list[str | None] = []
    question_hashes: Counter[str] = Counter()
    code_hashes: Counter[str] = Counter()
    code_clusters: dict[str, list[tuple[int, str | None, str, str]]] = defaultdict(list)

    for line_number, row in rows:
        example_id = row.get("example_id")
        if not isinstance(example_id, str):
            example_id = None
        example_ids.append(example_id)

        _, user, assistant, roles = extract_messages(row)
        role_shapes[tuple(roles)] += 1
        if roles != ["system", "user", "assistant"]:
            schema_issues.append((line_number, example_id, f"bad_roles={roles!r}"))
        if not user:
            schema_issues.append((line_number, example_id, "missing_user_content"))
        if not assistant:
            schema_issues.append((line_number, example_id, "missing_assistant_content"))

        current_framework = framework(row)
        frameworks[current_framework] += 1
        families[family(row)] += 1
        question_hashes[digest(user)] += 1
        code_digest = digest(assistant)
        code_hashes[code_digest] += 1
        code_clusters[code_digest].append(
            (line_number, example_id, current_framework, snippet(user, 120))
        )

        for issue_name, issue_snippet in question_cleanliness_issues(user):
            question_issues[issue_name].append((line_number, example_id, issue_snippet))
        for issue_name, issue_line, issue_snippet in assistant_purity_issues(assistant):
            assistant_issues[issue_name].append(
                (line_number, example_id, issue_line, issue_snippet)
            )

        if current_framework in PYTHON_FRAMEWORKS:
            try:
                ast.parse(assistant)
            except SyntaxError as error:
                python_syntax_issues.append(
                    (
                        line_number,
                        example_id,
                        current_framework,
                        error.msg,
                        error.lineno,
                        (error.text or "").strip()[:160],
                    )
                )

    duplicate_code_clusters = [cluster for cluster in code_clusters.values() if len(cluster) > 1]
    duplicate_code_clusters.sort(key=len, reverse=True)
    duplicate_example_ids = sum(count - 1 for count in Counter(example_ids).values() if count > 1)
    duplicate_questions = sum(count - 1 for count in question_hashes.values() if count > 1)
    duplicate_code_rows = sum(count - 1 for count in code_hashes.values() if count > 1)

    train_signatures = {normalized_signature(row) for _, row in rows}
    eval_signatures = {normalized_signature(row) for _, row in eval_rows}

    hard_issue_count = (
        len(parse_errors)
        + len(eval_parse_errors)
        + len(schema_issues)
        + sum(len(values) for values in question_issues.values())
        + sum(len(values) for values in assistant_issues.values())
        + len(python_syntax_issues)
    )

    return {
        "train_file": str(train_file),
        "eval_file": str(eval_file) if eval_file is not None else None,
        "row_count": len(rows),
        "eval_row_count": len(eval_rows),
        "json_parse_errors": parse_errors[:20],
        "eval_json_parse_errors": eval_parse_errors[:20],
        "schema_issue_count": len(schema_issues),
        "schema_issue_examples": schema_issues[:20],
        "role_shapes": {str(key): value for key, value in sorted(role_shapes.items())},
        "framework_distribution": dict(sorted(frameworks.items())),
        "family_count": len(families),
        "question_issue_counts": {
            key: len(value) for key, value in sorted(question_issues.items())
        },
        "question_issue_examples": {
            key: value[:10] for key, value in sorted(question_issues.items())
        },
        "assistant_issue_counts": {
            key: len(value) for key, value in sorted(assistant_issues.items())
        },
        "assistant_issue_examples": {
            key: value[:10] for key, value in sorted(assistant_issues.items())
        },
        "python_framework_rows": sum(frameworks[name] for name in PYTHON_FRAMEWORKS),
        "python_syntax_issue_count": len(python_syntax_issues),
        "python_syntax_issue_examples": python_syntax_issues[:20],
        "duplicate_example_id_extra_rows": duplicate_example_ids,
        "duplicate_question_extra_rows": duplicate_questions,
        "duplicate_code_extra_rows": duplicate_code_rows,
        "exact_duplicate_code_cluster_count": len(duplicate_code_clusters),
        "largest_duplicate_code_clusters": [
            {
                "size": len(cluster),
                "frameworks": dict(Counter(item[2] for item in cluster)),
                "examples": cluster[:8],
            }
            for cluster in duplicate_code_clusters[:20]
        ],
        "train_eval_signature_overlap": len(train_signatures & eval_signatures)
        if eval_file
        else None,
        "clean_questions": not question_issues and not schema_issues and not parse_errors,
        "pure_code_answers": not assistant_issues
        and not python_syntax_issues
        and not schema_issues
        and not parse_errors,
        "hard_issue_count": hard_issue_count,
        "warnings": {
            "duplicate_code_extra_rows": duplicate_code_rows,
            "exact_duplicate_code_cluster_count": len(duplicate_code_clusters),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-file", required=True, type=Path)
    parser.add_argument("--eval-file", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--fail-on-duplicate-code", action="store_true")
    args = parser.parse_args()

    report = build_report(args.train_file, args.eval_file)
    output = json.dumps(report, ensure_ascii=False, indent=2)
    print(output)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output + "\n")

    if report["hard_issue_count"]:
        return 1
    if args.fail_on_duplicate_code and report["duplicate_code_extra_rows"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
