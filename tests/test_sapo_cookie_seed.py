"""TDD tests for scripts/sapo_cookie_seed.py — the plaintext aihuanxin cookie bridge.

B-044 (2026-09-10): the seed wrote FIXED Chrome-epoch timestamp constants
(creation_utc = 13390000000000000 -> 2025-04-24, expires_utc = 13399000000000000
-> 2025-08-07). Both are in the PAST, so Chrome expired every seeded cookie at
load: the daemon profiles never received KEYCLOAK_IDENTITY and the transport
could not recover auth (ASI1 :20646 and ASI3 :20653 stuck booting while ASI2
:19004 happened to still hold a live session of its own).

The constants also carried a wrong comment ("~Jan 2027"). The fix derives both
timestamps from the clock at write time, so the seed can never silently go
stale again.
"""

from __future__ import annotations

import datetime
import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO / "scripts" / "sapo_cookie_seed.py"

# Chrome's epoch is 1601-01-01 UTC; creation_utc/expires_utc are microseconds
# since then.
CHROME_EPOCH = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)


def load_module():
    spec = importlib.util.spec_from_file_location("sapo_cookie_seed", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sapo_cookie_seed"] = module
    spec.loader.exec_module(module)
    return module


def to_datetime(chrome_us: int) -> datetime.datetime:
    return CHROME_EPOCH + datetime.timedelta(microseconds=chrome_us)


def test_module_exposes_clock_derived_timestamps():
    """The seed must derive its timestamps from the clock, not from constants."""
    mod = load_module()
    assert hasattr(mod, "chrome_time_now"), "chrome_time_now() must exist"
    assert hasattr(mod, "chrome_time_expiry"), "chrome_time_expiry() must exist"


def test_creation_time_is_now():
    """creation_utc must be ~now; a stale constant makes Chrome drop the cookie."""
    mod = load_module()
    created = to_datetime(mod.chrome_time_now())
    now = datetime.datetime.now(datetime.timezone.utc)
    delta = abs((now - created).total_seconds())
    assert delta < 120, f"creation_utc maps to {created}, {delta:.0f}s away from now"


def test_expiry_is_in_the_future():
    """expires_utc must be in the FUTURE — the original constant was 13 months past."""
    mod = load_module()
    expires = to_datetime(mod.chrome_time_expiry())
    now = datetime.datetime.now(datetime.timezone.utc)
    assert expires > now, f"expires_utc maps to {expires}, which is in the past"
    # Long-lived but not absurd: the bridge should survive months of daemon churn.
    assert expires > now + datetime.timedelta(days=300), (
        f"expires_utc {expires} is less than 300 days ahead; too short-lived for a "
        "perpetual keepalive"
    )
    assert expires < now + datetime.timedelta(days=365 * 5), (
        f"expires_utc {expires} is more than 5 years ahead; implausible"
    )


def test_expiry_after_creation():
    mod = load_module()
    assert mod.chrome_time_expiry() > mod.chrome_time_now()


# --------------------------------------------------------------------------
# B-045: the seed bridged EVERY aihuanxin cookie, including the site's own
# per-ingress session cookies (68b329_0 = 3869 bytes, 68b329_1 = 507). Those are
# stale by the time they are copied, and together they push the request's Cookie
# header to 6212 bytes — past the ingress' ~6210-byte ceiling — so the ingress
# answered HTTP 400 for EVERY navigation. The transport then could not open a
# shell even though auth was fine (the same 6212-byte header also 400s the
# user's own Chrome, which is why aihuanxin.cn was unreachable there).
#
# The bridge's job is to carry the LOGIN (SSO), not the site's session state:
# the SPA mints its own session cookies on first load.
# --------------------------------------------------------------------------

LEGACY_INGRESS = {"68b329_0": "A" * 3869, "68b329_1": "B" * 507}


def test_only_auth_cookies_are_seeded():
    """Session cookies minted by the site must not be bridged."""
    mod = load_module()
    src = dict(LEGACY_INGRESS)
    src.update(
        {
            "KEYCLOAK_IDENTITY": "c" * 646,
            "KEYCLOAK_IDENTITY_LEGACY": "d" * 646,
            "KEYCLOAK_SESSION": "e" * 97,
            "KEYCLOAK_REMEMBER_ME": "username:xuda2025",
            "AUTH_SESSION_ID": "f" * 81,
            "AUTH_SESSION_ID_LEGACY": "g" * 81,
        }
    )
    kept = mod.select_seedable_cookies(src)
    assert not any(name.startswith("68b329") for name in kept), (
        "site session cookies (68b329_*) must be dropped — they are stale and "
        "overflow the ingress header limit"
    )
    for name in ("KEYCLOAK_IDENTITY", "KEYCLOAK_SESSION"):
        assert name in kept, f"{name} carries the SSO session and must be kept"
    # B-076: AUTH_SESSION_ID is per-flow state, not an SSO credential. A stale
    # one makes keycloak 404 the next auth URL and the terminal never mounts.
    assert "AUTH_SESSION_ID" not in kept, "per-flow auth-session cookies must not be bridged"


def test_seeded_header_stays_under_ingress_budget():
    """The whole point: never emit a Cookie header the ingress will 400."""
    mod = load_module()
    src = dict(LEGACY_INGRESS)
    src.update({f"KEYCLOAK_{i}": "x" * 646 for i in range(3)})
    kept = mod.select_seedable_cookies(src)
    header = "; ".join(f"{k}={v}" for k, v in kept.items())
    assert len(header) <= mod.COOKIE_HEADER_BUDGET, (
        f"seeded header is {len(header)} bytes, over the {mod.COOKIE_HEADER_BUDGET}"
        " budget — the ingress answers 400 above ~6210 bytes"
    )


def test_real_observed_set_is_under_limit():
    """Regression pin on the exact production set that caused the outage."""
    mod = load_module()
    observed = dict(LEGACY_INGRESS)
    observed.update(
        {
            "AUTH_SESSION_ID": "a" * 81,
            "AUTH_SESSION_ID_LEGACY": "b" * 81,
            "KEYCLOAK_IDENTITY": "c" * 646,
            "KEYCLOAK_IDENTITY_LEGACY": "d" * 646,
            "KEYCLOAK_REMEMBER_ME": "username:xuda2025",
            "KEYCLOAK_SESSION": "e" * 97,
            "KEYCLOAK_SESSION_LEGACY": "f" * 97,
        }
    )
    raw = "; ".join(f"{k}={v}" for k, v in observed.items())
    assert len(raw) > 6210, "fixture should reproduce the original over-limit header"
    kept = mod.select_seedable_cookies(observed)
    fixed = "; ".join(f"{k}={v}" for k, v in kept.items())
    assert len(fixed) <= mod.COOKIE_HEADER_BUDGET


def test_budget_drops_largest_when_still_over():
    """Fail-safe: if auth cookies alone would overflow, drop largest first."""
    mod = load_module()
    src = {"KEYCLOAK_IDENTITY": "x" * 9000, "KEYCLOAK_SESSION": "y" * 50}
    kept = mod.select_seedable_cookies(src)
    header = "; ".join(f"{k}={v}" for k, v in kept.items())
    assert len(header) <= mod.COOKIE_HEADER_BUDGET
    assert "KEYCLOAK_SESSION" in kept, "the small cookie should survive"


# --------------------------------------------------------------------------
# B-046: the seed wrote to the base profile AND to every live
# /var/folders/.../huanxin-profile-quantum-rnd-ASI*/Default/Cookies. Writing to a
# RUNNING daemon's profile deletes the session cookies its browser is using, and
# a reload then drops that daemon out of its authenticated session. Observed
# 2026-09-10: seeding for ASI1/ASI3 knocked the healthy ASI2 (:19004) into
# login_required. The writes are also pointless: ensureProfileDir() deletes the
# temp dir and re-copies the BASE profile on every launch, so the base profile is
# the only thing that needs seeding.
# --------------------------------------------------------------------------


def test_seed_targets_only_the_base_profile(tmp_path):
    """Only the base profile is a seed target — never a live daemon's profile."""
    mod = load_module()
    live_asi2 = "/var/folders/py/xxx/T/huanxin-profile-quantum-rnd-ASI2/Default/Cookies"
    targets = mod.seed_targets(base_profile=str(tmp_path / "profile"))
    assert targets == [str(tmp_path / "profile" / "Default" / "Cookies")], (
        f"expected only the base profile target, got {targets}"
    )
    assert live_asi2 not in targets


def test_seed_targets_is_base_only_by_construction():
    """The glob over live daemon profiles must be gone from the CODE.

    Scans code only — the removed glob is named in the B-046 explanatory
    comment, and a whole-file grep would match that prose (the comment-line trap
    this repo logged as B-038).
    """
    import ast

    tree = ast.parse(MODULE_PATH.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "glob":
                raise AssertionError(
                    f"line {node.lineno}: the seed must not glob live daemon profiles — "
                    "writing to a running daemon's profile destroys its session"
                )
    assert not any(
        isinstance(node, ast.Import) and any(a.name == "glob" for a in node.names)
        for node in ast.walk(tree)
    ), "the glob import is unused now that only the base profile is seeded"


def test_no_stale_hardcoded_constants_remain():
    """Guard against the exact regression: now/exp must not be frozen literals.

    Scans CODE only. The stale values are deliberately named in the module's
    explanatory comment, and a whole-file grep would match that prose instead of
    the defect (the same comment-line class this repo logged as B-038).
    """
    code_lines = []
    for line in MODULE_PATH.read_text().splitlines():
        stripped = line.split("#", 1)[0]
        if stripped.strip():
            code_lines.append(stripped)
    code = "\n".join(code_lines)
    for bad in ("13390000000000000", "13399000000000000"):
        assert bad not in code, (
            f"stale Chrome-epoch constant {bad} is still present in seed CODE — it "
            "encodes a date in the past and silently expires every seeded cookie"
        )
