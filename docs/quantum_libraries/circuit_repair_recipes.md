# Circuit repair and depth-optimization recipes

## Common micro-bugs in quantum candidate code

1. **Swapped control/target on CNOT**
   - Symptom: state vector probabilities mirror across qubits.
   - Fix: re-read protocol; control comes first in `cx(c, t)`.

2. **Missing H before measurement**
   - Symptom: superdense / teleportation tests fail because Bell-basis
     measurement was not performed.
   - Fix: the standard Bell-basis measurement is `CX(0, 1); H(0); measure`.

3. **Wrong endianness for amplitude lists**
   - Symptom: amplitudes look right for a relabelled state.
   - Fix: pin endianness once. For lists of 2^n complex numbers, prefer
     big-endian (qubit 0 = most significant bit).

4. **Float precision drift**
   - Symptom: `assertEqual` fails on `1/sqrt(2)` produced by repeated
     normalisation.
   - Fix: use `math.isclose` or `np.allclose` with `abs_tol=1e-9`.

5. **Missing alias / not raising on unknown gate**
   - Symptom: gate normalisation tests expect `ValueError` but the
     code returns the original token.
   - Fix: raise `ValueError(f"unknown gate: {gate}")` after the lookup.

## Depth optimization patterns
- Cancel adjacent pairs of self-inverse gates (HH, XX, CNOT-CNOT same wires).
- Merge consecutive single-qubit rotations: Rz(a) Rz(b) -> Rz(a+b).
- Use commutation rules to slide commuting gates past each other and
  expose more cancellations: e.g. `Rz` commutes with `CZ` on the same
  wires.
- Replace H Z H = X, H X H = Z when reducing surrounding context allows.

## Phase repair patterns
- Apply `np.mod(phases, 2 * np.pi)` before comparison.
- Convert between `exp(i * phi)` and `phi` carefully: use `np.angle` for
  the inverse.
- Phase pattern from QFT|x>: `phi_k = (2 * pi * x * k / N) mod 2*pi`.

## Checklist before returning candidate code
- [ ] Imports are present and minimal.
- [ ] Function signatures match the test's expectations exactly.
- [ ] Edge cases (empty list, n=0, p=0) are handled or explicitly raised.
- [ ] No unused parameters; no debug prints.
- [ ] No markdown fences in the final candidate file.
