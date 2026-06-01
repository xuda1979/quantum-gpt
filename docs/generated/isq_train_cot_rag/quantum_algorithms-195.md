# ISQ training COT RAG corpus: quantum_algorithms shard 195

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/985

- task_id: `isqTrain/985`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `405`

### Prompt

Implement a quantum circuit in isQ: implements the suzuki_trotter pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Looking at this task, I need to write a reasoning section for the Suzuki-Trotter decomposition circuit. Let me analyze what the circuit does:

1. The circuit starts with q[0] in |1> and q[1] in |0>, so the initial state is |10>

2. The Suzuki-Trotter decomposition approximates e^(-i*t*(ZZ + XX)) using:
   S2(t) = e^(-i*t/2*ZZ) * e^(-i*t*XX) * e^(-i*t/2*ZZ)

3. The ZZ term is implemented using:
   - CNOT(q[0], q[1])
   - Rz(2*angle, q[1])  - the angle is the coefficient in front of ZZ
   - CNOT(q[0], q[1])

4. The XX term is implemented using:
   - H on both qubits (to change XX to ZZ in the Hadamard basis)
   - CNOT(q[0], q[1])
   - Rz(2*angle, q[1])
   - CNOT(q[0], q[1])
   - H on both qubits

5. After the Suzuki-Trotter evolution, there's an X(q[0]) followed immediately by another X(q[0]), which is an identity operation (gate cancellation).

6. Then measurements are performed.

Let me trace through the state evolution:

Initial state: |10>

After first half ZZ step (t/2 = pi/16):
- CNOT(q[0], q[1]) leaves |10> as |11> (control is 1, so target flips)
- Rz(0.3927) on q[1]: applies phase e^(-i*0.1964) to |11> → the state becomes e^(-i*0.1964)|11>
- CNOT(q[0], q[1]) converts |11> back to |10>

So after first half-step: e^(-i*pi/32)|10>

Wait, I need to recalculate. The Rz gate is defined as:
Rz(θ) = e^(-iθ/2) * [[1, 0], [0, e^(iθ)]]

So Rz(θ)|1> = e^(-iθ/2) * e^(iθ)|1> = e^(iθ/2)|1>

For the ZZ interaction with angle α:
CNOT-Rz(2α)-CNOT implements e^(-iα*ZZ)

For the |10> state:
- After CNOT: |11>
- After Rz(2α) on q[1]: if q[1] is |1>, phase is e^(iα)|11> (plus global phase)
- After CNOT: e^(iα)|10>

Wait, I need to be more careful. Let me think about this again.

ZZ|10> = -|10> (since Z|1> = -|1> and Z|0> = |0>)
ZZ|01> = -|01>
ZZ|00> = |00>
ZZ|11> = |11>

For the CNOT-Rz-CNOT sequence implementing e^(-i*θ/2 * ZZ):
- CNOT(q[0], q[1])
- Rz(θ, q[1])
- CNOT(q[0], q[1])

When applied to |10>:
- CNOT: |11>
- Rz(θ) on q[1]: Rz(θ)|1> = e^(-iθ/2)|1> (up to global phase) Actually let me be precise:
  Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]
  Rz(θ)|1> = e^(iθ/2)|1>
- CNOT: e^(iθ/2)|10>

So the first half-step with θ = 0.3927 gives: e^(i*0.19635)|10>

For the XX step:
XX|10> = |01> (X swaps 0 and 1)

The full XX step uses Hadamard basis transformation.

After Hadamard on both:
|10> → H⊗H |10> = |1> ⊗ H|0> = |1> ⊗ |+> = (1/√2)(|10> + |11>)

Then CNOT-Rz(2t)-CNOT with t = π/8:
CNOT on (1/√2)(|10> + |11>):
= (1/√2)(|10> + |01>) (target flips when control is 1)

Rz(0.7854) on q[

## isqTrain/993

- task_id: `isqTrain/993`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `38`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the qdrift pattern using q[1] -> q[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this qdrift pattern circuit.

1. The goal is to implement a qdrift simulation of H = X + Z on qubit q[0], with an expanded register q[3].

2. We have 3 qubits (q[0], q[1], q[2]), and all are measured. The operations only act on q[0].

3. State evolution:
- Initial state: |000>
- After Rx(π/3) on q[0]: cos(π/6)|000> - i*sin(π/6)|100> = (√3/2)|000> - (i/2)|100>
- After Rz(π/3) on q[0]: This applies phase rotation. Rz(θ) = e^{-iθ/2}|0><0| + e^{iθ/2}|1><1|
  - |0> component: e^{-iπ/6}(√3/2)|000>
  - |1> component: e^{iπ/6}(-i/2)|100>
- After Rx(π/3) on q[0]: Apply Rx(π/3) again.

Let me recalculate more carefully.

Rx(θ) = cos(θ/2)I - i*sin(θ/2)X

Starting with |000>:

**After first Rx(π/3):**
cos(π/6)|0> - i*sin(π/6)|1> = (√3/2)|0> - (i/2)|1>
State: (√3/2)|000> - (i/2)|100>

**After Rz(π/3):**
Rz(θ)|0> = e^{-iθ/2}|0>
Rz(θ)|1> = e^{iθ/2}|1>

For θ = π/3:
e^{-iπ/6}|0> and e^{iπ/6}|1>

State: e^{-iπ/6}(√3/2)|000> - (i/2)e^{iπ/6}|100>
= e^{-iπ/6}(√3/2)|000> - (i/2)(cos(π/6) + i*sin(π/6))|100>
= e^{-iπ/6}(√3/2)|000> - (i/2)((√3/2) + i(1/2))|100>
= e^{-iπ/6}(√3/2)|000> - (i√3/4 + i²/4)|100>
= e^{-iπ/6}(√3/2)|000> - (i√3/4 - 1/4)|100>

This is getting complex. Let me use numerical values.

Let me just compute the probabilities.

Actually, let me think about what Rx(π/3) followed by Rz(π/3) followed by Rx(π/3) does numerically.

Rx(π/3) matrix:
cos(π/6) = √3/2 ≈ 0.8660
sin(π/6) = 1/2 = 0.5

Rx(π/3) = [[0.8660, -0.5i], [-0.5i, 0.8660]]

Rz(π/3) = [[e^{-iπ/6}, 0], [0, e^{iπ/6}]]
e^{-iπ/6} = cos(π/6) - i*sin(π/6) = 0.8660 - 0.5i
e^{iπ/6} = 0.8660 + 0.5i

Total operation U = Rx(π/3) * Rz(π/3) * Rx(π/3)

Starting from |0>:

Step 1: Rx(π/3)|0> = 0.8660|0> - 0.5i|1>

Step 2: Rz(π/3) applied:
= (0.8660 - 0.5i)(0.8660)|0> - (0.8660 + 0.5i)(0.5i)|1>
= (0.8660)(0.8660 - 0.5i)|0> - (0.5i)(0.8660 + 0.5i)|1>
= (0.7499 - 0.4330i)|0> - (0.4330i + 0.25i²)|1>
= (0.7499 - 0.4330i)|0> - (0.4330i -

## isqTrain/3049

- task_id: `isqTrain/3049`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_classical_vars`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `measurement_order`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `437`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```isq
import std;
bool flag;
qbit q[2];
// Conditional correction based on measurement
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    flag = M(q[0]);
    if (flag) {
        X(q[1]);
    }
    M(q[0]);
}

```

### Chain-of-thought reasoning

Let me analyze this bug.

The buggy code:

The corrected code:

The bug is in the last line: `M(q[0])` should be `M(q[1])`.

After the Bell state creation (H + CNOT), we get (|00> + |11>)/√2. Then we measure q[0]. If it's 1, we apply X to q[1]. So if the state was |11>, after X(q[1]) it becomes |10>. If the state was |00>, q[1] stays |0>. So after the conditional correction, the possible states are |00> or |10>, but q[0] has been measured and collapsed. The final measurement should be on q[1] to see the result of the correction.

Expected probabilities: {|01>: 0.5, |10>: 0.5}

Wait, let me re-examine. After H(q[0]) and CNOT(q[0], q[1]), we have (|00> + |11>)/√2.

Measuring q[0]:
- 50% chance: |00> → flag=0, no correction, q[1]=|0⟩. Final measurement of q[1] gives 0. State: q[0]=0, q[1]=0 → but then output would be |00>.
- 50% chance: |11> → flag=1, X(q[1]) applied → q[1] becomes |0⟩. Final measurement of q[1] gives 0. State: q[0]=1, q[1]=0 → |10>.

But expected is {|01>: 0.5, |10>: 0.5}. Hmm, that doesn't match.

Let me reconsider. Maybe I need to think about what the circuit is supposed to do differently. Actually, wait - The predicted output {|01>: 0.5, |10>: 0.5}. 

Maybe the conditional correction should NOT be there, or it's a different kind of protocol. Let me look at this differently.

Actually, wait. If we have the Bell state (|00> + |11>)/√2, and we measure q[0], then:
- If q[0]=0, q[1]=|0⟩, and the final measurement gives |00⟩
- If q[0]=1, q[1]=|1⟩, and we apply X(q[1]) making q[1]=|0⟩, final measurement gives |10⟩

But expected is {|01>: 0.5, |10>: 0.5}. This doesn't match either interpretation.

Hmm, let me reconsider. Maybe the correction is `Z(q[1])` not `X(q[1])`? No, the bug hint says "measurement applied to wrong qubit index."

Wait, maybe the original buggy code measures q[0] twice (which is the bug), and the fix is to measure q[1]. Let me think about what state we're in at the end.

Actually, after measurement of q[0], the quantum state collapses. Let me think about this more carefully.

After H(q[0]) + CNOT(q[0], q[1]): state is (|00⟩ + |11⟩)/√2

Measure q[0]:
- 50%: collapse to |00⟩, flag=0, no X applied
- 50%: collapse to |11⟩, flag=1, X(q[1]) applied → |10⟩

Now if we measure q[1] at the end:
- 50%: |00⟩ → measure q[1]=0, so bitstring is q[0]q[1] = 00
- 50%: |10⟩ → measure q[1]=0, so bitstring is q[0]q[1] = 10

So probabilities would be {|00⟩: 0.5, |10⟩: 0.5}, not {|01⟩: 0.5, |10⟩: 0.5}.

Hmm, but The predicted output {|01⟩: 0.5, |10⟩: 0.5}. Let me think about the indexing convention.

"--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)."

So the first measured qubit is the higher bit, second measured is

## isqTrain/4520

- task_id: `isqTrain/4520`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `interference`, `multi_controlled_logic`, `ancilla_usage`, `isq_syntax_oracle`
- source: `isq_train_cot`
- dataset_index: `857`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;

oracle Uf(3,1) = [0,0,0,0,0,0,1,0];

defgate U0 = [
    1, 0, 0, 0, 0, 0, 0, 0;
    0, -1, 0, 0, 0, 0, 0, 0;
    0, 0, -1, 0, 0, 0, 0, 0;
    0, 0, 0, -1, 0, 0, 0, 0;
    0, 0, 0, 0, -1, 0, 0, 0;
    0, 0, 0, 0, 0, -1, 0, 0;
    0, 0, 0, 0, 0, 0, -1, 0;
    0, 0, 0, 0, 0, 0, 0, -1
];

qbit q[3];
qbit anc;

procedure main() {
    
    H(q[0]); H(q[1]); H(q[2]);
    
    X(anc);
    H(anc);
    
    Uf(q[2], q[1], q[0], anc);
    H(q[0]); H(q[1]); H(q[2]);
    U0(q[2], q[1], q[0]);
    H(q[0]); H(q[1]); H(q[2]);
    
    Uf(q[2], q[1], q[0], anc);
    H(q[0]); H(q[1]); H(q[2]);
    U0(q[2], q[1], q[0]);
    H(q[0]); H(q[1]); H(q[2]);
    
    H(anc); X(anc);
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step quantum circuit analysis of the provided isQ program, ending with a specific predicted probability distribution for the measurement outcomes. The output must be concise (3-15 lines for complex ones).

2.  **Analyze the isQ program**:
    *   **Qubits**: `q[3]`, `anc`. Initial state is $|0000\rangle$ (assuming `q[0]` is highest bit or lowest, standard is $|q_2 q_1 q_0 \text{anc}\rangle$, but isQ standard might map indices to bits in a specific way. Let's trace vector indices).
    *   `H(q[0]); H(q[1]); H(q[2]);` -> State of `q` becomes $|+\rangle|+\rangle|+\rangle = \frac{1}{\sqrt{8}} \sum_{x=0}^7 |x\rangle$.
    *   `X(anc); H(anc);` -> `anc` becomes $|-\rangle$.
    *   Total state before oracles: $\frac{1}{\sqrt{8}} \sum_x |x\rangle |-\rangle$.
    *   `Uf` is a phase oracle: `oracle Uf(3,1) = [0,0,0,0,0,0,1,0]`. Wait, standard oracle `Uf(x)` on $|x\rangle|y\rangle$ is $|x\rangle|y \oplus f(x)\rangle$. If the last qubit is in $|-\rangle$, it acts as a phase oracle: $(-1)^{f(x)} |x\rangle |-\rangle$.
        Wait, let's look at the `Uf` array: `[0,0,0,0,0,0,1,0]`.
        In isQ, `oracle Uf(3,1) = [...]` defines the mapping $|x, y\rangle \to |x, y \oplus f(x)\rangle$. The array `[0,0,0,0,0,0,1,0]` specifies $f(x)$ where $x$ goes from 0 to 7.
        Let's check the array indices: index 0 is 0, index 1 is 0, ..., index 6 is 1, index 7 is 0.
        So $f(6) = 1$, all others are 0. (6 in binary is 110. So $f(110) = 1$).
    *   Wait, Grover's algorithm!
        Let's trace Grover iterations.
        1. `Uf`: Marks $|110\rangle$ (since $f(6)=1$). Wait, is `q[2]` MSB or LSB?
           In isQ, `q[0]` is usually LSB, but wait, the function maps $|x\rangle$ where $x$ is the index. `Uf(q[2], q[1], q[0], anc)` maps `q[2]q[1]q[0]` to some integer. Let's assume standard binary `q[2]q[1]q[0]` is just the integer $x$.
           Actually, `Uf` on $|6\rangle$ gives phase $-1$.
        2. Diffuser: `H H H`, `U0`, `H H H`.
           `U0` is diagonal matrix: `[1, -1, -1, -1, -1, -1, -1, -1]`. This is $2|0\rangle\langle0| - I$, which is the standard Grover diffusion operator $D$.
        3. Number of iterations: The code has TWO iterations of `(Uf, Diffuser)`.
        Wait, for $N=8$, the optimal number of iterations is $\approx \frac{\pi}{4} \sqrt{8} \approx 2.22$. So 2 iterations is good.
    *   Let's calculate the amplitude for $|110\rangle$ after 2 iterations.
        Initial amplitude $a = 1/\sqrt{8} \approx 0.35355$.
        Grover's algorithm amplitude update for the target state $|w\rangle$:
        $a_{w}^{(k)} = \frac{2k+1}{\sqrt{N}}$? No, that's not right.
        Exact formula for amplitude of $|w\rangle$ after $k$ iterations:
        $a_w(k) = \sin((2k+1)\theta)$, where $\sin\theta = 1/\sqrt{N} =

### Reference answer

{'predicted_probs': {'000': 0.007813, '001': 0.007812, '010': 0.007813, '011': 0.007812, '100': 0.007813, '101': 0.007812, '110': 0.007813, '111': 0.945312}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.0078, P(|001>) = 0.0078, P(|010>) = 0.0078, P(|011>) = 0.0078, P(|100>) = 0.0078, P(|101>) = 0.0078, P(|110>) = 0.0078, P(|111>) = 0.9453.'}

## isqTrain/2066

- task_id: `isqTrain/2066`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `data_encoding_qml`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5573`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]); H(q[1]);
    Rz(0.78539816339745, q[0]);
    Rz(1.57079632679490, q[1]);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step quantum state analysis of an isQ program, using Dirac notation, to explain the given probability distribution: {'00': 0.4268, '01': 0.4268, '10': 0.0732, '11': 0.0732}.

2.  **Analyze the isQ code**:
    *   Initialization: `qbit q[2];` -> $|00\rangle$
    *   `H(q[0]); H(q[1]);` -> $H \otimes H |00\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
    *   `Rz(0.78539816339745, q[0]); Rz(1.57079632679490, q[1]);`
        *   $0.78539816339745 = \pi/4$
        *   $1.57079632679490 = \pi/2$
        *   $Rz(\theta) = \begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$
        *   $Rz(\pi/4)$ on $q_0$.
        *   $Rz(\pi/2)$ on $q_1$.
    *   `H(q[0]); H(q[1]);` -> $H \otimes H$ applied to the state after $Rz$.
    *   `M(q[0]); M(q[1]);` -> Measurement.

3.  **Calculate state evolution mathematically**:
    *   Initial: $|\psi_0\rangle = |00\rangle$
    *   After $H \otimes H$: $|\psi_1\rangle = \frac{1}{2} (|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
    *   After $Rz(\pi/4) \otimes Rz(\pi/2)$:
        $|\psi_2\rangle = \frac{1}{2} (e^{-i(\pi/4)/2 - i(\pi/2)/2}|00\rangle + e^{-i(\pi/4)/2 + i(\pi/2)/2}|01\rangle + e^{i(\pi/4)/2 - i(\pi/2)/2}|10\rangle + e^{i(\pi/4)/2 + i(\pi/2)/2}|11\rangle)$
        $|\psi_2\rangle = \frac{1}{2} (e^{-i3\pi/8}|00\rangle + e^{i\pi/8}|01\rangle + e^{i\pi/8}|10\rangle + e^{i3\pi/8}|11\rangle)$
        Wait, let me recheck the angles.
        $\theta_0/2 = \pi/8$, $\theta_1/2 = \pi/4$.
        $|00\rangle \rightarrow e^{-i\pi/8 - i\pi/4} = e^{-i3\pi/8}$
        $|01\rangle \rightarrow e^{-i\pi/8 + i\pi/4} = e^{i\pi/8}$
        $|10\rangle \rightarrow e^{i\pi/8 - i\pi/4} = e^{-i\pi/8}$
        $|11\rangle \rightarrow e^{i\pi/8 + i\pi/4} = e^{i3\pi/8}$
        So $|\psi_2\rangle = \frac{1}{2} (e^{-i3\pi/8}|00\rangle + e^{i\pi/8}|01\rangle + e^{-i\pi/8}|10\rangle + e^{i3\pi/8}|11\rangle)$.
    *   Apply $H \otimes H$:
        $H \otimes H |ab\rangle = \frac{1}{2} (|00\rangle + (-1)^b|01\rangle + (-1)^a|10\rangle + (-1)^{a+b}|11\rangle)$
        $|\psi_3\rangle = \frac{1}{4} [ e^{-i3\pi/8}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) + e^{i\pi/8}(|00\rangle - |01\rangle + |

### Reference answer

{'predicted_probs': {'00': 0.4268, '01': 0.4268, '10': 0.0732, '11': 0.0732}, 'explanation': 'Z feature map encoding [pi/4, pi/2] into 2 qubits.'}

## isqTrain/4093

- task_id: `isqTrain/4093`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `1801`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[4];

unit grover_oracle(qbit q[4]) {
    X(q[1]);
    X(q[2]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    X(q[2]);
    X(q[1]);
} deriving gate

unit grover_diffusion(qbit q[4]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
} deriving gate

procedure main() {
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    for i in 0:3 {
        grover_oracle(q);
        grover_diffusion(q);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

This is a Grover's algorithm circuit with 4 qubits. Let me analyze it step by step.

First, let me understand the oracle. The oracle applies:
1. X(q[1]) and X(q[2]) - flip qubits 1 and 2
2. ctrl<2> CZ(q[0], q[1], q[2], q[3]) - this is a multi-controlled Z gate with 2 control qubits. Wait, let me re-read the syntax.

Actually, looking at the isQ syntax, `ctrl<2> CZ(q[0], q[1], q[2], q[3])` means a CZ gate with 2 additional controls. So CZ normally has 2 qubits (control and target). With `ctrl<2>`, we add 2 more controls, making it a 4-qubit gate. But wait, that doesn't quite make sense either.

Let me reconsider. In isQ, `ctrl<2>` might mean the total number of control qubits is 2. So CZ with ctrl<2> would be a 4-qubit gate where q[0] and q[1] are controls, and the CZ acts on q[2] and q[3]. Or maybe it's different.

Actually, looking at standard isQ syntax, `ctrl<2> CZ(q[0], q[1], q[2], q[3])` likely means: CZ gate with 2 control qubits. The CZ gate itself takes 2 qubits (control, target). So with ctrl<2>, the first 2 qubits are additional controls, and the last 2 are the CZ's control and target. This would be a 4-qubit gate that applies Z to q[3] when q[0], q[1], and q[2] are all |1>.

Wait, let me reconsider. CZ is a 2-qubit gate. With `ctrl<2>`, we specify 2 control qubits plus the original gate's qubits. So we have q[0], q[1] as controls, and q[2], q[3] as the CZ's inputs. The whole thing applies Z on q[3] when q[0]=1, q[1]=1, and q[2]=1.

Hmm, but CZ itself applies Z when control is |1>. So ctrl<2> CZ(q[0], q[1], q[2], q[3]) would apply Z to q[3] when q[0], q[1], and q[2] are all |1>.

So the oracle:
1. X(q[1]), X(q[2]) - flip qubits 1 and 2
2. Apply Z to q[3] when q[0]=1, q[1]=1, q[2]=1 (controlled Z with 3 controls)
3. X(q[2]), X(q[1]) - unflip qubits 1 and 2

After flipping q[1] and q[2], the condition q[0]=1, q[1]=1, q[2]=1 becomes q[0]=1, q[1]=0, q[2]=0 (since we flipped them). So the oracle marks the state |1001⟩ (where q[0]=1, q[1]=0, q[2]=0, q[3] gets phase flipped).

Wait, but it applies Z to q[3], which adds a phase of -1 when q[3]=1. So the state that gets the -1 phase is |1001⟩ (q[0]=1, q[1]=0, q[2]=0, q[3]=1).

So the marked state is |1001⟩. In binary, this is 1001 = 9.

Now, the diffusion operator in Grover's algorithm amplifies the amplitude of the marked state.

With 4 qubits, we have N = 16 possible states. The optimal number of iterations is approximately π/4 * √(N/M) where M is the number of marked states. Here M=1, so optimal iterations ≈ π/4 * 4 ≈ 3.14. So 3 iterations is close to optimal.

Let me compute the state evolution more carefully.

Initial state after Hadamards: |ψ⟩ = (1/4) Σ|x⟩ where the sum is over all 16 basis states.

After one Grover iteration, the amplitude of the marked state increases by approximately 2/√N = 1/2, while other amplitudes decrease.

After k iterations, the amplitude of the marked state is sin((2k+1)θ) where sin(θ) = 1/√16 = 1/4, so θ = arcsin(1/4) ≈

### Reference answer

Deterministic output: state |1001> with probability ~0.96

## isqTrain/1139

- task_id: `isqTrain/1139`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5649`

### Prompt

I need an isQ program to implements the graph_state_preparation pattern using an alternative gate decomposition (CZ -> H CNOT H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

The user wants me to analyze the given isQ program for graph state preparation using an alternative gate decomposition (CZ -> H CNOT H).

Let me trace through the circuit step by step:

1. Start with 3 qubits in |000⟩ state
2. Apply H to all qubits: |000⟩ → |+++⟩ = (1/√8)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

3. For edge (0,1), instead of CZ, we use H on q[1], then CNOT(q[0], q[1]), then H on q[1]:
   - CZ = (I ⊗ H) CNOT (I ⊗ H)
   
   After H(q[1]): state becomes entangled, H on middle qubit
   After CNOT(q[0], q[1]): controlled-NOT with q[0] as control, q[1] as target
   After H(q[1]): completes the CZ decomposition

4. For edge (1,2), same pattern:
   - H(q[2]), CNOT(q[1], q[2]), H(q[2])

5. Then H on all qubits for X-basis measurement, followed by measurement.

Let me trace the state more carefully:

Initial: |000⟩

After H(q[0]), H(q[1]), H(q[2]): |+++⟩

For CZ decomposition on (0,1):
- H(q[1]) applied to |+++⟩:
  |+⟩|+⟩|+⟩ → |+⟩ H|+⟩|+⟩ = |+⟩|0⟩|+⟩ = |+0+⟩

- CNOT(q[0], q[1]):
  |+0+⟩ = (1/√2)(|0⟩ + |1⟩)|0⟩|+⟩
  CNOT with q[0] control, q[1] target:
  = (1/√2)(|00⟩ + |11⟩)|+⟩

- H(q[1]):
  (1/√2)(|0⟩H|0⟩ + |1⟩H|1⟩)|+⟩
  = (1/√2)(|0⟩|+⟩ + |1⟩|−⟩)|+⟩
  
This is equivalent to applying CZ(q[0], q[1]) to |+++⟩

After CZ(0,1) on |+++⟩:
The graph state for edges {(0,1)} is:
|G₁⟩ = (1/2)(|0+⟩ + |1−⟩) ⊗ |+⟩

For CZ decomposition on (1,2):
- H(q[2]):
  |G₁⟩ with H on q[2]: still same structure but with |0⟩ instead of |+⟩ on q[2]
  
- CNOT(q[1], q[2]):
  Creates entanglement between q[1] and q[2]

- H(q[2]):
  Completes the CZ decomposition

After both CZ decompositions, we have the linear graph state |G⟩ for the graph with edges {(0,1), (1,2)}.

The linear graph state |G₃⟩ for 3 qubits is:
|G₃⟩ = (1/2√2)(|000⟩ + |001⟩ + |010⟩ - |011⟩ + |100⟩ + |101⟩ - |110⟩ + |111⟩)

Wait, let me recalculate. The linear graph state is:
|G₃⟩ = CZ₁₂ CZ₀₁ |+++⟩

Let me compute this more carefully.

|+++⟩ = (1/√8) Σᵢ |i₁i₂i₃⟩

CZ₀₁ applies phase -1 when both q[0] and q[1] are |1⟩:
CZ₀₁|+++⟩ = (1/√8)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ - |110⟩ - |111⟩)

CZ₁₂ applies phase -1 when both q[1] and q[2] are |1⟩:
CZ₁₂ CZ₀₁|+++⟩ = (1/√8)(|000⟩ + |001⟩ + |010⟩ - |011⟩ + |100⟩ + |101⟩ - |110⟩ + |111⟩)

Now we apply H to all qubits before measurement (measuring in X basis):

H⊗³ on the graph state transforms it. Let me compute H⊗³|G₃⟩.

H|0⟩ = |+⟩, H|1⟩ = |−⟩

Actually, measuring in X basis means applying H then measuring in

## isqTrain/1417

- task_id: `isqTrain/1417`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1399`

### Prompt

Write an isQ program that Apply the 3-qubit Quantum Fourier Transform to the input state |000> and measure all qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply the 3-qubit QFT to |000>, producing a uniform superposition, then measure all qubits.
Three qubits (q[0], q[1], q[2]) are used and all are measured.

State evolution (using qubit order q[2]q[1]q[0]):
- |000> → H(q[2]) → (|000>+|001>)/√2 (controlled gates on q[2] do nothing since q[1]=q[0]=0)
- H(q[1]) → (|000>+|001>+|010>+|011>)/2 (ctrl S(q[0],q[1]) does nothing since q[0]=0)
- H

## isqExpand/algo/81

- task_id: `isqExpand/algo/81`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `grover`, `multi_solution`, `amplitude_amplification`, `oracle`
- source: `isq_expansion`
- dataset_index: `1471`

### Prompt

Write an isQ program that implements Grover's algorithm on 3 qubits with two marked states: |000> and |111>. Apply exactly one Grover iteration. With M=2 solutions out of N=8 states, one iteration achieves perfect success (total probability 1.0 on marked states). The oracle should mark both states: use X gates on all qubits plus CCZ for |000>, and a plain CCZ for |111>.

### Chain-of-thought reasoning

## 推理
目标：3比特Grover同时搜索|000>和|111>。

### Oracle设计
1. 标记|000>: X(q[0]); X(q[1]); X(q[2]); ctrl @[q[0],q[1]] Z(q[2]); X(q[0]); X(q[1]); X(q[2]);
2. 标记|111>: ctrl @[q[0],q[1]] Z(q[2]); （CCZ直接在|111>上触发）

### 最优迭代次数
N=8, M=2: theta = arcsin(sqrt(M/N)) = arcsin(sqrt(1/4)) = arcsin(1/2) = pi/6
1次迭代后: P_total = sin^2((2*1+1)*pi/6) = sin^2(pi/2) = 1.0

因为两个目标态的振幅对称，每个标记态的概率为0.5。

预期概率: |000>(index 0) = 0.5, |111>(index 7) = 0.5, 其余 = 0.0

## isqQA/quantum_algorithms/86_optimization_variant

- task_id: `isqQA/quantum_algorithms/86_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `optimization_variant`, `algorithm`, `Deutsch算法原理`
- source: `qa_pipeline`
- dataset_index: `1417`

### Prompt

作为早期的量子算法，Deutsch算法证明了量子计算的并行潜力，但其仅处理单比特输入，实际应用受限。请问该算法有哪些重要的改进版本或变体？能否以最著名的推广版本为例，阐述其核心原理，并提供对应的isQ量子程序代码实现？

### Reference answer

<thought>Deutsch算法最重要的改进版本是Deutsch-Jozsa算法（DJ算法）。它将原本仅针对1位输入输出的函数推广到了n位输入输出的函数。在经典计算中，确定一个n位函数是常数（所有输入映射到同一值）还是平衡（一半输入映射到0，另一半映射到1），在最坏情况下需要查询预言机2^(n-1)+1次。而Deutsch-Jozsa算法利用量子叠加和干涉效应，仅需1次查询即可得出确定性结论，实现了相对于经典确定性算法的指数级加速。这为后来更复杂的算法（如Shor算法、Grover算法）奠定了相位反转和振幅放大的基础。

在isQ代码实现中，我们可以设定一个2量子比特的输入寄存器（n=2）和1个辅助量子比特。为了演示，我们可以将预言机硬编码为一个平衡函数（例如f(x0, x1) = x0 XOR x1）。电路的主要步骤包括：初始化辅助比特为|->态，对输入寄存器施加Hadamard门，执行预言机操作，再次对输入寄存器施加Hadamard门，最后测量。如果测量结果全为0，则函数为常数；否则为平衡函数。</thought>

Deutsch算法最著名且最重要的改进版本是**Deutsch-Jozsa算法（D-J算法）**。虽然原始的Deutsch算法仅针对单比特输入和输出的函数，证明了量子并行性，但其解决问题的范畴过于局限。David Deutsch和Richard Jozsa在1992年将其进行了多维度的推广，提出了Deutsch-Jozsa算法，这也成为了量子计算发展史上的一个重要里程碑。

**Deutsch-Jozsa算法的原理与改进：**
该变体处理的是一个N位输入、1位输出的黑盒函数。问题定义为：给定一个这样的函数，承诺它要么是“常数”（对所有输入都输出相同的0或1），要么是“平衡”（恰好对一半的输入输出0，另一半输出1）。在经典确定性计算中，最坏情况下需要查询预言机 $2^{N-1} + 1$ 次才能百分之百确定；而Deutsch-Jozsa算法利用量子叠加态，只需要**1次**查询就能以100%的概率得出结论，相对于经典确定性算法实现了指数级加速。

其核心物理机制在于量子干涉。算法将N个输入量子比特置于等概率叠加态，并将辅助量子比特置于 $| - 
angle$ 态。经过黑盒预言机作用后，函数值的信息被编码在量子态的相对相位中。第二次对输入寄存器施加Hadamard变换时，由于干涉效应，如果函数是常数，所有的概率幅会相长干涉汇聚到 $|00...0
angle$ 态；如果函数是平衡的，$|00...0
angle$ 态的概率幅则会相消干涉变为0。

以下是使用isQ语言编写的Deutsch-Jozsa算法代码示例（以 $N=2$ 为例，内置了一个平衡函数 $f(x_0, x_1) = x_0 \oplus x_1$ 的预言机）：

```isQ
import std;

// 声明3个量子比特：q[0]和q[1]为输入寄存器，q[2]为辅助寄存器
qbit q[3];

procedure main() {
    // 1. 初始化辅助比特到 |-> 状态
    X(q[2]);
    H(q[2]);
    
    // 2. 对输入寄存器施加Hadamard门，使其进入叠加态
    H(q[0]);
    H(q[1]);
    
    // 3. 执行预言机
    // 这里我们实现一个平衡函数：f(x0, x1) = x0 XOR x1
    // 等价于分别用q[0]和q[1]控制辅助比特q[2]翻转
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    
    // 4. 再次对输入寄存器施加Hadamard门
    H(q[0]);
    H(q[1]);
    
    // 5. 测量输入寄存器
    // 若函数为常数，则必测量得到 00
    // 若函数为平衡，由于干涉，测量结果必然不为 00 (如01, 10, 11)
    M(q[0]);
    M(q[1]);
}
```

除了Deutsch-Jozsa算法之外，另一个基于类似原理的重要变体是**Bernstein-Vazirani算法**。它将问题转变为寻找隐藏在黑盒中的秘密字符串。这些算法共同展示了如何通过巧妙的量子电路设计操纵相位，从而提取出经典计算难以高效获取的全局结构信息，为后续的Shor算法和Grover算法奠定了坚实的理论基础。
