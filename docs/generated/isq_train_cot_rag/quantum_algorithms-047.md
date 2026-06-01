# ISQ training COT RAG corpus: quantum_algorithms shard 47

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/112

- task_id: `isqExpand/algo/112`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `phase_manipulation`, `basis_change`
- source: `isq_expansion`
- dataset_index: `4028`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[3];

procedure main() {
    X(q[2]);
    H(q[0]); H(q[1]); H(q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. X(q[2]): ancilla |1>
2. H on all: q[0],q[1] -> |+,+>, q[2] -> |->
3. CNOT(q[0],q[2]): phase (-1)^{x0}
4. CNOT(q[1],q[2]): phase (-1)^{x1}
   Combined: (-1)^{x0+x1} for s=11
5. H on input: |11> = index 3

Expected: [0,0,0,1]

### Reference answer

{'predicted_probs': [0.0, 0.0, 0.0, 1.0], 'explanation': "This is a Bernstein-Vazirani circuit. The ancilla q[2] is prepared in |1> then H'd to |->. Both CNOT(q[0],q[2]) and CNOT(q[1],q[2]) implement f(x) = x0 XOR x1, the inner product with s=11. After H on the input register, we measure |s>=|11> with certainty. |11> = index 3 in 2-qubit measurement."}

## isqTrain/1415

- task_id: `isqTrain/1415`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4659`

### Prompt

Implement a quantum circuit in isQ: Apply the 2-qubit Quantum Fourier Transform to the input state |10> and measure all qubits.

### Chain-of-thought reasoning

Step 1: Understand the task.
- Apply a 2-qubit Quantum Fourier Transform to the input state |10> and measure all qubits.
- The input to QFT is |10>, which is state |2> in decimal.
- The output of QFT on a 2-qubit system is an equal superposition of |00>, |01>, |10>, |11>.
- Wait, QFT on |10> (which is $|2\rangle$ out of $N=4$) gives $\frac{1}{2} \sum_{k=0}^{3} e^{2\pi i 2 k / 4} |k\rangle = \frac{1}{2} \sum_{k=0}^{3} e^{i \pi k} |k\rangle = \frac{1}{2} (|0\rangle - |1\rangle + |2\rangle - |3\rangle) = \frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |11\rangle)$.
- In the isQ code provided, the initial state is |10> (q[0] is flipped to 1, q[1] is 0).
- Let's check the reference isQ code's QFT structure:
  - `X(q[0]);` -> state is |10>
  - `H(q[1]);` -> state is $\frac{1}{\sqrt{2}}(|10\rangle + |11\rangle)$
  - `ctrl S(q[0], q[1]);` -> Wait, standard QFT applies controlled-R2 from q[0] to q[1]... actually standard QFT applies H on q[1], then controlled-S on q[1] with control q[0]?
  - Wait, standard QFT:
    Start: |10>
    Apply H on q[1]: (q[1] is 0) -> $\frac{1}{\sqrt{2}}(|10\rangle + |11\rangle)$
    Apply ctrl S on q[1] controlled by q[0]. Since q[0] is |1>, it applies S to q[1]. $|0\rangle \to |0\rangle$, $|1\rangle \to i|1\rangle$. -> $\frac{1}{\sqrt{2}}(|10\rangle + i|11\rangle)$.
    Apply H on q[0]: q[0] is |1> -> $\frac{1}{2}(|00\rangle - |01\rangle + i|10\rangle - i|11\rangle)$
    Apply swap (three-CNOT decomposition)(q[0], q[1]): $\frac{1}{2}(|00\rangle - |10\rangle + i|01\rangle - i|11\rangle)$
    Wait, is this right? The QFT of $|2\rangle$ should be $\frac{1}{2}(|0\rangle - |1\rangle + |2\rangle - |3\rangle)$. In isQ bit ordering, $|2\rangle$ is |10>, $|1\rangle$ is |01>, $|3\rangle$ is |11>.
    Wait, let's re-evaluate QFT of $|2\rangle$:
    $\frac{1}{2} (|0\rangle + e^{i \pi 0 \cdot 2 / 4} |0\rangle ... )$. Wait, QFT is $|x\rangle \to \frac{1}{\sqrt{N}} \sum_{y=0}^{N-1} e^{2\pi i x y / N} |y\rangle$.
    For x=2, N=4:
    y=0 (|00>): phase 0
    y=1 (|01>): $e^{i \pi} = -1$
    y=2 (|10>): $e^{2 i \pi} = 1$
    y=3 (|11>): $e^{3 i \pi} = -1$
    So $\frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |11\rangle)$.
    Let's check my manual circuit again.
    Start: |10>
    H(q[1]): $\frac{1}{\sqrt{2}}(|10\rangle + |11\rangle)$
    ctrl S(q[0], q[1]): $S|0\rangle=|0\rangle, S|1\rangle=i|1\rangle$. Controlled by q[0] (which is 1). So it adds phase $i$ to the |11> component. Result: $\frac{1}{\sqrt{2}}(|10\r

## isqTrain/2827

- task_id: `isqTrain/2827`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_for_loop`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2766`

### Prompt

Implement the following in isQ: creates a 5-qubit GHZ state. Apply H to the first qubit, then chain CNOT gates to entangle all 5 qubits. Measure all qubits.

Requirements:
- Declare `qbit q[5];` at global scope.
- Use `procedure main()` as entry point.
- Measure all 5 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a 5-qubit GHZ state, the maximally entangled superposition (|00000⟩ + |11111⟩)/√2.
2. **Qubits**: 5 qubits declared globally (`qbit q[5]`), all 5 are measured at the end.
3. **State evolution**:
   - Start: |00000⟩
   - H(q[0]): (|00000⟩ + |10000⟩)/√2 — puts q[0] in |+⟩
   - CNOT(q[0], q[1]): (|00000⟩ + |11000⟩)/√2 — entangles q[1] with q[0]
   - CNOT(q[1], q[2]): (|00000⟩ + |11100⟩)/√2 — chain continues
   - CNOT(q[2], q[3]): (|00000⟩ + |11110⟩)/√2
   - CNOT(q[3], q[4]): (|00000⟩ + |11111⟩)/√2 — full GHZ state achieved
4. **Expected probabilities**: The final state is an equal superposition of |00000⟩ and |11111⟩, so measurement yields |00000⟩ with probability 0.5 and |11111⟩ with probability 0.5.

## isqTrain/2995

- task_id: `isqTrain/2995`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1497`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    Z(q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, step-by-step quantum circuit analysis for an isQ program. The analysis should use Dirac notation and end with the predicted probability distribution.

2.  **Analyze the isQ Code:**
    *   `qbit q[2];`: 2 qubits initialized to $|00\rangle$.
    *   `H(q[0]);`: Apply Hadamard to qubit 0.
        *   State: $|0\rangle \xrightarrow{H} \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$. Full state: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    *   `CNOT(q[0], q[1]);`: Control=q[0], Target=q[1].
        *   State: $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$. (Bell state)
    *   `Z(q[1]);`: Apply Pauli-Z to qubit 1.
        *   State: $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) \otimes |0\rangle$? Wait, Z applies to the second qubit.
        *   $|00\rangle \to |00\rangle$, $|11\rangle \to -|11\rangle$.
        *   State: $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$.
    *   `M(q[0]); M(q[1]);`: Measurement.
        *   Probabilities: $P(00) = |1/\sqrt{2}|^2 = 0.5$. $P(11) = |-1/\sqrt{2}|^2 = 0.5$. $P(01) = P(10) = 0$.

3.  **Draft the Analysis (incorporating rules):**
    *   Start with `## Circuit Analysis`.
    *   List operations: H(0), CNOT(0,1), Z(1).
    *   Evolution:
        *   Initial: $|00\rangle$
        *   H(0): $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$
        *   CNOT(0,1): $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$
        *   Z(1): $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$
    *   Final probabilities: $P(00) = 0.5, P(11) = 0.5$.

4.  **Refine for conciseness (3-8 lines target):**
    *   "1. Operations: H(0), CNOT(0,1), Z(1)."
    *   "2. Evolution: $|00\rangle \xrightarrow{H(0)} \frac{1}{\sqrt{2}}(|00\rangle + |10\rangle) \xrightarrow{CNOT} \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle) \xrightarrow{Z(1)} \frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$."
    *   "3. Final state: $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$."
    *   "4. Predicted probability distribution: {'00': 0.5, '11': 0.5}."

5.  **Check against Rules:**
    *   Output ONLY the analysis starting with "## Circuit Analysis": Yes.
    *   Do NOT include code blocks: Yes.
    *   End with the predicted probability distribution: Yes.
    *   Dirac notation used: Yes.
    *   Concise: Yes.

6.  **Final Polish:**
    ## Circuit Analysis
    1. Operations applied: H(q[0]), CNOT(q[0], q[1]), Z(q[1]).
    2. State evolution:
       - Initial: $|00\rangle$
       - H(0): $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$
       - CNOT(0,1): $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$
       - Z(1): $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$
    3. Final state before measurement: $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/4071

- task_id: `isqTrain/4071`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5071`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// QAOA MaxCut p=1 on 4-node complete graph
// gamma=0.500, beta=0.500
qbit q[4];

procedure main() {
    // Superposition
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    // Cost unitary
    // Edge (0,1)
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.500, q[1]);
    CNOT(q[0], q[1]);
    // Edge (0,2)
    CNOT(q[0], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[0], q[2]);
    // Edge (0,3)
    CNOT(q[0], q[3]);
    Rz(2.0 * 0.500, q[3]);
    CNOT(q[0], q[3]);
    // Edge (1,2)
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[1], q[2]);
    // Edge (1,3)
    CNOT(q[1], q[3]);
    Rz(2.0 * 0.500, q[3]);
    CNOT(q[1], q[3]);
    // Edge (2,3)
    CNOT(q[2], q[3]);
    Rz(2.0 * 0.500, q[3]);
    CNOT(q[2], q[3]);
    // Mixer
    Rx(2.0 * 0.500, q[0]);
    Rx(2.0 * 0.500, q[1]);
    Rx(2.0 * 0.500, q[2]);
    Ry(2.0 * 0.500, q[3]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: In the mixer section, `Ry(2.0 * 0.500, q[3])` is used instead of `Rx(2.0 * 0.500, q[3])`. In QAOA, the mixer unitary $U_M(\beta) = \prod_j e^{-i\beta X_j}$ requires $Rx(2\beta)$ on every qubit. The last qubit incorrectly received $Ry$ (rotation around $Y$) instead of $Rx$ (rotation around $X$).

2. **Fix**: Replace `Ry(2.0 * 0.500, q[3])` with `Rx(2.0 * 0.500, q[3])` so all four qubits receive the standard QAOA mixer.

3. **State evolution (corrected)**:
   - After Hadamards: $|+\rangle^{\otimes 4}$
   - Cost unitary: each edge $(i,j)$ applies $e^{-i\gamma Z_i Z_j}$ via CNOT-Rz-CNOT with $Rz(2\gamma)$, introducing phase differences between cut and uncut bitstrings.
   - Mixer $Rx(2\beta)$ on all four qubits rotates each around $X$, mixing amplitudes.
   - The symmetric application of $Rx$ to all qubits preserves the permutation symmetry of the complete graph, yielding equal probabilities for bitstrings of equal Hamming weight, with high probability on balanced cuts ($|0000\rangle$ and $|1111\rangle \approx 0.316$) and moderate probability on 2-2 splits ($\approx 0.058$), and very low probability on 3-1 splits ($\approx 0.002$).

## isqTrain/3427

- task_id: `isqTrain/3427`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `2824`

### Prompt

Code this in isQ: the 2-qubit Quantum Fourier Transform (QFT) in isQ.

The 2-qubit QFT maps computational basis states to the Fourier basis.
Circuit:
1. H(q[0])
2. Controlled-Rz(pi/2) from q[1] to q[0]
3. H(q[1])
4. SWAP q[0] and q[1]

Apply QFT to |00>. Then apply inverse QFT to return to |00>.
This tests the QFT + IQFT roundtrip.

Declare 2 global qubits, measure both. Expected: |00>.

### Chain-of-thought reasoning

Step 1: Understand the goal.
The user wants to implement a 2-qubit Quantum Fourier Transform (QFT) followed by its inverse (IQFT) in isQ.
This is a roundtrip test, meaning the initial state |00> should be returned to |00> at the end.

Step 2: Determine the QFT and IQFT circuit.
The 2-qubit QFT circuit consists of:
1. H(q[0])
2. Controlled-Rz(pi/2) from q[1] to q[0]. (Wait, the prompt says "from q[1] to q[0]", which means q[1] is control, q[0] is target).
Let's trace:
- H(q[0]) -> puts q[0] into |+>
- CRz(q[1] -> q[0]) -> controlled phase shift.
- H(q[1]) -> puts q[1] into |+>
- swap (three-CNOT decomposition)(q[0], q[1]) -> swaps the qubits.

The inverse QFT is the adjoint of the QFT:
1. swap (three-CNOT decomposition)(q[0], q[1])
2. H(q[1])
3. CRz(-pi/2) from q[1] to q[0]
4. H(q[0])

Wait, let me double check the CRz.
In the implementation:
Forward QFT:
H(q[0]);
ctrl Rz(pi/2, q[1], q[0]);
H(q[1]);
CNOT(q[0], q[1]); CNOT(q[1], q[0]); CNOT(q[0], q[1]);

Inverse QFT:
CNOT(q[0], q[1]); CNOT(q[1], q[0]); CNOT(q[0], q[1]);
H(q[1]);
ctrl Rz(-pi/2, q[1], q[0]);
H(q[0]);

Step 3: Write the reasoning.
- Goal: Apply a 2-qubit QFT followed by its inverse (IQFT) to verify the roundtrip returns the state to the original |00>.
- Qubits: 2 global qubits `q[2]`, both measured.
- State evolution:
  - Initialize to |00>.
  - Forward QFT applies H(0), CRz(q[1], q[0], pi/2), H(1), and swap (three-CNOT decomposition), transforming the state to the Fourier basis. Specifically, |00> -> |00> (ignoring global phase, QFT of |00> is |00> wait. Let's trace exactly).
  Wait, QFT on |00>.
  H(0): |0> -> 1/sqrt(2)(|0>+|1>) -> |00> goes to (|00> + |10>)/sqrt(2).
  CRz(q[1], q[0]): control is q[1], target is q[0]. Since q[1] is |0>, it does nothing!
  H(1): q[1] is |0> -> 1/sqrt(2)(|0>+|1>). State is (|00>+|01>+|10>+|11>)/2 = |++>.
  swap (three-CNOT decomposition): |++> remains |++>.
  Wait, if it's |++>, inverse QFT will bring it back to |00>.
  Let's trace Inverse QFT on |++>:
  - swap (three-CNOT decomposition)(|++>) = |++>.
  - H(1): |++> -> |+0>.
  - CRz(-pi/2): control is q[1] (which is |0>). Does nothing. State is |+0>.
  - H(0): |+0> -> |00>.
  So it perfectly returns to |00>.

- Expected probabilities: The final state is exactly |00>, so measurement yields |00> with probability 1.0.

Let's refine the reasoning.
1. Goal: Implement a 2-qubit QFT followed by its inverse (IQFT) to verify the roundtrip restores the initial state.
2. Qubits: 2 qubits `q[2]`, both measured.
3. Evolution: Start at |00>.
   - Forward QFT: H(0) creates (|00>+|10>)/√2. CRz(q[1]→q[0]) does nothing since q[1] is |0>. H(1) yields (|00>+|01>+|10>+|11>)/2 = |++>.
   - swap (three-CNOT decomposition) leaves |++> unchanged.
   - Inverse QFT: Reverse swap (three-CNOT decomposition) leaves |++>. H(1) maps it to |+0>. Reverse CRz does nothing. H(0) maps it back to |00>.
4. Probabilities: Since the state returns exactly to

## isqTrain/1351

- task_id: `isqTrain/1351`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_if_else`, `mid_circuit_measurement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `112`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

qbit u[1];
qbit anc1[1];
qbit anc0[1];

procedure main() {

    X(u[0]);

    H(anc1[0]);
    ctrl Z(anc1[0], u[0]);
    H(anc1[0]);
    int m1 = M(anc1[0]);

    H(anc0[0]);
    ctrl S(anc0[0], u[0]);

    if (m1 == 1) {
        Rz(-pi/4.0, anc0[0]);
    }
    H(anc0[0]);
    int m0 = M(anc0[0]);

}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step analysis of an isQ quantum program, predicting the probability distribution of the measurement outcomes.
2.  **Analyze the isQ program**:
    *   `qbit u[1]; anc1[1]; anc0[1];` -> 3 qubits: `u[0]`, `anc1[0]`, `anc0[0]`. Initial state: $|000\rangle$ (order: `u`, `anc1`, `anc0`? Let's check isQ global qubit indexing. Actually, the prompt says "Number of qubits measured: 2". `u[0]` is NOT measured. Only `anc1[0]` and `anc0[0]` are measured.
    *   Let's trace the state. Initial state: $|0\rangle_u |0\rangle_{anc1} |0\rangle_{anc0}$.
    *   `X(u[0]);` -> State is $|1\rangle_u |0\rangle_{anc1} |0\rangle_{anc0}$.
    *   `H(anc1[0]);` -> $|1\rangle \otimes |+\rangle \otimes |0\rangle$
    *   `ctrl Z(anc1[0], u[0]);` -> CZ between `anc1` (control) and `u` (target).
        Wait, CZ applies Z on `u` if `anc1` is $|1\rangle$. Since `u` is in $|1\rangle$, Z acts as -1.
        Let's be careful. $|1\rangle_u |0\rangle_{anc1} \to |1\rangle|-\rangle$? No, CZ applies a phase of -1 if both are 1. Since $u$ is always $|1\rangle$, CZ acts on `anc1` as Z. So $|+\rangle$ becomes $|-\rangle$.
        State: $|1\rangle_u |-\rangle_{anc1} |0\rangle_{anc0}$.
    *   `H(anc1[0]);` -> $|1\rangle_u |1\rangle_{anc1} |0\rangle_{anc0}$.
    *   `int m1 = M(anc1[0]);` -> Measurement of `anc1[0]`.
        It's in $|1\rangle$, so `m1 = 1` with probability 1.
        State collapses to $|1\rangle_u |1\rangle_{anc1} |0\rangle_{anc0}$.
    *   `H(anc0[0]);` -> $|1\rangle_u |1\rangle_{anc1} |+\rangle_{anc0}$.
    *   `ctrl S(anc0[0], u[0]);` -> CS gate. `anc0` is control, `u` is target.
        Since `u` is $|1\rangle$, CS applies S to `anc0` if `anc0` is 1.
        Wait, `ctrl S` means S is applied to `u[0]` if `anc0[0]` is 1. Since `u[0]` is $|1\rangle$, this is equivalent to applying S to `anc0[0]`. Wait, S applied to target if control is 1. Target is `u[0]`. If control is 1, $|1\rangle$ gets S applied? No, S acts on target. S on $|1\rangle$ is $i|1\rangle$. So CS puts a factor of $i$ on the $|11\rangle$ component of `anc0` and `u`. Since `u` is always 1, it puts $i$ on the $|1\rangle$ component of `anc0`.
        State: $|1\rangle_u |1\rangle_{anc1} \frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle)_{anc0}$.
    *   `if (m1 == 1) { Rz(-pi/4.0, anc0[0]); }`
        Since `m1 = 1` with probability 1, we always apply `Rz(-pi/4)`.
        Wait, `Rz(-pi/4)` applies a phase $e^{-i\pi/8}$ to $|0\rangle$ and $e^{i\pi/8}$ to $|1\rangle$.
        Let's check standard isQ Rz definition: $Rz(\theta) = \text{diag}(e^{-i\theta/2}, e^{i\theta/2})$.
        Let

### Reference answer

{'predicted_probs': {'2': 0.8535533905932738, '3': 0.1464466094067262}, 'explanation': 'Parametric variant of isqEval/496. Dimension: param_variant: pi2_to_pi4.'}

## isqTrain/3605

- task_id: `isqTrain/3605`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3839`

### Prompt

实现以下量子计算任务（使用isQ）：a 3-qubit Grover search algorithm that finds the target state |000> using 1 Grover iteration. The circuit should:
1. Initialize 3 qubits in uniform superposition with Hadamard gates
2. Apply an oracle that marks state |000> with a phase flip
3. Apply the Grover diffusion operator
4. Measure all 3 qubits
Use `deriving gate` for oracle and diffusion procedures.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement 3-qubit Grover search to find |000> using one iteration, maximizing its measurement probability.

**Qubits:** 3 qubits (q[0], q[1], q[2]), all measured.

**State Evolution:**
1. **Initialize:** |000⟩
2. **H⊗³:** → |s⟩ = (1/2√2)∑|x⟩, uniform superposition over all 8 basis states (each amplitude = 1/2√2)
3. **Oracle for |000⟩:** X gates map |000⟩↔|111⟩, multi-controlled CZ adds phase -1 to |111⟩, X gates undo mapping. Result: |s'⟩ = (1/2√2

## isqTrain/4843

- task_id: `isqTrain/4843`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `quantum_counting`, `interference`
- source: `isq_train_cot`
- dataset_index: `4871`

### Prompt

实现以下量子计算任务（使用isQ）：implementing the diffusion operator as a named procedure on 2 qubits. Start from X(q[0]) state (|10>), apply diffusion, measure.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a quantum circuit that implements the Grover diffusion operator on 2 qubits.

Let me trace through the circuit:

1. Initial state: |00⟩ (default)
2. After X(q[0]): |10⟩
3. Now apply diffusion operator:
   - The diffusion operator for n qubits is: 2|s⟩⟨s| - I, where |s⟩ is the uniform superposition
   - For 2 qubits, |s⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

   Step by step:
   a. H(q[0]), H(q[1]) on |10⟩:
      - H on q[0]: |10⟩ → (|0⟩ - |1⟩)/√2 ⊗ |0⟩ = (|00⟩ - |10⟩)/√2
      - H on q[1]: (|00⟩ - |10⟩)/√2 → (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
      
   b. X(q[0]), X(q[1]):
      - Flip both: (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2 → (|11⟩ + |10⟩ - |01⟩ - |00⟩)/2
      = -(|00⟩ + |01⟩ - |10⟩ - |11⟩)/2 = -(|00⟩ + |01⟩)/2 + (|10⟩ + |11⟩)/2
      
      Wait, let me be more careful. X|0⟩ = |1⟩ and X|1⟩ = |0⟩.
      
      (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
      After X on both:
      = (|11⟩ + |10⟩ - |01⟩ - |00⟩)/2
      = (-|00⟩ - |01⟩ + |10⟩ + |11⟩)/2
      
   c. CZ(q[0], q[1]): applies -1 phase when both are |1⟩
      (-|00⟩ - |01⟩ + |10⟩ + |11⟩)/2
      → (-|00⟩ - |01⟩ + |10⟩ - |11⟩)/2
      
   d. X(q[0]), X(q[1]):
      (-|00⟩ - |01⟩ + |10⟩ - |11⟩)/2
      → (-|11⟩ - |10⟩ + |01⟩ - |00⟩)/2
      = (-|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
      
   e. H(q[0]), H(q[1]):
      Need to apply H⊗2 to (-|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
      
      H⊗2|00⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
      H⊗2|01⟩ = (|00⟩ - |01⟩ + |10⟩ - |11⟩)/2
      H⊗2|10⟩ = (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
      H⊗2|11⟩ = (|00⟩ - |01⟩ - |10⟩ + |11⟩)/2
      
      Result: -(|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 + (|00⟩ - |01⟩ + |10⟩ - |11⟩)/2 - (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2 - (|00⟩ - |01⟩ - |10⟩ + |11⟩)/2
      
      Coefficients:
      |00⟩: -1 + 1 - 1 - 1 = -2
      |01⟩: -1 - 1 - 1 + 1 = -2
      |10⟩: -1 + 1 + 1 + 1 = 0... wait let me redo this
      
      Actually, let me compute H⊗2 applied to each basis state:
      
      H|0⟩ = (|0⟩ + |1⟩)/√2
      H|1⟩ = (|0⟩ - |1⟩)/√2
      
      H⊗2|00⟩ = [(|0⟩+|1⟩)/√2][(|0⟩+|1⟩)/√2] = (|00⟩+|01⟩+|10⟩+|11⟩)/2
      H⊗2|01⟩ = [(|0⟩+|1⟩)/√2][(|0⟩-|1⟩)/√2] = (|00⟩-|01⟩+|10⟩-|11⟩)/2
      H⊗2|10⟩ =

## isqExpand/algo/182

- task_id: `isqExpand/algo/182`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `grover_algorithm`, `diffusion_operator`, `multi_controlled_gates`, `ctrl_modifier`, `quantum_search`
- source: `isq_expansion`
- dataset_index: `5460`

### Prompt

The following isQ program implements one iteration of Grover's algorithm on 4 qubits, searching for the marked state |1010⟩. The diffusion operator is incorrect — it uses a simple CZ (2-qubit controlled-Z) instead of the required multi-controlled Z gate for 4 qubits. Fix the diffusion operator so that the algorithm correctly amplifies the probability of the marked state.

### Chain-of-thought reasoning

The 4-qubit Grover diffusion operator requires reflecting about the uniform superposition: H^4 (2|0><0| - I) H^4. The core of (2|0><0| - I) is implemented by: X on all qubits (maps |0000> to |1111>), then a phase flip on |1111> only, then X on all qubits again. To flip phase of |1111>, we need a Z gate on one qubit controlled by the other three: ctrl @[q[0],q[1],q[2]] Z(q[3]). The buggy code uses CZ(q[0],q[1]) which only requires q[0]=1 and q[1]=1, flipping phase of 4 states (|0011>,|0111>,|1011>,|1111>) instead of just |1111>. This fundamentally breaks the diffusion operator. For the marked state |1010> (q[3]=1,q[2]=0,q[1]=1,q[0]=0, index 10), after one correct Grover iteration: uniform amplitude is 1/4, oracle flips |1010> to -1/4, average becomes (15/4 - 1/4)/16 = 7/32, reflected amplitudes are 11/16 for |1010> and 3/16 for others, giving P(|1010>) = 121/256 = 0.47265625 and P(other) = 9/256 = 0.03515625 each.
