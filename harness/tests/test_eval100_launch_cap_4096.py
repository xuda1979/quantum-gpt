"""C-9379 RED test: the eval100 ASI2 launch script must not push a
1536-token cap that truncates long quantum solutions.

Background: C-9198 raised the eval runner default from 1536 to 4096
(run_holdout_leg1/2.py, run_asi2_base_adapter_rubric_eval.py and
eval_100_reeval.py's module-level MAX_NEW_TOKENS all carry 4096, guarded
by harness/tests/test_c9051_box_parity.py and
tests/test_c9198_token_cap_4096.py). But scripts/launch_eval100_asi2.sh
still passes an explicit --max-new-tokens 1536 which OVERRIDES the
module default when it dispatches eval_100_reeval.py -- silently re-
introducing the truncation bug the bank raised the ceiling to fix.

This test is the RED gate: it parses the launch script's explicit
--max-new-tokens flag and fails while it is still 1536.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

MIN_CAP = 4096

REEVAL_REL = "scripts/eval_100_reeval.py"
REEVAL_DEFAULT_RE = re.compile(r"MAX_NEW_TOKENS\s*=\s*(\d+)")

LAUNCH_REL = "scripts/launch_eval100_asi2.sh"
LAUNCH_FLAG_RE = re.compile(r"--max-new-tokens\s+(\d+)")


def _read(rel):
    p = ROOT / rel
    assert p.is_file(), "missing canonical file: " + rel
    return p.read_text(encoding="utf-8")


def _reeval_default():
    m = REEVAL_DEFAULT_RE.search(_read(REEVAL_REL))
    assert m, REEVAL_REL + " has no MAX_NEW_TOKENS constant"
    return int(m.group(1))


def _launch_flag():
    txt = _read(LAUNCH_REL)
    m = LAUNCH_FLAG_RE.search(txt)
    assert m, LAUNCH_REL + " has no explicit --max-new-tokens flag"
    return int(m.group(1))


class Eval100LaunchCapTest(unittest.TestCase):
    def test_reeval_module_default_is_4096(self):
        self.assertGreaterEqual(
            _reeval_default(), MIN_CAP,
            REEVAL_REL + " MAX_NEW_TOKENS must be >= " + str(MIN_CAP),
        )

    def test_launch_script_does_not_undercut_cap(self):
        launch = _launch_flag()
        self.assertGreaterEqual(
            launch, MIN_CAP,
            LAUNCH_REL + " --max-new-tokens " + str(launch)
            + " under-cuts the " + str(MIN_CAP) + " cap; truncates s97-class "
            "solutions (C-9038 rebank4 / C-9198).",
        )
        self.assertEqual(
            launch, _reeval_default(),
            LAUNCH_REL + " --max-new-tokens (" + str(launch)
            + ") drifted from " + REEVAL_REL + " default ("
            + str(_reeval_default()) + "); they must track the same cap.",
        )


if __name__ == "__main__":
    unittest.main()
