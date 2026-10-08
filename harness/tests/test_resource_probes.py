import os as _os
import tempfile as _tempfile

if not _os.environ.get("QGH_STATE_DIR"):
    _os.environ["QGH_STATE_DIR"] = _tempfile.mkdtemp(prefix="qgh-test-state-")
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qgh  # noqa: E402
import resource_probes as RP  # noqa: E402

LBRACE = chr(123)
RBRACE = chr(125)


def _fake_health(code):
    def fn(port, timeout=6):
        return dict(code=code, body=LBRACE + RBRACE)

    return fn


def _boom_health(port, timeout=6):
    raise OSError("connection refused")


def _fake_exec(out):
    def fn(port, cmd, timeout=90):
        return out

    return fn


def _boom_exec(port, cmd, timeout=90):
    raise OSError("exec transport died")


class TestFailClosed(unittest.TestCase):
    def test_dead_port_renders_unknown_never_dead(self):
        # induced-fire: nothing listens on this port
        p = RP.probe_daemon("asi1", 1, health_fn=_boom_health)
        self.assertEqual(p["status"], "unknown")
        self.assertIn("UNKNOWN", p["summary"])
        self.assertNotIn("dead", p["summary"].lower())
        self.assertNotIn("dead", json.dumps(p).lower())

    def test_http_non_200_is_unknown(self):
        p = RP.probe_daemon("asi2", 19004, health_fn=_fake_health(502))
        self.assertEqual(p["status"], "unknown")
        self.assertIn("UNKNOWN", p["summary"])

    def test_trainer_exec_transport_death_is_unknown(self):
        p = RP.probe_trainer(20653, exec_fn=_boom_exec)
        self.assertEqual(p["status"], "unknown")
        self.assertIn("UNKNOWN", p["summary"])
        self.assertNotIn("dead", json.dumps(p).lower())

    def test_trainer_empty_ps_is_unknown_not_absent(self):
        # box reachable but ps came back empty -> could be an /exec truncation
        # artifact; fail-closed says UNKNOWN, never a confident "no trainer".
        p = RP.probe_trainer(20653, exec_fn=_fake_exec(""))
        self.assertEqual(p["status"], "unknown")


class TestPositiveLiveness(unittest.TestCase):
    def test_healthy_daemon_nonfire(self):
        # positive liveness WITHOUT injection: a real local HTTP server that
        # answers /health 200 {"ok": true} must classify ready.
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer

        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                payload = json.dumps({"ok": True, "ready": True, "pid": 4242}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        srv = HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            port = srv.server_address[1]
            p = RP.probe_daemon("local", port)  # default health_fn (urllib)
            self.assertEqual(p["status"], "ready")
            self.assertIn("READY", p["summary"])
        finally:
            srv.shutdown()

    def test_trainer_pid_via_ps_is_positive_liveness(self):
        out = "12345 3600 python3 grpo_trainer.py --output-dir /box/run"
        p = RP.probe_trainer(20653, exec_fn=_fake_exec(out))
        self.assertEqual(p["status"], "ready")
        self.assertEqual(p["liveness"]["term"], "ps_pid")
        self.assertEqual(p["liveness"]["pid"], 12345)


class TestRealTransportFire(unittest.TestCase):
    # C-0030 acceptance: the fire must be REAL - a genuinely closed port probed
    # through the default urllib transport, not an injected exception.
    def test_real_dead_port_induced_fire(self):
        import socket

        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()  # port is now dead: nothing listens
        p = RP.probe_daemon("asi1", port)  # default health_fn = real urllib
        self.assertEqual(p["status"], "unknown")
        self.assertIn("UNKNOWN", p["summary"])
        self.assertNotIn("dead", json.dumps(p).lower())
        self.assertNotIn("ready", p["status"])

    def test_healthy_daemon_carries_positive_liveness_term(self):
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer

        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                payload = json.dumps(dict(ready=True, pid=4242)).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        srv = HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            p = RP.probe_daemon("asi1", srv.server_address[1])
            self.assertEqual(p["status"], "ready")
            # positive liveness term: the pid the daemon itself reported
            self.assertEqual(p["liveness"], dict(term="health_pid", pid=4242))
        finally:
            srv.shutdown()

    def test_runall_durable_file_carries_liveness_term(self):
        d = tempfile.mkdtemp(prefix="qgh-probe-live-")
        body = chr(123) + '"ready": true, "pid": 31337' + chr(125)

        def health(port, timeout=6):
            return dict(code=200, body=body)

        RP.run_all(d, health_fn=health, trainer_exec=_fake_exec("1 1 x"))
        for name in ("asi1", "asi2", "asi3"):
            data = json.load(open(os.path.join(d, "probes", name + ".json")))
            self.assertEqual(data["liveness"], dict(term="health_pid", pid=31337), name)


class TestDurableStateFiles(unittest.TestCase):
    def test_write_all_lands_files_and_renderer_reads_them(self):
        d = tempfile.mkdtemp(prefix="qgh-probe-test-")
        payloads = RP.run_all(
            d,
            health_fn=_fake_health(200),
            trainer_exec=_fake_exec("777 60 python3 grpo_trainer.py"),
        )
        self.assertEqual(sorted(payloads), ["asi1", "asi2", "asi3", "train_fire", "trainer"])
        for name in ("asi1", "asi2", "asi3", "train_fire", "trainer"):
            path = os.path.join(d, "probes", name + ".json")
            data = json.load(open(path, encoding="utf-8"))
            self.assertTrue(data["ts"])  # ts stamped at write time
            self.assertTrue(data["summary"])
            self.assertIn("status", data)
        # the actual standup renderer consumes these exact files
        old_state = qgh.STATE
        qgh.STATE = d
        try:
            rendered = qgh._probe_results()
        finally:
            qgh.STATE = old_state
        for name in ("asi1", "asi2", "asi3", "train_fire", "trainer"):
            self.assertNotIn("NO PROBE YET", rendered[name], name)
            self.assertNotIn("STALE", rendered[name], name)


if __name__ == "__main__":
    unittest.main()
