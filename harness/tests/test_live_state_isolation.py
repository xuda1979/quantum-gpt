"""CANARY: no harness test may ever bind qgh.STATE to the LIVE state dir.

Incident 2026-09-17: test_dep_graph_rebaseline.py imported qgh without the
isolation seam; module caching kept later files bound to the live dir, and
state-resetting setUps erased ~50 live cards. This canary pins the fix."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_qgh_state_is_not_the_live_dir():
    assert "QGH_STATE_DIR" in os.environ, "isolation seam must be set before importing qgh"
    import qgh

    live = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(qgh.__file__))), "harness", "state"
    )
    assert os.path.abspath(qgh.STATE) != os.path.abspath(live), (
        f"qgh.STATE ({qgh.STATE}) must never resolve to the live dir ({live})"
    )
