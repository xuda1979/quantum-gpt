# Prompt-Format Improvement Notes (2026-03-20 22:40)

## Observation
The `fast-mini-codefirst` targets are already strongly code-first. The remaining failure mode is not banner comments anymore; it is weak task-contract following, especially:
- exact required function names
- resisting chatty preambles even when the base model is strongly conversational
- staying semantically on-task for sparse prompts

## Evidence
Recent smoke comparisons showed:
- `session_window_summary`: adapter still opens with `Sure!` and hallucinates `pandas`
- `measurement_bug_repair`: adapter starts with code, but uses the wrong function name (`map_measurements` instead of `measurement_mapping`)
- `stabilizer_tableau_update_repair`: adapter remains descriptive instead of code-only

Meanwhile, the normalized training data already contains strong instructions such as:
- `Return only Python code.`
- `Return the solution as Python code only.`
- `Return only the code, no explanations.`

So instruction strictness exists, but exact interface-contract salience is still too weak.

## Likely Bottleneck
The user prompts usually include only a task title, e.g. `Task: Measurement mapping bug repair`, without explicit required function signatures. The reference answer contains the function name, but under completion-only training the model may not reliably bind the latent task title to the exact required interface after only a tiny LoRA run.

## Next Candidate Improvement
Create a stricter derivative dataset that augments the **user prompt** with explicit interface-contract hints extracted from the assistant reference, for example:
- `Required function: measurement_mapping(bitstring: str) -> dict[str, int]`
- `Required function: retry(...)`
- `Required class/function names: ...`

This targets the exact failure mode we are seeing and is a better next bet than more banner cleanup.
