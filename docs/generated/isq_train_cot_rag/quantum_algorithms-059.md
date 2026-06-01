# ISQ training COT RAG corpus: quantum_algorithms shard 59

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/119

- task_id: `isqExpand/algo/119`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `basis_change`, `multi_controlled_logic`
- source: `isq_expansion`
- dataset_index: `1573`

### Prompt

帮我写一个isQ程序：implementing 2-qubit Quantum Phase Estimation (QPE) for the Rx(pi) gate. The eigenstate is |-> = (|0>-|1>)/sqrt(2) with eigenvalue e^{i*pi/2}. Use q[0],q[1] as the 2-bit counting register and q[2] as the target qubit. Prepare |-> on q[2] via X(q[2]) then H(q[2]). Apply H to counting qubits. Then: ctrl Rx(3.14159265, q[1], q[2]) for U^{2^0}, and ctrl Rx(6.2831853, q[0], q[2]) for U^{2^1}. Apply inverse QFT: H(q[0]), ctrl inv S(q[1], q[0]), H(q[1]), then SWAP q[0]<->q[1] via 3 CNOTs. Measure q[0] and q[1] only. Note: in isQ, controlled parametric gates use syntax ctrl Rx(angle, control, target).

### Chain-of-thought reasoning

## Reasoning
Goal: QPE for Rx(pi) with eigenstate |->.

Rx(pi)|-> = e^{i*pi/2}|->. Phase = 1/4 (since e^{2*pi*i*(1/4)} = e^{i*pi/2}).
With 2 counting qubits, phi=1/4 encodes as k=1 -> binary 01 -> |01>.

isQ syntax: ctrl Rx(angle, control, target) for controlled rotation.
After IQFT and SWAP: counting register reads |01> = index 1.
Expected: [0,1,0,0]

## isqTrain/4135

- task_id: `isqTrain/4135`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `5255`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[4];

procedure main() {
    X(q[3]);
    H(q[0]); H(q[1]); H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 * 6.0 / 8.0 * 1.0, q[0], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 6.0 / 8.0 * 2.0, q[1], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 6.0 / 8.0 * 4.0, q[2], q[3]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    ctrl Rz(-3.14159265358979 / 4.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(-3.14159265358979 / 2.0, q[2], q[1]);
    H(q[2]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit has 4 qubits: q[0], q[1], q[2], q[3].

Initial state: |0000>

1. X(q[3]): |0001>

2. H(q[0]); H(q[1]); H(q[2]): 
   Apply H to first 3 qubits: (1/√8)(|0>+|1>)(|0>+|1>)(|0>+|1>)⊗|1>
   = (1/√8) Σ_{x∈{0,1}^3} |x>|1>

3. ctrl Rz(2π·6/8·1, q[0], q[3]): This is CPHASE on q[3] controlled by q[0] with angle 2π·3/4·1
   Wait, let me reconsider. The ctrl Rz gate with control q[0] and target q[3] applies Rz to q[3] when q[0] is |1>.
   
   But wait, the syntax is `ctrl Rz(theta, q[0], q[3])`. Looking at the isQ syntax, `ctrl` makes the first qubit the control. So this applies Rz(theta) to q[3] controlled by q[0].

   Actually, let me re-read: `ctrl Rz(theta, q[0], q[3])` - the Rz gate takes (theta, target). With ctrl modifier, q[0] becomes the control. So it's a controlled-Rz with q[0] as control and q[3] as target.

   The angle is 2π × 6/8 × 1 = 2π × 3/4 = 3π/2

   When q[0]=1, q[3] gets phase e^{-i·3π/2} applied. Wait, Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2}). But in controlled form, it applies the gate Rz to the target when control is |1>.

   Actually, let me think about this more carefully. This is a QFT circuit!

   Let me compute the phases:
   - Rz on q[3] controlled by q[0]: angle = 2π·6/8·1 = 3π/2, but this is applied as a phase. In QFT, the controlled phase for bit k is 2π/2^n · 2^k... wait, let me reconsider.

   Actually, this looks like it's computing the QFT of |6⟩|1⟩ or something like that. Let me think about it differently.

   Wait, q[3] is initialized to |1⟩, and then we apply controlled Rz gates. Let me think of q[3] as the target and q[0],q[1],q[2] as the "data" qubits.

   Hmm, but that's unusual. Let me re-examine.

   After the Hadamard gates on q[0], q[1], q[2], the state is:
   |+⟩|+⟩|+⟩|1⟩ = (1/√8) Σ_{j=0}^{7} |j⟩|1⟩

   Now the controlled Rz gates apply phases. The controlled Rz(θ, control, target) applies Rz(θ) to target when control is |1⟩. Since target q[3] is |1⟩, Rz(θ)|1⟩ = e^{iθ/2}|1⟩.

   So:
   - ctrl Rz(3π/2, q[0], q[3]): when q[0]=1, phase e^{i·3π/4}
   - ctrl Rz(2π·6/8·2 = 3π, q[1], q[3]): when q[1]=1, phase e^{i·3π/2}
   - ctrl Rz(2π·6/8·4 = 6π, q[2], q[3]): when q[2]=1, phase e^{i·3π} = e^{iπ} = -1

   Wait, Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2}). So Rz(θ)|1⟩ = e^{iθ/2}|1⟩.

   So for state |j₂j₁j₀⟩|1⟩ where j = 4j₂ + 2j₁ + j₀:
   
   Phase = j₀ · (3π/2)/2 + j₁ · (3π)/2 + j₂ · (6π)/2
   = j₀ · 3π/4

### Reference answer

Dominant output states: |1101> with probability ~0.59 each

## isqTrain/2008

- task_id: `isqTrain/2008`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5775`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[3];
procedure main() {
    X(q[1]);
    X(q[0]);
    Toffoli(q[0], q[1], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[2], q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement outcomes for an isQ program.
    *   Input: isQ code.
    *   Output format: "## Circuit Analysis" followed by step-by-step reasoning, ending with the probability distribution.
    *   Constraint: Concise (3-15 lines).

2.  **Analyze the isQ Code:**
    *   `qbit q[3];` -> 3 qubits: q[0], q[1], q[2]. Initial state: $|000\rangle$.
    *   `X(q[1]);` -> Apply X to q[1]. State: $|010\rangle$.
    *   `X(q[0]);` -> Apply X to q[0]. State: $|110\rangle$.
    *   `Toffoli(q[0], q[1], q[2]);` -> Flip q[2] if q[0]=1 and q[1]=1. Since both are 1, q[2] flips. State: $|111\rangle$.
    *   `CNOT(q[2], q[0]);` -> Flip q[0] if q[2]=1. Since q[2]=1, q[0] flips. State: $|011\rangle$.
    *   `CNOT(q[2], q[1]);` -> Flip q[1] if q[2]=1. Since q[2]=1, q[1] flips. State: $|001\rangle$.
    *   `M(q[0]); M(q[1]);` -> Measure q[0] and q[1].
    *   Wait, the prompt says "earlier measured qubit = higher bit".
        *   M(q[0]) is measured first, so q[0] is the higher bit.
        *   M(q[1]) is measured second, so q[1] is the lower bit.
        *   State before measurement: q[0] is 0, q[1] is 0. So $|00\rangle$ (for the measured qubits).
        *   Let's double check the state evolution.
            *   Initial: 000
            *   X(q[1]): 010
            *   X(q[0]): 110
            *   Toffoli(0, 1, 2): 111 (q[2] is the target, both controls are 1. So 0 -> 1)
            *   CNOT(2, 0): q[2] is 1, so q[0] flips 1 -> 0. State: 011
            *   CNOT(2, 1): q[2] is 1, so q[1] flips 1 -> 0. State: 001
            *   Measuring q[0] and q[1] -> q[0] is 0, q[1] is 0.
            *   Output bitstring: '00'.
            *   Wait, earlier measured qubit is higher bit.
                *   M(q[0]) = higher bit = '0'
                *   M(q[1]) = lower bit = '0'
                *   Bitstring = '00'.
            *   What about the circuit structure? X, X, Toffoli, CNOT, CNOT.
            *   Ah! This is exactly the circuit for a Full Subtractor or Full Adder un-computation!
            *   Let's check: Toffoli(c1, c2, t), CNOT(t, c1), CNOT(t, c2).
            *   Inputs: q[0]=1, q[1]=1, q[2]=0.
            *   Toffoli(1,1,0) -> q[2] becomes 1.
            *   CNOT(1,1) -> q[0] becomes 0.
            *   CNOT(1,1) -> q[1] becomes 0.
            *   Result for measured qubits: q[0]=0, q[1]=0.
            *   Prob('00') = 1.0.

3.  **Draft the Explanation:**
    *   State evolution step-by-step:
        *   Init: $|000\rangle$
        *   X gates: $|110\rangle$
        *   Toffoli(q0, q1, q2): $|111\rangle$
        *   CNOT(q2, q0): $|011\rangle$
        *   CNOT(q2, q1): $|001\rangle$
    *   Measurement: q[0] and q[1] are both 0.
    *   Outcome: '

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'Modular add (2+1) mod 3 = 0 -> state |00>, index 0 has P=1.0.'}

## isqTrain/3009

- task_id: `isqTrain/3009`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4434`

### Prompt

用isQ实现applies two Hadamard gates to each of 4 qubits (H*H = I). All qubits should end in |0>.

Requirements:
- Declare `qbit q[4];` at global scope.
- Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply two Hadamard gates to each of 4 qubits, exploiting H·H = I to return all qubits to |0⟩.
2. **Qubits**: 4 qubits (q[0]-q[3]), all measured at the end.
3. **State evolution**:
   - Initial: |0000⟩
   - H(q[0]): |0⟩→|+⟩, H(q[0]) again: |+⟩→|0⟩ (identity restored)
   - H(q[1]): |0⟩→|+⟩, H(q[1]) again: |+⟩→|0⟩
   - H(q[2]): |0⟩→|+⟩, H(q[2]) again: |+⟩→|0⟩
   - H(q[3]): |0⟩→|+⟩, H(q[3]) again: |+⟩→|0⟩
   - Final state: |0000⟩
4. **Expected probabilities**: Since H·H = I, each qubit returns to |0⟩, yielding P(|0000⟩) = 1.0.

## isqTrain/888

- task_id: `isqTrain/888`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3318`

### Prompt

Help me write isQ code that implements the phase_oracle pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a phase oracle marking |11⟩, with redundant X-X gates demonstrating cancellation.
2. **Qubits**: 2 qubits allocated, both measured.
3. **State evolution**:
   - Start: |00⟩
   - H⊗H → (|00⟩+|01⟩+|10⟩+|11⟩)/2
   - ctrl my_z → CZ flips phase of |11⟩: (|00⟩+|01⟩+|10⟩−|11⟩)/2
   - X(q[0]); X(q[0]) → identity (cancels), state unchanged
4. **Probabilities**: Measurement projects onto computational basis, seeing only |amplitude|². The phase on |11⟩ is invisible, yielding uniform 25% per outcome: {|00⟩:0.25, |01⟩:0.25, |10⟩:0.25, |11⟩:0.25}.

## isqTrain/2695

- task_id: `isqTrain/2695`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_if_else`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1153`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
oracle A(4,1) = [0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1];
oracle g(2,1) = [0,1,1,0]; 
int a;
qbit q[4], p[3];
procedure hadamard_layer(int k){
    H(q[2*k]);
    H(q[2*k+1]);
}
procedure recursive_fourier_sampling(int k){
    if (k == 2){
        A(q[0], q[1], q[2], q[3], p[2]);
    }else{
        hadamard_layer(k);
        X(p[k+1]);
        H(p[k+1]);
        recursive_fourier_sampling(k+1);
        hadamard_layer(k);
        g(q[2*k],q[2*k+1], p[k]);
        hadamard_layer(k);
        recursive_fourier_sampling(k+1);
        hadamard_layer(k);
        H(p[k+1]);
        X(p[k+1]);
    }
}
procedure main(){
    a = 0;
    recursive_fourier_sampling(a);
    int g = M(p[0]);    
    print g;
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants to know the probability of each computational basis state after measuring `p[0]` in the given isQ program. The output must be a concise step-by-step reasoning ending with the predicted probability distribution.

2.  **Analyze the Circuit:**
    *   **Qubits:** `q[0..3]`, `p[0..2]` (7 qubits total). Only `p[0]` is measured.
    *   **Oracles:**
        *   `A(4, 1)` = `[0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1]`. It takes 4 inputs and 1 output. It computes $A(x) \oplus y$ to the output. So if $A(x)=1$, it flips $y$.
        *   `g(2, 1)` = `[0,1,1,0]`. Takes 2 inputs, 1 output. $g(x) = x_0 \oplus x_1$. Output is XOR of inputs.
    *   **Procedure `hadamard_layer(k)`:** Applies H to `q[2k]` and `q[2k+1]`.
    *   **Procedure `recursive_fourier_sampling(k)`:**
        *   Base case (`k == 2`): Applies oracle $A$ to `q[0..3]` and `p[2]`.
            Let's look at $A$. $A(0)=0, A(1)=1, A(2)=1, A(3)=0, A(4)=0, A(5)=0, A(6)=0, A(7)=0, A(8)=0, A(9)=0, A(10)=1, A(11)=1, A(12)=0, A(13)=1, A(14)=0, A(15)=1$.
            $A(x)$ in binary: $A(0000_2)=0, A(0001_2)=1, A(0010_2)=1, A(0011_2)=0$, etc.
        *   Recursive case (`k < 2`):
            *   `hadamard_layer(k)` -> H on `q[2k], q[2k+1]`.
            *   `X(p[k+1]); H(p[k+1])` -> Sets `p[k+1]` to $|-\rangle$.
            *   `recursive_fourier_sampling(k+1)` -> Apply the next level.
            *   `hadamard_layer(k)`
            *   `g(q[2k], q[2k+1], p[k])` -> Applies phase based on $g(x) = x_0 \oplus x_1$.
                Wait, `g` is an oracle that writes to `p[k]`. Wait, `p[k]` is the output qubit.
                If `p[k]` is initially $|0\rangle$ or $|1\rangle$?
                In Fourier Sampling / Bernstein-Vazirani variants, the oracle $U_f$ maps $|x\rangle|y\rangle \to |x\rangle|y \oplus f(x)\rangle$.
                Let's trace carefully.
                If `p[k+1]` is in $|-\rangle$, then applying $U_f$ where $y = |-\rangle$ gives $(-1)^{f(x)} |x\rangle |-\rangle$.
            *   `hadamard_layer(k)` -> This is the inverse of the first `hadamard_layer(k)`!
            *   `recursive_fourier_sampling(k+1)` -> Next level again.
            *   `hadamard_layer(k)` -> Inverse of the H layer inside? Wait, let's look at the exact sequence:
                1. H_layer(k) (on q)
                2. X(p[k+1]); H(p[k+1]) -> |-> on p[k+1]
                3. Rec(k+1) -> involves U_A on q, p[k+1]. Since p[k+1] is |->, this applies phase $(-1)^{A(x)}$.
                4. H_layer(k) (on q) -> This uncomputes the first H_layer(k)? No, it's just another H layer. Wait, H applied twice is I. So H_layer ... H_layer cancels out? No, there's an oracle in between.
                Let's write out `k=1`:
                H_layer(1) on q[2], q[3].
                p[2] in |->.
                Rec

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/794

- task_id: `isqTrain/794`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1761`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the quantum_multiplier pattern using q[4] -> q[5]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
The circuit implements a partial quantum multiplier where q[0]=1 acts as multiplier and q[1:3]=111 (binary) acts as multiplicand, computing a AND of q[0] and q[1] into q[3].

Five qubits are used (q[0]–q[4]), with only q[3] and q[4] measured (2 qubits).

**State evolution:**
1. After `X(q[0])`, `X(q[1])`, `X(q[2])`: state is |1⟩₁|1⟩₁|1⟩₂|0⟩₃|0⟩₄ = |11100⟩
2. `Toffoli(q[0], q[1], q[3])`: both controls (q[0], q[1]) are |1⟩, so q[3] flips → |11110⟩

The final measured qubits are q[3]=1 (higher bit) and q[4]=0 (lower bit), yielding outcome |10⟩ with probability 1.0.

## isqTrain/4186

- task_id: `isqTrain/4186`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2992`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.500, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[1], q[2]);
    Rx(2.0 * 0.500, q[0]);
    Rx(2.0 * 0.500, q[1]);
    Rx(2.0 * 0.500, q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Goal:** Predict measurement output and probability distribution of an isQ quantum program.
    *   **Circuit:**
        *   3 qubits `q[0], q[1], q[2]`.
        *   Initialization: H on all 3 qubits -> $|+++\rangle$.
        *   Operations: `CNOT(q[0], q[1]); Rz(2.0*0.5, q[1]); CNOT(q[0], q[1]);` -> $e^{-iZZ/2}$ type interaction? Wait, let's trace exactly.
        *   `CNOT(0,1)`, `Rz(pi/2, 1)`, `CNOT(0,1)` corresponds to ZZ interaction. $R_z(\theta)$ is `diag(1, e^{i\theta})` in standard notation. `Rz(2.0 * 0.5)` is $\theta = 1.0$ (wait, $\pi$ or radians? Usually isQ uses radians unless `pi` is specified, so $\theta = 1.0$ rad). Let me assume radians.
        *   Then `CNOT(1,2)`, `Rz(1.0, 2)`, `CNOT(1,2)`.
        *   Then `Rx(1.0, 0)`, `Rx(1.0, 1)`, `Rx(1.0, 2)`.
        *   Measurement on all 3.
    *   **Constraints:** 3-8 lines for simple, up to 15 for complex. Output ONLY the analysis starting with "## Circuit Analysis". End with the predicted probability distribution.

2.  **Step-by-Step State Evolution:**
    *   **Initial state:** $|000\rangle$
    *   **H(0), H(1), H(2):** $|+++\rangle = \frac{1}{2\sqrt{2}} \sum_{x \in \{0,1\}^3} |x\rangle$.
    *   **CNOT(0,1) Rz(1, 1) CNOT(0,1):** This is equivalent to $e^{-i Z_0 Z_1 / 2}$ (up to global phase). Let's verify.
        *   $|00\rangle \to |00\rangle \to 1 \cdot |00\rangle \to |00\rangle$.
        *   $|01\rangle \to |01\rangle \to e^{i} |01\rangle \to e^{i} |01\rangle$.
        *   $|10\rangle \to |11\rangle \to e^{i} |11\rangle \to e^{i} |10\rangle$.
        *   $|11\rangle \to |10\rangle \to 1 \cdot |10\rangle \to |11\rangle$.
        *   So it applies $e^{i}$ phase when $q_0 \oplus q_1 = 1$.
        *   Equivalently, it applies phase $e^{i Z_0 Z_1 / 2}$ (if Rz is $e^{-iZ/2}$? No, let's stick to the $Z_0 Z_1$ phase).
        *   Wait, is `Rz(1.0)` equivalent to phase $e^{-i/2}$ on $|0\rangle$ and $e^{i/2}$ on $|1\rangle$?
        *   Let's use standard gate notation: $R_z(\theta) = e^{-i\theta Z/2} = \text{diag}(e^{-i\theta/2}, e^{i\theta/2})$.
        *   If $\theta = 1.0$, it's $\text{diag}(e^{-0.5i}, e^{0.5i})$.
        *   CNOT Rz(1) CNOT: $|00\rangle \to e^{-0.5i}|00\rangle$, $|11\rangle \to e^{-0.5i}|11\rangle$, $|01\rangle \to e^{0.5i}|01\rangle$, $|10\rangle \to e^{0.5i}|10\rangle$.
        *   Phase factor is $e^{-0.5i}$ when $q_0 = q_1$, $e^{0.5i}$ when $q_0 \neq q_1$.
        *   So it's $e^{-0.5i} e^{i \cdot Z_0 Z_1 / 2} =

### Reference answer

Uniform distribution across 8 states

## isqTrain/1990

- task_id: `isqTrain/1990`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4757`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    X(q[1]);
    ctrl Rx(3.14159265, q[0], q[1]);
    H(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program**:
    *   `qbit q[2];`: Two qubits, initialized to $|00\rangle$.
    *   `H(q[0]);`: Hadamard on q[0]. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    *   `X(q[1]);`: X gate on q[1]. State becomes $\frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$.
    *   `ctrl Rx(3.14159265, q[0], q[1]);`: Controlled-Rx gate. If q[0] is |1>, apply Rx($\pi$) to q[1].
        *   $Rx(\pi) = e^{-i\pi X/2} = \cos(\pi/2)I - i\sin(\pi/2)X = -iX$.
        *   Applying this to the state:
            *   For the $|01\rangle$ part (control is |0>), it remains $|01\rangle$.
            *   For the $|11\rangle$ part (control is |1>), it becomes $-iX|1\rangle = -i|0\rangle$.
        *   So state becomes $\frac{1}{\sqrt{2}}(|01\rangle - i|10\rangle)$. (Wait, let me recheck the tensor product indices. q[0] is control, q[1] is target. State is $c_0|q_0=0, q_1=1\rangle + c_1|q_0=1, q_1=1\rangle$. After CRx($\pi$), the $|q_0=1, q_1=1\rangle$ term becomes $-i|q_0=1, q_1=0\rangle$).
        *   State is $\frac{1}{\sqrt{2}}(|01\rangle - i|10\rangle)$.
    *   `H(q[0]);`: Hadamard on q[0].
        *   $H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
        *   $H|1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        *   New state: $\frac{1}{\sqrt{2}} [ \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)\otimes|1\rangle - i\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)\otimes|0\rangle ]$
        *   $= \frac{1}{2} (|01\rangle + |11\rangle - i|00\rangle + i|10\rangle)$.
        *   $= \frac{1}{2} (-i|00\rangle + |01\rangle + i|10\rangle + |11\rangle)$.
    *   `M(q[0]);`: Measure only q[0].
        *   Probability of measuring q[0]=0 is $|\frac{-i}{2}|^2 + |\frac{1}{2}|^2 = 1/4 + 1/4 = 1/2$.
        *   Probability of measuring q[0]=1 is $|\frac{i}{2}|^2 + |\frac{1}{2}|^2 = 1/4 + 1/4 = 1/2$.

2.  **Double check calculations**:
    *   Initial: $|00\rangle$
    *   $H(q_0)$: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$
    *   $X(q_1)$: $\frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$
    *   CRx($\pi$, q_0, q_1):
        *   $|0\rangle\langle0| \otimes I + |1\rangle\langle1| \otimes Rx(\pi)$
        *   $Rx(\pi) \approx -iX$. Since $X|1\rangle = |0\rangle$, $Rx(\pi)|1\rangle = -i|0\rangle$.
        *   State becomes $\frac{1}{\sqrt{2}}(|01\rangle - i|10\rangle)$.
    *   $H(q_0)$:
        *   $H_1 \otimes I_2 (\frac{1}{\sqrt{2}}

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'Expected probabilities: [0.5000000008974483, 0.49999999910255166]'}

## isqTrain/1209

- task_id: `isqTrain/1209`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1925`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the quantum_random_walk pattern using p[2] -> p[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this quantum random walk circuit carefully.

The circuit has:
- 1 coin qubit c[0]
- 4 position qubits p[0], p[1], p[2], p[3] (expanded from p[2] in base version)

Initial state: |0⟩_c ⊗ |0000⟩_p

Step 1: H(c[0]) on coin qubit
State becomes: (|0⟩ + |1⟩)/√2 ⊗ |0000⟩ = (|0,0000⟩ + |1,0000⟩)/√2

Step 2: ctrl CNOT(c[0], p[0], p[1])
This is a controlled-CNOT where c[0] controls a CNOT with p[0] as control and p[1] as target.
When c[0] = |1⟩, CNOT(p[0], p[1]) is applied.
- CNOT(p[0], p[1]) on |00⟩ = |00⟩ (p[0]=0, so no flip)
State remains: (|0,0000⟩ + |1,0000⟩)/√2

Wait, let me re-read the isQ syntax. `ctrl CNOT(c[0], p[0], p[1])` - this might mean c[0] is the control, and then CNOT is applied to p[0] and p[1] conditionally.

Actually, looking at the syntax more carefully:
- `ctrl CNOT(c[0], p[0], p[1])` means c[0] controls the CNOT gate between p[0] and p[1]
- When c[0] = |1⟩, CNOT(p[0]→p[1]) is applied

State still: (|0,0000⟩ + |1,0000⟩)/√2 (since p[0]=0, CNOT doesn't flip p[1])

Step 3: ctrl X(c[0], p[0])
When c[0] = |1⟩, apply X to p[0]
State: (|0,0000⟩ + |1,1000⟩)/√2

Step 4: nctrl X(c[0], p[0])
When c[0] = |0⟩, apply X to p[0] (anti-controlled)
State: (|1,0000⟩ + |1,1000⟩)/√2

Wait, that gives |1⟩ for both coin states. Let me redo.

After Step 3: (|0,0000⟩ + |1,1000⟩)/√2

Step 4: nctrl X(c[0], p[0]) - apply X to p[0] when c[0] = |0⟩
|0,0000⟩ → |0,1000⟩ (flip p[0] when coin is |0⟩)
|1,1000⟩ → |1,1000⟩ (no flip when coin is |1⟩)

State: (|0,1000⟩ + |1,1000⟩)/√2

Hmm, that doesn't match the predicted output either.

Wait, let me re-read. The expected measurement probabilities are {|1000⟩: 0.5, |1100⟩: 0.5}. But we're only measuring p[0]-p[3], not c[0].

Let me reconsider the gate order and effects.

Actually wait - the comment says "Increment: carry from p[0] to p[1], then flip p[0]" and "Decrement: flip p[0] first, then carry". This is a quantum walk on a 4-node cycle using 2 bits for position. But we have 4 qubits for position...

Hmm, but p[2] and p[3] are never touched, so they stay |0⟩. So effectively we have a 2-qubit position register (p[0], p[1]) and 2 idle qubits (p[2], p[3]).

Let me redo more carefully:

Initial: |0⟩_c ⊗ |0000⟩_p

After H(c[0]): (|0⟩ + |1⟩)/√2 ⊗ |0000⟩

ctrl CNOT(c[0], p[0], p[1]):
- When c[0]=|1⟩: CNOT(p[0], p[1]). Since p[0]=|0⟩, p[1] stays |0⟩. No change.
State: (|0,0000⟩ + |1,0000⟩)/√2

ctrl X(c[0], p[0]):
- When c[0]=|1⟩: X(p[0]). Flips p[0] from |0⟩ to |1
