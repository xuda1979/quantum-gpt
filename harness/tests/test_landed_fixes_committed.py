"""C-0078: named landed fixes must be TRACKED in git (tree-sync drop guard).

The QG harness queue named three landed-fix families that existed only as
untracked files, so a tree sync / checkout could silently drop them:
  1. C-0051 fire-on-ready watcher + its test (tmp/c0051_fire_on_ready.py)
  2. dep-graph rebaseline contract test family v1-v7 + goal-done fire-drill
  3. C-0034-class None-candidate scorer patch (already committed as 923c9c2;
     pinned here so it cannot regress to untracked)

RED 2026-09-17: items 1-2 were untracked (git ls-files empty).
GREEN: after git add + commit of exactly those files.
The guard is read-only (git ls-files) and never mutates the tree.
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Card C-0078 named set: path -> one-line why.
NAMED_LANDED_FIXES = {
    "tmp/c0051_fire_on_ready.py": "C-0051 fire-on-ready watcher (owns C-0002 role)",
    "harness/tests/test_c0051_fire_on_ready.py": "C-0051 watcher contract test",
    "harness/tests/test_dep_graph_rebaseline.py": "dep-graph rebaseline contract v1",
    "harness/tests/test_dep_graph_rebaseline_v2.py": "dep-graph rebaseline contract v2",
    "harness/tests/test_dep_graph_rebaseline_v3.py": "dep-graph rebaseline contract v3",
    "harness/tests/test_dep_graph_rebaseline_v4_p1_shells.py": "dep-graph contract v4 p1 shells",
    "harness/tests/test_dep_graph_rebaseline_v5_dep_existence.py": "dep-graph contract v5 dep existence",
    "harness/tests/test_dep_graph_rebaseline_v6_undeadlock_spine.py": "dep-graph contract v6 undeadlock spine",
    "harness/tests/test_dep_graph_rebaseline_v7_canonical_spine_shells.py": "dep-graph contract v7 canonical spine shells",
    "harness/tests/test_c0057_goal_done_fire_drill.py": "goal-done fire-drill (C-9055 reconciliation)",
    "evals/runner/single_candidate_eval.py": "C-0034-class None-candidate scorer patch (923c9c2)",
    "tests/test_single_candidate_eval_none_candidate.py": "C-0034-class scorer patch test (923c9c2)",
}


def _tracked(rel):
    proc = subprocess.run(
        ["git", "ls-files", "--error-unmatch", rel],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0


def test_named_landed_fixes_are_tracked_in_git():
    untracked = [p for p in NAMED_LANDED_FIXES if not _tracked(p)]
    assert (
        not untracked
    ), f"landed fixes untracked in git (a tree sync can silently drop them): {sorted(untracked)}"


def test_guard_list_covers_the_card_named_families():
    rels = set(NAMED_LANDED_FIXES)
    for family in (
        "tmp/c0051_fire_on_ready.py",
        "harness/tests/test_c0051_fire_on_ready.py",
        "harness/tests/test_dep_graph_rebaseline.py",
        "harness/tests/test_dep_graph_rebaseline_v7_canonical_spine_shells.py",
        "evals/runner/single_candidate_eval.py",
    ):
        assert family in rels, f"guard list lost a named family: {family}"
