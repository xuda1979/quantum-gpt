# ISQ training COT RAG corpus: circuit_basics shard 4

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4744

- task_id: `isqTrain/4744`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `superposition`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `3902`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    M(q[0]);
}

```

Program B:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    X(q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Compare two isQ programs and determine if they produce the same measurement probability distribution.
    *   Program A: `H(q[0]); M(q[0]);`
    *   Program B: `H(q[0]); X(q[0]); H(q[0]); M(q[0]);`
    *   Constraints: Generate an "Equivalence Analysis" section, 3-8 lines, use Dirac notation, end with a "Yes/No" verdict line. Output only the analysis.

2.  **Analyze Program A:**
    *   Initial state: $|0\rangle$
    *   Gate: $H$
    *   State after H: $H|0\rangle = |+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
    *   Measurement probabilities: $P(0) = 0.5$, $P(1) = 0.5$.

3.  **Analyze Program B:**
    *   Initial state: $|0\rangle$
    *   Gates: $H \cdot X \cdot H$
    *   State after HXH: Note that $HXH = Z$. Wait, let's check the order of operations in the code: `H(q[0]); X(q[0]); H(q[0]);`. The first gate applied to $|0\rangle$ is $H$. The second is $X$. The third is $H$.
    *   Let's trace it:
        1.  $H|0\rangle = |+\rangle$
        2.  $X|+\rangle = |+\rangle$
        3.  $H|+\rangle = |0\rangle$
    *   Wait, is $X|+\rangle = |+\rangle$? Yes, $X$ flips $|0\rangle \leftrightarrow |1\rangle$, so $X(\frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle) = \frac{1}{\sqrt{2}}|1\rangle + \frac{1}{\sqrt{2}}|0\rangle = |+\rangle$.
    *   Then $H|+\rangle = H(H|0\rangle) = |0\rangle$.
    *   Let me re-read the prompt's predicted output!
    *   predicted output: `HXH = Z, so HXH|0> = |0> (deterministic) vs H|0> = |+> (50/50) Program A produces {'0': 1.0} while Program B produces {'0': 0.5, '1': 0.5}.`
    *   Wait. The predicted output: "Program A produces {'0': 1.0} while Program B produces {'0': 0.5, '1': 0.5}." But my calculation shows Program A is $H|0\rangle = |+\rangle$ (50/50) and Program B is $HXH|0\rangle = Z|0\rangle = |0\rangle$ (deterministic).
    *   Wait, is $HXH = Z$?
        $H X H = \frac{1}{2} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} = \frac{1}{2} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} \begin{pmatrix} 1 & -1 \\ 1 & 1 \end{pmatrix} = \frac{1}{2} \begin{pmatrix} 2 & 0 \\ 0 & -2 \end{pmatrix} = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix} = Z$.
        So $HXH|0\rangle = Z|0\rangle = |0\rangle$.
    *   But the predicted output text in the prompt has a typo/flip! "Program A produces {'0': 1.0} while Program B produces {'0': 0.5, '1': 0.5}." This is mathematically backwards. Program A is H. Program B is HXH.
    *   Let me read the prompt again carefully: "predicted output: Equivalent: False. Explanation: HXH = Z, so HXH|0>

### Reference answer

{'equivalent': False, 'explanation': "HXH = Z, so HXH|0> = |0> (deterministic) vs H|0> = |+> (50/50) Program A produces {'0': 1.0} while Program B produces {'0': 0.5, '1': 0.5}.", 'probs_a': {'0': 0.5, '1': 0.5}, 'probs_b': {'0': 1.0}}

## isqTrain/1573

- task_id: `isqTrain/1573`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1948`

### Prompt

Code this in isQ: On 3 qubits, set q[0]=|1> and apply CNOT with control=q[0], target=q[2]. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an X gate to qubit 0 and a CNOT gate between qubits 0 and 2.
2. **Qubits**: 3 qubits ($q[0], q[1], q[2]$) are used and all are measured.
3. **Evolution**:
   - Initialize to $|000\rangle$.
   - Apply X to $q[0]$, evolving state to $|100\rangle$.
   - Apply CNOT($q[0]$, $q[2]$). Since the control $q[0]$ is $|1\rangle$, the target $q[2]$ is flipped to $|1\rangle$, yielding $|101\rangle$.
4. **Probabilities**: The final state is exactly $|101\rangle$, so measurement yields the bitstring `101` with 100% probability.

## isqTrain/4586

- task_id: `isqTrain/4586`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5307`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    Rx(pi/4.0, q[0]);
    H(q[1]); // superposition on last qubit
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: An isQ quantum program.
    *   Task: Predict the probability distribution of measurement outcomes and explain the reasoning.
    *   Constraints: Use Dirac notation, be concise (3-15 lines), output ONLY the analysis starting with "## Circuit Analysis", do NOT include code blocks, end with the predicted probability distribution.
    *   Program:
        

2.  **Step-by-Step Execution:**
    *   *Initial state:* $|00\rangle$
    *   *H(q[0]):* $(|0\rangle + |1\rangle)/\sqrt{2} \otimes |0\rangle = (|00\rangle + |10\rangle)/\sqrt{2}$
    *   *CNOT(q[0], q[1]):* $(|00\rangle + |11\rangle)/\sqrt{2}$ (Bell state $\Phi^+$)
    *   *Rx(\pi/4, q[0]):* Rotates q[0] around X-axis by $\pi/4$. Let's write it carefully.
        $Rx(\theta) = e^{-i\theta X/2} = \cos(\theta/2)I - i\sin(\theta/2)X$.
        Wait, $|0\rangle \to \cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle$.
        $|1\rangle \to -i\sin(\pi/8)|0\rangle + \cos(\pi/8)|1\rangle$.
        Actually, let's keep it in matrix form or use Dirac.
        $Rx(\pi/4)(|00\rangle + |11\rangle)/\sqrt{2}$
        $= (\cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle)|0\rangle/\sqrt{2} + (-i\sin(\pi/8)|0\rangle + \cos(\pi/8)|1\rangle)|1\rangle/\sqrt{2}$
        $= \frac{1}{\sqrt{2}} [\cos(\pi/8)|00\rangle - i\sin(\pi/8)|10\rangle - i\sin(\pi/8)|01\rangle + \cos(\pi/8)|11\rangle]$
    *   *H(q[1]):* Applies Hadamard to q[1].
        $|00\rangle \to (|00\rangle + |01\rangle)/\sqrt{2}$
        $|01\rangle \to (|00\rangle - |01\rangle)/\sqrt{2}$
        $|10\rangle \to (|10\rangle + |11\rangle)/\sqrt{2}$
        $|11\rangle \to (|10\rangle - |11\rangle)/\sqrt{2}$
    *   Substituting these into the state:
        State $= \frac{1}{\sqrt{2}} [\cos(\pi/8)\frac{|00\rangle+|01\rangle}{\sqrt{2}} - i\sin(\pi/8)\frac{|10\rangle+|11\rangle}{\sqrt{2}} - i\sin(\pi/8)\frac{|00\rangle-|01\rangle}{\sqrt{2}} + \cos(\pi/8)\frac{|10\rangle-|11\rangle}{\sqrt{2}}]$
        Let's group by qubit states:
        $|00\rangle$: $\frac{1}{2} [\cos(\pi/8) - i\sin(\pi/8)]$
        $|01\rangle$: $\frac{1}{2} [\cos(\pi/8) + i\sin(\pi/8)]$
        $|10\rangle$: $\frac{1}{2} [-i\sin(\pi/8) + \cos(\pi/8)]$
        $|11\rangle$: $\frac{1}{2} [-i\sin(\pi/8) - \cos(\pi/8)]$

    *   *Wait, look at the amplitudes!*
        Let $c = \cos(\pi/8)$ and $s = \sin(\pi/8)$.
        Amplitude of $|00\rangle$: $(c - is)/2$
        Amplitude of $|01\rangle$: $(c + is)/2$
        Amplitude of $|

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.2500, P(|01>) = 0.2500, P(|10>) = 0.2500, P(|11>) = 0.2500.'}

## isqTrain/4705

- task_id: `isqTrain/4705`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3386`

### Prompt

判断以下两段isQ代码是否产生相同的测量结果：

代码1：
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    S(q[0]);
    H(q[0]);
    M(q[0]);
}

```

代码2：
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    Rz(pi/2.0, q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Role: Quantum computing expert.
    *   Task: Determine if two isQ programs are equivalent in terms of measurement probability distribution.
    *   Program A: `H(q[0]); S(q[0]); H(q[0]); M(q[0]);`
    *   Program B: `H(q[0]); Rz(pi/2.0, q[0]); H(q[0]); M(q[0]);`
    *   Format Requirements: Concise, 3-8 lines for simple, step-by-step reasoning using Dirac notation, no code blocks, output ONLY "## Equivalence Analysis" section, end with a clear "Yes/No" verdict line.

2.  **Analyze Program A:**
    *   Initial state: $|0\rangle$
    *   Apply H: $(|0\rangle + |1\rangle)/\sqrt{2} = |+\rangle$
    *   Apply S: $(|0\rangle + i|1\rangle)/\sqrt{2}$
    *   Apply H: $1/2 ((|0\rangle+|1\rangle) + i(|0\rangle-|1\rangle)) = 1/2 ((1+i)|0\rangle + (1-i)|1\rangle)$
    *   Probabilities: $|(1+i)/2|^2 = 1/2$, $|(1-i)/2|^2 = 1/2$. Outcome: 50% |0>, 50% |1>.

3.  **Analyze Program B:**
    *   Initial state: $|0\rangle$
    *   Apply H: $|+\rangle$
    *   Apply Rz(pi/2): $R_z(\pi/2) = \exp(-i Z \pi/4) = \cos(\pi/4)I - i\sin(\pi/4)Z = \frac{1}{\sqrt{2}}(I - iZ) = \begin{pmatrix} e^{-i\pi/4} & 0 \\ 0 & e^{i\pi/4} \end{pmatrix} = e^{-i\pi/4} \begin{pmatrix} 1 & 0 \\ 0 & i \end{pmatrix} = e^{-i\pi/4} S$.
    *   So, $R_z(\pi/2)$ is equivalent to the $S$ gate up to a global phase ($e^{-i\pi/4}$).
    *   State after Rz: $e^{-i\pi/4} (|0\rangle + i|1\rangle)/\sqrt{2}$. Global phase doesn't affect measurement.
    *   Apply H: $e^{-i\pi/4} \cdot 1/2 ((1+i)|0\rangle + (1-i)|1\rangle)$
    *   Probabilities: $|e^{-i\pi/4} \cdot (1+i)/2|^2 = 1/2$. Outcome: 50% |0>, 50% |1>.

4.  **Compare and Formulate Reasoning:**
    *   Program A applies an S gate between two Hadamard gates.
    *   Program B applies an Rz($\pi/2$) gate between two Hadamard gates.
    *   The key difference is the substitution of S with Rz($\pi/2$). The $R_z(\pi/2)$ gate is equivalent to the S gate up to a global phase $e^{-i\pi/4}$, which does not affect measurement probabilities.
    *   Both circuits map $|0\rangle$ to an equal superposition of $|0\rangle$ and $|1\rangle$.
    *   Verdict: Yes.

5.  **Refine Text (Follow constraints: 3-8 lines, concise, Dirac notation):**
    ## Equivalence Analysis
    1. Program A applies $H \cdot S \cdot H$ to $|0\rangle$, evolving the state to $H \cdot S |+\rangle = H \frac{1}{\sqrt{2}}(|0\rangle + i|1\rangle) = \frac{1}{2}((1+i)|0\rangle + (1-i)|1\rangle)$.
    2. Program B applies $H \cdot R_z(\pi/2) \cdot H$ to $|0\rangle$.
    3. The only difference is the use of $R_z(\pi/2)$ instead of $S$. The $R_z(\pi/2)$ gate equals $e^{-i\pi/4}S$, differing from $S$ only by an undetectable global phase.

### Reference answer

{'equivalent': True, 'explanation': "Rz(pi/2) and S gate are the same operation Both programs produce the same probability distribution: {'0': 0.5, '1': 0.5}.", 'probs_a': {'0': 0.5, '1': 0.5}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/1820

- task_id: `isqTrain/1820`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `609`

### Prompt

Write isQ code for the following quantum task: Apply Ry(pi*10/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply Ry(π*10/6) to |0⟩ and measure the resulting state.

One qubit is needed (q[0]) and is measured.

State evolution:
- Initial state: |0⟩
- Apply Ry(10π/6): This rotates around Y-axis by θ = 10π/6 = 5π/3
- Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩
- θ/2 = 5π/6, so cos(5π/6) = -√3/2 and sin(5π/6) = 1/2
- Final state: (-√3/2)|0⟩ + (1/2)|1⟩

Expected probabilities:
- P(|0⟩) = |−√3/2|² = 3/4 = 0.75
- P(|1⟩) = |1/2|² = 1/4 = 0.25

## isqTrain/4651

- task_id: `isqTrain/4651`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `superposition`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `635`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    Z(q[0]);
    H(q[0]);
    X(q[0]); // additional bit flip
    M(q[0]);
}

```

Second program:
```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A applies the gate sequence H, Z, H, and X to the initial state |0>. This maps |0> -> |+> -> |-> -> |1> -> |0>, leaving the qubit in the |0> state before measurement.
2. Program B applies only the X gate to the initial state |0>, which maps |0> -> |1>, leaving the qubit in the |1> state before measurement.
3. The key difference is the final quantum state prior to measurement: Program A prepares |0>, while Program B prepares |1>.
4. The measurement probabilities are strictly different. Program A yields a 100% probability of measuring 0, whereas Program B yields a 100% probability of measuring 1.
Equivalent: No

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'0': 1.0}, 'probs_b': {'1': 1.0}}

## isqTrain/1802

- task_id: `isqTrain/1802`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1455`

### Prompt

Implement a quantum circuit in isQ: Apply Rx(pi*4/6) to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to prepare the state |0>, apply an Rx rotation of 2π/3 (pi*4/6), and measure the resulting state.
2. One qubit is needed, and it is measured at the end of the circuit.
3. The initial state |0> evolves under Rx(2π/3) to cos(π/3)|0> - i*sin(π/3)|1> = 0.5|0> - i*(√3/2)|1>.
4. The expected measurement probabilities follow directly from squaring the state amplitudes: |0.5|² = 0.25 for |0> and |-i*√3/2|² = 0.75 for |1>.

## isqTrain/4691

- task_id: `isqTrain/4691`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `671`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;
qbit q[1];

procedure main() {
    Z(q[0]);
    M(q[0]);
}

```

Version B:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Applies a Z gate to qubit q[0], which is initialized in the |0> state. The Z gate merely applies a phase to |1>, leaving the |0> state unchanged (up to global phase).
2. **Program B**: Applies an H (Hadamard) gate to q[0], transforming the initial |0> state into the superposition |+> = (|0> + |1>) / sqrt(2).
3. **Key difference**: Program A leaves the qubit in a deterministic basis state (|0>), while Program B introduces superposition.
4. **Probabilities**: Program A measures |0> with 100% probability (P(0)=1, P(1)=0). Program B measures |0> with 50% probability and |1> with 50% probability (P(0)=0.5, P(1)=0.5).
5. **Verdict**: No

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'0': 1.0}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/1779

- task_id: `isqTrain/1779`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `4870`

### Prompt

I need an isQ program to Apply X gate 11 times to |0> and measure. (X^11 = X.)

### Chain-of-thought reasoning

## Reasoning
Goal: Apply X gate 11 times to a single qubit initialized to |0⟩ and measure.

Qubits: 1 qubit (q[0]), which is measured.

State evolution:
- Initial state: |0⟩
- Each X gate flips the qubit: X|0⟩ = |1⟩, X|1⟩ = |0⟩
- Since X² = I, applying X 11 times (odd number) is equivalent to applying X once
- After 11 X gates: X¹¹|0⟩ = X|0⟩ = |1⟩

Expected probabilities: {|1⟩: 1.0}, because an odd number of X gates on |0⟩ always yields |1⟩.

## isqTrain/1832

- task_id: `isqTrain/1832`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1810`

### Prompt

Create an isQ quantum circuit that Apply the gate sequence XYZ on |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. The goal is to apply the gate sequence XYZ to a qubit initialized to |0> and measure the result.
2. The circuit requires 1 qubit, and 1 is measured.
3. State evolution:
   - Start: |0>
   - X gate: |0> -> |1>
   - Y gate: |1> -> i|0>
   - Z gate: i|0> -> i|0>
4. The final state is i|0>, which is equivalent to |0> up to a global phase, resulting in a 100% probability of measuring 0.
