# ISQ training COT RAG corpus: circuit_basics shard 20

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1755

- task_id: `isqTrain/1755`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2637`

### Prompt

实现以下量子计算任务（使用isQ）：Start with |1000000> on 7 qubits and apply a CNOT chain (q[0]->q[1], q[1]->q[2], ...). All qubits should end up as |1>.

### Chain-of-thought reasoning

## Reasoning
The goal is to propagate a |1> state across a chain of 7 qubits using sequential CNOT gates, transforming |1000000> into |1111111>.
We use 7 qubits, all of which are measured at the end of the circuit.
Starting in |0000000>, an X gate on q[0] prepares the initial state |1000000>.
The first CNOT(q[0], q[1]) flips q[1] to |1>, evolving the state to |1100000>.
Subsequent CNOTs propagate the |1> down the chain: |1110000> -> |1111000> -> |1111100> -> |1111110> -> |1111111>.
Because the system deterministically reaches the exact basis state |1111111>, measuring all 7 qubits yields a 100% probability for the bitstring 1111111.

## isqTrain/1599

- task_id: `isqTrain/1599`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4169`

### Prompt

Write an isQ program that Prepare |1> then apply Rx(pi/3). Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Initialize a qubit to |1> and apply an Rx rotation of π/3 to observe the resulting measurement probabilities.
2. **Qubits**: 1 qubit is required and measured.
3. **State Evolution**: 
   - Start in the initial state |0>.
   - Apply the X gate: |0> transitions to |1>.
   - Apply Rx(π/3), which evolves |1> to cos(π/6)|1> - i*sin(π/6)|0> = (√3/2)|1> - (i/2)|0>.
4. **Probabilities**: Measuring the final state yields a probability of |-i/2|² = 0.25 for |0> and |√3/2|² = 0.75 for |1>.

## isqTrain/1658

- task_id: `isqTrain/1658`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2647`

### Prompt

Write isQ code for the following quantum task: Apply CNOT chain on 4 qubits starting from |1000>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a chain of CNOT gates to propagate the |1⟩ state across 4 qubits.
2. **Qubits**: 4 qubits (q[0]–q[3]), all measured.
3. **State evolution**:
   - Start: |0000⟩ → Apply X(q[0]) → |1000⟩
   - CNOT(q[0], q[1]): control=|1⟩ flips target → |1100⟩
   - CNOT(q[1], q[2]): control=|1⟩ flips target → |1110⟩
   - CNOT(q[2], q[3]): control=|1⟩ flips target → |1111⟩
4. **Result**: Final state |1111⟩ yields measurement probability {|1111⟩: 1.0} since each CNOT propagates the excitation down the chain.

## isqTrain/4716

- task_id: `isqTrain/4716`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1908`

### Prompt

判断以下两段isQ代码是否产生相同的测量结果：

代码1：
```isq
import std;
qbit q[1];

procedure main() {
    Ry(pi/2.0, q[0]);
    M(q[0]);
}

```

代码2：
```isq
import std;
qbit q[1];

procedure main() {
    Ry(pi/4.0, q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A**:
    *   Starts in state |0>.
    *   Applies `Ry(pi/2.0, q[0])`. `Ry(pi/2)` rotates the state to |+> (superposition of |0> and |1> with equal positive amplitudes). Wait, $R_y(\pi/2)|0\rangle = \cos(\pi/4)|0\rangle + \sin(\pi/4)|1\rangle = \frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle = |+\rangle_y$ (or just equal superposition).
    *   Probability of |0> is $\cos^2(\pi/4) = 0.5$. Probability of |1> is $\sin^2(\pi/4) = 0.5$.
    *   The predicted output in the prompt says: "Program A produces {'0': 0.853553, '1': 0.146447} while Program B produces {'0': 0.5, '1': 0.5}." Wait! Is `Ry(pi/2)` in isQ actually `Ry(pi/2)` or is the prompt's predicted output using different angles?
    *   Let's check the prompt's predicted output:
        "Program A produces {'0': 0.853553, '1': 0.146447} while Program B produces {'0': 0.5, '1': 0.5}."
        But Program A has `Ry(pi/2.0, q[0])` and Program B has `Ry(pi/4.0, q[0])`.
        If B has `pi/4`, then $P(0) = \cos^2(\pi/8) \approx 0.853553$, $P(1) = \sin^2(\pi/8) \approx 0.146447$.
        If A has `pi/2`, then $P(0) = 0.5$, $P(1) = 0.5$.
        Ah! the predicted output in the prompt description says: "Program A produces {'0': 0.853553, '1': 0.146447} while Program B produces {'0': 0.5, '1': 0.5}." Wait, this is exactly swapped. If B has `pi/4` and A has `pi/2`, B produces 0.8535/0.146 and A produces 0.5/0.5.
        Wait, I shouldn't copy the exact numbers from the prompt if the prompt is flawed, or maybe I just need to state they are different. Let me re-read the prompt. "Program A produces {'0': 0.853553, '1': 0.146447} while Program B produces {'0': 0.5, '1': 0.5}." -> the predicted output has the distributions swapped in the text. A uses pi/2 so P(0)=0.5, B uses pi/4 so P(0)=0.8535.
        Regardless, they are NOT equivalent.

2.  **Draft the analysis**:
    *   Program A applies `Ry(pi/2)` to |0>, yielding $\cos(\pi/4)|0\rangle + \sin(\pi/4)|1\rangle$. This gives P(0)=0.5 and P(1)=0.5.
    *   Program B applies `Ry(pi/4)` to |0>, yielding $\cos(\pi/8)|0\rangle + \sin(\pi/8)|1\rangle$. This gives P(0)≈0.8536 and P(1)≈0.1464.
    *   The key difference is the rotation angle, which dictates the amplitude of the superposition and thus the measurement probabilities.
    *   Since the probabilities differ (0.5/0.5 vs 0.8536/0.1464), the programs are not equivalent.

3.  **Refine wording**: Keep it concise, 3-8 lines.
    - Program A applies an `Ry(pi/2)` gate to |0>, evolving the state to an equal superposition: $\frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle$, yielding measurement probabilities P(0)=0.5 and P(1)=0.5.
    - Program B applies an `Ry(pi/4)` gate to |0>, evolving the state to $\cos(\pi/8)|0

### Reference answer

{'equivalent': False, 'explanation': "Different rotation angles give different probability distributions Program A produces {'0': 0.853553, '1': 0.146447} while Program B produces {'0': 0.5, '1': 0.5}.", 'probs_a': {'0': 0.5, '1': 0.5}, 'probs_b': {'0': 0.853553, '1': 0.146447}}

## isqTrain/4734

- task_id: `isqTrain/4734`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5113`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[1];

procedure main() {
    Rx(pi/3.0, q[0]);
    M(q[0]);
}

```

vs.

```isq
import std;
qbit q[1];

procedure main() {
    Rx(pi/6.0, q[0]);
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A:**
    *   Initial state: |0>
    *   Gate: Rx($\pi/3$, q[0])
    *   Final state: $\cos(\pi/6)|0\rangle - i \sin(\pi/6)|1\rangle$
    *   Probabilities: $P(0) = \cos^2(\pi/6) = 3/4$, $P(1) = \sin^2(\pi/6) = 1/4$.

2.  **Analyze Program B:**
    *   Initial state: |0>
    *   Gate 1: Rx($\pi/6$, q[0])
    *   State after Gate 1: $\cos(\pi/12)|0\rangle - i \sin(\pi/12)|1\rangle$
    *   Gate 2: H(q[0])
    *   H on $a|0\rangle + b|1\rangle$ is $\frac{1}{\sqrt{2}}((a+b)|0\rangle + (a-b)|1\rangle)$.
    *   Here $a = \cos(\pi/12)$ and $b = -i \sin(\pi/12)$.
    *   Probability of 0: $\frac{1}{2} |a+b|^2 = \frac{1}{2} (\cos^2(\pi/12) + \sin^2(\pi/12) - 2i \cos(\pi/12)\sin(\pi/12)) = \frac{1}{2} (1 - i \sin(\pi/6)) = \frac{1}{2} (1 - i/2)$.
    *   Magnitude squared: Wait, let's just calculate the exact value.
    *   $P_A(0) = \cos^2(30^\circ) = 3/4 = 0.75$.
    *   $P_B(0) = \frac{1}{2} |\cos(\pi/12) - i \sin(\pi/12)|^2$. Wait, the formula for $P(0)$ after H is $\frac{1}{2} |a+b|^2$.
    *   $P_B(0) = \frac{1}{2} |\cos(\pi/12) - i \sin(\pi/12)|^2 = \frac{1}{2} (\cos^2(\pi/12) + \sin^2(\pi/12)) = 1/2 = 0.5$.
    *   Wait, $P_B(0) = 0.5$? Let me double check.
    *   If state is $a|0\rangle + b|1\rangle$, then $H = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$.
    *   So new state is $\frac{1}{\sqrt{2}} (a+b) |0\rangle + \frac{1}{\sqrt{2}} (a-b) |1\rangle$.
    *   $P(0) = \frac{1}{2} |a+b|^2 = \frac{1}{2} (|a|^2 + |b|^2 + a b^* + a^* b)$.
    *   Here $a = \cos(\pi/12)$ (real) and $b = -i \sin(\pi/12)$ (imaginary).
    *   $a b^* + a^* b = \cos(\pi/12) (i \sin(\pi/12)) + \cos(\pi/12) (-i \sin(\pi/12)) = 0$.
    *   So $P_B(0) = \frac{1}{2} (1 + 0) = 1/2$.
    *   Let me re-read my formula. Yes, $P_B(0) = 0.5$.
    *   Therefore $P_A(0) = 0.75 \neq 0.5 = P_B(0)$. They are different.

3.  **Structure the output:**
    *   **Program A:** Applies `Rx(pi/3)` to |0>, yielding $\cos(\pi/6)|0\rangle - i \sin(\pi/6)|1\rangle$. Measurement probability $P(0) = 3/4$.
    *   **Program B:** Applies `Rx(pi/6)` then `H` to |0>. The intermediate state is $\cos(\pi/12)|0\rangle - i \sin(\pi/12)|1\rangle$. Applying H results in probability $

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'0': 0.75, '1': 0.25}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/4729

- task_id: `isqTrain/4729`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3104`

### Prompt

比较这两个量子电路，它们的输出概率分布一样吗？

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    ctrl ctrl X(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    ctrl ctrl X(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A operations**: Applies an X gate to q[0], changing the state to |100>. Then it applies a double-controlled X (Toffoli) gate with q[0] and q[1] as controls and q[2] as the target. Since q[1] is in the |0> state, the Toffoli gate does nothing. The final state is |100>.

2. **Program B operations**: Applies X gates to both q[0] and q[1], changing the state to |110>. It then applies the same Toffoli gate. Since both controls (q[0] and q[1]) are in the |1> state, the target q[2] is flipped. The final state is |111>.

3. **Key difference**: Program B applies an additional X gate to q[1] before the Toffoli gate. This activates both control qubits for the Toffoli gate, causing the target qubit to flip, whereas Program A leaves the target unflipped.

4. **Measurement probabilities**: Program A will measure the state |100> with 100% probability, yielding the bitstring '100'. Program B will measure the state |111> with 100% probability, yielding the bitstring '111'. The probability distributions are entirely different.

5. **Verdict**: No

### Reference answer

{'equivalent': False, 'explanation': "Toffoli with both controls=1 flips target, with one control=0 does nothing Program A produces {'111': 1.0} while Program B produces {'100': 1.0}.", 'probs_a': {'100': 1.0}, 'probs_b': {'111': 1.0}}

## isqTrain/1776

- task_id: `isqTrain/1776`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1589`

### Prompt

请用isQ语言编写一个量子电路：Apply X gate 8 times to |0> and measure. (X^8 = I.)

### Chain-of-thought reasoning

## Reasoning
The goal is to apply the X gate eight times to an initial |0> state and measure the result.
This requires 1 qubit, which is the sole qubit measured at the end of the circuit.
Starting in the |0> state, the first X gate flips the state to |1>, and the second X gate flips it back to |0>. 
Since X^2 = I (the identity operator), applying X eight times is equivalent to applying it an even number of times, leaving the state unchanged.
The final quantum state is exactly |0>, which yields a measurement probability of {|0>: 1.0}.

## isqTrain/1490

- task_id: `isqTrain/1490`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `data_encoding_qml`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5262`

### Prompt

Create an isQ quantum circuit that Encode the integer 12 (binary 01100) into 5 qubits using basis encoding. Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Encode the integer 12 (binary 01100) into a 5-qubit register using basis encoding and measure the state.
2. **Qubits:** 5 qubits (`q[0]` to `q[4]`) are required, and all 5 are measured.
3. **State Evolution:**
   - Initialize 5 qubits to the ground state: `|00000>`
   - Apply `X(q[1])` to flip the second qubit, resulting in state: `|01000>`
   - Apply `X(q[2])` to flip the third qubit, resulting in state: `|01100>`
4. **Probabilities:** The final state is exactly the basis state `|01100>`. Thus, measuring all qubits deterministically yields the bitstring `01100` (where `q[0]` maps to the highest bit), with probability 1.0.

## isqTrain/1622

- task_id: `isqTrain/1622`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1081`

### Prompt

帮我写一个isQ程序：Apply SWAP(q[0],q[1]) twice (identity) on 4 qubits with q[0]=|1>. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Initialize q[0] to |1> and apply two swap (three-CNOT decomposition) gates between q[0] and q[1] to demonstrate the identity operation.
2. **Qubits**: Uses 4 qubits, all of which are measured at the end.
3. **Evolution**:
   - Start in the ground state |0000>.
   - Apply X(q[0]) to set q[0] to |1>: state becomes |1000>.
   - First swap (three-CNOT decomposition)(q[0], q[1]) swaps the states of q[0] and q[1]: state becomes |0100>.
   - Second swap (three-CNOT decomposition)(q[0], q[1]) swaps them back (swap (three-CNOT decomposition)² = I): state returns to |1000>.
4. **Probabilities**: The final quantum state is deterministically |1000>, yielding a measurement probability of 1.0 for the bitstring `1000`.

## isqTrain/1827

- task_id: `isqTrain/1827`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2620`

### Prompt

Create an isQ quantum circuit that Apply Hadamard gate 4 times to |0> and measure. H^4 = I.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the Hadamard gate four times to |0⟩ and measure, exploiting H⁴ = I.
2. **Qubits**: 1 qubit (`q[0]`), which is measured.
3. **State evolution**:
   - Start: |0⟩
   - H⁺H⁺H⁺H → |0⟩ (since H² = I and thus H⁴ = I)
4. **Expected probabilities**: {|0⟩: 1.0, |1⟩: 0.0}, because the identity operation leaves |0⟩ unchanged, so measurement always yields 0.
