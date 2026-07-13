import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_common"))
from science_judge import judge

QUESTION = """Step through how Shors algorithm finds the period r of f(x) = a^x mod N. Explain the role of superposition, the QPE subroutine, and how continued fractions extract r from the measured phase."""


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
