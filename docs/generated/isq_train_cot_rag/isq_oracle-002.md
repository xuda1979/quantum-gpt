# ISQ training COT RAG corpus: isq_oracle shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/217

- task_id: `isqTrain/217`
- task_type: `code_generation`
- category: `isq_oracle`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5271`

### Prompt

Write isQ code for the following quantum task: implements a variant of the amplitude_amplification pattern using anc[1] -> anc[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit implements Grover's algorithm with one iteration on 2 qubits, searching for the state |11⟩.

**Qubits:**
- `q[2]` - main register (measured)
- `anc[3]` - ancilla register (only anc[0] is used as oracle workspace, anc[1] and anc[2] are unused ground state)

**Step-by-step evolution:**

1. Initial state: |00⟩_q ⊗ |000⟩_anc

2. X(anc[0]): |00⟩_q ⊗ |100⟩_anc

3. H(anc[0]): |00⟩_q ⊗ (|0⟩-|1⟩)/√2 ⊗ |00⟩_anc[1:2] = |00⟩_q ⊗ |−⟩_anc[0] ⊗ |00⟩_anc[1:2]

4. H(q[0]), H(q[1]): (|00⟩+|01⟩+|10⟩+|11⟩)/2 ⊗ |−⟩ ⊗ |00⟩

5. grover_oracle(q, anc): This flips the phase of |11⟩ by applying a controlled operation. Since oracle checks x[0] && x[1], it marks |11⟩. The oracle uses anc[0] in |−⟩ state for phase kickback.
   Result: (|00⟩+|01⟩+|10⟩-|11⟩)/2 ⊗ |−⟩ ⊗ |00⟩

6. H(q[0]), H(q[1]): Applies Hadamard to all states.
   The state becomes: after H⊗2 on (|00⟩+|01⟩+|10⟩-|11⟩)/2
   
   H⊗2 applied:
   - |00⟩ → (|00⟩+|01⟩+|10⟩+|11⟩)/2
   - |01⟩ → (|00⟩-|01⟩+|10⟩-|11⟩)/2
   - |10⟩ → (|00⟩+|01⟩-|10⟩-|11⟩)/2
   - |11⟩ → (|00⟩-|01⟩-|10⟩+|11⟩)/2
   
   Sum: (|00⟩+|01⟩+|10⟩+|11⟩ + |00⟩-|01⟩+|10⟩-|11⟩ + |00⟩+|01⟩-|10⟩-|11⟩ - |00⟩+|01⟩+|10⟩-|11⟩)/4
   = (|00⟩ + |01⟩ + |10⟩ - |11⟩ + |01⟩ + |10⟩ + |01⟩ + |10⟩)/4 ... let me recalculate.
   
   Actually let me be more careful:
   |00⟩ coefficient: (1+1+1-1)/4 = 2/4 = 1/2
   |01⟩ coefficient: (1-1+1+1)/4 = 2/4 = 1/2
   |10⟩ coefficient: (1+1-1+1)/4 = 2/4 = 1/2
   |11⟩ coefficient: (1-1-1-1)/4 = -2/4 = -1/2
   
   So state: (|00⟩+|01⟩+|10⟩-|11⟩)/2 ⊗ |−⟩ ⊗ |00⟩

7. X(q[0]), X(q[1]): Apply X to both qubits
   |00⟩ → |11⟩, |01⟩ → |10⟩, |10⟩ → |01⟩, |11⟩ → |00⟩
   State: (|11⟩+|10⟩+|01⟩-|00⟩)/2

8. ctrl my_z(q[0], q[1]): This is a controlled-Z where q[0] controls, applying Z to q[1]. When q[0]=|1⟩, apply Z to q[1].
   
   Wait, `ctrl my_z(q[0], q[1])` means q[0] is the control and my_z is applied to q[1]. my_z is just Z gate.
   
   So this is CZ(q[0], q[1]): flips sign when both are |1⟩.
   
   |11⟩ → -|11⟩, |10⟩ → |10⟩, |01⟩ → |01⟩, |00⟩ → |00⟩
   State: (-|11⟩+|10⟩+|01⟩-|00⟩)/2

9. X(q[0]), X(q[1]):
   |11⟩ → |00⟩, |10⟩ → |01⟩, |

## isqTrain/213

- task_id: `isqTrain/213`
- task_type: `code_generation`
- category: `isq_oracle`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2385`

### Prompt

Help me write isQ code that implements the oracle_boolean pattern but with a different initial state preparation (flip q[[0, 1]] -> q[2]).

### Chain-of-thought reasoning

## Reasoning
The circuit implements a boolean oracle computing the majority function, initializing the system with a prepared input state.
Four qubits are used (`q[0], q[1], q[2]`, and `anc[0]`), all of which are measured at the end to reveal the input and computed output.
The initial state is |0000>. Applying the X(q[2]) gate flips the third qubit, evolving the state to |0010>.
The `majority` oracle calculates $(x_0 \land x_1) \lor (x_0 \land x_2) \lor (x_1 \land x_2)$ for the input $x = 001$, which evaluates to 0.
This result is XORed into the ancilla qubit, leaving the ancilla in the |0> state and the overall system in the exact state |0010>.
Since the final quantum state is a deterministic computational basis state, measurement yields the bitstring 0010 with a probability of 1.0.

## isqTrain/207

- task_id: `isqTrain/207`
- task_type: `code_generation`
- category: `isq_oracle`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5795`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the oracle_boolean pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement an XOR oracle variant with an expanded 4-qubit data register, computing the XOR of `q[0]` and `q[1]` into an ancilla qubit.
2. Qubits: 5 total (`q[0..3]` + `anc[0]`), all measured.
3. State evolution:
   - Initial: |00000⟩
   - After X(q[0]): |10000⟩
   - xor_oracle computes `q[0] ⊕ q[1]` = 1 ⊕ 0 = 1, flipping ancilla: |10001⟩
4. Final measurement yields |10001⟩ with probability 1.0.

## isqTrain/652

- task_id: `isqTrain/652`
- task_type: `code_generation`
- category: `isq_oracle`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `isq_syntax_ctrl_nctrl`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4152`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the oracle_boolean pattern using x[3] -> x[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement an oracle_boolean variant with an expanded 5-qubit register, where x[3] through x[4] remain unused ancillas in the ground state.
2. **Qubits**: 5 qubits (x[0]–x[4]); measurements on x[2], x[3], x[4].
3. **State evolution**:
   - Start: |00000⟩
   - X(x[0]) → |10000⟩; then X(x[0]) → |00000⟩; X(x[1]) → |01000⟩
   - ctrl ctrl X(x[0],x[1],x[2]) (Toffoli): controls x[0]=0, x[1]=1 → condition not met → no change → |01000⟩
   - X(x[0]) → |11000⟩; X(x[1]) → |10000⟩; X(x[2]) → |10100⟩
4. **Final state**: |10100⟩ (x[3] and x[4] untouched at |0⟩), so measuring x[2]=1, x[3]=0, x[4]=0 yields |100⟩ with probability 1.0.

## isqTrain/208

- task_id: `isqTrain/208`
- task_type: `code_generation`
- category: `isq_oracle`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `351`

### Prompt

Write an isQ program that implements a variant of the oracle_boolean pattern using anc[1] -> anc[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement a XOR oracle with an expanded ancilla register (anc[3] vs base anc[1]), leaving extra qubits in ground state.
2. 5 qubits total (q[2], anc[3]); all 5 measured, giving 32 possible outcomes.
3. State evolution:
   - Initial: |00000⟩ (q[0], q[1], anc[0], anc[1], anc[2])
   - X(q[0]): |10000⟩
   - xor_oracle computes q[0]≠q[1] = 1≠0 = true → flips anc[0]: |10100⟩
   - anc[1], anc[2] remain |0⟩ (ground state, unused)
4. Final state |10100⟩ is a computational basis state, so measurement yields |10100⟩ with probability 1.0.

## isqTrain/4518

- task_id: `isqTrain/4518`
- task_type: `output_prediction`
- category: `isq_oracle`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `interference`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1987`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;

oracle bool[1] balanced_f(bool x[2]) {
    bool res[] = [x[0] != x[1]];
    return res;
}

qbit q[2];
qbit anc[1];

procedure main() {
    X(anc[0]);
    H(anc[0]);
    H(q[0]); H(q[1]);
    balanced_f(q, anc);
    H(q[0]); H(q[1]);
    H(q[1]); // superposition on last qubit
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants an analysis of the given isQ program and the probability distribution of its measurement outcomes. The output must start with "## Circuit Analysis", be concise (3-15 lines), use Dirac notation, and end with the predicted probability distribution.

2.  **Analyze the isQ Program**:
    *   `qbit q[2];` and `qbit anc[1];` initializes $|q_1 q_0\rangle = |00\rangle$ and $|anc\rangle = |0\rangle$. Total state: $|000\rangle$. (Order doesn't strictly matter if we track them well, let's say $|q_0 q_1 anc\rangle = |000\rangle$).
    *   `X(anc[0]); H(anc[0]);` transforms $|0\rangle \to |1\rangle \to |-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$.
    *   `H(q[0]); H(q[1]);` transforms $|00\rangle \to |++\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   Combined state: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}}$.
    *   `balanced_f(q, anc);` computes `x[0] != x[1]` XORed into the ancilla (since ancilla is in $|-\rangle$, it applies a phase kickback of $(-1)^{x_0 \oplus x_1}$).
        *   $f(00)=0 \implies (-1)^0 = 1$
        *   $f(01)=1 \implies (-1)^1 = -1$
        *   $f(10)=1 \implies (-1)^1 = -1$
        *   $f(11)=0 \implies (-1)^0 = 1$
        *   State becomes: $\frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle) \otimes |-\rangle$. The q part is $|--\rangle \frac{1}{2}(1 -1 -1 1)^T$, wait.
        *   Wait, $H(|00\rangle) = \frac{1}{2}(1, 1, 1, 1)^T$. Phase kickback gives $(1, -1, -1, 1)^T$. Apply $H \otimes H$: $(H \otimes H) (1, -1, -1, 1)^T = |11\rangle$. Wait, let's do this carefully.
        *   $H|0\rangle = |+\rangle$, $H|1\rangle = |-\rangle$.
        *   $H \otimes H (|00\rangle - |01\rangle - |10\rangle + |11\rangle) = (H \otimes H)(|0\rangle(|0\rangle-|1\rangle) - |1\rangle(|0\rangle-|1\rangle))$
        *   $= (|+\rangle-|-\rangle) \otimes (|+\rangle-|-\rangle) = |1\rangle \otimes |1\rangle = |11\rangle$. Wait.
        *   Let's re-evaluate:
            *   $H|0\rangle = |+\rangle$, $H|1\rangle = |-\rangle$.
            *   $f(x) = x_0 \oplus x_1$.
            *   Phase oracle applies $(-1)^{f(x)}$.
            *   State of $q$: $\sum_x (-1)^{x_0 \oplus x_1} |x\rangle / 2$.
            *   This is exactly $\frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle) = \frac{1}{2}(|0\rangle(|0\rangle-|1\rangle) - |1\rangle(|0\rangle-|1\rangle))$.
            *   Wait, $|0\rangle - |1\rangle$ is proportional to $|1\rangle$. So $|0\rangle(|1\rangle) - |1\rangle(|1\rangle) = (|0\rangle - |1\rangle) |1\rangle$, which is $|11\rangle$ after Hadamards.

### Reference answer

{'predicted_probs': {'10': 0.5, '11': 0.5}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|10>) = 0.5000, P(|11>) = 0.5000.'}

## isqTrain/1909

- task_id: `isqTrain/1909`
- task_type: `output_prediction`
- category: `isq_oracle`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1368`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
oracle bool[1] grover_oracle(bool x[2]) {
    bool res[] = [x[0] && x[1]];
    return res;
}
qbit q[2];
qbit anc[1];
procedure my_z(qbit a) {
    Z(a);
} deriving gate
procedure main() {
    X(anc[0]);
    H(anc[0]);
    H(q[0]); H(q[1]);
    grover_oracle(q, anc);
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    ctrl my_z(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step analysis of an isQ quantum program, predicting the measurement outcome probabilities using Dirac notation. The circuit implements Grover's algorithm for a 2-qubit system (finding the state $|11\rangle$).

2.  **Analyze the isQ Code:**
    *   `grover_oracle`: Checks `x[0] && x[1]`. So it marks the state $|11\rangle$ by flipping the ancilla qubit (which is in the $|-\rangle$ state, effectively applying a phase flip to the marked state).
    *   `qbit q[2]; qbit anc[1];`: Two main qubits, one ancilla.
    *   `X(anc[0]); H(anc[0]);`: Initializes ancilla to $|-\rangle$.
    *   `H(q[0]); H(q[1]);`: Puts main qubits into uniform superposition $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   `grover_oracle(q, anc);`: Marks $|11\rangle$ with a negative phase. State becomes $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$. (Ancilla remains $|-\rangle$).
    *   `H(q[0]); H(q[1]);`: Applies Hadamard to main qubits.
        *   $H^{\otimes 2} \frac{1}{4}(1, 1, 1, -1)^T = \frac{1}{4}(2, 2, 2, 0)^T = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle)$. Wait, actually let's do the math.
        *   $H^{\otimes 2} |00\rangle = ++ = \frac{1}{2}(1,1,1,1)$
        *   $H^{\otimes 2} |01\rangle = +- = \frac{1}{2}(1,-1,1,-1)$
        *   $H^{\otimes 2} |10\rangle = -+ = \frac{1}{2}(1,1,-1,-1)$
        *   $H^{\otimes 2} |11\rangle = -- = \frac{1}{2}(1,-1,-1,1)$
        *   Input to $H^{\otimes 2}$ is $v = \frac{1}{2}(1, 1, 1, -1)$.
        *   $H^{\otimes 2} v = \frac{1}{4}(1+1+1-1, 1-1+1+1, 1+1-1+1, 1-1-1-1) = \frac{1}{4}(2, 2, 2, 0)$. Yes, correct.
    *   `X(q[0]); X(q[1]);`: State becomes $\frac{1}{2}(|11\rangle + |01\rangle + |10\rangle + |00\rangle)$ wait.
        *   Applying $X^{\otimes 2}$ to $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle)$ gives $\frac{1}{2}(|11\rangle + |10\rangle + |01\rangle)$.
    *   `ctrl my_z(q[0], q[1]);`: `my_z` is just `Z`. Controlled Z on `q[1]` with control `q[0]`.
        *   This applies a phase of -1 to $|11\rangle$.
        *   State becomes $\frac{1}{2}(|11\rangle + |10\rangle + |01\rangle - |11\rangle) = \frac{1}{2}(|10\rangle + |01\rangle)$? No wait.
        *   Let's re-evaluate the state after $H^{\otimes 2}$. It was $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle)$.
        *   Apply $X$ to both: state is $\frac{1}{2}(|11\rangle + |10\rangle + |01\rangle)$.
        *   Apply CZ: state is $\frac{1}{2}(-|11\rangle + |10\rangle + |01\rangle)$.
        *   Wait, Grover's diffusion operator is $H^{\otimes n} (2|0

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': "Grover's algorithm using oracle function."}

## isqTrain/618

- task_id: `isqTrain/618`
- task_type: `code_generation`
- category: `isq_oracle`
- difficulty: `basic`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4175`

### Prompt

Implement a quantum circuit in isQ: implements the oracle_parity_check pattern. Include explicit identity operations in the circuit (H-H pair before M(q[3])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Implement a parity oracle that computes the XOR of three data qubits into an ancilla, with H-H identity to demonstrate gate cancellation.

**Qubits:** 4 total (q[0-2] data, q[3] ancilla); only q[3] is measured.

**State evolution:**
- Start: |0000⟩
- After X(q[0-2]): |1110⟩
- CNOT(q[0], q[3]): |1111⟩ (q[0]=|1⟩ flips ancilla)
- CNOT(q[1], q[3]): |1110⟩ (q[1]=|1⟩ flips ancilla back)
- CNOT(q[2], q[3]): |1111⟩ (q[2]=|1⟩ flips ancilla; parity 1⊕1⊕1=1 stored)
- H(q[3]): |111⟩⊗|−⟩ where |−⟩ = (|0⟩−|1⟩)/√2
- H(q[3]): |1111⟩ (H·H = I, identity demonstrated)
- M(q[3]): collapses ancilla

**Result:** Parity of |111⟩ is odd (1), so q[3] = |1⟩ with certainty. Expected: {|1⟩: 1.0}.

## isqTrain/206

- task_id: `isqTrain/206`
- task_type: `code_generation`
- category: `isq_oracle`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5371`

### Prompt

用isQ实现implements a variant of the oracle_boolean pattern using anc[1] -> anc[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Implement an XOR oracle variant that computes x[0] ≠ x[1] into ancilla qubits, with an expanded 4-qubit register.

**Qubits**: 4 total — q[0], q[1] (main register), anc[0], anc[1] (ancilla); all measured.

**State evolution**:
1. Initial: |0000⟩ (ordering: q[0], q[1], anc[0], anc[1])
2. X(q[0]): |1000⟩ — flips q[0] to |1⟩
3. xor_oracle(q, anc): Since q[0]=1, q[1]=0, the condition x[0]≠x[1] is true (1), so anc[0] is XORed with 1 → |1010⟩

**Measurement**: The final state |1010⟩ gives probability 1.0 for bitstring |1010⟩, where earlier-measured qubits (q[0]=1, q[1]=0, anc[0]=1, anc[1]=0) map to higher-to-lower bits respectively.

## isqTrain/616

- task_id: `isqTrain/616`
- task_type: `code_generation`
- category: `isq_oracle`
- difficulty: `basic`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2227`

### Prompt

用isQ实现implements the oracle_parity_check pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

The user is asking me to write a reasoning section for the oracle_parity_check pattern using an alternative gate decomposition (CNOT -> H CZ H).

Let me analyze The implementation:

1. The circuit uses 4 qubits: q[0], q[1], q[2] (data), q[3] (ancilla)
2. The data qubits are initialized to |111>
3. The ancilla q[3] starts in |0>

The standard CNOT decomposition is: CNOT(c, t) = H(t) CZ(c, t) H(t)

The circuit performs a parity check - checking if the number of 1s in the data qubits is odd or even.

Let me trace through the state evolution:

Initial state: |1110>

After X gates on q[0], q[1], q[2]: |1110>

Now the oracle part:
1. H(q[3]): |1110> → |111+> where |+> = (|0> + |1>)/√2

2. CZ(q[0], q[3]): This applies Z to q[3] when q[0] is |1>. Since q[0] = |1>, Z is applied to q[3].
   CZ|11+> = CZ|11>(|0>+|1>)/√2 = |11>(|0>-|1>)/√2 = |11->

   Wait, let me be more careful. CZ applies a phase of -1 when both qubits are |1>.
   CZ|1>|+> = CZ|1>(|0>+|1>)/√2 = (|10> - |11>)/√2 = |1>|->

3. H(q[3]): |111-> → The H gate on |-> gives |1>
   H|-> = |1>

4. H(q[3]): |1111>

5. CZ(q[1], q[3]): Since both q[1] and q[3] are |1>, CZ applies Z to q[3].
   CZ|11> = -|11>
   So we get -|1111>

6. H(q[3]): -|1111> → -|11>|1>
   H|1> = |->

7. H(q[3]): -|11>|-> → -|111>

   Wait, let me recalculate. H|1> = |-> and H|-> = |1>

8. CZ(q[2], q[3]): Since both q[2] and q[3] are |1>... wait let me redo this more carefully.

Let me track the full state:

Initial: |1110>

X(q[0]), X(q[1]), X(q[2]): |1110>

H(q[3]): |111> ⊗ (|0>+|1>)/√2 = |111+>

CZ(q[0], q[3]): 
The CZ gate applies -1 phase when both are |1>.
|111+> = |111>(|0>+|1>)/√2
CZ on q[0],q[3]: When q[0]=1 and q[3]=1, apply -1 phase.
So: |111>(|0>-|1>)/√2 = |111->

H(q[3]): H|-> = |1>
So: |1111>

H(q[3]): H|1> = |->
So: |111->

CZ(q[1], q[3]):
|111-> = |111>(|0>-|1>)/√2
CZ on q[1],q[3]: When q[1]=1 and q[3]=1, apply -1 phase.
|111>(|0>-(-1)|1>)/√2 = |111>(|0>+|1>)/√2 = |111+>

H(q[3]): H|+> = |0>
So: |1110>

H(q[3]): H|0> = |+>
So: |111+>

CZ(q[2], q[3]):
CZ on q[2],q[3]: When q[2]=1 and q[3]=1, apply -1 phase.
|111>(|0>-|1>)/√2 = |111->

H(q[3]): H|-> = |1>
So: |1111>

Final measurement of q[3]: |1> with probability 1.0

This makes sense! The parity of 3 ones (111) is odd, and the ancilla ends up in |1>.

The key insight is that each CNOT(c, t) is decomposed as H(t) CZ(c, t) H(t), and the pattern H H CZ H H CZ H
