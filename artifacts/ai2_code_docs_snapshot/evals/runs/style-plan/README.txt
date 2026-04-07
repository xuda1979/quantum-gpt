This run directory captures prompt inputs and candidate output slots for a single eval batch.

Prompt style: plan_then_code
Prompt version: v2

Workflow:
1. Use SYSTEM_PROMPT.txt as the system message.
2. For each task, send prompts/<task_id>.txt as the user message.
3. Save the raw model code output into candidates/<task_id>.py.
4. Score the batch with:
   python3 evals/runner/run_eval.py --candidate-map evals/runs/style-plan/candidate-map.json
