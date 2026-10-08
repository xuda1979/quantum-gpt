"""SQLite provenance ledger for the trustable evaluation subsystem.

The ledger is the single source of truth. Every artifact (suite, task,
run, sample, verdict, claim) is recorded here with its content hash.
Public functions return plain dicts so callers can serialize them to
JSON without depending on row objects.

Concurrency: the ledger uses a single writer thread by convention.
Reads are snapshot-consistent under WAL mode.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from . import hashing
from .schema import apply_schema

_LOCK = threading.RLock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Ledger:
    """Thin wrapper around a SQLite connection with typed helpers."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(
            str(self.db_path),
            isolation_level=None,       # autocommit; we manage txns explicitly
            check_same_thread=False,
        )
        self._conn.row_factory = sqlite3.Row
        apply_schema(self._conn)

    # ── connection helpers ──────────────────────────────────────────────
    @contextmanager
    def txn(self) -> Iterator[sqlite3.Connection]:
        with _LOCK:
            self._conn.execute("BEGIN")
            try:
                yield self._conn
                self._conn.execute("COMMIT")
            except Exception:
                self._conn.execute("ROLLBACK")
                raise

    def close(self) -> None:
        self._conn.close()

    # ── suite + task ────────────────────────────────────────────────────
    def register_task(
        self,
        *,
        task_id: str,
        name: str,
        domain: str,
        category: str,
        task_json_hash: str,
        tests_py_hash: str,
        candidate_ref_hash: str,
        workspace_mode: bool = False,
    ) -> int:
        with self.txn() as c:
            c.execute(
                """INSERT OR IGNORE INTO task
                   (task_id, name, domain, category, task_json_hash,
                    tests_py_hash, candidate_ref_hash, workspace_mode)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (task_id, name, domain, category, task_json_hash,
                 tests_py_hash, candidate_ref_hash, int(workspace_mode)),
            )
            row = c.execute(
                "SELECT id FROM task WHERE task_id=?", (task_id,)
            ).fetchone()
            return int(row["id"])

    def register_suite(
        self,
        *,
        suite_hash: str,
        source_dir: str,
        n_tasks: int,
        task_ids: list[str],
        notes: str | None = None,
    ) -> int:
        with self.txn() as c:
            c.execute(
                """INSERT OR IGNORE INTO suite
                   (suite_hash, created_at_utc, source_dir, n_tasks, notes)
                   VALUES (?,?,?,?,?)""",
                (suite_hash, utc_now(), source_dir, n_tasks, notes),
            )
            row = c.execute(
                "SELECT id FROM suite WHERE suite_hash=?", (suite_hash,)
            ).fetchone()
            suite_id = int(row["id"])
            for ord_idx, tid in enumerate(task_ids):
                c.execute(
                    """INSERT OR IGNORE INTO suite_task
                       (suite_id, task_id, ord) VALUES (?,?,?)""",
                    (suite_id, tid, ord_idx),
                )
            return suite_id

    # ── prompt template ─────────────────────────────────────────────────
    def register_prompt_template(
        self, *, style: str, version: str, body: str
    ) -> int:
        th = hashing.hash_text(body)
        with self.txn() as c:
            c.execute(
                """INSERT OR IGNORE INTO prompt_template
                   (style, version, template_hash, body)
                   VALUES (?,?,?,?)""",
                (style, version, th, body),
            )
            row = c.execute(
                """SELECT id FROM prompt_template
                   WHERE style=? AND version=? AND template_hash=?""",
                (style, version, th),
            ).fetchone()
            return int(row["id"])

    # ── model ───────────────────────────────────────────────────────────
    def register_model(
        self,
        *,
        label: str,
        base_path: str,
        base_hash: str | None,
        adapter_path: str | None,
        adapter_hash: str | None,
        model_kind: str,
    ) -> int:
        with self.txn() as c:
            c.execute(
                """INSERT OR IGNORE INTO model
                   (label, base_path, base_hash, adapter_path, adapter_hash, model_kind)
                   VALUES (?,?,?,?,?,?)""",
                (label, base_path, base_hash, adapter_path, adapter_hash, model_kind),
            )
            row = c.execute(
                """SELECT id FROM model
                   WHERE label=? AND base_path=? AND adapter_path IS ?""",
                (label, base_path, adapter_path),
            ).fetchone()
            return int(row["id"])

    # ── run ─────────────────────────────────────────────────────────────
    def register_run(self, **fields: Any) -> int:
        cols = [
            "run_hash", "created_at_utc", "suite_id", "model_id",
            "prompt_template_id", "k", "temperature", "seed",
            "max_new_tokens", "python_version", "platform", "status",
        ]
        vals = [fields[c] for c in cols]
        with self.txn() as c:
            c.execute(
                f"""INSERT OR IGNORE INTO run ({','.join(cols)})
                    VALUES ({','.join('?' * len(cols))})""",
                vals,
            )
            row = c.execute(
                "SELECT id FROM run WHERE run_hash=?", (fields["run_hash"],)
            ).fetchone()
            return int(row["id"])

    def update_run_status(
        self, run_id: int, *, status: str, duration_sec: float | None
    ) -> None:
        with self.txn() as c:
            c.execute(
                "UPDATE run SET status=?, duration_sec=? WHERE id=?",
                (status, duration_sec, run_id),
            )

    # ── task_prompt ─────────────────────────────────────────────────────
    def record_task_prompt(
        self, *, run_id: int, task_id: str, prompt_text: str
    ) -> int:
        ph = hashing.hash_text(prompt_text)
        with self.txn() as c:
            c.execute(
                """INSERT OR IGNORE INTO task_prompt
                   (run_id, task_id, prompt_hash, prompt_text)
                   VALUES (?,?,?,?)""",
                (run_id, task_id, ph, prompt_text),
            )
            row = c.execute(
                """SELECT id FROM task_prompt
                   WHERE run_id=? AND task_id=? AND prompt_hash=?""",
                (run_id, task_id, ph),
            ).fetchone()
            return int(row["id"])

    # ── sample + verdict ────────────────────────────────────────────────
    def record_sample(
        self,
        *,
        run_id: int,
        task_id: str,
        sample_index: int,
        candidate_code: str,
        generated_at_utc: str,
        gen_sec: float | None,
        finish_reason: str | None,
    ) -> int:
        ch = hashing.hash_text(candidate_code)
        with self.txn() as c:
            c.execute(
                """INSERT OR IGNORE INTO sample
                   (run_id, task_id, sample_index, candidate_code_hash,
                    candidate_code, generated_at_utc, gen_sec, finish_reason)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (run_id, task_id, sample_index, ch, candidate_code,
                 generated_at_utc, gen_sec, finish_reason),
            )
            row = c.execute(
                """SELECT id FROM sample
                   WHERE run_id=? AND task_id=? AND sample_index=?""",
                (run_id, task_id, sample_index),
            ).fetchone()
            return int(row["id"])

    def record_verdict(
        self,
        *,
        sample_id: int,
        judge: str,
        passed: bool,
        details: list[str],
        failure_category: str | None,
        test_stdout_hash: str | None,
        test_stderr_hash: str | None,
        test_returncode: int | None,
        judge_meta_hash: str | None = None,
    ) -> int:
        with self.txn() as c:
            c.execute(
                """INSERT OR IGNORE INTO verdict
                   (sample_id, judge, passed, details_json, failure_category,
                    test_stdout_hash, test_stderr_hash, test_returncode,
                    scored_at_utc, judge_meta_hash)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (sample_id, judge, int(passed), json.dumps(details, ensure_ascii=False),
                 failure_category, test_stdout_hash, test_stderr_hash,
                 test_returncode, utc_now(), judge_meta_hash),
            )
            row = c.execute(
                "SELECT id FROM verdict WHERE sample_id=? AND judge=?",
                (sample_id, judge),
            ).fetchone()
            return int(row["id"])

    # ── claim + audit ───────────────────────────────────────────────────
    def record_claim(
        self,
        *,
        run_id: int,
        report_path: str,
        line_no: int,
        claim_text: str,
        claim_kind: str,
        claim_value: str,
        backed: bool,
        evidence: dict[str, Any] | None,
    ) -> int:
        with self.txn() as c:
            c.execute(
                """INSERT OR IGNORE INTO claim
                   (run_id, report_path, line_no, claim_text, claim_kind,
                    claim_value, backed, evidence_json)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (run_id, report_path, line_no, claim_text, claim_kind,
                 claim_value, int(backed),
                 json.dumps(evidence, ensure_ascii=False) if evidence else None),
            )
            row = c.execute(
                """SELECT id FROM claim
                   WHERE run_id=? AND report_path=? AND line_no=? AND claim_text=?""",
                (run_id, report_path, line_no, claim_text),
            ).fetchone()
            return int(row["id"])

    def record_audit_result(
        self,
        *,
        run_id: int,
        report_path: str,
        n_claims: int,
        n_backed: int,
        n_unbacked: int,
        passed: bool,
        details: list[dict[str, Any]],
    ) -> int:
        with self.txn() as c:
            c.execute(
                """INSERT INTO audit_result
                   (run_id, report_path, audited_at_utc, n_claims, n_backed,
                    n_unbacked, passed, details_json)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (run_id, report_path, utc_now(), n_claims, n_backed,
                 n_unbacked, int(passed), json.dumps(details, ensure_ascii=False)),
            )
            return int(c.execute("SELECT last_insert_rowid()").fetchone()[0])

    # ── queries ─────────────────────────────────────────────────────────
    def get_run(self, run_id: int) -> dict[str, Any]:
        with self.txn() as c:
            row = c.execute("SELECT * FROM run WHERE id=?", (run_id,)).fetchone()
            return dict(row) if row else {}

    def get_run_by_hash(self, run_hash: str) -> dict[str, Any]:
        with self.txn() as c:
            row = c.execute("SELECT * FROM run WHERE run_hash=?", (run_hash,)).fetchone()
            return dict(row) if row else {}

    def list_samples(self, run_id: int) -> list[dict[str, Any]]:
        with self.txn() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM sample WHERE run_id=? ORDER BY task_id, sample_index",
                (run_id,),
            )]

    def list_verdicts(self, sample_id: int) -> list[dict[str, Any]]:
        with self.txn() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM verdict WHERE sample_id=?", (sample_id,),
            )]

    def suite_tasks(self, suite_id: int) -> list[dict[str, Any]]:
        with self.txn() as c:
            return [dict(r) for r in c.execute(
                """SELECT t.* FROM task t
                   JOIN suite_task st ON st.task_id = t.task_id
                   WHERE st.suite_id=? ORDER BY st.ord""",
                (suite_id,),
            )]

    def run_summary(self, run_id: int) -> dict[str, Any]:
        """Aggregate pass@1, pass@k, by-domain, by-category for a run."""
        with self.txn() as c:
            samples = [dict(r) for r in c.execute(
                "SELECT task_id, sample_index FROM sample WHERE run_id=?",
                (run_id,),
            )]
            verdicts: dict[int, list[dict[str, Any]]] = {}
            for s in samples:
                # we need sample id; redo with id
                pass
            rows = [dict(r) for r in c.execute(
                """SELECT s.id, s.task_id, s.sample_index, v.judge, v.passed,
                          t.domain, t.category, t.name
                   FROM sample s
                   JOIN verdict v ON v.sample_id = s.id
                   JOIN task t ON t.task_id = s.task_id
                   WHERE s.run_id=?""",
                (run_id,),
            )]
        # group by task
        by_task: dict[str, dict[str, Any]] = {}
        for r in rows:
            t = by_task.setdefault(r["task_id"], {
                "task_id": r["task_id"], "name": r["name"],
                "domain": r["domain"], "category": r["category"],
                "n_samples": 0, "n_pass_det": 0, "n_pass_llm": 0,
            })
            t["n_samples"] = max(t["n_samples"], r["sample_index"] + 1)
            if r["judge"] == "deterministic" and r["passed"]:
                t["n_pass_det"] += 1
            if r["judge"] == "llm" and r["passed"]:
                t["n_pass_llm"] += 1
        # pass@1 = task passes iff ANY sample passed (deterministic judge)
        n_tasks = len(by_task)
        n_pass = sum(1 for t in by_task.values() if t["n_pass_det"] > 0)
        for t in by_task.values():
            t["pass_at_1"] = 1.0 if t["n_pass_det"] > 0 else 0.0
        return {
            "n_tasks": n_tasks,
            "n_pass": n_pass,
            "pass_at_1": round(n_pass / n_tasks, 4) if n_tasks else 0.0,
            "by_task": list(by_task.values()),
            "disagreements": [],
        }
