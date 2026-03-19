# PLAN.md

## Goals
- Build a compact, fine-tunable quantum coding LLM centered on the smallest practical Qwen 3.5 instruct model.
- Improve two capabilities together: quantum algorithm reasoning/code generation and general software-engineering behavior.
- Produce a CPU-first research pipeline that can curate data, run lightweight evaluation, and de-risk later fine-tuning before any GPU spend.
- Create artifacts that compound: datasets, eval sets, prompting baselines, tooling, and documented decisions.

## Constraints
- Local CPU only for now: no dependence on GPU training, large-scale distributed infra, or expensive online services in the critical path.
- Prefer small, inspectable experiments over broad but shallow automation.
- Optimize for the smallest model that is still plausibly useful after targeted fine-tuning.
- Focus on reproducible data prep, task design, and eval harnesses that can be exercised locally.
- Treat software-engineering skill as first-class: correctness, editing, debugging, tests, and repo navigation matter alongside quantum knowledge.

## Workstreams
1. **Base-model selection and prompting**
   - Lock the exact smallest practical Qwen 3.5 candidate, context limits, tokenizer assumptions, and baseline prompting recipes.
2. **Quantum task/data program**
   - Curate a compact corpus around circuits, simulation, Hamiltonians, variational methods, error mitigation, and library-specific coding tasks.
   - Emphasize executable tasks in Qiskit, Cirq, PennyLane, and small NumPy-based simulators.
3. **Software-engineering task/data program**
   - Build code-edit, bug-fix, test-writing, refactor, and small feature tasks from clean local repos and synthetic micro-projects.
4. **Local evaluation harness**
   - Create CPU-friendly evals for exact-match, test-pass rate, edit success, and rubric-scored reasoning quality.
5. **Fine-tuning readiness**
   - Prepare conversation/task schemas, filtering rules, train/val/test splits, and parameter-efficient training configs for later execution.
6. **Research memory and iteration loop**
   - Log decisions, failures, dataset gaps, and next actions so each autonomous cycle advances one concrete artifact.

## First 10 Tasks
1. Identify and record the exact Qwen 3.5 small-model target and why it is the best CPU-first starting point.
2. Create a model card note capturing parameter count, context length, license, tokenizer, and likely fine-tuning options.
3. Draft a task taxonomy covering quantum explanation, quantum code generation, code repair, testing, repo edits, and debugging.
4. Define a minimal JSONL schema for supervised examples, edit tasks, and eval items.
5. Build a seed list of 25-50 quantum coding tasks that are executable on CPU with small inputs.
6. Build a seed list of 25-50 software-engineering tasks focused on local code editing and tests.
7. Implement a tiny local eval harness that can run unit tests, compare outputs, and summarize pass/fail per task.
8. Create a baseline prompt pack for the target model: direct answer, plan-then-code, and repair-focused prompts.
9. Assemble a small gold eval set (about 20 quantum + 20 software tasks) reserved from training data.
10. Write fine-tuning readiness notes: preferred PEFT approach, sequence packing assumptions, and dataset size targets for the first training run.

## Evaluation Strategy
- **Quantum capability**
  - Measure correctness on small CPU-runnable tasks: circuit construction, statevector expectations, simple VQE/QAOA scaffolds, simulator debugging, and concept-to-code translation.
  - Score with unit tests, numerical tolerances, and compact rubric checks for explanation quality.
- **Software-engineering capability**
  - Measure bug fixing, test generation, small feature implementation, refactoring, and repository edits.
  - Use pass@1 on unit-test tasks, edit-application success, lint/test outcomes, and concise human review on a small sample.
- **Baseline discipline**
  - Keep a frozen baseline prompt/eval report for the untouched base model before any tuning.
  - Compare every dataset or prompt change against the same held-out eval set.
- **CPU realism**
  - Prefer tiny but representative tasks that run in seconds to a few minutes locally.
  - Defer large-scale benchmarking until the local harness and task design are stable.

## Immediate Next Step
Create `research/model-target.md` that selects the exact smallest practical Qwen 3.5 model candidate, states the selection criteria, and lists the first CPU-friendly baseline prompts and eval assumptions.
