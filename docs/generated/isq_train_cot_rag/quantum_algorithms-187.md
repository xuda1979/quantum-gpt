# ISQ training COT RAG corpus: quantum_algorithms shard 187

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4376

- task_id: `isqTrain/4376`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `4195`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;

qbit q[4];

procedure main() {
    // Eigenstate |1> of T gate
    X(q[3]);
    // Counting register in superposition
    H(q[0]);
    H(q[1]);
    H(q[2]);
    // Controlled powers of T
    // T^1 controlled by q[2]
    ctrl T(q[2], q[3]);
    // T^2 = S controlled by q[1]
    ctrl S(q[1], q[3]);
    // T^4 = Z controlled by q[0]
    ctrl Z(q[0], q[3]);
    // Inverse QFT on counting register
    // SWAP q[0] and q[2]
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    // QFT dagger
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2, q[0], q[1]);
    H(q[1]);
    ctrl Rz(-3.14159265358979 / 4, q[0], q[2]);
    ctrl Rz(-3.14159265358979 / 2, q[1], q[2]);
    H(q[2]);
    // Measure counting register
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

Let me analyze this quantum circuit step by step.

The circuit implements Quantum Phase Estimation (QPE) for the T gate, with an X gate flip on q[0] before measurement.

1. Initial state: |0000>

2. X(q[3]): |0001>

3. H(q[0]), H(q[1]), H(q[2]): Creates superposition on counting register
|ψ⟩ = (1/√8)(|0001⟩ + |0011⟩ + |0101⟩ + |0111⟩ + |1001⟩ + |1011⟩ + |1101⟩ + |1111⟩)
Wait, let me be more careful. The counting register is q[0], q[1], q[2] and the eigenstate register is q[3].

After X(q[3]): |0001⟩ (q[0]=0, q[1]=0, q[2]=0, q[3]=1)

After H on q[0], q[1], q[2]:
|ψ⟩ = (1/√8) Σ_{k=0}^{7} |k⟩|1⟩

where k is the binary representation using q[0] as highest bit, q[1] as middle, q[2] as lowest bit.

Wait, let me think about the bit ordering. In the state |q[0]q[1]q[2]q[3]⟩:

After X(q[3]): |0001⟩
After H(q[0]): (1/√2)(|0001⟩ + |1001⟩)
After H(q[1]): (1/2)(|0001⟩ + |0101⟩ + |1001⟩ + |1101⟩)
After H(q[2]): (1/√8)(|0001⟩ + |0011⟩ + |0101⟩ + |0111⟩ + |1001⟩ + |1011⟩ + |1101⟩ + |1111⟩)

4. Controlled powers of T on q[3]:
- ctrl T(q[2], q[3]): T^1 on q[3] when q[2]=1. T|1⟩ = e^(iπ/4)|1⟩
- ctrl S(q[1], q[3]): T^2 = S on q[3] when q[1]=1. S|1⟩ = e^(iπ/2)|1⟩  
- ctrl Z(q[0], q[3]): T^4 = Z on q[3] when q[0]=1. Z|1⟩ = e^(iπ)|1⟩

The phase accumulated for state |q[0]q[1]q[2]⟩|1⟩ is:
e^(iπ(q[0]·4 + q[1]·2 + q[2]·1)/4) = e^(i2πk/8) where k = q[0]·4 + q[1]·2 + q[2]·1

So after the controlled operations:
|ψ⟩ = (1/√8) Σ_{k=0}^{7} e^(i2πk/8) |k⟩|1⟩

Wait, let me reconsider. The T gate has eigenvalue e^(iπ/4) for |1⟩. The phase is φ = π/4, so φ/2π = 1/8.

In QPE, after the controlled operations:
|ψ⟩ = (1/√8) Σ_{k=0}^{7} e^(i2πk·φ/2π) |k⟩|1⟩ = (1/√8) Σ_{k=0}^{7} e^(i2πk/8) |k⟩|1⟩

where k is interpreted as q[0]·4 + q[1]·2 + q[2]·1.

Wait, let me reconsider the ordering. The state |q[0]q[1]q[2]q[3]⟩ represents k where:
- q[0] is the most significant bit (controls T^4 = Z)
- q[1] controls T^2 = S
- q[2] is the least significant bit (controls T^1)

So k = q[0]*4 + q[1]*2 + q[2]*1, and the phase applied is e^(i·k·φ) where φ = π/4.

|ψ⟩ = (1/√8) Σ_{k=0}^{7} e^(ikπ/4) |k⟩|1⟩

This is exactly the state where the QFT† should extract the phase.

5. Inverse QFT:

The standard QPE applies QFT† on the counting register to extract the phase.

### Reference answer

{'predicted_probs': {'0000': 0.021447, '0001': 0.125, '0101': 0.426777, '0110': 0.213388, '0111': 0.213388}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0000>) = 0.0214, P(|0001>) = 0.1250, P(|0101>) = 0.4268, P(|0110>) = 0.2134, P(|0111>) = 0.2134.'}

## isqTrain/2663

- task_id: `isqTrain/2663`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `global_phase`, `interference`, `isq_syntax_deriving_gate`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1576`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[2];

// Z gate wrapper for ctrl modifier
procedure my_z(qbit a) {
    Z(a);
} deriving gate

procedure main() {
    // Step 1: uniform superposition
    H(q[0]); H(q[1]);

    // Step 2: phase oracle marking |10>
    // |10> means q[0]=1, q[1]=0; negate q[1] to match ctrl
    X(q[1]);
    ctrl my_z(q[0], q[1]);
    X(q[1]);

    // Step 3: Grover diffusion operator
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    // Conditional phase flip for |00> (after X -> |11>)
    ctrl my_z(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);

    // Measure: |10> amplified to probability 1
    M(q[0]); M(q[1]);
}

```

vs.

```isq
import std;
qbit q[2];

// Z gate wrapper for ctrl modifier
procedure my_z(qbit a) {
    Z(a);
} deriving gate

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Step 1: uniform superposition
    H(q[0]); H(q[1]);

    // Step 2: phase oracle marking |10>
    // |10> means q[0]=1, q[1]=0; negate q[1] to match ctrl
    X(q[1]);
    ctrl my_z(q[0], q[1]);
    X(q[1]);

    // Step 3: Grover diffusion operator
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    // Conditional phase flip for |00> (after X -> |11>)
    ctrl my_z(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);

    // Measure: |10> amplified to probability 1
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A** implements a 2-qubit Grover search: it creates a uniform superposition via H on both qubits, applies a phase oracle marking |10⟩ (using X(q[1]), CZ, X(q[1])), then applies the Grover diffusion operator (H×H, X×X, CZ, X×X, H×H), and measures.

2. **Program B** applies exactly the same sequence of operations, preceded by `GPhase(0.0)`.

3. **Key difference:** Program B includes `GPhase(0.0)`, which multiplies the global state by e^{i·0} = 1 — an identity operation with no physical effect.

4. Since `GPhase(0.0)` is trivial, both programs produce the identical quantum state |10⟩ with probability 1 at measurement. Measurement distributions are the same.

5. **Verdict: Yes** — the programs are equivalent.

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/3911

- task_id: `isqTrain/3911`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `1626`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```
import std;
// Bernstein-Vazirani: find secret s = 1111
oracle f(4, 1) = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0];
qbit q[5];

procedure main() {
    // Output in |->
    X(q[4]);
    H(q[4]);
    // Hadamard on inputs
    for i in 0:4 {
    // BUG: missing gate here
    }
    // Oracle
    f(q[0], q[1], q[2], q[3], q[4]);
    // Hadamard
    for i in 0:4 {
        H(q[i]);
    }
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The first `for i in 0:4` loop (which should initialize the input qubits) has an empty body — the `H(q[i])` gate is missing. Without this, the input qubits remain in |0⟩ instead of being transformed to |+⟩, breaking the BV algorithm's superposition step.

2. **Fix**: Add `H(q[i]);` inside the first loop body:

3. **State evolution (corrected)**:
   - Initialize: |00000⟩ → X(q[4]) → |00001⟩ → H(q[4]) → |0000−⟩
   - H on inputs (q[0..3]): |++++−⟩ = Σ_x |x−⟩ / 4 (equal superposition over all 4-bit inputs)
   - Oracle f (s=1111): phase kickback applies (−1)^(x·s), giving Σ_x (−1)^(x·1111)|x⟩ ⊗ |−⟩ / 4
   - H on inputs (q[0..3]): constructive interference yields |1111⟩ ⊗ |−⟩
   - Measurement: qubits q[0..3] yield 1111 with certainty; q[4] in |−⟩ measures 0 or 1 with equal probability → {|11110⟩: 0.5, |11111⟩: 0.5} ✓

## isqTrain/3827

- task_id: `isqTrain/3827`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3935`

### Prompt

实现以下量子计算任务（使用isQ）：a 1D quantum walk on 8 positions using 2 step(s). Use q[0] as the coin qubit and q[1..3] as the position register. Each step: Hadamard coin flip followed by controlled shifts.

### Chain-of-thought reasoning

Let me analyze this quantum walk circuit step by step.

The circuit implements a 1D quantum walk on 8 positions (3 position qubits) with 2 steps.

Initial state: |0000⟩ (q[0] = coin = |0⟩, q[1..3] = position = |000⟩ = position 0)

**Step 1:**
1. H(q[0]) on coin: |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2
   State: (|0000⟩ + |1000⟩)/√2

2. ctrl X(q[0], q[1]): If coin=|1⟩, flip q[1]
   State: (|0000⟩ + |1010⟩)/√2

3. ctrl X(q[0], q[2]): If coin=|1⟩, flip q[2]
   State: (|0000⟩ + |1110⟩)/√2

4. ctrl X(q[0], q[3]): If coin=|1⟩, flip q[3]
   State: (|0000⟩ + |1111⟩)/√2

Wait, this is a conditional increment. When coin is |1⟩, all three position bits flip. So position 000 → 111 (which is position 7).

After Step 1: (|0000⟩ + |1111⟩)/√2

**Step 2:**
1. H(q[0]) on coin:
   The coin part of |0000⟩ has coin=|0⟩, so H|0⟩ = |+⟩
   The coin part of |1111⟩ has coin=|1⟩, so H|1⟩ = |−⟩
   
   State: (|+⟩|000⟩ + |−⟩|111⟩)/√2
        = ((|0⟩+|1⟩)|000⟩ + (|0⟩-|1⟩)|111⟩)/2
        = (|0000⟩ + |1000⟩ + |0111⟩ - |1111⟩)/2

Wait, let me be more careful. The state after step 1 is:
(|0⟩|000⟩ + |1⟩|111⟩)/√2

Applying H to q[0]:
H|0⟩ = (|0⟩+|1⟩)/√2
H|1⟩ = (|0⟩-|1⟩)/√2

New state: ((|0⟩+|1⟩)/√2 |000⟩ + (|0⟩-|1⟩)/√2 |111⟩)/√2
= ((|0⟩+|1⟩)|000⟩ + (|0⟩-|1⟩)|111⟩)/2
= (|0000⟩ + |1000⟩ + |0111⟩ - |1111⟩)/2

2. ctrl X(q[0], q[1]): If coin=|1⟩, flip q[1]
   |0000⟩ → |0000⟩ (coin=0)
   |1000⟩ → |1010⟩ (coin=1, flip q[1])
   |0111⟩ → |0111⟩ (coin=0)
   |1111⟩ → |1101⟩ (coin=1, flip q[1])

Hmm wait, that doesn't seem right. Let me re-examine.

Actually, the shift operation in a quantum walk should increment position when coin is |1⟩ and decrement when coin is |0⟩ (or vice versa). But here, the code just does controlled increments on each position qubit when coin is |1⟩.

Let me trace through more carefully.

State after H on coin in step 2:
(|0000⟩ + |1000⟩ + |0111⟩ - |1111⟩)/2

Now ctrl X(q[0], q[1]):
- |0000⟩: coin=0, no change → |0000⟩
- |1000⟩: coin=1, flip q[1] → |1010⟩
- |0111⟩: coin=0, no change → |0111⟩
- |1111⟩: coin=1, flip q[1] → |1101⟩

State: (|0000⟩ + |1010⟩ + |0111⟩ - |1101⟩)/2

Now ctrl X(q[0], q[2]):
- |0000⟩: coin=0 → |0000⟩
- |1010⟩: coin=1, flip q[2] → |1110⟩
- |0111⟩: coin=0 → |0111⟩
- |1101⟩: coin=1, flip q[2] → |1111⟩

State: (|0000⟩ + |1110

## isqTrain/2931

- task_id: `isqTrain/2931`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1136`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```isq
import std;
qbit q[2];
// Controlled Rz(1*pi/2)
procedure main() {
    H(q[0]);
    X(q[1]);
    ctrl Rz(1.570796, q[0], q[1]);
    // H(q[0]); // BUG: missing Hadamard
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

The buggy code is missing a Hadamard gate on q[0] after the controlled Rz operation. This is a phase kickback circuit where:

1. H(q[0]) puts q[0] in |+⟩ superposition
2. X(q[1]) puts q[1] in |1⟩
3. ctrl Rz(π/2, q[0], q[1]) applies Rz(π/2) to q[1] controlled on q[0], causing phase kickback
4. The second H(q[0]) is needed to convert the phase back to computational basis for measurement

Without the second Hadamard, the phase information stays in superposition and measurement won't give the predicted output.

The fix: uncomment H(q[0]) after the ctrl Rz.

State evolution of corrected circuit:
- |00⟩ → H on q[0] → (|0⟩+|1⟩)|0⟩/√2 = (|00⟩+|10⟩)/√2
- X on q[1] → (|01⟩+|11⟩)/√2
- ctrl Rz(π/2) on q[1] → (|01⟩+e^(iπ/2)|11⟩)/√2 = (|01⟩+i|11⟩)/√2
- H on q[0] → ((|0⟩+|1⟩)|1⟩ + i(|0⟩-|1⟩)|1⟩)/(2) = ((1+i)|0⟩+(1-i)|1⟩)|1⟩/2
- Probabilities: |01⟩: |1+i|²/4 = 2/4 = 0.5... wait that doesn't match.

Let me recalculate. The predicted output |01⟩: 0.8536, |11⟩: 0.1464.

Actually, let me reconsider the controlled Rz semantics. In isQ, `ctrl Rz(theta, q[0], q[1])` means q[0] is control, q[1] is target? Or is it `ctrl Rz(theta, q[0], q[1])` where the ctrl modifier applies to the next gate?

Looking at the syntax: `ctrl @[c1, c2] Gate(target);`

So `ctrl Rz(1.570796, q[0], q[1])` - this is ambiguous. Is q[0] the control and q[1] the target for Rz? Or are both q[0] and q[1] arguments to Rz?

Actually, looking at the isQ syntax more carefully: `ctrl @[c1, c2] Gate(target)`. The ctrl modifier adds control qubits. So `ctrl Rz(1.570796, q[0], q[1])` would mean... hmm.

Wait, in standard controlled gate syntax, `ctrl Rz(theta, target)` with a control qubit specified somehow. Let me look at the syntax again: `ctrl @[c1, c2] Gate(target);`

So it seems like the control qubits go in the @[] part. But the code doesn't use that syntax. Maybe in this case, for a two-qubit controlled gate like CNOT-style, the first qubit after theta is control?

Actually, I think the syntax might be that for `ctrl Rz(theta, q[0], q[1])`, q[0] is implicitly the control and q[1] is the target of Rz. This is common in quantum computing languages.

Let me recalculate:
- Start: |00⟩
- H(q[0]): (|0⟩+|1⟩)|0⟩/√2 = (|00⟩+|10⟩)/√2
- X(q[1]): (|01⟩+|11⟩)/√2
- ctrl Rz(π/2, q[0], q[1]): When q[0]=|1⟩, apply Rz(π/2) to q[1]
  Rz(π/2)|0⟩ = |0⟩, Rz(π/2)|1⟩ = e^(iπ/2)|1⟩ = i|1⟩
  So: (|01⟩ + i|11⟩)/√2
- H(q[0]): Apply H to q[0]
  |01⟩ → (|0⟩+|1⟩)|1⟩/√2 = (|01⟩+|11⟩)/√2
  i|11⟩ → i(|0⟩-|1⟩)|1⟩/√2 = i(|01⟩-|11⟩)/√2
  
  Total: (|01⟩+|11⟩ + i|01⟩ - i|11⟩)/(2)
       = ((1+i)|01⟩ +

## isqTrain/2951

- task_id: `isqTrain/2951`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `basis_change`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5094`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```isq
import std;
qbit q[3];
// X-basis measurement: prepare |+> then measure in X basis
procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
    M(q[0]);
    M(q[0]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug:** In the buggy code, the second measurement statement is `M(q[0])` instead of `M(q[1])`. This causes qubit `q[0]` to be measured twice while qubit `q[1]` is never measured.
2. **Fix:** Change the target of the second measurement from `q[0]` to `q[1]` so that the program measures `M(q[0])`, `M(q[1])`, and `M(q[2])`.
3. **State Evolution:** Initialized to |000>, the state becomes |111> after the X gates. The H gates then evolve the state into |+++>, which is an equal superposition of all eight computational basis states from |000> to |111>. Correctly measuring all three qubits yields identical probabilities of 0.125 for each outcome.

## isqQA/quantum_algorithms/39_principle_advantage

- task_id: `isqQA/quantum_algorithms/39_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `principle_advantage`, `algorithm`, `Bernstein-Vazirani算法`
- source: `qa_pipeline`
- dataset_index: `4718`

### Prompt

请详细解释Bernstein-Vazirani（伯恩斯坦-瓦济尼）算法的核心原理。在解决寻找隐藏字符串的问题时，它的量子时间复杂度与经典时间复杂度有何具体对比？这种量子加速的根本来源是什么？

### Reference answer

Bernstein-Vazirani（BV）算法是量子计算中用于展示量子并行性和查询复杂度优势的经典算法之一。其核心目标是寻找一个隐藏的比特字符串 $s \in \{0,1\}^n$。

**问题设定与经典时间复杂度：**
假设我们有一个黑盒（Oracle）函数 $f: \{0,1\}^n \rightarrow \{0,1\}$，该函数的内部逻辑被保证为 $f(x) = s \cdot x \pmod 2$，其中 $s$ 是我们未知的隐藏字符串，$\cdot$ 表示按位内积。在经典计算中，为了确定 $s$ 的每一位，我们必须独立地查询黑盒。例如，查询 $x = 100...0$ 可以得到 $s$ 的第一位，查询 $x = 010...0$ 可以得到第二位。因此，经典确定性算法需要进行 $n$ 次查询，时间复杂度为 $O(n)$。

**BV算法的核心原理与量子时间复杂度：**
BV算法利用量子特性，只需对黑盒进行 **$1$次查询** 即可得出完整的 $n$ 位隐藏字符串 $s$，时间复杂度骤降为 $O(1)$ 的查询复杂度（整体电路深度由于涉及Hadamard门操作，仍为 $O(n)$）。其原理步骤如下：
1. 初始化 $n+1$ 个量子比特，前 $n$ 个处于 $|0\rangle$ 态，最后1个（辅助比特）处于 $|1\rangle$ 态：$|0\rangle^{\otimes n}|1\rangle$。
2. 对所有量子比特应用Hadamard门。由于 $H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$ 且 $H|1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$，系统的状态变为均匀叠加态：$\frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} |x\rangle \left(\frac{|0\rangle - |1\rangle}{\sqrt{2}}\right)$。
3. 将量子态输入黑盒 $U_f$。由于辅助比特处于 $|0\rangle - |1\rangle$ 的状态，会产生**相位回溯（Phase Kickback）**效应。函数值 $f(x)$ 会被映射为相位因子 $(-1)^{f(x)}$。因为 $f(x) = s \cdot x$，量子态演变为：$\frac{1}{\sqrt{2^n}} \sum_{x} (-1)^{s \cdot x} |x\rangle \left(\frac{|0\rangle - |1\rangle}{\sqrt{2}}\right)$。辅助比特状态不变，可以丢弃或忽略。
4. 对前 $n$ 个量子比特再次应用Hadamard门。在数学上，二次Hadamard变换相当于对向量进行反向傅里叶变换，它将相位编码 $(-1)^{s \cdot x}$ 重新转换为计算基下的幅值。演算结果精确坍缩为：$|s\rangle$。
5. 测量前 $n$ 个量子比特，即可直接输出隐藏字符串 $s$。

**量子加速的根本来源：**
BV算法实现指数级查询加速（从 $O(n)$ 到 $O(1)$）的根本来源有两个：
第一是**量子叠加与并行性**。通过一次Hadamard变换，量子计算机同时生成了所有 $2^n$ 种可能的输入组合，并将它们置于叠加态中。这使得量子黑盒能够一次性处理所有可能的输入。
第二是**量子干涉（Interference）与相位回溯机制**。单纯的叠加无法让我们直接读取所有结果（因为测量只会随机坍缩到一个结果）。BV算法巧妙地利用了辅助比特的干涉效应，将黑盒的特征（内积结果）从计算基转换到了相位基上。随后的第二次Hadamard门起到了“解码器”的作用，通过相长干涉（放大正确答案 $s$ 的概率）和相消干涉（抵消所有错误答案的概率），将隐藏在相位中的信息完美提取到可测量的计算基态中。

## isqExpand/algo/3

- task_id: `isqExpand/algo/3`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `grover`, `oracle`, `bug_fix`
- source: `isq_expansion`
- dataset_index: `2139`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```isq
import std;
qbit q[2];

procedure oracle() {
    CZ(q[0], q[1]);
}

procedure diffusion() {
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);
}

procedure main() {
    H(q[0]); H(q[1]);
    oracle();
    diffusion();
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis

The oracle uses CZ(q[0], q[1]) which marks |11>, not |10>. To mark |10> (q[0]=1, q[1]=0), we need CZ to fire when q[0]=1 and q[1]=0.

Fix: Wrap q[1] with X gates to flip the condition:
- X(q[1]) before CZ: converts |10> -> |11> so CZ fires
- CZ(q[0], q[1]): applies phase
- X(q[1]) after: restores q[1]

State evolution after fix:
1. H|00> = (|00>+|01>+|10>+|11>)/2
2. Oracle marks |10>: (|00>+|01>-|10>+|11>)/2
3. Diffusion amplifies |10> to probability 1.0

## isqTrain/3454

- task_id: `isqTrain/3454`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `interference`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4502`

### Prompt

请用isQ语言编写一个量子电路：the SWAP test in isQ to compare two orthogonal states |0> and |1>.

For orthogonal states, P(q[0]=0) = 0.5 and P(q[0]=1) = 0.5.

Prepare q[1] = |0>, q[2] = |1> (X on q[2]).
Apply controlled-SWAP and measure control qubit.

Declare 3 qubits, measure q[0] only.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate reasoning for a swap (three-CNOT decomposition) test between $|0\rangle$ and $|1\rangle$ in isQ.
    *   Specifics: Explain goal, qubit count/measurements, step-by-step state evolution (Dirac notation), and expected probabilities.
    *   Constraints: ONLY output "## Reasoning" followed by text, NO code blocks, concise (up to 15 lines), precise Dirac notation.

2.  **Circuit / Goal Analysis:**
    *   Goal: Implement the swap (three-CNOT decomposition) test to compare two orthogonal quantum states, $|0\rangle$ and $|1\rangle$.
    *   Qubits: 3 qubits. q[0] is the control, q[1] is state A ($|0\rangle$), q[2] is state B ($|1\rangle$). Only q[0] is measured.
    *   Initial state: $|000\rangle$.

3.  **State Evolution:**
    *   Start: $|000\rangle$.
    *   X on q[2]: $|001\rangle$.
    *   H on q[0]: $\frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$.
    *   Controlled-swap (three-CNOT decomposition) (controlled-swap operation (three-CNOT decomposition)):
        *   When control is $|0\rangle$, do nothing: $|000\rangle$.
        *   When control is $|1\rangle$, swap (three-CNOT decomposition) q[1] and q[2]: $|1\rangle \otimes |01\rangle \rightarrow |1\rangle \otimes |10\rangle = |110\rangle$.
        *   State after c-swap (three-CNOT decomposition): $\frac{1}{\sqrt{2}}(|000\rangle + |110\rangle)$.
    *   H on q[0]:
        *   Apply H to q[0]: $H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$, $H|1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        *   State: $\frac{1}{\sqrt{2}} [ \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |00\rangle + \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) \otimes |10\rangle ]$
        *   $= \frac{1}{2} [ |000\rangle + |100\rangle + |010\rangle - |110\rangle ]$.
    *   Measure q[0] only:
        *   Probability of q[0]=0: Squared amplitude of terms with q[0]=$|0\rangle$.
        *   Terms: $|000\rangle$ and $|010\rangle$. Probability = $|1/2|^2 + |1/2|^2 = 1/4 + 1/4 = 1/2$.
        *   Probability of q[0]=1: Terms $|100\rangle$ and $|110\rangle$. Probability = $|1/2|^2 + |1/2|^2 = 1/2$.

4.  **Drafting the Reasoning (incorporating constraints):**
    *   *Line 1:* ## Reasoning
    *   *Line 2:* Goal: Perform a swap (three-CNOT decomposition) test between orthogonal states |0> and |1> to yield a 50% measurement probability on the control qubit.
    *   *Line 3:* Requires 3 qubits (q[0] control, q[1] state |0>, q[2] state |1>); only q[0] is measured.
    *   *Line 4:* Initialize q[2] to |1> via X, so the state is |001>. Apply H to q[0]: 1/√2(|001> + |101>).
    *   *Line 5:* Controlled-swap (three-CNOT decomposition) between q[1] and q[2] swaps them when q[0] is |1>: 1/√2(|001> + |110>).
    *   *Line 6:* Apply H to q[0]: 1/2(|001> + |101> + |010> - |110>).
    *   *Line 7:* Measuring q[0] collapses the state to either |0> or |1> with probabilities based on squared amplitudes of the respective terms.
    *   *Line 8:* The probability P(q[0]=0) = |1/2|² + |1

## isqTrain/4053

- task_id: `isqTrain/4053`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4998`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// QFT on 4 qubits with input state |0101>
qbit q[4];

procedure main() {
    // Prepare input state |0101>
    X(q[1]);
    X(q[3]);

    // QFT stage for qubit 0
    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    // QFT stage for qubit 1
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[3], q[1]);
    // QFT stage for qubit 2
    H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    // QFT stage for qubit 3
    H(q[3]);
    // Swap q[0] and q[3]
    CNOT(q[0], q[3]);
    CNOT(q[3], q[0]);
    CNOT(q[3], q[0]);
    // Swap q[1] and q[2]
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    // Measure after QFT
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug Location:**
The bug is in the third CNOT of the first swap operation (three-CNOT decomposition) (swapping q[0] and q[3]). The line `CNOT(q[3], q[0])` has swapped control/target — it should be `CNOT(q[0], q[3])`.

**2. The Fix:**
Change the third CNOT in the first swap from `CNOT(q[3], q[0])` to `CNOT(q[0], q[3])`. A correct swap (three-CNOT decomposition) requires: CNOT(a,b) → CNOT(b,a) → CNOT(a,b). The buggy code had CNOT(b,a) as the third gate instead of CNOT(a,b), resulting in a different permutation rather than a true swap.

**3. State Evolution (Corrected Circuit):**
- **Input preparation:** Apply X to q[1] and q[3] → state |0101⟩ (binary, decimal 5)
- **QFT stages:** Apply Hadamards and controlled-Rz rotations with angles π/2, π/4, π/8 to create proper phase relationships across all qubits
- **Swap q[0]↔q[3] and q[1]↔q[2]:** Correct the bit-reversal introduced by QFT's top-down structure
- **Final state:** QFT|5⟩ yields an equal superposition over all 16 basis states with relative phases: (1/4) Σ_k e^(2πi·5k/16)|k⟩
- **Measurement probabilities:** Each of the 16 states has probability |1/16|² = 0.0625, matching the expected uniform distribution
