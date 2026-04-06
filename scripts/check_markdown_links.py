#!/usr/bin/env python3
"""Check Markdown links for missing targets and non-portable absolute filesystem paths."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


INLINE_LINK_RE = re.compile(r"(?<!\!)\[([^\]]+)\]\(([^)\n]+)\)")
REFERENCE_DEF_RE = re.compile(r"^\[([^\]]+)\]:\s*(\S+)", re.MULTILINE)
EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    "node_modules",
}


@dataclass(frozen=True)
class MarkdownIssue:
    path: Path
    line: int
    kind: str
    target: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", default=["."], help="Markdown file or directory roots to scan.")
    return parser.parse_args()


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)


def normalize_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")].strip()
    return target.split()[0]


def is_external_target(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "tel:", "#"))


def split_target_path(target: str) -> str:
    return target.split("#", 1)[0].split("?", 1)[0]


def iter_markdown_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            if path.suffix == ".md" and not should_skip(path):
                yield path
            continue
        for candidate in path.rglob("*.md"):
            if not should_skip(candidate):
                yield candidate


def scan_markdown_file(path: Path) -> list[MarkdownIssue]:
    text = path.read_text(encoding="utf-8")
    issues: list[MarkdownIssue] = []
    matches = list(INLINE_LINK_RE.finditer(text)) + list(REFERENCE_DEF_RE.finditer(text))
    for match in matches:
        target = normalize_target(match.group(2))
        if not target or is_external_target(target):
            continue
        target_path = split_target_path(target)
        if not target_path:
            continue
        line = text.count("\n", 0, match.start()) + 1
        if target_path.startswith("/"):
            issues.append(
                MarkdownIssue(
                    path=path,
                    line=line,
                    kind="absolute-path",
                    target=target,
                    detail="avoid machine-local absolute filesystem links in Markdown",
                )
            )
            continue
        resolved = (path.parent / target_path).resolve(strict=False)
        if not resolved.exists():
            issues.append(
                MarkdownIssue(
                    path=path,
                    line=line,
                    kind="missing-target",
                    target=target,
                    detail=f"missing target: {path.parent / target_path}",
                )
            )
    return issues


def collect_markdown_issues(paths: Iterable[Path]) -> list[MarkdownIssue]:
    issues: list[MarkdownIssue] = []
    for path in sorted(iter_markdown_files(paths)):
        issues.extend(scan_markdown_file(path))
    return issues


def main() -> int:
    args = parse_args()
    issues = collect_markdown_issues(Path(path) for path in args.paths)
    for issue in issues:
        print(f"{issue.path}:{issue.line}: {issue.kind}: {issue.target} ({issue.detail})")
    if issues:
        print(f"Found {len(issues)} Markdown link issue(s).")
        return 1
    print("No Markdown link issues found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
