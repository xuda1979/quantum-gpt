# ISQ training COT RAG corpus: quantum_algorithms shard 95

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3718

- task_id: `isqTrain/3718`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5125`

### Prompt

Help me write isQ code that QAOA (p=1) for the MaxCut problem on a 3-node star graph with edges [(0, 1), (0, 2)]. Use parameters gamma=0.500 and beta=0.500. The circuit:
1. Initialize all qubits in superposition
2. Apply cost unitary: for each edge, use CNOT-Rz-CNOT
3. Apply mixer: Rx(2*beta) on each qubit
4. Measure all 3 qubits

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a QAOA circuit for MaxCut on a 3-node star graph.

Let me trace through the circuit:

1. Initialize 3 qubits in |000>
2. Apply H to all: |+++> = (1/√8)(|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)

3. Cost unitary for edge (0,1): CNOT(0,1), Rz(1.0, q[1]), CNOT(0,1)
   - This implements exp(-i*gamma*Z0*Z1) = exp(-i*0.5*Z0*Z1)
   - The phase applied is: e^(-i*0.5) when qubits agree, e^(i*0.5) when they disagree

4. Cost unitary for edge (0,2): CNOT(0,2), Rz(1.0, q[2]), CNOT(0,2)
   - This implements exp(-i*gamma*Z0*Z2) = exp(-i*0.5*Z0*Z2)

5. Mixer: Rx(1.0) on each qubit

Let me calculate the predicted output more carefully.

Starting state: |000>

After H on all: |+++> = 1/2√2 * (|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)

For the cost unitary, each basis state |q0,q1,q2> gets a phase based on the edges:
- Edge (0,1): phase factor e^(-i*γ*(−1)^(q0⊕q1)) where the sign depends on whether q0 and q1 agree
- Edge (0,2): phase factor e^(-i*γ*(−1)^(q0⊕q2))

Actually, let me be more careful. The Z⊗Z operator has eigenvalue +1 when both qubits are the same (both 0 or both 1) and -1 when they differ.

So for |q0,q1,q2>:
- Z0⊗Z1 eigenvalue: (-1)^(q0⊕q1)
- Z0⊗Z2 eigenvalue: (-1)^(q0⊕q2)

The phase from edge (0,1) is e^(-i*γ*(-1)^(q0⊕q1))
The phase from edge (0,2) is e^(-i*γ*(-1)^(q0⊕q2))

With γ = 0.5:

|000>: q0⊕q1=0, q0⊕q2=0, phase = e^(-i*0.5) * e^(-i*0.5) = e^(-i*1.0)
|001>: q0⊕q1=0, q0⊕q2=1, phase = e^(-i*0.5) * e^(i*0.5) = 1
|010>: q0⊕q1=1, q0⊕q2=0, phase = e^(i*0.5) * e^(-i*0.5) = 1
|011>: q0⊕q1=1, q0⊕q2=1, phase = e^(i*0.5) * e^(i*0.5) = e^(i*1.0)
|100>: q0⊕q1=1, q0⊕q2=1, phase = e^(i*0.5) * e^(i*0.5) = e^(i*1.0)
|101>: q0⊕q1=1, q0⊕q2=0, phase = e^(i*0.5) * e^(-i*0.5) = 1
|110>: q0⊕q1=0, q0⊕q2=1, phase = e^(-i*0.5) * e^(i*0.5) = 1
|111>: q0⊕q1=0, q0⊕q2=0, phase = e^(-i*0.5) * e^(-i*0.5) = e^(-i*1.0)

After cost unitary:
|ψ_C> = 1/2√2 * (e^(-i)|000> + |001> + |010> + e^(i)|011> + e^(i)|100> + |101> + |110> + e^(-i)|111>)

Now apply Rx(2β) = Rx

## isqTrain/3663

- task_id: `isqTrain/3663`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `2453`

### Prompt

I need an isQ program to 3-bit quantum phase estimation for phase angle 6*pi/4 (in multiples of 2π/8). Use 3 precision qubits, controlled-Rz rotations, and a 3-qubit inverse QFT. Measure all 4 qubits (3 precision + 1 eigenstate).

### Chain-of-thought reasoning

The user wants me to generate a step-by-step reasoning for the Quantum Phase Estimation (QPE) circuit with 3 precision qubits estimating a phase angle of $6\pi/4$.

Let me break down the circuit:
1. We have 4 qubits: q[0], q[1], q[2] (precision qubits), q[3] (eigenstate qubit)
2. The eigenstate |1⟩ is prepared on q[3] using X gate
3. Hadamard gates are applied to all precision qubits to create superposition
4. Controlled-Rz rotations are applied with angles $2\pi \cdot (6/8) \cdot 2^k$ for k=0,1,2
5. Inverse QFT is applied to the precision qubits
6. All qubits are measured

Let me trace through the quantum state evolution:

Initial state: |0000⟩

After X(q[3]): |0001⟩

After H on q[0], q[1], q[2]:
$\frac{1}{2\sqrt{2}} (|000\rangle + |001\rangle + |010\rangle + |011\rangle + |100\rangle + |101\rangle + |110\rangle + |111\rangle) \otimes |1\rangle$

For the controlled-Rz operations:
- Rz(θ)|1⟩ = e^{-iθ/2}|1⟩ (up to global phase considerations)
- Actually, Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2})
- So Rz(θ)|1⟩ = e^{iθ/2}|1⟩

Wait, let me reconsider. The phase we're estimating is $6\pi/4 = 3\pi/2$. But in QPE, we're looking for the eigenvalue of the form $e^{2\pi i \phi}$ where $\phi$ is what we want to estimate.

If $\phi = 6/8 = 3/4$, then the eigenvalue is $e^{2\pi i \cdot 3/4} = e^{3\pi i / 2}$.

But the Rz gate gives $e^{i\theta}$ on |1⟩ state (when applied to eigenstate |1⟩).

Let me recalculate. If we have a unitary U with eigenvalue $e^{2\pi i \phi}$ on eigenstate |ψ⟩, then in QPE we apply controlled-U^(2^k).

For this problem, $\phi = 6/8$ and we're using Rz as our unitary. The Rz(θ) gate on |1⟩ gives $e^{i\theta/2}|1\rangle$ (considering the matrix $R_z(\theta) = e^{-i\theta/2} Z(\theta)$... wait let me be more careful).

$R_z(\theta) = \begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$

So $R_z(\theta)|1\rangle = e^{i\theta/2}|1\rangle$.

For the phase to be $\phi = 6/8$, we need $e^{i\theta/2} = e^{2\pi i \cdot 6/8}$, so $\theta/2 = 2\pi \cdot 6/8 = 3\pi/2$, meaning $\theta = 3\pi$.

But wait, the code uses $2\pi \cdot 6/8 \cdot 2^k$. Let me check:
- For k=0: $\theta = 2\pi \cdot 6/8 = 3\pi/2$
- For k=1: $\theta = 2\pi \cdot 6/8 \cdot 2 = 3\pi$
- For k=2: $\theta = 2\pi \cdot 6/8 \cdot 4 = 6\pi$

After applying controlled-Rz(θ_k) with control q[k] on target q[3]:
The state becomes $\frac{1}{2\sqrt{2}} \sum_{k_2=0}^{1}\sum_{k_1=0}^{1}\sum_{k_0=0}^{1} |k_2 k_1 k_0\rangle \otimes e^{i(k_0 \cdot 3\pi/4 + k_1 \cdot 3\pi/2 + k_2 \cdot 3\pi)}|1\rangle$

Wait, I need to be more careful. Each controlled-Rz adds a phase to |1⟩ on q[3] only

## isqTrain/4289

- task_id: `isqTrain/4289`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4838`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[5];

procedure main() {
    // Set all three input qubits to |1>
    X(q[0]);
    X(q[1]);
    X(q[2]);
    // Add x0 to sum: sum_bit0 = x0
    CNOT(q[0], q[3]);
    // Add x1 with half-adder carry propagation
    Toffoli(q[1], q[3], q[4]);
    CNOT(q[1], q[3]);
    // Add x2 with half-adder carry propagation
    Toffoli(q[2], q[3], q[4]);
    CNOT(q[2], q[3]);
    // Measure the 2-bit sum
    X(q[0]); // flip qubit 0 before measurement
    M(q[3]);
    M(q[4]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a concise, step-by-step analysis of an isQ quantum program, predicting its measurement outcome probabilities.

2.  **Analyze the isQ code**:
    *   `qbit q[5];` -> 5 qubits initialized to $|00000\rangle$.
    *   `X(q[0]); X(q[1]); X(q[2]);` -> State becomes $|11100\rangle$. (q[0]=1, q[1]=1, q[2]=1, q[3]=0, q[4]=0).
    *   `CNOT(q[0], q[3]);` -> q[3] flips because q[0]=1. State becomes $|11110\rangle$.
    *   `Toffoli(q[1], q[3], q[4]);` -> q[4] flips because q[1]=1 and q[3]=1. State becomes $|11111\rangle$.
    *   `CNOT(q[1], q[3]);` -> q[3] flips because q[1]=1. State becomes $|11101\rangle$.
    *   `Toffoli(q[2], q[3], q[4]);` -> q[4] flips because q[2]=1 and q[3]=0. State remains $|11101\rangle$ (Wait, q[3] is 0, so Toffoli doesn't flip q[4]. Ah, let me re-evaluate).
        *   Wait, let's trace carefully:
        *   Start: 00000
        *   X(0), X(1), X(2): q0=1, q1=1, q2=1, q3=0, q4=0 -> State: 11100
        *   CNOT(0, 3): q3 = q3 XOR q0 = 0 XOR 1 = 1. -> State: 11110
        *   Toffoli(1, 3, 4): q4 = q4 XOR (q1 AND q3) = 0 XOR (1 AND 1) = 1. -> State: 11111
        *   CNOT(1, 3): q3 = q3 XOR q1 = 1 XOR 1 = 0. -> State: 11101
        *   Toffoli(2, 3, 4): q4 = q4 XOR (q2 AND q3) = 1 XOR (1 AND 0) = 1. -> State: 11101
        *   CNOT(2, 3): q3 = q3 XOR q2 = 0 XOR 1 = 1. -> State: 11111
    *   Let me re-read the code for the second half:
        *   `CNOT(q[0], q[3]);` -> q3 = 1
        *   `Toffoli(q[1], q[3], q[4]);` -> q4 = 1
        *   `CNOT(q[1], q[3]);` -> q3 = 0
        *   `Toffoli(q[2], q[3], q[4]);` -> q2=1, q3=0 -> no change to q4. q4=1.
        *   `CNOT(q[2], q[3]);` -> q3 = q3 XOR 1 = 1.
    *   Final state before `X(q[0])`: 11111
    *   `X(q[0]);` -> q0 flips to 0. -> State: 01111.
    *   `M(q[3]); M(q[4]);` -> q3 is 1, q4 is 1.

3.  **Determine final bitstring**:
    *   Qubits are q[0], q[1], q[2], q[3], q[4].
    *   Final states: q[0]=0, q[1]=1, q[2]=1, q[3]=1, q[4]=1.
    *   Expected string format usually puts q[0] as the highest bit or lowest bit depending on convention. The prompt says: "array indexed by measurement bitstring (earlier measured qubit = higher bit)".
    *   The predicted measurement probabilities in the prompt say: `{|00011>: 1.0}`.
    *   Let's check the bitstring `00011`. If it's 5 qubits, `00011` means q[4,3,2,1,0] where q[4]=0, q[3]=0

### Reference answer

{'predicted_probs': {'00011': 1.0}, 'explanation': 'This isQ program operates on 5 qubit(s). The measurement probability distribution is: P(|00011>) = 1.0000.'}

## isqExpand/algo/168

- task_id: `isqExpand/algo/168`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `half_adder`, `toffoli_gate`, `cnot_gate`, `quantum_arithmetic`
- source: `isq_expansion`
- dataset_index: `4192`

### Prompt

用isQ实现an isQ quantum half adder that adds 0+0. Use a Toffoli for carry and CNOT for sum. Measure sum and carry qubits.

### Chain-of-thought reasoning

A quantum half adder takes two input bits a and b and computes sum = a XOR b and carry = a AND b. For adding 0+0, both inputs q[0] and q[1] are in |0⟩ state. The sum is computed using two CNOT gates: CNOT(q[0], q[2]) followed by CNOT(q[1], q[2]), which XORs both inputs into q[2]. The carry is computed using a Toffoli gate: Toffoli(q[0], q[1], q[3]), which ANDs both inputs into q[3]. Since both inputs are |0⟩, CNOT(0,2) does nothing (control is 0), CNOT(1,2) does nothing (control is 0), and Toffoli(0,1,3) does nothing (both controls are 0). All four qubits remain |0⟩, so the probability of measuring |0000⟩ is 1.0 and all other outcomes have probability 0.0.

## isqTrain/4817

- task_id: `isqTrain/4817`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_import_qft`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5581`

### Prompt

Write an isQ program that imports the qft module and applies QFT to a 3-qubit register initialized to |000>. QFT of |0> produces a uniform superposition. Declare 3 global qubits, import std and qft, apply qft(q) in main, then measure all qubits. Expected: uniform distribution (1/8 each).

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Apply QFT to |000⟩ to produce a uniform superposition over all 3-qubit states.

2. **Qubits**: 3 global qubits q[0], q[1], q[2], all measured at the end.

3. **State evolution**:
   - Start: |ψ⟩ = |000⟩
   - QFT maps |0⟩^⊗3 to uniform superposition: |ψ⟩ = (1/√8)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

4. **Expected probabilities**: Each of the 8 basis states has amplitude 1/√8, giving probability |1/√8|² = 1/8 = 0.125 each—uniform distribution confirmed.

## isqTrain/2060

- task_id: `isqTrain/2060`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5414`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
oracle bool[1] f(bool x[3]) {
    bool res[] = [x[0] != x[2]];
    return res;
}
qbit q[3];
qbit anc[1];
procedure main() {
    X(anc[0]);
    H(anc[0]);
    H(q[0]); H(q[1]); H(q[2]);
    f(q, anc);
    H(q[0]); H(q[1]); H(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement probabilities for an isQ program.
    *   Input: An isQ program implementing the Deutsch-Jozsa algorithm for a 3-bit input function.
    *   Target Output: A concise step-by-step circuit analysis (3-15 lines) starting with "## Circuit Analysis" and ending with the predicted probability distribution.

2.  **Analyze the isQ Program:**
    *   `qbit q[3];` (Main register, 3 qubits).
    *   `qbit anc[1];` (Ancilla, 1 qubit).
    *   `X(anc[0]);` -> ancilla state becomes |1>.
    *   `H(anc[0]);` -> ancilla state becomes |-.
    *   `H(q[0]); H(q[1]); H(q[2]);` -> Main register state becomes |+++> = $\frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle$.
    *   `f(q, anc);` applies the phase oracle. The function is `f(x) = x[0] != x[2]`. This means $f(x) = x_0 \oplus x_2$. Since $f(x)$ is a balanced function (XOR of two bits), the oracle applies a phase $(-1)^{f(x)}$ to the state $|x\rangle|-\rangle$.
    *   The state becomes $|\psi\rangle = \frac{1}{\sqrt{8}} \sum_x (-1)^{x_0 \oplus x_2} |x\rangle |-\rangle$.
    *   `H(q[0]); H(q[1]); H(q[2]);` applies Hadamard transform again. The state of the main register becomes $\frac{1}{8} \sum_{x,y} (-1)^{x_0 \oplus x_2} (-1)^{x \cdot y} |y\rangle$.
    *   We want to find the amplitude of $|y_0 y_1 y_2\rangle$. The sum over $x$ separates for each bit.
    *   For $y_1$: $\sum_{x_1} (-1)^{x_1 y_1} = 2\delta_{y_1, 0}$.
    *   For $y_0, y_2$: $\sum_{x_0, x_2} (-1)^{x_0 \oplus x_2} (-1)^{x_0 y_0 + x_2 y_2} = \sum_{x_0, x_2} (-1)^{x_0(1 \oplus y_0)} (-1)^{x_2(1 \oplus y_2)}$.
    *   This evaluates to $4$ if $y_0 = 1$ and $y_2 = 1$, and $0$ otherwise.
    *   Thus, the only state with non-zero amplitude is $y_0=1, y_1=0, y_2=1$.
    *   So the main register collapses to $|101\rangle$.
    *   `M(q[0]); M(q[1]); M(q[2]);` measures the main register.

3.  **Synthesize the Analysis:**
    *   Initialization: $|000\rangle_q |1\rangle_a$.
    *   After Hadamards: $|+++\rangle_q |-\rangle_a$.
    *   Oracle: $f(x) = x_0 \oplus x_2$ is balanced. The oracle applies a phase $(-1)^{x_0 \oplus x_2}$.
    *   Final Hadamards: Cancel out the superposition for balanced functions, leaving the state corresponding to the binary vector of the phase function. Since phase is $(-1)^{x_0 \oplus x_2} = (-1)^{1 \cdot x_0 + 1 \cdot x_2}$, the vector is $(1, 0, 1)$.
    *   The final state of the measured qubits is $|101\rangle$.
    *   Probability of '101' is 1.0.

4.  **Draft the response:**
    *   Start with "## Circuit Analysis"
    *   Step 1: Initial state preparation applies H to all q[0..2] and X, H to anc[0], creating $|+++\rangle_q |-\rangle_a$.
    *   Step 2: The oracle applies a phase kickback based on $f(x) = x_0 \oplus x

### Reference answer

{'predicted_probs': {'101': 1.0}, 'explanation': 'Bernstein-Vazirani for s=101: P(|101>)=1.0 at index 5.'}

## isqExpand/algo/63

- task_id: `isqExpand/algo/63`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `mid_circuit_measurement`, `basis_change`, `superposition`
- source: `isq_expansion`
- dataset_index: `5713`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[3];

procedure main() {
    // Prepare |+> on q[0]
    H(q[0]);

    // Create Bell pair
    H(q[1]);
    CNOT(q[1], q[2]);

    // Bell measurement but NO classical corrections
    CNOT(q[0], q[1]);
    H(q[0]);

    M(q[0]); M(q[1]);

    // No corrections applied to q[2]
    // Apply H to attempt |+> -> |0> verification
    H(q[2]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis

This is teleportation of |+> without classical corrections, followed by H.

1. H(q[0]): q[0] = |+>
2. H(q[1]), CNOT(q[1],q[2]): Bell pair (|00>+|11>)/sqrt(2)
3. 3-qubit: |+> (x) |Phi+> = (|000>+|011>+|100>+|111>)/2
4. CNOT(q[0],q[1]): -> (|000>+|011>+|110>+|101>)/2
5. H(q[0]): standard decomposition into Bell measurement outcomes.

After measuring q[0],q[1] (no corrections):
- m0=0,m1=0: q[2] = |+> -> H -> |0>
- m0=0,m1=1: q[2] = |+> -> H -> |0>  (X|+> = |+>)
- m0=1,m1=0: q[2] = |-> -> H -> |1>  (Z|+> = |->)
- m0=1,m1=1: q[2] = |-> -> H -> |1>  (ZX|+> = |->)

Each outcome P = 1/4.
P(final 0) = 1/4 + 1/4 = 1/2.
P(final 1) = 1/4 + 1/4 = 1/2.

Result: {0: 0.5, 1: 0.5} - uniform random.

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'Without classical corrections, the state of q[2] after measurement of q[0],q[1] depends on which Bell measurement outcome occurred:\n- m0=0,m1=0: q[2]=|+>, H gives |0>\n- m0=0,m1=1: q[2]=X|+>=|+>, H gives |0>\n- m0=1,m1=0: q[2]=Z|+>=|->, H gives |1>\n- m0=1,m1=1: q[2]=ZX|+>=Z|+>=|->, H gives |1>\nEach outcome has probability 1/4. P(q[2]=0 after H) = P(m0=0) = 1/2. P(q[2]=1 after H) = P(m0=1) = 1/2. The missing Z correction (for m0=1 cases) flips |+> to |-> which maps to |1> under H, randomizing the result.'}

## isqQA/quantum_algorithms/119_comparison

- task_id: `isqQA/quantum_algorithms/119_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `comparison`, `algorithm`, `固定点振幅放大`
- source: `qa_pipeline`
- dataset_index: `3627`

### Prompt

在量子算法设计中，固定点振幅放大是对传统Grover振幅放大算法的重要改进。请从对比分析的角度，详细探讨固定点振幅放大算法与传统振幅放大算法在数学原理、优缺点以及适用场景上的异同，并使用isQ代码展示如何实现固定点振幅放大中的核心相位旋转逻辑。

### Reference answer

<thought>
要对比固定点振幅放大（FPAA）与传统振幅放大（Grover AA），我们需要先从数学原理入手：
1. 传统振幅放大：使用算子 $Q = -A S_0 A^{-1} S_\chi$，其中 $S_\chi$（神谕）和 $S_0$（关于零态的反射）对应的相位旋转角度都是固定的 $\pi$。这导致目标概率振幅的演化呈现正弦波形式 $\sin^2((2k+1)\theta)$。其缺点是如果迭代次数 $k$ 过大，或者初始成功概率 $a$ 未知，算法会发生“过冲”，导致测量概率反而下降。
2. 固定点振幅放大：打破了固定 $\pi$ 相位的限制，将 $S_\chi$ 和 $S_0$ 的相位替换为随迭代次数变化的 $\gamma_j$ 和 $\phi_j$。通过精心设计的相位序列（如Yoder等人的方案），态向量的演化轨迹被“拉向”目标子空间且不会越过它，最终收敛到目标态，成功概率 $P \ge 1 - \epsilon$。
3. 优缺点对比：传统AA查询复杂度为 $O(1/\sqrt{a})$，效率最高，但极其脆弱；FPAA鲁棒性极强，不依赖初始概率 $a$ 的精确预知，代价是查询复杂度增加了一个对数因子 $O(\frac{1}{\sqrt{a}} \log(1/\epsilon))$。
4. 适用场景：传统AA适用于明确知道解的数量或可以精确控制迭代次数的场景；FPAA则适用于容错量子计算、嵌套量子子程序（如量子线性系统求解中振幅估计的内循环）或初始概率 $a$ 极小且未知的无约束搜索。

基于上述推理，我们在isQ代码中需要体现非 $\pi$ 相位的反射操作。传统反射是 Z 门（相位 $\pi$），在FPAA中我们需要将其替换为任意角度的相位旋转（例如 Rz 门）。以下是体现非 $\pi$ 相位神谕 $S_\chi$ 和扩散算子 $S_0$ 的isQ代码实现示例：
</thought>

在量子计算中，**固定点振幅放大**与传统的**Grover振幅放大**虽然都是为了放大目标量子态的测量概率，但它们在数学原理和工程适用性上有着深刻的差异。

### 1. 数学原理对比
**传统振幅放大**的核心是两个固定为 $\pi$ 的相位反转：对目标态的相位反转 $S_\chi$ 和关于初态的相位反转（扩散算子） $S_0$。迭代过程相当于在二维子空间（由目标态和非目标态张成）中进行匀速的圆周旋转，转角为 $2\theta$。因为这种正弦演化的周期性，如果不知道确切的初始成功率 $a=\sin^2(\theta)$，盲目迭代极易导致概率振幅过冲（Overshoot）。

**固定点振幅放大**（例如 Yoder, Low 和 Chuang 提出的算法）则抛弃了固定的 $\pi$ 相位。其数学核心是引入随迭代步数 $j$ 变化的相位角 $\gamma_j$ 和 $\phi_j$。此时，迭代算子变为 $Q_j = -A e^{i\phi_j} S_0 A^{-1} e^{i\gamma_j} S_\chi$。这种变步长的相位设计改变了态向量的演化流形，使其呈现出类似经典二分法或牛顿迭代法的收敛特性，使得算法可以单调地逼近目标态。

### 2. 优缺点对比
* **传统AA的优点**：在海量数据搜索且明确知道解的个数时，查询复杂度严格为最优的 $O(\sqrt{N})$。
* **传统AA的缺点**：极其脆弱。若解的数量未知或初态叠加概率未知，系统会发生周期性振荡，无法稳定在高概率态。
* **固定点AA的优点**：具有极强的鲁棒性。只要给定容差 $\epsilon$，无论初始振幅多大，经过确定的迭代次数后，成功概率必定不低于 $1-\epsilon$。
* **固定点AA的缺点**：为了达到固定点收敛属性，其查询复杂度会比最优情况多出一个对数级别的惩罚，变为 $O(\frac{1}{\sqrt{a}} \log(1/\epsilon))$。

### 3. 适用场景对比
传统AA适用于单次运行的孤立搜索任务（如密码破解、NP问题求解），且用户可以通过量子计数预先获知解的数量。而FPAA则必不可少地应用于**嵌套量子算法**中，例如在量子线性方程组求解（HHL算法）或量子主成分分析中，内层的振幅放大往往无法预估初始概率 $a$，如果使用传统AA，内层过冲会直接导致外层算法崩溃。FPAA保证了算法在任意初态下都能稳定输出，是构建容错量子算法体系的重要基石。

### 4. isQ 代码实现：非 $\pi$ 相位旋转逻辑
在固定点振幅放大中，我们需要将传统的 Z 门（$\pi$ 相位）替换为任意角度 $\theta$ 的旋转。以下代码展示了如何利用 `Rz` 门和受控逻辑构造出具有可变相位 $\gamma$ 和 $\phi$ 的核心算子：

```isQ
import std;

qbit q[2];
qbit anc[1];

// 定义可变角度的神谕 S_chi(gamma)
// 传统 Grover 中这里是 ctrl @ Z 或类似逻辑，这里替换为角度 gamma 的旋转
procedure variable_oracle(double gamma) {
    // 假设目标态为 |11>，使用受控旋转来施加 gamma 相位
    X(q[0]);
    X(q[1]);
    // 利用 Toffoli 和 Rz 构造受控相位旋转
    Toffoli(q[0], q[1], anc[0]);
    Rz(gamma, anc[0]);
    Toffoli(q[0], q[1], anc[0]);
    X(q[0]);
    X(q[1]);
}

// 定义可变角度的扩散算子 S_0(phi)
procedure variable_diffuser(double phi) {
    // A 操作通常为 Hadamard
    H(q[0]);
    H(q[1]);
    // 对 |00> 态施加 phi 相位旋转
    Toffoli(q[0], q[1], anc[0]);
    X(anc[0]);
    Rz(phi, anc[0]);
    X(anc[0]);
    Toffoli(q[0], q[1], anc[0]);
    // A 逆操作
    H(q[0]);
    H(q[1]);
}

procedure main() {
    // 初始化均匀叠加态
    H(q[0]);
    H(q[1]);

    // 假设这是某次迭代的固定点参数
    double gamma = 1.234;
    double phi = 0.567;

    // FPAA 的核心步骤
    variable_oracle(gamma);
    variable_diffuser(phi);
}
```

## isqTrain/2980

- task_id: `isqTrain/2980`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `977`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    ctrl H(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Explain the quantum circuit defined by the isQ program, step-by-step, using Dirac notation, and predict the output probability distribution.
    *   Input isQ code:
        
    *   Output format: "## Circuit Analysis", step-by-step reasoning using Dirac notation, ending with the predicted probability distribution. Length constraint: 3-15 lines.

2.  **Circuit Breakdown:**
    *   `qbit q[2];` -> Initial state is $|00\rangle$.
    *   `X(q[0]);` -> Applies X gate to q[0]. State changes from $|00\rangle$ to $|10\rangle$.
    *   `ctrl H(q[0], q[1]);` -> Applies a controlled-H gate. In isQ, `ctrl H(control, target)` means apply H to the target if the control is $|1\rangle$. Wait, `ctrl` syntax: `ctrl Gate(control, target)`? Let me double check isQ syntax.
        *   Wait, standard isQ syntax for controlled gates: `ctrl H(q[0], q[1])` or `ctrl H(q[1], q[0])`?
        *   Usually `CNOT(control, target)` is explicitly `CNOT(c, t)`.
        *   If it's `ctrl H(q[0], q[1])`, the modifier `ctrl` turns the first qubit into the control and the second into the target (or the first listed is the control, wait). Let's look at the reference: "Control modifier: `ctrl @[c1, c2] Gate(target);`". Ah, but here it's `ctrl H(q[0], q[1])`. In isQ, `ctrl Gate(c, t)` applies the gate to `t` controlled by `c`. Wait, the syntax `ctrl H(q[0], q[1])` might mean `q[0]` is the control, `q[1]` is the target.
        *   Wait, let's trace the effect. Current state is $|10\rangle$ (q[0] is 1, q[1] is 0).
        *   If `q[0]` is the control, since it is $|1\rangle$, H is applied to `q[1]`.
        *   $H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
        *   So the state becomes $\frac{1}{\sqrt{2}}(|10\rangle + |11\rangle)$.
    *   `M(q[0]); M(q[1]);` -> Measure both qubits. Probabilities:
        *   $|10\rangle$: $(\frac{1}{\sqrt{2}})^2 = 0.5$
        *   $|11\rangle$: $(\frac{1}{\sqrt{2}})^2 = 0.5$
        *   Bitstring mapping: `q[0]` is measured first. Wait, `M(q[0])` then `M(q[1])`. In classical register mapping, usually the first measured qubit is the highest bit or lowest bit?
        *   Reference says: "--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)."
        *   So `q[0]` is the higher bit, `q[1]` is the lower bit.
        *   State $|10\rangle$ means `q[0]=1`, `q[1]=0` -> bitstring `10` -> 0.5.
        *   State $|11\rangle$ means `q[0]=1`, `q[1]=1` -> bitstring `11` -> 0.5.
        *   Expected measurement probabilities provided in the prompt: `{'10': 0.4999999999999999, '11': 0.5000000000000001}`. This exactly matches!

3.  **Drafting the step-by-step reasoning:**
    *   Initial state: $|00\rangle$
    *   Apply $X$ to $q_0$: $|00\rangle \to |10\rangle$
    *   Apply controlled-$H$ (control=$q_0$, target=$q_1$). Since $q_0$ is $|1\rangle$, $H$ is applied to $q_1$.

### Reference answer

{'predicted_probs': {'10': 0.4999999999999999, '11': 0.5000000000000001}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqQA/quantum_algorithms/97_isq_implementation

- task_id: `isqQA/quantum_algorithms/97_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_implementation`, `algorithm`, `Grover最优迭代次数推导`
- source: `qa_pipeline`
- dataset_index: `5765`

### Prompt

请提供一个完整的Grover量子搜索算法的isQ代码实现。要求以2个量子比特（即搜索空间大小N=4）和1个目标态（M=1）为例，目标态设为|11⟩。请在回答中先从数学角度推导Grover算法的最优迭代次数k与N、M的关系，然后利用推导出的公式计算本例所需的最优迭代次数，并据此编写带有逐行详细注释的isQ代码，代码需完整包含初始化、Oracle构建、Diffuser扩散算子构建以及最终的测量操作。

### Reference answer

<think>
首先，从数学角度分析Grover算法的几何意义，将状态演化投影到由目标态和均匀叠加态张成的二维子空间中。定义初始叠加态与目标态的夹角满足 $\sin(\theta/2) = \sqrt{M/N}$。每次Grover迭代（包含Oracle和扩散算子）会使系统状态向目标态旋转 $\theta$ 角度。为最大化测量得到目标态的概率，需使振幅接近 $\pi/2$，即满足 $(2k+1)\theta/2 = \pi/2$，从而推导出最优迭代次数 $k \approx \frac{\pi}{4}\sqrt{\frac{N}{M}}$。

接着，代入本题具体参数：搜索空间 $N=4$，目标数 $M=1$。计算可得 $\theta = \pi/3$，代入推导出的公式解得 $k=1$。即算法只需执行一次迭代即可达到最大概率。

最后，规划isQ代码的实现逻辑：先分配2个量子比特并用Hadamard门完成叠加态初始化；接着构建寻找|11⟩的Oracle，利用控制相位门（等价于H门包裹的CNOT门）实现目标态相位翻转；随后构建Diffuser扩散算子，对所有态执行相位翻转；串联执行1次完整的迭代循环后，对两个量子比特进行测量并保存至经典寄存器。
</think>

为了回答这个问题，我们首先从几何和数学的角度推导Grover算法的最优迭代次数，随后基于推导结果提供完整的isQ代码实现。对于搜索空间大小为 N=2^n 且目标解数量为 M=1 的情况，Grover算法本质上是在二维子空间（由均匀叠加态 |s⟩ 和目标态 |w⟩ 张成）中进行的旋转操作。初始状态 |s⟩ 可以表示为：|s⟩ = sin(θ/2)|w⟩ + cos(θ/2)|w^⊥⟩，其中 sin(θ/2) = √(M/N)。每次Grover迭代包含一次Oracle反射和一次关于 |s⟩ 的扩散反射，这两次操作会将状态矢量在二维子空间中向目标态 |w⟩ 旋转角度 θ。经过 k 次迭代后的状态为：sin((2k+1)θ/2)|w⟩ + cos((2k+1)θ/2)|w^⊥⟩。为了使得测量得到 |w⟩ 的概率 P = sin^2((2k+1)θ/2) 最大化，我们需要使得 (2k+1)θ/2 ≈ π/2。从而解得最优迭代次数公式为：k ≈ π/(2θ) - 1/2。当 N >> M 时，θ ≈ 2√(M/N)，代入可得最常见的近似公式 k ≈ (π/4)√(N/M)。在本题设定的案例中，N=4，M=1，因此 sin(θ/2) = √(1/4) = 1/2，即 θ/2 = π/6，θ = π/3。代入精确求解公式：k = π/(2 * π/3) - 1/2 = 1.5 - 0.5 = 1。因此，本例中的最优迭代次数为精确的 1 次。基于上述推导，下面是使用isQ语言编写的完整Grover算法代码，其中目标态设为 |11⟩：
import std;

// 全局声明2个量子比特用于构成N=4的搜索空间
qbit q[2];

procedure main() {
    // 初始化：将所有量子比特置于均匀叠加态 |s⟩
    // 相当于执行 Hadamard 门，此时概率幅各为 1/2
    for i in 0:2 {
        H(q[i]);
    }

    // 根据数学推导，最优迭代次数 k = 1，因此这里仅执行一次Grover迭代
    // 1. Oracle 算子：标记目标态 |11⟩ 并翻转其相位
    // 由于目标态是 |11⟩，直接使用 CZ 门即可实现相位翻转
    CZ(q[0], q[1]);

    // 2. Diffuser 扩散算子 (关于 |s⟩ 的反射)
    // 步骤 2.1: 再次应用 Hadamard 门，变换回计算基
    for i in 0:2 {
        H(q[i]);
    }

    // 步骤 2.2: 应用关于 |00⟩ 的条件相位翻转
    // 即翻转除 |00⟩ 以外所有状态的相位
    // 等效于对每一个量子比特应用 X 门，然后执行 CZ，最后再应用 X 门
    for i in 0:2 {
        X(q[i]);
    }
    CZ(q[0], q[1]);
    for i in 0:2 {
        X(q[i]);
    }

    // 步骤 2.3: 再次应用 Hadamard 门，完成反射操作
    for i in 0:2 {
        H(q[i]);
    }

    // 测量阶段：对两个量子比特进行测量
    // 经过 1 次最优迭代后，理论上将以 100% 的概率测量到目标态 |11⟩
    for i in 0:2 {
        M(q[i]);
    }
}
