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

if not os.environ.get("QGH_STATE_DIR"):
    os.environ["QGH_STATE_DIR"] = tempfile.mkdtemp(prefix="qgh-pytest-state-")
