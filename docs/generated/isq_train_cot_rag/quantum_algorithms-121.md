# ISQ training COT RAG corpus: quantum_algorithms shard 121

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3508

- task_id: `isqTrain/3508`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3691`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```
import std;

qbit q[2];

procedure main() {
    X(q[0]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations:** The circuit initializes 2 qubits (q[0], q[1]) in the |0> state. An X gate is applied to q[0]. Both qubits are then measured.
2. **State Evolution:**
   - Initial state: |q[0]> ⊗ |q[1]> = |0> ⊗ |0> = |00>
   - Apply X to q[0]: X|0> = |1>, so the state becomes |1> ⊗ |0> = |10>
3. **Final State:** The system is in the definite state |10> before measurement.
4. **Probability Distribution:** Since the state is exactly |10>, measuring it will yield '1' for q[0] and '0' for q[1] with certainty. Following the "earlier measured qubit = higher bit" convention (q[0] is the higher bit), the bitstring is '10' (index 2).

**Predicted probability distribution:**
- **10: 100%** (or index 2: 1.0)

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'The output is |10> with probability 1.0'}

## isqTrain/3419

- task_id: `isqTrain/3419`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `basis_change`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2561`

### Prompt

用isQ实现the 3-qubit phase-flip code in isQ with a Z error on q[1] and syndrome-based correction.

Steps:
1. Encode |0_L>: CNOT fan-out then H on all 3 qubits
2. Inject Z error on q[1]
3. Decode to computational basis: H on all 3
4. Syndrome extraction on 2 ancilla qubits
5. Correct the error using Toffoli gate
6. Re-encode and then decode for final measurement

Simplification: after H transform, a Z error becomes an X error, so the correction in computational basis is the same as bit-flip code.

Declare q[3] and anc[2]. Measure only q[0..2]. Expected: |000>.

### Chain-of-thought reasoning

## Reasoning
Goal: Encode |0⟩ into |+++⟩ (3-qubit phase-flip code), inject a Z error on q[1], then detect and correct it via syndrome measurement.

Qubits: q[3] (data) + anc[2] (syndrome); only q[0..2] are measured.

State evolution:
- |000⟩|00⟩ → CNOT fan-out → |000⟩|00⟩ → H⊗3 → |+++⟩|00⟩
- Z(q[1]): |+++⟩|00⟩ → |+−+⟩|00⟩ (phase flip on q[1])
- H⊗3 (decode): |+−+⟩|00⟩ → |010⟩|00⟩ — the Z error is now an X error
- Syndrome extraction via CNOTs: anc[0] parity(q[0]⊕q[1])=1, anc[1] parity(q[1]⊕q[2])=1 → syndrome |11⟩, pointing to q[1]
- Toffoli(anc[0], anc[1], q[1]): flips q[1] since both ancillae are |1⟩ → |000⟩|11⟩

Expected: |000⟩ with probability 1.0, confirming the phase-flip was successfully corrected.

## isqTrain/70

- task_id: `isqTrain/70`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `3983`

### Prompt

Help me write isQ code that implements the bell_state_preparation pattern but with a different initial state preparation (flip q[[0]] -> q[1]).

### Chain-of-thought reasoning

The user wants a reasoning section for the given isQ program that implements a modified Bell state preparation.
The circuit prepares a Bell state, encodes a "11" state (flipping q[0] and q[1] relative to the standard basis, wait, the prompt says "flip q[[0]] -> q[1]" but the code actually does `Z(q[0]); X(q[1]);`, wait, `Z(q[0]); X(q[1]);` is `Z` on 0 and `X` on 1? No, wait, Z(q[0]) maps |0> to |0>, |1> to -|1>. Let's trace the standard Bell state encoding).
Wait, the prompt says "Write an isQ program that implements the bell_state_preparation pattern but with a different initial state preparation (flip q[[0]] -> q[1])." but the circuit implementation code is already provided. Oh, I am supposed to generate reasoning for the *circuit implementation* provided, not write the code myself! Let me re-read the prompt.
Ah, the user wants me to "Generate a reasoning section that explains...". So I must analyze the code provided in the circuit implementation.

Let's trace the circuit implementation:
1. `H(q[0]); CNOT(q[0], q[1]);` creates the Bell state $\Phi^+ = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
2. `Z(q[0]); X(q[1]);` applies Z to q[0] and X to q[1].
Wait, applying Z and X to a Bell state is Superdense coding!
Alice encodes 2 classical bits into 1 qubit, but here it's `Z(q[0]); X(q[1]);`? Wait, typically Superdense coding applies gates only to Alice's qubit, then sends it to Bob who does CNOT and H. Here, `Z(q[0])` and `X(q[1])` are applied? Wait, if Alice holds q[0], she would apply `Z` and `X` to q[0]!
Let's trace:
Initial: $|00\rangle$
H(q[0]): $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$
CNOT(q[0], q[1]): $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$
Now, `Z(q[0]); X(q[1]);`
Z(q[0]): $\frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$
X(q[1]): $\frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$
Wait, then we decode:
CNOT(q[0], q[1]):
$\frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$? Let's trace carefully:
State before CNOT is $|01\rangle - |10\rangle$.
CNOT(0,1) on $|01\rangle$ is $|01\rangle \to |01\rangle$ (since q[0] is 0). Wait, no, CNOT(0,1) has q[0] as control. So $|01\rangle \to |01\rangle$.
CNOT(0,1) on $|10\rangle$ is $|10\rangle \to |11\rangle$.
So the state becomes $\frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$.
Then H(q[0]):
H on $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) |1\rangle = |-\rangle |1\rangle$.
Wait, $\frac{1}{\sqrt{2}}(|0\rangle(|1\rangle) - |1\rangle(|1\rangle)) = |-\rangle |1\rangle$.
H on $|-\rangle$ is $|1\rangle$.
So the state becomes $|1\rangle |1\rangle = |11\rangle$.
Wait, the predicted output is {|11>: 1.0}. This matches perfectly.

Let's write down the reasoning steps clearly.
1. Goal: The circuit prepares a Bell state, applies `Z` and `X` operations to encode information (analogous to superdense coding), and decodes it to yield the `|11>` state with certainty.
2. Qubits: 2 qubits are used, and both are measured.
3. Evolution:
- Initialize 2 qubits in `|00>`.
- `H(q[0]); CNOT(q[0], q[1]);` creates the Bell state `(1/sqrt(2))

## isqTrain/2722

- task_id: `isqTrain/2722`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2530`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
oracle bool[4] g(bool a[4]) {
    bool res[] = [a[0], a[1], a[2], false];
    return res;
}
qbit q[4], res[4];

procedure main(){
    H(q);
    g(q, res);
    H(q); 
    print M(q);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step analysis of a given isQ quantum program, explaining the state evolution and calculating the final measurement probabilities for the `q` qubits.

2.  **Analyze the isQ Code**:
    *   `qbit q[4], res[4];` -> 4 qubits in `q`, 4 qubits in `res`. Total 8 qubits, but only `q` is manipulated non-trivially and measured.
    *   `H(q);` -> Apply Hadamard to all 4 qubits in `q`. State of `q` goes from $|0000\rangle$ to $\frac{1}{4} \sum_{x \in \{0,1\}^4} |x\rangle$. State of `res` remains $|0000\rangle$.
    *   `g(q, res);` -> This is an oracle. The oracle definition is `bool res[] = [a[0], a[1], a[2], false];`.
        *   Wait, let's look at the oracle syntax. `oracle bool[4] g(bool a[4])` means it computes a classical function. In isQ, when an oracle is called like `g(q, res)`, it performs a transformation $|x\rangle |y\rangle \to |x\rangle |y \oplus g(x)\rangle$.
        *   Let's verify this. $g(x) = (x_0, x_1, x_2, 0)$.
        *   Initial joint state: $\frac{1}{4} \sum_x |x\rangle_q \otimes |0000\rangle_{res}$.
        *   After oracle: $\frac{1}{4} \sum_x |x\rangle_q \otimes |x_0, x_1, x_2, 0\rangle_{res}$.
        *   Notice that `res` qubits just become entangled copies of the first 3 `q` qubits.
    *   `H(q);` -> Apply Hadamard to all 4 `q` qubits again.
        *   Since `res` holds $x_0, x_1, x_2$, and `q` holds a superposition of $x$, the second `H` on `q` creates a superposition of $z$.
        *   Let's trace it carefully. The state is $\frac{1}{4} \sum_{x \in \{0,1\}^4} |x\rangle_q |x_0 x_1 x_2 0\rangle_{res}$.
        *   Apply $H^{\otimes 4}$ to `q`:
            $|x\rangle_q \to \frac{1}{4} \sum_{z \in \{0,1\}^4} (-1)^{x \cdot z} |z\rangle_q$.
        *   Total state: $\frac{1}{16} \sum_{x, z} (-1)^{x \cdot z} |z\rangle_q |x_0 x_1 x_2 0\rangle_{res}$.
    *   Wait, what is the probability of measuring `q`?
        *   The measurement is `M(q)`. We trace out `res`, or just find the marginal probability of `q` being in state $|z\rangle$.
        *   The reduced density matrix of `q` is $\sum_x |\frac{1}{16}|^2 |z\rangle \langle z|$ for each $x$? No.
        *   Let's write the state as $\frac{1}{16} \sum_{z} |z\rangle_q \otimes \sum_x (-1)^{x \cdot z} |x_0 x_1 x_2 0\rangle_{res}$.
        *   The probability of measuring `q` in state $|z\rangle$ is the norm squared of $\sum_x (-1)^{x \cdot z} |x_0 x_1 x_2 0\rangle_{res}$, multiplied by $(1/16)^2$.
        *   The states $|x_0 x_1 x_2 0\rangle$ for different $x$ are orthogonal. Thus, the sum $\sum_x (-1)^{x \cdot z} |x_0 x_1 x_2 0\rangle$ has length $\sqrt{16} = 4$.
        *   Therefore, the probability of $|z\rangle$ is $(1/16)^2 \times 16 = 1/16$.
        *   Since there are 16 possible outcomes for $

### Reference answer

{'predicted_probs': {'0000': 0.12500000000000003, '0001': 0.12500000000000003, '0010': 0.12500000000000003, '0011': 0.12500000000000003, '0100': 0.12500000000000003, '0101': 0.12500000000000003, '0110': 0.12500000000000003, '0111': 0.12500000000000003}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/4561

- task_id: `isqTrain/4561`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1873`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;

oracle bool[1] f(bool x[3]) {
    
    bool res[] = [x[1] != x[2]];
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
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the request:**
    *   Task: Output prediction of an isQ quantum program.
    *   Input program: A Deutsch-Jozsa style circuit, or an oracle-based phase kickback circuit. Wait, let's look closer.
    *   Program details:
        *   `oracle bool[1] f(bool x[3]) { bool res[] = [x[1] != x[2]]; return res; }` -> This means the function $f(x_0, x_1, x_2) = x_1 \oplus x_2$. Wait, the input size is 3, but only $x_1$ and $x_2$ are used. The oracle doesn't depend on $x_0$.
        *   `X(anc[0]); H(anc[0]);` -> Puts ancilla in $|-\rangle$ state.
        *   `H(q[0]); H(q[1]); H(q[2]);` -> Puts main register in uniform superposition.
        *   `f(q, anc);` -> Applies the phase oracle $U_f |x\rangle|-\rangle = (-1)^{f(x)} |x\rangle|-\rangle$.
        *   `H(q[0]); H(q[1]); H(q[2]);` -> Applies Hadamard transform again.
        *   `H(q[0]); Z(q[0]); H(q[0]);` -> This is exactly the $X$ gate on $q[0]$. $HZH = X$.
        *   Measurements: `M(q[0]); M(q[1]); M(q[2]);`
    *   Output: 3-15 lines explaining state evolution, starting with "## Circuit Analysis", ending with predicted probability distribution.

2.  **Step-by-step state evolution:**
    *   Initial state: $|000\rangle \otimes |0\rangle$
    *   After $X \otimes H$ on ancilla and $H^{\otimes 3}$ on main:
        *   Main: $\frac{1}{2\sqrt{2}} \sum_{x \in \{0,1\}^3} |x\rangle$
        *   Ancilla: $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
    *   After `f(q, anc)`: The state acquires a phase $(-1)^{f(x)}$. Here $f(x) = x_1 \oplus x_2$.
        *   Wait, $x_1 \oplus x_2 = 1$ for $x_1 \neq x_2$, and $0$ for $x_1 = x_2$.
        *   So phase is $-1$ when $x_1 \neq x_2$.
        *   Main register: $\frac{1}{2\sqrt{2}} \sum_{x \in \{0,1\}^3} (-1)^{x_1 \oplus x_2} |x\rangle$
        *   Ancilla: $|-\rangle$
    *   After $H^{\otimes 3}$ on main: The state transforms from $|x\rangle$ basis back to $|z\rangle$ basis.
        *   We know $H^{\otimes n} \sum_x (-1)^{f(x)}|x\rangle = \sum_z \hat{f}(z) |z\rangle$, where $\hat{f}(z)$ is the Fourier transform of $f(x)$.
        *   Actually, it's simpler. The phase is $(-1)^{x_1 \oplus x_2}$. This is just $Z_1 Z_2$ applied to the uniform superposition, then Hadamard.
        *   Wait: $H^{\otimes 3} (Z_1 Z_2) H^{\otimes 3} |000\rangle$. Since $Z_i = H X_i H$, this is equivalent to $(H Z_1 H)(H Z_2 H) |000\rangle = X_1 X_2 |000\rangle = |010\rangle + |011\rangle$? No.
        *   Let's do the math:
            $H^{\otimes 3}$ applied to $\sum_x (-1)^{x_1 \oplus x_2} |x\rangle$.
            For a given computational basis state $|z_0 z_1 z_2\rangle$, the amplitude is $\frac{1}{8} \sum_x (-1)^{x_1 \oplus x_2} (-1)^{x \

### Reference answer

{'predicted_probs': {'111': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|111>) = 1.0000.'}

## isqTrain/2854

- task_id: `isqTrain/2854`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4064`

### Prompt

Create an isQ quantum circuit that implements a Toffoli gate with both controls set to |1>. Apply the appropriate gates to 3 qubits and measure all of them.

Requirements:
- Declare `qbit q[3];` at global scope.
- Use `procedure main()` as entry point.
- Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a Toffoli gate with both controls in |1> state and measure the result.
We use 3 qubits (q[0], q[1] as controls, q[2] as target); all are measured.
Initial state: |000⟩. After X(q[0]): |100⟩. After X(q[1]): |110⟩.
Toffoli(q[0], q[1], q[2]) flips q[2] since both controls are |1⟩: |110⟩ → |111⟩.
Final state |111⟩ yields measurement outcome 111 with probability 1.0.

## isqTrain/1174

- task_id: `isqTrain/1174`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2022`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;

// IQP circuit: H -- diagonal -- H
qbit q[3];

procedure main() {
    // First Hadamard layer: create superposition
    H(q[0]); H(q[1]); H(q[2]);
    // Diagonal gate layer (commuting Z-basis gates)
    // Single-qubit phase gates
    T(q[0]); T(q[1]); T(q[2]);
    // Two-qubit diagonal gates (CZ)
    CZ(q[0], q[1]);
    CZ(q[1], q[2]);
    // Second Hadamard layer
    H(q[0]); H(q[1]); H(q[2]);
    // Measure all qubits
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

The user wants to analyze an isQ program that represents an IQP (Instantaneous Quantum Polynomial) circuit.
The circuit is: H-H-H, T-T-T, CZ-CZ, H-H-H.
Wait, let's trace the state.
Initial state: |000>
After H on all 3: (1/sqrt(8)) * sum_{x in {0,1}^3} |x> = |+++>

Then T on all 3: applies phase $e^{i \pi (x_0 + x_1 + x_2) / 4}$ to each $|x_0 x_1 x_2>$.
Then CZ(q[0], q[1]): applies phase -1 to $|x_0 x_1 x_2>$ if $x_0 x_1 = 1$.
Then CZ(q[1], q[2]): applies phase -1 to $|x_0 x_1 x_2>$ if $x_1 x_2 = 1$.

Overall phase factor for $|x_0 x_1 x_2>$ is:
$\exp(i \frac{\pi}{4} (x_0 + x_1 + x_2) + i \pi (x_0 x_1 + x_1 x_2))$
Wait, let's consider the global phase and just focus on the relative phases.
Actually, $|+\rangle \to H T H |+\rangle$. Let's evaluate $H T H$.
Wait, the state is a product state if there were no CZs, but CZs introduce entanglement.
Let's trace carefully.
The state after H on all is $|+\rangle|+\rangle|+\rangle$.
Then T gates: $T|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + e^{i\pi/4}|1\rangle)$.
The CZ gates are diagonal. They apply to the state $|x_0 x_1 x_2\rangle$:
$(-1)^{x_0 x_1} (-1)^{x_1 x_2} |x_0 x_1 x_2\rangle$.
So the state is $\frac{1}{\sqrt{8}} \sum_{x_0, x_1, x_2 \in \{0,1\}} e^{i \frac{\pi}{4} (x_0+x_1+x_2)} (-1)^{x_0 x_1 + x_1 x_2} |x_0 x_1 x_2\rangle$.
Then apply H on all again.
The amplitude for $|y_0 y_1 y_2\rangle$ is:
$\frac{1}{8} \sum_{x_0, x_1, x_2 \in \{0,1\}} (-1)^{x_0 y_0 + x_1 y_1 + x_2 y_2} e^{i \frac{\pi}{4} (x_0+x_1+x_2)} (-1)^{x_0 x_1 + x_1 x_2}$.

Let's compute this for each $y_0 y_1 y_2$.
For a single bit, $x \in \{0, 1\}$:
Amplitude $A(y_0, y_1, y_2) = \frac{1}{8} \sum_{x_0} \sum_{x_1} \sum_{x_2} (-1)^{x_0(y_0 + x_1) + x_1(y_1 + x_2) + x_2 y_2} e^{i \frac{\pi}{4}(x_0+x_1+x_2)}$.

Let's compute the inner sums.
For $x_2$: $(-1)^{x_2(y_2 + x_1)} e^{i \frac{\pi}{4} x_2} = 1 + e^{i \frac{\pi}{4}} (-1)^{y_2 + x_1} = 1 + e^{i \frac{\pi}{4}} (-1)^{y_2} (-1)^{x_1}$.
Let $\alpha = 1 + \beta (-1)^{y_2} (-1)^{x_1}$, where $\beta = e^{i \frac{\pi}{4}} = \frac{1+i}{\sqrt{2}}$.
Since $(-1)^{x_1}$ is $\pm 1$, the possible values for $x_2$ sum are:
$1 + \beta (-1)^{y_2}$ and $1 - \beta (-1)^{y_2}$

### Reference answer

{'predicted_probs': {'0': 0.14330582617584073, '1': 0.1066941738241592, '2': 0.23169417382415927, '3': 0.018305826175840777, '4': 0.1066941738241592, '5': 0.1433058261758408, '6': 0.018305826175840794, '7': 0.23169417382415916}, 'explanation': 'Parametric variant of isqEval/444. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3788

- task_id: `isqTrain/3788`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1718`

### Prompt

帮我写一个isQ程序：the Deutsch-Jozsa algorithm for a 2-input balanced oracle with truth table [0, 1, 0, 1]. Use the oracle keyword, prepare output in |-> state, apply Hadamard-oracle-Hadamard, measure input qubits. Result should be non-zero (balanced).

### Chain-of-thought reasoning

Let me analyze this Deutsch-Jozsa algorithm step by step.

The goal is to implement Deutsch-Jozsa for a 2-input balanced oracle with truth table [0, 1, 0, 1].

We have 3 qubits: q[0] and q[1] are input qubits, q[2] is the output qubit.

The oracle f(2, 1) = [0, 1, 0, 1] means:
- f(00) = 0
- f(01) = 1
- f(10) = 0
- f(11) = 1

This is balanced because half the outputs are 0 and half are 1.

Let me trace the state evolution:

1. Initial state: |000⟩

2. Apply X to q[2], then H to q[2]:
   |000⟩ → X(q[2]) → |001⟩ → H(q[2]) → (1/√2)(|000⟩ - |001⟩) = |00⟩|−⟩

3. Apply H to q[0] and q[1]:
   |0⟩|0⟩|−⟩ → (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)|−⟩

4. Apply oracle f:
   The oracle maps |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩
   Since output is in |−⟩ state, phase kickback occurs:
   |x⟩|−⟩ → (-1)^f(x)|x⟩|−⟩
   
   So the state becomes:
   (1/2)((-1)^0|00⟩ + (-1)^1|01⟩ + (-1)^0|10⟩ + (-1)^1|11⟩)|−⟩
   = (1/2)(|00⟩ - |01⟩ + |10⟩ - |11⟩)|−⟩

5. Apply H to q[0] and q[1]:
   H|00⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
   H|01⟩ = (|00⟩ - |01⟩ + |10⟩ - |11⟩)/2
   H|10⟩ = (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
   H|11⟩ = (|00⟩ - |01⟩ - |10⟩ + |11⟩)/2
   
   So H⊗2 applied to (|00⟩ - |01⟩ + |10⟩ - |11⟩)/2:
   
   Let me compute this more carefully:
   |00⟩ - |01⟩ + |10⟩ - |11⟩ = (|0⟩ + |1⟩)⊗|0⟩ - (|0⟩ + |1⟩)⊗|1⟩ = (|0⟩ + |1⟩)⊗(|0⟩ - |1⟩)
   
   Applying H⊗2:
   H(|0⟩ + |1⟩) = √2|0⟩ (since H|0⟩ = |+⟩ and H|1⟩ = |−⟩, so |+⟩ + |−⟩ = √2|0⟩)
   H(|0⟩ - |1⟩) = √2|1⟩ (since |+⟩ - |−⟩ = √2|1⟩)
   
   So the input qubits become √2|0⟩ ⊗ √2|1⟩ = 2|01⟩
   
   Wait, but we have 1/2 in front, so:
   (1/2) × 2|01⟩|−⟩ = |01⟩|−⟩

   Hmm, that would give deterministic measurement of |010⟩ or |011⟩ depending on the output qubit state.

Actually, let me recalculate. The oracle has truth table [0, 1, 0, 1] for the mapping f(00)=0, f(01)=1, f(10)=0, f(11)=1.

Phase kickback with |−⟩:
|x⟩|−⟩ → (-1)^f(x)|x⟩|−⟩

So:
|00⟩ → +|00⟩ (f(00)=0)
|01⟩ → -|01⟩ (f(01)=1)
|10⟩ → +|10⟩ (f(10)=0)
|11⟩ → -|11⟩ (f(11)=1)

After oracle: (1/2)(|00⟩ - |01⟩ + |10⟩ - |11⟩)|−⟩

The input state can be written as:
(1/2)[(|0⟩ + |1⟩)|0⟩ - (|0⟩ + |1⟩)|1⟩]
= (1/2)(|0⟩ +

## isqTrain/843

- task_id: `isqTrain/843`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `finite_field_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4223`

### Prompt

Implement the following in isQ: implements the gfp_multiplication pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

Let me analyze this GF(3) multiplication circuit with reversed measurement order.

The task is to implement GF(3) multiplication where:
- a = 1 (encoded as binary 01 in q[0:2])
- b = 2 (encoded as binary 10 in q[2:4])
- Product register is q[4:6]

GF(3) multiplication by 1 is the identity operation, so the product should equal b.

The circuit should:
1. X(q[0]) - sets a = 1 (binary 01)
2. X(q[3]) - sets b = 2 (binary 10)
3. CNOT(q[2], q[4]) - copies q[2] (0) to q[4]
4. CNOT(q[3], q[5]) - copies q[3] (1) to q[5]
5. M(q[5]) - measures first (higher bit in bitstring)
6. M(q[4]) - measures second (lower bit in bitstring)

With reversed measurement order for q, we need to swap the measurement order:
- M(q[4]) first (higher bit)
- M(q[5]) second (lower bit)

Wait, let me re-read the task. The reference shows:
- M(q[5]) first
- M(q[4]) second

So the current bitstring interpretation is: q[5] is higher bit, q[4] is lower bit.
If q[5]=1 and q[4]=0, the bitstring is 10 (binary) = 2.

For reversed measurement order:
- M(q[4]) first (higher bit)
- M(q[5]) second (lower bit)

If q[4]=0 and q[5]=1, the bitstring would be 01 (binary) = 1.

But The predicted output still |10>: 1.0, so I need to think about this more carefully.

Actually, looking at the predicted output: {|10>: 1.0}

With The implementation's measurement order (M(q[5]) first, M(q[4]) second):
- q[5] is measured first → higher bit position
- q[4] is measured second → lower bit position
- q[5] = 1 (after CNOT from q[3] which is 1)
- q[4] = 0 (after CNOT from q[2] which is 0)
- Bitstring = 10

For "reversed measurement order for q", we swap:
- M(q[4]) first → higher bit position
- M(q[5]) second → lower bit position
- q[4] = 0 → higher bit = 0
- q[5] = 1 → lower bit = 1
- Bitstring = 01

So with reversed measurement order, the predicted output would be |01>: 1.0, not |10>.

But the task says the expected measurement probabilities are {|10>: 1.0}. This is confusing.

Let me re-read: "Write an isQ program that implements the gfp_multiplication pattern with a different measurement ordering (reversed measurement order for q)."

Maybe the task is asking me to write the code that achieves |10>: 1.0 with reversed measurement order. In that case, I might need to adjust the CNOT connections or the inputs.

Or perhaps I'm overthinking this. Let me just trace through The implementation:

Initial state: |000000>

After X(q[0]): |000001> (but wait, this seems wrong for encoding)

Actually, the qubit ordering might be:
- q[0], q[1] = a register (a = 1 → binary 01 → q[0]=1, q[1]=0)
- q[2], q[3] = b register (b = 2 → binary 10 → q[2]=0, q[3]=1)
- q[4], q[5] = product register

So after X(q[0]): q[0]=1, encoding the LSB of a=1
After X(q[3]): q[3]=1, encoding the MSB of b=2

State after initialization: |001010> (q[0]=1, q[3]=1, others 0)

CNOT(q[2], q[4]): q[2]=0, so q[4] stays 0
CNOT(q[3], q[5]): q[3]=1, so q[5] flips to 1

Final state of product qubits: q[4]=0, q[5]=1

Now for measurement:
- Reference: M(q[5]) first (bit position 1), M(q[4]) second (bit position 0)
  -

## isqExpand/algo/201

- task_id: `isqExpand/algo/201`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `superdense_coding`, `bell_state`, `entanglement`, `encoding`, `quantum_communication`
- source: `isq_expansion`
- dataset_index: `1623`

### Prompt

帮我写一个isQ程序：an isQ superdense coding circuit that encodes the message '01' into one qubit of a Bell pair. Create a Bell pair (H then CNOT), apply the appropriate encoding gate to q[0] for the classical message '01', then decode by reversing the Bell state preparation (CNOT then H). Use 2 qubits.

### Chain-of-thought reasoning

Superdense coding allows transmitting 2 classical bits by sending 1 qubit when the parties share a Bell pair. The protocol: (1) Create Bell pair |Phi+> = (|00>+|11>)/sqrt(2) via H(q0) then CNOT(q0,q1). (2) To encode '01', Alice applies X to her qubit q[0], transforming |Phi+> into |Psi+> = (|01>+|10>)/sqrt(2). (3) Bob decodes by applying CNOT(q0,q1) then H(q0). After CNOT: |Psi+> -> (|01>+|11>)/sqrt(2). After H on q0: H(|0>+|1>)|1>/2 + H(|0>-|1>)|1>/2 = (|01>+|11>+|01>-|11>)/2 = |01>. The final state is deterministically |01>, so the probability distribution is [0, 1, 0, 0] for outcomes |00>,|01>,|10>,|11>.
