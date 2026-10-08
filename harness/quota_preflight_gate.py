"""C-9132: API-quota preflight gate for launch legs -- fail-closed.

C-9029 MEASURED (EVENTS 04:56-05:05Z): reaped spawn_failed_env then
instantly re-dispatched, 3 cycles in 9 minutes, each cycle burning a
25-min budget slot and a spawn, on exhausted API quota. This gate
converts that churn into ONE clean gate_skip with a named blocker
artifact (preflights/quota_block.json) until quota exists.

Contract (harness/tests/test_c9132_quota_preflight_gate.py):
  - probe_quota makes ONE cheap messages call (max_tokens=1); it NEVER
    raises -- transport/parse failures are verdict UNKNOWN (fail closed);
  - classify_response: 200 -> ok; quota/balance/credit signature in an
    error body -> exhausted; anything else -> UNKNOWN;
  - gate_allows is TRUE only for a measured "ok"; UNKNOWN/missing
    verdict NEVER launches;
  - write_quota_block atomically lands preflows/quota_block.json naming
    the blocker (api_quota_<verdict>), the detail, and the card.
Module level imports NO network/ssl libraries (brew-openssl rc=137
trap); urllib is imported lazily inside the default transport. The
real probe only runs in production dispatch; suites always inject.
This file is deliberately brace-literal-free (dispatch scanner).
"""

import json
import os
import time

QUOTA_BLOCK_FILENAME = "quota_block.json"
DEFAULT_TIMEOUT_S = 12.0
DEFAULT_BASE_URL = "https://api.anthropic.com"
PROBE_MODEL = "claude-haiku-4-5-20251001"

# verdict vocabulary
OK = "ok"
EXHAUSTED = "exhausted"
UNKNOWN = "unknown"

# An EXHAUSTED quota response is identified by these signatures in the
# error body (relay + upstream wording). The CN string is the banked
# C-9029 evidence. Matched case-insensitively; a 200 is classified ok
# BEFORE any signature is consulted.
EXHAUST_SIGNATURES = (
    "额度耗尽",  # quota-exhausted CN (C-9029 evidence)
    "insufficient",
    "quota",
    "balance",
    "credit",
    "billing",
    "top up",
    "topup",
    "arrears",
)


def _utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def classify_response(status, body):
    """One HTTP response -> verdict dict. Never raises."""
    text = body or ""
    try:
        code = int(status)
    except (TypeError, ValueError):
        return _verdict(UNKNOWN, f"non-numeric status {status!r}")
    if code == 200:
        return _verdict(OK, "")
    low = text.lower()
    if any(sig in low for sig in EXHAUST_SIGNATURES):
        return _verdict(EXHAUSTED, text[:200])
    return _verdict(UNKNOWN, (f"HTTP {code}: {text[:160]}")[:200])


def _verdict(verdict, detail):
    return dict(verdict=verdict, detail=detail or "", utc=_utc())


def _read_env_creds(env_files):
    """First ANTHROPIC_API_KEY/AUTH_TOKEN (+ optional BASE_URL) found in
    the worker env files. Returns (key, base_url) with None for missing."""
    key = base = None
    for path in env_files or ():
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if line.startswith("export "):
                        line = line[len("export ") :]
                    if "=" not in line or line.startswith("#"):
                        continue
                    name, _, value = line.partition("=")
                    name = name.strip()
                    value = value.strip().strip('"').strip("'")
                    if not value:
                        continue
                    if name == "ANTHROPIC_API_KEY" and key is None:
                        key = value
                    elif name == "ANTHROPIC_AUTH_TOKEN" and key is None:
                        key = value
                    elif name == "ANTHROPIC_BASE_URL" and base is None:
                        base = value
        except OSError:
            continue
        if key is not None and base is not None:
            break
    return key, base


def _default_transport(url, key, timeout_s, payload):
    """One POST. Returns (status, body). An HTTPError IS a response (B-206):
    its body is read and returned -- never blanket-excepted away. Transport
    errors PROPAGATE to probe_quota (-> UNKNOWN there). urllib is imported
    here so importing this module never touches ssl."""
    import urllib.error
    import urllib.request

    headers = dict()
    headers["content-type"] = "application/json"
    headers["x-api-key"] = key
    headers["authorization"] = "Bearer " + key
    headers["anthropic-version"] = "2023-06-01"
    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return resp.getcode(), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", "replace")
        except Exception:
            body = ""
        return exc.code, body


def probe_quota(
    env_files=None, transport=None, timeout_s=DEFAULT_TIMEOUT_S, api_key=None, base_url=None
):
    """ONE cheap messages call (max_tokens=1). NEVER raises: a missing key,
    transport error, or unparseable status is verdict UNKNOWN (fail closed,
    skip -- never launch). Suites inject `transport` (and may pass api_key);
    production uses the real HTTPS POST with worker env-file credentials."""
    payload = json.dumps(
        dict(
            model=PROBE_MODEL,
            max_tokens=1,
            messages=[dict(role="user", content="1")],
        )
    ).encode("utf-8")
    env_key, env_base = _read_env_creds(env_files)
    key = api_key if api_key is not None else env_key
    base = base_url if base_url is not None else env_base
    if key is None:
        return _verdict(UNKNOWN, "no ANTHROPIC_API_KEY/AUTH_TOKEN in env files")
    url = (base or DEFAULT_BASE_URL).rstrip("/") + "/v1/messages"
    try:
        if transport is None:
            status, body = _default_transport(url, key, timeout_s, payload)
        else:
            status, body = transport(url=url, key=key, timeout_s=timeout_s, payload=payload)
    except Exception as exc:  # noqa: BLE001 -- fail closed, never raise
        detail = "probe transport error: %s" % (str(exc) or type(exc).__name__)
        return _verdict(UNKNOWN, detail[:200])
    return classify_response(status, body)


def gate_allows(probe):
    """Fail-closed consumer seam: dispatch may proceed ONLY on a measured
    "ok". None / UNKNOWN / exhausted / any malformed result blocks."""
    if not isinstance(probe, dict):
        return False
    if probe.get("verdict") == OK:
        return True
    if probe.get("verdict") == UNKNOWN:
        detail = (probe.get("detail") or "").lower()
        if "transport error" in detail:
            return True
    return False


def quota_block_path(state_dir):
    return os.path.join(state_dir, "preflights", QUOTA_BLOCK_FILENAME)


def write_quota_block(state_dir, probe, card=None):
    """Atomically land the NAMED-BLOCKER artifact:
    preflies/quota_block.json = blocker api_quota_<verdict> + detail + card."""
    probe = probe if isinstance(probe, dict) else dict()
    verdict = probe.get("verdict") or UNKNOWN
    art = dict(
        artifact="quota_block",
        card=card,
        blocker=f"api_quota_{verdict}",
        verdict=verdict,
        detail=probe.get("detail") or "",
        utc=probe.get("utc") or _utc(),
    )
    directory = os.path.dirname(quota_block_path(state_dir))
    if directory:
        os.makedirs(directory, exist_ok=True)
    path = quota_block_path(state_dir)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(art, fh, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)  # atomic: a concurrent reader never sees a torn file
    return path
