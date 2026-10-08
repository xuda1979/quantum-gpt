from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "codex_skill_doctor.py"
SPEC = importlib.util.spec_from_file_location("codex_skill_doctor", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_skill(
    root: Path, name: str, description: str = "Trigger on bounded repo workflows."
) -> Path:
    skill_dir = root / "skills" / name
    (skill_dir / "references").mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        "---\n\n"
        "Use this skill.\n\n"
        "[Ref](references/guide.md)\n",
        encoding="utf-8",
    )
    (skill_dir / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    return skill_dir


def test_fix_creates_repo_and_user_skill_targets(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    home_dir = tmp_path / "home"
    write_skill(repo_root, "demo-skill")

    result = MODULE.run_doctor(
        repo_root=repo_root,
        home_dir=home_dir,
        command="fix",
        skip_repo=False,
        skip_global=False,
    )

    repo_entry = repo_root / ".agents" / "skills"
    assert repo_entry.exists()
    assert repo_entry.is_symlink()
    assert repo_entry.resolve() == (repo_root / "skills").resolve()

    codex_user_skill = home_dir / ".codex" / "skills" / "demo-skill" / "SKILL.md"
    assert codex_user_skill.exists()

    agents_user_entry = home_dir / ".agents" / "skills"
    assert agents_user_entry.exists()
    assert agents_user_entry.is_symlink()
    assert agents_user_entry.resolve() == (home_dir / ".codex" / "skills").resolve()

    assert not any(issue.level == "error" for issue in result.all_issues())


def test_missing_local_link_is_reported(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    home_dir = tmp_path / "home"
    skill_dir = repo_root / "skills" / "broken-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: broken-skill\n"
        "description: Trigger on bounded repo workflows.\n"
        "---\n\n"
        "[Missing](references/missing.md)\n",
        encoding="utf-8",
    )

    result = MODULE.run_doctor(
        repo_root=repo_root,
        home_dir=home_dir,
        command="verify",
        skip_repo=True,
        skip_global=True,
    )

    issues = [issue.code for issue in result.all_issues()]
    assert "missing_link_target" in issues
