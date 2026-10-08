"""TDD suite for the single-home py3.9-safe pairing idioms (architect lane #26).

The recurring bug class (2026-08-26): the strict-zip helper resurfaced 3x as
local point-fixes (trainer, fine-score deltas, judge calibration), and
``zip(..., strict=...)`` — a py3.10-only keyword — is a TypeError on the
canonical py3.9.6 training venv while silently working on the py3.14 dev host:
a split-brain failure mode. The structural fix is ONE home
(``training.compat.strict_zip``) plus a SOURCE guard that fails any new
``zip(..., strict=`` in the loop's core dirs and any local re-implementation
of the helper outside its home. A source-level guard is required because a
runtime test cannot catch the keyword on py3.14 (the same reasoning as the
existing test_fine_score / test_model_judge / test_grpo_utils deploy gates).

Scan scope: training/ + scripts/ + evals/runner/ (recursive, ``*.py``).
The frozen holdout task contracts live under evals/tasks/ — deliberately OUT
of scope (their ``strict=False`` pairings are frozen contract text).
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path

import pytest

from training.compat import strict_zip

ROOT = Path(__file__).resolve().parents[1]
SCOPED_DIRS = ("training", "scripts", "evals/runner")


# ---------------------------------------------------------------------------
# strict_zip behavior (py3.10 zip(strict=True) semantics on py3.9)
# ---------------------------------------------------------------------------


def test_strict_zip_yields_pairs() -> None:
    assert list(strict_zip([1, 2], ["a", "b"])) == [(1, "a"), (2, "b")]


def test_strict_zip_empty_inputs() -> None:
    assert list(strict_zip([], [])) == []


def test_strict_zip_raises_when_first_is_shorter() -> None:
    with pytest.raises(ValueError):
        list(strict_zip([1, 2], ["a"]))


def test_strict_zip_raises_when_later_is_shorter() -> None:
    with pytest.raises(ValueError):
        list(strict_zip([1], ["a", "b"]))


def test_strict_zip_yields_common_pairs_then_raises() -> None:
    """py3.10 semantics: pairs up to the short iterable's end are yielded,
    then the length mismatch raises (never a silent partial pairing)."""
    seen: list[tuple] = []
    with pytest.raises(ValueError):
        for pair in strict_zip([1, 2, 3], ["a", "b"]):
            seen.append(pair)
    assert seen == [(1, "a"), (2, "b")]


def test_strict_zip_is_lazy_generator() -> None:
    gen = strict_zip([1, 2, 3], ["a", "b", "c"])
    assert next(gen) == (1, "a")
    assert next(gen) == (2, "b")
    assert next(gen) == (3, "c")
    with pytest.raises(StopIteration):
        next(gen)


def test_strict_zip_accepts_generators_and_three_iterables() -> None:
    assert list(strict_zip((i for i in range(3)), ["a", "b", "c"], [True, False, True])) == [
        (0, "a", True),
        (1, "b", False),
        (2, "c", True),
    ]


def test_strict_zip_single_iterable() -> None:
    assert list(strict_zip([1, 2])) == [(1,), (2,)]


# ---------------------------------------------------------------------------
# Migration pins: grpo_trainer must re-export the SAME object (no local copy)
# ---------------------------------------------------------------------------


def test_grpo_trainer_strict_zip_is_compat_singleton() -> None:
    """The trainer's module-level ``_strict_zip`` must BE ``compat.strict_zip``
    — a local re-implementation (the resurfaced-duplication bug class) fails
    this identity pin."""
    from training import grpo_trainer

    assert grpo_trainer._strict_zip is strict_zip


def test_grpo_utils_imports_strict_zip_from_compat() -> None:
    from training import grpo_utils

    source = inspect.getsource(grpo_utils)
    assert "from training.compat import strict_zip" in source
    assert "def strict_zip" not in source and "def _strict_zip" not in source


# ---------------------------------------------------------------------------
# Source scanner (paren-aware, comment/string-safe)
# ---------------------------------------------------------------------------


def _strip_comments_and_strings(source: str) -> str:
    """Blank out line comments and string literals (same length, newlines
    preserved so line numbers and offsets stay 1:1 with the original) — a
    scan over the result can only ever see real code."""
    out = list(source)
    i = 0
    n = len(source)
    while i < n:
        ch = source[i]
        if ch == "#":  # line comment: blank to end of line
            while i < n and source[i] != "\n":
                out[i] = " "
                i += 1
            continue
        if ch in ("'", '"'):  # string literal (single or triple-quoted)
            quote = ch
            triple = source.startswith(quote * 3, i)
            delim = quote * (3 if triple else 1)
            j = i + len(delim)
            while j < n:
                if source.startswith(delim, j):
                    if source.startswith(quote * 2, j) and not source.startswith(quote * 3, j):
                        j += 2  # doubled quote inside a string ('' / "")
                        continue
                    j += len(delim)
                    break
                if source[j] == "\\":
                    j += 1
                j += 1
            for k in range(i, min(j, n)):
                if source[k] != "\n":
                    out[k] = " "
            i = j
            continue
        i += 1
    return "".join(out)


def _iter_zip_strict_calls(source: str):
    """Yield (line_no, excerpt) for every real ``zip(`` call whose argument
    list contains a ``strict=`` keyword.

    Comments and string literals are blanked first, so prose that merely
    mentions the pattern never trips the guard; the paren-depth walk then
    only ever sees real code (nested parens in args are fine).
    """
    code = _strip_comments_and_strings(source)
    for m in re.finditer(r"\bzip\s*\(", code):
        depth = 1
        pos = m.end()
        while pos < len(code) and depth > 0:
            if code[pos] == "(":
                depth += 1
            elif code[pos] == ")":
                depth -= 1
            pos += 1
        window = code[m.start() : pos]
        if re.search(r"strict\s*=", window):
            line_no = source.count("\n", 0, m.start()) + 1
            excerpt = " ".join(source[m.start() : pos].split())[:120]
            yield line_no, excerpt


def test_scanner_flags_inline_strict_keyword() -> None:
    findings = list(_iter_zip_strict_calls("x = zip(a, b, strict=True)\n"))
    assert len(findings) == 1
    assert findings[0][0] == 1
    assert "strict=True" in findings[0][1]


def test_scanner_flags_strict_false_too() -> None:
    assert len(list(_iter_zip_strict_calls("for a, b in zip(xs, ys, strict=False):\n"))) == 1


def test_scanner_flags_multiline_call() -> None:
    source = "zip(\n    xs,\n    ys,\n    strict=True,\n)\n"
    findings = list(_iter_zip_strict_calls(source))
    assert len(findings) == 1
    assert findings[0][0] == 1


def test_scanner_flags_nested_parens() -> None:
    source = "zip([(i, j) for i in a], b, strict=True)\n"
    assert len(list(_iter_zip_strict_calls(source))) == 1


def test_scanner_ignores_plain_zip() -> None:
    assert list(_iter_zip_strict_calls("for a, b in zip(xs, ys):\n")) == []


def test_scanner_ignores_strict_zip_name() -> None:
    # ``strict_zip(...)`` contains the substring ``zip(`` but is the compat
    # helper, not the py3.10 keyword — must never be flagged.
    assert list(_iter_zip_strict_calls("for a, b in strict_zip(xs, ys):\n")) == []


def test_scanner_ignores_comment_and_string_mentions() -> None:
    source = (
        "# never write zip(a, b, strict=True) here — use compat\n"
        'doc = "zip(x, y, strict=False) is py3.10-only"\n'
        "x = zip(a, b)  # strict=True is forbidden\n"
    )
    assert list(_iter_zip_strict_calls(source)) == []


# ---------------------------------------------------------------------------
# The structural guards (the point of this lane's first assignment)
# ---------------------------------------------------------------------------


def _scoped_py_files() -> list[Path]:
    files: list[Path] = []
    for dir_name in SCOPED_DIRS:
        base = ROOT / dir_name
        if base.is_dir():
            files.extend(sorted(base.rglob("*.py")))
    return files


def test_no_zip_strict_keyword_in_scoped_dirs() -> None:
    """Fail on ANY new ``zip(..., strict=`` in training/ + scripts/ +
    evals/runner/ (the frozen holdout contracts under evals/tasks/ are
    outside this scope by design). The canonical venv is py3.9.6 where the
    keyword TypeErrors at runtime; on the py3.14 dev host it silently works —
    the split-brain bug class. Use ``training.compat.strict_zip`` instead."""
    offenders: list[str] = []
    for path in _scoped_py_files():
        source = path.read_text(encoding="utf-8")
        for line_no, excerpt in _iter_zip_strict_calls(source):
            offenders.append(f"{path.relative_to(ROOT)}:{line_no}: {excerpt}")
    assert not offenders, (
        "py3.10-only zip(..., strict=) found in scoped dirs (py3.9 venv "
        "TypeError risk / silent split-brain):\n"
        + "\n".join(offenders)
        + "\nUse training.compat.strict_zip (one home, one test) instead."
    )


def test_no_local_strict_zip_reimplementation_in_scoped_dirs() -> None:
    """The helper must have exactly one home (training/compat.py). A local
    ``def strict_zip`` / ``def _strict_zip`` anywhere else in the scoped
    dirs is the resurfaced-duplication bug class — fail on it."""
    redefinition = re.compile(r"^\s*def\s+_?strict_zip\s*\(", re.MULTILINE)
    offenders: list[str] = []
    for path in _scoped_py_files():
        if path == ROOT / "training" / "compat.py":
            continue
        if redefinition.search(path.read_text(encoding="utf-8")):
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, (
        "local strict-zip re-implementations found (duplication bug class): "
        + ", ".join(offenders)
        + " — import from training.compat instead."
    )


# ---------------------------------------------------------------------------
# Union-type annotation guard (PEP 604 is py3.10-only at runtime)
# ---------------------------------------------------------------------------
# Same split-brain class as zip-strict: ``x: dict | None`` in a def signature
# or a module-level AnnAssign is EVALUATED at runtime on py3.9 (TypeError:
# unsupported operand type(s) for |) unless the file has
# ``from __future__ import annotations`` (which stringizes annotations).
# On the py3.14 dev host the same file works silently — so a runtime test can
# never catch it: only a source guard can. 2026-08-31: six files in the loop
# (build_rl_tasks_stageB.py, decompress_for_training.py, distill100/registry.py,
# generate_distill100_teacher_responses{,,_direct}.py, test_dataset_version.py)
# hit this exact class and failed py3.9 test collection.


def _iter_annotation_unions(source: str):
    """Yield (line_no, excerpt) for every ``X | Y`` union Python would
    EVALUATE at runtime in an annotation position: def/async-def signature
    arguments, ``->`` return annotations, and single-line module/class-level
    AnnAssign annotations. Only operands that are type-like (None, NoneType,
    builtin type names, or a ``]``-terminated subscript) are flagged — plain
    ``a | b`` value expressions and ``re.X | re.Y`` regex flags are not.

    Comments and string literals are blanked first (same helper as the
    zip-strict scanner), so prose that merely mentions the pattern never
    trips the guard.
    """
    code = _strip_comments_and_strings(source)
    seen: set[tuple[int, str]] = set()

    def _emit(line_no: int, excerpt: str) -> None:
        key = (line_no, excerpt)
        if key not in seen:
            seen.add(key)
            yield key

    type_operand = (
        r"(?:None|NoneType)"
        r"|\b(?:int|str|float|bool|bytes|dict|list|set|tuple|type|complex|frozenset)\b"
        r"|\]|(?<=\w)\.\w+|[A-Z][A-Za-z_0-9]*"
    )
    union_pat = re.compile(
        r"(" + type_operand + r")\s*\|\s*(\S+)|(\S+)\s*\|\s*(" + type_operand + r")"
    )

    def _excerpt(u: re.Match) -> str:
        left, right = (u.group(1) or u.group(3)), (u.group(2) or u.group(4))
        return f"{left} | {right}"

    # 1) def signatures: paren-aware walk from ``def`` to the signature
    #    terminator (first ':' at depth 0 after the closing paren, capped).
    for m in re.finditer(r"(?:async\s+)?def\s+\w+\s*\(", code):
        depth = 1
        pos = m.end()
        while pos < len(code) and depth > 0:
            if code[pos] == "(":
                depth += 1
            elif code[pos] == ")":
                depth -= 1
            pos += 1
        end = pos
        lines_left = 3  # return annotation: at most a few more lines
        while lines_left > 0 and end < len(code) and code[end] != ":":
            if code[end] == "\n":
                lines_left -= 1
            end += 1
        window = code[m.start() : min(end + 1, len(code))]
        for u in union_pat.finditer(window):
            line_no = source.count("\n", 0, m.start() + u.start()) + 1
            yield from _emit(line_no, _excerpt(u))
    # 2) single-line AnnAssign annotations: ``name: <ann> = value`` where the
    #    annotation contains a ``|`` before the first ``=`` (values with
    #    ``|`` after the ``=`` are plain runtime expressions, not evaluated
    #    annotations, and are not flagged).
    for m in re.finditer(r"^\s*[A-Za-z_]\w*\s*:\s*[^=\n]*\|[^=\n]*", code, re.MULTILINE):
        u = union_pat.search(m.group(0))
        if u:
            line_no = source.count("\n", 0, m.start()) + 1
            yield from _emit(line_no, _excerpt(u))


def test_union_scanner_flags_def_arg_annotation() -> None:
    findings = list(_iter_annotation_unions("def f(x: dict | None = None) -> None:\n    pass\n"))
    assert len(findings) == 1
    assert findings[0][0] == 1
    assert "dict | None" in findings[0][1]


def test_union_scanner_flags_return_annotation() -> None:
    findings = list(_iter_annotation_unions("def f() -> str | None:\n    return None\n"))
    assert len(findings) == 1
    assert "str | None" in findings[0][1]


def test_union_scanner_flags_multiline_signature() -> None:
    source = (
        "def build_tests(\n"
        "    row_id: str,\n"
        "    source_contract: dict | None = None,\n"
        ") -> str:\n"
        "    return ''\n"
    )
    findings = list(_iter_annotation_unions(source))
    assert len(findings) == 1
    assert findings[0][0] == 3


def test_union_scanner_flags_module_annassign() -> None:
    findings = list(_iter_annotation_unions("CACHE: dict[str, int] | None = None\n"))
    assert len(findings) == 1


def test_union_scanner_ignores_regex_flag_union() -> None:
    source = "FLAGS = re.compile(r'x', re.DOTALL | re.IGNORECASE)\n"
    assert list(_iter_annotation_unions(source)) == []


def test_union_scanner_ignores_plain_value_union_in_def_default() -> None:
    source = "def f(x=a | b):\n    pass\n"
    assert list(_iter_annotation_unions(source)) == []


def test_union_scanner_ignores_comment_and_string_mentions() -> None:
    source = (
        "# never write x: dict | None without the future import\n"
        'doc = "def f(x: str | None) -> None:"\n'
        "def f(x):\n    pass\n"
    )
    assert list(_iter_annotation_unions(source)) == []


def test_no_annotation_union_without_future_import_in_scoped_dirs() -> None:
    """Fail on ANY ``X | Y`` union in an evaluated annotation position in
    training/ + scripts/ + evals/runner/ unless the file has
    ``from __future__ import annotations`` (stringized — safe). On the
    py3.9.6 venv these TypeErrors at module import; on the py3.14 dev host
    they silently work — the split-brain bug class that took six files on
    2026-08-31. Add the future import (or drop the union) in the file."""
    offenders: list[str] = []
    for path in _scoped_py_files():
        source = path.read_text(encoding="utf-8")
        if re.search(r"^from __future__ import annotations", source, re.MULTILINE):
            continue
        for line_no, excerpt in _iter_annotation_unions(source):
            offenders.append(f"{path.relative_to(ROOT)}:{line_no}: {excerpt}")
    assert not offenders, (
        "py3.10-only annotation unions without 'from __future__ import "
        "annotations' found in scoped dirs (py3.9 venv TypeError at import):\n"
        + "\n".join(offenders)
        + "\nAdd 'from __future__ import annotations' (behavior-neutral) instead."
    )
