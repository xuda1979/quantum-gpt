"""C-10450 wiring guard: the daemon must recover browser wedges in-process.

The keeper log shows 380 'Protocol error (Target.createTarget): Failed to open
a new tab' events and 6 full-daemon restarts in one 30min window. The fix is:
the daemon imports the wedge detector + browser-relaunch helpers and uses them
in its launcher-page path, so a wedged browser recovers WITHOUT a keeper kick.

This guard is textual (like test_huanxin_heartbeat_dispatch_action.py) and is
paired with the behavioural node suite test_huanxin_browser_wedge_detect.js.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DAEMON = REPO / "browser-automation" / "huanxin_browser_daemon.js"
LAUNCH = REPO / "browser-automation" / "huanxin_browser_launch.js"


def test_launch_module_exports_wedge_helpers() -> None:
    src = LAUNCH.read_text()
    for symbol in (
        "isBrowserWedgedProtocolError",
        "newPageWithBrowserReload",
        "relaunchBrowserOnWedge",
    ):
        assert symbol in src, f"launch.js must export {symbol}"
    assert "module.exports" in src


def test_daemon_imports_and_uses_wedge_recovery() -> None:
    src = DAEMON.read_text()
    for symbol in (
        "isBrowserWedgedProtocolError",
        "newPageWithBrowserReload",
        "relaunchBrowserOnWedge",
    ):
        assert symbol in src, f"daemon.js must import {symbol}"
    # The daemon delegates page acquisition to the shared wedge-recovering
    # helper, which logs the in-process relaunch path it runs.
    launch_src = LAUNCH.read_text()
    assert "relaunching browser in-process" in launch_src, "recovery helper must log its path"
