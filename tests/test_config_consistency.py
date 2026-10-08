"""TDD: pipeline config consistency — catch mismatches like 2048 train vs 4096 eval.

The harness should find stupid mistakes like this at first place, not weeks later.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from harness.harness_lib import check_pipeline_config_consistency


class TestConfigConsistency(unittest.TestCase):
    def test_token_mismatch_detected(self):
        """Training rollout 2048 vs eval 4096 must be flagged."""
        configs = {
            "training_max_new_tokens": 2048,
            "eval_max_new_tokens": 4096,
            "inference_max_new_tokens": 4096,
        }
        issues = check_pipeline_config_consistency(configs)
        self.assertTrue(any("max_new_tokens" in i["field"] for i in issues))

    def test_tokens_all_match_no_issue(self):
        configs = {
            "training_max_new_tokens": 4096,
            "eval_max_new_tokens": 4096,
            "inference_max_new_tokens": 4096,
        }
        issues = check_pipeline_config_consistency(configs)
        self.assertEqual(issues, [])

    def test_benchmark_file_mismatch_detected(self):
        configs = {
            "training_benchmark": "v8_holdout_adjacent.txt",
            "eval_benchmark": "sapo_promotion_holdout_v1_18.txt",
        }
        issues = check_pipeline_config_consistency(configs)
        self.assertTrue(any("benchmark" in i["field"] for i in issues))

    def test_model_path_mismatch_detected(self):
        configs = {
            "training_model": "/root/work/filestorage/Qwen3.8-27B",
            "eval_model": "/root/work/filestorage/Qwen3.8-27B-old",
        }
        issues = check_pipeline_config_consistency(configs)
        self.assertTrue(any("model" in i["field"] for i in issues))


if __name__ == "__main__":
    unittest.main()
