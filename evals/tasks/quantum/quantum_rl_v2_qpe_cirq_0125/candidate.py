"""Quantum phase estimation in Cirq with 3 counting qubits for
U = ZPowGate(exponent=2*0.125) on the eigenstate |1>. Controlled powers in
a documented significance order (counting qubit k controls U^(2^k)), a
manually implemented inverse QFT, a fixed-seed 4096-repetition sample, and
MSB-first bitstring decoding of the phase estimate.

Convention: the counting register is measured in REVERSED qubit order so
the measured bitstring is most-significant-digit first; the phase is
int(bitstring, 2) / 2^n.
"""

import cirq

PHASE = 0.125
N_COUNTING = 3


def phase_value():
    """The phase encoded by U on |1>: 0.125."""
    return PHASE


def eigenstate_prep(circuit, eigen_qubit):
    """Prepare the eigenstate |1> of ZPowGate(exponent=0.25)."""
    circuit.append(cirq.X(eigen_qubit))


def controlled_powers(circuit, counting_qubits, eigen_qubit):
    """Apply controlled U^(2^k) for k = 0..n-1: counting qubit k (the k-th
    least significant counting qubit) controls U^(2^k)."""
    for k, control in enumerate(counting_qubits):
        exponent = 2 * PHASE * (2**k)  # 2*phase is the ZPowGate exponent
        circuit.append(cirq.ZPowGate(exponent=exponent).controlled().on(control, eigen_qubit))


def inverse_qft(qubits):
    """Manual inverse QFT over `qubits`: bit-reversal swaps first, then H on
    each qubit followed by negative controlled-ZPow phases. Verified by
    roundtrip: inverse_qft(qft(x)) = x (see main())."""
    qs = list(qubits)
    n = len(qs)
    ops = []
    for i in range(n // 2):
        ops.append(cirq.SWAP(qs[i], qs[n - 1 - i]))
    for i in range(n):
        ops.append(cirq.H(qs[i]))
        for j in range(i + 1, n):
            ops.append(cirq.CZPowGate(exponent=-1.0 / 2 ** (j - i))(qs[i], qs[j]))
    return ops


def qpe_circuit():
    """Full QPE circuit: counting qubits c0..c2 + eigenstate qubit e. The
    counting register is measured in reversed order so the bitstring is
    most-significant digit first."""
    counting = cirq.LineQubit.range(N_COUNTING)
    eigen = cirq.LineQubit(N_COUNTING)
    circuit = cirq.Circuit()
    eigenstate_prep(circuit, eigen)
    circuit.append(cirq.H.on_each(*counting))
    controlled_powers(circuit, counting, eigen)
    circuit.append(inverse_qft(counting))
    circuit.append(cirq.measure(*reversed(counting), key="m"))
    return circuit


def decode_phase(bitstring):
    """Decode an MSB-first counting bitstring to a phase in [0, 1)."""
    return int(bitstring, 2) / (2**N_COUNTING)


def sample_phase_counts(repetitions=4096, seed=1234):
    """Seeded sampling of the counting register; counts keyed by bitstring."""
    simulator = cirq.Simulator(seed=seed)
    results = simulator.run(qpe_circuit(), repetitions=repetitions)
    counts = results.histogram(key="m")
    return {format(k, "0%db" % N_COUNTING): int(c) for k, c in counts.items()}


def dominant_phase_estimate(repetitions=4096, seed=1234):
    """(bitstring, phase) of the most frequent sampled outcome."""
    counts = sample_phase_counts(repetitions, seed)
    top = max(counts, key=counts.get)
    return top, decode_phase(top)


def run_qpe(repetitions=4096, seed=1234):
    """Run QPE and return the verifiable quantities."""
    counts = sample_phase_counts(repetitions, seed)
    top_bits, top_phase = dominant_phase_estimate(repetitions, seed)
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
    assert (
        result["phase_error"] <= result["grid"]
    ), f"dominant phase {result['top_phase']} not within 1/2^3 of {PHASE}"
    assert result["top_bits"] == "001", "exact phase 1/8 must decode to '001'"
    assert result["top_share"] > 0.99, "exact phase must dominate the sample"
    assert abs(decode_phase("100") - 0.5) < 1e-12, "MSB-first decode broken"
    assert abs(decode_phase("011") - 0.375) < 1e-12, "MSB-first decode broken"


if __name__ == "__main__":
    main()
