# Quantum Theory QA Generation Spec

You are an advanced quantum information theorist and quantum software engineer.
Generate difficult, self-contained quantum-computing question/answer pairs for a
training corpus.

## Hard Requirements

1. Generate exactly `[BATCH_SIZE]` distinct pairs.
2. Number samples sequentially starting at `[START_ID]` with no gaps or reuse.
3. Keep every sample technically rigorous and fully self-contained.
4. Use $ for inline math and $$ for display math.
5. Do not include hidden chain-of-thought, scratch work, or meta commentary.
6. Answers must provide a concise derivation summary and a final result.
7. Do not fabricate benchmark numbers, fidelities, runtimes, or measurements.
8. Keep the two modes distinct:
   - `Hardened-Rigor`: proof-heavy, theorem-driven, asymptotically precise
   - `Grounded-Innovation`: speculative but physically consistent, with clear
     implementation constraints

## Output Format

Return each sample in one block:

```xml
<sample id="[CALCULATED_ID]">
<metadata>
  <domain>Quantum Computing</domain>
  <type>[Hardened-Rigor|Grounded-Innovation]</type>
</metadata>
<question>
...
</question>
<answer>
...
</answer>
</sample>
```

## Topic Coverage

Prioritize:

- Block encoding, LCU, QSP, QSVT
- Hamiltonian simulation and error bounds
- Fault-tolerant compilation and gate synthesis
- Stabilizer codes, qLDPC, syndrome decoding, lattice surgery
- QPE, amplitude estimation, and related spectral methods
- Variational algorithms and resource tradeoffs
- Open quantum systems, control, and error mitigation
- Tomography, certification, and verification
- Quantum walks, oracle complexity, and state transfer

## Style

- Questions should be mathematically sharp and nontrivial.
- Answers should be compact but complete.
- Prefer exact scaling laws, explicit constraints, and final formulas.
- Keep sample IDs globally unique across the full run.
