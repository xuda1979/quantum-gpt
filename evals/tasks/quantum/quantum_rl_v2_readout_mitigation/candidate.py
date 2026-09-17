"""One-qubit readout-error mitigation in Qiskit Aer. Prepare RY(2.0)|0>,
add a readout assignment error P(1|0)=0.1, P(0|1)=0.04, derive the exact
2x2 assignment matrix under an explicit row/column convention (rows =
measured outcome, columns = prepared state), prove by exact probability
algebra that matrix inversion recovers cos(2.0), estimate the calibration
columns and the target counts with 30000 seeded shots, reject
ill-conditioned matrices, and assert that the shot-based corrected Z
agrees with cos(2.0) within a propagated statistical tolerance."""

import math

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError

P11_GIVEN_0 = 0.1  # P(measure 1 | prepared 0)
P00_GIVEN_1 = 0.04  # P(measure 0 | prepared 1)
TARGET_EXPECTATION = math.cos(2.0)  # <Z> of RY(2.0)|0>


def assignment_matrix():
    """Exact 2x2 assignment matrix, rows = measured outcome,
    columns = prepared state: [[P(0|0), P(0|1)], [P(1|0), P(1|1)]]."""
    return np.array(
        [
            [1.0 - P11_GIVEN_0, P00_GIVEN_1],
            [P11_GIVEN_0, 1.0 - P00_GIVEN_1],
        ],
        dtype=float,
    )


def condition_number():
    """Condition number of the exact assignment matrix (ill-conditioned
    matrices must be rejected before inversion)."""
    return float(np.linalg.cond(assignment_matrix()))


def prepare_circuit():
    """One-qubit circuit preparing RY(2.0)|0>."""
    qc = QuantumCircuit(1)
    qc.ry(2.0, 0)
    return qc


def exact_true_probabilities():
    """Exact ideal (noise-free) outcome probabilities of RY(2.0)|0>:
    [cos^2(1.0), sin^2(1.0)]."""
    return np.array([math.cos(1.0) ** 2, math.sin(1.0) ** 2])


def exact_algebra_proof():
    """Exact probability algebra: A^-1 (A p_true) must recover p_true, and
    the recovered Z must equal cos(2.0) exactly."""
    p_true = exact_true_probabilities()
    measured = assignment_matrix() @ p_true
    recovered = np.linalg.solve(assignment_matrix(), measured)
    z = 2.0 * recovered[0] - 1.0
    return {
        "measured": measured,
        "recovered": recovered,
        "recovered_z": float(z),
        "target_z": float(TARGET_EXPECTATION),
    }


def _noisy_counts(prep_circuit, shots, seed):
    """Sample a prepared circuit through the readout assignment channel.
    qiskit-aer's ReadoutError matrix has rows = prepared state and columns =
    measured outcome, the transpose of our rows=measured convention."""
    readout = ReadoutError(assignment_matrix().T.tolist())
    noise_model = NoiseModel()
    noise_model.add_readout_error(readout, [0])
    qc = prep_circuit.copy()
    qc.measure_all()
    backend = AerSimulator(noise_model=noise_model, seed_simulator=seed)
    return backend.run(qc, shots=shots).result().get_counts()


def calibrate(shots=30000, seed=1234):
    """Estimate the two calibration columns with seeded shots:
    column 0 from |0> preparation, column 1 from |1> preparation."""
    zero_circ = QuantumCircuit(1)
    one_circ = QuantumCircuit(1)
    one_circ.x(0)
    col0_counts = _noisy_counts(zero_circ, shots, seed)
    col1_counts = _noisy_counts(one_circ, shots, seed)
    col0 = np.array([col0_counts.get("0", 0), col0_counts.get("1", 0)], dtype=float)
    col1 = np.array([col1_counts.get("0", 0), col1_counts.get("1", 0)], dtype=float)
    col0 /= col0.sum()
    col1 /= col1.sum()
    return np.column_stack([col0, col1])


def sample_target(shots=30000, seed=1234):
    """Seeded noisy counts of the RY(2.0) target circuit."""
    return _noisy_counts(prepare_circuit(), shots, seed)


def mitigate(counts, calibration):
    """Invert the estimated assignment matrix on the measured counts with
    normalization and physical clipping diagnostics."""
    measured = np.array([counts.get("0", 0), counts.get("1", 0)], dtype=float)
    measured /= measured.sum()
    if np.linalg.cond(calibration) > 20.0:
        raise ValueError("ill-conditioned calibration matrix: cond > 20")
    corrected = np.linalg.solve(calibration, measured)
    raw_norm = float(corrected.sum())
    clipped = np.clip(corrected, 0.0, 1.0)
    clip_amount = float(np.sum(np.abs(clipped - corrected)))
    corrected = clipped
    total = corrected.sum()
    if total > 0.0:
        corrected = corrected / total
    return corrected, {
        "raw_norm": raw_norm,
        "clip_amount": clip_amount,
        "cond": float(np.linalg.cond(calibration)),
    }


def corrected_expectation(shots=30000, seed=1234):
    """Shot-based corrected <Z> after mitigation."""
    calibration = calibrate(shots, seed)
    counts = sample_target(shots, seed)
    corrected, diagnostics = mitigate(counts, calibration)
    return 2.0 * float(corrected[0]) - 1.0, diagnostics


def run_mitigation(shots=30000, seed=1234, tolerance=0.03):
    """Full mitigation run with the propagated statistical tolerance
    (3 sigma for 30000 shots is about 0.016; 0.03 is conservative)."""
    proof = exact_algebra_proof()
    calibration = calibrate(shots, seed)
    counts = sample_target(shots, seed)
    corrected, diagnostics = mitigate(counts, calibration)
    z_corrected = 2.0 * float(corrected[0]) - 1.0
    measured = np.array([counts.get("0", 0), counts.get("1", 0)], dtype=float)
    z_raw = 2.0 * float(measured[0] / measured.sum()) - 1.0
    return {
        "z_corrected": float(z_corrected),
        "z_raw": float(z_raw),
        "z_true": float(TARGET_EXPECTATION),
        "z_algebra": float(proof["recovered_z"]),
        "tolerance": float(tolerance),
        "condition_number": condition_number(),
        "diagnostics": diagnostics,
        "passed": abs(z_corrected - TARGET_EXPECTATION) <= tolerance,
    }


def main():
    result = run_mitigation()
    print("raw <Z> =", result["z_raw"])
    print("corrected <Z> =", result["z_corrected"])
    print("target cos(2.0) =", result["z_true"])
    print("algebra recovery =", result["z_algebra"])
    print("cond(A) =", result["condition_number"])
    print("diagnostics =", result["diagnostics"])
    proof = exact_algebra_proof()
    assert (
        abs(proof["recovered_z"] - TARGET_EXPECTATION) < 1e-12
    ), "exact algebra must recover cos(2.0)"
    assert result["condition_number"] < 20.0, "assignment matrix ill-conditioned"
    assert result["passed"], "shot-based corrected Z deviates beyond tolerance"
    # the propagated statistical tolerance is the guarantee, not "looks better
    # than one noisy draw": the shot noise sigma is ~0.005 at 30000 shots, so
    # a 0.03 window is roughly 6 sigma


if __name__ == "__main__":
    main()
