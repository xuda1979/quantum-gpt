"""C-9108: Base-leg slice transport verifier (box -> Mac, fail-closed).

C-9029 leg outputs must land Mac-side complete (18/18, parseable,
truncation-field intact) before C-9030 reads them. The box->Mac pull has a
documented truncation history (box_pull_ledger; chunked-b64 fix), and
C-9030 is file-only: a silent short pull would bounce the base verdict
around the whole chain again.

Pinned here:
- a pull yielding < expected_tasks files, a non-JSON-parseable slice, or a
  slice missing the per-task truncation field (`output_chars`) is rejected
  FAIL-CLOSED with named missing-ids / named files,
- transport is the chunked-b64 recipe (stat size, then `dd bs=1 skip=N
  count=CH | base64 -w0` via /exec) -- never one raw `cat`,
- per-file byte counts are verified vs the box-side stat size,
- slices land under outputs/c9003_base_slice*.json (the exact C-9030 glob),
- a transport receipt with sha256 per slice is written (updated in place,
  never duplicated),
- idempotent re-run: already-verified slices are skipped, not re-pulled,
- a short/tampered chunk NEVER lands a partial slice (tmp+os.replace only
  after full byte-count verify).
"""

import base64
import hashlib
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, HARNESS_DIR)
import slice_transport  # noqa: E402

try:  # canonical 18 ids for naming missing-ids precisely
    sys.path.insert(0, os.path.join(HARNESS_DIR, os.pardir, "evals", "runner"))
    from holdout_freeze import bench_task_ids

    EXPECTED_IDS = sorted(bench_task_ids())
except Exception:  # pragma: no cover - keeps the test hermetic
    EXPECTED_IDS = [f"task_{i:02d}" for i in range(18)]

PORT = 19004


def _slice_payload(ids, truncation_field="output_chars"):
    records = []
    for tid in ids:
        rec = {"task_id": tid, "passed": False, "scores": {"overall": 0.0}}
        if truncation_field is not None:
            rec[truncation_field] = 128
        records.append(rec)
    return {
        "leg": "c9003-base",
        "task_ids": list(ids),
        "records": records,
    }


def _write_slice(outdir, name, payload):
    path = os.path.join(outdir, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, indent=2) + "\n")
    return path


class TestC9108SliceTransport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="c9108-")
        self.out = os.path.join(self.tmp, "outputs")
        os.makedirs(self.out, exist_ok=True)

    # -- verify_slices: the fail-closed core --------------------------------

    def test_short_pull_rejected_with_named_missing_ids(self):
        _write_slice(self.out, "c9003_base_slice0.json", _slice_payload(EXPECTED_IDS[:6]))
        _write_slice(self.out, "c9003_base_slice6.json", _slice_payload(EXPECTED_IDS[6:11]))
        verdict = slice_transport.verify_slices(self.out, expected_task_ids=EXPECTED_IDS)
        self.assertFalse(verdict["ok"], "11/18 tasks must be rejected")
        self.assertEqual(
            sorted(verdict["missing_task_ids"]),
            EXPECTED_IDS[11:],
            "the 7 absent task ids must be NAMED, not counted",
        )

    def test_unparseable_slice_rejected_and_named(self):
        # the documented truncation history: file cut mid-JSON
        path = _write_slice(self.out, "c9003_base_slice0.json", _slice_payload(EXPECTED_IDS[:18]))
        with open(path, encoding="utf-8") as f:
            text = f.read()
        with open(path, "w", encoding="utf-8") as f:
            f.write(text[: len(text) // 2])
        verdict = slice_transport.verify_slices(self.out, expected_task_ids=EXPECTED_IDS)
        self.assertFalse(verdict["ok"], "a torn slice must be rejected")
        self.assertIn("c9003_base_slice0.json", verdict["unparseable"])

    def test_slice_missing_truncation_field_rejected_named_task(self):
        _write_slice(self.out, "c9003_base_slice0.json", _slice_payload(EXPECTED_IDS[:9]))
        # 8 ok records + 1 record WITHOUT the truncation field
        payload = _slice_payload(EXPECTED_IDS[9:18])
        payload["records"][3].pop("output_chars")
        payload["task_ids"] = [r["task_id"] for r in payload["records"]]
        _write_slice(self.out, "c9003_base_slice9.json", payload)
        verdict = slice_transport.verify_slices(self.out, expected_task_ids=EXPECTED_IDS)
        self.assertFalse(verdict["ok"], "missing truncation field must fail closed")
        self.assertIn(EXPECTED_IDS[12], verdict["missing_truncation_field"])

    def test_complete_18_of_18_pull_accepted(self):
        _write_slice(self.out, "c9003_base_slice0.json", _slice_payload(EXPECTED_IDS[:6]))
        _write_slice(self.out, "c9003_base_slice6.json", _slice_payload(EXPECTED_IDS[6:12]))
        _write_slice(self.out, "c9003_base_slice12.json", _slice_payload(EXPECTED_IDS[12:]))
        verdict = slice_transport.verify_slices(self.out, expected_task_ids=EXPECTED_IDS)
        self.assertTrue(verdict["ok"], "18/18 complete must be accepted")
        self.assertEqual(verdict["n_tasks"], 18)

    def test_duplicate_task_across_slices_rejected(self):
        _write_slice(self.out, "c9003_base_slice0.json", _slice_payload(EXPECTED_IDS[:6]))
        # second slice starts at index 5 -> one id lands in both slices
        _write_slice(self.out, "c9003_base_slice6.json", _slice_payload(EXPECTED_IDS[5:12]))
        verdict = slice_transport.verify_slices(self.out, expected_task_ids=EXPECTED_IDS)
        self.assertFalse(verdict["ok"], "double-counted tasks must be rejected")
        self.assertIn(EXPECTED_IDS[5], verdict["duplicate_task_ids"])

    # -- transport: chunked-b64, byte-verified, atomic land ------------------

    def _fake_exec(self, remote_files, captured=None):
        """Build an exec stub serving `stat` then `dd|base64` chunk commands."""

        def run(cmd_text, port=PORT):
            if captured is not None:
                captured.append(cmd_text)
            if cmd_text.startswith("stat -c %s "):
                remote = cmd_text.split("stat -c %s ", 1)[1].strip()
                return str(os.path.getsize(remote_files[remote]))
            if cmd_text.startswith("dd if="):
                body = cmd_text.split(" | ", 1)[0]
                parts = body.split()
                remote = parts[1].split("=", 1)[1]
                skip = int(parts[3].split("=")[1])
                count = int(parts[4].split("=")[1])
                with open(remote_files[remote], "rb") as f:
                    f.seek(skip)
                    data = f.read(count)
                return base64.b64encode(data).decode("ascii")
            raise AssertionError(f"unexpected exec command: {cmd_text!r}")

        return run

    def test_chunked_transport_lands_complete_slice_with_receipt(self):
        captured = []
        payload = _slice_payload(EXPECTED_IDS)
        boxdir = os.path.join(self.tmp, "box", "outputs")
        os.makedirs(boxdir, exist_ok=True)
        remote = os.path.join(boxdir, "c9003_base_slice0.json")
        with open(remote, "w", encoding="utf-8") as f:
            f.write(json.dumps(payload, indent=2) + "\n")
        remote_bytes = open(remote, "rb").read()

        exec_run = self._fake_exec({remote: remote}, captured)
        with mock.patch.object(slice_transport, "_exec_run", exec_run):
            result = slice_transport.pull_slice(
                PORT,
                remote,
                "c9003_base_slice0.json",
                outputs_dir=self.out,
                chunk_size=512,
            )
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["bytes"], len(remote_bytes), "byte count vs box size")
        local = os.path.join(self.out, "c9003_base_slice0.json")
        self.assertEqual(open(local, "rb").read(), remote_bytes)
        # chunked recipe: stat first, then dd|base64 -- NEVER a bare cat
        self.assertTrue(captured[0].startswith("stat -c %s "))
        self.assertGreater(
            len([c for c in captured if c.startswith("dd if=")]),
            1,
            "must be CHUNKED, not one chunk",
        )
        self.assertFalse(
            any(c.startswith("cat ") for c in captured), "single raw pull is the banned transport"
        )
        receipt = slice_transport.read_receipt(self.out)
        self.assertEqual(
            receipt["slices"]["c9003_base_slice0.json"]["sha256"],
            hashlib.sha256(remote_bytes).hexdigest(),
        )
        self.assertEqual(receipt["slices"]["c9003_base_slice0.json"]["bytes"], len(remote_bytes))

    def test_tampered_short_chunk_never_lands_partial_slice(self):
        boxdir = os.path.join(self.tmp, "box", "outputs")
        os.makedirs(boxdir, exist_ok=True)
        remote = os.path.join(boxdir, "c9003_base_slice0.json")
        _write_slice(boxdir, "c9003_base_slice0.json", _slice_payload(EXPECTED_IDS))
        real_exec = self._fake_exec({remote: remote})

        def short_run(cmd_text, port=PORT):
            out = real_exec(cmd_text, port)
            if cmd_text.startswith("dd if="):
                return out[: max(0, len(out) - 8)]  # chopped b64 tail
            return out

        with mock.patch.object(slice_transport, "_exec_run", short_run):
            result = slice_transport.pull_slice(
                PORT,
                remote,
                "c9003_base_slice0.json",
                outputs_dir=self.out,
                chunk_size=512,
            )
        self.assertFalse(result["ok"], "short transfer must fail closed")
        self.assertEqual(
            [p for p in os.listdir(self.out) if p.endswith(".tmp")],
            [],
            "no torn temp file may survive a rejected pull",
        )
        self.assertFalse(
            os.path.exists(os.path.join(self.out, "c9003_base_slice0.json")),
            "a byte-short slice must NEVER land under the C-9030 glob",
        )

    def test_idempotent_rerun_skips_verified_slices_receipt_not_duplicated(self):
        boxdir = os.path.join(self.tmp, "box", "outputs")
        os.makedirs(boxdir, exist_ok=True)
        remote = os.path.join(boxdir, "c9003_base_slice0.json")
        _write_slice(boxdir, "c9003_base_slice0.json", _slice_payload(EXPECTED_IDS))
        exec_run = self._fake_exec({remote: remote})

        with mock.patch.object(slice_transport, "_exec_run", exec_run):
            first = slice_transport.pull_slice(
                PORT, remote, "c9003_base_slice0.json", outputs_dir=self.out, chunk_size=512
            )
            self.assertTrue(first["ok"])
            captured = []
            exec_run2 = self._fake_exec({remote: remote}, captured)
            with mock.patch.object(slice_transport, "_exec_run", exec_run2):
                second = slice_transport.pull_slice(
                    PORT,
                    remote,
                    "c9003_base_slice0.json",
                    outputs_dir=self.out,
                    chunk_size=512,
                )
        self.assertTrue(second["ok"])
        self.assertTrue(second["skipped"], "verified slice must be skipped, not re-pulled")
        self.assertEqual(
            [c for c in captured if c.startswith("dd if=")],
            [],
            "idempotent re-run must issue no chunk fetches",
        )
        self.assertEqual(
            [p for p in os.listdir(self.out) if "receipt" in p],
            [slice_transport.RECEIPT_NAME],
            "receipt updated in place, never duplicated",
        )

    def test_zero_slices_fail_closed_names_all_18(self):
        verdict = slice_transport.verify_slices(self.out, expected_task_ids=EXPECTED_IDS)
        self.assertFalse(verdict["ok"], "zero slices must fail closed")
        self.assertEqual(verdict["n_slices"], 0)
        self.assertEqual(
            sorted(verdict["missing_task_ids"]),
            EXPECTED_IDS,
            "all 18 absent ids must be NAMED, not counted",
        )

    def test_disk_tampered_verified_slice_is_repulled_not_trusted(self):
        boxdir = os.path.join(self.tmp, "box", "outputs")
        os.makedirs(boxdir, exist_ok=True)
        remote = os.path.join(boxdir, "c9003_base_slice0.json")
        _write_slice(boxdir, "c9003_base_slice0.json", _slice_payload(EXPECTED_IDS))
        remote_bytes = open(remote, "rb").read()
        exec_run = self._fake_exec(dict([(remote, remote)]))
        with mock.patch.object(slice_transport, "_exec_run", exec_run):
            first = slice_transport.pull_slice(
                PORT, remote, "c9003_base_slice0.json", outputs_dir=self.out, chunk_size=512
            )
        self.assertTrue(first["ok"])
        local = os.path.join(self.out, "c9003_base_slice0.json")
        payload = json.loads(open(local, encoding="utf-8").read())
        payload["records"][0]["scores"]["overall"] = 99.0
        _write_slice(self.out, "c9003_base_slice0.json", payload)
        captured = []
        exec_run2 = self._fake_exec(dict([(remote, remote)]), captured)
        with mock.patch.object(slice_transport, "_exec_run", exec_run2):
            second = slice_transport.pull_slice(
                PORT, remote, "c9003_base_slice0.json", outputs_dir=self.out, chunk_size=512
            )
        self.assertFalse(
            second["skipped"], "a receipt-sha-mismatched slice must be re-pulled, not trusted"
        )
        self.assertTrue(
            any(c.startswith("dd if=") for c in captured), "re-pull must actually re-fetch"
        )
        self.assertEqual(open(local, "rb").read(), remote_bytes, "re-pull restores exact bytes")

    def test_cli_pulls_all_slices_and_verifies_gate(self):
        boxdir = os.path.join(self.tmp, "box", "outputs")
        os.makedirs(boxdir, exist_ok=True)
        remotes = dict()
        for start in (0, 6, 12):
            name = "c9003_base_slice" + str(start) + ".json"
            remotes[os.path.join(boxdir, name)] = _write_slice(
                boxdir, name, _slice_payload(EXPECTED_IDS[start : start + 6])
            )
        exec_run = self._fake_exec(remotes)
        with mock.patch.object(slice_transport, "_exec_run", exec_run):
            rc = slice_transport.main(
                ["--port", str(PORT), "--outputs", self.out, "--remote-root", boxdir]
            )
        self.assertEqual(rc, 0, "complete 18/18 transport + gate must exit 0")
        landed = sorted(p for p in os.listdir(self.out) if p.startswith("c9003_base_slice"))
        self.assertEqual(
            landed,
            ["c9003_base_slice0.json", "c9003_base_slice12.json", "c9003_base_slice6.json"],
            "slices must land under the exact C-9030 glob names",
        )
        receipt = slice_transport.read_receipt(self.out)
        self.assertEqual(len(receipt["slices"]), 3, "one receipt entry per slice, in ONE receipt")
        self.assertTrue(slice_transport.verify_slices(self.out, EXPECTED_IDS)["ok"])

    def test_cli_verify_only_issues_zero_transport_calls_and_fails_closed(self):
        _write_slice(self.out, "c9003_base_slice0.json", _slice_payload(EXPECTED_IDS[:6]))

        def boobytrap(cmd_text, port=PORT):
            raise AssertionError("verify-only must issue zero transport calls")

        with mock.patch.object(slice_transport, "_exec_run", boobytrap):
            rc = slice_transport.main(["--verify-only", "--outputs", self.out])
        self.assertEqual(rc, 1, "6/18 under verify-only must fail closed with exit 1")

    def test_landed_name_matches_c9030_glob(self):
        # the C-9030 contract: outputs/c9003_base_slice*.json
        self.assertRegex(slice_transport.slice_local_name(0), r"^c9003_base_slice\d+\.json$")


if __name__ == "__main__":
    unittest.main()
