#!/usr/bin/env python3
"""Plaintext cookie seed (2026-09-03, PROVEN): copy the live aihuanxin SSO
session from the user's logged-in Chrome into every automation profile.

Why plaintext: Chrome 127+ app-bound-encrypts httpOnly cookie blobs per
profile; copying the encrypted blob fails on the daemon side (silently
dropped). Decrypting with the Keychain 'Chrome Safe Storage' key and writing
the plaintext into the 'value' column works on every profile (verified live:
ASI3 went ready on the first boot after this seed).

Plaintext layout of a Chrome v10 blob: b'v10' + AES-128-CBC(PBKDF2(key,
'saltysalt', 1003), IV=' '*16, plaintext = sha256(host)[32] + value + PKCS7).
"""

from __future__ import annotations

import datetime
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

from Crypto.Cipher import AES

COLS = [
    "creation_utc",
    "host_key",
    "top_frame_site_key",
    "name",
    "value",
    "encrypted_value",
    "path",
    "expires_utc",
    "is_secure",
    "is_httponly",
    "last_access_utc",
    "has_expires",
    "is_persistent",
    "priority",
    "samesite",
    "source_scheme",
    "source_port",
    "last_update_utc",
    "source_type",
    "has_cross_site_ancestor",
]

# Chrome's epoch is 1601-01-01 UTC and creation_utc/expires_utc are microseconds
# since then.
#
# B-044 (2026-09-10): these were FROZEN CONSTANTS (13390000000000000 / 13399000000000000)
# that decoded to 2025-04-24 and 2025-08-07 — both in the PAST — so Chrome expired
# every seeded cookie at load. The daemon profiles never received KEYCLOAK_IDENTITY
# and ASI1/ASI3 could not recover auth while the constants silently aged. Derive both
# from the clock instead, so the seed can never go stale again.
CHROME_EPOCH = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
EXPIRY_DAYS = 400  # long enough to survive churn; refreshed on every seed run

# B-045 (2026-09-10): the seed used to bridge EVERY aihuanxin cookie, including
# the site's own ingress session cookies (observed: 68b329_0 = 3869 bytes,
# 68b329_1 = 507). Those are stale by the time we copy them, and together they
# drove the request Cookie header to 6212 bytes — past the ingress' ~6210-byte
# ceiling — so the ingress answered HTTP 400 for EVERY navigation. The daemon
# could not open a shell even though the login itself was fine, and the user's
# own Chrome (same 6212-byte header) could not load aihuanxin.cn at all.
#
# The bridge's job is to carry the LOGIN, not the site's session state: the SPA
# mints its own ingress/session cookies on first load. So seed only the SSO
# cookies, and fail-safe on a hard header budget.
AUTH_COOKIE_PREFIXES = ("KEYCLOAK_", "AUTH_SESSION_ID")
# Measured on the live ingress: 6207 bytes -> 200, 6217 bytes -> 400.
COOKIE_HEADER_BUDGET = 6000


def _header_len(cookies: dict[str, str]) -> int:
    return len("; ".join(f"{name}={value}" for name, value in cookies.items()))


def seed_targets(base_profile: str | None = None) -> list[str]:
    """Cookie DBs to seed: the BASE profile only.

    B-046 (2026-09-10): this used to also glob every live
    /var/folders/.../huanxin-profile-quantum-rnd-ASI*/Default/Cookies. Writing to a
    RUNNING daemon's profile deletes the cookies its browser is using, and the
    next reload drops that daemon out of its session — seeding for ASI1/ASI3
    knocked the healthy ASI2 into login_required. It is also redundant:
    ensureProfileDir() deletes the temp dir and re-copies the base profile on
    every launch, so seeding the base covers every daemon at boot.
    """
    root = base_profile or "/Users/daxu/software/quantum-gpt/browser-automation/profile"
    return [str(Path(root) / "Default" / "Cookies")]


def select_seedable_cookies(vals: dict[str, str]) -> dict[str, str]:
    """Keep only the login (SSO) cookies, within the ingress' header budget.

    Session cookies the site mints for itself are dropped: they are stale and
    oversized, and the SPA recreates them on first load. If the auth cookies
    alone would still overflow the budget, drop the largest first — never emit a
    header the ingress will reject with 400.
    """
    kept = {name: value for name, value in vals.items() if name.startswith(AUTH_COOKIE_PREFIXES)}
    dropped: list[str] = []
    for name, value in sorted(kept.items(), key=lambda kv: -len(kv[1])):
        if _header_len(kept) <= COOKIE_HEADER_BUDGET:
            break
        kept.pop(name)
        dropped.append(f"{name}({len(value)}B)")
    if dropped:
        print(
            f"cookie seed: dropped {len(dropped)} oversized cookie(s) to stay under the "
            f"{COOKIE_HEADER_BUDGET}B header budget: {', '.join(dropped)}",
            file=sys.stderr,
        )
    return kept


def _chrome_epoch_us(moment: datetime.datetime) -> int:
    return int((moment - CHROME_EPOCH).total_seconds() * 1_000_000)


def chrome_time_now() -> int:
    """Microseconds since the Chrome epoch for the current instant."""
    return _chrome_epoch_us(datetime.datetime.now(datetime.timezone.utc))


def chrome_time_expiry() -> int:
    """Microseconds since the Chrome epoch, EXPIRY_DAYS in the future."""
    return _chrome_epoch_us(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=EXPIRY_DAYS)
    )


def storage_key() -> bytes:
    out = subprocess.run(
        ["security", "find-generic-password", "-w", "-s", "Chrome Safe Storage"],
        capture_output=True,
        text=True,
    )
    if out.returncode != 0:
        sys.exit("keychain denied — cannot decrypt user cookies")
    return out.stdout.strip().encode()


def decrypt(blob: bytes, key: bytes) -> str:
    d = hashlib.pbkdf2_hmac("sha1", key, b"saltysalt", 1003, dklen=16)
    p = AES.new(d, AES.MODE_CBC, IV=b" " * 16).decrypt(blob[3:])
    pad = p[-1]
    if 1 <= pad <= 16:
        p = p[:-pad]
    return p[32:].decode("utf-8", "replace")  # skip 32-byte host hash


def main() -> int:
    key = storage_key()
    src = Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies"
    tmp = Path(tempfile.gettempdir()) / "ck_seed_copy.sqlite"
    shutil.copy2(src, tmp)
    con = sqlite3.connect(tmp)
    vals = {}
    for name, blob in con.execute(
        "SELECT name, encrypted_value FROM cookies WHERE host_key LIKE '%aihuanxin%'"
    ):
        try:
            vals[name] = decrypt(bytes(blob), key)
        except Exception as exc:
            print(f"decrypt fail {name}: {exc}", file=sys.stderr)
    con.close()
    if not vals:
        sys.exit("no decryptable aihuanxin cookies in user Chrome — LOGIN NEEDED")
    vals = select_seedable_cookies(vals)
    if not vals:
        sys.exit("no seedable auth cookies within the header budget — LOGIN NEEDED")
    now = chrome_time_now()
    exp = chrome_time_expiry()
    targets = seed_targets()
    seeded = 0
    for db in targets:
        con = sqlite3.connect(db)
        con.execute("DELETE FROM cookies WHERE host_key LIKE '%aihuanxin%'")
        for name, val in vals.items():
            con.execute(
                f"INSERT OR REPLACE INTO cookies ({','.join(COLS)}) "
                f"VALUES ({','.join('?' * len(COLS))})",
                [
                    now,
                    "aihuanxin.cn",
                    "",
                    name,
                    val,
                    b"",
                    "/",
                    exp,
                    1,
                    1,
                    now,
                    1,
                    1,
                    1,
                    0,
                    2,
                    443,
                    now,
                    1,
                    0,
                ],
            )
        con.commit()
        con.close()
        seeded += 1
    print(f"cookie seed: {len(vals)} cookies -> {seeded} profiles")
    Path("/tmp/huanxin_cookie_plaintext.json").write_text(json.dumps(vals))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
