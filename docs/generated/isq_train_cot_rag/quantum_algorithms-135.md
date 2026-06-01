# ISQ training COT RAG corpus: quantum_algorithms shard 135

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3495

- task_id: `isqTrain/3495`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3387`

### Prompt

帮我分析一下这个量子程序的输出：

```
import std;

qbit q[4];

procedure main() {
    X(q[0]); X(q[1]); X(q[2]);

    ctrl ctrl X(q[0], q[1], q[3]);
    CNOT(q[0], q[1]);
    ctrl ctrl X(q[1], q[2], q[3]);
    CNOT(q[2], q[1]);

    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request**:
    *   Task: Predict output probability distribution.
    *   Program: isQ code.
    *   State representation: Dirac notation.
    *   Length limit: Concise (3-8 lines for simple, up to 15 for complex).
    *   Output format: MUST start with "## Circuit Analysis", end with predicted probability distribution. no code blocks.

2.  **Analyze the Circuit**:
    *   `qbit q[4];` -> 4 qubits, initial state |0000>.
    *   `X(q[0]); X(q[1]); X(q[2]);` -> Flips first 3 qubits.
        *   State: |1110>
    *   `ctrl ctrl X(q[0], q[1], q[3]);` -> Toffoli gate. If q[0] and q[1] are 1, flip q[3].
        *   q[0] and q[1] are 1, so q[3] flips to 1.
        *   State: |1111>
    *   `CNOT(q[0], q[1]);` -> If q[0] is 1, flip q[1].
        *   q[0] is 1, so q[1] flips to 0.
        *   State: |1011>
    *   `ctrl ctrl X(q[1], q[2], q[3]);` -> Toffoli gate. If q[1] and q[2] are 1, flip q[3].
        *   q[1]=0, q[2]=1. Since q[1]=0, target is not flipped.
        *   State: |1011>
    *   `CNOT(q[2], q[1]);` -> If q[2] is 1, flip q[1].
        *   q[2] is 1, so q[1] flips from 0 to 1.
        *   State: |1111>

3.  **Confirm the states**:
    *   Start: `|q3 q2 q1 q0>` = `|0000>` (Standard order usually q[N-1]...q[0], let's trace carefully).
    *   Let's use bit string: `q3 q2 q1 q0`.
    *   Init: 0000
    *   X(q[0,1,2]): 1110 (q3=0, q2=1, q1=1, q0=1)
    *   Toffoli(q0, q1, q3): q0=1, q1=1 => flip q3. q3 becomes 1. State: 1111
    *   CNOT(q0, q1): q0=1 => flip q1. q1 becomes 0. State: 1011
    *   Toffoli(q1, q2, q3): q1=0, q2=1 => q1 is 0, so no flip on q3. State: 1011
    *   CNOT(q2, q1): q2=1 => flip q1. q1 becomes 1. State: 1111.
    *   Wait, is the Toffoli condition satisfied? q1 is 0. Yes, so q3 stays 1.
    *   Final state: |1111> (q0=1, q1=1, q2=1, q3=1).
    *   Let's double check standard bit ordering for isQ. Generally, earlier measured qubit = higher bit (or maybe standard is little endian). The prompt mentions: "--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)."
    *   The prompt wants the "basis states with non-zero probability." I will write the string in `q3q2q1q0` or `q0q1q2q3` format, explicitly defining it. "1111" is unambiguous if I specify.

4.  **Drafting the explanation**:
    *   Start with "## Circuit Analysis"
    *   State initial: |0000>
    *   Apply X gates: |1110>
    *   Apply `ctrl ctrl X(q[0], q[1], q[3])`: q[0] and q[1] are 1, so q[3] flips. State |1111>.
    *   Apply `CNOT(q[0], q[1])`: q[0] is 1, so q[1] flips. State |1011>.
    *   Apply `ctrl ctrl X(q[1], q[2], q[3

### Reference answer

{'predicted_probs': {'1111': 1.0}, 'explanation': 'The output is |1111> with probability 1.0'}

## isqTrain/3545

- task_id: `isqTrain/3545`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `hamiltonian_simulation`
- source: `isq_train_cot`
- dataset_index: `259`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should QAOA MaxCut on 4-node cycle.

### Chain-of-thought reasoning

## Bug Analysis

**The Bug:** In the Edge (0,1) ZZ interaction block, the first CNOT has reversed arguments: `CNOT(q[1], q[0])` instead of `CNOT(q[0], q[1])`. This breaks the standard CNOT-Rz-CNOT decomposition of a ZZ interaction, which requires both CNOTs to share the same control and target qubits.

**The Fix:** Change the first CNOT from `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])` so both CNOTs are identical and properly cancel.

**State Evolution (corrected circuit):**
1. After Hadamards: all qubits in |+⟩, state is |++++⟩ (equal superposition).
2. Each ZZ interaction applies $e^{-i\gamma Z_i Z_j}$ on edge (i,j). The correct decomposition: CNOT(q[i],q[j]) maps $Z_j \to Z_i Z_j$; Rz(γ,q[j]) phases by $e^{-i\gamma Z_i Z_j}$; CNOT(q[i],q[j]) undoes the basis change.
3. The buggy CNOT(q[1],q[0]) followed by CNOT(q[0],q[1]) does not cancel — instead it performs a swap (three-CNOT decomposition)-like operation, corrupting the entanglement structure.
4. After the corrected ZZ layer on edges (0,1), (1,2), (2,3), (3,0), the state acquires phases from the 4-node cycle graph.
5. Mixer layer applies Rx(0.7) ≈ Rx(2β) to each qubit, rotating around X-axis.
6. Measurement yields the expected distribution with highest probabilities on |0000⟩ and |1111⟩ (~0.249 each), consistent with the 4-node cycle's bipart

## isqTrain/2004

- task_id: `isqTrain/2004`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4143`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[5];
procedure main() {
    X(q[0]);
    X(q[2]);
    Toffoli(q[0], q[2], q[4]);
    CNOT(q[0], q[2]);
    CNOT(q[1], q[3]);
    CNOT(q[4], q[3]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **X(q[0])** and **X(q[2])** flip qubits q[0] and q[2] to |1>. The initial state is |00000>, becoming |00101>.
2. **Toffoli(q[0], q[2], q[4])** flips q[4] because both controls (q[0], q[2]) are |1>. The state becomes |10101>.
3. **CNOT(q[0], q[2])** flips q[2] because q[0] is |1>. The state becomes |10001>.
4. **CNOT(q[1], q[3])** does nothing because q[1] is |0>. The state remains |10001>.
5. **CNOT(q[4], q[3])** flips q[3] because q[4] is |1>. The state becomes |11001>.
6. The final state before measurement has deterministic values for all measured qubits: q[2]=|0> and q[3]=|1>.
7. Measuring q[2] and q[3] yields q[2] as the higher bit and q[3] as the lower bit (bitstring '01').

Predicted probability distribution: {'01': 1.0}

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'Ripple carry 1+1=2: sum0=0, sum1=1. Index 1 has P=1.0.'}

## isqTrain/1167

- task_id: `isqTrain/1167`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1331`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the iqp_circuit pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this IQP (Instantaneous Quantum Polynomial) circuit variant.

The circuit uses qubits q[0] through q[4] (5 qubits total), but only q[0], q[1], q[2] are actively used in the computation. Qubits q[3] and q[4] remain in the ground state |0⟩.

The IQP circuit structure is: H layer → diagonal gates → H layer

Let me trace through the state evolution:

1. Initial state: |00000⟩

2. First Hadamard layer on q[0], q[1], q[2]:
   |00000⟩ → (H⊗H⊗H⊗I⊗I)|00000⟩ = |+++00⟩ = (1/√8)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)⊗|00⟩

3. Apply T gates (phase gates) on q[0], q[1], q[2]:
   T|0⟩ = |0⟩, T|1⟩ = e^(iπ/4)|1⟩
   This applies phases based on the computational basis states.

4. Apply CZ(q[0], q[1]) and CZ(q[1], q[2]):
   CZ adds a phase of -1 when both qubits are |1⟩.

5. Second Hadamard layer: H on q[0], q[1], q[2]

Let me compute this more carefully.

After first H layer: |+++00⟩ = 1/√8 ∑_{x∈{0,1}^3} |x⟩|00⟩

After T gates on all three: 1/√8 ∑_{x∈{0,1}^3} e^(iπ/4 * (x_0 + x_1 + x_2)) |x⟩|00⟩

After CZ(q[0], q[1]): adds phase (-1)^(x_0·x_1)
After CZ(q[1], q[2]): adds phase (-1)^(x_1·x_2)

So the state becomes:
1/√8 ∑_{x∈{0,1}^3} e^(iπ/4 * (x_0 + x_1 + x_2)) · (-1)^(x_0·x_1 + x_1·x_2) |x⟩|00⟩

After second H layer on first 3 qubits:
The amplitude for |y⟩|00⟩ where y ∈ {0,1}^3 is:
1/8 ∑_{x∈{0,1}^3} (-1)^(y·x) · e^(iπ/4 * (x_0 + x_1 + x_2)) · (-1)^(x_0·x_1 + x_1·x_2)

Let me compute this for each y:

For y = 000: 1/8 ∑_x e^(iπ/4 * (x_0+x_1+x_2)) · (-1)^(x_0·x_1 + x_1·x_2)

Let me enumerate:
x=000: e^0 · 1 = 1
x=001: e^(iπ/4) · 1 = e^(iπ/4)
x=010: e^(iπ/4) · 1 = e^(iπ/4)
x=011: e^(iπ/2) · (-1) = -i
x=100: e^(iπ/4) · 1 = e^(iπ/4)
x=101: e^(iπ/2) · 1 = i
x=110: e^(iπ/2) · (-1) = -i
x=111: e^(3iπ/4) · (-1) = -e^(3iπ/4)

Let me use exact values. e^(iπ/4) = (1+i)/√2

x=000: 1
x=001: (1+i)/√2
x=010: (1+i)/√2
x=011: -i · (-1) for CZ... wait, let me recalculate.

Wait, x=011 means x_0=0, x_1=1, x_2=1.
Phase from T: e^(iπ/4 * 2) = e^(iπ/2) = i
CZ(q[0],q[1]): x_0·x_1 = 0·1 = 0, so factor = 1
CZ(q[1],q[2]): x_1·x

## isqTrain/4477

- task_id: `isqTrain/4477`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `interference`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `889`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

qbit q[3];

procedure main() {
    
    X(q[2]);
    
    H(q[0]);
    
    ctrl SWAP(q[0], q[1], q[2]);
    
    H(q[0]);
    
    H(q[2]); // superposition on last qubit
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: output_prediction (predict measurement probabilities).
    *   Input: isQ quantum program.
    *   Constraints: Concise step-by-step reasoning, Dirac notation, max 3-15 lines, start with "## Circuit Analysis", output ONLY the analysis, no code blocks, end with probability distribution.
    *   Program:
        

2.  **Analyze the Circuit:**
    *   Initial state: $|000\rangle$ (for q[0], q[1], q[2]). Let's use standard ordering $q_2 q_1 q_0$ or $q_0 q_1 q_2$. isQ usually uses $q_0$ as the lowest bit, but let's trace carefully. Let's write the state as $|q_0 q_1 q_2\rangle$.
    *   `X(q[2])`: Flips q[2] to $|1\rangle$. State: $|001\rangle$.
    *   `H(q[0])`: Applies H to q[0]. State: $\frac{1}{\sqrt{2}}(|001\rangle + |101\rangle)$.
        *Wait, standard notation is $|q_0 q_1 q_2\rangle$. Let's use $|q_0\rangle \otimes |q_1\rangle \otimes |q_2\rangle$.
        State before H(0): $|0\rangle_0 \otimes |0\rangle_1 \otimes |1\rangle_2$
        State after H(0): $|+\rangle_0 \otimes |0\rangle_1 \otimes |1\rangle_2 = \frac{1}{\sqrt{2}}(|0\rangle_0 + |1\rangle_0)|0\rangle_1|1\rangle_2 = \frac{1}{\sqrt{2}}(|001\rangle + |101\rangle)$.
    *   `ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2])`: If q[0] is $|1\rangle$, swap (three-CNOT decomposition) q[1] and q[2].
        Since q[1] is $|0\rangle$ and q[2] is $|1\rangle$, swap (three-CNOT decomposition) makes q[1]=$|1\rangle$ and q[2]=$|0\rangle$.
        If q[0] is $|0\rangle$, nothing happens.
        State: $\frac{1}{\sqrt{2}}(|0\rangle_0 |0\rangle_1 |1\rangle_2 + |1\rangle_0 |1\rangle_1 |0\rangle_2) = \frac{1}{\sqrt{2}}(|001\rangle + |110\rangle)$.
        Wait, controlled-swap operation (three-CNOT decomposition)!
        Let's re-read: `ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2])` means q[0] is the control, q[1] and q[2] are the targets of the swap (three-CNOT decomposition).
        $|0\rangle_0|0\rangle_1|1\rangle_2 \to |0\rangle_0|0\rangle_1|1\rangle_2$
        $|1\rangle_0|0\rangle_1|1\rangle_2 \to |1\rangle_0|1\rangle_1|0\rangle_2$
        State is $\frac{1}{\sqrt{2}}(|001\rangle + |110\rangle)$.
    *   `H(q[0])`: Apply H to q[0].
        State becomes $\frac{1}{\sqrt{2}} [ (\frac{|0\rangle_0+|1\rangle_0}{\sqrt{2}})|0\rangle_1|1\rangle_2 + (\frac{|0\rangle_0-|1\rangle_0}{\sqrt{2}})|1\rangle_1|0\rangle_2 ]$
        $= \frac{1}{2} |0\rangle_0 (|0\rangle_1|1\rangle_2 + |1\rangle_1|0\rangle_2) + \frac{1}{2} |1\rangle_0 (|0\rangle_1|1\rangle_2 - |1\rangle_1|0\rangle_2)$
    *   `H(q[2])`:

### Reference answer

{'predicted_probs': {'000': 0.5, '001': 0.5}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.5000, P(|001>) = 0.5000.'}

## isqTrain/3513

- task_id: `isqTrain/3513`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `interference`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `1953`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```
import std;

qbit q[4];
qbit anc[1];

procedure main() {
    X(anc[0]);
    H(anc[0]);

    H(q[0]); H(q[1]); H(q[2]); H(q[3]);

    CNOT(q[1], anc[0]);
    CNOT(q[2], anc[0]);

    H(q[0]); H(q[1]); H(q[2]); H(q[3]);

    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **X(anc[0])**: $|0\rangle \to |1\rangle$
2.  **H(anc[0])**: $|1\rangle \to |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
3.  **H(q[0..3])**: State of $q$ is $H^{\otimes 4}|0000\rangle = \frac{1}{4}\sum_{x=0}^{15}|x\rangle$.
    Overall state: $\frac{1}{4}\sum_x |x\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
4.  **CNOT(q[1], anc[0])** and **CNOT(q[2], anc[0])**:
    This applies $X$ to anc[0] controlled by $q_1 \oplus q_2$.
    Phase kickback: $CNOT_{1,anc} CNOT_{2,anc} |x\rangle |-\rangle = (-1)^{x_1 \oplus x_2} |x\rangle |-\rangle$.
    State becomes: $\frac{1}{4}\sum_x (-1)^{x_1 \oplus x_2} |x\rangle \otimes |-\rangle$.
5.  **H(q[0..3])**: Applying $H^{\otimes 4}$ again.
    Since $H^{\otimes n} \sum_x (-1)^{f(x)} |x\rangle = \sum_y \frac{1}{2^n} \sum_x (-1)^{f(x) + x \cdot y} |y\rangle$.
    Here $f(x) = x_1 \oplus x_2$. So $H^{\otimes 4}$ transforms the state.
    Wait, let's look at the terms.
    $x_1 \oplus x_2$ is a linear function $c \cdot x$ where $c = 0110$ (assuming q[0] is MSB and q[3] is LSB, wait, q[1] and q[2] means $c_1=1, c_2=1$, others 0).
    So $(-1)^{x_1 \oplus x_2}$ is a phase $(-1)^{c \cdot x}$ where $c = 0110_2 = 6$.
    Applying $H^{\otimes n}$ on $\sum_x (-1)^{c \cdot x}|x\rangle$ simply outputs $|c\rangle = |0110\rangle$.
    Let's verify: $H^{\otimes n} \sum_x (-1)^{c \cdot x} |x\rangle = |c\rangle$.
    Since $x_1 \oplus x_2$ is just $x \cdot (0,1,1,0)^T$.
    So the final state of q[0..3] is exactly $|0110\rangle$.
    Wait! The qubits measured are $q_0, q_1, q_2, q_3$.
    In isQ, `qbit q[4];` measured in order `M(q[0]); M(q[1]); M(q[2]); M(q[3]);`.
    The probability is 100% for $|0110\rangle$.
    Let me double check the endianness and state.
    Initial q: $|0000\rangle$.
    H on q: $\sum_x |x\rangle / 4$.
    CNOT(q[1], anc[0]) flips anc[0] if $x_1 = 1$.
    CNOT(q[2], anc[0]) flips anc[0] if $x_2 = 1$.
    Since anc is in $|-\rangle$, flipping it applies a phase of $-1$ if $x_1=1$, and another phase of $-1$ if $x_2=1$.
    Total phase on $|x\rangle |-\rangle$ is $(-1)^{x_1}(-1)^{x_2} = (-1)^{x_1 \oplus x_2}$.
    So the state of q is $\sum_x (-1)^{x_1 \oplus x_2} |x\rangle / 4$.
    This is exactly $H^{\otimes 4} Z_1 Z_2 H^{\otimes 4} |0000\rangle$.
    $H^{\otimes 4} Z

### Reference answer

{'predicted_probs': {'0110': 1.0}, 'explanation': 'The output is |0110> with probability 1.0'}

## isqTrain/2693

- task_id: `isqTrain/2693`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1888`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
oracle g(3, 1) = [0, 0, 1, 1, 1, 1, 0, 0];
qbit q[3], anc;
procedure main(){
    for i in 0:3{
        H(q[i]);
    }
    X(anc);
    H(anc);
    g(q[0], q[1], q[2], anc);
    for i in 0:3{
        H(q[i]);
        int a = M(q[i]);
        print a;
    }
}
```

### Chain-of-thought reasoning

This is a Deutsch-Jozsa algorithm implementation. Let me analyze it step by step.

The oracle is defined as `g(3, 1) = [0, 0, 1, 1, 1, 1, 0, 0]`.

This means g maps:
- |000⟩ → 0
- |001⟩ → 0
- |010⟩ → 1
- |011⟩ → 1
- |100⟩ → 1
- |101⟩ → 1
- |110⟩ → 0
- |111⟩ → 0

The oracle applies |x⟩|y⟩ → |x⟩|y ⊕ g(x)⟩.

Initial state: |000⟩|0⟩

Step 1: H on q[0], q[1], q[2] and X then H on anc:
The state becomes: (1/√8) Σ|x⟩ ⊗ |−⟩ where x ranges from 000 to 111.

Step 2: Apply oracle g:
Since the ancilla is in |−⟩, the oracle applies a phase: (-1)^g(x)|x⟩|−⟩

So the state becomes:
|x⟩ gets phase (-1)^g(x):
- |000⟩: (-1)^0 = 1
- |001⟩: (-1)^0 = 1
- |010⟩: (-1)^1 = -1
- |011⟩: (-1)^1 = -1
- |100⟩: (-1)^1 = -1
- |101⟩: (-1)^1 = -1
- |110⟩: (-1)^0 = 1
- |111⟩: (-1)^0 = 1

So the state of q[0..2] is (1/√8)(|000⟩ + |001⟩ - |010⟩ - |011⟩ - |100⟩ - |101⟩ + |110⟩ + |111⟩)|−⟩

Step 3: Apply H on q[0], q[1], q[2]:

For the Deutsch-Jozsa algorithm, after applying H⊗n, the amplitude of |000⟩ is (1/2^n) Σ_x (-1)^g(x).

Let me compute: Σ (-1)^g(x) = 1 + 1 + (-1) + (-1) + (-1) + (-1) + 1 + 1 = 0.

So the amplitude of |000⟩ is 0.

Actually, let me compute all amplitudes properly.

The state after oracle is (1/√8) Σ_x (-1)^g(x) |x⟩.

After applying H⊗3, the amplitude of |z⟩ is:
(1/8) Σ_x (-1)^g(x) (-1)^{x·z}

Let me compute for each z:

For z = 000:
(1/8)(1·1 + 1·1 + (-1)·1 + (-1)·1 + (-1)·1 + (-1)·1 + 1·1 + 1·1) = (1/8)(0) = 0

For z = 001 (x·z = x₂):
(1/8)(1·0 + 1·1 + (-1)·0 + (-1)·1 + (-1)·0 + (-1)·1 + 1·0 + 1·1) = (1/8)(0) = 0

For z = 010 (x·z = x₁):
(1/8)(1·0 + 1·0 + (-1)·1 + (-1)·1 + (-1)·0 + (-1)·0 + 1·1 + 1·1) = (1/8)(0) = 0

For z = 011 (x·z = x₁ + x₂):
(1/8)(1·0 + 1·1 + (-1)·1 + (-1)·0 + (-1)·0 + (-1)·1 + (-1)... wait let me be more careful.

x ranges from 0 to 7. Let me write x = (x₂, x₁, x₀) where x₂ is the most significant bit.

g = [0, 0, 1, 1, 1, 1, 0, 0]

x: 000→g=0, 001→g=0, 010→g=1, 011→g=1, 100→g=1, 101→g=1, 110→g=0, 111→g=0

(-1)^g(x): 1, 1, -1, -1, -1, -1,

### Reference answer

{'predicted_probs': {'110': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqQA/quantum_algorithms/88_step_by_step

- task_id: `isqQA/quantum_algorithms/88_step_by_step`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `step_by_step`, `algorithm`, `DJ算法的Oracle构造`
- source: `qa_pipeline`
- dataset_index: `4430`

### Prompt

在Deutsch-Jozsa算法中，如何通过量子Oracle区分常函数和平衡函数？请分步推导并手动追踪两量子比特输入下，对应平衡函数 f(x) = x_0 ⊕ x_1 的完整计算过程，并提供该Oracle的isQ代码实现。

### Reference answer

<think>
整体推导思路分为四个核心步骤：

1. **状态演化与并行性准备**：初始化系统并对所有量子比特应用Hadamard门。计算比特进入等概率叠加态，辅助比特转为 $|-\rangle$ 态，使算法能够同时评估所有可能的输入。
2. **相位反推机制分析**：利用辅助比特处于 $|-\rangle$ 态时的线性性质，将Oracle对辅助比特的模2加操作，等效转化为计算比特上的相位翻转 $(-1)^{f(x)}$。对于给定的平衡函数 $f(x)=x_0\oplus x_1$，需精确追踪叠加态中哪些基态（如01和10）会被引入负相位。
3. **量子干涉与结果放大**：对计算比特再次施加Hadamard门。通过矩阵运算，将隐藏在相位中的差异转化为测量概率振幅的差异。由于目标是平衡函数，相长干涉和相消干涉会使得全零状态 $|00\rangle$ 的振幅完全抵消为0。
4. **线路至代码的逻辑映射**：将理论推导中的布尔逻辑转换为具体量子门。在isQ代码实现中，利用控制非门（CNOT）等基本量子门组合，构建出能精确模拟该异或运算相位变化的Oracle矩阵。
</think>

Deutsch-Jozsa（DJ）算法的核心优势在于仅需一次量子查询，即可百分之百确定一个函数是常函数还是平衡函数。为了深入理解这一过程，我们将以两个输入量子比特（n=2）和一个辅助比特为例，一步步追踪算法中量子态的演化，并构造一个特定的平衡函数 Oracle。

第一步：初始化与叠加态生成
假设我们有两个计算比特和 一个辅助比特。系统的初始状态被初始化为 |0⟩|0⟩|1⟩。
为了使算法能够同时计算所有可能的输入，我们对所有量子比特施加 Hadamard 门（H门）。这会将计算比特转化为等概率的叠加态，辅助比特变为 |−⟩ 态：
|ψ₁⟩ = (H⊗H⊗H)|000⟩|1⟩ = [(|00⟩ + |01⟩ + |10⟩ + |11⟩)/√2] ⊗ [(|0⟩ - |1⟩)/√2]

第二步：构造并应用平衡函数 Oracle
Oracle 的作用定义为：|x⟩|y⟩ -> |x⟩|y ⊕ f(x)⟩。
当辅助比特处于 |−⟩ = (|0⟩ - |1⟩)/√2 态时，由于其特有的线性性质，Oracle 的作用会把 f(x) 的值提取到计算比特的相位上（这被称为相位反冲）：
|x⟩(|0 ⊕ f(x)⟩ - |1 ⊕ f(x)⟩)/√2 = (-1)^f(x)|x⟩(|0⟩ - |1⟩)/√2
我们选定平衡函数 f(x₀, x₁) = x₀ ⊕ x₁（即两个比特的异或）。该函数的真值表为：f(00)=0, f(01)=1, f(10)=1, f(11)=0。因为有两个输出0和两个输出1，所以它是平衡的。
将 f(x) 代入叠加态 |ψ₁⟩，Oracle 作用后的态 |ψ₂⟩ 变为：
|ψ₂⟩ = (1/2) [ (-1)⁰|00⟩ + (-1)¹|01⟩ + (-1)¹|10⟩ + (-1)⁰|11⟩ ] ⊗ |−⟩
|ψ₂⟩ = (1/2) [ |00⟩ - |01⟩ - |10⟩ + |11⟩ ] ⊗ |−⟩
此时辅助比特已经解耦，我们可以只关注计算寄存器的状态。

第三步：再次施加 Hadamard 变换
对前两个计算比特再次应用 H 门。H 门的作用不仅可以在基态和叠加态之间转换，还能在计算基下将相位干涉放大。代入 H|0⟩ = (|0⟩+|1⟩)/√2 和 H|1⟩ = (|0⟩-|1⟩)/√2 进行展开：
|ψ₃⟩ = H⊗H [(|00⟩ - |01⟩ - |10⟩ + |11⟩)/2]
计算每一项：
H⊗H|00⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
H⊗H|01⟩ = (|00⟩ - |01⟩ + |10⟩ - |11⟩)/2
H⊗H|10⟩ = (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
H⊗H|11⟩ = (|00⟩ - |01⟩ - |10⟩ + |11⟩)/2
将上述结果依据符号相加：
|ψ₃⟩ = (1/4) [ (1+1+1+1)|00⟩ + (1-1+1-1)|01⟩ + (1+1-1-1)|10⟩ + (1-1-1+1)|11⟩ ]
化简后得到：
|ψ₃⟩ = |11⟩

第四步：测量与结论
对计算寄存器进行测量，我们将百分之百得到结果 |11⟩。因为结果不是 |00⟩，我们确信该函数是平衡函数。如果是常函数，所有的相位将相同（全为+1或全为-1），干涉相长后必然测得 |00⟩。这就是 DJ 算法的绝妙之处。

第五步：isQ 代码实现
在代码中，前两个量子比特对应 x₀ 和 x₁，第三个量子比特是辅助比特。为了实现 f(x) = x₀ ⊕ x₁ 的 Oracle，我们只需分别用 CNOT 将 x₀ 和 x₁ 控制辅助比特即可。

import std;

qbit q[3];

procedure main() {
    // 初始化辅助比特为 |1>
    X(q[2]);

    // 对所有比特施加 Hadamard 门产生叠加态
    for i in 0:3 {
        H(q[i]);
    }

    // 构造对应平衡函数 f(x0, x1) = x0 ⊕ x1 的 Oracle
    // 两次 CNOT 操作等效于将 x0 和 x1 的异或结果累加到辅助比特上
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);

    // 对计算寄存器再次施加 Hadamard 门以进行干涉还原
    H(q[0]);
    H(q[1]);

    // 测量计算寄存器，预期结果恒为 11 (即十进制 3)
    int r0 = M(q[0]);
    int r1 = M(q[1]);
}

## isqTrain/3582

- task_id: `isqTrain/3582`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5431`

### Prompt

Fix the bug in the following isQ program.

Bug description: Missing X gate for state preparation

The program should Draper QFT adder: 1+1=2.

### Chain-of-thought reasoning

Let me analyze this bug carefully.

The program implements a Draper QFT adder that should compute 1+1=2.

The qubit mapping is:
- q[0] = a0 (LSB of a)
- q[1] = a1 (MSB of a)
- q[2] = b0 (LSB of b)
- q[3] = b1 (MSB of b)

The goal is a=01(1) + b=01(1) = 10(2), which means both a and b should be set to 1.

For LSB-first encoding:
- a=01 means a0=1, a1=0, so we need X(q[0]) to set q[0]=|1⟩
- b=01 means b0=1, b1=0, so we need X(q[2]) to set q[2]=|1⟩

The buggy code only has `X(q[2])` but is missing `X(q[0])`.

So the initial state in the buggy code is:
- q[0]=|0⟩, q[1]=|0⟩, q[2]=|1⟩, q[3]=|0⟩

This means a=00(0) and b=01(1), so the result would be 0+1=1 instead of 1+1=2.

The fix is to add `X(q[0])` before `X(q[2])` to set a=01(1).

Now let me trace the corrected circuit:

Initial state: q[0]=1, q[1]=0, q[2]=1, q[3]=0 → |1010⟩ (in q[3]q[2]q[1]q[0] order, that's |0101⟩)

Wait, let me be more careful with the state notation. Let me use |q[3]q[2]q[1]q[0]⟩.

After X(q[0]) and X(q[2]): |1010⟩ wait no.

Actually let me just think in terms of the individual qubits:
- q[0] = |1⟩
- q[1] = |0⟩  
- q[2] = |1⟩
- q[3] = |0⟩

So the full state is |q[3]⟩|q[2]⟩|q[1]⟩|q[0]⟩ = |0⟩|1⟩|0⟩|1⟩ = |0101⟩

Now QFT on b register (q[2], q[3]):

After H(q[2]): q[2] goes from |1⟩ to |−⟩ = (|0⟩ - |1⟩)/√2

After ctrl Rz(π/2, q[3], q[2]): q[3] is |0⟩, so no effect.

After H(q[3]): q[3] goes from |0⟩ to |+⟩

After swap of q[2] and q[3]: q[2] = |+⟩, q[3] = |−⟩

Now add a to b in Fourier space:

ctrl Rz(π, q[0], q[2]): q[0]=|1⟩, so apply Rz(π) to q[2]. Rz(π) = [[e^{-iπ/2}, 0], [0, e^{iπ/2}]] = [[-i, 0], [0, i]]. This adds a phase of i to |1⟩ component and -i to |0⟩ component... actually let me think about this differently.

Actually, in the Draper adder, the phase rotations encode the addition. Let me think about what the predicted output should be.

After all operations, the b register should contain 1+1=2, which in binary is 10, so q[2]=0, q[3]=1 (LSB first).

The expected measurement result is |1011⟩ which in terms of q[3]q[2]q[1]q[0] means q[0]=1, q[1]=0, q[2]=1, q[3]=1.

Wait, but that would mean b = 10 = 2 in decimal? No, q[2]=b0=1, q[3]=b1=1, so b = 11 = 3? That doesn't seem right for 1+1=2.

Hmm, let me re-read. The predicted output {|1011>: 1.0}. In the --probs output format, earlier measured qubit = higher bit.

The measurements are M(q[0]), M(q[1]), M(q[2]), M(q[3]). 

Earlier measured

## isqTrain/71

- task_id: `isqTrain/71`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `3100`

### Prompt

用isQ实现implements the bell_state_preparation pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

Step 1: Understand the Goal
The goal is to write an isQ program that implements the `bell_state_preparation` pattern but uses an alternative gate decomposition for the CNOT gate, which is `CNOT(a, b) -> H(b), CZ(a, b), H(b)`. The final output probabilities must match the standard decomposition, which for The implementation given is `{|11>: 1.0}`.

Wait, Analyzing the circuit requirements, it doesn't just prepare a Bell state and measure. It seems to do some encoding/decoding or just a specific sequence to end up at |11>.
circuit implementation:
q[0], q[1] initialized to |00>.
H(q[0]); H(q[1]) -> |++> = 0.5*(|00> + |01> + |10> + |11>)
CZ(q[0], q[1]) -> 0.5*(|00> + |01> + |10> - |11>)
H(q[1]) -> 1/sqrt(2) * (|0>(|0>+|1>) + |1>(|0>-|1>))/sqrt(2) = 0.5*(|00> + |01> + |10> - |11>)
Z(q[0]); X(q[0]) -> (Y with negative sign? Z*X = -iY. Wait, Z*X|psi> = ZX|psi>. Z then X on |0> -> |1> then -|1> -> -|1>.)
Let's trace it:
State after first CZ:
q[0] is control, q[1] is target.
H(q[0])|0> = |+>
H(q[1])|0> = |+>
|++> -> CZ -> (1/2) (|00> + |01> + |10> - |11>)
Then H(q[1]) -> (1/2) (|00> + |01> + |10> - |11>) wait no.
H on q[1] of (|00> + |01> + |10> - |11>) is:
|0>(|0>+|1>) + |1>(|0>-|1>) = |00>+|01>+|10>-|11>
Wait, applying H to second qubit of |00>+|01> is |0>(|0>+|1>) wait no, |+> + |-> = |0>. So H|+> = |0>. H|-> = |1>.
Let's re-evaluate:
|00> + |01> = |0>|+>. H(q[1]) gives |0>|0>.
|10> - |11> = |1>|->. H(q[1]) gives |1>|1>.
So after first CZ and H(q[1]), the state is |00> + |11>. (This is a Bell state!)
Then Z(q[0]); X(q[0]) on |00> + |11>.
Z(q[0]) makes it |00> - |11>.
X(q[0]) makes it |10> - |01>.
Then H(q[1]): |1>(|0>-|1>) - |0>(|0>-|1>) = |10> - |11> - |00> + |01>.
Then CZ(q[0], q[1]): |10> - (-|11>) - |00> + |01> = |10> + |11> - |00> + |01>.
Then H(q[1]):
|1>(|+>) + |1>(|->) - |0>(|+>) + |0>(|->)
= |1>|0> + |1>|1> - |0>|0> + |0>|1>
Wait, let's do this carefully.
|10> + |11> = |1>|+>. H(q[1]) gives |1>|0>.
- |00> + |01> = -|0>(|0>-|1>) = -|0>|->. H(q[1]) gives -|0>|1>.
So state is |10> - |01>.
Then H(q[0]) and H(q[1])? Wait, the reference has:
H(q[1]);
CZ(q[0], q[1]);
H(q[1]);
H(q[0]);
Let's trace from |10> - |01>.
Wait, before the last CZ, state was -|00> + |01> + |10> + |11>.
Apply CZ(q[0], q[1]):
- |00> + |01> + |10> - |11>
Apply H(q[1]):
|0>(-|0>+|1>) + |1>(|0>-|1
