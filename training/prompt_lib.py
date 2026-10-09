"""C-9829: SINGLE shared prompt-render function for train/eval parity.

Both the taskgen trainer (training/taskgen/families.build_prompt) and the LIVE
ASI2 scorer (scripts/run_asi2_base_adapter_rubric_eval.build_prompt) call this
ONE function, so the train-row prompt and the live-eval prompt render
identity-equal for an equivalent task spec. C-9820's logjam was two separate
inline prompt builders that could drift; this is the single source of truth.

The live-eval prompt distribution (documented in scripts/... L192-211) is:

    {task_spec}

    Domain: {domain}
    Category: {category}

    Return only the final Python code.

where {task_spec} is the self-contained task text (problem + embedded required
public API for taskgen rows / meta['task_prompt'] for live eval tasks).
"""


def render_user_prompt(task_spec: str, domain: str, category: str) -> str:
    """Render the single canonical user prompt shared by train & live eval.

    task_spec: self-contained task text (problem + signatures/API block).
    domain/category: metadata identifying the task domain/category.
    Returns the exact user-message string the model sees for this task.
    """
    return "\n\n".join(
        [
            str(task_spec),
            f"Domain: {domain}\nCategory: {category}",
            "Return only the final Python code.",
        ]
    )
