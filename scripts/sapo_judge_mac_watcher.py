#!/usr/bin/env python3
"""SAPO judge Mac watcher (2026-08-27, JUDGE BRIDGE lane).

The Mac CAN call the dp4 subscription (the `claude -p huanxin -m dp4` proxy on
127.0.0.1:55648); the training box cannot (its DNS maps aihuanxin.cn to an
internal gateway without our route). This watcher closes the loop for the
box-side bridge (scripts/sapo_judge_bridge.py): every ~POLL seconds it lists
{BOX_QUEUE}/req_*.json via the box daemon, and for each request without a
response it fetches the request, POSTs it to the Mac dp4 proxy (Anthropic
/v1/messages, no env proxy), and stages {BOX_QUEUE}/resp_<id>.json back.

Env: SAPO_DAEMON (default http://127.0.0.1:19005),
     SAPO_DP4_PROXY (default http://127.0.0.1:55648),
     SAPO_BOX_QUEUE (box-side queue dir),
     SAPO_LOG, SAPO_POLL (seconds, default 3).
"""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.request

DAEMON = os.environ.get("SAPO_DAEMON", "http://127.0.0.1:19005")
DP4_PROXY = os.environ.get("SAPO_DP4_PROXY", "http://127.0.0.1:55648")
BOX_QUEUE = os.environ.get("SAPO_BOX_QUEUE", "")
LOG = os.environ.get("SAPO_LOG", "/tmp/sapo_judge_mac_watcher.log")
POLL = float(os.environ.get("SAPO_POLL", "3"))
ORPHAN_MINUTES = 10


def log(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%SZ', time.gmtime())} {msg}\n"
    try:
        with open(LOG, "a", encoding="utf-8") as handle:
            handle.write(line)
    except OSError:
        pass


def daemon_exec(script: str) -> str:
    """Run a bash snippet on the box via the daemon; return stdout (or '')."""
    b64 = base64.b64encode(script.encode("utf-8")).decode("ascii")
    payload = json.dumps({"command": f"echo {b64} | base64 -d | bash"})
    req = urllib.request.Request(
        DAEMON.rstrip("/") + "/exec",
        data=payload.encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    timeout_s = int(os.environ.get("SAPO_DAEMON_EXEC_TIMEOUT", "65"))
    with opener.open(req, timeout=timeout_s) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return str(data.get("output") or "")


def list_requests() -> list[str]:
    """List pending requests through the console transport.

    2026-08-27 (live bug, class-extinction): the console WRAPS long lines —
    the 112-char ls path wrapped mid-filename ('req_...af.\\njson') and the
    '.endswith(.json)' filter dropped EVERY request, silently blinding the
    watcher (both step-1 and step-2 judge calls timed out judge-absent). Same
    fix as fetch: base64 the ls output box-side, strip whitespace, decode.
    """
    out = daemon_exec(f"ls '{BOX_QUEUE}'/req_*.json 2>/dev/null | base64 -w0")
    compact = "".join(out.split())
    if not compact:
        return []
    try:
        raw = base64.b64decode(compact.encode("ascii")).decode("utf-8")
    except Exception:
        return []
    return [line.strip() for line in raw.splitlines() if line.strip().endswith(".json")]


def fetch(path: str) -> str:
    """Fetch a queue file through the console transport.

    The huanxin browser-console output capture WRAPS long lines mid-word
    (observed: a JSON line split at ~107 chars), so raw `cat` corrupts any
    single-line JSON. Base64 round-trip instead: base64 output may be wrapped
    arbitrarily, but its alphabet has no whitespace, so stripping all
    whitespace before decoding recovers the exact bytes.
    """
    try:
        out = daemon_exec(f"base64 -w0 '{path}' 2>/dev/null")
        compact = "".join(out.split())
        if not compact:
            return ""
        return base64.b64decode(compact.encode("ascii")).decode("utf-8")
    except Exception:
        # 2026-08-29: a corrupted/wrapped transport capture must fail THIS
        # request (empty body -> skipped), not abort the whole tick (a raise
        # here skipped every other queued request that cycle).
        return ""


def stage(path: str, data: str) -> None:
    b64 = base64.b64encode(data.encode("utf-8")).decode("ascii")
    daemon_exec(f"echo {b64} | base64 -d > '{path}'")


def call_dp4(body_text: str, timeout_s: int = 250) -> str:
    """Forward the trainer's Anthropic payload to the judge. Two transports:
    (a) SAPO_DP4_CLI=1 — shell out to the user's `claude -p huanxin -m dp4`
    wrapper (it carries its own live route + proxy; 2026-08-30: this WORKS
    while the static proxy routes had been rotated platform-side);
    (b) default — HTTP to the Mac dp4 proxy."""
    try:
        req_body = json.loads(body_text)
    except Exception:
        return json.dumps(
            {"error": {"message": "watcher: invalid request JSON", "type": "watcher_error"}}
        )
    if os.environ.get("SAPO_DP4_CLI") == "1":
        import subprocess

        prompt = "\n\n".join(str(m.get("content", "")) for m in req_body.get("messages", []))
        try:
            out = subprocess.run(
                ["claude", "-p", "huanxin", "-m", "dp4"],
                input=prompt.encode(),
                capture_output=True,
                timeout=timeout_s,
            )
            text = out.stdout.decode("utf-8", "replace")
            if text.strip():
                return json.dumps({"content": [{"type": "text", "text": text}]})
            return json.dumps(
                {"error": {"message": repr(out.stderr.decode()[:200]), "type": "cli_error"}}
            )
        except Exception as exc:
            return json.dumps({"error": {"message": repr(exc)[:200], "type": "cli_error"}})
    req = urllib.request.Request(
        DP4_PROXY.rstrip("/") + "/v1/messages",
        data=json.dumps(req_body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": "bridge",
            "anthropic-version": "2023-06-01",
        },
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=timeout_s) as resp:
            return resp.read().decode("utf-8")
    except Exception as exc:
        return json.dumps({"error": {"message": repr(exc)[:200], "type": "watcher_error"}})


def has_resp(req_path: str) -> bool:
    resp_path = resp_for(req_path)
    return daemon_exec(f"[ -f '{resp_path}' ] && echo yes").strip() == "yes"


def resp_for(req_path: str) -> str:
    rid = req_path.rsplit("/", 1)[-1][len("req_") : -len(".json")]
    return f"{BOX_QUEUE.rstrip('/')}/resp_{rid}.json"


def cleanup_orphans() -> None:
    script = (
        f"cd '{BOX_QUEUE}' 2>/dev/null || exit 0\n"
        "for r in resp_*.json; do\n"
        '  [ -e "$r" ] || continue\n'
        "  id=${r#resp_}; id=${id%.json}\n"
        '  [ -e "req_$id.json" ] || find . -name "$r" -mmin '
        f"+{ORPHAN_MINUTES} -delete\n"
        "done"
    )
    daemon_exec(script)


def tick(immediate: bool = False) -> int:
    """One poll cycle. Returns the number of requests processed.

    2026-08-29 (live bug, judge-latency class): a dp4 response staged AFTER the
    box bridge's judge-timeout (290s) is inert — the trainer already recorded
    judge-absent. Under box load, list+fetch latency could exceed that budget.
    FIX: fast-path re-check — after every failed/plain tick, retry the queue
    listing once more within the same cycle (the "immediate" second look), and
    when called with immediate=True the tick SKIPS the orphan cleanup to spend
    the transport budget purely on request pickup."""
    processed = 0
    req_paths = list_requests()
    if immediate and not req_paths:
        # second look inside the same cycle: a request may have landed between
        # the first listing and now (the judge call lands mid-generation and
        # every second counts against the bridge's 290s deadline)
        req_paths = list_requests()
    for req_path in req_paths:
        if has_resp(req_path):
            continue
        body = fetch(req_path)
        if not body.strip():
            continue
        log("judging {}".format(req_path.rsplit("/", 1)[-1]))
        resp = call_dp4(body)
        stage(resp_for(req_path), resp)
        log("staged {}".format(resp_for(req_path).rsplit("/", 1)[-1]))
        processed += 1
    if not immediate:
        cleanup_orphans()
    return processed


def startup_selfcheck() -> None:
    """2026-08-28 (live bug, judge-chain class): a watcher re-armed with a STALE
    proxy port (recorded in a previous session's notes) served no scores until
    someone noticed NA judge dims several steps later. The watcher now proves
    its full chain AT STARTUP: (1) dp4 proxy answers /v1/messages with a 1-token
    reply, (2) the box queue dir is listable through the console transport.
    Failures are LOUD in the log (the watcher still runs — the queue may gain
    requests later after an operator fixes the port) but every start carries
    evidence instead of silent blindness."""
    try:
        probe = json.dumps(
            {
                "model": "dp4",
                "max_tokens": 8,
                "messages": [{"role": "user", "content": "Reply: PROXY_OK"}],
            }
        )
        reply = call_dp4(probe, timeout_s=30)
        # Any well-formed Anthropic-shaped reply with content proves the chain;
        # the exact echo text is up to the model (free-form models paraphrase).
        ok = False
        try:
            body = json.loads(reply)
            ok = any(
                isinstance(b, dict) and b.get("type") == "text" and b.get("text")
                for b in body.get("content") or []
            )
        except Exception:
            ok = False
        log(f"selfcheck proxy: {'OK' if ok else 'FAIL body=' + reply[:120]}")
    except Exception as exc:  # noqa: BLE001
        log(f"selfcheck proxy: ERROR {exc!r}")
    try:
        out = daemon_exec(f"ls '{BOX_QUEUE}' 2>/dev/null | wc -l")
        log(f"selfcheck queue: {out.strip() or '?'} entries visible ({BOX_QUEUE})")
        # 2026-08-29 (env-drift class): prove the queue dir belongs to the NEWEST
        # run dir; a watcher re-armed against a dead run's queue serves nobody.
        newest = daemon_exec(
            "ls -td /root/work/software/quantum-gpt/outputs/sapo-27b-ai-* 2>/dev/null | head -1"
        ).strip()
        if newest and BOX_QUEUE.startswith(newest):
            log(f"selfcheck queue-run: OK ({newest})")
        elif newest:
            log(f"selfcheck queue-run: MISMATCH newest={newest}")
        else:
            log("selfcheck queue-run: newest undetermined")
    except Exception as exc:  # noqa: BLE001
        log(f"selfcheck queue: ERROR {exc!r}")


def main() -> int:
    if not BOX_QUEUE:
        print("SAPO_BOX_QUEUE is required", flush=True)
        return 2
    log(f"watcher start (daemon={DAEMON} proxy={DP4_PROXY} queue={BOX_QUEUE})")
    startup_selfcheck()
    while True:
        try:
            # 2026-08-29 (judge-latency fix): cycle = fast tick (cleanup skipped,
            # second queue look if empty) + normal tick. Doubles pickup chances
            # per sleep and trims the response latency vs the bridge's 290s.
            if tick(immediate=True) == 0:
                tick()
        except Exception as exc:  # daemon blips must never kill the watcher
            log(f"tick error: {exc!r}")
        time.sleep(POLL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
