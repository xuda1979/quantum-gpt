"""Bell state on the local Braket simulator with parity verification.

Uses the AWS-local `braket.devices.LocalSimulator` so the test does not
require AWS credentials.
"""

from braket.circuits import Circuit
from braket.devices import LocalSimulator


def bell_circuit() -> Circuit:
    """Return a Bell-state circuit: H on q0, CNOT(0,1)."""
    c = Circuit()
    c.h(0)
    c.cnot(0, 1)
    return c


def sample_bell_state(shots: int = 1000, seed: int | None = None) -> dict:
    """Run the Bell circuit on the local simulator and return a histogram."""
    dev = LocalSimulator()
    c = bell_circuit()
    if seed is not None:
        # Braket LocalSimulator seed via kwargs is backend-dependent; wrap defensively.
        try:
            result = dev.run(c, shots=shots, seed=seed).result()
        except TypeError:
            result = dev.run(c, shots=shots).result()
    else:
        result = dev.run(c, shots=shots).result()
    counts = result.measurement_counts
    return dict(counts)


def parity_check(bitstring: str) -> int:
    """Return the parity (XOR) of a bitstring."""
    p = 0
    for b in bitstring:
        p ^= int(b)
    return p


if __name__ == "__main__":
    counts = sample_bell_state(shots=500)
    print("Bell state counts:", counts)
    print("All parities even:", all(parity_check(bs) == 0 for bs in counts))
