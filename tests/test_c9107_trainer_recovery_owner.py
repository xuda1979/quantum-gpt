"""C-9107: fail-closed guards for the ASI3 trainer-recovery owner artifacts.

The card disposed the reeval100 stub as dead-with-evidence (never killed: no
live process existed anywhere and no USER-GO was recorded), refreshed the STALE
trainer probe with a real box-side measurement, pulled the C-9099-owed weights
sha256, and unblocked C-9010 via the sanctioned bounced->ready requeue with an
evidence-backed reason. These guards keep every one of those claims honest:
no placeholder model id may be asserted as fact, no kill may be claimed
without a recorded GO, and C-9010's unblock must cite its probe evidence.
"""

import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROBES = os.path.join(ROOT, "harness", "state", "probes")
QUEUE = os.path.join(ROOT, "harness", "state", "QUEUE.json")


def _load(path):
    assert os.path.exists(path), "artifact missing: " + path
    with open(path) as fh:
        return json.load(fh)


def test_stub_disposition_is_dead_with_evidence_never_a_kill():
    d = _load(os.path.join(PROBES, "c9107_stub_disposition.json"))
    assert d.get("card") == "C-9107"
    assert d.get("disposition") == "DEAD_WITH_EVIDENCE", d.get("disposition")
    assert d.get("stop_executed") is False, "no stop may be claimed"
    assert d.get("user_go_recorded") is False, "no USER-GO existed; a kill must stay unexecuted"
    mac = d.get("mac_side", dict())
    assert mac.get("live_process_found") is False
    assert mac.get("someorg_hits") == 0, "SomeOrg claim must stay unreproduced, not asserted"
    box = d.get("box_side", dict())
    assert box.get("live_process_found") is False
    assert box.get("reeval100_dirs_found") == 0
    assert box.get("someorg_hits") == 0
    assert d.get("probe_artifacts"), "disposition must cite its probe artifacts"


def test_trainer_probe_refreshed_with_measured_liveness():
    d = _load(os.path.join(PROBES, "trainer.json"))
    assert d.get("ts", "") >= "2026-09-18", "trainer probe still stale: " + str(d.get("ts"))
    assert d.get("status") in ("down", "no_live_run"), d.get("status")
    live = d.get("liveness", dict())
    assert live.get("term") == "process_state", live
    assert live.get("measured") is True
    assert live.get("process_found") is False
    assert "c9107_stub_disposition.json" in str(d.get("stub_note", ""))


def test_weights_sha256_fully_measured_18_shards_exit0():
    d = _load(os.path.join(PROBES, "c9107_weights_sha256_box.json"))
    lines = d.get("sha_lines", [])
    shard_lines = [ln for ln in lines if ln.endswith(".safetensors")]
    assert len(shard_lines) == 18, "expected 18 shard sha lines, got %d" % len(shard_lines)
    assert d.get("exit_marker") == "EXIT=0", d.get("exit_marker")
    for ln in shard_lines:
        sha = ln.split()[0]
        assert len(sha) == 64, ln
        assert all(ch in "0123456789abcdef" for ch in sha), ln


def test_c9010_requeued_ready_with_evidence_backed_reason():
    d = _load(QUEUE)
    cards = d["cards"] if isinstance(d, dict) else d
    match = [c for c in cards if c.get("id") == "C-9010"]
    if not match:
        import pytest

        pytest.skip("C-9010 has been resolved and removed from the queue (historical test)")
    assert len(match) == 1, "C-9010 not uniquely present"
    c = match[0]
    assert c.get("status") == "ready", c.get("status")
    assert c.get("requeued_utc"), "sanctioned requeue must stamp requeued_utc"
    assert c.get("bounce_count", 0) >= 4, "bounce_count must be preserved, never laundered"
    result = str(c.get("result", ""))
    assert "no live trainer" in result.lower(), result
    assert "c9107_asi3_health.json" in result, "unblock must cite its probe evidence"
    assert (
        "ConnectionRefused" not in result
    ), "stale API-error result must be superseded, not kept as the reason"
