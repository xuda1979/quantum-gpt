# Model Target

## Research target vs executable source

This project needs two separate truths recorded clearly:

1. **research target** — what family/size we want to optimize around
2. **executable source** — what exact checkpoint we can honestly fetch, verify, and hand off right now

They are not the same thing today.

## Research target

**Preferred research target:** smallest practical Qwen-family instruct checkpoint for quantum + software-engineering work.

Historically, the project centered this as:

- `Qwen3.5-1.5B-Instruct`

That remains the intended target shape and ambition.

## Executable source status

The exact identifier `Qwen/Qwen3.5-1.5B-Instruct` is **not currently a verified public executable source from this machine**.

Current publicly verified execution candidates are:

- `Qwen/Qwen2.5-1.5B-Instruct` — smallest verified public fallback in the same 1.5B size band
- `Qwen/Qwen3-1.7B` — verified public Qwen 3 family alternative at slightly higher cost

So the project should stop acting as if the research target and the executable artifact are already identical.

## Why the research target still makes sense

- **Small enough to be realistic for local CPU-first work.** A 1.5B-ish instruct model is still large, but meaningfully more tractable than 3B+ models for local experimentation, tokenization checks, dataset formatting, and later low-cost adaptation planning.
- **Still plausibly useful after targeted tuning.** Sub-1B models are more likely to collapse on multi-step coding, repository edits, and quantum-library API usage.
- **Better match to the project goal than a pure tiny baseline.** The project needs both quantum algorithm work and software-engineering ability.
- **Good fit for a staged CPU-first workflow.** Even before full fine-tuning, this size band works for eval harnesses, prompt baselines, data schemas, and PEFT planning.
- **Instruct variants are the right baseline.** Task-following, code completion, and concise execution matter more here than starting from a base pretraining checkpoint.

## Rejected alternatives

### Smaller than 1.5B

- **Rejected because likely too weak for the combined target.** Very small models may work for narrow quantum classification or templated completion, but this project needs both quantum algorithm tasks and general software-engineering tasks.
- **Higher risk of false economy.** Saving CPU and memory up front is not worth it if the model is too weak to show meaningful gains from the data and eval program.

### 3B-class or larger first target

- **Rejected for now because CPU-first iteration would slow down too much.** Prompt baselines, local eval loops, and later adaptation experiments become much heavier.
- **Too expensive as the first lock-in target.** If the ~1.5B path proves insufficient later, moving up is easy. Starting bigger makes every early experiment slower.

### Non-instruct variants

- **Rejected because the project needs task-following behavior immediately.** The current phase is about realistic baselines, evals, and dataset design, not raw pretraining continuation.

### Non-Qwen small coding models

- **Rejected because they miss the project constraint.** The program is centered on the smallest practical Qwen-family coding model unless Qwen proves unworkable.

## CPU-first baseline plan

1. **Keep the research target frozen conceptually.**
   - smallest practical Qwen-family instruct model
   - preserve software-engineering capability as first-class

2. **Do not pretend an unavailable artifact is executable.**
   - if exact Qwen 3.5 artifacts appear, use the strict verifier + Huanxin handoff path
   - otherwise require an explicit execution-source choice before acquisition/transfer

3. **Use quantized/local-lightweight workflows first.**
   - keep sequence lengths modest for baseline runs
   - favor tokenization checks, prompt baselines, small eval tasks, and dataset work over expensive full-model experiments

4. **Start with tiny but representative tasks.**
   - Quantum: circuit construction, simulator debugging, textbook protocols, small Qiskit/Cirq/PennyLane snippets
   - Software engineering: bug fixes, small feature edits, test writing, refactors, docstring or interface cleanup

5. **Keep runtime expectations strict.**
   - individual eval tasks should usually run in seconds, not hours
   - favor Python tasks with tiny dependencies and tiny inputs

6. **Delay remote training claims until the source is real.**
   - first prove the checkpoint source is auditable and locally verified
   - then transfer only the verified local snapshot into Huanxin and run tokenizer smoke before any PEFT claim

## Current execution fork

There are only three honest execution states:

1. **Exact Qwen 3.5 source appears**
   - verify it locally with `training/verify_qwen_snapshot.py`
   - transfer it into `/root/root/work/quantum-gpt/models/Qwen3.5-1.5B-Instruct`
   - run remote tokenizer smoke

2. **Public 1.5B fallback is explicitly approved**
   - use `Qwen/Qwen2.5-1.5B-Instruct`
   - acquisition helper: `python3 training/acquire_public_qwen_snapshot.py --target qwen25`
   - handoff note: `research/qwen25-public-fallback-handoff.md`

3. **Public Qwen 3 family alternative is explicitly approved**
   - use `Qwen/Qwen3-1.7B`
   - acquisition helper: `python3 training/acquire_public_qwen_snapshot.py --target qwen3-1.7b`
   - handoff note: `research/qwen3-public-alternative-handoff.md`

## Eval assumptions

- **The baseline must be judged on executable tasks, not prose quality.** Unit tests, numerical checks, and repository-edit validation should dominate.
- **Small-task pass rate matters more than benchmark theater.** A compact local eval suite is more useful than chasing large public benchmark numbers during this phase.
- **Quantum tasks must stay CPU-runnable.** Small circuits, tiny simulators, and low-qubit examples only.
- **Software-engineering quality is first-class.** The model should be evaluated on debugging, tests, edits, and maintainability-oriented tasks, not only code synthesis from scratch.
- **Context window is not the main bottleneck in the first phase.** Most local tasks should fit in short contexts so CPU latency stays tolerable.
- **Prompt discipline matters.** The same prompt templates should be reused across baselines so later tuning gains are interpretable.

## Open questions

- Will a real exact `Qwen/Qwen3.5-1.5B-Instruct` source appear, or should execution explicitly move to a verified public branch?
- What exact local runtime stack should be standardized first for CPU inference: llama.cpp-compatible weights, MLX conversion if available, or another quantized path?
- What is the acceptable latency target per task on this machine for baseline eval runs?
- Is ~1.5B strong enough for repository-edit tasks, or will the software-engineering track quickly force a move to a larger model?
- Which quantum frameworks should be in the first eval slice: Qiskit only, or Qiskit plus one of Cirq/PennyLane?
- What minimum held-out eval set size is enough to make early prompt/data decisions without overfitting to anecdotes?
- When the project reaches adaptation experiments, should the first training path aim for LoRA-style fine-tuning externally while keeping all data and eval work local?
