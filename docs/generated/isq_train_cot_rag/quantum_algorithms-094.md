# ISQ training COT RAG corpus: quantum_algorithms shard 94

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2026

- task_id: `isqTrain/2026`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_deriving_gate`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4332`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[2];
procedure my_z(qbit a) {
    Z(a);
} deriving gate
procedure main() {
    H(q[0]); H(q[1]);
    ctrl my_z(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

The user wants to analyze an isQ program and predict the probability distribution of measurement outcomes.
The isQ program applies the following gates to a 2-qubit register `q`:
1. `H(q[0]); H(q[1]);` -> Both qubits are put into the |+> state. Initial state |00> -> |+> |+> = 1/2(|00> + |01> + |10> + |11>)
2. `ctrl my_z(q[0], q[1]);` -> Controlled-Z gate between q[0] (control) and q[1] (target).
Wait, `my_z(a)` is just `Z(a)`.
`ctrl my_z(q[0], q[1])` means `q[0]` controls the application of `my_z(q[1])`. Wait, in `ctrl my_z(q[0], q[1])`, wait, isQ syntax: `ctrl` applies the gate with the control qubit added. But the procedure takes one parameter: `procedure my_z(qbit a)`. So `my_z(q[1])` applies Z to q[1].
Wait, `ctrl my_z(q[0], q[1])` in isQ: `ctrl` consumes the control qubit from the argument list. So `q[0]` is the control, `q[1]` is the target.
Thus, CZ(q[0], q[1]) is applied.
Let's check the state evolution:
Initial: |00>
After H, H: 1/2 (|00> + |01> + |10> + |11>)
After CZ: 1/2 (|00> + |01> + |10> - |11>) -> This is equivalent to measuring in the Hadamard basis. Wait, H|0> = |+>, H|1> = |->. If we apply H on both again, we get |00>.
But here we only apply CZ.
The state is $|\psi\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$.
Wait, let me read the expected outcome: {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}.
Ah! The probability of measuring $|00\rangle$ is $(1/2)^2 = 0.25$, etc. CZ only introduces phases, it doesn't change the probabilities of the computational basis states.
Let's trace carefully:
$|00\rangle \xrightarrow{H \otimes H} \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
$\xrightarrow{CZ} \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$
Probabilities are $|1/2|^2 = 0.25$ for each of the 4 states.

Format requirements:
- Output ONLY the analysis, starting with "## Circuit Analysis"
- Do NOT include code blocks
- End with the predicted probability distribution
- 3-8 lines for simple circuits.

Let's draft the response:
## Circuit Analysis
1. The circuit initializes a 2-qubit register to |00>. It applies H gates to both qubits, followed by a Controlled-Z (CZ) gate where q[0] is the control and q[1] is the target.
2. Initial state: |00>.
3. After H on both qubits: 1/2(|00> + |01> + |10> + |11>).
4. The CZ gate applies a phase of -1 when both are |1>: 1/2(|00> + |01> + |10> - |11>).
5. Measuring both qubits in the computational basis yields an equal probability of 0.25 for each of the four possible states, since the phase change does not affect magnitudes.

Predicted probability distribution: {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}

Let's refine to fit 3-8 lines.

## Circuit Analysis
1. The circuit applies H gates to two qubits initially in |00>, followed by a Controlled-Z gate (defined via `ctrl my_z`).
2. State after H gates: 1/2(|00> + |01> + |10> + |11>).
3. The CZ gate flips the phase of the |11> state, resulting in: 1/2(|00> + |01> + |10> - |11>).
4. Because phase shifts do not affect

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'Phase oracle on uniform superposition: all probabilities remain 0.25 since measurement is phase-insensitive.'}

## isqTrain/3510

- task_id: `isqTrain/3510`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `basis_change`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5715`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```
import std;

qbit q[3];
qbit anc[2];

procedure main() {
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    H(q[0]); H(q[1]); H(q[2]);

    Z(q[1]);

    H(q[0]); H(q[1]); H(q[2]);

    CNOT(q[0], anc[0]);
    CNOT(q[1], anc[0]);
    CNOT(q[1], anc[1]);
    CNOT(q[2], anc[1]);

    ctrl ctrl X(anc[0], anc[1], q[1]);

    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

The circuit applies operations to 3 data qubits and 2 ancilla qubits.

Initial state: |00000> (q[0], q[1], q[2], anc[0], anc[1])

After CNOT(q[0], q[1]) -> |00000>
After CNOT(q[0], q[2]) -> |00000>

H(q[0]) H(q[1]) H(q[2]) on |000> (first 3 qubits):
State of q[0..2] becomes |+++> = (1/2√2)(|000>+|001>+|010>+|011>+|100>+|101>+|110>+|111>)

Z(q[1]) applies Z to q[1].
This flips the sign of states where q[1] = 1.
In the |+++> state, applying Z(q[1]) changes |+> to |-> on q[1], so the state becomes |+ - +>.

H(q[0]) H(q[1]) H(q[2]):
H Z H = X.
H(q[1]) converts Z(q[1]) in the H basis to X(q[1]) in the computational basis.
Actually, H Z H = X.
So the combined operation H H H Z H H H on q[0..2] is:
H⊗3 Z1 H⊗3 |+++> = H⊗3 Z1 |000> = H⊗3 (|000> - |010>) / √2? No wait.

Let me trace more carefully.
Initial state of q[0..2]: |000>
After CNOT(q[0], q[1]) and CNOT(q[0], q[2]): |000>
After H(q[0]) H(q[1]) H(q[2]): |+++> = 1/(2√2) sum_x |x>

Now Z(q[1]):
Z on |+> gives |->.
Z on |-> gives |+>.
Z on |0> gives |0>.
Z on |1> gives -|1>.

State of q[1] before Z is |+>.
State of q[1] after Z is |->.
State of q[0..2] after Z(q[1]) is |+ -> +>.

Now H(q[0]) H(q[1]) H(q[2]):
H on q[0]: |+> -> |0>
H on q[1]: |-> -> |1>
H on q[2]: |+> -> |0>
So state of q[0..2] becomes |010>.
The overall state is |01000>.

Now CNOT(q[0], anc[0]): q[0]=0, so anc[0] remains 0. State: |01000>
CNOT(q[1], anc[0]): q[1]=1, so anc[0] flips to 1. State: |01010>
CNOT(q[1], anc[1]): q[1]=1, so anc[1] flips to 1. State: |01011>
CNOT(q[2], anc[1]): q[2]=0, so anc[1] remains 1. State: |01011>

ctrl ctrl X(anc[0], anc[1], q[1]):
anc[0] = 1, anc[1] = 1, so X is applied to q[1].
q[1] was 1, so it flips to 0.
State becomes |00011>.

M(q[0]) -> 0
M(q[1]) -> 0
M(q[2]) -> 0

Wait, let me re-evaluate H H H Z H H H on |000>.
H on |000> gives |+++>.
Z on q[1] of |+++>:
|+> = (|0>+|1>)/√2
|-> = (|0>-|1>)/√2
Z_1 |+++> = |+ -> +>
H_1 |-> = |1>
H_0 |+> = |0>
H_2 |+> = |0>
So H H H Z_1 H H H |000> = |010>. This is correct.

CNOT(q[0], anc[0]) on |010>_{q} |00>_{anc}:
q[0]=0 -> anc[0] unchanged. State: |01000>
CNOT(q[1], anc[0]):
q[1]=1 -> anc[0] flips. State: |01010>
CNOT(q[1], anc[1]):
q[1]=1 -> anc[1] flips. State: |01011>
CNOT(q[2], anc[1]):
q[2]=0 -> anc[1

### Reference answer

{'predicted_probs': {'000': 1.0}, 'explanation': 'The output is |000> with probability 1.0'}

## isqTrain/3812

- task_id: `isqTrain/3812`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3112`

### Prompt

Implement the following in isQ: the swap test to compare states |+> vs |->. Use:
1. q[0] as ancilla, q[1] for state A, q[2] for state B
2. A controlled-SWAP (Fredkin) gate via CNOT+Toffoli
3. Hadamard on ancilla before and after CSWAP
4. Measure all 3 qubits. P(ancilla=0) = (1+|<A|B>|²)/2.

### Chain-of-thought reasoning

Let me analyze this swap test circuit step by step.

The goal is to implement a swap test to compare states |+> and |->.

**Initial state:** |000>

**Step 1: Prepare state A (|+>) on q[1]**
H(q[1]) → |0+0> = |000> + |010>) / √2

**Step 2: Prepare state B (|->) on q[2]**
X(q[2]); H(q[2]) → first X gives |1> on q[2], then H gives |-> = (|0> - |1>)/√2

State becomes: |0>(|0>(|0>-|1>)/√2 + |1>(|0>-|1>)/√2)/√2
= |0>(|00> - |01> + |10> - |11>)/2

**Step 3: H on ancilla q[0]**
H(q[0]) → (|0> + |1>)(|00> - |01> + |10> - |11>)/2√... wait let me redo this more carefully.

After preparations: q[0]=|0>, q[1]=|+>, q[2]=|->

State = |0> ⊗ (|0>+|1>)/√2 ⊗ (|0>-|1>)/√2
= |0>(|0>(|0>-|1>) + |1>(|0>-|1>))/2
= (|000> - |001> + |010> - |011>)/2

**Step 4: H(q[0])**
H on q[0]:
(|0>+|1>)⊗(|0>+|1>)⊗(|0>-|1>) / 2√... no wait

H on ancilla:
State = (|0>+|1>)/√2 ⊗ (|00>-|01>+|10>-|11>)/2

Actually let me write it as:
(|0> + |1>)(|000> - |001> + |010> - |011>) / (2√2)

**Step 5: Cswap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition))**

Cswap (three-CNOT decomposition) swaps q[1] and q[2] when q[0]=|1>.

Let me track what happens to each component:
- When q[0]=|0>: no swap → terms stay
- When q[0]=|1>: swap q[1]↔q[2]

|000> → |000> (no change since q[1]=q[2]=0)
|001> → |010> (swap q[1]=0, q[2]=1 → q[1]=1, q[2]=0)
|010> → |001> (swap q[1]=1, q[2]=0 → q[1]=0, q[2]=1)
|011> → |011> (no change since q[1]=q[2]=1)

So after Cswap (three-CNOT decomposition):
State = (|0>(|000>-|001>+|010>-|011>) + |1>(|000>-|010>+|001>-|011>)) / (2√2)
= (|0>(|000>-|001>+|010>-|011>) + |1>(|000>+|001>-|010>-|011>)) / (2√2)

**Step 6: H(q[0])**

Applying H on q[0]: |0>→(|0>+|1>)/√2, |1>→(|0>-|1>)/√2

State = ((|0>+|1>)(|000>-|001>+|010>-|011>) + (|0>-|1>)(|000>+|001>-|010>-|011>)) / 4

Let me collect by basis states:

For q[0]=|0>:
Coefficient = (|000>-|001>+|010>-|011>) + (|000>+|001>-|010>-|011>) 
= 2|000> + 0|001> + 0|010> - 2|011>
= 2(|000> - |011>)

For q[0]=|1>:
Coefficient = (|000>-|001>+|010>-|011>) - (|000>+|001>-|010>-|011>)
= 0|000> - 2|001> + 2|010> + 0|011>
= -2|001> + 2|010>
= 2(-|001> + |010>)

So final state = (

## isqTrain/2871

- task_id: `isqTrain/2871`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2081`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```isq
import std;
qbit q[2];
// phase kickback with controlled-Z
procedure main() {
    // X(q[1]); // BUG: missing initialization
    H(q[0]);
    ctrl Z(q[0], q[1]);
    H(q[0]);
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: `X(q[1])` is commented out on line 7, leaving q[1] in |0> instead of |1>.

2. **Fix**: Uncomment `X(q[1])` to initialize q[1] to |1>.

3. **State evolution (corrected)**:
   - |00⟩ → X(q[1]) → |01⟩
   - H(q[0]) → (|01⟩ + |11⟩)/√2
   - ctrl Z: when q[0]=|1⟩, Z|1⟩ = −|1⟩ → (|01⟩ − |11⟩)/√2 (phase kickback flips control phase)
   - H(q[0]) → |11⟩
   - Measurement yields |11⟩ with probability 1.0 ✓

## isqTrain/3497

- task_id: `isqTrain/3497`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1905`

### Prompt

预测以下isQ代码的输出概率：

```
import std;

qbit q[1];

procedure main() {
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 1 qubit, q[0], to the state |0>.
2. The Hadamard gate `H(q[0])` is applied, evolving the state to |+> = (1/sqrt(2))|0> + (1/sqrt(2))|1>.
3. The measurement `M(q[0])` collapses the equal superposition.

Predicted probability distribution:
- |0>: 50%
- |1>: 50%

### Reference answer

Probability distribution: |0>: 0.5, |1>: 0.5

## isqTrain/4096

- task_id: `isqTrain/4096`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `1259`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[4];

unit grover_oracle(qbit q[4]) {
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
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

1.  **Analyze the Request:**
    *   **Circuit:** isQ code implementing Grover's algorithm on 4 qubits.
    *   **Oracle:** `ctrl<2> CZ(q[0], q[1], q[2], q[3])`. Wait, this is a multi-controlled Z gate. `ctrl<2> CZ(a, b, c, d)` usually implies Toffoli-like but with CZ? Actually, in isQ `ctrl<2> CZ(a, b, c, d)` is a 4-qubit gate where the last qubit is the target, so it flips the phase of |1111>. Wait, `ctrl<2>` usually means 2 controls. But CZ has 1 control, so adding 2 makes 3 controls? Let me check isQ syntax: `ctrl<N>` adds N controls. So `ctrl<2> CZ` on 4 qubits means 3 controls and 1 target (from the original CZ). So it's a 4-qubit gate: phase flip on |1111>. Let's assume standard behavior: the oracle marks |1111>.
    *   **Diffusion:** H, X, ctrl<2> CZ, X, H. This is the standard Grover diffusion operator on 4 qubits.
    *   **Iterations:** 3 iterations (`for i in 0:3` which is 0, 1, 2 in typical notation, but wait! In isQ, `a:b` is inclusive of `a`, exclusive of `b`? Yes, typically `0:3` means i=0, 1, 2. That is 3 iterations). Let's check the number of iterations. Wait, $N=2^4=16$. Optimal iterations $R \approx \frac{\pi}{4} \sqrt{N} = \frac{\pi}{4} \sqrt{16} = \pi \approx 3.14$. So 3 iterations is very close to optimal!
    *   **Goal:** Predict the measurement output, describe probability distribution, using Dirac notation, concise (3-15 lines).

2.  **Step-by-step state evolution:**
    *   Initial state: $|0000\rangle$.
    *   Apply H to all: $\frac{1}{4} \sum_{x=0}^{15} |x\rangle$. Let's denote the target state $|w\rangle = |1111\rangle$ and the uniform superposition $|s\rangle = \frac{1}{4} \sum |x\rangle$.
    *   Grover iteration: Apply Oracle ($U_w$), then Diffusion ($U_s$).
    *   $U_w$ flips the sign of $|1111\rangle$.
    *   $U_s$ inverts about the mean.
    *   After 1 iteration: amplitude of $|w\rangle$ goes from $1/4$ to $3 \times (1/4) = 3/4$ roughly?
        *   Initial amplitude $a = 1/4$. Mean of amplitudes before $U_s$: 14 of them are $1/4$, one is $-1/4$. Mean is $(14/4 - 1/4)/16 = 13/64$.
        *   Wait, $a' = 2 \mu - a_{old} = 2(13/64) - (-1/4) = 26/64 + 16/64 = 42/64 = 21/32 \approx 0.656$.
    *   Let's trace exactly:
        *   $\sin(\theta/2) = 1/4 \implies \theta/2 \approx \arcsin(0.25) \approx 14.477^\circ$. So $\theta \approx 28.955^\circ$.
        *   After $k$ iterations, amplitude of $|w\rangle$ is $\sin((2k+1)\theta/2)$.
        *   For $k=3$: $2k+1 = 7$. Angle $= 7 \times 14.477^\circ = 101.34^\circ$.
        *   $\sin(101.34^\circ) \approx \sin(78.66^\circ) \approx 0.9806$.
    *   Probability of $|1111\rangle$ is $0.9806^2 \approx 96.1\%$.
    *   Probability of other states (e.g., |0000>, |0001>, etc.): uniform and very low (~0.26% each).

3.  **Drafting the Analysis:**
    *   *Operations:* Initializes $|0000

### Reference answer

Deterministic output: state |1111> with probability ~0.96

## isqTrain/2929

- task_id: `isqTrain/2929`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4228`

### Prompt

Write isQ code for the following quantum task: applies a controlled Rz rotation of 1*pi/2 radians. Put the control qubit in superposition with H, set the target to |1>, apply controlled Rz, then H on the control. Measure both.

Requirements:
- Declare `qbit q[2];` at global scope.
- Use `procedure main()` as entry point.
- Measure both qubits.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |00⟩

1. H(q[0]): Puts control qubit in superposition → (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2

2. X(q[1]): Flips target qubit → (|01⟩ + |11⟩)/√2

3. ctrl Rz(π/2, q[0], q[1]): This applies Rz(π/2) to q[1] only when q[0] is |1⟩

Rz(θ) = [[1, 0], [0, e^(iθ)]]

Rz(π/2) = [[1, 0], [0, e^(iπ/2)]] = [[1, 0], [0, i]]

So when q[0] = |1⟩:
- |11⟩ gets multiplied by i in the amplitude of |11⟩'s target part
- Actually, Rz(π/2)|0⟩ = |0⟩, Rz(π/2)|1⟩ = i|1⟩

State becomes: (|01⟩ + i|11⟩)/√2

4. H(q[0]): Apply H to control qubit
H|0⟩ = (|0⟩ + |1⟩)/√2
H|1⟩ = (|0⟩ - |1⟩)/√2

So:
|01⟩ → (|0⟩ + |1⟩)/√2 ⊗ |1⟩ = (|01⟩ + |11⟩)/√2
i|11⟩ → i(|0⟩ - |1⟩)/√2 ⊗ |1⟩ = i(|01⟩ - |11⟩)/√2

Total: (|01⟩ + |11⟩ + i|01⟩ - i|11⟩)/(2)
= ((1+i)|01⟩ + (1-i)|11⟩)/2

Probabilities:
P(|01⟩) = |1+i|²/4 = (1+1)/4 = 2/4 = 1/2
P(|11⟩) = |1-i|²/4 = (1+1)/4 = 2/4 = 1/2

Wait, that gives 0.5 each, not the expected 0.8535 and 0.1464. Let me reconsider.

Hmm, The predicted output {|01>: 0.853553448362991, |11>: 0.14644655163700912}

0.8535534 ≈ (1 + 1/√2)/2 ≈ (2 + √2)/4 ≈ 0.8536
0.1464466 ≈ (1 - 1/√2)/2 ≈ (2 - √2)/4 ≈ 0.1464

Let me re-examine the controlled Rz gate. 

Actually, wait. In isQ, `ctrl Rz(1.570796, q[0], q[1])` - is the control q[0] or q[1]?

Looking at the syntax: `ctrl @[c1, c2] Gate(target);`

For `ctrl Rz(1.570796, q[0], q[1])`, the format seems to be ctrl Gate(args...), where q[0] is the control and q[1] is the target for Rz.

But wait, let me reconsider. Rz normally takes one qubit. With ctrl, it takes control first then target.

So `ctrl Rz(theta, control, target)` applies Rz to target when control is |1⟩.

Hmm, but the predicted output don't match my calculation. Let me think about this differently.

Actually, wait. Let me reconsider the Rz gate definition. Some frameworks define Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]], not [[1, 0], [0, e^(iθ)]].

If Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]], then:
Rz(π/2) = [[e^(-iπ/4), 0], [0, e^(iπ/4)]]

Hmm, but that would still give equal probabilities after the second H because the relative phase just rotates.

Wait, actually let me reconsider. Let me look at what happens more carefully.

After step 2: (|01⟩ + |11⟩)/√2 = (|0⟩ + |1⟩)/√2 ⊗ |1⟩

After controlled Rz

## isqTrain/2917

- task_id: `isqTrain/2917`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_classical_vars`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `502`

### Prompt

用isQ实现teleports the |0> state using the quantum teleportation protocol. Create a Bell pair, perform Bell measurement, and apply conditional corrections.

Requirements:
- Use 3 qubits and 2 classical bits.
- Implement the teleportation procedure.
- Measure the destination qubit.

### Chain-of-thought reasoning

The user wants to generate a quantum teleportation program in isQ that teleports the |0> state.
Let's trace the standard quantum teleportation circuit.
Goal: Teleport the state of qubit 1 (|0>) to qubit 3 using qubit 2 as the ancilla, and measure qubit 3 at the end to verify (or just measure all).
Wait, The resulting probabilities should be {|001>: 0.25, |010>: 0.25, |101>: 0.25, |110>: 0.25}.
Wait, In the implementation, `q_1` is qsrc, `q_2` is qanc, `q_3` is qdest.
The state is |000> initially.
H(q_2) -> |0>|+>|0>
CNOT(q_2, q_3) -> |0>|00> + |1>|11> over sqrt(2) -> |0> (|00> + |11>) / sqrt(2)
Since q_1 is |0>, the state is |000> + |011> (over sqrt 2).
CNOT(q_1, q_2) -> q_1 controls q_2. So |000> + |011> stays the same because q_1 is |0>.
H(q_1) -> H acts on |0>, making it |0>+|1> over sqrt 2.
State: (|000> + |011> + |100> + |111>) / 2
Wait, wait. Let's carefully write down the qubits in order q1, q2, q3.
Initially |000>.
H(q_2): |0>(|0>+|1>)|0> / sqrt 2
CNOT(q_2, q_3): |0>(|00>+|11>) / sqrt 2
CNOT(q_1, q_2): q_1 is 0, so it doesn't affect q_2. Still |000> + |011>.
H(q_1): (|0>+|1>)(|00>+|11>) / 2 = (|000> + |011> + |100> + |111>) / 2.
Wait, why are the predicted output for `|001>` and `|010>` etc.?
Ah! the predicted output in the prompt say: `{|001>: 0.25, |010>: 0.25, |101>: 0.25, |110>: 0.25}`.
Wait, if the state is (|000> + |011> + |100> + |111>) / 2, then M(q_1) and M(q_2) will yield 00, 01, 10, 11 with equal probability.
If M(q_1) = 0 and M(q_2) = 0, q_3 is 0. If m1=1, m2=0, q_3 is 1.
Let's trace the corrections:
If m2 (which is M(q_2)) is 1, X(q_3). If m1 is 1, Z(q_3).
But q_3 was 0 when m2=0, and 1 when m2=1.
Wait. If m1=0, m2=0: q_3 is 0. No corrections. M(q_3) = 0. Total |000>.
If m1=0, m2=1: q_3 is 1. Correction X(q_3). q_3 becomes 0. M(q_3)=0. Total |010>.
If m1=1, m2=0: q_3 is 0. Correction Z(q_3). q_3 remains 0. M(q_3)=0. Total |000>? Wait.
If m1=1, m2=0, state is |100>. M(q1)=1. Correction: Z(q3). M(q3)=0. So it's |100>.
If m1=1, m2=1, state is |111>. Correction X(q3) then Z(q3). M(q3)=0. Total |110>.
So the final states before final M(q3) are always having q3 in |0>.
Wait! The prompt says `Expected measurement probabilities: {|001>: 0.25, |010>: 0.25, |101>: 0.25, |110>: 0.25}`.
Why is there a 1 in the last bit for some of them?
Ah, wait. In the implementation, `q_1` is `qsrc`. It is initialized to `|0>`.
Wait! In isQ, global variables are initialized to `|0>`.
Does

## isqTrain/3530

- task_id: `isqTrain/3530`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1899`

### Prompt

What is the measurement probability distribution of this isQ program?

```
import std;

qbit q[3];
qbit anc[2];

procedure main() {
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);

    X(q[2]);

    CNOT(q[0], anc[0]);
    CNOT(q[1], anc[0]);
    CNOT(q[1], anc[1]);
    CNOT(q[2], anc[1]);

    nctrl ctrl X(anc[0], anc[1], q[2]);

    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The objective is to analyze an isQ quantum program, determine the quantum state evolution step-by-step, and output the final measurement probability distribution over the measured qubits (q[0], q[1], q[2]).

2.  **Analyze the Circuit**:
    *   **Qubits**: `q[3]` (q0, q1, q2) and `anc[2]` (a0, a1). Measured qubits: `q[0], q[1], q[2]`.
    *   **Initial State**: $|00000\rangle$ (q0, q1, q2, a0, a1). Order is usually declaration order or parameter order. Let's stick to $|q_0 q_1 q_2 a_0 a_1\rangle$.
    *   **Operations**:
        1.  `CNOT(q[0], q[1])`: If $q_0=1$, flip $q_1$.
        2.  `CNOT(q[0], q[2])`: If $q_0=1$, flip $q_2$.
        3.  `X(q[2])`: Flip $q_2$.
        4.  `CNOT(q[0], anc[0])`: If $q_0=1$, flip $a_0$.
        5.  `CNOT(q[1], anc[0])`: If $q_1=1$, flip $a_0$.
        6.  `CNOT(q[1], anc[1])`: If $q_1=1$, flip $a_1$.
        7.  `CNOT(q[2], anc[1])`: If $q_2=1$, flip $a_1$.
        8.  `nctrl ctrl X(anc[0], anc[1], q[2])`: This is a multi-controlled X. In isQ, `nctrl ctrl X(c1, c2, target)` is typically a Toffoli gate but wait, "nctrl" means "negative controls" or "non-controlled"?
            *Wait, isQ syntax:* `nctrl ctrl X(anc[0], anc[1], q[2])` -> Let's check the syntax reference. "Control modifier: ctrl @[c1, c2] Gate(target)". The code says `nctrl ctrl X(anc[0], anc[1], q[2])`. Wait, isQ doesn't use `nctrl` in the prompt's provided syntax reference! Let me re-read the prompt's syntax reference.
            "Control modifier: `ctrl @[c1, c2] Gate(target);`"
            Wait, what is `nctrl ctrl X`? In some isQ versions, `ctrl X` is CNOT. `ctrl ctrl X` is Toffoli. What does `nctrl` mean? Could it mean "negative control"? If so, it triggers when controls are 0.
            Wait, maybe `nctrl` is a typo for something or specific to isQ? Actually, looking closely: "nctrl ctrl X(anc[0], anc[1], q[2])" - "nctrl" is NOT in the provided syntax reference. However, if `nctrl` means negative control, it would trigger when anc[0]==0 and anc[1]==0.
            Let me search my knowledge base for "isQ nctrl". "nctrl" might mean "native controlled" or "negative control". Let's assume negative control for a moment, or maybe it means Toffoli but with negative controls. Wait, the prompt says: "nctrl ctrl X(anc[0], anc[1], q[2]);" Wait, if `nctrl` is a modifier, maybe it means "negative controls"? Let's trace the ancilla values to see.
        Let's trace the state first.
        *   Initial: $|00000\rangle$
        *   `CNOT(q[0], q[1])`: $|00000\rangle$ (no change, q0 is 0)
        *   `CNOT(q[0], q[2])`: $|00000\rangle$ (no change, q0 is 0)
        *   `X(q[2])`: $|00100\rangle$
        *   Current state: $|q_0=0, q_1=0, q_2=1, a_0=0, a_1=0\rangle$.
        *   `CNOT(q[0], a0)`: no change.
        *   `CNOT(q[1], a0)`: no change.
        *   `

### Reference answer

{'predicted_probs': {'000': 1.0}, 'explanation': 'The output is |000> with probability 1.0'}

## isqTrain/3918

- task_id: `isqTrain/3918`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `447`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```
import std;
// QPE with 3-bit precision for phase 3*pi/4
qbit q[4];

procedure main() {
    // Prepare eigenstate |1>
    X(q[3]);
    // Hadamard on precision qubits
    H(q[0]); H(q[1]); H(q[2]);
    // Controlled-U^(2^k) for each precision qubit
    ctrl Rz(2.0 * 2.0 * 3.14159265358979 * 3.0 / 8.0 * 1.0, q[0], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 3.0 / 8.0 * 2.0, q[1], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 3.0 / 8.0 * 4.0, q[2], q[3]);
    // Inverse QFT on 3 precision qubits
    // Swap q[0] <-> q[2]
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    // iQFT stages
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    ctrl Rz(-3.14159265358979 / 4.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(-3.14159265358979 / 2.0, q[2], q[1]);
    H(q[2]);
    // Measure all
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

Let me analyze this bug carefully.

The task is a 3-bit QPE (Quantum Phase Estimation) for phase 3*pi/4.

The buggy line is:

The fixed version is:

The difference is the extra `2.0 *` in the buggy line. Let me understand why this is wrong.

In QPE, we have a unitary U with eigenstate |ψ⟩ and eigenvalue e^(2πiφ). We want to estimate φ.

Here, the phase is φ = 3π/4, but wait - in the QPE framework, we typically write the phase as φ where U|ψ⟩ = e^(2πiφ)|ψ⟩. So if the phase is 3π/4, then... hmm, let me reconsider.

Actually, looking at the Rz gate: Rz(θ) applies a phase of e^(iθ/2) to |1⟩. But more importantly, in isQ, Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]].

Wait, actually let me reconsider. The Rz gate in many frameworks is:
Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]

But some frameworks define it differently. In isQ, based on the context, Rz(θ) seems to apply a phase of θ to |1⟩ relative to |0⟩, meaning Rz(θ)|1⟩ = e^(iθ)|1⟩ (up to global phase), or more precisely the phase difference between |1⟩ and |0⟩ is θ.

Actually, looking at the code pattern: `Rz(2.0 * pi * 3.0 / 8.0 * k)`. 

For k=1: `2.0 * pi * 3/8 = 3π/4`
For k=2: `2.0 * pi * 3/8 * 2 = 3π/2`
For k=4: `2.0 * pi * 3/8 * 4 = 3π`

This suggests the Rz gate applies a phase of θ (not θ/2) to |1⟩. So Rz(θ)|1⟩ has phase e^(iθ)|1⟩ (or more precisely, the relative phase between |0⟩ and |1⟩ is θ).

Wait, let me reconsider. The isQ Rz gate might be defined as:
Rz(θ) = [[1, 0], [0, e^(iθ)]]

This is a common definition that differs from the standard Qiskit Rz by a factor of 2.

In this case, for QPE with U = Rz(2πφ), where φ = 3/8 (so that the phase is 3/8 of 2π = 3π/4... wait, that's the same thing).

Hmm, let me reconsider. The phase to estimate is 3π/4. In QPE notation, U|1⟩ = e^(iφ)|1⟩ where φ = 3π/4.

But QPE estimates φ/(2π) = 3π/4/(2π) = 3/8.

With 3 bits, we'd expect to measure 011 (binary) = 3 (in standard binary), which represents 3/8. But wait, Let me verify the output.

Expected measurement probabilities: {|0101>: 0.426777, |0111>: 0.073223, |1001>: 0.125, |1011>: 0.125, |1101>: 0.25}

The measurement bitstring has 4 bits. The first 3 bits are the precision qubits, and the last bit is the eigenstate qubit.

Looking at |1101>: this means q[0]=1, q[1]=1, q[2]=0, q[3]=1 (since earlier measured = higher bit).

Wait, but with --probs mode, "earlier measured qubit = higher bit". So the bitstring is ordered with M(q[0]) as the highest bit.

So for |1101>: q[0]=1, q[1]=1, q[2]=0, q[3
