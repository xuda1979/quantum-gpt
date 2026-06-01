# ISQ training COT RAG corpus: isq_defgate shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1901

- task_id: `isqTrain/1901`
- task_type: `output_prediction`
- category: `isq_defgate`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4636`

### Prompt

What does this isQ program output when measured?

```isq
import std;
defgate Fredkin(3) = perm [0, 1, 2, 3, 4, 6, 5, 7];
qbit q[3];
procedure main() {
    X(q[0]);
    X(q[1]);
    Fredkin(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Predict measurement outcome probabilities of a given isQ program.
    *   **Input Program:** Initializes 3 qubits to |000>. Applies X to q[0] and X to q[1]. Then applies a controlled-swap operation (three-CNOT decomposition) `controlled-swap (three-CNOT decomposition)(q[0], q[1], q[2])` defined as `perm [0, 1, 2, 3, 4, 6, 5, 7]`.
    *   **Requirements:** Provide 3-8 lines for simple circuits (this is simple). Use Dirac notation. Start with "## Circuit Analysis". End with predicted probability distribution. Do not include code blocks.

2.  **Analyze the Circuit:**
    *   Initial state: |000>.
    *   `X(q[0]); X(q[1]);`: State becomes |011>. (Assuming standard bit ordering, q[0] is the rightmost or leftmost depending on convention, but in isQ standard `q[0]` is usually the first qubit. Let's trace carefully. If q[0]=1, q[1]=1, q[2]=0, state is |110> or |011> depending on bit significance. Let's assume standard ordering: `q[0]` is bit 0 (least significant), `q[1]` is bit 1, `q[2]` is bit 2. So |110>. Wait, the prompt asks for probability distribution based on measurement bitstrings where "earlier measured qubit = higher bit". `M(q[0])` is bit 2, `M(q[1])` is bit 1, `M(q[2])` is bit 0. Let's trace state evolution first).
    *   Let's define state as $|q_2 q_1 q_0\rangle$. Initial: |000>.
    *   `X(q[0])`: |001>
    *   `X(q[1])`: |011>
    *   `controlled-swap (three-CNOT decomposition)(q[0], q[1], q[2])` with permutation `[0, 1, 2, 3, 4, 6, 5, 7]`.
        *   A 3-qubit state has basis states 0 to 7: |000> (0) to |111> (7).
        *   The permutation maps index $i$ to index $P[i]$.
        *   So basis state 5 ($|101\rangle$, or $|q_2=1, q_1=0, q_0=1\rangle$) maps to 6 ($|110\rangle$), and 6 maps to 5.
        *   Wait, let's look at the isQ controlled-swap (three-CNOT decomposition) definition: `perm [0, 1, 2, 3, 4, 6, 5, 7]`.
        *   Basis states are indexed as $|q_0 q_1 q_2\rangle$ or $|q_2 q_1 q_0\rangle$?
        *   If $i = 4 q_2 + 2 q_1 + q_0$, then 5 is $|101\rangle$ (which means $q_0=1, q_1=0, q_2=1$).
        *   But a standard controlled-swap (three-CNOT decomposition) (Cswap (three-CNOT decomposition)) gate swaps the last two qubits if the first is 1.
        *   Here, `controlled-swap (three-CNOT decomposition)(q[0], q[1], q[2])` implies $q[0]$ is the control, $q[1]$ and $q[2]$ are the targets to be swapped.
        *   If $q[0]$ is the control, it swaps $q[1]$ and $q[2]$ when $q[0] = 1$.
        *   Let's check the permutation `[0, 1, 2, 3, 4, 6, 5, 7]`.
        *   If $q[0]$ is the *least* significant bit (LSB), $i = 4q[2] + 2q[1] + q[0]$.
        *   When $q[0]=1$, the states are 1, 3, 5, 7. The perm swaps 5 and 6. But 6 has $q[0]=0$. This means it swaps a state where $q[0]=1$ to a state where $q[0]=0$, which violates $q[0]$ being the control!
        *   Therefore, the index $i$ must be $i = 4q[0] + 2q[1]

### Reference answer

{'predicted_probs': {'101': 1.0}, 'explanation': 'defgate perm CSWAP gate on |110⟩ yields |101⟩.'}
