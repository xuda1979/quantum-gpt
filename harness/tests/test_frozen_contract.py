"""Tests for evals.runner.frozen_contract -- frozen eval contract verification."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from evals.runner.frozen_contract import (  # noqa: E402
    aggregate_sha256,
    repo_relative,
    sha256_bytes,
    sha256_file,
    sha256_text,
    verify_frozen_eval_contract,
)


class TestShaHelpers(unittest.TestCase):
    def test_sha256_bytes_matches_hashlib(self):
        import hashlib

        self.assertEqual(sha256_bytes(b"hello"), hashlib.sha256(b"hello").hexdigest())

    def test_sha256_text_encodes_utf8(self):
        import hashlib

        self.assertEqual(sha256_text("hello"), hashlib.sha256(b"hello").hexdigest())

    def test_aggregate_sha256_is_deterministic(self):
        h1 = aggregate_sha256({"a": 1, "b": 2})
        h2 = aggregate_sha256({"a": 1, "b": 2})
        self.assertEqual(h1, h2)

    def test_repo_relative_strips_root(self):
        root = Path("/tmp/test_root")
        rel = repo_relative(root / "evals" / "foo.py", root)
        self.assertEqual(rel, "evals/foo.py")


class TestVerifyFrozenEvalContract(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="frozen-contract-test-"))
        self.run_dir = self.root / "outputs" / "run1"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.task_dir = self.root / "evals" / "tasks" / "quantum" / "test_task"
        self.task_dir.mkdir(parents=True, exist_ok=True)
        self.task_json = self.task_dir / "task.json"
        self.task_json.write_text(
            json.dumps({"id": "quantum_test_task", "name": "Test", "task_prompt": "Do X"})
        )
        self.tests_py = self.task_dir / "tests.py"
        self.tests_py.write_text("def run_tests(c):\n    return dict(passed=True, details=[])\n")
        self.prompt_file = self.run_dir / "prompt_test.txt"
        self.prompt_text = "Solve the test task."
        self.prompt_file.write_text(self.prompt_text)
        self.runner = self.root / "evals" / "runner" / "run_eval.py"
        self.runner.parent.mkdir(parents=True, exist_ok=True)
        self.runner.write_text("# eval runner\n")

    def tearDown(self):
        import shutil

        shutil.rmtree(self.root, ignore_errors=True)

    def _full_manifest(self):
        m = {
            "tasks": [
                {
                    "id": "test",
                    "prompt_file": "prompt_test.txt",
                    "prompt_sha256": sha256_text(self.prompt_text),
                    "test_file": "evals/tasks/quantum/test_task/tests.py",
                    "test_file_sha256": sha256_file(self.tests_py),
                    "task_json_file": "evals/tasks/quantum/test_task/task.json",
                    "task_json_sha256": sha256_file(self.task_json),
                }
            ],
            "evaluation_runner_sha256": sha256_file(self.runner),
        }
        return m

    def test_correct_contract_passes(self):
        m = self._full_manifest()
        result = verify_frozen_eval_contract(self.run_dir, m, root=self.root)
        self.assertIsNotNone(result["evaluation_runner_sha256"])

    def test_tampered_prompt_raises(self):
        m = self._full_manifest()
        self.prompt_file.write_text("TAMPERED")
        with self.assertRaises(SystemExit):
            verify_frozen_eval_contract(self.run_dir, m, root=self.root)

    def test_missing_prompt_file_raises(self):
        m = self._full_manifest()
        self.prompt_file.unlink()
        with self.assertRaises(SystemExit):
            verify_frozen_eval_contract(self.run_dir, m, root=self.root)

    def test_tampered_test_file_raises(self):
        m = self._full_manifest()
        self.tests_py.write_text("TAMPERED")
        with self.assertRaises(SystemExit):
            verify_frozen_eval_contract(self.run_dir, m, root=self.root)

    def test_tampered_task_json_raises(self):
        m = self._full_manifest()
        self.task_json.write_text(json.dumps({"id": "tampered"}))
        with self.assertRaises(SystemExit):
            verify_frozen_eval_contract(self.run_dir, m, root=self.root)

    def test_historical_manifest_without_hashes_passes(self):
        m = {"tasks": [{"id": "test", "prompt_file": "prompt_test.txt"}]}
        result = verify_frozen_eval_contract(self.run_dir, m, root=self.root)
        self.assertIsNone(result["public_eval_contract_sha256"])
        self.assertIsNone(result["scorer_contract_sha256"])

    def test_scorer_sha_without_test_file_path_fails_closed(self):
        """C-9479: a manifest with test_file_sha256 but no test_file path
        must fail-closed, not silently skip the scorer verification."""
        m = self._full_manifest()
        del m["tasks"][0]["test_file"]
        with self.assertRaises(SystemExit) as ctx:
            verify_frozen_eval_contract(self.run_dir, m, root=self.root)
        self.assertIn("test_file", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
