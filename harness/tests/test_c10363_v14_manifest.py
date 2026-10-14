"""C-10363 TDD: v14 SFT mixture manifest authoring.

GREEN required:
  - v14 manifest exists under outputs/ (JSON + MD);
  - 13 failing tasks from C-10358 panel represented, each with exact
    (task, missing symbol) api-gap pair;
  - every gap symbol validated present in the reference solutions dir;
  - full 39 delta rows (13 tasks x 3 prompt variants);
  - counts delta vs v12e mixture recorded (2213 base, +39 delta, 2252 total);
  - no training launch required (pure manifest authoring).
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from collections import Counter

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

PANEL = json.loads(open(os.path.join(_REPO, "outputs", "C10358_step322_failure_delta_panel.json")).read())
VAL = json.loads(open(os.path.join(_REPO, "outputs", "C10363_gap_symbol_validation.json")).read())
JSON_MAN = json.loads(open(os.path.join(_REPO, "outputs", "C10363_v14_mixture_manifest.json")).read())
MD_PATH = os.path.join(_REPO, "outputs", "C10363_v14_mixture_manifest.md")

FAILING_TASKS = [t["task_id"] for t in PANEL["failing_tasks"]]


class TestC10363V14Manifest(unittest.TestCase):
    def test_manifest_files_exist(self):
        self.assertTrue(os.path.isfile(os.path.join(_REPO, "outputs", "C10363_v14_mixture_manifest.json")))
        self.assertTrue(os.path.isfile(MD_PATH))

    def test_all_13_failing_tasks_covered(self):
        rows = JSON_MAN["few_shot_rows"]
        bench_ids = set(r["bench_task_id"] for r in rows)
        self.assertEqual(len(FAILING_TASKS), 13)
        self.assertEqual(bench_ids, set(FAILING_TASKS))

    def test_each_row_has_exact_api_gap_pair(self):
        rows = JSON_MAN["few_shot_rows"]
        by_task = {}
        for t in PANEL["failing_tasks"]:
            by_task[t["task_id"]] = t["api_gap"]
        for r in rows:
            self.assertIn(r["bench_task_id"], by_task)
            self.assertEqual(r["api_gap"], by_task[r["bench_task_id"]])
            self.assertTrue(r["gap_symbol_verified"])

    def test_gap_symbols_validated_in_reference_solutions(self):
        self.assertTrue(VAL["all_gap_symbols_valid_in_reference_solutions"])
        self.assertEqual(VAL["n_failing_tasks"], 13)

    def test_39_delta_rows_3_per_task(self):
        rows = JSON_MAN["few_shot_rows"]
        self.assertEqual(len(rows), 39)
        counts = Counter(r["bench_task_id"] for r in rows)
        self.assertEqual(set(counts.values()), {3})

    def test_counts_delta_vs_v12e(self):
        counts = JSON_MAN["counts_delta_vs_v12e"]
        self.assertEqual(counts["v12e_replay_rows"], 2213)
        self.assertEqual(counts["v14_delta_rows"], 39)
        self.assertEqual(counts["v14_total_rows"], 2252)
        self.assertEqual(counts["row_delta_abs"], 39)
        self.assertEqual(counts["v12e_sha256"], "e0bbdf5fb0f606dc247c4f757c204eb645faf7f8cdaf922625be0edb6bede991")
        self.assertEqual(JSON_MAN["v14_row_count"], 2252)

    def test_completion_is_frozen_reference_candidate(self):
        from pathlib import Path
        for r in JSON_MAN["few_shot_rows"]:
            tdir = r["task_id"]
            cand = Path(_REPO) / "evals" / "tasks" / "quantum" / tdir / "candidate.py"
            self.assertTrue(cand.is_file(), "missing candidate " + tdir)
            src = cand.read_text(encoding="utf-8").rstrip(chr(10))
            self.assertEqual(r["messages"][-1]["content"], src)

    def test_fault_class_counts_match_panel(self):
        self.assertEqual(JSON_MAN["fault_class_counts"], dict(PANEL["fault_class_counts"]))


if __name__ == "__main__":
    unittest.main()
