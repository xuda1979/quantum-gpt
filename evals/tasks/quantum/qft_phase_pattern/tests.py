import cmath
import importlib.util
import math


TOL = 1e-9


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _expected_qft_state(n_qubits: int, basis_index: int) -> list[complex]:
    dimension = 1 << n_qubits
    scale = dimension ** -0.5
    return [
        scale * cmath.exp(2j * cmath.pi * basis_index * output_index / dimension)
        for output_index in range(dimension)
    ]


def _close_complex(a: complex, b: complex) -> bool:
    return math.isclose(a.real, b.real, abs_tol=TOL, rel_tol=TOL) and math.isclose(
        a.imag, b.imag, abs_tol=TOL, rel_tol=TOL
    )


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)

    cases = [(2, 0), (2, 1), (3, 5)]
    failures = []
    for n_qubits, basis_index in cases:
        actual = module.qft_basis_state(n_qubits, basis_index)
        expected = _expected_qft_state(n_qubits, basis_index)
        if len(actual) != len(expected):
            failures.append(
                f"qft_basis_state({n_qubits}, {basis_index}) returned length {len(actual)}, expected {len(expected)}"
            )
            continue
        if not all(_close_complex(a, b) for a, b in zip(actual, expected)):
            failures.append(f"qft_basis_state({n_qubits}, {basis_index}) did not match expected amplitudes")

    error_failures = []
    for bad_args in [(0, 0), (2, 4), (2, -1)]:
        try:
            module.qft_basis_state(*bad_args)
        except ValueError:
            continue
        except Exception as exc:  # pragma: no cover - diagnostic path
            error_failures.append(f"qft_basis_state{bad_args} raised {type(exc).__name__}, expected ValueError")
        else:
            error_failures.append(f"qft_basis_state{bad_args} did not raise ValueError")

    failures.extend(error_failures)
    return {
        "passed": not failures,
        "details": failures or ["QFT basis-state phase pattern matches exact formula"],
    }
