# ISQ training COT RAG corpus: gate_synthesis shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4791

- task_id: `isqTrain/4791`
- task_type: `code_generation`
- category: `gate_synthesis`
- difficulty: `basic`
- concept_tags: `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `819`

### Prompt

Help me write isQ code that implements: defgate perm swap variant 1. Declare a global qbit array q of 2 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

The user wants to implement a quantum circuit with 2 qubits.
The goal is to use a custom gate `defgate MySwap1(2) = perm [0, 2, 1, 3];`.
Initial state preparation should likely be something like `X(q[1])` to get `|10>` (or `X(q[0])` to get `|01>` then swap to `|10>`).
Let's trace `X(q[1])` followed by `MySwap1(q[0], q[1])`.
Initial state: |00>
After X(q[1]): |10> (which is q[0]=1, q[1]=0. Wait, q[0] is higher bit or q[1] is higher bit? Usually |q[1]q[0]>. Let's assume standard notation. If q[0] is index 0, it's the rightmost bit. Wait, if it's isQ, q[0] is typically the lowest bit in the computational basis state representation, so |q[1]q[0]>.)
Let's see: |00> -> X(q[1]) -> |10>.
Permutation `[0, 2, 1, 3]` on basis states [00, 01, 10, 11]:
00 -> 00
01 -> 10
10 -> 01
11 -> 11
This swaps the two qubits!
So if we have |10>, applying the permutation gives |01>.
Wait, if initial is |01>, then X(q[0]) -> |01>.
Permutation [0, 2, 1, 3]: 01 -> 10.
If we measure both, the expected state is |10>, which has probability 1.0.
Ah, the prompt says: "Expected measurement probabilities: {|10>: 1.0}".
If we start with `X(q[0])`, state is |01> (where q[0] is the 1). After permutation it goes to |10>.
Wait, The implementation says:

If we do X(q[1]), the state is |10>. Applying a swap on |10> gives |01>.
Wait! Why does The implementation say `X(q[1])` and expects `|10>: 1.0`?
Let's understand the permutation.
Permutation is defined as an array mapping the *new* basis state index to the *old* basis state index, or vice versa?
`perm [0, 2, 1, 3]` means:
new 0 is old 0 -> |00> -> |00>
new 1 is old 2 -> |10> -> |01>
new 2 is old 1 -> |01> -> |10>
new 3 is old 3 -> |11> -> |11>
Let's check the swap matrix:
[[1, 0, 0, 0],
 [0, 0, 1, 0],
 [0, 1, 0, 0],
 [0, 0, 0, 1]]
This maps |00> to |00>, |01> to |10>, |10> to |01>, |11> to |11>.
If state is |01> (which is index 1), it maps to index 2 which is |10>.
If state is |10> (which is index 2), it maps to index 1 which is |01>.
But The implementation does `X(q[1])` making it |10> (assuming q[1] is index 2). Applying the gate maps |10> to |01>.
Wait, why does The implementation yield `{|10>: 1.0}`?
Is it possible that `q[0]` and `q[1]` are measured in a certain order, or `X(q[0])` was meant?
Wait, if `M(q[0]); M(q[1]);` then earlier measured qubit = higher bit.
`M(q[0])` is the first measurement. So `q[0]` is the higher bit.
If `q[0]` is the higher bit, then `q[0]q[1]`:
Initial `|00>`.
`X(q[1])` makes it `|01>`.
Permutation `[0, 2, 1, 3]` on the 2-qubit state.
Wait, if `q[0]q[1]` is the bit string, then `01` is q[0]=0, q[1]=1.
Index is $q_0 \cdot 2^1 + q_

## isqTrain/4793

- task_id: `isqTrain/4793`
- task_type: `code_generation`
- category: `gate_synthesis`
- difficulty: `basic`
- concept_tags: `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `1187`

### Prompt

Help me write isQ code that implements: defgate HH=I then X variant 3. Declare a global qbit array q of 1 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a custom Hadamard gate twice (yielding Identity) followed by an X gate to flip the state to |1>.
2. **Qubits**: 1 global qubit array `q[1]` is used, and `q[0]` is explicitly measured.
3. **Evolution**: 
   - Initialize `q[0]` to |0⟩.
   - Apply `MyH3` (H gate): |0⟩ → |+⟩.
   - Apply `MyH3` (H gate): |+⟩ → |0⟩.
   - Apply X gate: |0⟩ → |1⟩.
4. **Probabilities**: The final state is exactly |1⟩, resulting in a 100% probability of measuring 1.

## isqTrain/4796

- task_id: `isqTrain/4796`
- task_type: `code_generation`
- category: `gate_synthesis`
- difficulty: `basic`
- concept_tags: `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `4418`

### Prompt

请用isQ语言编写一个量子电路：implements: inv H self-inverse variant 2. Declare a global qbit array q of 1 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement `inv H` (self-inverse property) and apply gates to reach |1⟩ with certainty.
2. **Qubits**: 1 qubit `q[0]` is declared globally and measured.
3. **State evolution**:
   - Start: |0⟩
   - `inv H(q[0])` → H is self-inverse (H† = H), so inv H = H, giving |+⟩ = (|0⟩+|1⟩)/√2
   - `H(q[0])` → H|+⟩ = |0⟩ (H² = I)
   - `X(q[0])` → X|0⟩ = |1⟩
4. **Expected probabilities**: Final state is |1⟩, so measurement yields {|1⟩: 1.0}.

## isqTrain/4795

- task_id: `isqTrain/4795`
- task_type: `code_generation`
- category: `gate_synthesis`
- difficulty: `basic`
- concept_tags: `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `567`

### Prompt

Write an isQ program that implements: defgate Toffoli perm variant 5. Declare a global qbit array q of 3 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a custom Toffoli gate via permutation [0,1,2,3,4,5,7,6] and verify it flips the target when both controls are |1⟩.
Three qubits (q[0], q[1], q[2]) are used and all are measured.
Initial state: |000⟩ → After X(q[0]): |100⟩ → After X(q[1]): |110⟩.
The permutation swaps basis states |6⟩=|110⟩ and |7⟩=|111⟩ while leaving others unchanged, equivalent to Toffoli: MyTof5 maps |110⟩ → |111⟩.
Final state is |111⟩, so measurement yields bitstring 111 with probability 1.0.

## isqTrain/4794

- task_id: `isqTrain/4794`
- task_type: `code_generation`
- category: `gate_synthesis`
- difficulty: `basic`
- concept_tags: `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `4135`

### Prompt

Create an isQ quantum circuit that implements: defgate phase + X + H variant 4. Declare a global qbit array q of 1 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Apply X gate, then a custom phase gate (S gate = [1,0;0,i]), then H to a single qubit and measure.

2. **Qubits**: 1 qubit `q[0]`, which is measured.

3. **State evolution**:
   - Start: |0⟩
   - After X: |1⟩
   - After MyS4 (phase gate): i|1⟩ (multiplies |1⟩ amplitude by i)
   - After H: i·(1/√2)(|0⟩ - |1⟩) = (i/√2)|0⟩ - (i/√2)|1⟩

4. **Probabilities**: |i/√2|² = 0.5 for both |0⟩ and |1⟩, giving equal superposition {|0⟩: 0.5, |1⟩: 0.5}.

## isqTrain/4769

- task_id: `isqTrain/4769`
- task_type: `code_generation`
- category: `gate_synthesis`
- difficulty: `basic`
- concept_tags: `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1891`

### Prompt

Write isQ code for the following quantum task: implements: procedure call variant 1 on 3 qubits. Declare a global qbit array q of 3 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a procedure call variant that applies H to q[0] and X to q[2] via a helper procedure, then measures all qubits.
2. **Qubits**: 3 global qubits q[0], q[1], q[2], all measured.
3. **State evolution**:
   - Initial: |000⟩
   - H(q[0]): |000⟩ → (1/√2)(|000⟩ + |100⟩)
   - X(q[2]): (1/√2)(|000⟩ + |100⟩) → (1/√2)(|001⟩ + |101⟩)
4. **Probabilities**: Each basis state has amplitude 1/√2, yielding P(|001⟩) = 0.5 and P(|101⟩) = 0.5, matching the predicted output.

## isqTrain/4768

- task_id: `isqTrain/4768`
- task_type: `code_generation`
- category: `gate_synthesis`
- difficulty: `basic`
- concept_tags: `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4613`

### Prompt

帮我写一个isQ程序：implements: procedure call variant 0 on 2 qubits. Declare a global qbit array q of 2 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply X to qubit 0 and H to qubit 1 via a helper procedure, then measure both qubits.
2. Uses 2 global qubits q[0] and q[1]; both are measured.
3. Initial state |00⟩ → X(q[0]) → |10⟩ → H(q[1]) → (|10⟩ + |11⟩)/√2.
4. Measuring both qubits yields |10⟩ or |11⟩ each with probability 0.5.

## isqTrain/4792

- task_id: `isqTrain/4792`
- task_type: `code_generation`
- category: `gate_synthesis`
- difficulty: `basic`
- concept_tags: `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `1392`

### Prompt

请用isQ语言编写一个量子电路：implements: unit deriving gate + inv variant 2. Declare a global qbit array q of 2 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. The circuit aims to demonstrate a unitary procedure defined with `deriving gate` and revert its action using the `inv` modifier.
2. It requires 2 global qubits, `q[0]` and `q[1]`, both of which are explicitly measured.
3. Starting in |00>, `entangle2` applies an H gate to `q[0]` followed by a CNOT, creating the Bell state 1/sqrt(2)|00> + 1/sqrt(2)|11>. Applying `inv entangle2` exactly uncomputes this operation (acting as CNOT then H), deterministically returning the system to |00>.
4. Because the final quantum state is exactly |00>, the measurements yield '00' with a 100% probability.

## isqTrain/4797

- task_id: `isqTrain/4797`
- task_type: `code_generation`
- category: `gate_synthesis`
- difficulty: `basic`
- concept_tags: `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `312`

### Prompt

用isQ实现implements: unit deriving gate + inv variant 3. Declare a global qbit array q of 2 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1.  **Goal:** The circuit demonstrates the `deriving gate` feature by applying a unitary transformation and then its exact inverse to return to the initial state.
2.  **Qubits:** A global array of 2 qubits `q[2]` is used, and both qubits are explicitly measured.
3.  **State Evolution:**
    *   Initialize to |00>.
    *   `prep3(q[0], q[1])`: Applies H to q[0] creating |+0>, then CNOT creates the Bell state (|00> + |11>)/√2.
    *   `inv prep3(q[0], q[1])`: Automatically inverts the gate sequence to CNOT then H.
    *   CNOT disentangles the state to |+0>, and H returns it to |00>.
4.  **Probabilities:** The final state is exactly |00>, so measurement yields the bitstring '00' with a probability of 1.0.

## isqTrain/4790

- task_id: `isqTrain/4790`
- task_type: `code_generation`
- category: `gate_synthesis`
- difficulty: `basic`
- concept_tags: `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `1211`

### Prompt

Write isQ code for the following quantum task: implements: defgate matrix variant 0. Declare a global qbit array q of 1 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Define a custom gate using `defgate` with matrix representation and apply it to a single qubit.
2. One qubit (`q[0]`) is used and measured.
3. State evolution:
   - Initial state: |0⟩
   - Apply `MyGate0` (matrix `[1, 0; 0, -1]`, which is the Z gate): Z|0⟩ = 1·|0⟩ + 0·|1⟩ = |0⟩
4. The final state is |0⟩, so measurement yields |0⟩ with probability 1.0.
