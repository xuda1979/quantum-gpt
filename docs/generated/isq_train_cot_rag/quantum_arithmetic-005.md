# ISQ training COT RAG corpus: quantum_arithmetic shard 5

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4033

- task_id: `isqTrain/4033`
- task_type: `bug_fix`
- category: `quantum_arithmetic`
- difficulty: `expert`
- concept_tags: `reversible_computing`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4848`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```
import std;
// 2-bit quantum adder: 0 + 2 = 2
// a[0..1] = A, b[0..1] = B, s[0..2] = Sum
// Using ripple-carry approach
qbit a[2];  // input A
qbit b[2];  // input B
qbit c[3];  // carry chain + sum output

procedure main() {
    // Prepare A = 0
    // a[0] = 0
    // a[1] = 0
    // Prepare B = 2
    X(b[0]);
    // b[1] = 0
    // Bit 0: half adder a[1] + b[1]
    Toffoli(a[1], b[1], c[1]);
    CNOT(a[1], b[1]);
    // Bit 1: full adder a[0] + b[0] + c[1]
    Toffoli(a[0], b[0], c[0]);
    // BUG: missing gate here
    Toffoli(b[0], c[1], c[0]);
    CNOT(c[1], b[0]);
    // b now holds sum bits, c[0] holds carry-out
    // Measure: a (unchanged), b (sum low bits), c[0] (carry)
    M(a[0]); M(a[1]); M(b[0]); M(b[1]); M(c[0]); M(c[1]); M(c[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

Let me analyze this quantum adder circuit carefully.

The task is to implement a 2-bit quantum adder computing 0 + 2 = 2.

**Inputs:**
- A = 0: a[0] = |0⟩, a[1] = |0⟩
- B = 2: In binary, 2 = 10, so b[0] = 0 (LSB), b[1] = 1 (MSB)

Wait, let me check the encoding. B = 2 in binary is "10". If b[0] is the LSB, then b[0] = 0 and b[1] = 1. But the code says `X(b[0])` which sets b[0] = 1, and b[1] = 0. That would be B = 1, not B = 2.

Hmm, let me reconsider the bit ordering. Maybe in this implementation:
- b[0] is the MSB and b[1] is the LSB

So B = 2 = binary 10:
- b[0] = 1 (MSB), b[1] = 0 (LSB)

This matches `X(b[0])`.

A = 0 = binary 00:
- a[0] = 0, a[1] = 0

Now let me trace through the circuit:

**Bit 0 (half adder): a[1] + b[1] = 0 + 0**
- Initial: a[1]=|0⟩, b[1]=|0⟩, c[1]=|0⟩
- Toffoli(a[1], b[1], c[1]): Both controls are |0⟩, so c[1] stays |0⟩
- CNOT(a[1], b[1]): Control a[1]=|0⟩, b[1] stays |0⟩
- Result: c[1] = 0 (carry = 0), b[1] = 0 (sum = 0)

**Bit 1 (full adder): a[0] + b[0] + c[1] = 0 + 1 + 0 = 1**
- Initial: a[0]=|0⟩, b[0]=|1⟩, c[1]=|0⟩, c[0]=|0⟩
- Toffoli(a[0], b[0], c[0]): a[0]=|0⟩, so c[0] stays |0⟩
- **Missing gate: CNOT(a[0], b[0])**: a[0]=|0⟩, b[0] stays |1⟩
- Toffoli(b[0], c[1], c[0]): b[0]=|1⟩, c[1]=|0⟩, so c[0] stays |0⟩
- CNOT(c[1], b[0]): c[1]=|0⟩, b[0] stays |1⟩
- Result: c[0] = 0 (carry-out = 0), b[0] = 1 (sum = 1)

Final state:
- a[0] = 0, a[1] = 0, b[0] = 1, b[1] = 0, c[0] = 0, c[1] = 0, c[2] = 0

In the measurement bitstring, earlier measured qubit = higher bit:
M(a[0]) = 0 (bit 6)
M(a[1]) = 0 (bit 5)
M(b[0]) = 1 (bit 4)
M(b[1]) = 0 (bit 3)
M(c[0]) = 0 (bit 2)
M(c[1]) = 0 (bit 1)
M(c[2]) = 0 (bit 0)

Bitstring: 0010000 in binary = 16 in decimal.

The predicted output {|0010000⟩: 1.0}, which matches!

Now let me verify what happens WITHOUT the missing gate CNOT(a[0], b[0]):

Without CNOT(a[0], b[0]):
- After Toffoli(a[0], b[0], c[0]): c[0] = 0
- b[0] is still |1⟩ (no CNOT to potentially change it)
- Toffoli(b[0], c[1], c[0]): c[0] stays 0
- CNOT(c[1], b[0]): c[1] = 0, b[0] stays 1

Actually, in this specific case (a[0]=0), the CNOT(a[0], b[0])

## isqTrain/3697

- task_id: `isqTrain/3697`
- task_type: `code_generation`
- category: `quantum_arithmetic`
- difficulty: `expert`
- concept_tags: `reversible_computing`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5145`

### Prompt

实现以下量子计算任务（使用isQ）：a 2-bit quantum ripple-carry adder computing 0 + 1 = 1. Use registers a[2], b[2], c[3] where the sum appears in b[] (low bits) and c[0] (carry-out). Use Toffoli and CNOT gates for the ripple-carry logic. Measure all 7 qubits.

### Chain-of-thought reasoning

Let me trace through this 2-bit quantum ripple-carry adder step by step.

Initial state: |0000000> for qubits a[0], a[1], b[0], b[1], c[0], c[1], c[2]

1. Prepare inputs: a = 00, b = 10 (representing 1 in bit-reversed form: b[1] is high bit)
   - Wait, let me reconsider. For a 2-bit number, if b[1] is the more significant bit and b[0] is the less significant bit, then b = 1 means b[1]=0, b[0]=1.

   But looking at the code:
   - b[0] = 0 (no gate applied)
   - b[1] gets X gate, so b[1] = 1
   
   Hmm, this seems like b = 2 (binary 10, with b[1] as high bit) or b = 1 (binary 10, with b[1] as low bit).

Let me re-examine the code more carefully.

The code says:
- a[0] = 0, a[1] = 0 (so a = 0)
- b[0] = 0 (no X gate), b[1] gets X gate (so b[1] = 1)

Then the addition logic:
- Bit 0: half adder on a[1] + b[1]
  - Toffoli(a[1], b[1], c[1]): carry
  - CNOT(a[1], b[1]): sum in b[1]

- Bit 1: full adder on a[0] + b[0] + c[1]
  - Toffoli(a[0], b[0], c[0])
  - CNOT(a[0], b[0])
  - Toffoli(b[0], c[1], c[0])
  - CNOT(c[1], b[0])

Wait, I think there might be a convention issue. Let me think about this differently.

In many quantum adder implementations, the bit ordering is such that:
- a[1] and b[1] are the least significant bits (bit 0)
- a[0] and b[0] are the most significant bits (bit 1)

So if we want to compute 0 + 1:
- a = 00 (a[1] = 0, a[0] = 0), representing 0
- b = 01 (b[1] = 1, b[0] = 0), representing 1

This matches the code: X(b[1]) sets the LSB of b to 1.

Let me trace through:

Initial state: |0⟩ for all 7 qubits
Order: a[0], a[1], b[0], b[1], c[0], c[1], c[2]

After X(b[1]):
State = |0010000⟩ (a[0]=0, a[1]=0, b[0]=0, b[1]=1, c[0]=0, c[1]=0, c[2]=0)

Bit 0 (LSB): half adder on a[1] and b[1]
- Toffoli(a[1], b[1], c[1]): Since a[1]=0, no effect. c[1] stays 0.
- CNOT(a[1], b[1]): Since a[1]=0, no effect. b[1] stays 1.

State still = |0010000⟩

Bit 1 (MSB): full adder on a[0], b[0], c[1]
- Toffoli(a[0], b[0], c[0]): Since a[0]=0 and b[0]=0, no effect. c[0] stays 0.
- CNOT(a[0], b[0]): Since a[0]=0, no effect. b[0] stays 0.
- Toffoli(b[0], c[1], c[0]): Since b[0]=0 and c[1]=0, no effect. c[0] stays 0.
- CNOT(c[1], b[0]): Since c[1]=0, no effect. b[0] stays 0.

Final state: |0010000⟩

This represents:
- a = 00 (input A = 0)
- b = 01 (sum low bits = 1)
- c = 000 (c[0] = carry out = 0)

The result 0 + 1 = 1 is stored in b (with b[1]=1 being the

## isqTrain/3706

- task_id: `isqTrain/3706`
- task_type: `code_generation`
- category: `quantum_arithmetic`
- difficulty: `expert`
- concept_tags: `reversible_computing`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4746`

### Prompt

Implement the following in isQ: a 2-bit quantum ripple-carry adder computing 2 + 3 = 5. Use registers a[2], b[2], c[3] where the sum appears in b[] (low bits) and c[0] (carry-out). Use Toffoli and CNOT gates for the ripple-carry logic. Measure all 7 qubits.

### Chain-of-thought reasoning

Let me analyze this 2-bit quantum ripple-carry adder circuit step by step.

**Goal**: Implement a 2-bit quantum adder computing 2 + 3 = 5 using ripple-carry logic.

**Qubits**: 7 qubits total (a[0], a[1], b[0], b[1], c[0], c[1], c[2])

**Initial state**: |0000000⟩ (all qubits in |0⟩)

**Step-by-step evolution**:

1. **Prepare A = 2** (binary 10):
   - X(a[0]) → a[0] = |1⟩
   - a[1] remains |0⟩
   - So a represents binary 10 = 2 (a[0] is LSB? Let me check... actually looking at the code comments, it seems a[0] corresponds to bit 0 and a[1] to bit 1)
   
   Wait, let me re-read the code. The comment says "Prepare A = 2" and then X(a[0]) with a[1] = 0. If a[0] is the LSB, then a = binary 10 = 2. That makes sense.

2. **Prepare B = 3** (binary 11):
   - X(b[0]) and X(b[1])
   - b = binary 11 = 3

3. **Bit 1 (MSB) half adder**: a[1] + b[1]
   - Toffoli(a[1], b[1], c[1]): Since a[1]=0, b[1]=1, Toffoli doesn't trigger. c[1] = 0
   - CNOT(a[1], b[1]): Since a[1]=0, no flip. b[1] remains 1

4. **Bit 0 (LSB) full adder**: a[0] + b[0] + c[1]
   - Toffoli(a[0], b[0], c[0]): Since a[0]=1, b[0]=1, both controls are |1⟩, so c[0] flips from 0 to 1
   - CNOT(a[0], b[0]): Since a[0]=1, b[0] flips from 1 to 0
   - Toffoli(b[0], c[1], c[0]): b[0]=0, c[1]=0, doesn't trigger. c[0] remains 1
   - CNOT(c[1], b[0]): c[1]=0, no flip. b[0] remains 0

**Final state**:
- a[0] = 1, a[1] = 0 (A unchanged = 2)
- b[0] = 0, b[1] = 1 (sum low bits)
- c[0] = 1 (carry-out), c[1] = 0, c[2] = 0

The sum is: c[0] b[1] b[0] = 1 1 0 = 6? That doesn't match 5...

Wait, let me reconsider. Let me trace more carefully.

Actually, I think there might be a different bit ordering. Let me re-trace:

A = 2 = binary 10, so a[0]=0 (LSB), a[1]=1 (MSB)? But the code does X(a[0]) and says a[1]=0...

Hmm, if a[0]=1 and a[1]=0, then if a[0] is MSB and a[1] is LSB, A = 10 (binary) = 2. That could work.

B = 3 = binary 11, b[0]=1, b[1]=1.

Let me trace again with this interpretation where a[0] and b[0] are the higher-order bits:

Actually, let me just trace the gate operations carefully:

Initial: |0000000⟩

After X(a[0]): |1000000⟩ (bit position 0 = a[0] = 1)
After X(b[0]): |1001000⟩ (bit position 3 = b[0] = 1)
After X(b[1]): |1001100⟩ (bit position 4 = b[1] = 1)

Now the computational part:

Toffoli(a[1], b[1], c[1]): a[1]=0 (pos 1), b[1]=1 (pos 4). Since a[1]=0, no action. State unchanged.

CNOT(a[1], b[1]): a[1]=0, no flip. State unchanged.

Toffoli

## isqTrain/3698

- task_id: `isqTrain/3698`
- task_type: `code_generation`
- category: `quantum_arithmetic`
- difficulty: `expert`
- concept_tags: `reversible_computing`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `41`

### Prompt

帮我写一个isQ程序：a 2-bit quantum ripple-carry adder computing 0 + 2 = 2. Use registers a[2], b[2], c[3] where the sum appears in b[] (low bits) and c[0] (carry-out). Use Toffoli and CNOT gates for the ripple-carry logic. Measure all 7 qubits.

### Chain-of-thought reasoning

Let me analyze this quantum ripple-carry adder circuit.

**Goal**: Implement a 2-bit quantum ripple-carry adder computing 0 + 2 = 2, with result appearing in b[] (low bits) and c[0] (carry-out).

**Qubits**: 7 total - a[2], b[2], c[3], all measured.

**Initial state**: |0000000⟩ (all zeros)

**State evolution**:

1. **Initial state**: |0000000⟩ (a[1]a[0]b[1]b[0]c[2]c[1]c[0])

Wait, let me re-read The implementation carefully.

The input is A=0, B=2. In binary:
- A = 0 = 00 in 2-bit binary
- B = 2 = 10 in 2-bit binary

Looking at the code:
- a[0] = 0, a[1] = 0 (A = 0)
- X(b[0]) is applied, so b[0] = 1, b[1] = 0

Wait, this seems odd. B = 2 in binary is 10, so the LSB is 0 and MSB is 1. But the code does X(b[0]) which makes b[0] = 1.

Let me re-read... The comment says "Prepare B = 2" and then "X(b[0])". Hmm, maybe the indexing is different.

Actually wait, let me re-read the circuit logic:

So bit 0 uses a[1] and b[1]? That's interesting - the bit ordering seems to have a[1] and b[1] as the least significant bits.

So:
- a[1], b[1] are bit 0 (LSB)
- a[0], b[0] are bit 1 (MSB)

With A = 0: a[1] = 0, a[0] = 0
With B = 2 = 10: b[1] = 0 (LSB), b[0] = 1 (MSB)

So X(b[0]) gives b[0] = 1, making B = 2. That makes sense!

Initial state: |a[0]a[1]b[0]b[1]c[0]c[1]c[2]⟩ = |0000000⟩

After X(b[0]): |0,0,1,0,0,0,0⟩ = |0010000⟩

Now the adder:

Bit 0 (half adder): a[1] + b[1]
- a[1] = 0, b[1] = 0
- Toffoli(a[1], b[1], c[1]): both controls are 0, so c[1] stays 0
- CNOT(a[1], b[1]): control is 0, so b[1] stays 0

State: |0,0,1,0,0,0,0⟩

Bit 1 (full adder): a[0] + b[0] + c[1]
- a[0] = 0, b[0] = 1, c[1] = 0
- Toffoli(a[0], b[0], c[0]): a[0] = 0, so c[0] stays 0
- CNOT(a[0], b[0]): a[0] = 0, so b[0] stays 1
- Toffoli(b[0], c[1], c[0]): c[1] = 0, so c[0] stays 0
- CNOT(c[1], b[0]): c[1] = 0, so b[0] stays 1

Final state: |0,0,1,0,0,0,0⟩ = |0010000⟩

The sum is: c[0] = 0 (carry-out), b[0] = 1, b[1] = 0, which represents 0*4 + 1*2 + 0*1 = 2. ✓

Expected measurement: {|0010000⟩: 1.0}

The measurement order is: a[0], a[1], b[0], b[1], c[0], c[1], c[2]

So the bitstring is: a[0]a[1]b[0

## isqTrain/3951

- task_id: `isqTrain/3951`
- task_type: `bug_fix`
- category: `quantum_arithmetic`
- difficulty: `expert`
- concept_tags: `reversible_computing`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5144`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```
import std;
// 2-bit quantum adder: 3 + 2 = 5
// a[0..1] = A, b[0..1] = B, s[0..2] = Sum
// Using ripple-carry approach
qbit a[2];  // input A
qbit b[2];  // input B
qbit c[3];  // carry chain + sum output

procedure main() {
    // Prepare A = 3
    X(a[0]);
    X(a[1]);
    // Prepare B = 2
    X(b[0]);
    // b[1] = 0
    // Bit 0: half adder a[1] + b[1]
    Toffoli(a[1], b[1], c[1]);
    CNOT(a[1], b[1]);
    // Bit 1: full adder a[0] + b[0] + c[1]
    Toffoli(a[0], b[0], c[0]);
    CNOS(a[0], b[0]);
    Toffoli(b[0], c[1], c[0]);
    CNOT(c[1], b[0]);
    // b now holds sum bits, c[0] holds carry-out
    // Measure: a (unchanged), b (sum low bits), c[0] (carry)
    M(a[0]); M(a[1]); M(b[0]); M(b[1]); M(c[0]); M(c[1]); M(c[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

Let me analyze the buggy code and the fix.

The buggy code has `CNOS(a[0], b[0]);` on one line, which is a typo - it should be `CNOT(a[0], b[0]);`.

Let me verify the circuit correctness:

Initial state: a[0]=|1⟩, a[1]=|1⟩, b[0]=|1⟩, b[1]=|0⟩, all c=|0⟩
So A = 3 (a[0]=1, a[1]=1), B = 2 (b[0]=1, b[1]=0)

Wait, let me check the bit ordering. If A = 3, and a[0] and a[1] are both |1⟩:
- If a[0] is LSB: A = 1 + 2 = 3 ✓
- B = 2: b[0] = 1, b[1] = 0 → B = 1 + 0 = 1... that's not 2.

Wait, let me reconsider. B = 2 means b[1] = 1, b[0] = 0. But the code says:

Hmm, but looking at the code: X(b[0]) sets b[0]=|1⟩, and b[1] is left as |0⟩. So if b[0] is LSB, B = 1, not 2.

But wait, looking at the comments: "Bit 0: half adder a[1] + b[1]" and "Bit 1: full adder a[0] + b[0] + c[1]". This suggests a[0] is MSB and a[1] is LSB.

So A: a[1] is bit 0 (LSB), a[0] is bit 1 (MSB)
- a[1] = 1, a[0] = 1 → A = 1*1 + 1*2 = 3 ✓

B: b[1] is bit 0 (LSB), b[0] is bit 1 (MSB)  
- b[1] = 0, b[0] = 1 → B = 0*1 + 1*2 = 2 ✓

Now the half adder for bit 0 (a[1] + b[1]):
- a[1] = 1, b[1] = 0
- Toffoli(a[1], b[1], c[1]): both controls need to be 1. a[1]=1 but b[1]=0, so c[1] stays 0.
- CNOT(a[1], b[1]): control a[1]=1, so b[1] flips to 1.

After bit 0: a[1]=1, b[1]=1, c[1]=0

Full adder for bit 1 (a[0] + b[0] + c[1]):
- a[0] = 1, b[0] = 1, c[1] = 0
- Toffoli(a[0], b[0], c[0]): both controls are 1, so c[0] flips to 1.
- CNOT(a[0], b[0]): control a[0]=1, so b[0] flips to 0.
- Toffoli(b[0], c[1], c[0]): b[0]=0, c[1]=0, so c[0] stays 1.
- CNOT(c[1], b[0]): control c[1]=0, so b[0] stays 0.

After bit 1: a[0]=1, b[0]=0, c[0]=1

So result: b[1]=1 (bit 0), b[0]=0 (bit 1), c[0]=1 (carry)
Sum = 1*1 + 0*2 + 1*4 = 5 ✓

Expected measurement: |1101100⟩
Bit ordering: earlier measured = higher bit
M(a[0])=1, M(a[1])=1, M(b[0])=0, M(b[1])=1, M(c[0])=1, M(c[1])=0, M(c[2])=0
Binary: 1101100 = 108... wait let me check.

Actually, "earlier measured qubit = higher bit" means:
- a[0] is bit 6 (MSB)
- a[1] is bit 5
- b[0] is

## isqTrain/4588

- task_id: `isqTrain/4588`
- task_type: `output_prediction`
- category: `quantum_arithmetic`
- difficulty: `expert`
- concept_tags: `qft_based_arithmetic`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `961`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;

qbit q[5];

procedure main() {
    
    X(q[1]);
    
    X(q[4]);
    
    H(q[2]);
    ctrl Rz(3.14159265358979 / 2, q[3], q[2]);
    ctrl Rz(3.14159265358979 / 4, q[4], q[2]);
    H(q[3]);
    ctrl Rz(3.14159265358979 / 2, q[4], q[3]);
    H(q[4]);
    
    
    ctrl Rz(3.14159265358979, q[1], q[4]);
    ctrl Rz(3.14159265358979 / 2, q[1], q[3]);
    ctrl Rz(3.14159265358979 / 4, q[1], q[2]);
    
    ctrl Rz(3.14159265358979, q[0], q[3]);
    ctrl Rz(3.14159265358979 / 2, q[0], q[2]);
    
    H(q[4]);
    ctrl Rz(-3.14159265358979 / 2, q[4], q[3]);
    H(q[3]);
    ctrl Rz(-3.14159265358979 / 4, q[4], q[2]);
    ctrl Rz(-3.14159265358979 / 2, q[3], q[2]);
    H(q[2]);
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[2]); M(q[3]); M(q[4]);
}
```

### Chain-of-thought reasoning

Let me analyze this quantum circuit step by step.

The circuit involves 5 qubits q[0] through q[4], and measures q[2], q[3], and q[4].

Let me trace through the operations:

Initial state: |00000⟩

After X(q[1]): |00010⟩ (q[1] flipped)
After X(q[4]): |10010⟩ (q[4] flipped, using bit ordering q[4]q[3]q[2]q[1]q[0])

Wait, let me be more careful with the ordering. Let me use |q[4]q[3]q[2]q[1]q[0]⟩ notation.

Initial state: |00000⟩

After X(q[1]): |00010⟩
After X(q[4]): |10010⟩

Now the QFT-like operations begin. This looks like it's computing the QFT on qubits 2, 3, 4 of the state |100⟩ encoded in those positions, then doing something with q[1] and q[0].

Actually, let me re-read more carefully. 

The circuit structure:
1. X(q[1]) - prepares q[1] in |1⟩
2. X(q[4]) - prepares q[4] in |1⟩
3. QFT on q[2], q[3], q[4] (forward)
4. Phase rotations controlled by q[1]
5. Phase rotations controlled by q[0]
6. Inverse QFT on q[2], q[3], q[4]
7. X(q[0]) - flip q[0] before measurement
8. Measure q[2], q[3], q[4]

Let me trace this more carefully.

State after steps 1-2: |q[4]=1, q[3]=0, q[2]=0, q[1]=1, q[0]=0⟩ = |10010⟩ (in q4q3q2q1q0 order)

Now the QFT forward on q[2], q[3], q[4]:

The QFT on 3 qubits transforms the computational basis. Let me think of q[2], q[3], q[4] as encoding a 3-bit value with q[2] as bit 0 (least significant), q[3] as bit 1, q[4] as bit 2.

Wait, actually in the standard QFT, the output is bit-reversed. Let me just trace through the gates.

State before QFT forward: q[4]=1, q[2]=0, q[3]=0, q[1]=1, q[0]=0

The QFT forward section:
- H(q[2])
- ctrl Rz(π/2, q[3], q[2])  -- controlled phase when q[3]=1
- ctrl Rz(π/4, q[4], q[2])  -- controlled phase when q[4]=1
- H(q[3])
- ctrl Rz(π/2, q[4], q[3])  -- controlled phase when q[4]=1
- H(q[4])

Since q[2]=0 and q[3]=0 initially, and q[4]=1:

After H(q[2]): q[2] = (|0⟩ + |1⟩)/√2, so state is (1/√2)(|1000...0...10⟩ + |100...1...10⟩) where the ...1... is at q[2] position.

Actually, let me think about this differently. The controlled Rz gates only apply phases when the control is |1⟩. Since only q[4] is |1⟩ initially:

- H(q[2]): creates superposition on q[2]
- ctrl Rz(π/2, q[3], q[2]): q[3]=0, so no effect
- ctrl Rz(π/4, q[4], q[2]): q[4]=1, so this applies Rz(π/4) to q[2], which multiplies |1⟩ component by e^{iπ/8}
- H(q[3]): creates superposition on q[3]
- ctrl Rz(π/2, q[4], q[3]): q[4]=1, so applies Rz(π/2) to q[3], multiplies |1⟩ by e^{iπ/4}
- H(q[4]): creates superposition on q[4]

This is getting complicated. Let me think about this circuit at a higher level.

This circuit looks like it implements Quantum Phase Estimation (QPE). 

In QPE:
1. Prepare an eigenstate

### Reference answer

{'predicted_probs': {'00010': 1.0}, 'explanation': 'This isQ program operates on 5 qubit(s). The measurement probability distribution is: P(|00010>) = 1.0000.'}

## isqTrain/4171

- task_id: `isqTrain/4171`
- task_type: `output_prediction`
- category: `quantum_arithmetic`
- difficulty: `expert`
- concept_tags: `reversible_computing`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4037`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit a[2];
qbit b[2];
qbit c[3];

procedure main() {
    X(b[0]);
    X(b[1]);
    Toffoli(a[1], b[1], c[1]);
    CNOT(a[1], b[1]);
    Toffoli(a[0], b[0], c[0]);
    CNOT(a[0], b[0]);
    Toffoli(b[0], c[1], c[0]);
    CNOT(c[1], b[0]);
    M(a[0]); M(a[1]); M(b[0]); M(b[1]); M(c[0]); M(c[1]); M(c[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Predict the measurement output of an isQ quantum circuit.
    *   **Input:** isQ circuit implementing an adder-like circuit (Ripple Carry Adder / Cuccaro Adder).
    *   **Output constraints:** Concise (3-15 lines), precise, step-by-step reasoning using Dirac notation. Start with "## Circuit Analysis", NO isQ code blocks, end with the predicted probability distribution.

2.  **Analyze the Circuit:**
    *   Initial state: |0000000> (a[0], a[1], b[0], b[1], c[0], c[1], c[2])
    *   `X(b[0])`: b[0] becomes 1. State: |0001000>
    *   `X(b[1])`: b[1] becomes 1. State: |0011000>
    *   (Note: Quantum state ordering depends on standard conventions, but tracking individual qubits is easier: a=|00>, b=|11>, c=|000>)
    *   `Toffoli(a[1], b[1], c[1])`: If a[1]=1 and b[1]=1, flip c[1]. a[1]=0, b[1]=1. No flip. c[1]=0.
    *   `CNOT(a[1], b[1])`: If a[1]=1, flip b[1]. a[1]=0. No flip. b[1]=1.
    *   `Toffoli(a[0], b[0], c[0])`: If a[0]=1 and b[0]=1, flip c[0]. a[0]=0, b[0]=1. No flip. c[0]=0.
    *   `CNOT(a[0], b[0])`: If a[0]=1, flip b[0]. a[0]=0. No flip. b[0]=1.
    *   `Toffoli(b[0], c[1], c[0])`: If b[0]=1 and c[1]=1, flip c[0]. b[0]=1, c[1]=0. No flip. c[0]=0.
    *   `CNOT(c[1], b[0])`: If c[1]=1, flip b[0]. c[1]=0. No flip. b[0]=1.
    *   Measurements: a[0], a[1], b[0], b[1], c[0], c[1], c[2]

3.  **Evaluate the logic:**
    *   This is the standard Cuccaro ripple-carry adder.
    *   Inputs: `a` = 0 (00 in binary), `b` = 3 (11 in binary). Carry-in `c[0]` = 0.
    *   The adder computes `a + b`.
    *   Result should be 0 + 3 = 3 (011 in binary).
    *   Wait, let's carefully trace Cuccaro adder truth tables:
        *   Input: a=00, b=11
        *   Outputs: b will contain sum bits? No, in Cuccaro, b gets XORed.
        *   Let's just track the qubits literally.
        *   Initial:
            a[0]=0, a[1]=0
            b[0]=1, b[1]=1
            c[0]=0, c[1]=0, c[2]=0
        *   Toffoli(a[1], b[1], c[1]):
            a[1]=0, b[1]=1 -> c[1] stays 0.
        *   CNOT(a[1], b[1]):
            a[1]=0 -> b[1] stays 1.
        *   Toffoli(a[0], b[0], c[0]):
            a[0]=0, b[0]=1 -> c[0] stays 0.
        *   CNOT(a[0], b[0]):
            a[0]=0 -> b[0] stays 1.
        *   Toffoli(b[0], c[1], c[0]):
            b[0]=1, c[1]=0 -> c[0] stays 0.
        *   CNOT(c[1], b[0]):
            c[1]=0 -> b[0] stays 1.
    *   Wait, none of the Toffolis or CNOTs do anything because `a[0]` and `a[1]` are 0, and `c

### Reference answer

Deterministic output: state |0011000> with probability ~1.00

## isqTrain/4159

- task_id: `isqTrain/4159`
- task_type: `output_prediction`
- category: `quantum_arithmetic`
- difficulty: `difficult`
- concept_tags: `reversible_computing`, `ancilla_usage`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3044`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[4];

procedure main() {
    X(q[0]);
    X(q[1]);
    Toffoli(q[0], q[1], q[3]);
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the measurement output of the given isQ circuit.
    *   Circuit:
        
    *   Qubits: `q[0]`, `q[1]`, `q[2]`, `q[3]` (all initialized to |0>).
    *   Output format: "## Circuit Analysis", concise, 3-8 lines, Dirac notation, no isQ code blocks, end with the probability distribution.

2.  **Trace Circuit Execution:**
    *   Initial state: $|0000\rangle_{q3 q2 q1 q0}$
    *   `X(q[0])` and `X(q[1])`: State becomes $|0011\rangle_{q3 q2 q1 q0}$ (where q1=1, q0=1).
    *   `Toffoli(q[0], q[1], q[3])`: Since q0=1 and q1=1, flip q3. State becomes $|1011\rangle$.
    *   `CNOT(q[0], q[2])`: Since q0=1, flip q2. State becomes $|1111\rangle$.
    *   `CNOT(q[1], q[2])`: Since q1=1, flip q2. State becomes $|1101\rangle_{q3 q2 q1 q0}$. Wait, let's re-check bit order.
        *   State vector: $|q_3 q_2 q_1 q_0\rangle$.
        *   Init: 0000
        *   X(0), X(1): 0011
        *   Toffoli(0, 1, 3): 1011
        *   CNOT(0, 2): 1111
        *   CNOT(1, 2): 1101
    *   Let's double check CNOT(0,2) and CNOT(1,2).
        *   q[2] starts as 0.
        *   CNOT(0,2) -> q0 is 1, so q2 flips to 1.
        *   CNOT(1,2) -> q1 is 1, so q2 flips to 0.
        *   So q[2] is 0.
        *   Let's check `M(q[0]); M(q[1]); M(q[2]); M(q[3]);`
        *   Bits measured: q3=1, q2=0, q1=1, q0=1.
    *   Wait, what is the bitstring order in isQ's `--probs` output? "indexed by measurement bitstring (earlier measured qubit = higher bit)".
        *   Measured in order: q0, q1, q2, q3.
        *   Wait, the prompt says "earlier measured qubit = higher bit". So:
            *   1st measured = q0 = highest bit (leftmost or rightmost? "higher bit" usually means MSB, so index 3 in a 4-bit string `b3 b2 b1 b0`).
            *   Let's assume the bitstring is `q[0] q[1] q[2] q[3]` if measured in that order.
            *   q[0]=1, q[1]=1, q[2]=0, q[3]=1.
            *   Bitstring = 1101. Decimal = 13.
    *   Let's re-verify state evolution.
        *   $|q_3 q_2 q_1 q_0\rangle$
        *   Start: $|0000\rangle$
        *   X(0), X(1): $|0011\rangle$
        *   Toff(0,1,3): flips $q_3$. $|1011\rangle$
        *   CNOT(0,2): flips $q_2$. $|1111\rangle$
        *   CNOT(1,2): flips $q_2$. $|1101\rangle$
        *   So $q_3=1, q_2=0, q_1=1, q_0=1$.
        *   In order of measurement (q0, q1, q

### Reference answer

Deterministic output: state |1101> with probability ~1.00

## isqTrain/4179

- task_id: `isqTrain/4179`
- task_type: `output_prediction`
- category: `quantum_arithmetic`
- difficulty: `expert`
- concept_tags: `reversible_computing`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5312`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit a[2];
qbit b[2];
qbit c[3];

procedure main() {
    X(a[0]);
    X(a[1]);
    Toffoli(a[1], b[1], c[1]);
    CNOT(a[1], b[1]);
    Toffoli(a[0], b[0], c[0]);
    CNOT(a[0], b[0]);
    Toffoli(b[0], c[1], c[0]);
    CNOT(c[1], b[0]);
    M(a[0]); M(a[1]); M(b[0]); M(b[1]); M(c[0]); M(c[1]); M(c[2]);
}

```

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: All qubits in |0⟩
- a[0] = |0⟩, a[1] = |0⟩, b[0] = |0⟩, b[1] = |0⟩, c[0] = |0⟩, c[1] = |0⟩, c[2] = |0⟩

Step 1: X(a[0]) and X(a[1])
- a[0] = |1⟩, a[1] = |1⟩

State: |1,1,0,0,0,0,0⟩ (in order a[0], a[1], b[0], b[1], c[0], c[1], c[2])

Step 2: Toffoli(a[1], b[1], c[1])
- a[1] = |1⟩, b[1] = |0⟩ → both controls not |1⟩, so no flip
- c[1] remains |0⟩

State: |1,1,0,0,0,0,0⟩

Step 3: CNOT(a[1], b[1])
- a[1] = |1⟩ → flip b[1]
- b[1] becomes |1⟩

State: |1,1,0,1,0,0,0⟩

Step 4: Toffoli(a[0], b[0], c[0])
- a[0] = |1⟩, b[0] = |0⟩ → not both controls |1⟩
- c[0] remains |0⟩

State: |1,1,0,1,0,0,0⟩

Step 5: CNOT(a[0], b[0])
- a[0] = |1⟩ → flip b[0]
- b[0] becomes |1⟩

State: |1,1,1,1,0,0,0⟩

Step 6: Toffoli(b[0], c[1], c[0])
- b[0] = |1⟩, c[1] = |0⟩ → not both controls |1⟩
- c[0] remains |0⟩

State: |1,1,1,1,0,0,0⟩

Step 7: CNOT(c[1], b[0])
- c[1] = |0⟩ → no flip
- b[0] remains |1⟩

State: |1,1,1,1,0,0,0⟩

Final measurements:
- M(a[0]) = 1
- M(a[1]) = 1
- M(b[0]) = 1
- M(b[1]) = 1
- M(c[0]) = 0
- M(c[1]) = 0
- M(c[2]) = 0

This is a classical circuit (no superposition), so the outcome is deterministic.

The measurement bitstring (earlier measured qubit = higher bit):
a[0] is the highest bit, then a[1], b[0], b[1], c[0], c[1], c[2]

Bitstring: 1111000

This looks like an adder circuit. Let me verify:
- a = a[1]a[0] = 11 = 3
- b = b[1]b[0] = 00 = 0
- c = c[2]c[1]c[0] = 000 = 0

Actually wait, looking more carefully at the circuit structure:

After X(a[0]) and X(a[1]): a = 11 (binary for 3)
b = 00, c = 000

The circuit seems to be computing a + b into c or something similar.

Let me re-trace more carefully:

Initial: a[0]=1, a[1]=1, b[0]=0, b[1]=0, c[0]=0, c[1]=0, c[2]=0

After Toffoli(a[1], b[1], c[1]): no change (b[1]=0)
After CNOT(a[1], b[1]): b[1] = 1
After Toffoli(a[0], b[0], c[0]): no change (b[0]=0)
After CNOT(a[0], b[0]): b[0] = 1
After Toffoli(b[0], c[1], c[0]): no change (c[1]=0)
After CNOT(c[1], b[0]): no change (c[1]=0)

Final state: a[0]=

### Reference answer

Deterministic output: state |1111000> with probability ~1.00

## isqTrain/4336

- task_id: `isqTrain/4336`
- task_type: `output_prediction`
- category: `quantum_arithmetic`
- difficulty: `difficult`
- concept_tags: `reversible_computing`, `boolean_logic`
- source: `isq_train_cot`
- dataset_index: `1204`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;

qbit q[4];

procedure main() {
    // Inputs: x0=1, x1=1
    X(q[0]);
    X(q[1]);
    // Weight 1*x0 -> LSB of output
    CNOT(q[0], q[2]);
    // Weight 2*x1 -> MSB of output
    CNOT(q[1], q[3]);
    // Result: 1+2 = 3 = |11>
    X(q[0]); // flip qubit 0 before measurement
    M(q[2]); M(q[3]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Output prediction for a given isQ program.
    *   Format: Step-by-step reasoning using Dirac notation, 3-15 lines.
    *   Specifics: Start with "## Circuit Analysis", do not include code blocks, end with predicted probability distribution.
    *   Input program: A 4-qubit circuit. `q[0]` and `q[1]` initialized to |1>. `q[0]` CNOTs to `q[2]`, `q[1]` CNOTs to `q[3]`. Then `q[0]` is flipped to |0>. Measurements on `q[2]` and `q[3]`.
    *   Wait, the prompt says "Number of qubits measured: 4" In the implementation and "Expected measurement probabilities: {|0011>: 1.0}". Ah, the --probs mode in isQ usually measures all qubits in the array, and the bitstring is indexed by measurement order (earlier measured = higher bit). Wait, the reference says `{|0011>: 1.0}`. Let's trace the exact state.

2.  **Trace the Quantum State:**
    *   Initial state: $|0000\rangle$ (q[3]q[2]q[1]q[0] standard ordering usually, but let's track indices).
    *   `X(q[0])`, `X(q[1])` $\rightarrow |11\rangle_{q[1]q[0]}|00\rangle_{q[3]q[2]} \rightarrow |1111\rangle$ is wrong, wait. If q[3] is MSB, q[0] is LSB: $|0000\rangle$. After X(q[0]) and X(q[1]): $|0011\rangle$.
    *   `CNOT(q[0], q[2])`: Control q[0] is 1, target q[2] flips to 1. State: $|0111\rangle$. (q[3]=0, q[2]=1, q[1]=1, q[0]=1).
    *   `CNOT(q[1], q[3])`: Control q[1] is 1, target q[3] flips to 1. State: $|1111\rangle$. (q[3]=1, q[2]=1, q[1]=1, q[0]=1).
    *   `X(q[0])`: Flips q[0] back to 0. State: $|1110\rangle$.
    *   Wait, The implementation says: `Expected measurement probabilities: {|0011>: 1.0}`. Let me re-analyze the carefully.
    *   `Expected measurement probabilities: {|0011>: 1.0}`
    *   Let me check the reference again. Is it possible the reference in the prompt is a bit scrambled or I need to follow exactly the output format?
    *   Wait, if state is $|1110\rangle$, why would it be $|0011\rangle$?
    *   Let's re-read the prompt code. `q[0]` and `q[1]` are initialized to 1.
    *   Wait, is The implementation wrong, or am I interpreting the bitstring order differently?
    *   Let's check standard isQ `--probs` bit order. Usually: earlier measured qubit = higher bit. If only M(q[2]) and M(q[3]) are explicitly measured, `--probs` often measures ALL qubits at the end of the program. The reference says "Number of qubits measured: 4".
    *   Let's re-read the state: $q[0]=1, q[1]=1, q[2]=0, q[3]=0$.
    *   CNOT(q[0], q[2]) -> $q[2]$ becomes 1.
    *   CNOT(q[1], q[3]) -> $q[3]$ becomes 1.
    *   X(q[0]) -> $q[0]$ becomes 0.
    *   So $q[3]=1, q[2]=1, q[1]=1, q[0]=0$. In binary $1110$.
    *   Why does the reference say `{|0011>: 1.0}`? Maybe the bitstring in reference is literally $q[3]=0, q[2]=0, q[1]=1, q[0]=1$? If it's $|0011\rangle$, that means none of the CNOTs fired.
    *   Wait

### Reference answer

{'predicted_probs': {'0011': 1.0}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0011>) = 1.0000.'}
