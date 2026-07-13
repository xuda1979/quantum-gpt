def heavy_output_threshold(n_qubits: int) -> float:
    """Return the median probability threshold for heavy output detection.

    For a uniformly random n-qubit circuit, ideal output probabilities are
    approximately uniform on 2^n outcomes. The median probability is 1/2^n,
    and heavy outputs are those with probability > median. The threshold
    here is the median probability (used as the heavy/light boundary).
    """
    if n_qubits < 1:
        raise ValueError("n_qubits must be >= 1")
    return 1.0 / (1 << n_qubits)


def is_heavy_output(probability: float, threshold: float) -> bool:
    """Return True if `probability` exceeds the heavy-output threshold."""
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be in [0, 1]")
    return probability > threshold


def heavy_output_probability(probabilities: list[float]) -> float:
    """Return the fraction of probabilities strictly above the median.

    For an ideal random circuit, this fraction is ~0.5 + (1 - 2/ln(2))/2^n
    which approaches 0.5 from above as n grows; here we just compute the
    actual fraction above the median value of the list.
    """
    if not probabilities:
        raise ValueError("probabilities must be non-empty")
    if any(not 0.0 <= p <= 1.0 for p in probabilities):
        raise ValueError("probabilities must be in [0, 1]")
    sorted_p = sorted(probabilities)
    n = len(sorted_p)
    median = sorted_p[n // 2] if n % 2 == 1 else (sorted_p[n // 2 - 1] + sorted_p[n // 2]) / 2.0
    heavy = sum(1 for p in probabilities if p > median)
    return heavy / n


def quantum_volume_is_achieved(
    n_qubits: int, observed_hop: float, confidence_threshold: float = 0.625
) -> bool:
    """Decide whether Quantum Volume 2^n is achieved.

    Convention: QV 2^n is achieved if the observed heavy-output probability
    exceeds the threshold > 0.5 with the standard 2-sigma confidence, using
    the canonical boundary 5/8 = 0.625.
    """
    if n_qubits < 1:
        raise ValueError("n_qubits must be >= 1")
    if not 0.0 <= observed_hop <= 1.0:
        raise ValueError("observed_hop must be in [0, 1]")
    return observed_hop > confidence_threshold
