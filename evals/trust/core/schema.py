"""SQL schema for the trustable-evaluation provenance ledger.

The ledger is a single SQLite file per evaluation workspace. It is
append-only by convention: rows are inserted, never deleted or mutated.
A `ledger_meta` table carries a schema version and a creation timestamp;
migrations are forward-only.

Tables
------
suite            one row per pinned task-suite version
task             one row per task definition (immutable once pinned)
suite_task       join: which tasks belong to which suite (ordered)
run              one row per evaluation run (model + adapter + suite + k)
prompt_template  one row per (prompt_style, prompt_version) template
task_prompt      one row per (suite, task, prompt_template) — the exact
                 prompt string shown to the model, hashed
model            one row per model checkpoint (base + adapter), hashed
sample           one row per (run, task, sample_index) — the generated
                 candidate code + gen metadata, hashed
verdict          one row per (sample, judge) — deterministic or llm judge
                 result, with test stdout/stderr hashes
claim            one row per numeric claim extracted from a human report
audit_result     one row per (run, report) audit pass
"""
from __future__ import annotations

SCHEMA_VERSION = 1

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS ledger_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS suite (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    suite_hash      TEXT NOT NULL UNIQUE,
    created_at_utc  TEXT NOT NULL,
    source_dir      TEXT NOT NULL,
    n_tasks         INTEGER NOT NULL,
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS task (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id         TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    domain          TEXT NOT NULL,
    category        TEXT NOT NULL,
    task_json_hash  TEXT NOT NULL,
    tests_py_hash   TEXT NOT NULL,
    candidate_ref_hash TEXT NOT NULL,
    workspace_mode  INTEGER NOT NULL DEFAULT 0,
    schema_version  INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS suite_task (
    suite_id    INTEGER NOT NULL REFERENCES suite(id),
    task_id     TEXT NOT NULL REFERENCES task(task_id),
    ord         INTEGER NOT NULL,
    PRIMARY KEY (suite_id, task_id)
);

CREATE TABLE IF NOT EXISTS prompt_template (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    style           TEXT NOT NULL,
    version         TEXT NOT NULL,
    template_hash   TEXT NOT NULL,
    body            TEXT NOT NULL,
    UNIQUE (style, version, template_hash)
);

CREATE TABLE IF NOT EXISTS model (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    label           TEXT NOT NULL,
    base_path       TEXT NOT NULL,
    base_hash       TEXT,           -- may be NULL if path is unavailable
    adapter_path    TEXT,
    adapter_hash    TEXT,
    model_kind      TEXT NOT NULL,  -- 'base' | 'adapter' | 'openai'
    UNIQUE (label, base_path, adapter_path)
);

CREATE TABLE IF NOT EXISTS run (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_hash        TEXT NOT NULL UNIQUE,
    created_at_utc  TEXT NOT NULL,
    suite_id        INTEGER NOT NULL REFERENCES suite(id),
    model_id        INTEGER NOT NULL REFERENCES model(id),
    prompt_template_id INTEGER REFERENCES prompt_template(id),
    k               INTEGER NOT NULL,
    temperature     REAL,
    seed            INTEGER NOT NULL,
    max_new_tokens  INTEGER,
    python_version  TEXT NOT NULL,
    platform        TEXT NOT NULL,
    status          TEXT NOT NULL,  -- 'running' | 'completed' | 'failed'
    duration_sec    REAL
);

CREATE TABLE IF NOT EXISTS task_prompt (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          INTEGER NOT NULL REFERENCES run(id),
    task_id         TEXT NOT NULL REFERENCES task(task_id),
    prompt_hash     TEXT NOT NULL,
    prompt_text     TEXT NOT NULL,
    UNIQUE (run_id, task_id, prompt_hash)
);

CREATE TABLE IF NOT EXISTS sample (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          INTEGER NOT NULL REFERENCES run(id),
    task_id         TEXT NOT NULL REFERENCES task(task_id),
    sample_index    INTEGER NOT NULL,
    candidate_code_hash TEXT NOT NULL,
    candidate_code  TEXT NOT NULL,
    generated_at_utc TEXT NOT NULL,
    gen_sec         REAL,
    finish_reason   TEXT,
    UNIQUE (run_id, task_id, sample_index)
);

CREATE TABLE IF NOT EXISTS verdict (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_id       INTEGER NOT NULL REFERENCES sample(id),
    judge           TEXT NOT NULL,        -- 'deterministic' | 'llm'
    passed          INTEGER NOT NULL,     -- 0 or 1
    details_json    TEXT NOT NULL,        -- list[str]
    failure_category TEXT,
    test_stdout_hash TEXT,
    test_stderr_hash TEXT,
    test_returncode INTEGER,
    scored_at_utc   TEXT NOT NULL,
    judge_meta_hash TEXT,                 -- hash of judge config (for llm)
    UNIQUE (sample_id, judge)
);

CREATE TABLE IF NOT EXISTS claim (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          INTEGER NOT NULL REFERENCES run(id),
    report_path     TEXT NOT NULL,
    line_no         INTEGER NOT NULL,
    claim_text      TEXT NOT NULL,
    claim_kind      TEXT NOT NULL,        -- 'pass_count' | 'pass_at_1' | 'n_tasks' | ...
    claim_value     TEXT NOT NULL,
    backed          INTEGER NOT NULL,     -- 0 or 1
    evidence_json   TEXT                  -- null if unbacked
);

CREATE TABLE IF NOT EXISTS audit_result (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          INTEGER NOT NULL REFERENCES run(id),
    report_path     TEXT NOT NULL,
    audited_at_utc  TEXT NOT NULL,
    n_claims        INTEGER NOT NULL,
    n_backed        INTEGER NOT NULL,
    n_unbacked      INTEGER NOT NULL,
    passed          INTEGER NOT NULL,     -- 1 iff n_unbacked == 0
    details_json    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sample_run ON sample(run_id);
CREATE INDEX IF NOT EXISTS idx_verdict_sample ON verdict(sample_id);
CREATE INDEX IF NOT EXISTS idx_claim_run ON claim(run_id);
"""


def apply_schema(conn) -> None:
    """Create all tables if missing and record schema version."""
    conn.executescript(SCHEMA_SQL)
    conn.execute(
        "INSERT OR IGNORE INTO ledger_meta(key, value) VALUES (?, ?)",
        ("schema_version", str(SCHEMA_VERSION)),
    )
    conn.execute(
        "INSERT OR IGNORE INTO ledger_meta(key, value) VALUES (?, ?)",
        ("created_at_utc", _utc_now()),
    )
    conn.commit()


def _utc_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
