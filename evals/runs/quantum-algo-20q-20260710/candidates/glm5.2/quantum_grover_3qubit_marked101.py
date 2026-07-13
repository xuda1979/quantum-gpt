from qiskit import QuantumCircuit, transpile
from qiskit.primitives import StatevectorSampler

sampler = StatevectorSampler()
job = sampler.run(qc, shots=1000)
result = job.result()
counts = result[0].data.meas.get_counts()

Actually in V2, the result contains PubResult objects. result[0].data.<register>.get_counts(). If the circuit has a classical register named "meas", then result[0].data.meas.get_counts(). If no name, maybe result[0].data.cr.get_counts()? Let's inspect memory.

Example from Qiskit docs for SamplerV2:

from qiskit.primitives import StatevectorSampler
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0,1)
qc.measure_all()
sampler = StatevectorSampler()
job = sampler.run([qc], shots=1000)
result = job.result()
counts = result[0].data.meas.get_counts()
print(counts)

Actually measure_all() adds a classical register named "meas". So result[0].data.meas.get_counts() works.

But maybe result[0].data["meas"].get_counts(). Let's check. In V2, PubResult.data is a DataBin object. You can access by attribute: data.meas.get_counts(). Or data["meas"].get_counts(). Both should work.

We can use measure_all() and then get counts via result[0].data.meas.get_counts().

Alternatively, if we use QuantumCircuit(3,3) and measure(q, c), the classical register default name is "c"? In QuantumCircuit(3,3), classical register name is "c" maybe? Actually QuantumCircuit(3,3) creates ClassicalRegister(3, 'c'). Then result[0].data.c.get_counts(). But to be safe, use measure_all() and attribute 'meas'.

Need to print most likely bitstring and probability. The counts are bitstrings with keys like '101'. Need to find max count, probability = max_count/1000 rounded to 3 decimals.

But note: Qiskit bitstrings are printed with the classical bits in order of the classical register. If we measure qubits [0,1,2] into classical bits [0,1,2] using measure_all(), the bitstring order: Qiskit uses little-endian? Let's recall. In Qiskit, the statevector order is little-endian: qubit 0 is the least significant bit (rightmost) in the bitstring. When measuring, counts keys are bitstrings where the leftmost bit corresponds to classical bit with highest index? Actually standard: counts string is ordered as c_{n-1}...c_0, where c_0 is the least significant bit (from qubit 0). So if we measure qubit 0 to classical bit 0, the bitstring's rightmost char is qubit 0. For state |101> in Dirac notation |q2 q1 q0>? Wait, in Qiskit, |101> usually means qubit 2 is 1, qubit 1 is 0, qubit 0 is 1? Let's be careful.

The problem says "find the marked state |101>" and oracle: X on q1 (the bit that is 0 in |101>). So in |101>, the middle bit (q1) is 0. That suggests the bitstring is ordered as q2 q1 q0? Actually |101> written as three bits: first bit is q0? In many textbooks, |101> means qubit 0 = 1, qubit 1 = 0, qubit 2 = 1, with q0 leftmost? Wait, standard Dirac notation for multi-qubit states: |b_{n-1} ... b_0> where b_0 is the state of qubit 0? In Qiskit, the label |101> corresponds to qubit 2=1, qubit 1=0, qubit 0=1 because Qiskit uses little-endian indexing. But the prompt says "X on q1 (the bit that is 0 in |101>)". If |101> bits are read left-to-right as q0 q1 q2? Then q0=1, q1=0, q2=1. So q1 is indeed the bit that is 0. That suggests they are using the convention that the bitstring's leftmost char is q0, next is q1, rightmost is q2. But Qiskit's counts may output in the opposite order. Need to be careful to get the printed most-likely bitstring correct.

The oracle description: "X on q1 (the bit that is 0 in |101>), then CCZ on all 3 qubits (implemented as H on q2, MCX with controls [q0, q1] targeting q2, H on q2), then X on q1 to uncompute."

This oracle marks state |101>. Let's analyze. The oracle should flip phase of |101>. They propose: X on q1 (so |101> becomes |111>), then CCZ on all 3 qubits flips phase of |111>, then X on q1 uncomputes. So indeed the marked state is the one where after X on q1, all qubits are 1. That means original state has q0=1, q1=0, q2=1. So the bitstring |101> corresponds to q0=1, q1=0, q2=1 (left-to-right = q0 q1 q2). This is the textbook convention (qubit 0 is leftmost). Qiskit's internal statevector ordering is little-endian, but the circuit drawing and gate labels use q0 as the top wire. The counts bitstrings from Qiskit are typically printed with the most significant bit corresponding to the highest-index classical bit, which is often q2 if measuring q0->c0, q1->c1, q2->c2. Let's verify.

In Qiskit, if you do:

qc = QuantumCircuit(3)
qc.x(0)
qc.x(2)
qc.measure_all()
sampler.run...
counts: {'101': 1000}? Or {'110': 1000}? Let's recall from experience. If you initialize a state with x on q0 and x on q2, the statevector is |101> in Qiskit's convention? Actually the statevector index for q0=1, q1=0, q2=1 is binary 101 (q2 q1 q0 = 1 0 1) = decimal 5. The counts key for that state should be '101' because Qiskit prints the bitstring as the binary representation with qubit 0 as the least significant bit (rightmost). So counts key '101' corresponds to q2=1, q1=0, q0=1. That matches the state where q0=1, q1=0, q2=1. So the counts key '101' is exactly what we want, even though it's displayed as q2 q1 q0. Wait, the string '101' has leftmost char = q2, middle = q1, rightmost = q0. But the marked state |101> in the problem has q0=1, q1=0, q2=1. In Qiskit's counts, that is also '101' because q2=1, q1=0, q0=1. So the string is the same! The only difference is interpretation of which char corresponds to which qubit, but the string '101' is identical. So if the algorithm works, the most likely bitstring in counts should be '101'. Good.

But let's double-check. If we apply X on q1 (the middle qubit) in the oracle, that is X(1). The CCZ on all 3 qubits implemented as H on q2, MCX controls [q0,q1] target q2. This is a standard decomposition of CCZ with q2 as target. It flips phase of |111>. After X on q1, the state |101> (q0=1,q1=0,q2=1) becomes |111>. So oracle marks it. Good.

Now diffusion: H on all, X on all, CCZ on all (same construction), X on all, H on all. That's the standard Grover diffusion operator using CCZ. It should work.

We need 2 Grover iterations. For 3 qubits, optimal number is about pi/4 * sqrt(N/M) = pi/4 * sqrt(8) ≈ 2.22. So 2 iterations is fine. The marked state should have high probability. Let's compute expected probability after 2 iterations. For M=1, N=8, after k iterations amplitude ~ sin((2k+1)θ), where sin θ = sqrt(M/N)=1/sqrt(8). θ = arcsin(0.35355)=0.361367 rad. After k=2: (5θ)=1.8068 rad, sin=0.972. So probability ~0.945? Actually amplitude = sin(5θ) ≈ sin(1.8068) ≈ 0.972. Probability ~0.945. With 1000 shots, probability printed should be around 0.945. But due to StatevectorSampler (ideal) with 1000 shots, counts will be random; probability could be e.g., 0.95. But they might want deterministic? StatevectorSampler with shots returns random samples. The most likely should be '101' with high probability. The exact rounded probability will vary per run. The prompt says "prints the most-likely bitstring and its probability." So it's okay to be stochastic. But maybe they expect the exact probability from statevector? Wait, they explicitly say StatevectorSampler (1000 shots). So it's sampling. The output will vary. But the problem likely checks that the program is correct, not the exact output. However, they say "Output exactly: Most likely: ... Probability: ...". In an evaluation, they might run the program and compare output? If it's random, they can't compare exact probability. Maybe they just check format. Or maybe they expect to use the sampler's result and compute probability as count/1000, which will be random but close. Alternatively, maybe they expect to use StatevectorSampler to get quasi-probabilities? Let's think.

StatevectorSampler in Qiskit can also return counts. It samples. With 1000 shots, the most likely bitstring will almost certainly be '101'. Probability will be around 0.94. Rounding to 3 decimals will vary. The evaluation might not require exact probability. But the instruction "Output exactly:" might be a template. We'll follow it.

Need to ensure we import correct modules. Qiskit version might be 1.0+. Let's write code that works with Qiskit 1.0.

Potential issues:
- MCX gate: In Qiskit, we can use qc.mcx([0,1], 2) or qc.ccx(0,1,2) since it's 2 controls. The prompt says MCX with controls [q0, q1] targeting q2. So use qc.mcx([0,1], 2).
- CCZ implementation: H on q2, MCX controls [0,1] target 2, H on q2.
- Grover iterations: 2 times.
- Diffusion: H on all, X on all, CCZ on all, X on all, H on all. The CCZ same construction: H on q2, MCX [0,1] target 2, H on q2. Note: After H on all and X on all, the diffusion operator should be a reflection about |s>. The standard diffusion is H^n (2|0><0| - I) H^n. And (2|0><0| - I) is implemented as X^n (2|1><1| - I) X^n? Actually the standard is: apply X to all, then multi-controlled Z (which flips phase of |11...1>), then X to all. Then H. So yes, the described diffusion is correct.
- Need to apply H to all at start of Grover to create uniform superposition. The prompt doesn't explicitly mention initial H, but Grover's algorithm requires it. The description of diffusion includes H on all, but we need initial Hadamards. Should we include them? The problem says "Implements Grover's algorithm... Uses 2 Grover iterations." Grover's algorithm includes initial Hadamard on all qubits. We must include it. The diffusion operator also starts and ends with H. So the circuit is: H on all; [oracle; diffusion] repeated 2 times; measure.

Let's verify the oracle and diffusion with initial H.

Circuit:
q = QuantumRegister(3)
qc = QuantumCircuit(q)
qc.h([0,1,2])
for _ in range(2):
    # Oracle
    qc.x(1)
    # CCZ
    qc.h(2)
    qc.mcx([0,1], 2)
    qc.h(2)
    qc.x(1)
    # Diffusion
    qc.h([0,1,2])
    qc.x([0,1,2])
    # CCZ
    qc.h(2)
    qc.mcx([0,1], 2)
    qc.h(2)
    qc.x([0,1,2])
    qc.h([0,1,2])
qc.measure_all()

Wait, the diffusion: "H on all, X on all, CCZ on all (same construction), X on all, H on all." The CCZ on all is the same as oracle's CCZ. So yes.

But note: In the diffusion, the CCZ is on all 3 qubits. The construction uses H on q2, MCX controls [q0,q1] target q2. That's a CCZ with q2 as target. It works.

Now, after 2 iterations, measure.

Let's test mentally if the circuit indeed amplifies |101>. We can simulate the statevector to ensure. Let's do a quick analytical or semi-analytical check.

Initial state: |s> = (1/√8) Σ_x |x>.
Oracle: flips phase of |101> (q0=1,q1=0,q2=1). In Qiskit's ordering, that's basis index 5 (binary 101). So after oracle: |ψ1> = |s> - 2/√8 |101>.
Diffusion: reflects about |s>. After one iteration, amplitude of |101> increases.

After 2 iterations, should be high.

But there is a subtlety: The oracle uses X on q1. In Qiskit, q1 is the middle qubit. The marked state |101> in Qiskit counts is index 5 (binary 101 where q2 is MSB). The q1 bit is 0. So X on q1 flips it to 1. The state becomes |111> (index 7). CCZ flips phase of |111>. Then X on q1 returns to |101>. So oracle marks index 5. Good.

The diffusion operator: H, X, CCZ, X, H. The CCZ flips phase of |111>. After X on all, the state |000> becomes |111>. So the operator (X⊗X⊗X) CCZ (X⊗X⊗X) = CZ? Actually it implements -I on |000> and identity on others? Let's see: CCZ flips phase of |111>. X on all maps |000>↔|111>. So the combined operator is a diagonal phase flip on |000> (since |000> -> X -> |111> -> CCZ flips -> |111> -> X -> |000> with phase -1). For any other state, it's not all ones after X, so no phase flip. So the operator is 2|000><000| - I (phase flip on |000>). Then H on both sides gives the diffusion operator. So it's correct.

Now, the code. Need to be careful with imports for State
