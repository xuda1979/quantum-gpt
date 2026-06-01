# ISQ training COT RAG corpus: deutsch_jozsa shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3306

- task_id: `isqTrain/3306`
- task_type: `code_generation`
- category: `deutsch_jozsa`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`
- source: `isq_train_cot`
- dataset_index: `986`

### Prompt

Create an isQ quantum circuit that an isQ program: 2-bit Deutsch-Jozsa with constant-0 oracle. Use 3 qubits (2 query + 1 ancilla).

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement 2-bit Deutsch-Jozsa algorithm with constant-0 oracle to demonstrate that $f(x)=0$ is constant.

2. **Qubits**: 3 qubits — q[0], q[1] (query register), q[2] (ancilla); all 3 measured.

3. **State evolution**:
   - Start: $|000\rangle$
   - $X(q[2])$: $|001\rangle$
   - $H(q[2])$: $|00\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}} = |00{-}\rangle$
   - $H(q[0])H(q[1])$: $\frac{|00\rangle+|01\rangle+|10\rangle+|11\rangle}{2} \otimes |{-}\rangle = |{++}\rangle|{-}\rangle$
   - Oracle ($f=0$, no gates): state unchanged (phase factor $(-1)^{f(x)}=1$)
   - $H(q[0])H(q[1])$: $|00\rangle \otimes |{-}\rangle$

4. **Probabilities**: The query register collapses to $|00\rangle$ with certainty. The ancilla $|-\rangle = \frac{|0\rangle-|1\rangle}{\sqrt{2}}$ gives equal probability for |0⟩ and |1⟩. With q[0] as highest bit in bitstring: $\{|000\rangle: 0.5, |001\rangle: 0.5\}$.

## isqTrain/3122

- task_id: `isqTrain/3122`
- task_type: `code_generation`
- category: `deutsch_jozsa`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1577`

### Prompt

Write isQ code for the following quantum task: an isQ program: 1-bit Deutsch algorithm with constant-0 function. Use 2 qubits. Initialize q[0] with H (query), q[1] with X then H (ancilla). Apply oracle, then H on q[0], measure both.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement 1-bit Deutsch algorithm with constant-0 oracle to demonstrate constant function detection.

Two qubits used: q[0] (query) and q[1] (ancilla), both measured.

State evolution:
1. |00⟩ → H(q[0]) → (|0⟩+|1⟩)/√2 ⊗ |0⟩
2. → X(q[1]); H(q[1]) → (|0⟩+|1⟩)/√2 ⊗ (|0⟩−|1⟩)/√2
3. Oracle f(x)=0 (identity): state unchanged
4. → H(q[0]) → |0⟩ ⊗ (|0⟩−|1⟩)/√2 = (|00⟩−|01⟩)/√2

Expected probabilities: |00⟩: 0.5, |01⟩: 0.5 — equal superposition over q[1] while q[0] collapses to |0⟩, confirming constant function (query qubit always measures 0).

## isqTrain/3123

- task_id: `isqTrain/3123`
- task_type: `code_generation`
- category: `deutsch_jozsa`
- difficulty: `intermediate`
- concept_tags: `superposition`, `interference`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3578`

### Prompt

帮我写一个isQ程序：an isQ program: 1-bit Deutsch algorithm with balanced-NOT function. Use 2 qubits. Initialize q[0] with H (query), q[1] with X then H (ancilla). Apply oracle, then H on q[0], measure both.

### Chain-of-thought reasoning

Step 1: Understand the goal of the Deutsch algorithm.
The Deutsch algorithm determines if a 1-bit function $f(x)$ is constant ($f(0)=f(1)$) or balanced ($f(0) \neq f(1)$) using only one query.
The problem asks for the balanced-NOT function, $f(x) = x$ (or $f(x) = x \oplus c$, but balanced-NOT usually implies $f(x) = x$ or $f(x) = \neg x$, here it's $x$).
Wait, $f(x) = x$ means $f(0)=0, f(1)=1$, which is balanced.

Step 2: Identify qubits and measurements.
2 qubits: `q[0]` (query) and `q[1]` (ancilla). Both are measured.

Step 3: Trace quantum state evolution.
Initial state: $|00\rangle$.
Apply $H$ to `q[0]`: $|+0\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
Apply $X$ then $H$ to `q[1]`: $X$ makes it $|1\rangle$, $H$ makes it $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
Overall state before oracle: $\frac{1}{2}(|0\rangle + |1\rangle) \otimes (|0\rangle - |1\rangle)$.
Oracle for $f(x) = x$ is CNOT(q[0], q[1]).
Since the target is in $|-\rangle$, CNOT leaves the target unchanged up to a phase depending on the control.
Wait, $CNOT (|x\rangle \otimes |-\rangle) = (-1)^x |x\rangle \otimes |-\rangle$.
Let's trace:
$|0\rangle(|0\rangle - |1\rangle) \to |0\rangle(|0\rangle - |1\rangle)$
$|1\rangle(|0\rangle - |1\rangle) \to |1\rangle(|1\rangle - |0\rangle) = -|1\rangle(|0\rangle - |1\rangle)$
So the state after CNOT is $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) \otimes |-\rangle$.
Then apply $H$ to `q[0]`:
$H(|0\rangle - |1\rangle) = |1\rangle$.
So the state becomes $|1\rangle \otimes |-\rangle = |1\rangle \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = \frac{1}{\sqrt{2}}(|10\rangle - |11\rangle)$.

Step 4: Determine probabilities.
State is $\frac{1}{\sqrt{2}}(|10\rangle - |11\rangle)$.
Measuring both qubits gives:
$|10\rangle$ with probability $|\frac{1}{\sqrt{2}}|^2 = 0.5$.
$|11\rangle$ with probability $|-\frac{1}{\sqrt{2}}|^2 = 0.5$.

Let's double check. Is it $|1\rangle$ for query? Yes, for a balanced function, the query qubit ends up as $|1\rangle$. The ancilla qubit remains in $|-\rangle$, which is an equal superposition of $|0\rangle$ and $|1\rangle$.

Structure of reasoning:
1. Goal: Distinguish balanced function $f(x)=x$ from constant functions using a single query in the Deutsch algorithm.
2. Qubits: 2 (`q[0]` as query, `q[1]` as ancilla); both are measured.
3. State evolution:
   - Start: $|00\rangle$.
   - $H(q[0])$, $X(q[1])$, $H(q[1]) \to \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |-\rangle$.
   - CNOT$(q[0], q[1])$ phase-kicks back $-1$ when $q[0]$ is $|1\rangle \to \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) \otimes |-\rangle$.
   - $H(q[0])$ maps $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$ to $|1\rangle$.
   - Final state
