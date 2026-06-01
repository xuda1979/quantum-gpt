# ISQ training COT RAG corpus: quantum_algorithms shard 18

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/995

- task_id: `isqTrain/995`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3057`

### Prompt

Implement the following in isQ: implements the qdrift pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this qdrift pattern circuit step by step.

The circuit simulates H = X + Z using the qdrift protocol with t = π/4, λ = 2, N = 3 samples, and τ = π/6.

Starting state: |0⟩

1. Rx(π/3) on |0⟩:
Rx(θ) = cos(θ/2)I - i·sin(θ/2)X = cos(θ/2)|0⟩⟨0| + cos(θ/2)|1⟩⟨1| - i·sin(θ/2)|1⟩⟨0| - i·sin(θ/2)|0⟩⟨1|
Rx(π/3)|0⟩ = cos(π/6)|0⟩ - i·sin(π/6)|1⟩ = (√3/2)|0⟩ - i(1/2)|1⟩

2. Rz(π/3) on the result:
Rz(θ)|0⟩ = e^{-iθ/2}|0⟩
Rz(θ)|1⟩ = e^{iθ/2}|1⟩

After Rz(π/3): e^{-iπ/6}(√3/2)|0⟩ - i·e^{iπ/6}(1/2)|1⟩

3. Rx(π/3) again:
Let me denote the state as α|0⟩ + β|1⟩ where α = e^{-iπ/6}(√3/2), β = -i·e^{iπ/6}(1/2)

Rx(π/3)(α|0⟩ + β|1⟩) = cos(π/6)(α|0⟩ + β|1⟩) - i·sin(π/6)(β|0⟩ + α|1⟩)
= (√3/2)(α|0⟩ + β|1⟩) - i(1/2)(β|0⟩ + α|1⟩)
= ((√3/2)α - i(1/2)β)|0⟩ + ((√3/2)β - i(1/2)α)|1⟩

Let me compute:
α = e^{-iπ/6}·(√3/2)
β = -i·e^{iπ/6}·(1/2)

(√3/2)α = (√3/2)·(√3/2)·e^{-iπ/6} = (3/4)·e^{-iπ/6}
i(1/2)β = i·(1/2)·(-i)·e^{iπ/6}·(1/2) = (1/4)·e^{iπ/6}

Coefficient of |0⟩ = (3/4)e^{-iπ/6} - (1/4)e^{iπ/6}

Let me use Euler's formula:
e^{-iπ/6} = cos(π/6) - i·sin(π/6) = (√3/2) - i(1/2)
e^{iπ/6} = (√3/2) + i(1/2)

(3/4)((√3/2) - i(1/2)) - (1/4)((√3/2) + i(1/2))
= (3√3/8 - √3/8) + i(-3/8 - 1/8)
= (2√3/8) - i(4/8)
= (√3/4) - i(1/2)

|coef_0|² = (√3/4)² + (1/2)² = 3/16 + 4/16 = 7/16

Similarly for |1⟩:
(√3/2)β = (√3/2)·(-i)·e^{iπ/6}·(1/2) = -i(√3/4)·e^{iπ/6}
i(1/2)α = i·(1/2)·e^{-iπ/6}·(√3/2) = i(√3/4)·e^{-iπ/6}

Coefficient of |1⟩ = -i(√3/4)·e^{iπ/6} - i(√3/4)·e^{-iπ/6}
= -i(√3/4)(e^{iπ/6} + e^{-iπ/6})
= -i(√3/4)·2·cos(π/6)
= -i(√3/4)·2·(√3/2)
= -i(3/4)

|

## isqTrain/4307

- task_id: `isqTrain/4307`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1633`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

qbit q[3];

procedure main() {
    X(q[1]);
    
    // QFT
    H(q[2]);
    ctrl S(q[1], q[2]);
    ctrl T(q[0], q[2]);
    
    H(q[1]);
    ctrl S(q[0], q[1]);
    
    H(q[0]);
    
    // SWAP
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    
    // Measure all qubits
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The task is to analyze an isQ quantum program, trace the quantum state evolution, and predict the final probability distribution of the measurements, matching the provided circuit implementation. The output must be strictly the analysis starting with "## Circuit Analysis", using concise Dirac notation.

2.  **Analyze the Circuit**:
    *   Initial state: |000>
    *   `X(q[1])`: Flips q1. State becomes |010>.
    *   QFT on 3 qubits (q[0], q[1], q[2]):
        *   `H(q[2])`: Acts on q2. |010> -> 1/sqrt(2) (|010> + |110>)
        *   `ctrl S(q[1], q[2])`: Apply S to q2 if q1 is 1. S|0> = |0>, S|1> = i|1>. State -> 1/sqrt(2) (|010> + i|110>)
        *   `ctrl T(q[0], q[2])`: Apply T to q2 if q0 is 1. Since q0 is 0, no effect. State remains 1/sqrt(2) (|010> + i|110>)
        *   `H(q[1])`: Acts on q1. State -> 1/2 (|000> + |010> + i(|100> + |110>)) ... wait, let's trace carefully.
            *   |010> + i|110>.
            *   H on q1: |0> -> |+>, |1> -> |->
            *   |010> -> 1/sqrt(2) (|000> + |010>)
            *   i|110> -> i/sqrt(2) (|100> - |110>)
            *   State -> 1/2 (|000> + |010> + i|100> - i|110>)
        *   `ctrl S(q[0], q[1])`: Apply S to q1 if q0 is 1. q0 is 0, no effect.
        *   `H(q[0])`: Acts on q0.
            *   |000> -> 1/sqrt(2)(|000>+|100>)
            *   |010> -> 1/sqrt(2)(|010>+|110>)
            *   i|100> -> i/sqrt(2)(|000>-|100>)
            *   -i|110> -> -i/sqrt(2)(|010>-|110>)
            *   Combine: 1/(2sqrt2) [ |000>+|100> + |010>+|110> + i|000>-i|100> - i|010>+i|110> ]
            *   = 1/(2sqrt2) [ (1+i)|000> + (1-i)|100> + (1-i)|010> + (1+i)|110> ]
    *   `swap (three-CNOT decomposition)(q[0], q[2])`:
        *   Implemented as `CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2]);`
        *   This swaps the states of q0 and q2.
        *   In our state, q2 is always |0>. So swapping q0 and q2 just leaves q0 as |0> and q2 as whatever q0 was.
        *   Wait, q0 was in a superposition of |0> and |1>. After swap (three-CNOT decomposition), q2 will be in that superposition, and q0 will be |0>.
        *   Let's check:
            *   (1+i)|000> -> (1+i)|000>
            *   (1-i)|100> -> (1-i)|001>
            *   (1-i)|010> -> (1-i)|010>
            *   (1+i)|110> -> (1+i)|011>
        *   So state becomes 1/(2sqrt2) [ (1+i)|000> + (1-i)|001> + (1-i)|010> + (1+i)|011> ]
    *   `X(q[0])`: Flips q0.
        *   State becomes 1/(2sqrt2) [ (1+i)|100> + (1-i)|101> + (1-i)|110> + (1+i)|111> ]
    *   Measurement probabilities:
        *   Magnitude squared of each amplitude is |1+i|^2 / 8 = 2/8 = 0.25.
        *   Since there are 4 terms, each has probability 0.25.
        *   Wait, The predicted output: `

### Reference answer

{'predicted_probs': {'000': 0.125, '001': 0.125, '010': 0.125, '011': 0.125, '100': 0.125, '101': 0.125, '110': 0.125, '111': 0.125}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.1250, P(|001>) = 0.1250, P(|010>) = 0.1250, P(|011>) = 0.1250, P(|100>) = 0.1250, P(|101>) = 0.1250, P(|110>) = 0.1250, P(|111>) = 0.1250.'}

## isqTrain/4613

- task_id: `isqTrain/4613`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4468`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[1];

procedure main() {
    
    X(q[0]);
    H(q[0]);
    
    
    H(q[0]);
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    *   `X(q[0])`: Apply X gate to qubit 0.
    *   `H(q[0])`: Apply H gate to qubit 0.
    *   `H(q[0])`: Apply H gate to qubit 0.
    *   `H(q[0])`: Apply H gate to qubit 0.
    *   `Z(q[0])`: Apply Z gate to qubit 0.
    *   `H(q[0])`: Apply H gate to qubit 0. (Comment says HZH = X)
    *   `M(q[0])`: Measure qubit 0.

2.  **Simplify the operations:**
    *   Start with |0>.
    *   `X` -> |1>.
    *   `H` -> |-> = (|0> - |1>)/sqrt(2).
    *   The comment explicitly says `H H H Z H` which is `H Z H` since $H^2 = I$.
    *   Wait, let's trace exactly:
        *   Initial: |0>
        *   `X`: |1>
        *   `H`: |->
        *   `H`: |1>  (since H applied to |-> is |1>)
        *   `H`: |->
        *   `Z`: H|1> -> Z|-> = -|-> (actually Z|-> = -|->) Wait.
        *   Let's check Z|->
            $Z \frac{1}{\sqrt{2}}(|0> - |1>) = \frac{1}{\sqrt{2}}(|0> + |1>) = |+>$.
        *   `H`: H|+> = |0>.
    *   So, the final state is |0>.

3.  **Step-by-step state evolution:**
    *   Initial state: |0>
    *   After `X(q[0])`: |1>
    *   After first `H(q[0])`: |->
    *   After second `H(q[0])`: |1>
    *   After third `H(q[0])`: |->
    *   After `Z(q[0])`: |+> (since ZH|1> = Z|-> = |+>)
    *   After fourth `H(q[0])` (which is the 5th H in total): |0> (since H|+> = |0>)

    *Alternative simplification:*
    Sequence of gates: H, Z, H, H, H, X, H.
    H * Z * H = X.
    So we have H * Z * H * H * X * H = X * X * H = I * H ? Wait, no.
    Let's read the code again carefully:
    `X(q[0]);`
    `H(q[0]);`
    `H(q[0]);`
    `H(q[0]); Z(q[0]); H(q[0]);`
    Total sequence from right to left (in matrix multiplication): H Z H H H X.
    Wait, program executes top to bottom:
    1. X
    2. H
    3. H
    4. H
    5. Z
    6. H
    So the matrix is $H \cdot Z \cdot H \cdot H \cdot H \cdot X$.
    $H \cdot H = I$.
    So it's $H \cdot Z \cdot H \cdot X$.
    $H Z H = X$.
    So it's $X \cdot X = I$.
    Wait, $H \cdot Z \cdot H \cdot X = X \cdot X = I$.
    Let's re-verify: $H Z H = X$.
    So $H Z H X = X X = I$.
    State goes $|0> \xrightarrow{X} |1> \xrightarrow{H} |-> \xrightarrow{H} |1> \xrightarrow{H} |-> \xrightarrow{Z} |+> \xrightarrow{H} |0>$.
    Yes! The final state is |0>.

4.  **Format the output:**
    *   Must start with "## Circuit Analysis".
    *   Explain operations, step-by-step evolution, final state, probabilities.
    *   End with the distribution format.

5.  **Drafting the text:**
    ## Circuit Analysis
    1. **Operations:** The circuit applies the following gates to qubit `q[0]`: X, H, H, H, Z, H.
    2. **State Evolution:**

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 1.0000.'}

## isqTrain/2799

- task_id: `isqTrain/2799`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_classical_vars`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3527`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```isq
import std;

bool m1, m2;
qbit q_1, q_2, q_3;

procedure Teleport(qbit qsrc, qbit qanc, qbit qdest) 
{
    H(qanc);
    // CNOT(qanc, qdest); // BUG: missing CNOT
    CNOT(qsrc, qanc);
    H(qsrc);
    m1 = M(qsrc);
    m2 = M(qanc);
    if (m2) { X(qdest); }
    if (m1) { Z(qdest); }
}

procedure main()
{
    X(q_1);
    Teleport(q_1, q_2, q_3);
    print M(q_3);
}
```

### Chain-of-thought reasoning

Step 1: Analyze the buggy code.
The buggy code is a quantum teleportation protocol.
In `Teleport`, the operations are:
1. `H(qanc);`
2. `// CNOT(qanc, qdest); // BUG: missing CNOT`
3. `CNOT(qsrc, qanc);`
4. `H(qsrc);`
5. `m1 = M(qsrc);`
6. `m2 = M(qanc);`
7. `if (m2) { X(qdest); }`
8. `if (m1) { Z(qdest); }`

The missing gate is `CNOT(qanc, qdest);`. This is supposed to create a Bell pair between `qanc` and `qdest`. Without it, there is no entanglement, and the state of `qsrc` cannot be transferred to `qdest`.

Step 2: Describe the fix.
The fix is to uncomment or add the `CNOT(qanc, qdest);` gate immediately after `H(qanc);`.

Step 3: Trace the state evolution of the corrected circuit.
- Initial state: q_1 is |1>, q_2 is |0>, q_3 is |0>. State is |100>.
- H(q_2): q_2 is |+>. State is (1/sqrt(2))(|100> + |110>).
- CNOT(q_2, q_3): Entangles q_2 and q_3 into a Bell pair. State is (1/sqrt(2))(|100> + |111>).
- CNOT(q_1, q_2): Entangles q_1 with q_2. State is (1/sqrt(2))(|100> + |011>).
- H(q_1): Hadamard on q_1. State is (1/2)(|000> - |100> + |011> - |111>).
- Measurements & Corrections: Depending on measurements, the X and Z corrections will leave q_3 in the original state of q_1 (|1>).
- Final state before measurement of q_3: The system is in a mixture of |0_1 0_2 1_3>, |0_1 1_2 1_3>, |1_1 0_2 1_3>, |1_1 1_2 1_3>. The resulting probabilities should be given as {|000>: 0.25, |011>: 0.25, |100>: 0.25, |111>: 0.25} which corresponds to the final measurement of all three qubits after q_3 ends up as |1> (q_3 is the lowest bit, so |001> etc. Wait, the output string is earlier measured qubit = higher bit. So m1 (q_1) is highest bit, m2 (q_2) is middle bit, M(q_3) is lowest bit. Thus |100>, |110>, |100>, |110>? No, the state is |0_1 0_2 1_3> = |001>, |0_1 1_2 1_3> = |011>, |1_1 0_2 1_3> = |101>, |1_1 1_2 1_3> = |111>.
Wait, the prompt says: Expected measurement probabilities: {|000>: 0.25, |011>: 0.25, |100>: 0.25, |111>: 0.25}.
Let's check `X(q_1);` initializes q_1 to |1>. After teleportation, q_3 will be |1>.
Wait, why `|000>` and `|100>`? If q_3 is |1>, then the lowest bit should be 1, so |001>, |011>, |101>, |111>.
Let's recalculate.
Initial state: |100>.
H(q_2): |100> -> (1/sqrt(2)) (|100> + |110>)
CNOT(q_2, q_3): (1/sqrt(2)) (|100> + |111>)
CNOT(q_1, q_2): (1/sqrt(2)) (|110> + |011>) -> Wait. CNOT(q_1, q_2). Control is q_1, target is q_2.
|100> + |111> -> |1(0⊕1)0> + |0(1⊕0)1> = |110> + |011>.
Let me re-evaluate CNOT(q_1, q_2).
|100>: control is 1, target is 0. 0⊕1 = 1 -> |110

## isqTrain/1250

- task_id: `isqTrain/1250`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1328`

### Prompt

What does this isQ program output when measured?

```isq
import std;

// Phase kickback demonstration with controlled-T
qbit q[2];

procedure main() {
    // Control qubit in |+> state
    H(q[0]);
    // Target in eigenstate |1> of T gate
    X(q[1]);
    // Controlled-T: phase e^(i*pi/4) kicks back to control
    ctrl T(q[0], q[1]);
    // Hadamard converts phase to measurable amplitude
    H(q[0]);
    // Measure control to observe kickback effect
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Analyze an isQ program predicting measurement probabilities.
    *   Input program:
        *   Initialize `q[0]` and `q[1]` to `|0>` (implicitly).
        *   `H(q[0])`: `|0> -> |+>`
        *   `X(q[1])`: `|0> -> |1>`
        *   `ctrl T(q[0], q[1])`: Apply T gate to `q[1]` controlled on `q[0]`. Since `q[1]` is in eigenstate `|1>` of T, it kicks back the phase $e^{i\pi/4}$ to the `|1>` state of the control qubit `q[0]`.
        *   `H(q[0])`: Hadamard on control qubit.
        *   `M(q[0])`: Measure control qubit.
    *   Target output: Step-by-step reasoning, circuit analysis, predicted probabilities.

2.  **State Evolution Step-by-Step:**
    *   Initial state: $|00\rangle$
    *   `H(q[0])`, `X(q[1])`: $|00\rangle \to |+\rangle|1\rangle = \frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$.
    *   `ctrl T(q[0], q[1])`:
        *   T gate is $|0\rangle\langle0| + e^{i\pi/4}|1\rangle\langle1|$.
        *   Controlled-T applies T to `q[1]` if `q[0]` is 1.
        *   $\frac{1}{\sqrt{2}}(|0\rangle \otimes T|1\rangle + |1\rangle \otimes T|1\rangle)$ wait, no.
        *   Controlled-T: $|00\rangle\to|00\rangle, |01\rangle\to|01\rangle, |10\rangle\to|10\rangle, |11\rangle\to e^{i\pi/4}|11\rangle$.
        *   State becomes: $\frac{1}{\sqrt{2}}(|01\rangle + e^{i\pi/4}|11\rangle) = \frac{1}{\sqrt{2}}(|0\rangle + e^{i\pi/4}|1\rangle) \otimes |1\rangle$.
    *   `H(q[0])`:
        *   Apply H to first qubit: $\frac{1}{\sqrt{2}}(H|0\rangle + e^{i\pi/4}H|1\rangle) \otimes |1\rangle$.
        *   $H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
        *   $H|1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        *   First qubit state: $\frac{1}{2} |0\rangle (1 + e^{i\pi/4}) + \frac{1}{2} |1\rangle (1 - e^{i\pi/4})$.
    *   Measure `q[0]`:
        *   $P(0) = \frac{1}{4} |1 + e^{i\pi/4}|^2 = \frac{1}{4} (1 + \cos(\pi/4) + i\sin(\pi/4))(1 + \cos(\pi/4) - i\sin(\pi/4))$.
        *   $= \frac{1}{4} ( (1 + \cos(\pi/4))^2 + \sin^2(\pi/4) ) = \frac{1}{4} (1 + 2\cos(\pi/4) + \cos^2(\pi/4) + \sin^2(\pi/4)) = \frac{1}{4} (2 + 2\cos(\pi/4)) = \frac{1}{2}(1 + \frac{\sqrt{2}}{2}) = \frac{2 + \sqrt{2}}{4} \approx 0.85355339059$.
        *   $P(1) = \frac{1}{4} |1 - e^{i\pi/4}|^2 = \frac{1}{4} (2 - 2\cos(\pi/4)) = \frac{2 - \sqrt{2}}{4} \approx 0.146

### Reference answer

{'predicted_probs': {'0': 0.8535533905932737, '1': 0.14644660940672624}, 'explanation': 'Parametric variant of isqEval/458. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3469

- task_id: `isqTrain/3469`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1851`

### Prompt

I need an isQ program to the iSWAP gate using CNOTs and S gates in isQ.

iSWAP swaps |01> <-> i|10> and |10> <-> i|01>.
Decomposition:
  S(q[0]); S(q[1]); H(q[0]); CNOT(q[0],q[1]); CNOT(q[1],q[0]); H(q[1])

Test: apply to |10>. Expected: superposition due to phase.
Declare 2 qubits, measure both.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement iSWAP (custom gate) via S, H, CNOT decomposition and test on |10>, expecting output i|01>.

Two qubits q[0], q[1]; both measured.

State evolution from |10>:
1. S(q[0]); S(q[1]): S|1>=i|1>, S|0>=|0> → i|10>
2. H(q[0]): i·(|00>-|10>)/√2
3. CNOT(q[0],q[1]): |00>→|00>, |10>→|11> → i·

## isqTrain/1851

- task_id: `isqTrain/1851`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `872`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[3];
procedure balanced_oracle(qbit a, qbit b, qbit out) {
    CNOT(a, out);
    CNOT(b, out);
}
procedure main() {
    X(q[2]);
    H(q[2]);
    H(q[0]); H(q[1]);
    balanced_oracle(q[0], q[1], q[2]);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the input code:**
    -   3 qubits initialized to |000>.
    -   `X(q[2])`: q[2] becomes |1>. State: |001>.
    -   `H(q[2])`: q[2] becomes (|0>-|1>)/sqrt(2) = |->. State: |00>|->.
    -   `H(q[0]); H(q[1])`: State becomes (|00>+|01>+|10>+|11>)/sqrt(4) |-> / sqrt(2) = (1/2) Sum_{x} |x>|->.
    -   `balanced_oracle(q[0], q[1], q[2])`:
        -   `CNOT(q[0], q[2])`: Flips phase of q[2] if q[0] is 1.
        -   `CNOT(q[1], q[2])`: Flips phase of q[2] if q[1] is 1.
        -   This acts as a phase oracle for $f(x) = x_0 \oplus x_1$.
        -   If q[0] = 1, the |-> state gets a phase of -1. If q[1] = 1, it gets another phase of -1. So if exactly one of them is 1, the phase is -1. If both are 1 or 0, the phase is +1.
        -   Effectively, state becomes (1/2) Sum_{x} (-1)^{f(x)} |x>|->.
        -   Wait, let's trace it exactly.
        -   Input: (1/2)(|0>|0> + |1>|0> + |0>|1> + |1>|1>) (|0> - |1>) / sqrt(2)
        -   Let's just track the first two qubits and the phase on the third.
        -   Start with qubits 0,1 in |++> and qubit 2 in |->
        -   CNOT(0, 2): If q[0]=1, qubit 2 flips. |- > becomes - |- >.
        -   CNOT(1, 2): If q[1]=1, qubit 2 flips.
        -   Let's check the effect on the tensor product state.
        -   |0>|1>|-> -> |0>|1>(-|- >) = - |0>|1>|- >
        -   |1>|0>|-> -> |1>|0>(-|- >) = - |1>|0>|- >
        -   |1>|1>|-> -> |1>|1>(|- >) = |1>|1>|- >
        -   |0>|0>|-> -> |0>|0>|->.
        -   So the state is 1/2 (|00> - |01> - |10> + |11>) |- >.
        -   Notice that the first two qubits are in state |--> wait.
        -   |--> = (|0>-|1>)(|0>-|1>)/2 = 1/2 (|00> - |01> - |10> + |11>).
        -   Yes! The phase oracle for $f(x) = x_0 \oplus x_1$ maps |++> to |-->.
    -   `H(q[0]); H(q[1])`: H applied to |--> gives |11>.
    -   State becomes |11>|->.
    -   `M(q[0]); M(q[1])`: Measure q[0] and q[1].
    -   Since they are in |11>, the outcome is '11' with 100% probability.
    -   Note: The order of measurement doesn't matter for the final probabilities, but conventionally earlier measured qubit = higher bit.
    -   Here, M(q[0]) is first, so it's the highest bit (index 0). M(q[1]) is lowest bit.
    -   Result is q[0]=1, q[1]=1 -> '11'.

2.  **Format the output:**
    -   Use 3-8 lines.
    -   Step-by-step state evolution.
    -   Final state and probabilities.
    -   Predicted probability distribution at the end.

3.  **Drafting the steps:**
    -   Initial state |000>. X(q[2]) creates |001>.
    -   H gates put q[0],q[1] into superposition and q[2] into |->: 1/2(|00>+|01>+|10>+|11>) ⊗ |->

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'DJ algorithm with xor balanced oracle yields |11⟩. P(|11⟩) = 1.0 at index 3.'}

## isqTrain/3031

- task_id: `isqTrain/3031`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1887`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[4];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    X(q[3]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |0000>. The `H(q[0])` gate creates a superposition: 1/√2 (|0000> + |1000>).
2. The sequence of CNOT gates propagates the state of q[0] to q[1], q[2], and q[3], resulting in a GHZ state: 1/√2 (|0000> + |1111>).
3. The `X(q[3])` gate flips the 4th qubit, transforming the state to: 1/√2 (|0001> + |1110>).
4. Measurement of all qubits collapses this superposition into one of the two basis states with equal probability.

Predicted probability distribution:
{'0001': 0.5, '1110': 0.5}

### Reference answer

{'predicted_probs': {'0001': 0.5, '1110': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3829

- task_id: `isqTrain/3829`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5223`

### Prompt

I need an isQ program to Demonstrate phase kickback using controlled-Z gate.
1. Put control qubit q[0] in |+> state
2. Prepare target q[1] in eigenstate |1>
3. Apply controlled-Z
4. Apply H to control and measure both qubits.
Explanation: Z|1> = -|1>, phase π kicked back

### Chain-of-thought reasoning

## Reasoning
Goal: Demonstrate phase kickback by applying a controlled-Z to a |+> control and a |1> target, which kicks back a π phase to the control.
Qubits: 2 qubits are used: q[0] (control) and q[1] (target). Both qubits are measured at the end.
State Evolution:
- Initial state: |00>
- H(q[0]): |00> → |+0> = (|00> + |10>)/√2
- X(q[1]): |+0> → |+1> = (|01> + |11>)/√2
- ctrl Z(q[0], q[1]): The Z gate applied to target q[1] in |1> yields -|1>, kicking a -1 phase back to the |1> component of the control, changing the state to (|01> - |11>)/√2
- H(q[0]): The second Hadamard converts the relative phase on the control into a computational basis change: (|01> - |11>)/√2 → -|11>
Outcome: The final state is exactly |11>. Thus, measuring the circuit yields bitstring '11' with 100% probability.

## isqTrain/15

- task_id: `isqTrain/15`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1898`

### Prompt

帮我写一个isQ程序：implements a variant of the qft_subcircuit pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a quantum circuit implemented in isQ. Let me analyze the given circuit:

1. We have 4 qubits: q[0], q[1], q[2], q[3]
2. The circuit applies X(q[2]) to set q[2] to |1>
3. Then applies qft3 to q[0], q[1], q[2]
4. Measures all 4 qubits

The qft3 procedure implements a 3-qubit QFT on qubits a, b, c:
- H(a)
- ctrl Rz(pi/2, b, a) - controlled phase from b to a
- ctrl Rz(pi/4, c, a) - controlled phase from c to a
- H(b)
- ctrl Rz(pi/2, c, b) - controlled phase from c to b
- H(c)
- swap(a, c) via three CNOTs using 3 CNOTs

Let me trace through:

Initial state: |0000>
After X(q[2]): |0010>

Now apply qft3(q[0], q[1], q[2]):

The 3-qubit QFT transforms |001> (which is computational basis state |1>) into a uniform superposition with specific phases.

For a 3-qubit QFT, the transformation of |1> = |001> (in qubit order q[2], q[1], q[0]) should give us:
QFT|001> = (1/√8) Σ_k ω^k |k> where ω = e^(2πi/8) and the sum is over k with phase depending on k*1.

Actually, let me be more careful. The QFT on n qubits transforms |j> to (1/√N) Σ_k e^(2πijk/N) |k>.

For |j=1> with N=8:
|ψ> = (1/√8) Σ_{k=0}^{7} e^(2πi*1*k/8) |k>

But wait, the swap (three-CNOT decomposition) at the end reverses the qubit order, so the final state will have the bit-reversed version.

Let me trace more carefully with the actual gates:

After X(q[2]): q[0]=0, q[1]=0, q[2]=1, q[3]=0
State: |0>_q0 ⊗ |0>_q1 ⊗ |1>_q2 ⊗ |0>_q3 = |0010>

qft3(q[0], q[1], q[2]):
- H(q[0]): q[0] is |0>, so H|0> = |+> = (|0> + |1>)/√2
  State: (|0> + |1>)/√2 ⊗ |0> ⊗ |1> ⊗ |0>
  = (|0010> + |1010>)/√2

- ctrl Rz(pi/2, q[1], q[0]): q[1] controls, q[0] is target. Since q[1]=|0>, nothing happens.

- ctrl Rz(pi/4, q[2], q[0]): q[2] controls, q[0] is target. Since q[2]=|1>, apply Rz(pi/4) to q[0].
  Rz(pi/4)|0> = |0>, Rz(pi/4)|1> = e^(iπ/8)|1>
  State: (|0010> + e^(iπ/8)|1010>)/√2

Wait, I need to reconsider. The ctrl syntax in isQ: `ctrl Rz(pi/2.0, b, a)` - what's the control and what's the target?

Looking at the isQ syntax, `ctrl Rz(theta, control, target)` or is it `ctrl Rz(theta, target, control)`?

From the reference: "ctrl Rz(pi/2.0, b, a)" - this seems to mean control on b, apply Rz to a.

So:
- ctrl Rz(pi/2, q[1], q[0]): if q[1] is |1>, apply Rz(pi/2) to q[0]
- Since q[1]=|0>, nothing happens

- ctrl Rz(pi/4, q[2], q[0]): if q[2] is |1>, apply Rz(pi/4) to q[0]
- Since q[2]=|1>, apply Rz(pi/4) to q[0]

Rz(θ) = [[1, 0], [0, e^(iθ)]]
So Rz(π/
