# ISQ training COT RAG corpus: quantum_algorithms shard 24

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/791

- task_id: `isqTrain/791`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `finite_field_arithmetic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4342`

### Prompt

Implement the following in isQ: implements the gf2_multiplication pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement GF(2) polynomial multiplication a(x)·b(x) where a(x)=1+x and b(x)=1, computing product coefficients with reversed measurement order.
2. **Qubits**: 5 qubits total; q[0],q[1] encode a(x), q[2] encodes b(x), q[3],q[4] store product p0,p1. Only q[4] and q[3] are measured.
3. **State evolution**:
   - |00000⟩ → X(q[0]),X(q[1]),X(q[2]) → |11100⟩ (sets a0=1, a1=1, b0=1)
   - Toffoli(q[0],q[2],q[3]): p0 = a0·b0 = 1·1 = 1 → |11110⟩
   - Toffoli(q[1],q[2],q[4]): p1 = a1·b0 = 1·1 = 1 → |11111⟩
4. **Measurement**: M(q[4]) first (higher bit), then M(q[3]) (lower bit). Both yield 1, giving bitstring |11⟩.
5. **Expected result**: {|11⟩: 1.0} since both product coefficients are deterministically 1 in this classical computation.

## isqTrain/4117

- task_id: `isqTrain/4117`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `1856`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);

    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    H(q[2]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement output of the provided isQ circuit.
    *   Circuit: 3 qubits, `q[0]`, `q[1]`, `q[2]`.
    *   Initial state: `|000>`.
    *   Gates: `X(q[0])`, `CNOT(q[0], q[2])`, `CNOT(q[2], q[0])`, `CNOT(q[0], q[2])` (which is a swap (three-CNOT decomposition) between `q[0]` and `q[2]`).
    *   Then `H(q[2])`, `ctrl Rz(-pi/2, q[2], q[1])` (which is CRZ(-pi/2, q2, q1)), `H(q[1])`, `ctrl Rz(-pi/4, q[2], q[0])`, `ctrl Rz(-pi/2, q[1], q[0])`, `H(q[0])`.
    *   Measurements: `M(q[0])`, `M(q[1])`, `M(q[2])`.
    *   Format: "## Circuit Analysis" section, 3-15 lines, Dirac notation, concise step-by-step reasoning, ending with predicted probability distribution.

2.  **Step-by-step Quantum State Evolution:**
    *   *Initial state:* `|000>`
    *   `X(q[0])` -> `|100>`
    *   `CNOT(q[0], q[2])`, `CNOT(q[2], q[0])`, `CNOT(q[0], q[2])` -> swap (three-CNOT decomposition)(q[0], q[2]) -> `|001>`
    *   `H(q[2])` -> `1/sqrt(2) (|0> + |1>) |0> |0>` = `1/sqrt(2) (|000> + |001>)`. Wait, standard notation: `|q[2] q[1] q[0]>`. Let's stick to `|q[2] q[1] q[0]>` or explicit `|q2>_q2 |q1>_q1 |q0>_q0`. Let's use `|q0, q1, q2>`.
    State is `|1, 0, 0>`. After swap(q0, q2) via three CNOTs: `|0, 0, 1>`.
    After `H(q2)`: `1/sqrt(2) (|0, 0, 0> + |0, 0, 1>)`. (Let's use q0 as highest bit).
    *   Let's re-evaluate the inverse Quantum Fourier Transform (IQFT) structure. The gates on `q[1]` and `q[0]` look like an inverse QFT!
    *   Let's trace carefully.
        State: `1/sqrt(2) (|000> + |001>)` (q2 is right-most, so `|q2 q1 q0> = |00> + |01>` over 3 qubits? No, `|q0 q1 q2>`)
        Let's use `|q2, q1, q0>` format for states where `q0` is bit 0.
        Initial: `|0,0,0>`
        X(q0): `|0,0,1>`
        swap(q0, q2) via three CNOTs: `|1,0,0>`
        H(q2): `1/sqrt(2)(|0,0,0> + |1,0,0>)`
        Wait, the gates are:
        `H(q[2])`
        `CRZ(-pi/2, q[2], q[1])` -> wait, `ctrl Rz(theta, q2, q1)` means `q2` is control, `q1` is target!
        Let's look at standard QFT. QFT goes:
        H(0), CR(0,1), CR(0,2)...
        Here we have:
        H(q2)
        CR(q2, q1) -> Rz(-pi/2)
        H(q1)
        CR(q2, q0) -> Rz(-pi/4)
        CR(q1, q0) -> Rz(-pi/2)
        H(q0)
        This is exactly the inverse QFT on `q2, q1, q0` with a specific sign convention. QFT has $e^{2\pi i / 2^k}$, here we have negative angles: `-pi/2`, `-pi/4`, `-pi/2`. Wait, `ctrl

### Reference answer

Uniform distribution across 8 states

## isqTrain/3450

- task_id: `isqTrain/3450`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `phase_manipulation`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `3422`

### Prompt

Write isQ code for the following quantum task: a parity oracle for 3 input bits in isQ.

The parity function returns 1 when an odd number of inputs are 1.
States with odd parity: |001>, |010>, |100>, |111>.

Parity can be computed as XOR of all bits: a XOR b XOR c.
Phase oracle: CNOT chain into ancilla in |-> state.

Apply the oracle to equal superposition to demonstrate phase marking.
Then apply H to all data qubits to reveal the phase pattern.

Declare 3 data qubits and 1 ancilla. Measure data qubits only.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a 3-bit parity oracle as a phase oracle, apply it to an equal superposition, and read out the phase pattern via Hadamard transform.

2. **Qubits**: 3 data qubits (q[0], q[1], q[2]) + 1 ancilla (anc[0]). Only data qubits are measured.

3. **State evolution**:
   - Initialize ancilla to |−⟩: `X(anc[0]); H(anc[0])` → |000⟩|−⟩
   - Equal superposition: `H(q[0]); H(q[1]); H(q[2])` → (1/√8)Σ_x |x⟩|

## isqTrain/1095

- task_id: `isqTrain/1095`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `275`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the bernstein_vazirani pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement Bernstein-Vazirani to find hidden string s=101 using qubits q[0..4] (with q[3,4] idle), plus ancilla.

**Qubits:** 5 data qubits q[0..4] and 1 ancilla; all 5 data qubits measured.

**State evolution:**
1. **Init:** |00000⟩|0⟩ → X(anc) → |00000⟩|1⟩ → H(anc) → |00000⟩|−⟩
2. **Superposition:** H(q[0..2]) → (1/2√2)∑_{x∈{0,1}³}|x⟩|00⟩|−⟩
3. **Oracle:** f computes s·x = x[0]⊕x[2]; phase kickback yields (1/2√2)∑(-1)^{s·x}|x⟩|00⟩|−⟩
4. **Decode:** H(q[0..2]) converts phase encoding → |101⟩|00⟩|−⟩
5. **Final:** |10100⟩|−⟩ deterministically

**Expected probabilities:** {|10100⟩: 1.0} — the hidden string s=101 appears on q[0..2]; q[3..4] remain |0⟩ untouched.

## isqTrain/348

- task_id: `isqTrain/348`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2832`

### Prompt

Create an isQ quantum circuit that implements the arithmetic_circuit pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit has:
- `qbit c[1]` - a control qubit
- `qbit p[2]` - two qubits that will be measured

Main circuit:
1. `H(c[0])` - puts c[0] in |+> state
2. `ctrl INC(c[0], p[0], p[1])` - controlled INC with c[0] as control
3. `nctrl DEC(c[0], p[0], p[1])` - negative controlled DEC (applies when c[0] is |0>)
4. `M(p[0]); M(p[1])` - measure p[0] and p[1]

Let me trace through:

Initial state: |c=0, p0=0, p1=0> = |000>

After H(c[0]): (|000> + |100>) / √2

**Controlled INC (c[0] is control):**
INC = H(p1), CZ(p0, p1), H(p1), X(p0)

This is applied when c[0] = |1>.

For the |100> component:
- p0=0, p1=0
- H(p1): |p0=0, p1=+> 
- CZ(p0, p1): Since p0=0, CZ doesn't apply Z, stays |0+> = |0>(|0>+|1>)/√2
- H(p1): |00>
- X(p0): |10>

So |100> stays |110> after ctrl INC.

For the |000> component:
ctrl INC doesn't apply when c=0, so stays |000>.

State after ctrl INC: (|000> + |110>) / √2

**Negative controlled DEC (c[0] is control, applies when c=0):**
DEC = X(p0), H(p1), CZ(p0, p1), H(p1)

Applied when c[0] = |0>.

For the |000> component (c=0, so this applies):
- p0=0, p1=0
- X(p0): |p0=1, p1=0>
- H(p1): |1+>
- CZ(p0, p1): Since p0=1, CZ applies Z to p1: |1>|-> = |1>(|0>-|1>)/√2
- H(p1): |1>|1>

So |000> becomes |011>.

Wait, but c is still 0, so the full state is |011>.

For the |110> component (c=1, so nctrl doesn't apply):
Stays |110>.

State after nctrl DEC: (|011> + |110>) / √2

Now measuring p[0] and p[1]:
- From |011>: p0=1, p1=1 → |11>
- From |110>: p0=1, p1=0 → |10>

So we get:
- |10>: 50%
- |11>: 50%

This matches the predicted output {|10>: 0.5, |11>: 0.5}.

Let me double-check the INC decomposition:
INC: H(p1), CZ(p0, p1), H(p1), X(p0)

H-CZ-H on target = CNOT (where CZ applies Z to target when control is |1>)
So H-CZ-H on p1 with p0 as control = CNOT(p0, p1)
Then X(p0)

So INC = CNOT(p0, p1) followed by X(p0).

DEC: X(p0), H(p1), CZ(p0, p1), H(p1)
= X(p0) followed by CNOT(p0, p1)

Let me verify with the state evolution again.

For |000> branch through ctrl INC: doesn't apply (c=0), stays |000>
For |100> branch through ctrl INC: applies INC(p0,p1)
  - CNOT(p0,p1) on |00> = |00>
  - X(p0) on |00> = |10>
  Result: |110> (with c=1)

State: (|000> + |110>)/√2

For |000> branch through nctrl DEC: applies (c=0)
  DEC = X(p0) then CNOT(p0,p1)
  - X(p0) on |00> = |10>
  - CNOT(p0,p1) on |10> = |11>
  Result: |011> (with c=0)

For |110> branch through nctrl DEC: doesn't apply (

## isqTrain/3883

- task_id: `isqTrain/3883`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `354`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// Inverse QFT on 3 qubits with input |010>
qbit q[3];

procedure main() {
    // Prepare input
    // BUG: missing gate here

    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    H(q[2]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    // Measure after inverse QFT
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

1.  **Analyze the Buggy Code**:
    *   Initial state: |000>
    *   Goal: Inverse QFT on |010>.
    *   Bug: Missing gate at the start (where `// BUG: missing gate here` is).
    *   Current code: Starts with |000> because no gates are applied to prepare |010>.
    *   Inverse QFT of |000> is just |000> (if standard QFT is applied to |000>, it becomes (1/sqrt(8)) * sum(|x>) where x=0..7. Inverse QFT of |000> is |000>. Wait, the code represents an Inverse QFT. If we apply Inverse QFT to |000>, the output is |000>. the predicted output probabilities show a uniform distribution over all 8 states: { |000>: 0.125, ... }.
    *   Wait, let's trace standard QFT.
    *   Standard QFT on |k> gives $\frac{1}{\sqrt{N}} \sum_{j=0}^{N-1} e^{2\pi i j k / N} |j>$.
    *   If we want a uniform distribution after Inverse QFT, the input to Inverse QFT must be a Fourier basis state. Wait, Inverse QFT maps a Fourier basis state back to the computational basis state.
    *   If the output is uniformly distributed, the input to Inverse QFT must have been... wait.
    *   Let's look at the expected measurement probabilities: uniform over all 8 states.
    *   If the state is $|+\rangle |+\rangle |+\rangle$ or similar, or if it's a specific state.
    *   Actually, let's reverse the Inverse QFT gates to see what state the Inverse QFT maps to the uniform distribution.
    *   Wait, Inverse QFT maps $\frac{1}{\sqrt{N}} \sum_{j} e^{-2\pi i j k / N} |j>$ to $|k\rangle$.
    *   But here the *output* of the Inverse QFT is uniformly distributed! This means the *input* to the Inverse QFT must be $\frac{1}{\sqrt{8}} \sum_{x=0}^7 |x\rangle$.
    *   Does QFT on $|0\rangle^{\otimes 3}$ give a uniform superposition? Yes. So Inverse QFT on $|0\rangle^{\otimes 3}$ gives $|0\rangle^{\otimes 3}$.
    *   Let's trace Inverse QFT on $|010\rangle$.
    *   Inverse QFT on $|2\rangle$ (where $|010\rangle$ is 2 in binary): $|2\rangle = \frac{1}{\sqrt{8}} \sum_{j=0}^7 e^{2\pi i (2)j/8} |j\rangle$.
    *   Wait, standard QFT: $|k\rangle \to \frac{1}{\sqrt{N}} \sum_{j} e^{2\pi i j k / N} |j\rangle$.
    *   So Inverse QFT: $\frac{1}{\sqrt{N}} \sum_{j} e^{-2\pi i j k / N} |j\rangle \to |k\rangle$.
    *   Let's see the code: it applies Inverse QFT.
    *   Wait, if I have standard QFT on $|0\rangle^{\otimes 3}$, the output is $\frac{1}{\sqrt{8}} \sum |j\rangle$.
    *   If the task is "3-qubit inverse QFT with input |010>", and the output is a uniform distribution, let's check the QFT definition used in the code.
    *   Wait, the task literally says "inverse QFT on 3 qubits with input |010>".
    *   Let's reverse the output. Output is $|+\rangle |+\rangle |+\rangle$ (uniform).
    *   Let's see what happens if we apply the code's QFT to $|010\rangle$.
    *   The code has SWAPs at the beginning: `CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2]);` which swaps q[0] and q[2].
    *   Then H(q[2]), etc.
    *   Let's do standard QFT on |q[2], q[1], q[0]>.
    *   Wait, the swap is at the *begin

## isqTrain/3630

- task_id: `isqTrain/3630`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2691`

### Prompt

Implement a quantum circuit in isQ: the 3-qubit Quantum Fourier Transform (QFT) applied to the input state |101>. The circuit should:
1. Prepare the input state by applying X gates where needed
2. Apply the QFT using Hadamard and controlled-Rz gates
3. Include the final bit-reversal swaps
4. Measure all 3 qubits

### Chain-of-thought reasoning

Let me analyze this 3-qubit QFT circuit applied to |101>.

The goal is to implement the 3-qubit QFT on the input state |101>.

The 3-qubit QFT transforms a computational basis state |k⟩ into a superposition that encodes k in the phases.

For a 3-qubit system, |101⟩ = |5⟩ in decimal.

The QFT of |k⟩ for n qubits is: (1/√N) Σ_j e^(2πijk/N) |j⟩ where N = 2^n = 8.

So QFT|5⟩ = (1/√8) Σ_{j=0}^{7} e^(2πi·5·j/8) |j⟩

Let me compute the amplitudes:
- j=0: e^(0) = 1
- j=1: e^(10πi/8) = e^(5πi/4)
- j=2: e^(20πi/8) = e^(5πi/2) = e^(πi/2) = i
- j=3: e^(30πi/8) = e^(15πi/4)
- j=4: e^(40πi/8) = e^(5πi) = -1
- j=5: e^(50πi/8) = e^(25πi/4)
- j=6: e^(60πi/8) = e^(15πi/2) = e^(3πi/2) = -i
- j=7: e^(70πi/8) = e^(35πi/4)

The magnitudes are all 1, so all probabilities are equal: 1/8 = 0.125.

Now let me trace through the circuit:

Initial state: |000⟩

After X(q[0]) and X(q[2]): |101⟩

QFT stage for qubit 0:
- H(q[0]): creates superposition on qubit 0
  |101⟩ → (1/√2)(|001⟩ + |101⟩) — wait, H on q[0] which is the first qubit (least significant in some conventions)

Actually, let me be careful about the qubit ordering. In isQ, q[0] is typically the first qubit. Let me trace more carefully.

State |101⟩ means q[2]=1, q[1]=0, q[0]=1.

After H(q[0]):
(1/√2)(|100⟩ + |101⟩)

After ctrl Rz(π/2, q[1], q[0]):
q[1] is 0 in both terms, so no phase is applied. State unchanged.

After ctrl Rz(π/4, q[2], q[0]):
q[2] is 1 when q[0] is 0, so |100⟩ picks up e^(iπ/4). State becomes:
(1/√2)(e^(iπ/4)|100⟩ + |101⟩)

After H(q[1]):
|100⟩ = |10⟩⊗|0⟩ → (1/√2)|10⟩(|0⟩+|1⟩) but I need to be more careful.

Actually, let me reconsider. The state is in the form |q[2] q[1] q[0]⟩.

Current state: (1/√2)(e^(iπ/4)|100⟩ + |101⟩)

H(q[1]) acts on the middle qubit:
|100⟩ = |1⟩⊗|0⟩⊗|0⟩ → |1⟩⊗(1/√2)(|0⟩+|1⟩)⊗|0⟩ = (1/√2)(|100⟩ + |110⟩)
|101⟩ = |1⟩⊗|0⟩⊗|1⟩ → |1⟩⊗(1/√2)(|0⟩+|1⟩)⊗|1⟩ = (1/√2)(|101⟩ + |111⟩)

So state becomes:
(1/√2)(e^(iπ/4) · (1/√2)(|100⟩ + |110⟩) + (1/√2)(|101⟩ + |111⟩))
= (1/2)(e^(iπ/4)|100⟩ + e^(iπ/4)|110⟩ + |101⟩ + |111⟩)

After ctrl Rz(π/2, q[2], q[1]):
When q[2]=1 and q[1]=1, phase e^(iπ/2) = i is applied to |110⟩ and |111⟩.

Wait, actually Rz(θ) on |1⟩ gives e^(iθ/2)|

## isqTrain/1244

- task_id: `isqTrain/1244`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `1407`

### Prompt

帮我写一个isQ程序：implements the qft_subcircuit pattern but with a different initial state preparation (flip q[[0, 2]] -> q[1]).

### Chain-of-thought reasoning

## Reasoning
**Goal**: Implement 3-qubit QFT on initial state |010⟩ (X gate on q[1] instead of q[0] and q[2]).
**Qubits**: 3 qubits (q[0], q[1], q[2]), all measured at the end.
**State evolution**: |000⟩ → X(q[1]) → |010⟩ → QFT → (1/√8)Σₖ e^(πik/2)|k⟩ for k=0..7
- H(q[2]) on |010⟩: q[2] is |0⟩ → |0⟩ becomes (|0⟩+|1⟩)/√2, giving (|010⟩+|011⟩)/√2
- ctrl R(2,q[1],q[2]): q[1]=|1⟩ applies phase e^(iπ/2)=i to |011⟩ → (|010⟩+i|011⟩)/√2
- ctrl R(3,q[0],q[2]): q[0]=|0⟩, no phase applied
- H(q[1]) on the state: transforms q[1], mixing |010⟩ and |011⟩ components with phases
- ctrl R(2,q[0],q[1]): q[0]=|0⟩, no phase
- H(q[0]) on q[0]=|0⟩ → creates superposition
- swap (three-CNOT decomposition)(q[0],q[2]) reverses qubit order
**Expected probabilities**: All 8 basis states have probability |1/√8|² = 0.125 (uniform), since QFT of any computational basis state produces an equal-magnitude superposition with different phases.

## isqExpand/algo/88

- task_id: `isqExpand/algo/88`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `amplitude_estimation`, `grover`, `phase_manipulation`, `interference`
- source: `isq_expansion_qa`
- dataset_index: `605`

### Prompt

量子振幅估计（Quantum Amplitude Estimation, QAE）的基本原理是什么？它是如何利用量子相位估计来获取振幅信息的？请说明其与经典Monte Carlo采样的精度对比。

### Chain-of-thought reasoning

## 推理
振幅估计是QPE+振幅放大的推广。核心链条：
1. A产生目标振幅 -> 2. Grover-like算子Q编码振幅为相位 -> 3. QPE提取相位 -> 4. 从相位恢复振幅

与经典对比是关键：O(1/eps) vs O(1/eps^2)。
还要提到与量子计数的关系和近期无QFT变体。

### Reference answer

## 量子振幅估计 (QAE)

### 问题设定
给定一个量子算子A，使得 A|0> = sin(theta)|good> + cos(theta)|bad>，目标是估计振幅a = sin(theta)（或概率 a^2 = sin^2(theta)）。

### 核心原理
定义Grover-like算子 Q = A * S_0 * A^(-1) * S_good，其中：
- S_good 对|good>翻转相位
- S_0 对|0>翻转相位

Q的特征值为 exp(+/-2i*theta)，其中 a = sin(theta)。

### 算法步骤
1. 准备t个辅助量子位和工作寄存器
2. 对工作寄存器施加A得到 sin(theta)|good> + cos(theta)|bad>
3. 使用受控Q^(2^k)进行相位估计
4. 对辅助寄存器做逆QFT
5. 测量得到theta的估计值
6. 计算 a_est = sin(theta_est)

### 精度分析
- **经典Monte Carlo**：要达到精度epsilon，需要O(1/epsilon^2)次采样
- **量子振幅估计**：只需O(1/epsilon)次量子操作

这是从O(1/epsilon^2)到O(1/epsilon)的**二次加速**。

### 与量子计数的关系
量子计数是QAE的特殊情况：
- A = H^n（产生均匀叠加）
- a = sin(theta) = sqrt(M/N)
- 估计a^2就等价于估计M/N

### 应用
- Monte Carlo积分的量子加速
- 期权定价（量子金融）
- 统计推断

### 近期变体
无需QFT的振幅估计算法（如Iterative QAE, Maximum Likelihood QAE）降低了电路深度需求，更适合近期量子设备。

## isqTrain/3417

- task_id: `isqTrain/3417`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2500`

### Prompt

Help me write isQ code that the 3-qubit bit-flip code in isQ with error injection and majority-vote correction.

Steps:
1. Encode |0> into |000> using CNOT fan-out
2. Inject a bit-flip error on q[1] (simulate X error)
3. Compute syndrome: use CNOT from data qubits to 2 ancilla qubits
   - anc[0] = q[0] XOR q[1], anc[1] = q[1] XOR q[2]
4. Correct based on syndrome:
   - syndrome 11 -> error on q[1], apply X(q[1])
   Use Toffoli (ctrl ctrl X) to conditionally correct
5. Measure the 3 data qubits (not ancillas)

Expected: |000> with probability 1.0 after correction.

Declare 3 data qubits q[3] and 2 ancilla qubits anc[2], but only measure q[0..2].

### Chain-of-thought reasoning

## Reasoning
**Goal:** Demonstrate the 3-qubit bit-flip code encoding, error injection, syndrome extraction, and majority-vote correction to recover |000⟩.

**Qubits:** 5 total (q[0..2] data, anc[0..1] syndrome); only q[0..2] measured.

**State evolution:**
1. **Init:** |000⟩|00⟩ — all qubits in |0⟩.
2. **Encode:** CNOT(q[0],q[1]), CNOT(q[0],q[2]) — since q[0]=|0⟩, no change: |000⟩|00⟩.
3. **Error:** X(q[1]) flips qubit 1: |010⟩|00⟩.
4. **Syndrome:** CNOT(q[0],anc[0])→|010⟩|00⟩; CNOT(q[1],anc[0])→|010⟩|10⟩; CNOT(q[1],anc[1])→|010⟩|11⟩; CNOT(q[2],anc[1])→|010⟩|11⟩. Syndrome anc=|11⟩ indicates q[1] disagrees with both neighbors.
5. **Correct:** Toffoli(anc[0],anc[1],q[1]) flips q[1] back: |000⟩|11⟩.

**Result:** Data qubits are |000⟩ with probability 1.0 — error successfully corrected.
