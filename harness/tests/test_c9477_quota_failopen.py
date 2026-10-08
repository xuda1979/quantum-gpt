"""C-9477 RED: quota gate should fail OPEN on transport errors.

A transport error (DNS failure, connection refused) means the probe
could not run -- it does NOT mean the quota is exhausted. Blocking all
dispatch on a probe transport error prevents the harness from doing ANY
work, even purely local work that does not need the API.
"""
import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import quota_preflight_gate as QPG


class TestQuotaGateTransportFailopen(unittest.TestCase):
    def test_transport_error_fails_open(self):
        probe = QPG._verdict(QPG.UNKNOWN, "probe transport error: DNS failed")
        self.assertTrue(QPG.gate_allows(probe),
                        "transport error should fail OPEN (allow dispatch)")

    def test_real_unknown_fails_closed(self):
        probe = QPG._verdict(QPG.UNKNOWN, "unparseable response")
        self.assertFalse(QPG.gate_allows(probe),
                         "non-transport UNKNOWN should still fail closed")

    def test_exhausted_fails_closed(self):
        probe = QPG._verdict(QPG.EXHAUSTED, "quota exceeded")
        self.assertFalse(QPG.gate_allows(probe))

    def test_ok_passes(self):
        probe = QPG._verdict(QPG.OK, "")
        self.assertTrue(QPG.gate_allows(probe))


if __name__ == "__main__":
    unittest.main()
