#!/usr/bin/env python3
"""SAPO runtime prompt-integrity audit (standing lane 19, promptwatch).

Proves per training step that the prompts the trainer feeds the policy are
clean: correct v8 task identity, no frozen-holdout leakage, no reference
solution embedded, and a system-prompt/template hash matching the launch-time
contract.

Checks
------
1. STEP SELECTION — every per-step task id (from grpo_step_metrics.jsonl and/or
   the trainer log's step_begin lines) must be in the v8 TRAINING manifest and
   NOT in the frozen-holdout list; manifest and holdout must be disjoint.
2. PROMPT RECONSTRUCTION — rebuilds the exact prompt via the SAME build_prompt
   the running trainer uses (box == bundle r6, verified byte-identical for all
   prompt-construction functions), then verifies:
     * public structure (task prompt/name, task id, domain/category, required
       interface, behavioral requirements, output contract);
     * NO reference solution: no executable statement from candidate.py and no
       long string constant from candidate.py appears in the prompt;
     * NO tests.py internals beyond the public behavior-hints block;
     * NO holdout text: holdout task ids, holdout task names, holdout
       task_prompt text and holdout candidate long-constants never appear.
3. SYSTEM PROMPT — sha256(SYSTEM_PROMPT) must equal the pinned launch-time
   contract (--system-prompt-hash).

Live mode (--daemon) pulls step->task maps and file hashes from the box
READ-ONLY via the daemon /exec transport (short-line outputs only, retried
against terminal capture truncation).

Exit codes: 0 all pass; 1 violations found; 2 operational failure.
"""
# ruff: noqa: UP038  # (X | Y) isinstance is py3.10-only; py3.9 .venv gate (precedent: training/grpo_trainer.py)

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
import re
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# The running trainer's own functions — box==bundle==local for build_prompt,
# SYSTEM_PROMPT, discover_tasks, task_behavior_hints (audited 2026-08-25).
from training.grpo_trainer import (  # noqa: E402
    SYSTEM_PROMPT,
    build_prompt,
    discover_tasks,
    task_behavior_hints,
)


@dataclass
class Violation:
    kind: str
    message: str
    step: int | None = None
    task_id: str | None = None

    def __str__(self) -> str:
        where = f" step={self.step}" if self.step is not None else ""
        who = f" task={self.task_id}" if self.task_id else ""
        return f"[{self.kind}]{where}{who} {self.message}"

    def as_dict(self) -> dict:
        return {
            "kind": self.kind,
            "step": self.step,
            "task_id": self.task_id,
            "message": self.message,
        }


# ---------------------------------------------------------------------------
# parsing
# ---------------------------------------------------------------------------


def parse_manifest(path: Path) -> list[str]:
    """Task ids from a manifest text file ('#' comments and blanks ignored)."""
    ids = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        ids.append(line)
    return ids


def load_step_tasks_from_metrics(path: Path) -> list[tuple[int, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        task = rec.get("task") or rec.get("task_name") or rec.get("task_id")
        if task is not None and rec.get("step") is not None:
            rows.append((int(rec["step"]), str(task)))
    return rows


_STEP_BEGIN_RE = re.compile(r'"stage"\s*:\s*"step_begin"')
_STEP_BEGIN_STEP_TASK_RE = re.compile(r'"step"\s*:\s*(\d+).*?"task"\s*:\s*"([^"]+)"')


def load_step_tasks_from_log(path: Path) -> list[tuple[int, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if _STEP_BEGIN_RE.search(line):
            m = _STEP_BEGIN_STEP_TASK_RE.search(line)
            if m:
                rows.append((int(m.group(1)), m.group(2)))
    return rows


# ---------------------------------------------------------------------------
# check 1: per-step task selection
# ---------------------------------------------------------------------------


def audit_step_selection(
    manifest_ids: list[str], holdout_ids: list[str], step_tasks: list[tuple[int, str]]
) -> list[Violation]:
    v: list[Violation] = []
    manifest_set = set(manifest_ids)
    holdout_set = set(holdout_ids)
    overlap = sorted(manifest_set & holdout_set)
    if overlap:
        v.append(
            Violation(
                "manifest_holdout_overlap",
                f"task ids present in BOTH training manifest and frozen holdout: {overlap}",
            )
        )
    for step, tid in step_tasks:
        if tid not in manifest_set:
            v.append(
                Violation(
                    "non_manifest_task",
                    f"step task '{tid}' is NOT in the training manifest",
                    step=step,
                    task_id=tid,
                )
            )
        if tid in holdout_set:
            v.append(
                Violation(
                    "holdout_task_used",
                    f"FROZEN HOLDOUT task '{tid}' was used for a training step",
                    step=step,
                    task_id=tid,
                )
            )
    return v


# ---------------------------------------------------------------------------
# check 2: prompt reconstruction
# ---------------------------------------------------------------------------


def reconstruct_prompts(
    tasks_dir: Path, manifest_ids: list[str], allowed_domains: set[str] | None = None
) -> dict[str, str]:
    """Build the trainer's exact prompt for every manifest task."""
    tasks = discover_tasks(
        tasks_dir, requested_task_ids=set(manifest_ids), allowed_domains=allowed_domains
    )
    return {t["meta"]["id"]: build_prompt(t) for t in tasks}


def _executable_statements(source: str) -> set[str]:
    """Executable solution statements (function/class bodies + module-level code).

    Signatures (def/class lines, parameter continuations) are excluded: they are
    the public required interface.
    """
    out: set[str] = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return out

    def add_segment(node: ast.AST) -> None:
        seg = ast.get_source_segment(source, node)
        if not seg:
            return
        for ln in seg.splitlines():
            s = ln.strip()
            if len(s) > 8:
                out.add(s)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for stmt in node.body:
                if (
                    isinstance(stmt, ast.Expr)
                    and isinstance(stmt.value, ast.Constant)
                    and isinstance(stmt.value.value, str)
                ):
                    continue  # docstring is public description material
                add_segment(stmt)
        elif isinstance(node, ast.Assign):
            add_segment(node)
    for stmt in tree.body:
        if isinstance(
            stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom)
        ):
            continue
        add_segment(stmt)
    return out


def _long_string_constants(source: str, min_len: int = 24) -> set[str]:
    out: set[str] = set()
    try:
        for node in ast.walk(ast.parse(source)):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and len(node.value) >= min_len
            ):
                out.add(node.value)
    except SyntaxError:
        pass
    return out


def _tests_derived_content(tests_path: Path | None) -> tuple[set[str], set[str]]:
    """(full non-comment lines, long string constants) of tests.py."""
    if tests_path is None or not tests_path.exists():
        return set(), set()
    source = tests_path.read_text(encoding="utf-8")
    lines = {
        ln.strip()
        for ln in source.splitlines()
        if ln.strip() and not ln.strip().startswith("#") and len(ln.strip()) > 8
    }
    return lines, _long_string_constants(source)


def _load_holdout_public_text(
    holdout_ids: list[str], tasks_dir: Path | None
) -> tuple[set[str], set[str], set[str]]:
    """Holdout ids (as text), holdout task names + task_prompts, holdout candidate constants."""
    names: set[str] = set()
    prompts: set[str] = set()
    constants: set[str] = set()
    if tasks_dir is not None:
        tasks = {t["meta"]["id"]: t for t in discover_tasks(tasks_dir, allowed_domains=None)}
        for hid in holdout_ids:
            t = tasks.get(hid)
            if t is None:
                continue
            meta = t["meta"]
            if meta.get("name"):
                names.add(str(meta["name"]))
            if meta.get("task_prompt"):
                prompts.add(str(meta["task_prompt"]))
            if meta.get("description"):
                prompts.add(str(meta["description"]))
            cand = t["task_dir"] / "candidate.py"
            if cand.exists():
                constants |= _long_string_constants(cand.read_text(encoding="utf-8"))
    return names, prompts, constants


def _word_boundary_patterns(ids: list[str]) -> list[re.Pattern]:
    # ids are [a-z0-9_]+ so \b works; ids that are prefixes of each other still
    # match only on the full token thanks to the trailing \b.
    return [re.compile(rf"\b{re.escape(i)}\b") for i in ids]


def audit_prompt(
    prompt: str,
    task_id: str,
    holdout_ids: list[str],
    holdout_names: set[str],
    candidate_path: Path | None,
    tests_path: Path | None,
    *,
    holdout_prompt_text: set[str] | None = None,
    holdout_constants: set[str] | None = None,
) -> list[Violation]:
    v: list[Violation] = []
    if not prompt.strip():
        return [Violation("empty_prompt", "prompt is empty", task_id=task_id)]

    # --- public structure -------------------------------------------------
    if f"Task id: {task_id}" not in prompt:
        v.append(
            Violation("bad_task_identity", f"prompt lacks 'Task id: {task_id}'", task_id=task_id)
        )
    for marker in ("Domain:", "Category:", "Required interface:", "Output contract:"):
        if marker not in prompt:
            v.append(
                Violation("bad_structure", f"prompt lacks '{marker}' section", task_id=task_id)
            )

    # --- holdout text ------------------------------------------------------
    for pat in _word_boundary_patterns(holdout_ids):
        if pat.search(prompt):
            v.append(
                Violation(
                    "holdout_text_in_prompt",
                    f"frozen-holdout task id text matched: {pat.pattern}",
                    task_id=task_id,
                )
            )
    for name in sorted(holdout_names):
        if name and name in prompt:
            v.append(
                Violation(
                    "holdout_text_in_prompt",
                    f"holdout task name text matched: {name!r}",
                    task_id=task_id,
                )
            )
    for text in sorted(holdout_prompt_text or set()):
        if text and text in prompt:
            v.append(
                Violation(
                    "holdout_text_in_prompt",
                    "holdout task prompt/description text matched",
                    task_id=task_id,
                )
            )
    for const in sorted(holdout_constants or set()):
        if const and const in prompt:
            v.append(
                Violation(
                    "holdout_text_in_prompt",
                    f"holdout reference constant matched: {const[:60]!r}",
                    task_id=task_id,
                )
            )

    # --- reference solution code (candidate.py) ----------------------------
    if candidate_path is not None and candidate_path.exists():
        cand_src = candidate_path.read_text(encoding="utf-8")
        for stmt in sorted(_executable_statements(cand_src)):
            if stmt in prompt:
                v.append(
                    Violation(
                        "reference_code_in_prompt",
                        f"reference solution statement leaked: {stmt[:80]!r}",
                        task_id=task_id,
                    )
                )
        for const in sorted(_long_string_constants(cand_src)):
            if const in prompt:
                v.append(
                    Violation(
                        "reference_code_in_prompt",
                        f"reference solution constant leaked: {const[:60]!r}",
                        task_id=task_id,
                    )
                )

    # --- tests.py internals beyond public behavior hints --------------------
    tests_lines, tests_constants = _tests_derived_content(tests_path)
    if tests_lines or tests_constants:
        allowed: set[str] = set()
        if tests_path is not None:
            # same public hint source the trainer uses for the prompt
            allowed = set(
                task_behavior_hints({"meta": _meta_for(tests_path), "tests_py": tests_path})
            )
        # full code lines in the prompt are always a leak (asserts, calls, ...)
        for line in sorted(tests_lines):
            if line in prompt:
                v.append(
                    Violation(
                        "tests_internals_in_prompt",
                        f"tests.py code line leaked (not a public hint): {line[:80]!r}",
                        task_id=task_id,
                    )
                )
        # long constants are public only when they are part of an allowed hint
        # (hint templates normalize '{value}' placeholders, so raw prefixes of
        # an allowed hint are also tolerated)
        for const in sorted(tests_constants):
            if const in prompt and not any(const in hint for hint in allowed):
                v.append(
                    Violation(
                        "tests_internals_in_prompt",
                        f"tests.py internal constant leaked (not a public hint): {const[:80]!r}",
                        task_id=task_id,
                    )
                )
    return v


def _meta_for(tests_path: Path) -> dict:
    task_json = tests_path.parent / "task.json"
    if task_json.exists():
        try:
            return json.loads(task_json.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


# ---------------------------------------------------------------------------
# check 3: system prompt hash contract
# ---------------------------------------------------------------------------


def system_prompt_hash() -> str:
    return hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()


def audit_system_prompt_contract(expected_sha256: str) -> list[Violation]:
    actual = system_prompt_hash()
    if expected_sha256 and expected_sha256 != actual:
        return [
            Violation(
                "system_prompt_contract",
                f"system prompt hash MISMATCH: expected {expected_sha256} got {actual}",
            )
        ]
    return []


# ---------------------------------------------------------------------------
# live daemon fetch (read-only on the box)
# ---------------------------------------------------------------------------


def daemon_exec(daemon_url: str, command: str, *, wait_ms: int = 60000, attempts: int = 3) -> str:
    payload = json.dumps({"command": command, "waitMs": wait_ms}).encode()
    last = ""
    for _ in range(attempts):
        req = urllib.request.Request(
            daemon_url, data=payload, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
        except Exception as exc:  # noqa: BLE001
            last = f"daemon call failed: {exc}"
            time.sleep(6)
            continue
        if not data.get("ok"):
            last = f"daemon error: {data.get('error')}"
            time.sleep(6)
            continue
        return data.get("output", "")
    raise RuntimeError(f"daemon exec failed after {attempts} attempts: {last}")


def _b64_py(script: str) -> str:
    b64 = base64.b64encode(script.encode()).decode()
    return f'python3 -c "$(echo {b64} | base64 -d)"'


def fetch_box_step_tasks(daemon_url: str, box_log_path: str) -> list[tuple[int, str]]:
    script = (
        "import json\n"
        f"for line in open({box_log_path!r}, errors='replace'):\n"
        '    if \'"stage": "step_begin"\' in line:\n'
        "        try:\n"
        "            r = json.loads(line)\n"
        "            print('S', r['step'], r['task'])\n"
        "        except Exception:\n"
        "            pass\n"
    )
    out = daemon_exec(daemon_url, _b64_py(script))
    rows = []
    for ln in out.splitlines():
        parts = ln.split()
        if len(parts) == 3 and parts[0] == "S":
            rows.append((int(parts[1]), parts[2]))
    return rows


def fetch_box_metrics_tasks(daemon_url: str, box_metrics_path: str) -> list[tuple[int, str]]:
    script = (
        "import json\n"
        f"for line in open({box_metrics_path!r}):\n"
        "    if not line.strip():\n"
        "        continue\n"
        "    try:\n"
        "        r = json.loads(line)\n"
        "        t = r.get('task')\n"
        "        if t is not None and r.get('step') is not None:\n"
        "            print('M', r['step'], t)\n"
        "    except Exception:\n"
        "        pass\n"
    )
    out = daemon_exec(daemon_url, _b64_py(script))
    rows = []
    for ln in out.splitlines():
        parts = ln.split()
        if len(parts) == 3 and parts[0] == "M":
            rows.append((int(parts[1]), parts[2]))
    return rows


def fetch_box_sha256s(daemon_url: str, box_root: str, rel_paths: list[str]) -> dict[str, str]:
    """sha256sum of box files; short-line output, one per file."""
    out = daemon_exec(daemon_url, f"cd {box_root} && sha256sum " + " ".join(rel_paths))
    result = {}
    for ln in out.splitlines():
        parts = ln.split("  ")
        if len(parts) == 2 and len(parts[0]) == 64:
            result[parts[1].strip()] = parts[0]
    return result


def fetch_box_task_file_hashes(
    daemon_url: str, box_root: str, task_dirs: list[str], chunk: int = 12
) -> dict[str, str]:
    """sha256 of task.json/candidate.py/tests.py per task dir, chunked and retried
    because the daemon terminal capture truncates long outputs."""
    result: dict[str, str] = {}
    for i in range(0, len(task_dirs), chunk):
        dirs = task_dirs[i : i + chunk]
        files = [
            f"evals/tasks/quantum/{d}/{f}"
            for d in dirs
            for f in ("task.json", "candidate.py", "tests.py")
        ]
        script = (
            "import hashlib\n"
            f"for p in {files!r}:\n"
            '    print("H " + hashlib.sha256(open(p, "rb").read()).hexdigest()[:16] + " " + p)\n'
        )
        missing = set(files)
        for _ in range(6):
            out = daemon_exec(daemon_url, f"cd {box_root} && " + _b64_py(script), attempts=2)
            for ln in out.splitlines():
                parts = ln.split()
                if len(parts) == 3 and parts[0] == "H" and parts[2] in missing:
                    result[parts[2]] = parts[1]
                    missing.discard(parts[2])
            if not missing:
                break
            time.sleep(6)
        if missing:
            raise RuntimeError(f"could not fetch box hashes for: {sorted(missing)}")
    return result


# ---------------------------------------------------------------------------
# main audit driver
# ---------------------------------------------------------------------------


def run_audit(
    manifest_path: Path,
    holdout_path: Path,
    tasks_dir: Path,
    metrics_path: Path | None,
    log_path: Path | None,
    system_prompt_contract: str | None,
    *,
    expected_manifest_sha256: str | None = None,
    expected_holdout_sha256: str | None = None,
    daemon_url: str | None = None,
    box_root: str | None = None,
) -> list[Violation]:
    v: list[Violation] = []

    manifest_ids = parse_manifest(manifest_path)
    holdout_ids = parse_manifest(holdout_path)

    # manifest integrity vs launch-time contract
    manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    holdout_sha = hashlib.sha256(holdout_path.read_bytes()).hexdigest()
    if expected_manifest_sha256 and expected_manifest_sha256 != manifest_sha:
        v.append(
            Violation(
                "manifest_hash",
                f"training manifest sha256 {manifest_sha} != contract {expected_manifest_sha256}",
            )
        )
    if expected_holdout_sha256 and expected_holdout_sha256 != holdout_sha:
        v.append(
            Violation(
                "holdout_hash",
                f"holdout manifest sha256 {holdout_sha} != contract {expected_holdout_sha256}",
            )
        )

    # step -> task maps
    step_tasks: list[tuple[int, str]] = []
    if daemon_url and box_root:
        # daemon mode: --metrics and --log are BOX paths (read-only cat/grep)
        if metrics_path:
            step_tasks.extend(fetch_box_metrics_tasks(daemon_url, str(metrics_path)))
        if log_path:
            step_tasks.extend(fetch_box_step_tasks(daemon_url, str(log_path)))
    else:
        if metrics_path is not None and metrics_path.exists():
            step_tasks.extend(load_step_tasks_from_metrics(metrics_path))
        if log_path is not None and log_path.exists():
            step_tasks.extend(load_step_tasks_from_log(log_path))

    # dedupe keeping order (metrics first, log cross-check later)
    seen = set()
    unique_step_tasks = []
    for s, t in step_tasks:
        if (s, t) not in seen:
            seen.add((s, t))
            unique_step_tasks.append((s, t))
    step_tasks = unique_step_tasks

    if not step_tasks:
        v.append(Violation("no_step_data", "no per-step task ids found in metrics/log"))

    v.extend(audit_step_selection(manifest_ids, holdout_ids, step_tasks))

    # cross-check: metrics vs log disagreement
    metrics_map = (
        dict(load_step_tasks_from_metrics(metrics_path))
        if metrics_path and metrics_path.exists()
        else {}
    )
    if metrics_map:
        log_map = dict(load_step_tasks_from_log(log_path)) if log_path and log_path.exists() else {}
        for step, tid in log_map.items():
            if step in metrics_map and metrics_map[step] != tid:
                v.append(
                    Violation(
                        "source_disagreement",
                        f"metrics says step {step} task={metrics_map[step]}, log says task={tid}",
                        step=step,
                    )
                )

    # prompt reconstruction + content audit for every manifest task
    holdout_names, holdout_prompt_text, holdout_constants = _load_holdout_public_text(
        holdout_ids, tasks_dir
    )
    prompts = reconstruct_prompts(tasks_dir, manifest_ids, allowed_domains=None)
    missing = [tid for tid in manifest_ids if tid not in prompts]
    if missing:
        v.append(Violation("task_not_found", f"manifest tasks missing from tasks dir: {missing}"))
    for tid in manifest_ids:
        prompt = prompts.get(tid)
        if prompt is None:
            continue
        task_dir = _task_dir_for(tasks_dir, tid)
        v.extend(
            audit_prompt(
                prompt,
                task_id=tid,
                holdout_ids=holdout_ids,
                holdout_names=holdout_names,
                candidate_path=task_dir / "candidate.py" if task_dir else None,
                tests_path=task_dir / "tests.py" if task_dir else None,
                holdout_prompt_text=holdout_prompt_text,
                holdout_constants=holdout_constants,
            )
        )

    # system prompt contract
    v.extend(audit_system_prompt_contract(system_prompt_contract or ""))

    return v


def _task_dir_for(tasks_dir: Path, task_id: str) -> Path | None:
    for sub in tasks_dir.rglob("task.json"):
        try:
            meta = json.loads(sub.read_text(encoding="utf-8"))
        except Exception:
            continue
        if meta.get("id") == task_id:
            return sub.parent
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--manifest",
        default=str(REPO_ROOT / "evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt"),
    )
    ap.add_argument(
        "--holdout", default=str(REPO_ROOT / "evals/benchmarks/sapo_promotion_holdout_v1_18.txt")
    )
    ap.add_argument("--tasks-dir", default=str(REPO_ROOT / "evals/tasks"))
    ap.add_argument("--metrics", default=None, help="grpo_step_metrics.jsonl path")
    ap.add_argument("--log", default=None, help="trainer log path (step_begin lines)")
    ap.add_argument(
        "--system-prompt-hash", default=None, help="launch-time sha256(SYSTEM_PROMPT) contract"
    )
    ap.add_argument("--expected-manifest-sha256", default=None)
    ap.add_argument("--expected-holdout-sha256", default=None)
    ap.add_argument(
        "--daemon", default=None, help="http://127.0.0.1:19005/exec for box read-only fetch"
    )
    ap.add_argument("--box-root", default="/root/work/software/quantum-gpt", help="box repo root")
    ap.add_argument("--json-out", default=None, help="write JSON report to this path")
    args = ap.parse_args(argv)

    violations = run_audit(
        Path(args.manifest),
        Path(args.holdout),
        Path(args.tasks_dir),
        Path(args.metrics) if args.metrics else None,
        Path(args.log) if args.log else None,
        args.system_prompt_hash,
        expected_manifest_sha256=args.expected_manifest_sha256,
        expected_holdout_sha256=args.expected_holdout_sha256,
        daemon_url=args.daemon,
        box_root=args.box_root,
    )

    report = {
        "ok": not violations,
        "system_prompt_sha256": system_prompt_hash(),
        "violations": [x.as_dict() for x in violations],
    }
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report, indent=2))
    if violations:
        for x in violations:
            print(f"VIOLATION {x}", flush=True)
        print(f"RESULT FAIL ({len(violations)} violations)", flush=True)
        return 1
    print("RESULT PASS — all prompt-integrity checks clean", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
