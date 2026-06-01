# ISQ training COT RAG corpus: boolean_logic shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4025

- task_id: `isqTrain/4025`
- task_type: `bug_fix`
- category: `boolean_logic`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3944`

### Prompt

修复以下isQ程序中的错误：

```
import std;
// Boolean function oracle: f(x0, x1) = x0 NAND x1
oracle bool[1] f(bool x[2]) {
    bool res[] = [!(x[0] && x[1])];
    return res;
}

qbit p[2];
qbit r[1];

procedure main() {
    // Inputs in superposition
    X(p[0]); H(p[1]);
    // Apply oracle
    f(p, r);
    // Measure all
    M(p[0]); M(p[1]); M(r[0]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: In `main()`, `X(p[0])` is applied instead of `H(p[0])`. The X gate flips |0⟩→|1⟩ classically, which prevents p[0] from entering superposition, yielding only two input states instead of four.

2. **Fix**: Replace `X(p[0])` with `H(p[0])` so both input qubits enter equal superposition.

3. **State evolution (corrected)**:
   - Initial: |000⟩
   - After H⊗H on p: (|00⟩+|01⟩+|10⟩+|11⟩)/2 ⊗ |0⟩
   - Oracle f(x₀,x₁)=x₀ NAND x₁ maps: 00→1, 01→1, 10→1, 11→0, XORing into r[0]
   - Result: (|001⟩+|011⟩+|101⟩+|110⟩)/2 — matching expected probabilities of 0.25 each.

## isqTrain/3768

- task_id: `isqTrain/3768`
- task_type: `code_generation`
- category: `boolean_logic`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `469`

### Prompt

Write isQ code for the following quantum task: Boolean oracle f(x0,x1) = x0 XNOR x1 using isQ `oracle bool[]` syntax. Use qbit arrays p[2] and r[1]. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement XNOR oracle f(x0,x1) = 1 when x0==x1, placing input qubits in superposition and computing f into ancilla r.

Qubits: p[2] (inputs), r[1] (output). All 3 measured.

State evolution (ordering p[0], p[1], r[0]):
- Initial: |000⟩
- H(p[0]); H(p[1]): → ½(|00⟩+|01⟩+|10⟩+|11⟩)⊗|0⟩ = ½(|000⟩+|010⟩+|100⟩+|110⟩)
- Oracle f: computes XNOR by XOR into r: f=1 flips r, so |00⟩→|001⟩, |01⟩→|010⟩, |10⟩→|100⟩, |11⟩→|111⟩
- Final: ½(|001⟩+|010⟩+|100⟩+|111⟩)

Each basis state has amplitude ½, giving probability |½|² = 0.25 each. The XNOR truth table (00→1, 01→0, 10→0, 11→1) correctly maps r: r=1 when inputs match, r=0 otherwise.

## isqTrain/4390

- task_id: `isqTrain/4390`
- task_type: `output_prediction`
- category: `boolean_logic`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5505`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;

qbit q[3];

procedure main() {
    // Prepare state |101>
    X(q[0]);
    X(q[2]);
    // Bit-flip oracle: flip q[1] conditioned on q[0]=1 and q[2]=1
    ctrl ctrl X(q[0], q[2], q[1]);
    // Now state is |111>
    // Undo to demonstrate oracle is reversible
    ctrl ctrl X(q[0], q[2], q[1]);
    // Back to |101>
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts in the initial state |000>.
2. `X(q[0])` and `X(q[2])` flip the first and third qubits, changing the state to |101>.
3. The first `ctrl ctrl X` (Toffoli gate) flips target `q[1]` from 0 to 1 because controls `q[0]` and `q[2]` are in the |1> state, evolving the state to |111>.
4. The second `ctrl ctrl X` reverses the previous operation, flipping `q[1]` back to 0 and returning the state to |101>.
5. A final `X(q[0])` flips the first qubit from 1 to 0, resulting in the final quantum state |001>.

Predicted probability distribution: {|001>: 1.0}

### Reference answer

{'predicted_probs': {'001': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|001>) = 1.0000.'}

## isqTrain/3765

- task_id: `isqTrain/3765`
- task_type: `code_generation`
- category: `boolean_logic`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2582`

### Prompt

Write isQ code for the following quantum task: a Boolean function oracle f(x0,x1) = x0 AND (NOT x1) using the isQ `oracle bool[]` syntax. Use separate qbit arrays for input (p[2]) and output (r[1]). Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Apply oracle f(x₀,x₁) = x₀ AND (NOT x₁) to a superposition of all inputs and measure all qubits.

**Qubits:** 3 total — p[0], p[1] (input), r[0] (output). All measured.

**State evolution:**
1. Start: |000⟩
2. H(p[0]), H(p[1]) → ½(|000⟩ + |010⟩ + |100⟩ + |110⟩)
3. Oracle flips r[0] when x₀=1, x₁=0 (only |100⟩ → |101⟩)
4. Final state: ½(|000⟩ + |010⟩ + |101⟩ + |110⟩)

**Probabilities:** Four basis states each with amplitude ½, giving probability |½|² = 0.25 for |000⟩, |010⟩, |101⟩, and |110⟩.

## isqTrain/3761

- task_id: `isqTrain/3761`
- task_type: `code_generation`
- category: `boolean_logic`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `isq_syntax_oracle`, `superposition`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3290`

### Prompt

实现以下量子计算任务（使用isQ）：Build a 2-input OR oracle using `oracle` keyword. Apply to superposition inputs and measure all 3 qubits.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

1. Goal: Build a 2-input OR oracle and apply it to superposition inputs, measuring all 3 qubits.

2. Qubits: 3 qubits (q[0], q[1] are inputs, q[2] is the output/target)

3. The OR oracle is defined as `oracle or_oracle(2, 1) = [0, 1, 1, 1]`
   - This means for inputs |00>, |01>, |10>, |11>, the OR outputs are 0, 1, 1, 1 respectively.
   - The oracle truth table maps: |00>→0, |01>→1, |10>→1, |11>→1

4. Step-by-step evolution:

Initial state: |000>

After H on all 3 qubits:
|000> → (1/√8)(|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)

The OR oracle (2 inputs, 1 output) takes q[0], q[1] as inputs and q[2] as target. The oracle computes q[2] = q[2] XOR OR(q[0], q[1]).

Since q[2] starts in |+> state (superposition of |0> and |1>), the oracle will XOR the OR result into q[2].

For each basis state:
- |000>: OR(0,0)=0, q[2] XOR 0 = 0 → |000>
- |001>: OR(0,0)=0, q[2] XOR 0 = 1 → |001>
- |010>: OR(0,1)=1, q[2] XOR 1 = 1 → |011>
- |011>: OR(0,1)=1, q[2] XOR 1 = 0 → |010>
- |100>: OR(1,0)=1, q[2] XOR 1 = 1 → |101>
- |101>: OR(1,0)=1, q[2] XOR 1 = 0 → |100>
- |110>: OR(1,1)=1, q[2] XOR 1 = 1 → |111>
- |111>: OR(1,1)=1, q[2] XOR 1 = 0 → |110>

Wait, let me reconsider. The oracle truth table is [0, 1, 1, 1] for inputs indexed as 00, 01, 10, 11.

The oracle performs: |x>|y> → |x>|y XOR f(x)> where x is the 2 input qubits and y is the target qubit.

So after the oracle:
- |0,0,0> → |0,0,0 XOR 0> = |000>
- |0,0,1> → |0,0,1 XOR 0> = |001>
- |0,1,0> → |0,1,0 XOR 1> = |011>
- |0,1,1> → |0,1,1 XOR 1> = |010>
- |1,0,0> → |1,0,0 XOR 1> = |101>
- |1,0,1> → |1,0,1 XOR 1> = |100>
- |1,1,0> → |1,1,0 XOR 1> = |111>
- |1,1,1> → |1,1,1 XOR 1> = |110>

So the final state is:
(1/√8)(|000> + |001> + |011> + |010> + |101> + |100> + |111> + |110>)

Wait, this is still the same superposition of all 8 states! Let me reconsider...

Actually, when we apply H to all 3 qubits, we get:
(1/√8)(|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)

The oracle permutation just rearranges terms, but since all amplitudes are equal (1/√8), the state looks the same.

Hmm, but the expected measurement probabilities are {|000>: 0.25, |011>: 0.25, |101>: 0.25, |111>: 0.25}

That doesn't match what I calculated. Let me reconsider the problem.

Oh wait, I think I need to be more careful. Let me reconsider what happens when the target qubit starts in |

## isqTrain/4391

- task_id: `isqTrain/4391`
- task_type: `output_prediction`
- category: `boolean_logic`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5076`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;

qbit q[3];

procedure main() {
    // Prepare state |101>
    X(q[0]);
    X(q[2]);
    // Bit-flip oracle: flip q[1] conditioned on q[0]=1 and q[2]=1
    ctrl ctrl X(q[0], q[2], q[1]);
    // Now state is |111>
    // Undo to demonstrate oracle is reversible
    ctrl ctrl X(q[0], q[2], q[1]);
    // Back to |101>
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts in the initial state |000>.
2. `X(q[0])` and `X(q[2])` flip the first and third qubits, preparing the state |101>.
3. The first `ctrl ctrl X` (Toffoli) gate flips the target `q[1]` because both controls (`q[0]` and `q[2]`) are in the |1> state, changing the state to |111>.
4. The second `ctrl ctrl X` gate reverses the previous operation, returning the state to |101>.
5. The gate sequence `H(q[0])`, `Z(q[0])`, `H(q[0])` is mathematically equivalent to applying an X gate (since HZH = X).
6. Applying this X gate to `q[0]` flips it from |1> to |0>, resulting in the final state |001> before measurement.

Predicted probability distribution: {|001>: 1.0}

### Reference answer

{'predicted_probs': {'001': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|001>) = 1.0000.'}

## isqTrain/3766

- task_id: `isqTrain/3766`
- task_type: `code_generation`
- category: `boolean_logic`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3270`

### Prompt

Write isQ code for the following quantum task: Boolean oracle f(x0,x1) = x0 XOR x1 using isQ `oracle bool[]` syntax. Use qbit arrays p[2] and r[1]. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement and evaluate the XOR Boolean oracle f(x0,x1) = x0 ⊕ x1 using isQ's `oracle bool[]` syntax, putting inputs in superposition to observe all input-output correlations.

**Qubits:** 3 total — p[0], p[1] (inputs), r[0] (result) — all measured.

**State evolution:**
1. Initial: |000⟩
2. H(p[0]); H(p[1]): → (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 ⊗ |0⟩ = (|000⟩ + |010⟩ + |100⟩ + |110⟩)/2
3. Oracle f(p, r) computes XOR into r[0]: f(0,0)=0, f(0,1)=1, f(1,0)=1, f(1,1)=0
4. Final state: (|000⟩ + |011⟩ + |101⟩ + |110⟩)/2

**Probabilities:** Each basis state has amplitude 1/2, giving probability |1/2|² = 0.25 each. The result bit r[0] equals x0⊕x1 in every term, confirming the XOR function.

## isqTrain/3762

- task_id: `isqTrain/3762`
- task_type: `code_generation`
- category: `boolean_logic`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `isq_syntax_oracle`, `superposition`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3805`

### Prompt

Write isQ code for the following quantum task: Build a 3-input OR oracle using `oracle` keyword. Apply to superposition inputs and measure all 4 qubits.

### Chain-of-thought reasoning

Step 1: Understand the goal.
The user wants a 3-input OR oracle implemented using the `oracle` keyword in isQ, applied to a superposition of inputs, with all 4 qubits measured.

Step 2: Analyze the requirements.
- 3 input qubits and 1 output qubit, total 4 qubits.
- 3-input OR oracle truth table: output is 0 only if all inputs are 0, otherwise 1.
- Apply H to all 4 qubits. Input qubits go into superposition, output qubit goes into |-> state.
- Apply the oracle.
- Measure all 4 qubits.

Wait, the prompt says "Apply to superposition inputs and measure all 4 qubits."
But if I apply H to the output qubit, it goes to |+>.
If I want phase kickback, I should put the output qubit in |-> (by applying H, then X? No, X then H gives |->).
Wait, The circuit should H to all 4 qubits!
Let's trace:
Initial state: |0000>
After H on all 4: 1/2 * (|0> + |1>)^3 \otimes (|0> + |1>) = 1/sqrt(8) * sum_{x=0}^{7} |x> \otimes |+>
Oracle `or_oracle(q[0], q[1], q[2], q[3])` maps |x>|y> to |x>|y \oplus f(x)>.
Truth table for 3-input OR: f(000)=0, f(x)=1 for x \neq 000.
The truth table array is `[0, 1, 1, 1, 1, 1, 1, 1]`.
Wait, in isQ, the `oracle` keyword defines a unitary that performs |x>|y> -> |x>|y \oplus f(x)>.
If the last qubit is |+>, applying an XOR oracle does NOT apply phase kickback. It entangles the input and output:
|x>|0> + |x>|1> becomes |x>|f(x)> + |x>|1 \oplus f(x)> = |x>|0 \oplus f(x)> + |x>|1 \oplus f(x)> = |x> \otimes (|f(x)> + |1 \oplus f(x)>) = |x> \otimes |+>.
Wait! If the last qubit is |+>, applying CNOT (or any XOR operation) leaves it unchanged (|+> is an eigenstate of X).
Wait, The implementation is:
`for i in 0:3 { H(q[i]); }`
Then oracle.
If the output qubit is in |+>, the oracle just puts it in |+>. The state remains 1/sqrt(8) sum_{x} |x>|+>.
Then measuring all 4 qubits gives equal probability 1/16 for all states from 0000 to 1111?
Wait, if the state is 1/sqrt(8) sum_{x} |x>|+>, it's just an equal superposition of 16 states.
But the expected measurement probabilities given are:
`{|0000>: 0.125, |0011>: 0.125, |0101>: 0.125, |0111>: 0.125, |1001>: 0.125, |1011>: 0.125, |1101>: 0.125, |1111>: 0.125}`
Let's check these probabilities.
There are 8 states, each with probability 1/8 = 0.125.
Notice that for all these states, the last qubit is 1!
Wait, if the oracle maps |x>|y> to |x>|y \oplus f(x)>, and the initial state is |x>|+> = |x>|0> + |x>|1>.
Wait, if the initial state is |x>|0>, after oracle it is |x>|0 \oplus f(x)>.
If initial is |x>|1>, after oracle it is |x>|1 \oplus f(x)>.
So |x>|0> + |x>|1> becomes |x>|f(x)> + |x>|1 \oplus f(x)>.
For x=000: f(000)=0. State becomes |000>|0> + |000>|1> = |0000> + |0001>.
For x=001: f(001)=1. State becomes |001>|1> + |001>|0> = |0011> + |0010>.
Summing over all x, the total state is:
1/sqrt(8) ( |

## isqTrain/3767

- task_id: `isqTrain/3767`
- task_type: `code_generation`
- category: `boolean_logic`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1102`

### Prompt

Help me write isQ code that Boolean oracle f(x0,x1) = x0 NAND x1 using isQ `oracle bool[]` syntax. Use qbit arrays p[2] and r[1]. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a NAND oracle f(x0,x1)=!(x0&&x1), apply it with inputs in superposition, and measure all qubits.

2. **Qubits**: 3 qubits — p[0],p[1] (input array) and r[0] (output) — all measured.

3. **State evolution**:
   - Start: |000⟩
   - H(p[0]); H(p[1]) → (1/2)(|000⟩+|010⟩+|100⟩+|110⟩) (equal superposition over inputs, r=|0⟩)
   - Oracle f(p,r): flips r[0] when NAND(p[0],p[1])=1 (i.e., all cases except |11⟩):
     - |00⟩→1: |000⟩→|001⟩
     - |01⟩→1: |010⟩→|011⟩  
     - |10⟩→1: |100⟩→|101⟩
     - |11⟩→0: |110⟩→|110⟩ (no flip)
   - Final state: (1/2)(|001⟩+|011⟩+|101⟩+|110⟩)

4. **Probabilities**: Each of the four basis states has amplitude 1/2, giving probability |1/2|²=0.25 each. The bitstring ordering is (p[0],p[1],r[0]) based on measurement order, yielding {|001⟩:0.25, |011⟩:0.25, |101⟩:0.25, |110⟩:0.25}.

## isqTrain/3923

- task_id: `isqTrain/3923`
- task_type: `bug_fix`
- category: `boolean_logic`
- difficulty: `expert`
- concept_tags: `boolean_logic`, `isq_syntax_oracle`, `superposition`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4450`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```
import std;
// 4-input parity oracle: f(x) = XOR of all input bits
oracle parity_oracle(4, 1) = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0];
qbit q[5];

procedure main() {
    // Put input qubits in superposition
    for i in 0:4 {
        X(q[i]);
    }
    // Apply parity oracle
    parity_oracle(q[0], q[1], q[2], q[3], q[4]);
    // Measure all qubits
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
    M(q[4]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

The bug is that the code uses `X(q[i])` instead of `H(q[i])` to put the input qubits in superposition. The comment says "Put input qubits in superposition" but X gate doesn't create superposition - it just flips |0> to |1>. The H (Hadamard) gate is the correct gate to create superposition.

Let me verify the output:

With H gates on all 5 qubits:
- After H on all 5 qubits: equal superposition of all 32 states (1/sqrt(32) * sum of all |x> for x in {0,...,31})

The parity oracle f(x) = XOR of all 4 input bits. The oracle maps |x>|y> -> |x>|y ⊕ f(x)>.

For the 4 input qubits with parity:
- f(0000) = 0
- f(0001) = 1
- f(0010) = 1
- f(0011) = 0
- f(0100) = 1
- f(0101) = 0
- f(0110) = 0
- f(0111) = 1
- f(1000) = 1
- f(1001) = 0
- f(1010) = 0
- f(1011) = 1
- f(1100) = 0
- f(1101) = 1
- f(1110) = 1
- f(1111) = 0

So the oracle truth table [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0] matches.

After applying H to all 5 qubits, we get:
(1/4) * sum over all 16 input states |x> ⊗ (|0> + |1>)/sqrt(2)

After oracle: (1/4) * sum over all 16 input states |x> ⊗ (|0 ⊕ f(x)> + |1 ⊕ f(x)>)/sqrt(2)
= (1/4) * sum over all 16 input states |x> ⊗ (|f(x)> + |1⊕f(x)>)/sqrt(2)
= (1/4) * sum over all 16 input states |x> ⊗ (|0> + |1>)/sqrt(2)

Wait, that's just the same state. The oracle doesn't change the state when the target is in |+>.

Actually, let me think again. After H on all qubits:
State = (1/√16) Σ|x⟩ ⊗ (1/√2)(|0⟩ + |1⟩) for x in {0,1}^4

After oracle |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩:
= (1/√16) Σ|x⟩ ⊗ (1/√2)(|0 ⊕ f(x)⟩ + |1 ⊕ f(x)⟩)
= (1/√16) Σ|x⟩ ⊗ (1/√2)(|f(x)⟩ + |1⊕f(x)⟩)
= (1/√16) Σ|x⟩ ⊗ (1/√2)(|0⟩ + |1⟩)

So the state remains the same. The 5 qubits are all in |+⟩ states, meaning equal superposition of all 32 basis states, each with probability 1/32 = 0.03125.

But The predicted output probabilities of 0.0625 for 16 specific states and 0 for others. Let me look more carefully...

Expected states: |00000>, |00011>, |00101>, |00110>, |01001>, |01010>, |01100>, |01111>, |10001>, |10010>, |10100>, |10111>, |11000>, |11011>, |11101>, |11110>

These 16 states all have even parity of the last 4 bits when the first bit is 0... Wait, let me re-examine.

Looking at the bit patterns (5 bits, first measured = higher bit, so q[0] is MSB):
- 00000: parity of bits 1-4 = 0 (even)
- 00011: parity = 0 (even)
- 00101: parity = 0 (even)
- 00110: parity = 0 (even)
- 01001: parity = 0 (even)
- 01010: parity = 0 (even)
- 011
