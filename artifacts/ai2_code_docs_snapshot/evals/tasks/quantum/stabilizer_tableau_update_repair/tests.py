import copy
import importlib.util



def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


CASES = [
    ("X", ["H"], (1, "Z")),
    ("Z", ["H", "H"], (1, "Z")),
    ("Y", ["H"], (-1, "Y")),
    ("X", ["S"], (1, "Y")),
    ("Y", ["S"], (-1, "X")),
    ("X", ["SDG"], (-1, "Y")),
    ("Y", ["SDG"], (1, "X")),
    ("-X", ["S", "H"], (1, "Y")),
    (" z ", [" h ", " s ", " sdg "], (1, "X")),
    ("I", ["H", "S", "SDG", "H"], (1, "I")),
    ("-Y", ["H", "S", "H"], (-1, "Z")),
    ("X", ["S", "S", "H"], (-1, "Z")),
    ("Y", ["SDG", "H", "S", "H"], (1, "X")),
]


BAD_PAULIS = ["", "A", "-Q"]
BAD_GATES = [["T"], ["H", "measure"], ["S", "CZ"]]



def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    for pauli, gates, expected in CASES:
        original_gates = copy.deepcopy(gates)
        actual = module.apply_gate_sequence(pauli, gates)
        if actual != expected:
            failures.append(
                f"apply_gate_sequence({pauli!r}, {gates!r}) -> {actual!r}, expected {expected!r}"
            )
        if gates != original_gates:
            failures.append(f"apply_gate_sequence mutated gates input for {pauli!r}, {gates!r}")

    for bad_pauli in BAD_PAULIS:
        try:
            module.apply_gate_sequence(bad_pauli, ["H"])
        except ValueError:
            pass
        except Exception as exc:
            failures.append(
                f"apply_gate_sequence({bad_pauli!r}, ['H']) raised {type(exc).__name__}, expected ValueError"
            )
        else:
            failures.append(f"apply_gate_sequence({bad_pauli!r}, ['H']) did not raise ValueError")

    for bad_gates in BAD_GATES:
        try:
            module.apply_gate_sequence("X", bad_gates)
        except ValueError:
            pass
        except Exception as exc:
            failures.append(
                f"apply_gate_sequence('X', {bad_gates!r}) raised {type(exc).__name__}, expected ValueError"
            )
        else:
            failures.append(f"apply_gate_sequence('X', {bad_gates!r}) did not raise ValueError")

    return {
        "passed": not failures,
        "details": failures or [
            "Stabilizer tableau repair preserves sign and axis updates across H/S/SDG sequences"
        ],
    }
