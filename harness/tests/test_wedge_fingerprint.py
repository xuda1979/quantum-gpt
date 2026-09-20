"""C-9062: stale-code fingerprint probe (pid-start vs daemon-file mtime).

RED first (2026-09-17): the wedge cards (C-9018/C-9050/C-9036) measure through
an /exec wedge whose premise is "every daemon predates the cure mtime = stale
code", but no instrument compares process start to file mtime -- the check was
done by eye. This module makes the comparison mechanical and fail-closed:

  verdict(daemon) = POST-CURE  iff process_start > file_mtime (STRICT)
                  = STALE-CODE iff process_start <= file_mtime
                  = UNKNOWN    when pid/start/file-mtime is missing or
                               non-numeric (never guessed)

The boundary is strict fail-closed: start == mtime cannot prove the loader saw
the new bytes, so it is STALE, never post-cure. The fleet rollup is cured only
when every row is post-cure; any stale row makes the fleet stale; any unknown
row (and no stale row) makes the fleet unknown.

These tests bind ONLY to the fixture table below (hermetic: no ps, no live
daemons, no filesystem).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wedge_fingerprint import POST_CURE, STALE_CODE, UNKNOWN, fingerprint_fleet

FILE_MTIME = 2000.0

# Fixture table: (name, pid, start_epoch) -> expected per-daemon verdict
FIXTURES = [
    # started BEFORE the cure mtime: running old code
    dict(name="stale-daemon", pid=49946, start_epoch=1000.0, expected=STALE_CODE),
    # started strictly AFTER the cure mtime: loaded the cured file
    dict(name="fresh-daemon", pid=50429, start_epoch=3000.0, expected=POST_CURE),
    # boundary start == mtime: cannot prove the new bytes were loaded -> stale
    dict(name="boundary-daemon", pid=1, start_epoch=2000.0, expected=STALE_CODE),
    # unmeasured pid/start (ps found nothing): UNKNOWN, never guessed
    dict(name="unmeasured-daemon", pid=None, start_epoch=None, expected=UNKNOWN),
    # garbage numeric type: UNKNOWN, never coerced
    dict(name="garbage-daemon", pid="50429", start_epoch="later", expected=UNKNOWN),
]


class TestWedgeFingerprint(unittest.TestCase):
    def test_fixture_table(self):
        rows = [dict(name=f["name"], pid=f["pid"], start_epoch=f["start_epoch"]) for f in FIXTURES]
        out = fingerprint_fleet(rows, file_mtime=FILE_MTIME)
        by_name = dict((r["name"], r) for r in out["table"])
        for f in FIXTURES:
            self.assertEqual(
                by_name[f["name"]]["verdict"],
                f["expected"],
                msg=f["name"] + ": " + by_name[f["name"]].get("reason", ""),
            )

    def test_after_cure_requirement_is_strict(self):
        # The after-cure requirement is process-start > file-mtime on the
        # serving daemon: one tick EQUAL must not read as cured.
        out = fingerprint_fleet(
            [dict(name="d", pid=1, start_epoch=FILE_MTIME)], file_mtime=FILE_MTIME
        )
        self.assertEqual(out["table"][0]["verdict"], STALE_CODE)

    def test_fleet_cured_only_when_all_post_cure(self):
        rows = [
            dict(name="a", pid=1, start_epoch=FILE_MTIME + 10),
            dict(name="b", pid=2, start_epoch=FILE_MTIME + 20),
        ]
        self.assertEqual(
            fingerprint_fleet(rows, file_mtime=FILE_MTIME)["fleet"], "cured-fingerprint"
        )

    def test_fleet_stale_when_any_row_stale(self):
        rows = [
            dict(name="a", pid=1, start_epoch=FILE_MTIME + 10),
            dict(name="b", pid=2, start_epoch=FILE_MTIME - 10),
        ]
        out = fingerprint_fleet(rows, file_mtime=FILE_MTIME)
        self.assertEqual(out["fleet"], STALE_CODE)
        self.assertEqual(out["stale_names"], ["b"])

    def test_fleet_unknown_when_no_row_stale_but_any_unknown(self):
        rows = [
            dict(name="a", pid=1, start_epoch=FILE_MTIME + 10),
            dict(name="b", pid=None, start_epoch=None),
        ]
        self.assertEqual(fingerprint_fleet(rows, file_mtime=FILE_MTIME)["fleet"], UNKNOWN)

    def test_missing_file_mtime_fails_closed(self):
        rows = [dict(name="a", pid=1, start_epoch=FILE_MTIME + 10)]
        out = fingerprint_fleet(rows, file_mtime=None)
        self.assertEqual(out["table"][0]["verdict"], UNKNOWN)
        self.assertEqual(out["fleet"], UNKNOWN)

    def test_empty_fleet_is_unknown_not_cured(self):
        self.assertEqual(fingerprint_fleet([], file_mtime=FILE_MTIME)["fleet"], UNKNOWN)


if __name__ == "__main__":
    unittest.main()
