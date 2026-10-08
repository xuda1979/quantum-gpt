"""Quantum phase estimation in Qiskit with 3 counting qubits for
U = P(2*pi*0.375) on the eigenstate |1>. Controlled U^(2^k) gates, a manual
inverse QFT, 2048 seeded shots, and an explicitly tested MSB-first bit
order conversion. The phase 0.375 = 3/8 is exactly representable with 3
counting qubits, so the dominant estimate must equal 0.375 exactly."""

import math

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

PHASE = 0.375
N_COUNTING = 3


def phase_value():
    """The phase encoded by U = P(2*pi*0.375) on |1>: 0.375."""
    return PHASE


def controlled_powers(qc):
    """Apply controlled U^(2^k) for k = 0..n-1: counting qubit k controls
    U^(2^k), i.e. a CP(2*pi*PHASE*2^k) from counting qubit k onto the
    eigenstate qubit (the last qubit)."""
    eigen = N_COUNTING
    for k in range(N_COUNTING):
        qc.cp(2.0 * math.pi * PHASE * (2**k), k, eigen)


def inverse_qft(qc, n=N_COUNTING):
    """Manual n-qubit inverse QFT on the first n qubits: bit-reversal swaps,
    then H and negative controlled-phase rotations."""
    for i in range(n // 2):
        qc.swap(i, n - 1 - i)
    for i in range(n):
        qc.h(i)
        for j in range(i + 1, n):
            qc.cp(-np.pi / 2 ** (j - i), i, j)


def qpe_circuit():
    """Full QPE circuit: 3 counting qubits + 1 eigenstate qubit |1>, H on
    the counting register, controlled powers, inverse QFT, measurement of
    the counting register."""
    qc = QuantumCircuit(N_COUNTING + 1, N_COUNTING)
    qc.x(N_COUNTING)  # eigenstate |1>
    qc.h(range(N_COUNTING))
    controlled_powers(qc)
    inverse_qft(qc)
    qc.measure(range(N_COUNTING), range(N_COUNTING))
    return qc


def decode_phase(bitstring):
    """Decode an MSB-first counting bitstring (first char = most significant
    digit) to a phase in [0, 1)."""
    return int(bitstring, 2) / (2**N_COUNTING)


def sample_counts(shots=2048, seed=1234):
    """Seeded AerSimulator sampling; counts keyed by 3-bit bitstrings."""
    backend = AerSimulator(seed_simulator=seed)
    return backend.run(qpe_circuit(), shots=shots).result().get_counts()


def dominant_phase_estimate(shots=2048, seed=1234):
    """(bitstring, phase) of the most frequent sampled outcome."""
    counts = sample_counts(shots, seed)
    top = max(counts, key=counts.get)
    return top, decode_phase(top)


def run_qpe(shots=2048, seed=1234):
    """Run QPE and return the verifiable quantities."""
    counts = sample_counts(shots, seed)
    top_bits, top_phase = dominant_phase_estimate(shots, seed)
    total = sum(counts.values())
    return {
        "phase": PHASE,
        "top_bits": top_bits,
        "top_phase": top_phase,
        "phase_error": abs(top_phase - PHASE),
        "top_share": counts[top_bits] / float(total),
        "counts": counts,
        "grid": 1.0 / (2**N_COUNTING),
    }


def main():
    result = run_qpe()
    print("phase =", result["phase"])
    print("dominant bits =", result["top_bits"])
    print("dominant estimate =", result["top_phase"])
    print("top share =", result["top_share"])
    # explicitly tested bit-order conversion
    assert abs(decode_phase("011") - 0.375) < 1e-12, "011 must decode to 3/8"
    assert abs(decode_phase("100") - 0.5) < 1e-12, "100 must decode to 1/2"
    assert abs(decode_phase("111") - 0.875) < 1e-12, "111 must decode to 7/8"
    assert (
        result["phase_error"] <= result["grid"]
    ), f"dominant phase {result['top_phase']} not within 1/2^3 of {PHASE}"
    assert result["top_bits"] == "011", "exact phase 3/8 must decode to '011'"
    assert result["top_share"] > 0.99, "exact phase must dominate the sample"


if __name__ == "__main__":
    main()
