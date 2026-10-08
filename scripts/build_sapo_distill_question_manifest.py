#!/usr/bin/env python3
"""Build a compact, diverse SAPO manifest from verified questions_and_code.

The JSONL supplies public question text. Only rows with an existing,
self-checked executable RL harness are eligible, so reference code is never
placed in a rollout prompt. The pool stays compact so early updates receive
useful breadth without spreading 50-100 updates over all 917 source rows.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import uuid
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / (
    "data/generated/quantum_dedup_1k_glm52_soft_distill_v3_verified_nologit_v3/"
    "questions_and_code.jsonl"
)
TARGETED = ROOT / "evals/benchmarks/quantum_grpo_training_v4_targeted_disjoint.txt"
DETERMINISTIC = ROOT / "evals/benchmarks/quantum_distill_v3_deterministic.txt"
SEMANTIC = ROOT / "evals/benchmarks/quantum_distill_v3_sampling.txt"
DEFAULT_OUTPUT = ROOT / "evals/benchmarks/quantum_grpo_training_v6_runtime30_disjoint.txt"
KNOWN_REFERENCE_REJECTS = ROOT / "evals/benchmarks/sapo_reference_rejects_aac1bad.txt"
PROMOTION = (
    ROOT / "evals/benchmarks/quantum_generalization_holdout_v1.txt",
    ROOT / "evals/benchmarks/quantum_generalization_holdout_v2_hard.txt",
    ROOT / "evals/benchmarks/quantum_generalization_holdout_v3_multi_framework.txt",
    ROOT / "evals/benchmarks/qwen36_27b_quantum_holdout_v1.txt",
    ROOT / "evals/benchmarks/sapo_promotion_holdout_v1_18.txt",
)

FRAMEWORKS = (
    ("qiskit", ("qiskit", "qiskit_aer")),
    ("cirq", ("cirq",)),
    ("pennylane", ("pennylane", "qml.")),
    ("stim", ("stim",)),
    ("qutip", ("qutip",)),
    ("braket", ("braket",)),
)
TOPICS = (
    "error correction",
    "phase estimation",
    "randomized benchmarking",
    "teleport",
    "hamiltonian",
    "tomography",
    "quantum walk",
    "grover",
    "maxcut",
    "qaoa",
    "vqe",
    "qft",
    "noise",
    "ghz",
    "bell",
)
UNSUPPORTED = re.compile(
    r"\b(?:q#|qsharp|azure quantum|ibm quantum service|real quantum hardware|"
    r"download|http://|https://|api token)\b",
    re.IGNORECASE,
)
LARGE_RUN = re.compile(r"\b(\d{5,})\s+(?:shots|repetitions|samples)\b", re.IGNORECASE)


def manifest_ids(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def normalized_ngrams(text: str, n: int = 4) -> set[tuple[str, ...]]:
    words = re.findall(r"[a-z_]+", text.lower())
    return {tuple(words[i : i + n]) for i in range(max(0, len(words) - n + 1))}


def jaccard(left: set, right: set) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def promotion_texts() -> list[str]:
    wanted = {task_id for path in PROMOTION for task_id in manifest_ids(path)}
    texts: list[str] = []
    for task_json in (ROOT / "evals/tasks").glob("*/*/task.json"):
        meta = json.loads(task_json.read_text(encoding="utf-8"))
        if meta.get("id", task_json.parent.name) in wanted:
            texts.append(
                " ".join(str(meta.get(key, "")) for key in ("task_prompt", "description", "name"))
            )
    return texts


def framework_of(question: str, code: str) -> str:
    text = f"{question}\n{code}".lower()
    for name, markers in FRAMEWORKS:
        if any(marker in text for marker in markers):
            return name
    return "python"


def topic_of(question: str) -> str:
    lowered = question.lower()
    return next((topic for topic in TOPICS if topic in lowered), "other")


def reference_import_roots(code: str) -> set[str]:
    """Return top-level imports used by the verified reference program."""
    tree = ast.parse(code)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".", 1)[0])
    return {root for root in roots if root}


def task_contract_hash(task_ids: list[str]) -> str:
    """Hash every selected public prompt and executable harness."""
    task_dirs: dict[str, Path] = {}
    for task_json in (ROOT / "evals/tasks").glob("*/*/task.json"):
        meta = json.loads(task_json.read_text(encoding="utf-8"))
        task_dirs[str(meta.get("id", task_json.parent.name))] = task_json.parent
    digest = hashlib.sha256()
    for task_id in sorted(task_ids):
        task_dir = task_dirs.get(task_id)
        if task_dir is None:
            raise SystemExit(f"unable to hash missing task contract: {task_id}")
        for name in ("task.json", "tests.py"):
            path = task_dir / name
            if not path.is_file():
                raise SystemExit(f"unable to hash missing task artifact: {path}")
            digest.update(task_id.encode())
            digest.update(b"\0")
            digest.update(name.encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


def stable_key(task_id: str) -> str:
    return hashlib.sha256(f"sapo-distill-v1:{task_id}".encode()).hexdigest()


def balanced_pick(
    candidates: list[dict], limit: int, *, exclude_near: list[dict] | None = None
) -> list[dict]:
    buckets: dict[tuple[str, str], deque[dict]] = defaultdict(deque)
    for row in sorted(candidates, key=lambda item: stable_key(item["id"])):
        buckets[(row["framework"], row["topic"])].append(row)
    order = sorted(buckets, key=lambda key: (len(buckets[key]), stable_key(":".join(key))))
    selected: list[dict] = []
    while len(selected) < limit and order:
        next_order: list[tuple[str, str]] = []
        for key in order:
            while buckets[key] and len(selected) < limit:
                candidate = buckets[key].popleft()
                candidate_ngrams = normalized_ngrams(candidate["question"])
                comparison = [*(exclude_near or []), *selected]
                if any(
                    jaccard(candidate_ngrams, normalized_ngrams(chosen["question"])) >= 0.82
                    for chosen in comparison
                ):
                    continue
                selected.append(candidate)
                break
            if buckets[key]:
                next_order.append(key)
        order = next_order
    return selected


def eligible_rows(source: Path) -> tuple[list[dict], dict[str, int]]:
    rows = [
        json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    deterministic = set(manifest_ids(DETERMINISTIC))
    semantic = set(manifest_ids(SEMANTIC))
    collisions = deterministic & semantic
    holdout_ngrams = [normalized_ngrams(text) for text in promotion_texts()]
    stats: dict[str, int] = defaultdict(int)
    eligible: list[dict] = []

    for index, row in enumerate(rows, 1):
        task_id = f"qc-{index:04d}"
        source_kind = (
            "deterministic"
            if task_id in deterministic
            else "semantic"
            if task_id in semantic
            else None
        )
        if source_kind is None or task_id in collisions:
            stats["missing_or_collision"] += 1
            continue
        question = row.get("question")
        code = row.get("code")
        if (
            not isinstance(question, str)
            or not isinstance(code, str)
            or not question.strip()
            or not code.strip()
        ):
            stats["schema"] += 1
            continue
        try:
            ast.parse(code)
        except SyntaxError:
            stats["syntax"] += 1
            continue
        if not 140 <= len(question) <= 900 or len(code) > 12_000:
            stats["size"] += 1
            continue
        if UNSUPPORTED.search(question) or LARGE_RUN.search(question):
            stats["unsupported_or_expensive"] += 1
            continue
        question_ngrams = normalized_ngrams(question)
        if any(jaccard(question_ngrams, held) >= 0.72 for held in holdout_ngrams):
            stats["holdout_near_duplicate"] += 1
            continue
        task_dir = (
            ROOT
            / "evals/tasks"
            / ("quantum_distill" if source_kind == "deterministic" else "quantum_distill_sampling")
            / task_id
        )
        if not all(
            (task_dir / name).is_file() for name in ("task.json", "solution.py", "tests.py")
        ):
            stats["incomplete_harness"] += 1
            continue
        tests_source = (task_dir / "tests.py").read_text(encoding="utf-8")
        checker_match = re.search(r"^CHECKER_NAME\s*=\s*['\"]([^'\"]+)", tests_source, re.MULTILINE)
        eligible.append(
            {
                "id": task_id,
                "source": source_kind,
                "framework": framework_of(question, code),
                "topic": topic_of(question),
                "question": question,
                "code": code,
                "import_roots": sorted(reference_import_roots(code)),
                "task_dir": task_dir,
                "checker_name": checker_match.group(1) if checker_match else "unknown",
            }
        )
    return eligible, dict(stats)


def verify_reference(row: dict, runs: int = 1) -> tuple[bool, list[str]]:
    """Execute a source reference through the exact rollout harness."""
    task_dir = Path(row["task_dir"])
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir=str(task_dir), encoding="utf-8"
    ) as handle:
        handle.write(str(row["code"]))
        candidate_path = Path(handle.name)
    details: list[str] = []
    try:
        for run in range(max(1, int(runs))):
            spec = importlib.util.spec_from_file_location(
                f"sapo_manifest_tests_{uuid.uuid4().hex}", task_dir / "tests.py"
            )
            if spec is None or spec.loader is None:
                return False, ["unable to load tests.py"]
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                result = module.run_tests(str(candidate_path))
            except Exception as exc:
                return False, [f"{type(exc).__name__}: {exc}"]
            if not isinstance(result, dict) or not bool(result.get("passed")):
                run_details = result.get("details", []) if isinstance(result, dict) else []
                details.extend(f"run {run + 1}: {item}" for item in run_details[:4])
                return False, details or [f"run {run + 1}: harness rejected reference"]
        return True, details
    finally:
        candidate_path.unlink(missing_ok=True)


def verified_balanced_pick(
    candidates: list[dict],
    limit: int,
    *,
    exclude_near: list[dict] | None = None,
    validation_runs: int = 1,
) -> tuple[list[dict], dict[str, list[str]]]:
    """Balanced selection that replaces every stale/invalid reference."""
    selected: list[dict] = []
    remaining = list(candidates)
    failures: dict[str, list[str]] = {}
    while len(selected) < limit:
        batch = balanced_pick(
            remaining,
            limit - len(selected),
            exclude_near=[*(exclude_near or []), *selected],
        )
        if not batch:
            break
        batch_ids = {row["id"] for row in batch}
        remaining = [row for row in remaining if row["id"] not in batch_ids]
        for row in batch:
            passed, details = verify_reference(row, runs=validation_runs)
            if passed:
                selected.append(row)
            else:
                failures[row["id"]] = details
    return selected, failures


def build(
    source: Path,
    output: Path,
    deterministic_count: int,
    semantic_count: int,
    available_import_roots: set[str] | None = None,
    available_checker_names: set[str] | None = None,
    verify_references: bool = False,
    reference_validation_runs: int = 1,
) -> dict:
    eligible, rejected = eligible_rows(source)
    known_rejects = (
        set(manifest_ids(KNOWN_REFERENCE_REJECTS)) if KNOWN_REFERENCE_REJECTS.is_file() else set()
    )
    known_rejected = sum(row["id"] in known_rejects for row in eligible)
    eligible = [row for row in eligible if row["id"] not in known_rejects]
    checker_rejected = 0
    if available_checker_names is not None:
        before = len(eligible)
        eligible = [row for row in eligible if row["checker_name"] in available_checker_names]
        checker_rejected = before - len(eligible)
    deterministic_rows = [row for row in eligible if row["source"] == "deterministic"]
    semantic_rows = [row for row in eligible if row["source"] == "semantic"]
    runtime_rejected = 0
    if available_import_roots is not None:
        runtime_allowlist = set(getattr(sys, "stdlib_module_names", ())) | set(
            available_import_roots
        )
        before = len(semantic_rows)
        semantic_rows = [
            row for row in semantic_rows if set(row["import_roots"]) <= runtime_allowlist
        ]
        runtime_rejected = before - len(semantic_rows)
    reference_failures: dict[str, list[str]] = {}
    if verify_references:
        deterministic_selected, deterministic_failures = verified_balanced_pick(
            deterministic_rows,
            deterministic_count,
            validation_runs=reference_validation_runs,
        )
        semantic_selected, semantic_failures = verified_balanced_pick(
            semantic_rows,
            semantic_count,
            exclude_near=deterministic_selected,
            validation_runs=reference_validation_runs,
        )
        reference_failures.update(deterministic_failures)
        reference_failures.update(semantic_failures)
    else:
        deterministic_selected = balanced_pick(deterministic_rows, deterministic_count)
        semantic_selected = balanced_pick(
            semantic_rows, semantic_count, exclude_near=deterministic_selected
        )
    selected = deterministic_selected + semantic_selected
    if len(selected) != deterministic_count + semantic_count:
        raise SystemExit(
            f"not enough eligible tasks: selected={len(selected)}, "
            f"wanted={deterministic_count + semantic_count}"
        )
    targeted = manifest_ids(TARGETED)
    ids = targeted + [row["id"] for row in selected]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate task id in generated SAPO manifest")
    promotion_ids = {task_id for path in PROMOTION for task_id in manifest_ids(path)}
    overlap = sorted(set(ids) & promotion_ids)
    if overlap:
        raise SystemExit(f"training/promotion id overlap: {overlap}")

    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    contract_hash = task_contract_hash(ids)
    required_import_roots = sorted(
        {
            root
            for row in selected
            for root in row["import_roots"]
            if root not in set(getattr(sys, "stdlib_module_names", ()))
        }
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "\n".join(
            [
                "# SAPO runtime-compatible: targeted tasks plus verified questions_and_code rows.",
                f"# source={source.relative_to(ROOT)} sha256={source_hash}",
                f"# task_contract_sha256={contract_hash}",
                f"# targeted={len(targeted)} deterministic={deterministic_count} semantic={semantic_count}",
                "# required_import_roots=" + ",".join(required_import_roots),
                f"# reference_execution_verified={str(verify_references).lower()} runs={reference_validation_runs if verify_references else 0}",
                "# Reference code remains hidden; every qc task has an executable semantic harness.",
                *targeted,
                *[row["id"] for row in selected],
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "output": str(output),
        "source_sha256": source_hash,
        "task_contract_sha256": contract_hash,
        "targeted": len(targeted),
        "deterministic": deterministic_count,
        "semantic": semantic_count,
        "total": len(ids),
        "eligible": len(eligible),
        "rejected": rejected,
        "runtime_rejected": runtime_rejected,
        "known_reference_rejected": known_rejected,
        "checker_rejected": checker_rejected,
        "reference_rejected": len(reference_failures),
        "reference_failures": reference_failures,
        "required_import_roots": required_import_roots,
        "frameworks": sorted({row["framework"] for row in selected}),
        "checkers": sorted({row["checker_name"] for row in selected}),
        "topics": sorted({row["topic"] for row in selected}),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    # Exact-stdout harnesses are unsuitable for RL when the required stdout is
    # not part of the public question: they turn otherwise-correct programs
    # into hidden-format failures. Use semantic executable harnesses only.
    parser.add_argument("--deterministic-count", type=int, default=0)
    parser.add_argument("--semantic-count", type=int, default=64)
    parser.add_argument(
        "--available-import-root",
        action="append",
        default=None,
        help=(
            "Only select reference programs whose third-party imports are in this "
            "repeatable allowlist. Pass once per installed top-level package."
        ),
    )
    parser.add_argument(
        "--checker-name",
        action="append",
        default=None,
        help="Only select semantic harnesses with this repeatable CHECKER_NAME.",
    )
    parser.add_argument(
        "--verify-references",
        action="store_true",
        help="Execute every selected source solution through its exact RL harness and replace failures.",
    )
    parser.add_argument(
        "--reference-validation-runs",
        type=int,
        default=1,
        help="Number of successful harness executions required per selected reference.",
    )
    args = parser.parse_args()
    if args.reference_validation_runs <= 0:
        parser.error("--reference-validation-runs must be positive")
    print(
        json.dumps(
            build(
                args.source,
                args.output,
                args.deterministic_count,
                args.semantic_count,
                set(args.available_import_root) if args.available_import_root is not None else None,
                set(args.checker_name) if args.checker_name is not None else None,
                verify_references=args.verify_references,
                reference_validation_runs=args.reference_validation_runs,
            ),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
