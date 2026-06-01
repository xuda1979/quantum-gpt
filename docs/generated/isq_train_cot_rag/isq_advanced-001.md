# ISQ training COT RAG corpus: isq_advanced shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1634

- task_id: `isqTrain/1634`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `basic`
- concept_tags: `isq_syntax_inv`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4138`

### Prompt

Implement the following in isQ: Apply T then inv T (T-dagger) to |0>. Result should be |0>.

### Chain-of-thought reasoning

## Reasoning
- Goal: Verify that applying T followed by its inverse returns the qubit to its original state.
- Qubits: 1 qubit (q[0]), which is measured.
- Evolution:
  1. Initial state: |0⟩
  2. T gate: T|0⟩ = |0⟩ (T leaves |0⟩ unchanged, as T = diag(1, e^{iπ/4}))
  3. inv T gate: T†|0⟩ = |0⟩ (T† cancels T exactly)
- Expected measurement: {|0⟩: 1.0}, since the final state is |0⟩.

## isqTrain/4608

- task_id: `isqTrain/4608`
- task_type: `output_prediction`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5138`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;

qbit q[1];
qbit p[1];

procedure oracleA(qbit a) {
    X(a);
}

procedure oracleB(qbit a) {
    Z(a);
}

procedure execute_oracle(qbit target, unit op(qbit)) {
    H(target);
    op(target);
    H(target);
}

procedure main() {
    execute_oracle(q[0], oracleA); 
    execute_oracle(p[0], oracleB); 
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(p[0]); 
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a concise step-by-step reasoning for the given isQ quantum program, predicting the measurement probability distribution. The output must follow specific formatting rules (start with "## Circuit Analysis", no code blocks, end with probability distribution).

2.  **Analyze the Code**:
    *   Initialization: `qbit q[1]; qbit p[1];` -> both `|0>` initially. State is `|00>`.
    *   `execute_oracle(q[0], oracleA)` -> Applies `H(q[0])`, `X(q[0])`, `H(q[0])`.
        *   Initial: `|0>` -> H -> `|+>` -> X -> `|+>` -> H -> `|0>`.
        *   Result: `q[0]` is `|0>`.
    *   `execute_oracle(p[0], oracleB)` -> Applies `H(p[0])`, `Z(p[0])`, `H(p[0])`.
        *   Initial: `|0>` -> H -> `|+>` -> Z -> `|->` -> H -> `|1>`.
        *   Result: `p[0]` is `|1>`.
    *   State after oracles: `|01>`.
    *   `H(q[0]); Z(q[0]); H(q[0]);`
        *   `q[0]` is `|0>` -> H -> `|+>` -> Z -> `|+>` -> H -> `|0>`.
        *   Alternatively, HZH = X. So `X(q[0])`.
        *   Result: `q[0]` is `|0>`.
    *   Wait, let me re-evaluate `HZH`.
        *   HZH = X. So `X(|0>) = |1>`.
        *   Let's check: `|0>` -> H -> `|+>` -> Z -> `|+>` -> H -> `|0>`. Wait.
        *   $H Z H = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix} \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} = \frac{1}{2} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} \begin{pmatrix} 1 & 1 \\ -1 & 1 \end{pmatrix} = \frac{1}{2} \begin{pmatrix} 0 & 2 \\ 2 & 0 \end{pmatrix} = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix} = X$.
        *   Yes, HZH is X.
        *   Wait, the code says: `H(q[0]); Z(q[0]); H(q[0]);`
        *   So $H Z H |0\rangle = X |0\rangle = |1\rangle$.
        *   Let me re-read my manual check: $|0\rangle \xrightarrow{H} |+\rangle \xrightarrow{Z} |+\rangle \xrightarrow{H} |0\rangle$.
        *   Wait, $Z |+\rangle = Z \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = |-\rangle$.
        *   Then $H |-\rangle = H \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = \frac{1}{2}(|0\rangle + |1\rangle - |0\rangle + |1\rangle) = |1\rangle$.
        *   Yes! $HZH |0\rangle = |1\rangle$.
        *   So `q[0]` becomes `|1>`.
    *   `p[0]` is `|1>` (from $HZH |0\rangle = |1\rangle$ applied to p[0] via oracleB).
        *   Wait, $H Z H |0\rangle = |1\rangle$. oracleB applies H, Z, H. So p[0] becomes $|1\rangle$.
    *   So before the final line, `q[0]` is $|0\rangle$ (from oracle

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 1.0000.'}

## isqTrain/1639

- task_id: `isqTrain/1639`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1169`

### Prompt

Code this in isQ: Apply nctrl X to |11>. Control is |1> so no flip, stays |11>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Initialize the system to |11> and apply a negatively controlled X gate (flip target only when control is |0>).
2. **Qubits**: 2 qubits (`q[0]`, `q[1]`), both are measured.
3. **Evolution**: 
   - Initial state is |00>.
   - `X(q[0]); X(q[1])` transforms the state to |11>.
   - `nctrl X(q[0], q[1])` evaluates the control qubit `q[0]`. Since it is in state |1>, the condition (control = |0>) for the negative control is not met, and the target qubit `q[1]` is not flipped.
   - The state remains |11>.
4. **Probabilities**: The final quantum state is exactly |11>, yielding a 100% probability of measuring the bitstring `11`.

## isqTrain/1974

- task_id: `isqTrain/1974`
- task_type: `output_prediction`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `isq_syntax_procedures`, `multi_controlled_logic`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `944`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[3];
procedure mcp() {
    ctrl<2> Z(q[0], q[1], q[2]);
}
procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    mcp();
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the measurement probabilities of an isQ program.
    *   Program: 3 qubits, each applied H, then a `ctrl<2> Z(q[0], q[1], q[2])` (which is a double-controlled-Z (ctrl @[c1, c2] Z(target)) gate), then measured.
    *   Output format: "## Circuit Analysis", step-by-step reasoning, concise (3-15 lines), ending with the predicted probability distribution.

2.  **Analyze the isQ Program:**
    *   Initialization: `q[0], q[1], q[2]` start at `|000>`.
    *   Apply H to all: `H(q[0]); H(q[1]); H(q[2]);` -> state becomes `|+++>`.
        $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
        $|+++\rangle = \frac{1}{2\sqrt{2}}(|000\rangle + |001\rangle + |010\rangle + |011\rangle + |100\rangle + |101\rangle + |110\rangle + |111\rangle)$.
    *   Apply `ctrl<2> Z(q[0], q[1], q[2]);` -> This is a doubly-controlled Z gate (double-controlled-Z (ctrl @[c1, c2] Z(target))). It applies a Z gate to `q[2]` if `q[0]` and `q[1]` are both `|1>`. Since Z acts as `|1\rangle \to -|1\rangle`, the double-controlled-Z (ctrl @[c1, c2] Z(target)) gate flips the phase of the `|111>` basis state.
        New state: $\frac{1}{2\sqrt{2}}(|000\rangle + |001\rangle + |010\rangle + |011\rangle + |100\rangle + |101\rangle + |110\rangle - |111\rangle)$.
    *   Measurement: `M(q[0]); M(q[1]); M(q[2]);`
    *   Probability calculation: Since all amplitudes have magnitude $\frac{1}{2\sqrt{2}}$, the probability for each state is $(\frac{1}{2\sqrt{2}})^2 = \frac{1}{8} = 0.125$.

3.  **Draft the Circuit Analysis (concise):**
    *   Start with `|000>`. Apply H gates to all qubits, creating the uniform superposition `|+++> = 1/sqrt(8) * (|000> + |001> + ... + |111>)`.
    *   Apply the `ctrl<2> Z` gate (double-controlled-Z (ctrl @[c1, c2] Z(target)) gate). This adds a phase of -1 to the `|111>` component.
    *   The final state is $1/\sqrt{8} \sum_{x \in \{0,1\}^3} (-1)^{x_0 x_1 x_2} |x\rangle$.
    *   Since the amplitude magnitudes are all $1/\sqrt{8}$, measuring all qubits yields an equal probability of 1/8 (12.5%) for each of the 8 possible outcomes.
    *   Format output as requested.

4.  **Refine constraints:**
    *   3-8 lines (this is simple, so keep it short).
    *   Start with "## Circuit Analysis".
    *   End with predicted probabilities.
    *   no code blocks.
    *   Dirac notation used.

5.  **Finalizing the text:**
    ## Circuit Analysis
    1. The circuit initializes 3 qubits in `|000>` and applies an H gate to each, creating the uniform superposition `|+++> = 1/√8 * (|000> + |001> + ... + |111>)`.
    2. The `ctrl<2> Z` (double-controlled-Z (ctrl @[c1, c2] Z(target))) gate applies a Z gate to the target qubit when both controls are `|1>`. This flips the phase of the `|111>` basis state.
    3. The resulting state is `1/√8 * (|000> + |001> + |010> + |011> + |100> + |101> + |110> - |111>)`.
    4. Because the absolute magnitude of each basis state's amplitude is equal, the probabilities of measuring each bitstring are uniformly distributed.

    Predicted probability distribution:
    {'000': 0.125, '001': 0.125, '010': 0.125, '011': 0.125, '100': 0.125, '101': 0.125, '110': 0.125, '111':

### Reference answer

{'predicted_probs': {'000': 0.125, '001': 0.125, '010': 0.125, '011': 0.125, '100': 0.125, '101': 0.125, '110': 0.125, '111': 0.125}, 'explanation': 'Doubly-controlled Z gate (ctrl<2> Z) on |111⟩ with H to observe phase.'}

## isqTrain/1629

- task_id: `isqTrain/1629`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1572`

### Prompt

Code this in isQ: Apply a Toffoli gate (double-controlled X) to the state |010> using `ctrl ctrl X` syntax. Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply a Toffoli gate (double-controlled X) to the state |010> and measure all 3 qubits.
Three qubits q[0], q[1], q[2] are used, and all are measured.
State evolution: |000> →(X on q[1])→ |010> →(ctrl ctrl X with controls q[0],q[1], target q[2])→ |010>.
The Toffoli gate flips the target only when both controls are |1>. Here q[0]=|0>, so the condition fails and the state remains |010>.
Expected measurement probability is {|010>: 1.0} since the Toffoli gate doesn't activate.

## isqTrain/536

- task_id: `isqTrain/536`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `5530`

### Prompt

Code this in isQ: implements a variant of the gate_decomposition pattern using w[5] -> w[6]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

1. We have a 6-qubit register w[6], but only 5 qubits are measured (w[0] through w[4]).

2. First loop (i from 0 to 3):
   - X2P(w[i]) = Rx(π/2) on w[i]
   - Y2P(w[i+1]) = Ry(π/2) on w[i+1]
   - CNOT(w[i], w[i+1])

3. Second loop (triple nested loop with i, j, k from 0 to 3):
   - H(w[(i+j+k) % 5])

4. Measurement of w[0] to w[4]

Let me trace through this more carefully.

Initial state: |000000>

First loop (i=0):
- X2P(w[0]): Rx(π/2) on w[0] → takes |0⟩ to (|0⟩ - i|1⟩)/√2
- Y2P(w[1]): Ry(π/2) on w[1] → takes |0⟩ to (|0⟩ + |1⟩)/√2
- CNOT(w[0], w[1])

After X2P(w[0]) and Y2P(w[1]):
State is (|0⟩ - i|1⟩)/√2 ⊗ (|0⟩ + |1⟩)/√2 ⊗ |0000⟩
= (|00⟩ + |01⟩ - i|10⟩ - i|11⟩)/2 ⊗ |0000⟩

CNOT(w[0], w[1]):
= (|00⟩ + |01⟩ - i|11⟩ - i|10⟩)/2 ⊗ |0000⟩
= (|00⟩ + |01⟩ - i|10⟩ - i|11⟩)/2 ⊗ |0000⟩

Wait, let me recalculate. CNOT with w[0] as control and w[1] as target:
- |00⟩ → |00⟩
- |01⟩ → |01⟩
- |10⟩ → |11⟩
- |11⟩ → |10⟩

So (|00⟩ + |01⟩ - i|10⟩ - i|11⟩)/2 ⊗ |0000⟩
After CNOT: (|00⟩ + |01⟩ - i|11⟩ - i|10⟩)/2 ⊗ |0000⟩
= (|00⟩ + |01⟩ - i|10⟩ - i|11⟩)/2 ⊗ |0000⟩

Hmm, that's the same thing because -i|10⟩ → -i|11⟩ and -i|11⟩ → -i|10⟩, so it swaps them but the sum is the same.

Let me continue with i=1:
- X2P(w[1])
- Y2P(w[2])
- CNOT(w[1], w[2])

This is getting complex. Let me think about the predicted output.

the predicted output show that only states with w[5] = 0 are measured (since we only measure w[0:5]), and the probabilities are:
|00000⟩: 0.125
|00100⟩: 0.125
|01000⟩: 0.125
|01100⟩: 0.125
|10000⟩: 0.125
|10100⟩: 0.125
|11000⟩: 0.125
|11100⟩: 0.125

So the states are all superpositions of states where qubits 0,1,2,3,4 have specific patterns. Looking at the bitstrings:
- w[4] = 0 always
- w[3] = 0 always  
- w[2] varies (gives the 001 and 000 patterns)
- w[1] and w[0] vary freely

Wait, let me re-read. Earlier measured qubit = higher bit. So if we measure w[0], w[1], w[2], w[3], w[4] in order, then w[0] is the highest bit.

So |00000⟩ means w[0]=0, w[1]=0, w[2]=0, w[3]=0, w[4]=0
|00100⟩ means w[0]=0, w[1]=0, w[2]=1, w[3]=0, w[4]=0
|01000⟩ means w[0]=0, w[1]=1, w[2]=0, w[3]=0, w[4]=0
etc.

So w[3] = 0 and w[4] = 0 always (the last two

## isqTrain/490

- task_id: `isqTrain/490`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5402`

### Prompt

用isQ实现implements the qft_subcircuit pattern but with a different initial state preparation (flip q[[0]] -> q[1]).

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

1. The circuit prepares a 3-qubit state |100⟩ (by applying X to q[1]) and then applies QFT.

Wait, let me re-read. The implementation says `X(q[1])` prepares |100⟩. But if we have q[0], q[1], q[2], and we apply X to q[1], that flips q[1], giving us |010⟩, not |100⟩.

Hmm, actually looking at the predicted output - it's a uniform distribution over all 8 states (each with probability 1/8). This is consistent with QFT of |010⟩.

Let me trace through:

Initial state: |000⟩

After X(q[1]): |010⟩

QFT of |010⟩:

QFT acts on computational basis states. QFT|k⟩ = (1/√N) Σ_j e^(2πijk/N) |j⟩ where N = 2^n.

For |010⟩ = |2⟩ in 3 qubits:
QFT|2⟩ = (1/√8) Σ_{j=0}^{7} e^(2πi·2·j/8) |j⟩
= (1/√8) Σ_j e^(πij/2) |j⟩

j=0: e^0 = 1
j=1: e^(iπ/2) = i
j=2: e^(iπ) = -1
j=3: e^(3iπ/2) = -i
j=4: e^(2iπ) = 1
j=5: e^(5iπ/2) = i
j=6: e^(3iπ) = -1
j=7: e^(7iπ/2) = -i

So QFT|2⟩ = (1/√8)(|0⟩ + i|1⟩ - |2⟩ - i|3⟩ + |4⟩ + i|5⟩ - |6⟩ - i|7⟩)

Each amplitude has magnitude 1/√8, so each probability is 1/8 = 0.125.

This matches the predicted output perfectly.

Now for the task: "implements the qft_subcircuit pattern but with a different initial state preparation (flip q[[0]] -> q[1])"

Wait, The implementation already flips q[1]. The prompt says "flip q[[0]] -> q[1]" which means change from flipping q[0] to flipping q[1]. So the original pattern would have X(q[0]), and now we change it to X(q[1]).

But The implementation already has X(q[1])... So I think the task is asking me to explaIn the implementation, not generate new code.

Actually, looking at the task type "code_generation" and the prompt asking to "Write an isQ program", but then it gives a circuit implementation. I think I just need to generate the reasoning.

Let me trace the QFT more carefully:

Starting with |010⟩:

QFT on 3 qubits with the standard algorithm (Hadamard + controlled rotations, then bit reversal):

Step 1: Process q[0] (i=0):
- H on q[0]: |010⟩ → |010⟩ ⊗ (|0⟩+|1⟩)/√2 but wait, q[0] is already |0⟩ in |010⟩
  State: 1/√2(|010⟩ + |110⟩)
- CRz(π/2, q[1], q[0]): controlled Rz with angle π/2
  When q[0] is |1⟩ and q[1] is |1⟩... wait, this is ctrl Rz(angle, arr[j], arr[i])
  
  For i=0, j=1: ctrl Rz(π, arr[1], arr[0]) - wait angle = pi/(1<<(j-i)) = pi/(1<<1) = pi/2
  
  ctrl Rz(π/2, q[1], q[0]): applies Rz(π/2) to q[1] controlled by q[0]
  
  When q[0]=1: Rz(π/2) on q[1]. q[1] is |1⟩, so Rz(π/2)|1⟩ = e^(-iπ/4)|1⟩
  
  State: 1/√2(|010⟩ + e^(-iπ/4)|110⟩)
  
  For i=0, j=2: ctrl Rz(π/4, q[2], q[0])
  
  When q[0]=1: Rz(π/4) on q[2]. q[

## isqTrain/1697

- task_id: `isqTrain/1697`
- task_type: `code_generation`
- category: `isq_advanced`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1199`

### Prompt

Write an isQ program that Define a procedure that applies X gate n times, call it with n=2. Measure the result.

### Chain-of-thought reasoning

## Reasoning
The goal of this circuit is to apply the Pauli-X gate twice to an initial qubit and measure the final state.
One qubit is used, which is initialized to |0> and measured at the end.
The first X gate flips the qubit from |0> to |1>, and the second X gate flips it back from |1> to |0>.
Since the final quantum state is deterministically |0>, the measurement outcome will be 0 with a probability of 1.0.

## isqTrain/538

- task_id: `isqTrain/538`
- task_type: `output_prediction`
- category: `isq_advanced`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4339`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;

qbit w[5];
procedure main() {
    for i in 0:3{
        X2P(w[i]);
        Y2P(w[i+1]);
        CNOT(w[i], w[i+1]);
    }
    for i in 0:3{
        for j in 0:3{
            for k in 0:3{
                H(w[(i+j+k) % 5]);
            }
        }
    }
    for i in 0:5{
        M(w[i]);
    }
}
```

### Chain-of-thought reasoning

The isQ program does the following:
1. Initialize a 5-qubit register `w[5]` to |00000>.
2. Apply a sequence of `X2P(w[i])`, `Y2P(w[i+1])`, and `CNOT(w[i], w[i+1])` for `i` from 0 to 3.
3. Apply `H` gates in a triple nested loop over indices `(i+j+k) % 5`.
4. Measure all 5 qubits.

Let's trace the first loop for `i` from 0 to 3.
X2P is Rx(pi/2) = (1/sqrt(2)) [[1,-i],[-i,1]]
Y2P is Ry(pi/2) = (1/sqrt(2)) [[1,-1],[1,1]]
CNOT flips target if control is 1.

Initial state: |00000>

i = 0:
X2P(w[0]) acts on w[0]: |0> -> (1/sqrt(2))(|0> - i|1>)
Y2P(w[1]) acts on w[1]: |0> -> (1/sqrt(2))(|0> + |1>)
State so far: (1/2) (|00> - i|10> + |01> - i|11>) |000>
CNOT(0, 1): control=0, target=1.
-> (1/2) (|00> - i|11> + |01> - i|10>) |000>

i = 1:
X2P(w[1]):
|00> -> (1/sqrt(2))|0>(|0>-i|1>)
|11> -> (1/sqrt(2))|1>(|0>-i|1>)
|01> -> (1/sqrt(2))|0>(|0>+i|1>)
|10> -> (1/sqrt(2))|1>(|0>+i|1>)
Wait, let's apply X2P to the actual superposition:
State before X2P(w[1]) is (1/2) (|00> - i|11> + |01> - i|10>) |000>
Apply X2P to qubit 1:
|0> -> (|0> - i|1>)/sqrt(2)
|1> -> (-i|0> + |1>)/sqrt(2)
So:
|00> -> (1/sqrt(2))|0>(|0>-i|1>)
|11> -> (1/sqrt(2))|1>(-i|0>+|1>)
|01> -> (1/sqrt(2))|0>(-i|0>+|1>)
|10> -> (1/sqrt(2))|1>(|0>-i|1>)
Summing these up (multiplied by 1/2 and with their signs):
(1/2) * (1/sqrt(2)) [ |00> - i|01> - i|11> + |10> - i|00> + |01> + |10> - i|11> ]
= (1/(2sqrt(2))) [ (1-i)|00> + (-i+1)|01> + (1+1)|10> + (-i-i)|11> ]
= (1/(2sqrt(2))) [ (1-i)|00> + (1-i)|01> + 2|10> - 2i|11> ]

Then Y2P(w[2]):
|0> -> (|0> + |1>)/sqrt(2)
|1> -> (-|0> + |1>)/sqrt(2)
This just multiplies each term by (|0>+|1>) or (-|0>+|1>) for qubit 2.
State becomes (1/4) [ (1-i)|000> + ... ] (multiplied by |00> for qubits 3, 4)
Then CNOT(1, 2): control=1, target=2.
Let's simplify the state of qubits 0, 1, 2.
Actually, we can just look at the final expected probabilities.
The probabilities are expected to be exactly equal for 8 states, and 0 for the others.
Let's see: Expected probabilities are equally distributed among 8 states where qubits 3 and 4 are |00>.
Wait! The expected measurement probabilities only list states ending in `00` (w[3] and w[4] are 0).
Let's check the code:
The first loop `for i in 0:3` applies CNOT(w[i], w[i+1]).
When i=2, X2P(w[2]), Y2

### Reference answer

{'predicted_probs': {'0': 0.12500000000000003, '4': 0.12499999999999986, '8': 0.1250000000000001, '12': 0.12500000000000003, '16': 0.12499999999999997, '20': 0.12499999999999994, '24': 0.12500000000000006, '28': 0.12499999999999994}, 'explanation': 'Parametric variant of isqHumanEval/164. Dimension: predict probabilities for reference circuit.'}

## isqTrain/4648

- task_id: `isqTrain/4648`
- task_type: `output_prediction`
- category: `isq_advanced`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2493`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

qbit q[2];
qbit anc[1];

procedure my_dj_oracle() {
    CNOT(q[0], anc[0]);
    nctrl X(q[1], anc[0]);
} deriving gate

procedure main() {
    
    H(q);
    X(anc[0]); 
    H(anc[0]);
    
    my_dj_oracle();
    
    
    
    
    
    H(q);
    H(q[1]); // superposition on last qubit
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    *   Initialization: 3 qubits total (`q[0]`, `q[1]`, `anc[0]`). Initial state is $|0\rangle^{\otimes 3} = |000\rangle$.
    *   `H(q);`: Applies H to `q[0]` and `q[1]`. State becomes $\frac{1}{\sqrt{2}}(|0\rangle+|1\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle+|1\rangle) \otimes |0\rangle = \frac{1}{2}(|00\rangle+|01\rangle+|10\rangle+|11\rangle)\otimes|0\rangle$.
    *   `X(anc[0]); H(anc[0]);`: Applies X and H to `anc[0]`. `anc[0]` goes from $|0\rangle \xrightarrow{X} |1\rangle \xrightarrow{H} |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$. Total state is $\frac{1}{2}(|00\rangle+|01\rangle+|10\rangle+|11\rangle)\otimes|-\rangle$.
    *   `my_dj_oracle()`:
        *   `CNOT(q[0], anc[0])`: Flips `anc[0]` if `q[0]` is 1. Effectively maps $|x\rangle|-\rangle \to (-1)^{x_0}|x\rangle|-\rangle$.
        *   `nctrl X(q[1], anc[0])`: This is a negative control. Flips `anc[0]` if `q[1]` is $|0\rangle$. Wait, let's trace this exactly.
        *   State before oracle: $\frac{1}{2}(|00\rangle+|01\rangle+|10\rangle+|11\rangle)\otimes|-\rangle$.
        *   Apply `CNOT(q[0], anc[0])`:
            *   $|00\rangle|-\rangle \to |00\rangle|-\rangle$
            *   $|01\rangle|-\rangle \to |01\rangle|-\rangle$
            *   $|10\rangle|-\rangle \to |10\rangle X|-\rangle = -|10\rangle|-\rangle$
            *   $|11\rangle|-\rangle \to |11\rangle X|-\rangle = -|11\rangle|-\rangle$
            *   State: $\frac{1}{2}(|00\rangle+|01\rangle-|10\rangle-|11\rangle)\otimes|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle-|1\rangle)\otimes\frac{1}{\sqrt{2}}(|0\rangle+|1\rangle)\otimes|-\rangle$.
        *   Apply `nctrl X(q[1], anc[0])`: Flips target if `q[1]` is $|0\rangle$.
            *   $|00\rangle|-\rangle \to |00\rangle X|-\rangle = -|00\rangle|-\rangle$
            *   $|01\rangle|-\rangle \to |01\rangle|-\rangle$
            *   $|10\rangle|-\rangle \to -|10\rangle X|-\rangle = |10\rangle|-\rangle$
            *   $|11\rangle|-\rangle \to -|11\rangle X|-\rangle = |11\rangle|-\rangle$
            *   State: $\frac{1}{2}(-|00\rangle+|01\rangle+|10\rangle-|11\rangle)\otimes|-\rangle = \frac{1}{2}(-|0\rangle+|1\rangle)\otimes\frac{1}{\sqrt{2}}(|0\rangle+|1\rangle)\otimes|-\rangle$.
            *   Actually, the function evaluates to $f(x_0, x_1) = x_0 \oplus \bar{x_1}$. Phase kickback gives $(-1)^{x_0 \oplus \bar{x_1}} = (-1)^{x_0}(-1)^{\bar{x_1}}$. So `q[0]` has phase $(-1)^{x_0}$, `q[1]` has phase $(-1)^{\bar{x_1}}$. This makes `q[0]` in $

### Reference answer

{'predicted_probs': {'00': 0.5, '01': 0.5}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.5000, P(|01>) = 0.5000.'}
