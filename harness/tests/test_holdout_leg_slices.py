"""Tests for run_holdout_leg1 compute_slices and merge_slice_scores."""

from __future__ import annotations

import json
import os
import sys
import unittest

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from scripts.run_holdout_leg1 import compute_slices, merge_slice_scores  # noqa: E402


class TestComputeSlices(unittest.TestCase):
    def test_18_tasks_3_slices(self):
        slices = compute_slices(18, 3)
        self.assertEqual(len(slices), 3)
        self.assertEqual(sum(c for _, c in slices), 18)
        self.assertTrue(all(c > 0 for _, c in slices))
        # Disjoint and contiguous
        self.assertEqual(slices, [(0, 6), (6, 6), (12, 6)])

    def test_1_task_3_slices_degenerates_to_1_slice(self):
        slices = compute_slices(1, 3)
        self.assertEqual(len(slices), 1)
        self.assertEqual(sum(c for _, c in slices), 1)

    def test_2_tasks_3_slices(self):
        slices = compute_slices(2, 3)
        self.assertEqual(sum(c for _, c in slices), 2)
        self.assertTrue(all(c > 0 for _, c in slices))

    def test_0_tasks_raises(self):
        with self.assertRaises(ValueError):
            compute_slices(0, 3)

    def test_7_tasks_3_slices(self):
        slices = compute_slices(7, 3)
        self.assertEqual(sum(c for _, c in slices), 7)
        self.assertTrue(all(c > 0 for _, c in slices))
        # 7 = 3+2+2
        self.assertEqual(slices, [(0, 3), (3, 2), (5, 2)])


class TestMergeSliceScores(unittest.TestCase):
    def _slice_payload(self, task_ids, adapter_passes, base_passes):
        records = []
        for tid, ap, bp in zip(task_ids, adapter_passes, base_passes, strict=False):
            records.append(
                dict(
                    model="adapter",
                    task_id=tid,
                    passed=ap,
                    scores=dict(overall=1.0 if ap else 0.0),
                    truncated=False,
                )
            )
            records.append(
                dict(
                    model="base",
                    task_id=tid,
                    passed=bp,
                    scores=dict(overall=1.0 if bp else 0.0),
                    truncated=False,
                )
            )
        return dict(task_ids=list(task_ids), records=records)

    def test_merge_2_slices_covers_all_tasks(self):
        import tempfile

        tmp = tempfile.mkdtemp()
        ids = ["t%02d" % i for i in range(6)]
        s1 = self._slice_payload(ids[:3], [True, True, False], [False, False, False])
        s2 = self._slice_payload(ids[3:], [True, False, False], [False, False, False])
        p1 = os.path.join(tmp, "s1.json")
        p2 = os.path.join(tmp, "s2.json")
        with open(p1, "w") as f:
            json.dump(s1, f)
        with open(p2, "w") as f:
            json.dump(s2, f)
        merged = merge_slice_scores([p1, p2], ids)
        self.assertEqual(len(merged["records"]), 12)
        self.assertEqual(merged["benchmark_ids"], ids)


if __name__ == "__main__":
    unittest.main()
