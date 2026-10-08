"""C-9475 RED: run_eval --candidate-map should only run tasks in the map."""

import json
import os
import sys
import unittest
from pathlib import Path

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
REPO = os.path.dirname(HARNESS_DIR)
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "evals", "runner"))

import run_eval as RE


class TestCandidateMapFilters(unittest.TestCase):
    def test_candidate_map_filters_task_list(self):
        all_tasks = RE.discover_tasks()
        task_ids = []
        for tf in all_tasks:
            meta = json.loads(tf.read_text())
            task_ids.append(meta["id"])
            if len(task_ids) >= 3:
                break
        overrides = {tid: Path("/dev/null") for tid in task_ids}
        filtered = RE.select_candidate_tasks(all_tasks, overrides)
        self.assertEqual(len(filtered), 3)

    def test_empty_overrides_keeps_all_tasks(self):
        all_tasks = RE.discover_tasks()
        filtered = RE.select_candidate_tasks(all_tasks, {})
        self.assertEqual(len(filtered), len(all_tasks))


if __name__ == "__main__":
    unittest.main()
