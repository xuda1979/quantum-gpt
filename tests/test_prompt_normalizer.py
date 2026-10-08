"""B-329 RED: Train/eval prompt-format normalization.

The eval harness imports the candidate as a module and calls specific
function names (e.g. ``module.bitstring_cut``, ``module.inclusive_range_sum``).
The training rollout prompt must instruct the model to implement those exact
function signatures so train and eval are byte-identical in their expectations.
"""

from __future__ import annotations

from training.prompt_normalizer import normalize_prompt


def test_normalize_prompt_exists():
    """The normalizer function must exist."""
    assert normalize_prompt is not None


def test_normalize_prompt_adds_solve_interface_when_missing():
    """A prompt with no 'Required interface' section gets the eval-style
    scaffolding appended so the model knows what functions to implement."""
    raw = "Implement a function that computes the max-cut of a graph."
    normalized = normalize_prompt(raw, required_interface=["def solve(graph: list) -> int"])
    assert "def solve(graph: list) -> int" in normalized
    assert "Required interface" in normalized


def test_normalize_prompt_preserves_existing_interface():
    """A prompt that already has a 'Required interface' section is not
    duplicated — the existing section is preserved."""
    raw = (
        "Implement QAOA.\n\n"
        "Required interface:\n"
        "- def bitstring_cut(bits, edges)\n"
        "- def qaoa_circuit(gamma, beta, edges)"
    )
    normalized = normalize_prompt(raw, required_interface=["def bitstring_cut(bits, edges)"])
    # Should not duplicate the section
    assert normalized.count("Required interface") == 1
    # Should preserve the existing interface lines
    assert "def bitstring_cut(bits, edges)" in normalized
    assert "def qaoa_circuit(gamma, beta, edges)" in normalized


def test_train_and_eval_prompts_are_byte_identical():
    """When the same task meta is used, train and eval prompts must be
    byte-identical after normalization."""
    task_prompt = "Implement a quantum circuit for Bell state preparation."
    interface = ["def create_bell_state() -> list", "def measure_circuit(circuit) -> dict"]

    train_prompt = normalize_prompt(task_prompt, required_interface=interface)
    eval_prompt = normalize_prompt(task_prompt, required_interface=interface)

    assert train_prompt == eval_prompt


def test_normalize_prompt_replaces_overly_restrictive_output_contract():
    """The old output contract 'Stop immediately after the final required
    Python statement' suppresses valid multi-function solutions. The normalizer
    replaces it with a contract that allows complete implementations."""
    raw = (
        "Implement a solution.\n\n"
        "Output contract:\n"
        "- Return only the final Python code.\n"
        "- Stop immediately after the final required Python statement."
    )
    normalized = normalize_prompt(raw, required_interface=["def solve() -> int"])
    assert "Stop immediately" not in normalized
    assert "def solve() -> int" in normalized


def test_normalize_prompt_handles_empty_interface():
    """When no required_interface is available, the normalizer passes through
    without crashing."""
    raw = "Write a Python function to sort a list."
    normalized = normalize_prompt(raw, required_interface=[])
    assert "sort a list" in normalized
    # Should not crash, should not add empty interface section
    assert "Required interface:\n\n" not in normalized
