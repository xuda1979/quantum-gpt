"""C-0076 leg-2: the ASI3 wedge artifacts must carry the LIVE broker evidence.

RED (measured 2026-09-16T20:53-20:58Z): leg-1 (18:40Z dispatch) ruled the
auth-capture retry loop OUT at 18:45Z, but the shared auth-broker log
(/tmp/huanxin-auth-broker.log, singleton launchd com.quantumgpt.huanxin-auth-broker
on :19090) shows the loop LIVE from 18:53:43Z -- 331 "session expired;
re-bootstrapping" lines, 103 "capture returned no callback (user Chrome not
logged in?)", capture attempts abandoned after attempt 3 (19:23:30Z) -- and
ASI3's /health currentUrl gained OAuth callback params (code=/session_state=)
that were ABSENT in leg-1's own probes. A cure package that omits the live
auth loop tells the user to cure half the wedge.

These tests bind ONLY to the two card artifacts (hermetic: no network, no
live daemons). They parse the leg-2 amendment block, so an amendment that
drops the measured numbers, the user-Chrome cure step, or the fail-closed
verification bar fails here.
"""

import os
import re
import unittest

HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBES = os.path.join(HARNESS_DIR, "state", "probes")
WEDGE_PATH = os.path.join(PROBES, "asi3_wedge_class.md")
CURE_PATH = os.path.join(PROBES, "asi3_user_cure_package.md")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class TestWedgeClassArtifact(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(WEDGE_PATH):
            self.skipTest("wedge-class artifact missing: " + WEDGE_PATH)
        self.text = read(WEDGE_PATH)

    def test_leg1_class_and_restart_survival_recorded(self):
        self.assertIn("exec-transport-hung", self.text)
        self.assertIn("98203", self.text)
        self.assertIn("23:03:30", self.text)

    def test_leg2_amendment_present(self):
        self.assertIn("LEG 2", self.text, "no leg-2 amendment block")
        self.assertIn("/tmp/huanxin-auth-broker.log", self.text)
        self.assertIn("18:53:43", self.text, "broker loop onset missing")
        self.assertIn("capture returned no callback", self.text)
        self.assertIn("user Chrome", self.text)

    def test_leg2_does_not_overrule_leg1_fail_closed(self):
        m = re.search(r"LEG 2.*", self.text, re.S)
        self.assertIsNotNone(m)
        leg2 = m.group(0)
        self.assertIsNotNone(
            re.search(r"correlat", leg2, re.I),
            "leg-2 must mark the broker loop correlated, not causal",
        )

    def test_no_fabricated_cure_claim(self):
        self.assertNotRegex(self.text, r"VERDICT.*\bcured\b", "cured claimed without verification")


class TestCurePackageArtifact(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(CURE_PATH):
            self.skipTest("cure package missing: " + CURE_PATH)
        self.text = read(CURE_PATH)

    def test_user_gated_marker(self):
        self.assertIn("USER-GATED", self.text)

    def test_names_env_and_pod(self):
        self.assertIn("ASI3", self.text)
        self.assertIn("dl-c72bd81a96e33134bbe0ae4a478fbab0", self.text)

    def test_leg2_user_chrome_login_step(self):
        self.assertIn("LEG 2", self.text, "no leg-2 amendment block")
        m = re.search(r"LEG 2.*", self.text, re.S)
        leg2 = m.group(0)
        self.assertRegex(leg2, r"Chrome", "leg-2 cure must name the user-Chrome login path")

    def test_verification_bar_is_positive_exec(self):
        self.assertIn("lastCommandCompletedAt", self.text)
        self.assertRegex(self.text, r"pendingRequestCount.*<=\s*3")
        self.assertIn("2 consecutive", self.text)

    def test_banned_actions_recorded(self):
        self.assertIn("/stop", self.text, "POST /stop must be named as forbidden")
        self.assertIn("_asi3_auth_probe.sh", self.text, "banned Safari SSO probe must be named")


if __name__ == "__main__":
    unittest.main()
