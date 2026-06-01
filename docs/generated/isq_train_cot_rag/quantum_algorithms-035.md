# ISQ training COT RAG corpus: quantum_algorithms shard 35

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3800

- task_id: `isqTrain/3800`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4102`

### Prompt

请用isQ语言编写一个量子电路：4-bit Bernstein-Vazirani to find secret s=0001. Use oracle keyword, for loops for Hadamard. Measure all 5 qubits.

### Chain-of-thought reasoning

Let me analyze the Bernstein-Vazirani circuit step by step.

**Goal**: Find the secret string s=0001 using the Bernstein-Vazirani algorithm.

**Qubits**: 5 qubits (q[0]-q[3] for input, q[4] for output/ancilla). All 5 are measured.

**Step-by-step state evolution**:

1. **Initial state**: |00000⟩

2. **X(q[4])**: Flips q[4] → |00001⟩

3. **H(q[4])**: Puts q[4] in |-⟩ = (|0⟩ - |1⟩)/√2 → |0000⟩ ⊗ |-⟩

4. **Hadamard on q[0]-q[3]**: Creates uniform superposition
   (1/4) Σ|x⟩ ⊗ |-⟩ where x ranges over 4-bit strings

5. **Oracle f**: The oracle computes f(x) = x·s mod 2 where s=0001. The truth table is:
   - f(0000)=0, f(0001)=1, f(0010)=0, f(0011)=1, f(0100)=0, f(0101)=1, f(0110)=0, f(0111)=1
   - f(1000)=0, f(1001)=1, f(1010)=0, f(1011)=1, f(1100)=0, f(1101)=1, f(1110)=0, f(1111)=1
   
   This is because x·s = x[3] (the last bit of x, since s=0001).
   
   The oracle applies phase kickback: |x⟩|−⟩ → (-1)^f(x)|x⟩|−⟩
   
   So: (1/4) Σ(-1)^(x·s)|x⟩ ⊗ |-⟩

6. **Hadamard on q[0]-q[3]**: Applying H^⊗4 to the phase state gives |s⟩ = |0001⟩
   
   So the state becomes |0001⟩ ⊗ |-⟩

7. **Measurement**: 
   - q[0] measures 0
   - q[1] measures 0
   - q[2] measures 0
   - q[3] measures 1
   - q[4] measures 0 or 1 with equal probability (since |-⟩ = (|0⟩-|1⟩)/√2)

Wait, Let me verify the output: {|00010>: 0.5, |00011>: 0.5}

In the isQ measurement bitstring format, earlier measured qubit = higher bit.

So the bitstring is q[0]q[1]q[2]q[3]q[4] where q[0] is the highest bit.

|00010⟩ means q[0]=0, q[1]=0, q[2]=0, q[3]=1, q[4]=0
|00011⟩ means q[0]=0, q[1]=0, q[2]=0, q[3]=1, q[4]=1

This matches my analysis: the input qubits give |0001⟩ (the secret s) and q[4] is in |-⟩ which measures 0 or 1 with equal probability.

Wait, but |-⟩ = (|0⟩ - |1⟩)/√2, so the probabilities are:
P(0) = |1/√2|² = 0.5
P(1) = |-1/√2|² = 0.5

Yes, that's correct.

Let me also verify the oracle truth table. The oracle is defined as:

For a 4-input, 1-output oracle, the truth table has 16 entries (for each of the 2^4 = 16 input combinations). The index i corresponds to the binary representation of the input.

Index 0 (0000): f=0 → 0·0001 = 0 ✓
Index 1 (0001): f=1 → 0001·0001 = 1 ✓
Index 2 (0010): f=0 → 0010·0001 = 0 ✓
Index 3 (0011): f=1 → 0011·0001 = 1 ✓
... and so on.

Yes, this is f(x) = x·s

## isqTrain/2910

- task_id: `isqTrain/2910`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4820`

### Prompt

修复以下isQ程序中的错误：

```isq
import std;
oracle bool[1] g(bool a[4]) {
    bool s[] = [true, false, true, false];
    bool ba[] = s & a;
    bool res[1];
    res[0] = ba[0] != ba[1] != ba[2] != ba[3];
    return res;
}
qbit q[4];
qbit anc[1];

procedure main() {
    X(anc);
    H(anc);
    H(q);
    g(q, anc);
    // H(q); // BUG: missing Hadamard
    for i in 0:4 {
        M(q[i]);
    }
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: The second `H(q)` application after the oracle call `g(q, anc)` is commented out (missing). In the Bernstein-Vazirani algorithm, the Hadamard gates *after* the oracle are essential to convert the phase-encoded answer back into the computational basis. Without them, the qubits remain in a phase-encoded superposition, and measurement yields random results instead of the secret string.

2. **Fix**: Uncomment (add back) `H(q)` after `g(q, anc);`. This applies the inverse Hadamard transform to decode the phase information into the bitstring `s = 1010`.

3. **State evolution (corrected)**:
   - `|0000>|0>` → X(anc) → `|0000>|1>`
   - H(anc), H(q) → `|++++>|->` (uniform superposition with ancilla in `|->`)
   - g(q, anc) → Phase kickback encodes `s=1010`: `(1/4)Σ_x (-1)^(s·x)|x>|->`
   - H(q) → Inverse Hadamard recovers `|1010>|->`
   - Measure q → `|1010>` with probability 1.0

## isqTrain/335

- task_id: `isqTrain/335`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `701`

### Prompt

Code this in isQ: implements the qft_subcircuit pattern but with a different initial state preparation (flip q[[1]] -> q[2]).

### Chain-of-thought reasoning

Let me analyze this QFT circuit step by step.

The goal is to implement a QFT subcircuit on 3 qubits with initial state preparation of |100⟩ (X on q[2]).

Initial state: |000⟩
After X(q[2]): |100⟩ (qubit 2 is |1⟩, qubits 0,1 are |0⟩)

Now let me trace through the QFT on this state.

The QFT acts on qubits q[0], q[1], q[2]. The standard QFT on 3 qubits transforms |k⟩ → (1/√8) Σ_j e^{2πijk/8} |j⟩.

For |100⟩ = |4⟩ in the computational basis:

QFT|4⟩ = (1/√8) Σ_{j=0}^{7} e^{2πi·4·j/8} |j⟩ = (1/√8) Σ_{j=0}^{7} e^{πij} |j⟩

e^{πij} alternates: j=0→1, j=1→-1, j=2→1, j=3→-1, j=4→1, j=5→-1, j=6→1, j=7→-1

So QFT|4⟩ = (1/√8)(|0⟩ - |1⟩ + |2⟩ - |3⟩ + |4⟩ - |5⟩ + |6⟩ - |7⟩)

This is an equal superposition with alternating phases.

The probability of each basis state is |1/√8|² = 1/8 = 0.125.

This matches the expected measurement probabilities perfectly!

Let me verify the circuit structure:

Starting: |000⟩
X(q[2]): |100⟩

QFT on q[2] (most significant):
H(q[2]): |100⟩ → q[2] goes through H, so |0⟩→|+⟩ for q[2]... wait, q[2] is |1⟩ initially.

Actually wait, the state is |100⟩ meaning q[0]=1, q[1]=0, q[2]=0... no.

Let me re-check the bit ordering. In isQ, q[0] is typically the least significant bit. So |100⟩ means q[2]=1, q[1]=0, q[0]=0.

X(q[2]) flips q[2], so state becomes |q[2]=1, q[1]=0, q[0]=0⟩ = |100⟩ in the standard notation where q[0] is LSB.

Now the QFT circuit:
- The QFT processes from the highest index qubit down.
- H(q[2]) acts on q[2]: |1⟩ → |−⟩ = (|0⟩−|1⟩)/√2
- ctrl S(q[1], q[2]): q[1]=|0⟩, so no phase applied to q[2]
- ctrl T(q[0], q[2]): q[0]=|0⟩, so no phase applied to q[2]

After processing q[2]: state is (|0⟩−|1⟩)/√2 ⊗ |0⟩ ⊗ |0⟩ = (|000⟩−|100⟩)/√2

Wait, that doesn't seem right. Let me be more careful with the ordering.

State = |q[0]⟩ ⊗ |q[1]⟩ ⊗ |q[2]⟩ or is it |q[2]⟩ ⊗ |q[1]⟩ ⊗ |q[0]⟩?

In the standard convention for QFT, the state |k⟩ where k = k_{n-1}...k_1 k_0 in binary has q[i] = k_i.

So |4⟩ = |100₂⟩ means q[2]=1, q[1]=0, q[0]=0.

After X(q[2]): state is |4⟩.

H(q[2]): |1⟩ → |−⟩, so the part involving q[2] is (|0⟩−|1⟩)/√2.
ctrl S(q[1], q[2]): Since q[1]=|0⟩, S is not applied. No change.
ctrl T(q[0], q[2]): Since q[0]=|0⟩, T is not applied. No change.

So after q[2] stage: (|000⟩ − |100⟩)/√2... hmm, that means q[2] is in superposition and q[1], q[0] remain |0⟩.

Wait, I need to think about this more carefully with the full QFT.

Actually, QFT|4⟩ should give equal amplit

## isqTrain/2881

- task_id: `isqTrain/2881`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `measurement_order`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5301`

### Prompt

I need an isQ program to implementing a 3-controlled X gate. Set all 3 control qubits to |1>, then apply the multi-controlled X gate. Measure all 4 qubits.

Requirements:
- Declare `qbit q[4];` at global scope.
- Use `procedure main()` as entry point.
- Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a 3-controlled X gate with all controls set to |1>, flipping the target qubit.
2. **Qubits**: 4 qubits (q[0], q[1], q[2] as controls, q[3] as target); all 4 are measured.
3. **State evolution**:
   - Initial: |0000⟩
   - After X(q[0]), X(q[1]), X(q[2]): |1110⟩
   - After ctrl ctrl ctrl X(q[0], q[1], q[2], q[3]): All three controls are |1⟩, so X is applied to q[3], giving |1111⟩
4. **Expected result**: Measurement yields |1111⟩ with probability 1.0, since all four qubits are in the |1⟩ state.

## isqTrain/2887

- task_id: `isqTrain/2887`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `811`

### Prompt

用isQ实现applies a Rx(pi/2) rotation to a single qubit and measures it.

Requirements:
- Declare `qbit q[1];` at global scope.
- Use `procedure main()` as entry point.
- Measure the qubit.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an Rx(π/2) rotation to a single qubit initialized to |0⟩, then measure it.
2. **Qubits**: 1 qubit (`q[0]`) is used and measured.
3. **State evolution**:
   - Initial state: |0⟩
   - After Rx(π/2): Rx(π/2)|0⟩ = cos(π/4)|0⟩ - i·sin(π/4)|1⟩ = (1/√2)(|0⟩ - i|1⟩)
4. **Expected probabilities**: |⟨0|ψ⟩|² = |1/√2|² = 0.5, |⟨1|ψ⟩|² = |-i/√2|² = 0.5, giving equal probability {|0⟩: 0.5, |1⟩: 0.5}.

## isqTrain/1171

- task_id: `isqTrain/1171`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4946`

### Prompt

请用isQ语言编写一个量子电路：implements the iqp_circuit pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

Let me analyze this IQP circuit step by step.

The circuit has:
- 3 qubits: q[0], q[1], q[2]
- First Hadamard layer on all 3 qubits
- Diagonal gates: T on all qubits, CZ(q[0], q[1]), CZ(q[1], q[2])
- Second Hadamard layer on all 3 qubits
- Measurement in reversed order: M(q[2]), M(q[1]), M(q[0])

The measurement order is reversed, which means:
- q[2] is measured first (becomes the highest bit)
- q[1] is measured second (becomes middle bit)
- q[0] is measured last (becomes lowest bit)

So the bitstring ordering is: q[2] q[1] q[0]

Let me trace through the circuit:

1. Initial state: |000>

2. After first H layer: H(q[0]) H(q[1]) H(q[2])
   |+++> = (1/2√2)(|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)

3. After T(q[0]), T(q[1]), T(q[2]):
   T applies phase e^(iπ/4) to |1> state
   Each computational basis state |abc> gets phase e^(iπ(a+b+c)/4)

4. After CZ(q[0], q[1]):
   CZ applies Z to target when control is |1>, which means it adds phase -1 when both are |1>
   So states where q[0]=1 AND q[1]=1 get a phase of -1

5. After CZ(q[1], q[2]):
   States where q[1]=1 AND q[2]=1 get a phase of -1

6. After second H layer:
   This maps back to computational basis with Hadamard transform

Let me calculate more carefully.

After H⊗3, the state is:
|ψ₁> = (1/2√2) Σ_{abc} |abc>

After T⊗3:
|ψ₂> = (1/2√2) Σ_{abc} e^(iπ(a+b+c)/4) |abc>

After CZ(q[0], q[1]):
Phase factor (-1) when a=1 and b=1

After CZ(q[1], q[2]):
Phase factor (-1) when b=1 and c=1

So the combined diagonal phase for state |abc> is:
φ(abc) = π(a+b+c)/4 + π·ab + π·bc

where ab = a·b (1 if both 1, 0 otherwise), bc = b·c (1 if both 1, 0 otherwise)

Let me compute φ for each basis state:
- |000>: φ = 0
- |001>: φ = π/4
- |010>: φ = π/2
- |011>: φ = 3π/4 + π = 7π/4
- |100>: φ = π/4
- |101>: φ = π/2
- |110>: φ = 3π/4 + π = 7π/4
- |111>: φ = 3π/4 + π + π = 11π/4 = 3π/4 (mod 2π)

After H⊗3:
|ψ_final> = (1/2√2) Σ_{abc} Σ_{xyz} e^(iφ(abc)) (-1)^(a·x + b·y + c·z) |xyz>

The amplitude for |xyz> is:
A(xyz) = (1/2√2) Σ_{abc} e^(iφ(abc)) (-1)^(ax + by + cz)

Let me compute |A(xyz)|² for each xyz:

Actually, this is getting complex. Let me verify the probabilities are correct by computing numerically.

φ(abc) values:
- |000>: 0
- |001>: π/4
- |010>: π/2
- |011>: 3π/4 + π = 7π/4
- |100>: π/4
- |101>: π/2
- |110>: 3π/4 + π = 7π/4
- |111>: 3π/4 + π + π = 11π/4 = 3π/4 (mod 2π)

Wait, let me recalculate:
- |011>: a=0, b=1, c=1
  φ = π(0+1+1)/4 + π·(0·1)

## isqTrain/1388

- task_id: `isqTrain/1388`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5213`

### Prompt

Implement the following in isQ: the Bernstein-Vazirani algorithm to find the secret string s = 001 (MSB first). Use 3 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Implement Bernstein-Vazirani to find secret string s = 001 (encoded in oracle).

**Qubits**: 3 input qubits q[0], q[1], q[2] + 1 ancilla anc[0]; measure q[0], q[1], q[2].

**State evolution**:
1. Initialize: |000⟩|0⟩
2. X then H on ancilla: |000⟩|−⟩ where |−⟩ = (|0⟩−|1⟩)/√2
3. H⊗3 on input: |+++⟩|−⟩ = (Σ_x |x⟩/√8)|−⟩
4. Oracle CNOT(q[2], anc[0]): phase kickback adds (−1)^(s·x) where s=001, giving Σ_x (−1)^(x₂)|x⟩/√8 |−⟩
5. H⊗3 on input: transforms phase-encoded s into computational basis state |001⟩

**Result**: Final input state is exactly |001⟩ with probability 1.0, revealing the secret string s = 001.

## isqTrain/3069

- task_id: `isqTrain/3069`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `5497`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[4];
procedure main() {
    X(q[2]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Four qubits initialized to |0000>.
2. X(q[2]) flips qubit 2: |0000> → |0010>.
3. All qubits measured. The state is an eigenstate of the measurement basis.
4. Only outcome q[0]q[1]q[2]q[3] = 0010 is possible.

Predicted probability distribution: {'0010': 1.0}

### Reference answer

{'predicted_probs': {'0010': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/743

- task_id: `isqTrain/743`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `5619`

### Prompt

Implement the following in isQ: implements the qft_adder pattern with modified rotation parameters (num_pi2_to_pi4). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Let me analyze this isQ quantum program step by step.

The circuit implements a QFT-based adder with modified rotation parameters.

**Initial state:** |00>

**Step 1: Encode input value 1**
- X(q[0]) → |10>

**Step 2: Forward QFT on 2 qubits**
- H(q[1]) → 1/√2 (|10> + |11>) = |1⟩⊗|+⟩
- ctrl S(q[0], q[1]) → This applies S to q[1] when q[0] is |1⟩
  - S|0⟩ = |0⟩, S|1⟩ = i|1⟩
  - So |10⟩ → |10⟩, |11⟩ → i|11⟩
  - Result: 1/√2 (|10⟩ + i|11⟩) = |1⟩⊗(|0⟩ + i|1⟩)/√2 = |1⟩⊗(H·S)|+⟩
  
  Wait, let me reconsider. Actually q[0] is the control and q[1] is the target. So when q[0]=|1⟩, apply S to q[1].
  
  Current state: 1/√2 (|10⟩ + |11⟩)
  After ctrl S(q[0], q[1]): 1/√2 (|10⟩ + i|11⟩)

- H(q[0]) → Apply H to q[0]
  - H|1⟩ = 1/√2(|0⟩ - |1⟩)
  - |10⟩ → 1/√2(|00⟩ - |10⟩)
  - |11⟩ → 1/√2(|01⟩ - |11⟩)
  - So 1/√2 (1/√2(|00⟩ - |10⟩) + i·1/√2(|01⟩ - |11⟩))
  = 1/2 (|00⟩ - |10⟩ + i|01⟩ - i|11⟩)

**Step 3: Add constant via phase rotations**
- Rz(π, q[0]) → Apply Rz(π) to q[0], which is essentially Z gate (up to global phase)
  - Rz(π)|0⟩ = e^{-iπ/2}|0⟩ = -i|0⟩
  - Rz(π)|1⟩ = e^{iπ/2}|1⟩ = i|1⟩
  
  Actually Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]
  So Rz(π) = [[e^{-iπ/2}, 0], [0, e^{iπ/2}]] = [[-i, 0], [0, i]]
  
  Applied to q[0]:
  - |00⟩ → -i|00⟩
  - |10⟩ → i|10⟩
  - |01⟩ → -i|01⟩
  - |11⟩ → i|11⟩
  
  State: 1/2 (-i|00⟩ + i|10⟩ - i·i|01⟩ + i·i|11⟩) = 1/2 (-i|00⟩ + i|10⟩ + |01⟩ - |11⟩)

- Rz(π/4, q[1]) → Apply Rz(π/4) to q[1]
  - Rz(π/4) = [[e^{-iπ/8}, 0], [0, e^{iπ/8}]]
  
  Applied to q[1]:
  - |00⟩ → e^{-iπ/8}|00⟩
  - |01⟩ → e^{iπ/8}|01⟩
  - |10⟩ → e^{-iπ/8}|10⟩
  - |11⟩ → e^{iπ/8}|11⟩
  
  State: 1/2 (-i·e^{-iπ/8}|00⟩ + i·e^{-iπ/8}|10⟩ + e^{iπ/8}|01⟩ - e^{iπ/8}|11⟩)

**Step 4: Inverse QFT**
- H(q[0]):
  Apply H to q[0]:
  - |00⟩ → 1/√2(|00⟩ + |10⟩)
  - |01⟩ → 1/√2(|01⟩ + |11⟩)
  - |10⟩ → 1/√2(|00⟩ - |10⟩)
  - |11⟩ → 1/√2(|01⟩ - |11⟩)
  
  Let me compute carefully:
  State = 1/2 (-i·e^{-iπ/8}|

## isqTrain/1227

- task_id: `isqTrain/1227`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2937`

### Prompt

Create an isQ quantum circuit that implements the shor_subroutine pattern but with a different initial state preparation (flip w[[0]] -> w[1]).

### Chain-of-thought reasoning

## Reasoning

**Goal**: Implement Shor's modular exponentiation subroutine computing 2^x mod 3, with work register initialized to |01>.

**Qubits**: 3 qubits (x[0], w[0], w[1]); all measured. Output bitstring: x[0] (bit 2), w[0] (bit 1), w[1] (bit 0).

**State evolution**:
1. **Initial**: |000>
2. **X(w[1])**: Prepares work register to |01> (decimal 1) → |001>
3. **H(x[0])**: Superposition on exponent → (|001> + |101>)/√2
4. **ctrl swap (three-CNOT decomposition)(x[0], w[0], w[1])**: When x[0]=|1>, swap w[0]↔w[1]:
   - x=0 branch: work stays |01> (2^0 mod 3 = 1)
   - x=1 branch: |01> → |10> (2^1 mod 3 = 2)
   → (|001> + |110>)/√2

**Result**: Equal superposition of |001> and |110>, giving P(|001>) = 0.5, P(|110>) = 0.5.
