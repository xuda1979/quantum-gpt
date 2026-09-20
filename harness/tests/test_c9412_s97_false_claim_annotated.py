# C-9412 QA-STEWARD governance test.
#
# C-9387's why-field in the live QUEUE.json previously falsely claimed the s97
# adapter was trained on Qwen3.6-35B-A3B. Verified truth:
#   harness/state/staged/s97_20260908/adapter_config.json
#       base_model_name_or_path = /root/work/filestorage/Qwen3.8-27B
# C-9412 annotates that why-field so decision makers know s97 IS on Qwen3.8-27B
# and s97 re-eval is a valid goal path. Fail closed if the annotation is missing.
from __future__ import annotations

import json
import os
import unittest

STATE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "harness",
    "state",
    "QUEUE.json",
)


def c9387_why():
    with open(STATE) as f:
        data = json.load(f)
    for c in data["cards"]:
        if c.get("id") == "C-9387":
            return c.get("why", "")
    return None


class TestC9387S97CorrectionAnnotation(unittest.TestCase):
    def test_c9387_why_field_says_s97_is_qwen38_27b(self):
        why = c9387_why()
        self.assertIsNotNone(why, "C-9387 not present in live QUEUE.json")
        self.assertIn("Qwen3.8-27B", why, "C-9387 why-field does not state s97 is on Qwen3.8-27B")
        self.assertIn("CORRECTED", why, "C-9387 why-field lacks CORRECTED annotation marker")

    def test_c9387_why_field_no_longer_loads_false_claim(self):
        why = c9387_why()
        self.assertIn("is FALSE", why, "C-9387 why-field does not mark the old claim as false")
        self.assertIn(
            "adapter_config.json", why, "C-9387 why-field does not cite the verified source"
        )


if __name__ == "__main__":
    unittest.main()
