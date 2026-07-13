#!/usr/bin/env python3
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FRONT_MATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@dataclasses.dataclass
class Issue:
    level: str
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload = {
            "level": self.level,
            "code": self.code,
            "message": self.message,
        }
        if self.path:
            payload["path"] = self.path
        return payload


@dataclasses.dataclass
class SkillCheck:
    name: str
    path: Path
    digest: str | None
    issues: list[Issue]
    description_length: int | None

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "path": str(self.path),
            "digest": self.digest,
            "description_length": self.description_length,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclasses.dataclass
class TargetStatus:
    label: str
    path: Path
    mode: str
    issues: list[Issue]
    synced_skills: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "path": str(self.path),
            "mode": self.mode,
            "synced_skills": self.synced_skills,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclasses.dataclass
class DoctorResult:
    repo_root: Path
    source_skills_dir: Path
    skill_names: list[str]
    skill_checks: list[SkillCheck]
    target_statuses: list[TargetStatus]
    actions: list[str]

    def all_issues(self) -> list[Issue]:
        issues: list[Issue] = []
        for check in self.skill_checks:
            issues.extend(check.issues)
        for target in self.target_statuses:
            issues.extend(target.issues)
        return issues

    def to_dict(self) -> dict[str, object]:
        return {
            "repo_root": str(self.repo_root),
            "source_skills_dir": str(self.source_skills_dir),
            "skill_names": self.skill_names,
            "skill_checks": [check.to_dict() for check in self.skill_checks],
            "targets": [target.to_dict() for target in self.target_statuses],
            "actions": self.actions,
            "issues": [issue.to_dict() for issue in self.all_issues()],
        }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect and repair Codex skill discovery in this repo. "
            "Keeps repo-local .agents/skills plus user-level caches in sync."
        )
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=("status", "verify", "fix"),
    )
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--home-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--skip-repo", action="store_true")
    parser.add_argument("--skip-global", action="store_true")
    return parser.parse_args(argv)


def parse_front_matter(text: str) -> dict[str, str]:
    match = FRONT_MATTER_PATTERN.match(text)
    if not match:
        return {}
    payload: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        payload[key.strip()] = value.strip().strip('"').strip("'")
    return payload


def is_local_markdown_link(target: str) -> bool:
    lowered = target.lower()
    return not (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("mailto:")
        or lowered.startswith("#")
    )


def tree_digest(root: Path) -> str:
    hasher = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        if path.is_symlink():
            hasher.update(b"link")
            hasher.update(relative)
            hasher.update(os.readlink(path).encode("utf-8"))
            continue
        if path.is_dir():
            hasher.update(b"dir")
            hasher.update(relative)
            continue
        hasher.update(b"file")
        hasher.update(relative)
        hasher.update(path.read_bytes())
    return hasher.hexdigest()


def backup_path(path: Path) -> Path:
    timestamp = time.strftime("%Y%m%dT%H%M%S")
    candidate = path.with_name(f"{path.name}.bak-{timestamp}")
    counter = 1
    while candidate.exists():
        candidate = path.with_name(f"{path.name}.bak-{timestamp}-{counter}")
        counter += 1
    return candidate


def replace_tree(src: Path, dest: Path) -> None:
    if dest.exists() or dest.is_symlink():
        if dest.is_dir() and not dest.is_symlink():
            shutil.rmtree(dest)
        else:
            dest.rename(backup_path(dest))
    shutil.copytree(src, dest)


def discover_skill_dirs(skills_root: Path) -> list[Path]:
    if not skills_root.exists():
        return []
    directories: list[Path] = []
    for candidate in sorted(skills_root.iterdir()):
        if candidate.is_dir() and (candidate / "SKILL.md").is_file():
            directories.append(candidate)
    return directories


def sync_managed_skill_dirs(source_root: Path, dest_root: Path, actions: list[str]) -> None:
    dest_root.mkdir(parents=True, exist_ok=True)
    for skill_dir in discover_skill_dirs(source_root):
        dest_skill_dir = dest_root / skill_dir.name
        replace_tree(skill_dir, dest_skill_dir)
        actions.append(f"Synced {skill_dir.name} -> {dest_skill_dir}")


def ensure_symlink_or_mirror(
    source_dir: Path,
    dest_path: Path,
    *,
    prefer_symlink: bool,
    actions: list[str],
) -> str:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    relative_target = os.path.relpath(source_dir, dest_path.parent)

    if prefer_symlink:
        if dest_path.is_symlink():
            current_target = os.readlink(dest_path)
            if current_target == relative_target:
                return "symlink_ok"
            dest_path.unlink()
            actions.append(
                f"Replaced wrong symlink {dest_path} -> {current_target} with {relative_target}"
            )
        elif dest_path.exists():
            if dest_path.is_dir():
                sync_managed_skill_dirs(source_dir, dest_path, actions)
                return "directory_mirror"
            moved_to = backup_path(dest_path)
            dest_path.rename(moved_to)
            actions.append(f"Backed up blocking path {dest_path} -> {moved_to}")
        dest_path.symlink_to(relative_target)
        actions.append(f"Created symlink {dest_path} -> {relative_target}")
        return "symlink_created"

    sync_managed_skill_dirs(source_dir, dest_path, actions)
    return "directory_mirror"


def build_skill_check(skill_dir: Path) -> SkillCheck:
    issues: list[Issue] = []
    skill_md_path = skill_dir / "SKILL.md"
    digest: str | None = None
    description_length: int | None = None

    if not skill_md_path.exists():
        issues.append(
            Issue(
                level="error",
                code="missing_skill_md",
                message="Skill directory is missing SKILL.md",
                path=str(skill_md_path),
            )
        )
    else:
        text = skill_md_path.read_text(encoding="utf-8")
        front_matter = parse_front_matter(text)
        if not front_matter.get("name"):
            issues.append(
                Issue(
                    level="error",
                    code="missing_skill_name",
                    message="SKILL.md front matter is missing name",
                    path=str(skill_md_path),
                )
            )
        description = front_matter.get("description")
        if not description:
            issues.append(
                Issue(
                    level="error",
                    code="missing_skill_description",
                    message="SKILL.md front matter is missing description",
                    path=str(skill_md_path),
                )
            )
        else:
            description_length = len(description)
            if description_length > 220:
                issues.append(
                    Issue(
                        level="warning",
                        code="long_skill_description",
                        message=(
                            "Skill description is long enough that Codex may truncate it "
                            "in the initial skills list."
                        ),
                        path=str(skill_md_path),
                    )
                )
        for link_target in LINK_PATTERN.findall(text):
            if not is_local_markdown_link(link_target):
                continue
            normalized_target = link_target.split("#", 1)[0]
            if not normalized_target:
                continue
            resolved = (skill_dir / normalized_target).resolve()
            if not resolved.exists():
                issues.append(
                    Issue(
                        level="error",
                        code="missing_link_target",
                        message=f"Linked local skill resource does not exist: {link_target}",
                        path=str(skill_md_path),
                    )
                )
        digest = tree_digest(skill_dir)

    return SkillCheck(
        name=skill_dir.name,
        path=skill_dir,
        digest=digest,
        issues=issues,
        description_length=description_length,
    )


def compare_skill_digests(source_root: Path, dest_root: Path) -> tuple[list[str], list[Issue]]:
    synced: list[str] = []
    issues: list[Issue] = []
    for skill_dir in discover_skill_dirs(source_root):
        dest_skill_dir = dest_root / skill_dir.name
        if not dest_skill_dir.exists():
            issues.append(
                Issue(
                    level="error",
                    code="missing_synced_skill",
                    message=f"Destination is missing synced skill {skill_dir.name}",
                    path=str(dest_skill_dir),
                )
            )
            continue
        if tree_digest(skill_dir) != tree_digest(dest_skill_dir):
            issues.append(
                Issue(
                    level="error",
                    code="skill_drift",
                    message=f"Destination copy for {skill_dir.name} is out of sync",
                    path=str(dest_skill_dir),
                )
            )
        else:
            synced.append(skill_dir.name)
    return synced, issues


def inspect_target(label: str, source_root: Path, target_path: Path) -> TargetStatus:
    issues: list[Issue] = []
    synced: list[str] = []
    mode = "missing"

    if target_path.is_symlink():
        mode = "symlink"
        resolved = target_path.resolve()
        if not resolved.exists():
            issues.append(
                Issue(
                    level="error",
                    code="broken_symlink",
                    message="Skill target symlink is broken",
                    path=str(target_path),
                )
            )
        else:
            synced, compare_issues = compare_skill_digests(source_root, resolved)
            issues.extend(compare_issues)
    elif target_path.exists():
        if target_path.is_dir():
            mode = "directory"
            synced, compare_issues = compare_skill_digests(source_root, target_path)
            issues.extend(compare_issues)
        else:
            mode = "blocking_file"
            issues.append(
                Issue(
                    level="error",
                    code="blocking_file",
                    message="Skill target path is a file, not a directory or symlink",
                    path=str(target_path),
                )
            )
    else:
        issues.append(
            Issue(
                level="error",
                code="missing_target",
                message="Skill target path does not exist",
                path=str(target_path),
            )
        )

    return TargetStatus(
        label=label,
        path=target_path,
        mode=mode,
        issues=issues,
        synced_skills=synced,
    )


def run_doctor(
    *,
    repo_root: Path,
    home_dir: Path,
    command: str,
    skip_repo: bool,
    skip_global: bool,
) -> DoctorResult:
    source_skills_dir = repo_root / "skills"
    repo_skills_entrypoint = repo_root / ".agents" / "skills"
    codex_user_skills = home_dir / ".codex" / "skills"
    agents_user_skills = home_dir / ".agents" / "skills"
    actions: list[str] = []

    if command == "fix":
        if not skip_repo:
            ensure_symlink_or_mirror(
                source_skills_dir,
                repo_skills_entrypoint,
                prefer_symlink=True,
                actions=actions,
            )
        if not skip_global:
            sync_managed_skill_dirs(source_skills_dir, codex_user_skills, actions)
            ensure_symlink_or_mirror(
                codex_user_skills,
                agents_user_skills,
                prefer_symlink=True,
                actions=actions,
            )

    skill_checks = [
        build_skill_check(skill_dir) for skill_dir in discover_skill_dirs(source_skills_dir)
    ]
    target_statuses: list[TargetStatus] = []
    if not skip_repo:
        target_statuses.append(
            inspect_target("repo_local", source_skills_dir, repo_skills_entrypoint)
        )
    if not skip_global:
        target_statuses.append(
            inspect_target("user_codex_cache", source_skills_dir, codex_user_skills)
        )
        target_statuses.append(
            inspect_target("user_agents_cache", source_skills_dir, agents_user_skills)
        )

    return DoctorResult(
        repo_root=repo_root,
        source_skills_dir=source_skills_dir,
        skill_names=[skill_dir.name for skill_dir in discover_skill_dirs(source_skills_dir)],
        skill_checks=skill_checks,
        target_statuses=target_statuses,
        actions=actions,
    )


def print_human(result: DoctorResult) -> None:
    print(f"repo_root={result.repo_root}")
    print(f"source_skills_dir={result.source_skills_dir}")
    print(f"skill_names={','.join(result.skill_names)}")
    for target in result.target_statuses:
        print(f"target={target.label} mode={target.mode} path={target.path}")
        if target.synced_skills:
            print(f"target_synced={target.label}:{','.join(target.synced_skills)}")
        for issue in target.issues:
            print(f"{issue.level} {issue.code} {issue.message} path={issue.path or ''}".strip())
    for check in result.skill_checks:
        print(f"skill={check.name} digest={check.digest or 'missing'}")
        for issue in check.issues:
            print(f"{issue.level} {issue.code} {issue.message} path={issue.path or ''}".strip())
    for action in result.actions:
        print(f"action={action}")


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    repo_root = (args.repo_root or Path(__file__).resolve().parents[1]).resolve()
    home_dir = (args.home_dir or Path.home()).resolve()
    result = run_doctor(
        repo_root=repo_root,
        home_dir=home_dir,
        command=args.command,
        skip_repo=args.skip_repo,
        skip_global=args.skip_global,
    )
    issues = result.all_issues()
    has_error = any(issue.level == "error" for issue in issues)
    has_warning = any(issue.level == "warning" for issue in issues)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print_human(result)

    if args.command == "status":
        return 0
    if has_error:
        return 1
    if args.strict and has_warning:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
