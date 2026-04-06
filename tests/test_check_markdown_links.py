from __future__ import annotations

from pathlib import Path

from scripts.check_markdown_links import collect_markdown_issues


def test_collect_markdown_issues_accepts_valid_relative_and_external_links(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    target = docs / "target.md"
    target.write_text("# target\n", encoding="utf-8")
    source = docs / "source.md"
    source.write_text(
        "\n".join(
            [
                "[relative](target.md)",
                "[external](https://example.com)",
                "[anchor](#section)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    issues = collect_markdown_issues([tmp_path])
    assert issues == []


def test_collect_markdown_issues_reports_missing_targets_and_absolute_paths(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    source = docs / "source.md"
    source.write_text(
        "\n".join(
            [
                "[missing](missing.md)",
                "[absolute](/Users/example/project/file.md)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    issues = collect_markdown_issues([tmp_path])

    assert len(issues) == 2
    issue_map = {issue.kind: issue.target for issue in issues}
    assert issue_map["absolute-path"] == "/Users/example/project/file.md"
    assert issue_map["missing-target"] == "missing.md"
