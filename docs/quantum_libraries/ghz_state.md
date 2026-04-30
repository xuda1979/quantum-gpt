# GHZ state and entanglement witness

## Concept
The Greenberger-Horne-Zeilinger (GHZ) state is a tripartite (or
n-partite) maximally entangled state. For three qubits:

|GHZ> = (|000> + |111>) / sqrt(2)

For n qubits the state is (|0...0> + |1...1>) / sqrt(2). It is the
canonical multi-partite entanglement resource.

## Amplitudes (n=3)
Indexed by big-endian (|000>, |001>, ..., |111>):

```
amp = 2 ** -0.5
ghz3 = [amp, 0, 0, 0, 0, 0, 0, amp]
```

## Reference circuit
1. H on qubit 0
2. CNOT(0, 1)
3. CNOT(1, 2)  (or CNOT(0, 2))

```python
def ghz_state(n: int) -> list[float]:
    amp = 2 ** -0.5
    state = [0.0] * (1 << n)
    state[0] = amp
    state[(1 << n) - 1] = amp
    return state
```

## Entanglement witness
A witness W is an observable with `Tr(W rho_separable) >= 0` for all
separable states and `Tr(W rho) < 0` for some entangled rho. A common
GHZ witness is

  W = 1/2 I - |GHZ><GHZ|

For the perfect GHZ state, <GHZ|W|GHZ> = 1/2 - 1 = -1/2 < 0, signalling
entanglement. Numerically the witness expectation can be computed as:

```python
def ghz_witness(state):
    # state is a length-2**n complex vector for n qubits
    n = (len(state)).bit_length() - 1
    amp = 2 ** -0.5
    target_first, target_last = 0, (1 << n) - 1
    overlap = abs(state[target_first].conjugate() * amp
                  + state[target_last].conjugate() * amp)
    fidelity = overlap ** 2
    return 0.5 - fidelity   # negative => entanglement detected
```

## Common pitfalls
- The "all-zero plus all-one" pattern only works in the computational
  basis with big-endian indexing.
- Using CNOT(0, 1) followed by CNOT(0, 2) is functionally equivalent to
  CNOT(0,1) then CNOT(1,2) for producing GHZ.
