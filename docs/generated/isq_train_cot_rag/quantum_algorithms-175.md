# ISQ training COT RAG corpus: quantum_algorithms shard 175

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3020

- task_id: `isqTrain/3020`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5669`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```isq
import std;
qbit q[3];
// GHZ-like state with X on q[2]
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    // CNOT(q[1], q[2]); // BUG: missing CNOT
    X(q[2]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The Bug:** The CNOT gate entangling `q[1]` and `q[2]` is commented out, preventing the creation of a 3-qubit GHZ state and leaving `q[2]` completely unentangled.
2. **The Fix:** Uncomment `CNOT(q[1], q[2]);` so that `q[2]` is entangled with the first two qubits before the X gate is applied.
3. **State Evolution:** Initial state |000> -> H(q[0]) -> (|000> + |100>)/√2 -> CNOT(q[0],q[1]) -> (|000> + |110>)/√2 -> CNOT(q[1],q[2]) -> (|000> + |111>)/√2 -> X(q[2]) -> (|001> + |110>)/√2.

## isqTrain/4602

- task_id: `isqTrain/4602`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `ancilla_usage`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3541`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;

qbit q[4];

procedure main() {
    
    X(q[3]);
    H(q[3]);
    
    H(q[3]);  // target different qubit
    H(q[1]);
    H(q[2]);
    
    CNOT(q[0], q[3]);
    CNOT(q[2], q[3]);
    
    H(q[0]);
    H(q[1]);
    H(q[2]);
    
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

Step-by-step analysis of this isQ program:

1. Initial state: |0000>
2. X(q[3]): q[3] becomes |1> -> |0001>
3. H(q[3]): q[3] -> (|0>-|1>)/√2 -> |0000>/√2 - |0001>/√2
4. H(q[3]): H on q[3] again -> q[3] back to |1> -> -|0001>
5. H(q[1]): q[1] -> |+> -> -|0101>/√2 - |0111>/√2
6. H(q[2]): q[2] -> |+> -> -(|0101>+|0111>+|1101>+|1111>)/2
7. CNOT(q[0], q[3]): control q[0], target q[3]. When q[0]=|1>, flip q[3].
   -> -(|0101>+|0110>+|1100>+|1111>)/2
8. CNOT(q[2], q[3]): control q[2], target q[3]. When q[2]=|1>, flip q[3].
   -> -(|0101>+|0111>+|1101>+|1111>)/2
   Wait, let me redo:
   Before CNOT(q[2], q[3]): -(|0101>+|0110>+|1100>+|1111>)/2
   CNOT(q[2], q[3]): when q[2]=1, flip q[3]:
   |0101> (q[2]=0) -> |0101>
   |0110> (q[2]=1, q[3]=0) -> |0111>
   |1100> (q[2]=0) -> |1100>
   |1111> (q[2]=1, q[3]=1) -> |1110>
   So after: -(|0101>+|0111>+|1100>+|1110>)/2

Let me use notation |q[3]q[2]q[1]q[0]> or |q[0]q[1]q[2]q[3]>.

Actually, let me be careful with bit ordering. In the standard convention, |q[0]q[1]q[2]q[3]> where q[0] is the most significant bit.

Let me redo with |q0,q1,q2,q3>:

1. Initial: |0000>
2. X(q[3]): |0001>
3. H(q[3]): (|0000>-|0001>)/√2
4. H(q[3]) again: -|0001>
   Wait, H|0> = |+>, H|1> = |->
   So H applied to q[3] which is in state (|0>-|1>)/√2:
   H(|0>-|1>)/√2 = (|+>-|->)/√2 = ((|0>+|1>)-(|0>-|1>))/(√2·√2) = 2|1>/2 = |1>
   So we get back to -|0001>

5. H(q[1]): q[1] is |0> -> |+>
   -|0001> -> -(|0101>+|0001>)/√2... 
   Wait, q[1] is the second bit from the left in |q0,q1,q2,q3>.
   H on q[1]: |0>_1 -> (|0>+|1>)_1/√2
   -|0001> -> -(|0001>+|0101>)/√2

   Hmm wait, if q[1] is the second position, then applying H to q[1] on |0001>:
   The q[1] position is |0>, so it becomes (|0>+|1>)/√2 at that position.
   Result: -(|0001>+|0101>)/√2

6. H(q[2]): q[2] is the third position, currently |0> -> (|0>+|1>)/√2
   -(|0001>+|0101>)/√2 -> -(|0001>+|0011>+|0101>+|0111>)/2

7. CNOT(q[0], q[3]): control=q[0], target=q[3]
   |0001>: q[0]=0, no flip -> |0001>
   |0011>: q[0]=0, no flip -> |001

### Reference answer

{'predicted_probs': {'0000': 0.25, '0001': 0.25, '0100': 0.25, '0101': 0.25}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0000>) = 0.2500, P(|0001>) = 0.2500, P(|0100>) = 0.2500, P(|0101>) = 0.2500.'}

## isqTrain/2784

- task_id: `isqTrain/2784`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3286`

### Prompt

Fix the bug in this quantum program:

```isq
import std;

qbit q[2];

procedure main(){
    H(q[0]);
    // CNOT(q[0],q[1]); // BUG: missing CNOT
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The CNOT gate on `CNOT(q[0], q[1])` is commented out (`//`), so the two qubits are never entangled. Without it, q[1] remains |0⟩ while q[0] is in superposition, producing states |00⟩ and |10⟩ instead of the desired Bell state.

2. **Fix**: Uncomment the CNOT line to restore entanglement between q[0] and q[1].

3. **State evolution (corrected)**:
   - Initial: |00⟩
   - H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2
   - CNOT(q[0], q[1]): (|00⟩ + |11⟩)/√2 — Bell state |β₀₀⟩
   - Measurement: {|00⟩: 0.5, |11⟩: 0.5} ✓

## isqTrain/4280

- task_id: `isqTrain/4280`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `438`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;

qbit q[2];

procedure main() {
    // Superposition
    H(q[0]);
    H(q[1]);
    // Function oracle: phase flips
    Z(q[0]);
    Z(q[1]);
    // Fourier transform back
    H(q[0]);
    H(q[1]);
    // Measure
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 2 qubits in |00> and applies H gates to both, creating the superposition |++>.
2. Applying Z gates to both qubits flips the phase of the |1> components, changing the state to |-->.
3. A second application of H gates to both qubits maps the state back to the computational basis, resulting in |11>.
4. The sequence H, Z, H on q[0] is mathematically equivalent to an X gate (HZH = X), which flips q[0] from |1> to |0>.
5. The final quantum state before measurement is |01>.

Predicted probability distribution: {|01>: 1.0}

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 1.0000.'}

## isqTrain/3658

- task_id: `isqTrain/3658`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `1269`

### Prompt

请用isQ语言编写一个量子电路：3-bit quantum phase estimation for phase angle 1*pi/4 (in multiples of 2π/8). Use 3 precision qubits, controlled-Rz rotations, and a 3-qubit inverse QFT. Measure all 4 qubits (3 precision + 1 eigenstate).

### Chain-of-thought reasoning

Let me analyze this quantum phase estimation (QPE) circuit step by step.

The goal is to implement 3-bit QPE for a phase angle of 1π/4 (i.e., θ = 1/8 in multiples of 2π).

Wait, let me re-read: "phase angle 1*pi/4 (in multiples of 2π/8)". So the phase is 1 * π/4 = π/4.

Actually, Analyzing the code more carefully:
- `ctrl Rz(2.0 * pi * 1.0 / 8.0 * 1.0, q[0], q[3])` - this is Rz(2π * 1/8) = Rz(π/4)
- `ctrl Rz(2.0 * pi * 1.0 / 8.0 * 2.0, q[1], q[3])` - this is Rz(2π * 2/8) = Rz(π/2)
- `ctrl Rz(2.0 * pi * 1.0 / 8.0 * 4.0, q[2], q[3])` - this is Rz(2π * 4/8) = Rz(π)

So the phase is φ = 1/8 (in units of 2π), meaning the eigenvalue is e^(2πi * 1/8) = e^(iπ/4).

Let me trace through the circuit:

**Initial state**: |0000⟩

**After X(q[3])**: |0001⟩

**After H on q[0], q[1], q[2]**: (1/√8)(|0⟩+|1⟩)(|0⟩+|1⟩)(|0⟩+|1⟩)|1⟩ = (1/√8)∑_{k=0}^{7} |k⟩|1⟩

**Controlled-Rz operations**:
The controlled-Rz(θ) gate acts as: if control is |1⟩, apply Rz(θ) to target.

Rz(θ)|0⟩ = e^(-iθ/2)|0⟩
Rz(θ)|1⟩ = e^(iθ/2)|1⟩

So controlled-Rz(θ) on control q[k], target q[3]:
- When q[k] = |1⟩, the eigenstate |1⟩ picks up phase e^(iθ/2)

Wait, but QPE typically uses controlled-U^k where U has eigenvalue e^(2πiφ). Let me think about this more carefully.

In standard QPE, if U|u⟩ = e^(2πiφ)|u⟩, then:
- The k-th precision qubit (counting from 0) applies U^(2^k)

The phase accumulated for the k-th qubit is 2πφ * 2^k.

Looking at the code:
- q[0] applies Rz(2π * 1/8 * 1) → phase factor e^(i * 2π/8 * 1/2) = e^(iπ/8) on |1⟩ state
   
Wait, Rz(θ) applies:
Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]

So Rz(θ)|1⟩ = e^(iθ/2)|1⟩

For the k-th qubit, the controlled operation is Rz(2π * 1/8 * 2^k).

When the control qubit is |1⟩, the target |1⟩ picks up e^(i * 2π * 1/8 * 2^k / 2) = e^(iπ * 2^k / 8)

Hmm, but this doesn't quite match standard QPE which should give a clean binary fraction output.

Let me reconsider. The issue is that Rz gates also apply a global phase e^(-iθ/2) which matters when controlled.

Actually, controlled-Rz(θ) in isQ is:
- When control = |0⟩: Identity
- When control = |1⟩: Rz(θ)

But the effect on the state is more subtle. Let me think about what controlled-Rz does:

For state |c⟩|t⟩ where c is control and t is target:
If c = 0: |0⟩|t⟩ unchanged
If c = 1: |1⟩(Rz(θ)|t⟩) = |1⟩(e^(-iθ/2)|0⟩ if t=0, e^(iθ/2)|1⟩ if t=1)

Since our target is always |1⟩, the effect is:
|1

## isqTrain/4825

- task_id: `isqTrain/4825`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_import_qft`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `491`

### Prompt

Write an isQ program that applies QFT to a subset of qubits. Import std and qft. Declare 4 global qubits. Apply X(q[0]) to set the first qubit. Apply qft on just the first 2 qubits by using qft(q[0:2]). Leave q[2] and q[3] unchanged. Measure all 4 qubits.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Write a reasoning section for an isQ program applying QFT to a subset of qubits.
    *   Inputs: 4 global qubits, X(q[0]), qft(q[0:2]), M(q[0..3]).
    *   Expected Probabilities: |0000>: 0.25, |0100>: 0.25, |1000>: 0.25, |1100>: 0.25.
    *   Constraints: Output ONLY the reasoning section starting with "## Reasoning". Use Dirac notation. Be concise (3-15 lines).

2.  **Break down the circuit:**
    *   Initial state: |0000>
    *   After X(q[0]): |1000>
    *   QFT on first 2 qubits (q[0] and q[1]): The state is |10> on these two qubits. The other two qubits (q[2], q[3]) are in |00>. Let's trace the 2-qubit QFT on |10>.
    *   Standard 2-qubit QFT maps basis states $|x_1 x_0\rangle$ to a superposition.
    *   Specifically, $QFT|x_1 x_0\rangle = \frac{1}{2} \sum_{y=0}^3 e^{2\pi i x y / 4} |y\rangle$, where $x = 2x_1 + x_0$.
    *   Here $x_1=1, x_0=0 \Rightarrow x=2$.
    *   $QFT|2\rangle = \frac{1}{2} \sum_{y=0}^3 e^{2\pi i (2) y / 4} |y\rangle = \frac{1}{2} \sum_{y=0}^3 e^{i \pi y} |y\rangle = \frac{1}{2}(|0\rangle - |1\rangle + |2\rangle - |3\rangle)$.
    *   In binary for 2 qubits: $|0\rangle = |00\rangle$, $|1\rangle = |01\rangle$, $|2\rangle = |10\rangle$, $|3\rangle = |11\rangle$.
    *   So the first two qubits become $\frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |11\rangle)$.
    *   Factoring out: $\frac{1}{2}(|0\rangle + |1\rangle) \otimes (|0\rangle - |1\rangle)$. Wait, is this right?
    *   Let's check: $(|0\rangle+|1\rangle) \otimes (|0\rangle-|1\rangle) = |00\rangle - |01\rangle + |10\rangle - |11\rangle$. Yes, it is just H(q[1]) on |0> and H(q[0]) on |1>. (Actually standard QFT swaps at the end, but `qft` usually handles standard QFT mapping $|j\rangle \to \frac{1}{\sqrt{N}} \sum e^{2\pi i j k/N} |k\rangle$. Wait, QFT usually outputs in bit-reversed order if no swaps are added, but standard definition includes the swaps. Let's assume standard QFT with swaps).
    *   Let's use the matrix: $|10\rangle$ means q[0] is 0, q[1] is 1. Wait, standard notation: $|q_1 q_0\rangle = |10\rangle$ means q[1]=1, q[0]=0. So $x=2$.
    *   $QFT |10\rangle$ (with swaps, so q[1] is MSB of output) gives $\frac{1}{2}(|00\rangle - |01\rangle + |10\rangle - |11\rangle)$.
    *   Total state: $\frac{1}{2}(|0000\rangle - |0100\rangle + |1000\rangle - |1100\rangle)$.
    *   Measurement probabilities: magnitude squared of each amplitude is $(1/2)^2 = 1/4 = 0.25$. Probabilities are equal for |0000>, |0100>, |1000>, |1100>.

3.  **Draft the reasoning section:**
    *   **Goal:** Apply a 2-qubit Quantum Fourier Transform (QFT) to a specific subset of qubits within a 4-qubit register and measure the results.

## isqTrain/972

- task_id: `isqTrain/972`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3153`

### Prompt

用isQ实现implements the lie_trotter pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this Lie-Trotter circuit step by step.

Goal: Implement a first-order Trotter decomposition of $e^{-itH}$ where $H = ZZ + XX$ with $t = \pi/8$, starting from $|10\rangle$, with explicit H-H identity pairs before measurement.

Qubits: 2 qubits q[0] and q[1], both measured.

Let me trace through the state evolution:

1. Initial: $|00\rangle$
2. After X(q[0]): $|10\rangle$

Now the Trotter decomposition: $e^{-it(XX+ZZ)} \approx e^{-it \cdot ZZ} \cdot e^{-it \cdot XX}$

**Step 1: $e^{-it \cdot ZZ}$**
3. CNOT(q[0], q[1]): $|10\rangle \to |11\rangle$ (control is 1, flip target)
4. Rz(2t = π/4, q[1]): $|11\rangle \to e^{-i\pi/8}|11\rangle$ (phase on |1⟩ of q[1])
5. CNOT(q[0], q[1]): $|11\rangle \to |10\rangle$

So after ZZ evolution: $e^{-i\pi/8}|10\rangle$

**Step 2: $e^{-it \cdot XX}$**
6. H(q[0]); H(q[1]): 
   - $|10\rangle = |1\rangle|0\rangle$
   - H on q[0]: $|1\rangle \to \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = -|-\rangle$... wait, $H|1\rangle = |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
   - H on q[1]: $|0\rangle \to |+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
   - So state becomes $|-\rangle|+\rangle = \frac{1}{2}(|0\rangle - |1\rangle)(|0\rangle + |1\rangle) = \frac{1}{2}(|00\rangle + |01\rangle - |10\rangle - |11\rangle)$

7. CNOT(q[0], q[1]): 
   - $|00\rangle \to |00\rangle$
   - $|01\rangle \to |01\rangle$
   - $|10\rangle \to |11\rangle$
   - $|11\rangle \to |10\rangle$
   - So: $\frac{1}{2}(|00\rangle + |01\rangle - |11\rangle - |10\rangle)$

8. Rz(2t = π/4, q[1]): applies $e^{-i\pi/8}$ to |1⟩ component of q[1]
   - $|00\rangle \to |00\rangle$
   - $|01\rangle \to e^{-i\pi/8}|01\rangle$
   - $|10\rangle \to e^{-i\pi/8}|10\rangle$
   - $|11\rangle \to e^{-i3\pi/8}|11\rangle$... wait, Rz(θ)|0⟩ = |0⟩, Rz(θ)|1⟩ = e^{-iθ/2}|1⟩... 

Hmm, let me be more careful. The Rz gate is defined as:
$$Rz(\theta) = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\theta} \end{pmatrix}$$

Wait, different conventions exist. Let me think about what convention isQ uses.

Looking at the circuit description: Rz(2t) applies the ZZ phase. For ZZ evolution $e^{-it \cdot ZZ}$, the decomposition uses CNOT-Rz(2t)-CNOT. 

For $ZZ = Z \otimes Z$, the eigenvalues are +1 for |00⟩, |11⟩ and -1 for |01⟩, |10⟩.

$e^{-it \cdot ZZ}|ab\rangle = e^{-it \cdot (-1)^{a \oplus b}}|ab\rangle$... no wait:
- $ZZ|00\rangle = |00\rangle$ (eigenvalue +1)
- $ZZ|01\rangle = -|01\rangle$ (eigenvalue -1)
- $ZZ|10\rangle = -|10\rangle$ (eigenvalue -1)
- $ZZ|11\rangle = |11\rangle$ (eigenvalue

## isqTrain/4611

- task_id: `isqTrain/4611`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2428`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[1];

procedure main() {
    
    
    
    

    
    Rx(1.04719755119660, q[0]);
    
    Rz(1.04719755119660, q[0]);
    
    Rx(1.04719755119660, q[0]);

    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants an analysis of an isQ quantum program to determine the probability distribution of the measurement outcomes. The response must follow specific rules: use Dirac notation, be 3-15 lines long, start with "## Circuit Analysis", no isq code blocks, end with the predicted probability distribution.

2.  **Analyze the Circuit**:
    *   Initial state: $|0\rangle$
    *   Gate 1: `Rx(1.04719755119660, q[0])`. Note: $1.04719755119660 \approx \pi/3$. So this is $R_x(\pi/3)$.
        $R_x(\pi/3) = \cos(\pi/6)I - i\sin(\pi/6)X = \frac{\sqrt{3}}{2}|0\rangle - i\frac{1}{2}|1\rangle$.
    *   Gate 2: `Rz(1.04719755119660, q[0])`. This is $R_z(\pi/3)$.
        $R_z(\pi/3) | \psi \rangle = e^{-i\pi/6} \frac{\sqrt{3}}{2}|0\rangle - i e^{i\pi/6} \frac{1}{2}|1\rangle$.
        Wait, I need to be precise. $R_z(\theta) = e^{-i\theta/2}|0\rangle\langle 0| + e^{i\theta/2}|1\rangle\langle 1|$.
    *   Gate 3: `Rx(1.04719755119660, q[0])`. This is $R_x(\pi/3)$.
        Actually, it's easier to multiply the matrices or simplify mathematically. Let's use python or do the math in my head.
        Let's see if the combination forms a known gate or specific probabilities.
        State after $R_x(\pi/3)$: $|\psi_1\rangle = \cos(\pi/6)|0\rangle - i\sin(\pi/6)|1\rangle = \frac{\sqrt{3}}{2}|0\rangle - i\frac{1}{2}|1\rangle$.
        State after $R_z(\pi/3)$: $|\psi_2\rangle = e^{-i\pi/6}\frac{\sqrt{3}}{2}|0\rangle - i e^{i\pi/6}\frac{1}{2}|1\rangle$.
        Now apply $R_x(\pi/3) = \begin{pmatrix} \cos(\pi/6) & -i\sin(\pi/6) \\ -i\sin(\pi/6) & \cos(\pi/6) \end{pmatrix} = \begin{pmatrix} \sqrt{3}/2 & -i/2 \\ -i/2 & \sqrt{3}/2 \end{pmatrix}$.
        $|\psi_3\rangle = R_x(\pi/3) |\psi_2\rangle = \begin{pmatrix} \sqrt{3}/2 & -i/2 \\ -i/2 & \sqrt{3}/2 \end{pmatrix} \begin{pmatrix} e^{-i\pi/6}\sqrt{3}/2 \\ -i e^{i\pi/6}/2 \end{pmatrix}$.
        $\alpha = \frac{3}{4} e^{-i\pi/6} - \frac{1}{4} e^{i\pi/6}$.
        $\beta = -i \frac{\sqrt{3}}{4} e^{-i\pi/6} - i \frac{\sqrt{3}}{4} e^{i\pi/6} = -i \frac{\sqrt{3}}{4} (e^{-i\pi/6} + e^{i\pi/6}) = -i \frac{\sqrt{3}}{4} (2 \cos(\pi/6)) = -i \frac{\sqrt{3}}{4} (\sqrt{3}) = -i \frac{3}{4}$.
        Let's re-evaluate $\alpha$: $\frac{3}{4} (\frac{\sqrt{3}}{2} - i\frac{1}{2}) - \frac{1}{4} (\frac{\sqrt{3}}{2} + i\frac{1}{2}) = \frac{3\sqrt{3}}{8} - i\frac{3}{8} - \frac{\sqrt{3}}{8} - i\frac{1}{8} = \frac

### Reference answer

{'predicted_probs': {'0': 0.5625, '1': 0.4375}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.5625, P(|1>) = 0.4375.'}

## isqTrain/4084

- task_id: `isqTrain/4084`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `1794`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[3];

unit grover_oracle(qbit q[3]) {
    ctrl CZ(q[0], q[1], q[2]);
} deriving gate

unit grover_diffusion(qbit q[3]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
} deriving gate

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    grover_oracle(q);
    grover_diffusion(q);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement output of a 3-qubit isQ quantum program.
    *   Circuit structure: Grover's algorithm with one iteration.
        *   Initialization: 3 qubits.
        *   Superposition: H(q[0]), H(q[1]), H(q[2]) -> $|+\rangle^{\otimes 3}$.
        *   Oracle: `ctrl CZ(q[0], q[1], q[2])` (Toffoli-like Z, actually double-controlled-Z (ctrl @[c1, c2] Z(target))).
        *   Diffusion: H, X, double-controlled-Z (ctrl @[c1, c2] Z(target)), X, H.
        *   Measurement: M(q[0]), M(q[1]), M(q[2]).
    *   Target state: double-controlled-Z (ctrl @[c1, c2] Z(target)) applies Z to |111>. Grover diffusion reflects around the mean. The oracle marks |111>.
    *   Format: "## Circuit Analysis", step-by-step, concise (3-15 lines), end with probability distribution.

2.  **Analyze the Circuit:**
    *   Initial state: $|000\rangle$.
    *   H gates: $|+++\rangle = \frac{1}{2\sqrt{2}} \sum_{x=0}^{7} |x\rangle$.
    *   Oracle: `ctrl CZ(q[0], q[1], q[2])` is a controlled-controlled-Z gate. It adds a phase of -1 to the $|111\rangle$ state.
        *   State becomes $\frac{1}{2\sqrt{2}} (|000\rangle + |001\rangle + |010\rangle + |011\rangle + |100\rangle + |101\rangle + |110\rangle - |111\rangle)$.
    *   Diffusion operator:
        *   $H^{\otimes 3}$: Maps marked state to $|000\rangle$ and uniform superposition to $|111\rangle$... wait.
        *   Standard diffusion is $H^{\otimes n} (2|0\rangle\langle0| - I) H^{\otimes n}$.
        *   Let's check the implementation: H X double-controlled-Z (ctrl @[c1, c2] Z(target)) X H.
        *   double-controlled-Z (ctrl @[c1, c2] Z(target)) on $|111\rangle$ applies -1.
        *   X H transforms basis. $H^{\otimes 3} X^{\otimes 3} |111\rangle = H^{\otimes 3} |000\rangle = |+++\rangle$.
        *   Wait, the oracle marked $|111\rangle$. The oracle flips the sign of $|111\rangle$.
        *   In Grover's algorithm, one iteration with 1 marked state out of $N=8$ should amplify the amplitude of the marked state. Wait!
        *   Amplitude of marked state initially is $1/\sqrt{8}$. After oracle, it is $-1/\sqrt{8}$. The mean is $(7 - 1)/8 = 6/8 = 3/4$.
        *   Reflection around mean: new amplitude = $2 \times \text{mean} - \text{old}$.
        *   For unmarked: $2(3/4) - (1/\sqrt{8}) \dots$ wait, amplitudes are $\pm 1/\sqrt{8}$. Mean = $(7(1/\sqrt{8}) - 1/\sqrt{8}) / 8 = 6/(8\sqrt{8}) = 3/(4\sqrt{8})$.
        *   Unmarked amp: $2(3/(4\sqrt{8})) - 1/\sqrt{8} = 6/(4\sqrt{8}) - 4/(4\sqrt{8}) = 2/(4\sqrt{8}) = 1/(2\sqrt{8})$.
        *   Marked amp: $2(3/(4\sqrt{8})) - (-1/\sqrt{8}) = 6/(4\sqrt{8}) + 4/(4\sqrt{8}) = 10/(4\sqrt{8}) = 5/(2\sqrt{8}) = 5/(4\sqrt{2})$.
        *   Wait, is it $5/(4\sqrt{2})$? Let's trace exactly.
        *   Initial state $|\psi\rangle = \frac{1}{2\sqrt{2}} \sum |x\rangle$.
        *   Oracle $U_w$ applies -1 to $|111\rangle$.
        *   $|\psi_1\rangle = \frac{1}{2\sqrt{2}}(|000\rangle + \dots + |110\rangle - |111\rangle)$.
        *

### Reference answer

Dominant output states: |111> with probability ~0.78 each

## isqTrain/902

- task_id: `isqTrain/902`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4010`

### Prompt

Create an isQ quantum circuit that implements the bit_flip_oracle pattern but with a different initial state preparation (flip q[[0]] -> q[1]).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a bit-flip oracle for f(x) = x[0] XOR x[1] with input state x = |10⟩, storing the result in an ancilla qubit.
2. **Qubits**: 3 qubits (q[0], q[1] for input x; q[2] as output ancilla); all 3 are measured.
3. **State evolution**:
   - Initial state: |000⟩
   - After X(q[1]): |010⟩ (prepares x = |10⟩)
   - After CNOT(q[0], q[2]): |010⟩ (control q[0]=|0⟩, no flip)
   - After CNOT(q[1], q[2]): |011⟩ (control q[1]=|1⟩, flips q[2])
4. **Expected probabilities**: Final state is |011⟩ with certainty, giving {|011⟩: 1.0}.
