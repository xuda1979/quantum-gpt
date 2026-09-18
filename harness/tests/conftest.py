"""Test-isolation seam — imported by pytest BEFORE any test module.

Incident 2026-09-17: a test file imported qgh without the QGH_STATE_DIR seam;
module caching kept every later file bound to the LIVE state dir, and
state-resetting setUps erased ~50 live cards. This conftest guarantees the
seam exists before qgh is first imported in any pytest process, so no harness
test can ever read or mutate the live harness state.

Set QGH_STATE_DIR explicitly to override (not used by CI or tests).
"""

import os
import tempfile

# The live state dir — NEVER trusted as a test state dir.
_live_state = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state")
_inherited = os.environ.get("QGH_STATE_DIR")
if not _inherited or os.path.realpath(_inherited) == os.path.realpath(_live_state):
    os.environ["QGH_STATE_DIR"] = tempfile.mkdtemp(prefix="qgh-pytest-state-")
