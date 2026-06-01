# ISQ training COT RAG corpus: quantum_algorithms shard 150

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/771

- task_id: `isqTrain/771`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3480`

### Prompt

Write isQ code for the following quantum task: implements the weighted_adder pattern but with a different initial state preparation (flip q[[0, 1, 2]] -> q[3]).

### Chain-of-thought reasoning

Looking at this weighted adder circuit, let me trace through the state evolution.

1. Goal: Implement a weighted adder with q[0,1,2] as inputs and q[3,4] as sum/carry outputs.

2. Qubits: 5 qubits (q[0..4]). q[3] and q[4] are measured.

3. Initial state: |00000⟩

4. After X(q[3]): |00010⟩ (q[3] is flipped to |1⟩)

5. The adder adds x0+x1+x2 to the sum register (q[3]) with carry (q[4]).

Since q[0]=0, q[1]=0, q[2]=0 (all inputs are |0⟩):
- CNOT(q[0], q[3]): q[0] is |0⟩, so no flip on q[3]. State: |00010⟩
- Toffoli(q[1], q[3], q[4]): q[1]=|0⟩, so no action. State: |00010⟩
- CNOT(q[1], q[3]): q[1]=|0⟩, so no flip. State: |00010⟩
- Toffoli(q[2], q[3], q[4]): q[2]=|0⟩, so no action. State: |00010⟩
- CNOT(q[2], q[3]): q[2]=|0⟩, so no flip. State: |00010⟩

Final state: |00010⟩

Measured qubits: q[3]=1, q[4]=0

In the output, earlier measured qubit = higher bit, so q[3] is the higher bit, q[4] is the lower bit.
Bitstring = q[3]q[4] = 10 = decimal 2.

Wait, The predicted output {|10⟩: 1.0}. So |10⟩ means q[3]=1, q[4]=0, which matches decimal 2.

Actually, wait - let me re-read. The problem says "flip q[[0, 1, 2]] -> q[3]". This seems like it's saying to flip q[0,1,2] to q[3]? But the code only does X(q[3]). Let me re-read the prompt.

"Write an isQ program that implements the weighted_adder pattern but with a different initial state preparation (flip q[[0, 1, 2]] -> q[3])."

This is confusing. But Analyzing the circuit requirements, only X(q[3]) is applied, not X(q[0]), X(q[1]), X(q[2]). 

The implementation only flips q[3] to |1⟩. So the inputs x0=0, x1=0, x2=0, and the sum register starts at 1.

Sum = 0 + 0 + 0 + 1 = 1 (binary: 01, but wait...)

Actually, I need to understand the adder better. The adder is computing x0 + x1 + x2 and storing the result in q[3] (sum bit) and q[4] (carry bit).

Wait, but q[3] starts at |1⟩. So the adder is computing 1 + x0 + x1 + x2? No, let me re-think.

The adder pattern here:
- CNOT(q[0], q[3]): adds x0 to sum
- Toffoli(q[1], q[3], q[4]) + CNOT(q[1], q[3]): half-adder for x1
- Toffoli(q[2], q[3], q[4]) + CNOT(q[2], q[3]): half-adder for x2

Since q[3] starts at |1⟩, and x0=x1=x2=0:
- After all operations, q[3] stays at 1, q[4] stays at 0.

So the sum is 1 (q[3]=1, q[4]=0), representing the value 1 in a 2-bit encoding.

Measurement: q[3]=1 (higher bit), q[4]=0 (lower bit) → |10⟩ with probability 1.0.

Wait, that would be binary 10 = decimal 2. But the actual sum is 1.

Hmm, let me reconsider. The sum register q[3] represents the LSB and q[4] represents the MSB (carry). So:
- q[3] = 1, q[4] = 0 means sum = 0*2 + 1 = 1.

But the bitstring for measurement is: earlier

## isqTrain/3639

- task_id: `isqTrain/3639`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4286`

### Prompt

实现以下量子计算任务（使用isQ）：the 4-qubit QFT applied to input state |1100>. The circuit should use Hadamard gates, controlled-Rz rotations with angles 2π/2^k, and final bit-reversal swaps. Measure all 4 qubits.

### Chain-of-thought reasoning

Let me analyze this QFT circuit step by step.

1. Goal: Implement 4-qubit QFT on input state |1100⟩ (which is |12⟩ in decimal).

2. Qubits: 4 qubits, all measured.

3. State evolution:
- Initial state: |0000⟩
- After X(q[0]) and X(q[1]): |1100⟩ = (|0⟩ + |1⟩)/√2 ⊗ ... wait, let me be more careful. 
  - |1100⟩ means q[3]=1, q[2]=1, q[1]=0, q[0]=0 if q[0] is the least significant bit.
  - Wait, let me check: X(q[0]) flips q[0], X(q[1]) flips q[1], so state becomes |0011⟩ in the usual bit ordering where q[0] is least significant.
  - But in the context of QFT, the input is typically interpreted as representing the integer 12 = 1100 in binary, where the first qubit represents the most significant bit.
  
Let me think about this differently. In many quantum computing frameworks:
- q[0] represents the least significant bit
- So |1100⟩ with X on q[0] and q[1] means q[0]=1, q[1]=1, q[2]=0, q[3]=0
- This represents |3⟩ = |0011⟩ in standard notation

Wait, but The predicted output uniform distribution over all 16 states. Let me verify this.

QFT on |3⟩ for 4 qubits:
QFT_N |k⟩ = (1/√N) Σ_j e^{2πijk/N} |j⟩

For N=16 and k=3:
QFT_16 |3⟩ = (1/4) Σ_{j=0}^{15} e^{2πi·3·j/16} |j⟩

The magnitude of each coefficient is 1/4, so the probability of measuring each state is 1/16 = 0.0625.

This matches the predicted output!

So the state evolution:
- Start: |0000⟩
- After X(q[0]), X(q[1]): |0011⟩ (q[0]=1, q[1]=1) = |3⟩ in computational basis

Now the QFT stages:

For qubit 0 (least significant):
- H on q[0]: transforms the state
- Controlled Rz rotations from q[1], q[2], q[3] to q[0]

Actually, let me think about the QFT more carefully. The QFT circuit works as follows:

For the j-th qubit (starting from 0):
1. Apply H to qubit j
2. For each k > j, apply controlled-R_k (rotation by 2π/2^k) with qubit k as control and qubit j as target

Then swap qubits for bit reversal.

The input |3⟩ = |0011⟩ means:
- q[0] = 1
- q[1] = 1
- q[2] = 0
- q[3] = 0

After QFT, we get a uniform superposition over all 16 states with equal magnitude but different phases. Since QFT preserves the normalization and spreads the amplitude uniformly (each has magnitude 1/4), each state has probability (1/4)² = 1/16 = 0.0625.

Let me write the reasoning concisely:

## Reasoning

1. **Goal**: Apply 4-qubit QFT to input |3⟩ (prepared as |0011⟩ with X on q[0] and q[1]), then measure all qubits.

2. **Qubits**: 4 qubits (q[0]-q[3]), all measured.

3. **State evolution**:
   - Initial: |0000⟩ → After X(q[0]), X(q[1]): |3⟩ = |0011⟩
   - QFT stage on q[0]: H creates superposition, controlled-Rz from q[1],q[2],q[3] add phase rotations with angles π/2, π/4, π/8
   - QFT stage on q[1]: H creates superposition, controlled-Rz from q[2],q[3] add phases π/2, π/4
   - QFT stage on q[2]: H creates superposition, controlled-Rz from q[3] adds phase π/2
   - QFT stage on q[3]: H creates superposition
   - Bit-reversal swaps: q[0]↔q[3], q[1]↔q

## isqTrain/4642

- task_id: `isqTrain/4642`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2473`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[2];

procedure main() {
    
    X(q[0]);

    
    
    
    

    
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);
    
    X(q[0]); H(q[1]);  // replaced H with X
    CNOT(q[0], q[1]);
    Rz(0.785398163397448, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);

    
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);
    
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(0.785398163397448, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);

    
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

The user wants to analyze an isQ program and predict the probability distribution of measurement outcomes.
The circuit operates on 2 qubits $q_0$ and $q_1$.
Initial state is $|00\rangle$.

1. `X(q[0])`: State becomes $|10\rangle$.
2. `CNOT(q[0], q[1])`: State becomes $|11\rangle$.
3. `Rz(0.392699081698724, q[1])`: which is $\pi/8$. State is $e^{-i\pi/16}|11\rangle$.
4. `CNOT(q[0], q[1])`: State is $e^{-i\pi/16}|10\rangle$.
5. `X(q[0])`: State is $e^{-i\pi/16}|00\rangle$.
6. `H(q[1])`: State is $e^{-i\pi/16} \frac{1}{\sqrt{2}}(|00\rangle + |01\rangle)$.
7. `CNOT(q[0], q[1])`: Control is $q_0$ (which is $|0\rangle$). State is unchanged.
8. `Rz(0.785398163397448, q[1])`: which is $\pi/4$. State is $\frac{1}{\sqrt{2}}(e^{-i\pi/8}|00\rangle + e^{i\pi/8}|01\rangle)$.
9. `CNOT(q[0], q[1])`: Control is $q_0$. Unchanged.
10. `H(q[0]); H(q[1]);`: 
State becomes $\frac{1}{\sqrt{2}} \left( \frac{1}{\sqrt{2}}(|0\rangle+|1\rangle) \otimes \frac{1}{\sqrt{2}}(e^{-i\pi/8}(|0\rangle+|1\rangle) + e^{i\pi/8}(|0\rangle-|1\rangle)) \right)$
$= \frac{1}{2} |+\rangle \otimes ( \frac{e^{-i\pi/8} + e^{i\pi/8}}{\sqrt{2}} |0\rangle + \frac{e^{-i\pi/8} - e^{i\pi/8}}{\sqrt{2}} |1\rangle )$
$= \frac{1}{2} |+\rangle \otimes ( \cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle )$
Actually, it might be easier to just write the state vector or use the rotation equivalences.
Let's trace carefully:
Initial: $|00\rangle$
1. X(q0): $|10\rangle$
2. CNOT: $|11\rangle$
3. Rz(pi/8, q1): $e^{-i\pi/16}|11\rangle$
4. CNOT: $e^{-i\pi/16}|10\rangle$
5. X(q0): $e^{-i\pi/16}|00\rangle$
6. H(q1): $e^{-i\pi/16} |0\rangle \otimes |+\rangle$
7. CNOT: Control $q_0=0$, target $q_1$, unchanged: $e^{-i\pi/16} |0\rangle \otimes |+\rangle$
8. Rz(pi/4, q1): $e^{-i\pi/16} |0\rangle \otimes (e^{-i\pi/8}|0\rangle + e^{i\pi/8}|1\rangle)/\sqrt{2}$
9. CNOT: unchanged.
10. H(q0)H(q1): 
$e^{-i\pi/16} \frac{1}{2} (|0\rangle+|1\rangle) \otimes (e^{-i\pi/8}(|0\rangle+|1\rangle) + e^{i\pi/8}(|0\rangle-|1\rangle))/\sqrt{2}$
$= \frac{1}{2} (|0\rangle+|1\rangle) \otimes (\cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle)$

Wait, the sequence is a bit long, let's use the result from the simulator output. It is a uniform distribution over $|00\rangle, |01\rangle, |10\rangle, |11\rangle$, each with probability 0.25.
Let's see why.
Let's analyze the

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.2500, P(|01>) = 0.2500, P(|10>) = 0.2500, P(|11>) = 0.2500.'}

## isqTrain/2714

- task_id: `isqTrain/2714`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5705`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[2];

procedure main(){
    H(q[0]);
    CNOT(q[0],q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |00>.
2. H gate on q[0] creates an equal superposition: (|00> + |10>) / sqrt(2).
3. CNOT(q[0], q[1]) entangles the qubits, flipping q[1] when q[0] is |1>: (|00> + |11>) / sqrt(2).
4. Measuring both qubits collapses the state to either |00> or |11>.

Predicted probability distribution: {'00': 0.5, '11': 0.5}

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3628

- task_id: `isqTrain/3628`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `371`

### Prompt

Code this in isQ: the 3-qubit Quantum Fourier Transform (QFT) applied to the input state |011>. The circuit should:
1. Prepare the input state by applying X gates where needed
2. Apply the QFT using Hadamard and controlled-Rz gates
3. Include the final bit-reversal swaps
4. Measure all 3 qubits

### Chain-of-thought reasoning

Let me trace through the 3-qubit QFT applied to |011>.

1. Goal: Apply 3-qubit QFT to input state |011>.

2. Qubits: 3 qubits q[0], q[1], q[2], all measured.

3. State evolution:
   - Initial: |000>
   - After X(q[1]), X(q[2]): |011>
   - QFT on 3 qubits transforms |011> which represents the number 3 (in big-endian, q[2]q[1]q[0] = 110 = 6... wait, let me be careful about indexing).

Wait, let me reconsider. In the QFT, we typically consider q[0] as the least significant bit. So |011> means q[0]=1, q[1]=1, q[2]=0, which represents the number 3.

Actually, let me just trace through the gates:

Starting state: |000>

After X(q[1]) and X(q[2]):
|011> (q[0]=0, q[1]=1, q[2]=1)

Now the QFT stage:

Stage for qubit 0 (q[0]):
- H(q[0]): |011> → (|0⟩ + |1⟩)/√2 ⊗ |11⟩ = (|011⟩ + |111⟩)/√2
- CRz(π/4, q[1]→q[0]): controlled by q[1], which is |1⟩ in both components, so Rz(π/4) is applied to q[0]. The |1⟩ component of q[0] picks up phase e^{-iπ/8}... 

Wait, let me be more careful. Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2}). So Rz(π/4) = diag(e^{-iπ/8}, e^{iπ/8}).

Actually, let me think about this differently. The QFT of a computational basis state |k⟩ gives (1/√N) Σ_j e^{2πijk/N} |j⟩.

For 3 qubits, N=8. Input |011⟩ where q[0]=1, q[1]=1, q[2]=0, so k = 1 + 2 + 0 = 3.

QFT|3⟩ = (1/√8) Σ_{j=0}^{7} e^{2πi·3·j/8} |j⟩

The phases are:
j=0: 1
j=1: e^{6πi/8} = e^{3πi/4}
j=2: e^{12πi/8} = e^{3πi/2} = -i... wait, e^{3πi/2} = e^{-πi/2} = -i
j=3: e^{18πi/8} = e^{9πi/4} = e^{πi/4}
j=4: e^{24πi/8} = e^{3πi} = -1
j=5: e^{30πi/8} = e^{15πi/4} = e^{3πi/4}... 

Hmm, this is getting complicated. Let me just verify the final result.

Actually, for the QFT, when applied to a computational basis state |k⟩, the output is:
QFT|k⟩ = (1/√N) Σ_{j=0}^{N-1} ω^{kj} |j⟩
where ω = e^{2πi/N}.

The magnitudes of all coefficients are 1/√8, so the measurement probabilities are all equal: 1/8 = 0.125 for each basis state.

This makes sense! The QFT of a computational basis state is a uniform superposition with equal magnitudes (but different phases), so all measurement outcomes have equal probability.

Let me trace more carefully through the circuit to verify:

Initial: |000⟩
After X(q[1]), X(q[2]): |011⟩

Stage for q[0]:
H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |11⟩ = (|011⟩+|111⟩)/√2
CRz(π/2, q[1]→q[0]): Since q[1]=1 in both terms, apply Rz(π/2) to q[0].
Rz(π/2) = diag(e^{-iπ/4}, e^{iπ/4})
|0⟩→e^{-iπ/4}|0⟩, |1⟩→e^{

## isqTrain/3580

- task_id: `isqTrain/3580`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `basis_change`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `4709`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should 3-qubit phase-flip code encode + decode |0_L>.

### Chain-of-thought reasoning

Let me analyze the buggy code and the fix.

The buggy code has:

The fixed code has:

The bug is that the first CNOT has the control and target swapped. In the buggy code, `CNOT(q[1], q[0])` uses q[1] as control and q[0] as target, but since q[1] starts in |0>, this CNOT does nothing. The correct version should use q[0] as control and q[1] as target, i.e., `CNOT(q[0], q[1])`.

Let me trace through the corrected circuit:

1. Initial state: |000>

2. CNOT(q[0], q[1]): q[0] is control, q[1] is target. Since q[0]=|0>, nothing happens. State: |000>

3. CNOT(q[0], q[2]): q[0] is control, q[2] is target. Since q[0]=|0>, nothing happens. State: |000>

4. H(q[0]); H(q[1]); H(q[2]): Apply H to all three qubits. State: |+++> = H⊗H⊗H |000>

5. H(q[0]); H(q[1]); H(q[2]): Apply H to all three qubits again. This undoes the previous H gates. State: |000>

6. CNOT(q[0], q[2]): Since q[0]=|0>, nothing happens. State: |000>

7. CNOT(q[0], q[1]): Since q[0]=|0>, nothing happens. State: |000>

8. Measurement: |000> with probability 1.0. ✓

Now let me trace through the buggy circuit:

1. Initial state: |000>

2. CNOT(q[1], q[0]): q[1] is control, q[0] is target. Since q[1]=|0>, nothing happens. State: |000>

3. CNOT(q[0], q[2]): Since q[0]=|0>, nothing happens. State: |000>

4. H(q[0]); H(q[1]); H(q[2]): State: |+++>

5. H(q[0]); H(q[1]); H(q[2]): State: |000>

6. CNOT(q[0], q[2]): Since q[0]=|0>, nothing happens. State: |000>

7. CNOT(q[0], q[1]): Since q[0]=|0>, nothing happens. State: |000>

Hmm, wait. In this specific case where we start from |000>, the buggy code actually gives the same result because q[0] and q[1] are both |0>, so the CNOT direction doesn't matter.

But let me think about this more carefully. The 3-qubit phase-flip code is designed to work for any input state. Let me consider a general input.

Actually, looking at this more carefully, the initial state is |000> and we're encoding |0_L>. The bit-flip encoding maps |0> → |000>, |1> → |111>. Then we apply H to all qubits to get phase-flip encoding: |0_L> = |+++>, |1_L> = |--->.

For the encoding from |0>:
- Start: |000> (only q[0] matters, q[1] and q[2] are ancillas)
- CNOT(q[0], q[1]): |000> (control is |0>, so no change)
- CNOT(q[0], q[2]): |000>
- H all: |+++>

For the buggy version with CNOT(q[1], q[0]):
- Start: |000>
- CNOT(q[1], q[0]): q[1] controls q[0]. Since q[1]=|0>, no change. |000>
- CNOT(q[0], q[2]): |000>
- H all: |+++>

So in this specific case, both give the same result. But conceptually, the encoding is wrong. The correct bit-flip encoding uses q[0] as the data qubit and copies it to q[1] and q[2].

The bug is in the first CNOT direction. It should be CNOT(q[0], q[1]) not CNOT(q[1], q[0]). The correct encoding treats q[0] as the data qubit and propagates its value to q[1] and q[

## isqTrain/3539

- task_id: `isqTrain/3539`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2223`

### Prompt

预测以下isQ代码的输出概率：

```
import std;

qbit q[2];

procedure main() {
    H(q[0]); H(q[1]);

    CZ(q[0], q[1]);

    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Predict the output probability distribution of an isQ program.
    *   **Input:** isQ code applying H, CZ on 2 qubits, H, X, CZ, X, H, and M.
    *   **Output format:** Step-by-step reasoning in Dirac notation. Starts with "## Circuit Analysis". List all basis states with non-zero probability at the end. Keep it concise (3-15 lines).
    *   **Key constraints:** Use Dirac notation. Output *only* the analysis. End with the predicted probability distribution.

2.  **Analyze the Circuit:**
    *   Initial state: $|00\rangle$
    *   `H(q[0]); H(q[1]);` -> $(H \otimes H)|00\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) = |++\rangle$
    *   `CZ(q[0], q[1]);` -> Apply CZ on $|++\rangle$. CZ flips the sign of $|11\rangle$.
        State becomes $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$
    *   `H(q[0]); H(q[1]);` -> Apply H to both qubits.
        Let's look at the mapping:
        $|00\rangle \xrightarrow{HH} |00\rangle + |01\rangle + |10\rangle + |11\rangle$
        $|01\rangle \xrightarrow{HH} |00\rangle - |01\rangle + |10\rangle - |11\rangle$
        $|10\rangle \xrightarrow{HH} |00\rangle + |01\rangle - |10\rangle - |11\rangle$
        $|11\rangle \xrightarrow{HH} |00\rangle - |01\rangle - |10\rangle + |11\rangle$
        Combine:
        $(1+1+1+1)|00\rangle = 4|00\rangle$
        $(1-1+1-1)|01\rangle = 0$
        $(1+1-1-1)|10\rangle = 0$
        $(1-1-1+1)|11\rangle = 0$ (Wait, sign of $|11\rangle$ is negative in previous state)
        Let's recalculate carefully:
        State is $\frac{1}{2}( |00\rangle + |01\rangle + |10\rangle - |11\rangle )$
        $H \otimes H (|00\rangle + |01\rangle + |10\rangle - |11\rangle)$
        $= \frac{1}{2} [ (|++\rangle) + (|+-\rangle) + (-+\rangle) - (|--\rangle) ]$ (using $H|0\rangle = |+\rangle, H|1\rangle = |-\rangle$)
        Let's use the identity: $H^{\otimes n} CZ_{12} H^{\otimes n} = CNOT_{12}$ (Wait, CZ is diag(1,1,1,-1). H on target changes CZ to CNOT. H on both changes CZ to something else? No, H on target of CZ gives CNOT. H on both gives $CNOT_{21}$? Let's check.)
        Actually, $H_2 CZ_{12} H_2 = CNOT_{12}$
        $H_1 CZ_{12} H_1 = CNOT_{21}$ ? No. $H_1 Z_1 H_1 = X_1$. So $H_1 CZ_{12} H_1$ applies $X_1$ when $q_2$ is 1. Yes, $CNOT_{21}$.
        So $H_1 H_2 CZ_{12} H_1 H_2$ is $H_1 CNOT_{12} H_1$ ?
        Wait, let's just track the state directly.
        State before second HH: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$.
        Apply $H \otimes H$:
        $H|0\rangle = |+\rangle$, $H|1\rangle = |-\rangle$.
        $H \otimes H$ applied to state:
        $|+\rangle|+\rangle + |+\rangle|-\rangle + |-\rangle|+\rangle - |-\rangle|-\rangle$
        $= (|0\rangle+|1\rangle)(|0\rangle+|1\rangle)

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'The output is |11> with probability 1.0'}

## isqTrain/79

- task_id: `isqTrain/79`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `467`

### Prompt

Write isQ code for the following quantum task: implements a variant of the gate_decomposition pattern using q[1] -> q[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement a gate_decomposition variant using q[1] -> q[2] with an expanded 3-qubit register, producing deterministic |10> measurement output.
2. Qubits needed: 3 (q[0], q[1], q[2]), with q[1] and q[2] measured.
3. State evolution:
   - Initial state: |000>
   - After X(q[1]): |010>
4. Final state |010> yields measurement outcome |10> (q[1]=1, q[2]=0) with probability 1.0, as earlier measured qubit (q[1]) is the higher bit.

## isqExpand/algo/124

- task_id: `isqExpand/algo/124`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `interference`, `superposition`
- source: `qa_pipeline`
- dataset_index: `1284`

### Prompt

什么是固定点振幅放大（Fixed-Point Amplitude Amplification）？它解决了标准Grover/振幅放大的什么问题？请解释其核心机制和优势。

### Chain-of-thought reasoning

## 推理
目标：解释固定点振幅放大。

关键点：
1. 标准Grover的周期性问题
2. 可变相位序列代替固定Pi相位
3. Chebyshev多项式确定最优序列
4. 与QSP的联系

### Reference answer

## 固定点振幅放大

### 标准振幅放大的问题
标准Grover搜索和振幅放大存在一个关键缺陷：如果不知道解的数目M，就无法精确选择迭代次数。迭代过多会导致振幅过冲——成功概率反而下降。这是因为Grover旋转是周期性的，成功概率会在0和1之间振荡。

### 固定点的含义
固定点振幅放大使得成功概率**单调递增**到目标值并保持不变。即使执行更多迭代，概率也不会下降。

### 核心机制
关键修改：将Oracle和反射算子中的相位从Pi变为精心设计的可变相位序列。

具体做法（Yoder, Low, Chuang 2014）：
1. 使用 L 次迭代，每次的相位角度不同
2. Oracle: O_j = I - (1 - e^{i*alpha_j})|good><good|
3. 相位序列由Chebyshev多项式确定

### 优势
1. 鲁棒性：不需要精确知道解的数目
2. 单调性：成功概率只增不减
3. 复杂度保持 O(1/sqrt(a))
4. 与量子信号处理(QSP)框架有深刻联系

## isqTrain/3904

- task_id: `isqTrain/3904`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4015`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```
import std;
// QFT on 3 qubits with input state |010>
qbit q[3];

procedure main() {
    // Prepare input state |010>
    X(q[1]);

    // QFT stage for qubit 0
    H(q[0]);
    ctrl Rz(2.0 * 2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    // QFT stage for qubit 1
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    // QFT stage for qubit 2
    H(q[2]);
    // Swap q[0] and q[2]
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    // Measure after QFT
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

The task is to analyze a bug in a 3-qubit QFT circuit with input state |010>.

Let me first understand the QFT circuit and then identify the bug.

For a 3-qubit QFT, the controlled rotation gates should be:
- For qubit 0: H(q[0]), then controlled R_{k} where k=2 (phase π/2) from q[1], and k=3 (phase π/4) from q[2]
- For qubit 1: H(q[1]), then controlled R_{k} where k=2 (phase π/2) from q[2]
- For qubit 2: H(q[2])

The rotation angle for R_k is 2π/2^k.

For the stage on qubit 0:
- Controlled by q[1]: R_{2} with angle 2π/2^2 = 2π/4
- Controlled by q[2]: R_{3} with angle 2π/2^3 = 2π/8

In the buggy code:

The first line has `2.0 * 2.0 * 3.14159265358979 / 4.0` which equals π, but it should be `2.0 * 3.14159265358979 / 4.0` which equals π/2.

In the corrected version:

So the bug is an extra `2.0 *` factor in the first controlled rotation, making it π instead of π/2.

Now let me verify the state evolution with the corrected circuit:

Input: |010> (in computational basis, meaning q[2]q[1]q[0] = 010, so q[0]=0, q[1]=1, q[2]=0)

After X(q[1]): |010> (q[0]=0, q[1]=1, q[2]=0)

Stage for qubit 0:
- H(q[0]): Since q[0]=0, this gives (|0>+|1>)/√2 ⊗ |1> ⊗ |0> = (|010> + |110>)/√2

Wait, let me be more careful with the notation. Let me write states as |q[2]q[1]q[0]>.

Initial: |010> means q[2]=0, q[1]=1, q[0]=0.

After X(q[1]): |010>

H(q[0]): (|011> + |010>)/√2

ctrl Rz(π/2, q[1], q[0]): When q[1]=1, apply Rz(π/2) to q[0]. Rz(θ)|0> = |0>, Rz(θ)|1> = e^{iθ/2}|1>.

Wait, I need to be careful about the Rz convention. Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]].

Actually for QFT, the standard is to use phase gates. Let me think about this differently.

The state after H(q[0]) on |010> is:
(|0> + |1>)_q[0] / √2 ⊗ |1>_{q[1]} ⊗ |0>_{q[2]}
= (|010> + |011>)/√2 in |q[2]q[1]q[0]> ordering

Wait, I'm getting confused. Let me use the ordering consistently. Let |q[2]q[1]q[0]>.

|010> means q[2]=0, q[1]=1, q[0]=0.

H(q[0]) acts on qubit 0:
|0>_q
