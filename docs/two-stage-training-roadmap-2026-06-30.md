# Two-Stage Training Roadmap

Date: 2026-06-30

This roadmap records the current product and research split for the quantum coding LLM program. The immediate phase is code ability. The later phase adds quantum-computing scientific understanding, paper-grounded reasoning, distillation, and reinforcement learning.

## Stage 1: Code Ability Training

Status: active.

Goal: train the model to be strong at quantum code and general software engineering before expanding into deep scientific paper reasoning.

Primary capabilities:

- Write, repair, and test quantum programs in Qiskit, Cirq, PennyLane, Braket, ISQ, and small NumPy simulators.
- Preserve general coding ability: debugging, unit tests, refactors, API hygiene, repository edits, and runnable scripts.
- Use RAG when framework APIs are likely to change, but score final answers through execution and tests.
- Learn agentic repair behavior from successful trajectories: read docs, write code, run, inspect errors, repair, and verify.

Current repo assets to keep using:

- `training/qwen_sft_peft.py` for LoRA SFT.
- `training/grpo_trainer.py` for verifier-driven GRPO once SFT is stable.
- `data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft` and strict repaired variants for high-quality quantum-code SFT.
- `data/generated/omnicoder-quantum-generalization-holdout-v1` and v2-style strict holdouts for unseen-task evaluation.
- `scripts/build_quantum_distillation_seed_questions.py`, `scripts/generate_distillation_teacher_responses.py`, `scripts/prepare_distillation_sft_split.py`, and `scripts/strictify_distillation_dataset.py` for seed-to-teacher-to-clean-SFT flow.
- `scripts/build_quantum_rag.py`, `scripts/eval_quantum_rag.py`, and `scripts/score_quantum_rag_retrieval.py` for retrieval grounding.

Recommended training order:

1. SFT on verified quantum-code and software-engineering examples.
2. SFT replay with agentic repair trajectories and RAG-aware examples.
3. GRPO or RLVR on executable benchmarks only after the SFT adapter clears local and remote smoke tests.
4. Keep a code replay mix during every later scientific training pass to avoid forgetting software behavior.

Exit gates for Stage 1:

- Held-out pass@1 improves over the base model on strict quantum-code tasks.
- General software-engineering evals do not regress materially.
- Generated code is runnable without manual repair on the benchmark protocol.
- Local checks pass before any Huanxin `AI` training launch.

## Stage 2: Quantum Scientific Capability Training

Status: planned after the code-capability phase is stable.

Goal: add paper-grounded quantum-computing scientific understanding and reasoning. The target corpus is 1000 important and classic academic papers, converted into progressive question-answer data for distillation and then mixed SFT/RL training.

Paper selection scope:

- Foundations and algorithms: Deutsch-Jozsa, Simon, Shor, Grover, QFT, QPE, amplitude amplification, HHL, Hamiltonian simulation, qubitization, quantum singular value transformation.
- Complexity and information: BQP, QMA, query complexity, entanglement theory, channel capacity, no-cloning, tomography, randomized benchmarking.
- Error correction and fault tolerance: stabilizer codes, surface code, color code, LDPC codes, magic-state distillation, lattice surgery, threshold theorems.
- NISQ and variational methods: VQE, QAOA, barren plateaus, error mitigation, shadow tomography, classical shadows.
- Quantum chemistry and simulation: Trotterization, phase estimation chemistry, tensor networks, fermion-to-qubit mappings.
- Compilers and programming systems: circuit optimization, routing, synthesis, IR design, resource estimation, quantum programming languages.
- Hardware, noise, and control: superconducting, trapped ion, photonic, neutral atom, pulse-level control, calibration, noise models.
- Quantum machine learning, cryptography, networking, and application papers where they materially affect code or research direction.

Data product from each paper:

- A paper card: metadata, provenance, field tags, prerequisites, main claims, assumptions, mathematical objects, algorithms, experiments, limitations, and related papers.
- Progressive QA pairs:
  - L0 bibliographic and contribution recall.
  - L1 concept explanation and terminology.
  - L2 equation, theorem, assumption, and derivation checks.
  - L3 method and algorithm reconstruction.
  - L4 implementation and code translation tasks.
  - L5 limitations, ablations, failure cases, and reproducibility questions.
  - L6 synthesis across multiple papers and feasible new research directions.
- Optional code artifacts: small simulators, pseudocode-to-Python tasks, resource estimators, verifier tests, and experiment scaffolds.
- Research-direction prompts: plausible extensions grounded in the paper, not generic speculation.

Quality gates:

- Keep train/eval/test paper-disjoint. Evaluation papers must not appear in training, even through generated variants.
- Require source provenance for every answer: paper id, section/page/chunk ids, and generation timestamp.
- Avoid training the model to reproduce full copyrighted paper text. Use open-access sources where possible and generate transformed, grounded QA rather than raw chunk-copy targets.
- Do not store private teacher chain-of-thought. Use visible derivation summaries, equation steps, or structured reasoning traces that are safe to train on.
- Deduplicate at paper, question, answer, and embedding-near-duplicate levels.
- Validate code examples with local execution when they claim to be runnable.
- Reject rows that invent unsupported conclusions or citations.

Scale plan:

- Pilot: 50 papers, 8 to 12 QA rows per paper, plus a 20-paper held-out eval set.
- Expansion: 200 papers, balanced across the taxonomy, with paper-disjoint splits and verifier reports.
- Full corpus: 1000 papers, roughly 8000 to 20000 high-quality QA/code/research rows, depending on paper density and quality gate yield.

Training plan:

1. Build the paper manifest and paper cards.
2. Build a paper RAG index for extraction and answer grounding.
3. Generate progressive QA with a strong teacher model.
4. Run quality filters, citation grounding checks, deduplication, and paper-disjoint splitting.
5. Distill with SFT on the scientific QA corpus while preserving 30% to 50% code replay.
6. Add RL/GRPO only after SFT: rewards should cover citation grounding, mathematical consistency, code-test pass rate, and evaluator preference on research usefulness.
7. Finish with mixed training: code tasks, paper QA, RAG-aware tasks, and verifier-driven RL examples in one controlled curriculum.

Repo gaps to implement for Stage 2:

- `scripts/build_quantum_paper_manifest.py`: build and validate the 1000-paper selection manifest.
- `scripts/extract_quantum_paper_cards.py`: turn papers into structured cards with provenance.
- `scripts/generate_quantum_paper_progressive_qa.py`: create L0-L6 QA tasks from cards and retrieved excerpts.
- `scripts/verify_quantum_paper_qa_dataset.py`: enforce provenance, paper-disjoint splits, deduplication, and runnable-code checks.
- `evals/benchmarks/quantum_paper_science_holdout_v1.json`: held-out scientific reasoning benchmark.

Immediate policy:

Do not spend the main training budget on the 1000-paper science corpus until Stage 1 code ability has a stable adapter and evaluation report. Stage 2 can still advance through low-cost local design work: manifest schema, taxonomy, extraction prompts, QA schema, and verifier tooling.