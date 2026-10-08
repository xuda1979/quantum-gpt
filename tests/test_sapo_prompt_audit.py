"""TDD regression tests for scripts/sapo_prompt_audit.py (lane 19 prompt integrity).

Coverage: manifest parsing, per-step task-selection audit (v8 manifest membership,
frozen-holdout exclusion), prompt reconstruction checks (public structure, no
reference solution code, no holdout text), system-prompt hash contract, and the
tampered-prompt fixtures (holdout text injected / reference code injected) that
MUST be flagged.
"""

import json
import sys
import textwrap

import pytest


def _repo_root():
    import pathlib

    return pathlib.Path(__file__).resolve().parent.parent


REPO_ROOT = _repo_root()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import sapo_prompt_audit as spa  # noqa: E402

# ---------------------------------------------------------------------------
# synthetic fixtures
# ---------------------------------------------------------------------------

SYNTH_MANIFEST = textwrap.dedent(
    """\
    # synthetic training manifest (v8-like)
    quantum_fake_synth
    quantum_fake_synth2
    # a comment-only line
    quantum_fake_synth3
    """
)

SYNTH_HOLDOUT = textwrap.dedent(
    """\
    # synthetic frozen holdout
    quantum_fake_holdout_alpha
    quantum_fake_holdout_beta
    """
)

SYNTH_TASK_JSON = {
    "id": "quantum_fake_synth",
    "name": "Fake synth adder",
    "domain": "quantum",
    "category": "fake_category",
    "candidate_file": "candidate.py",
    "test_file": "tests.py",
    "task_prompt": (
        "Implement the function `fake_adder(x)` that returns x + 1. "
        "The current implementation has bugs; fix them."
    ),
}

SYNTH_CANDIDATE_PY = textwrap.dedent(
    """\
    def fake_adder(x):
        y = x + 1
        return y

    def secret_helper():
        magic = 42
        return magic
    """
)

SYNTH_TESTS_PY = textwrap.dedent(
    """\
    def test_fake_adder():
        failures = []
        if fake_adder(1) != 2:
            failures.append("fake_adder returned wrong value for 1")
        if fake_adder(5) != 6:
            failures.append("fake_adder returned wrong value for 5")
        if secret_helper() != 42:
            failures.append("secret_helper returned the wrong constant")
        assert not failures
    """
)

HOLDOUT_ALPHA_TASK_JSON = {
    "id": "quantum_fake_holdout_alpha",
    "name": "Fake holdout alpha transform",
    "domain": "quantum",
    "category": "fake_holdout",
    "candidate_file": "candidate.py",
    "test_file": "tests.py",
    "task_prompt": "Build the alpha transform with secret axis handling.",
}

HOLDOUT_ALPHA_CANDIDATE = textwrap.dedent(
    """\
    def alpha_transform():
        secret_axis = 7
        return secret_axis
    """
)

HOLDOUT_ALPHA_TESTS = textwrap.dedent(
    """\
    def test_alpha():
        assert alpha_transform() == 7, "alpha transform must return 7"
    """
)


@pytest.fixture()
def synth_tasks_dir(tmp_path):
    """Build a synthetic evals/tasks tree with one v8 task and two holdout tasks."""
    tdir = tmp_path / "evals" / "tasks" / "quantum"
    for sub, meta, cand, tests in (
        ("quantum_fake_synth", SYNTH_TASK_JSON, SYNTH_CANDIDATE_PY, SYNTH_TESTS_PY),
        (
            "quantum_fake_holdout_alpha",
            HOLDOUT_ALPHA_TASK_JSON,
            HOLDOUT_ALPHA_CANDIDATE,
            HOLDOUT_ALPHA_TESTS,
        ),
    ):
        d = tdir / sub
        d.mkdir(parents=True)
        (d / "task.json").write_text(json.dumps(meta))
        (d / "candidate.py").write_text(cand)
        (d / "tests.py").write_text(tests)
    # holdout beta has no task dir (id-text check must still work)
    return tmp_path


@pytest.fixture()
def synth_prompt(synth_tasks_dir):
    """The prompt the trainer would build for the synthetic task."""
    prompts = spa.reconstruct_prompts(
        synth_tasks_dir / "evals" / "tasks",
        manifest_ids=["quantum_fake_synth"],
        allowed_domains={"quantum"},
    )
    assert "quantum_fake_synth" in prompts
    return prompts["quantum_fake_synth"]


# ---------------------------------------------------------------------------
# manifest parsing
# ---------------------------------------------------------------------------


def test_parse_manifest_ignores_comments_and_blanks(tmp_path):
    m = tmp_path / "manifest.txt"
    m.write_text(SYNTH_MANIFEST)
    assert spa.parse_manifest(m) == [
        "quantum_fake_synth",
        "quantum_fake_synth2",
        "quantum_fake_synth3",
    ]


# ---------------------------------------------------------------------------
# per-step task selection
# ---------------------------------------------------------------------------


def test_step_selection_clean_when_all_steps_from_manifest():
    manifest = ["quantum_fake_synth", "quantum_fake_synth2"]
    holdout = ["quantum_fake_holdout_alpha", "quantum_fake_holdout_beta"]
    steps = [(1, "quantum_fake_synth"), (2, "quantum_fake_synth2"), (3, "quantum_fake_synth")]
    v = spa.audit_step_selection(manifest, holdout, steps)
    assert v == []


def test_step_selection_flags_holdout_use():
    manifest = ["quantum_fake_synth"]
    holdout = ["quantum_fake_holdout_alpha"]
    steps = [(1, "quantum_fake_synth"), (2, "quantum_fake_holdout_alpha")]
    v = spa.audit_step_selection(manifest, holdout, steps)
    assert any("quantum_fake_holdout_alpha" in str(x) and "step=2" in str(x) for x in v)


def test_step_selection_flags_unknown_task():
    manifest = ["quantum_fake_synth"]
    holdout = ["quantum_fake_holdout_alpha"]
    steps = [(1, "quantum_fake_synth"), (2, "quantum_mystery_task")]
    v = spa.audit_step_selection(manifest, holdout, steps)
    assert any("quantum_mystery_task" in str(x) for x in v)


def test_manifest_holdout_overlap_detected():
    manifest = ["quantum_fake_synth", "quantum_fake_holdout_alpha"]
    holdout = ["quantum_fake_holdout_alpha", "quantum_fake_holdout_beta"]
    steps = [(1, "quantum_fake_synth")]
    v = spa.audit_step_selection(manifest, holdout, steps)
    assert any("overlap" in str(x).lower() for x in v)


def test_parse_step_tasks_from_metrics_jsonl(tmp_path):
    p = tmp_path / "metrics.jsonl"
    p.write_text(
        "\n".join(
            json.dumps({"step": s, "task": t, "loss": -0.01})
            for s, t in [(1, "quantum_fake_synth"), (2, "quantum_fake_synth2")]
        )
        + "\n"
    )
    assert spa.load_step_tasks_from_metrics(p) == [
        (1, "quantum_fake_synth"),
        (2, "quantum_fake_synth2"),
    ]


def test_parse_step_tasks_from_log(tmp_path):
    p = tmp_path / "train.log"
    p.write_text(
        '{"stage": "step_begin", "step": 4, "task": "quantum_fake_synth", "temperature": 1.0}\n'
        '{"stage": "generation_done", "step": 4}\n'
        '{"stage": "step_begin", "step": 5, "task": "quantum_fake_synth2", "temperature": 1.0}\n'
    )
    assert spa.load_step_tasks_from_log(p) == [
        (4, "quantum_fake_synth"),
        (5, "quantum_fake_synth2"),
    ]


# ---------------------------------------------------------------------------
# prompt reconstruction + tampered fixtures (RED -> GREEN core)
# ---------------------------------------------------------------------------


def test_reconstruct_prompt_has_public_structure(synth_prompt):
    p = synth_prompt
    assert p.startswith(SYNTH_TASK_JSON["task_prompt"])
    assert "Task id: quantum_fake_synth" in p
    assert "Domain: quantum" in p
    assert "Category: fake_category" in p
    assert "Required interface:" in p
    assert "Output contract:" in p
    assert "Return only the final Python code." in p


def test_prompt_has_no_reference_solution_code(synth_prompt):
    v = spa.audit_prompt(
        synth_prompt,
        task_id="quantum_fake_synth",
        holdout_ids=["quantum_fake_holdout_alpha", "quantum_fake_holdout_beta"],
        holdout_names=["Fake holdout alpha transform"],
        candidate_path=None,
        tests_path=None,
    )
    assert v == [], f"clean prompt must pass, got: {v}"


def test_tampered_prompt_with_holdout_text_flagged(synth_prompt):
    """TAMPERED FIXTURE: holdout task text injected into a training prompt."""
    tampered = (
        synth_prompt
        + "\n\nNote: remember the holdout task quantum_fake_holdout_alpha (Fake holdout alpha transform)."
    )
    v = spa.audit_prompt(
        tampered,
        task_id="quantum_fake_synth",
        holdout_ids=["quantum_fake_holdout_alpha", "quantum_fake_holdout_beta"],
        holdout_names=["Fake holdout alpha transform"],
        candidate_path=None,
        tests_path=None,
    )
    assert any(
        "holdout" in str(x).lower() for x in v
    ), "holdout text injection must be flagged as a violation"


def test_tampered_prompt_with_reference_code_flagged(synth_prompt, synth_tasks_dir):
    """TAMPERED FIXTURE: reference solution code injected into a training prompt."""
    cand = synth_tasks_dir / "evals" / "tasks" / "quantum" / "quantum_fake_synth" / "candidate.py"
    tampered = synth_prompt + "\n\nHere is a sketch:\n" + "y = x + 1\nmagic = 42\n"
    v = spa.audit_prompt(
        tampered,
        task_id="quantum_fake_synth",
        holdout_ids=["quantum_fake_holdout_alpha"],
        holdout_names=[],
        candidate_path=cand,
        tests_path=None,
    )
    assert any(
        "reference" in str(x).lower() for x in v
    ), "reference code injection must be flagged as a violation"


def test_no_false_positive_on_shared_id_prefix(synth_prompt):
    """Holdout id sharing a prefix with a v8 id must not false-positive."""
    # v8: quantum_fake_synth ; fake holdout that is a PREFIX of a v8 id text
    v = spa.audit_prompt(
        synth_prompt,
        task_id="quantum_fake_synth",
        holdout_ids=["quantum_fake_", "quantum_fake_holdout_beta"],
        holdout_names=[],
        candidate_path=None,
        tests_path=None,
    )
    assert v == [], "id-prefix overlap must not produce false positives"


def test_behavior_hints_are_allowed_in_prompt(synth_prompt, synth_tasks_dir):
    """tests.py hint strings in the Behavioral requirements block are public."""
    tests = synth_tasks_dir / "evals" / "tasks" / "quantum" / "quantum_fake_synth" / "tests.py"
    assert "fake_adder returned wrong value for 1" in synth_prompt
    v = spa.audit_prompt(
        synth_prompt,
        task_id="quantum_fake_synth",
        holdout_ids=["quantum_fake_holdout_alpha"],
        holdout_names=[],
        candidate_path=None,
        tests_path=tests,
    )
    assert v == [], "public behavior hints must not be flagged as leaks"


# ---------------------------------------------------------------------------
# system prompt hash contract
# ---------------------------------------------------------------------------


def test_system_prompt_hash_contract():
    h = spa.system_prompt_hash()
    assert len(h) == 64
    # contract: matches the hash of the trainer's SYSTEM_PROMPT constant
    import hashlib

    from training.grpo_trainer import SYSTEM_PROMPT

    assert h == hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()


def test_system_prompt_contract_mismatch_detected(tmp_path):
    v = spa.audit_system_prompt_contract("0" * 64)
    assert any("system prompt" in str(x).lower() for x in v)


def test_system_prompt_contract_match_passes(tmp_path):
    assert spa.audit_system_prompt_contract(spa.system_prompt_hash()) == []
