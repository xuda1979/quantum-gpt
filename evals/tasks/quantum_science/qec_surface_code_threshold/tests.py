import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_common"))
from science_judge import judge

QUESTION = """The surface code has an error threshold of approximately 1 percent for the depolarizing noise model. Explain why the threshold exists, what physical assumptions it depends on, and what happens to the logical error rate as the code distance d increases above and below the threshold."""


def run_tests(candidate_path):
    with open(candidate_path) as f:
        answer = f.read()
    if not answer.strip():
        return {"passed": False, "details": ["empty answer"]}
    verdict = judge(QUESTION, answer)
    failures = []
    if not verdict.get("is_correct"):
        failures.append("teacher_judged_incorrect: " + "; ".join(verdict.get("issues", [])))
    grounding = verdict.get("citation_grounding", 0.0)
    try:
        grounding = float(grounding)
    except Exception:
        grounding = 0.0
    if grounding < 0.7:
        failures.append(f"citation_grounding={grounding:.2f} < 0.7")
    if verdict.get("fabricated_claim"):
        failures.append("teacher_flagged_fabricated_claim")
    return {
        "passed": not failures,
        "details": failures or [f"teacher_judged_correct, grounding={grounding:.2f}"],
    }
