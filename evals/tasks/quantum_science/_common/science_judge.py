"""Teacher-judge helper for quantum-science eval tasks.

Sends the question + the model's prose answer to GLM5.2 and parses the
JSON verdict. Used by every science task's tests.py.
"""

import json
import os
import re
import urllib.request

JUDGE_SYSTEM_PROMPT = (
    "You are a careful quantum-computing science teacher grading a student's "
    "answer. Grade on scientific correctness, mathematical rigor, and citation "
    "grounding. Respond as strict JSON."
)

JUDGE_PROMPT_TEMPLATE = """You are grading a student's quantum-computing science submission.

Question:
{question}

Student answer:
{answer}

Respond as JSON with this schema:
{{
  "is_correct": true | false,
  "issues": ["<concise description of each problem>"],
  "confidence": 0.0 | ... | 1.0,
  "citation_grounding": 0.0 | ... | 1.0,
  "fabricated_claim": true | false
}}

Guidance:
- `is_correct` is true ONLY if the answer is scientifically correct, mathematically rigorous, and free of unsupported claims.
- `citation_grounding` is 1.0 if every non-trivial claim is grounded; 0.0 if fabricated.
- `fabricated_claim` is true if any claim/equation/result is invented.
"""


def _parse_json(text: str) -> dict:
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    if not s.startswith("{"):
        m = re.search(r"\{.*\}", s, re.DOTALL)
        if m:
            s = m.group(0)
    try:
        return json.loads(s)
    except Exception:
        return {
            "_parse_error": True,
            "is_correct": False,
            "citation_grounding": 0.0,
            "confidence": 0.0,
            "fabricated_claim": True,
            "issues": ["parse_error"],
        }


def judge(
    question: str,
    answer: str,
    api_base: str | None = None,
    api_key: str | None = None,
    model: str = "glm5.2",
    timeout: int = 300,
) -> dict:
    """Judge a science answer. Returns the teacher's JSON verdict dict."""
    api_base = api_base or os.environ.get("GLM52_API_BASE", "")
    api_key = api_key or os.environ.get("GLM52_API_KEY", "")
    if not api_base:
        return {
            "_parse_error": True,
            "is_correct": False,
            "citation_grounding": 0.0,
            "confidence": 0.0,
            "fabricated_claim": True,
            "issues": ["GLM52_API_BASE not set"],
        }
    user_prompt = JUDGE_PROMPT_TEMPLATE.format(question=question, answer=answer)
    body = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.0,
            "max_tokens": 1024,
            "response_format": {"type": "json_object"},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        api_base.rstrip("/") + "/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {
            "_parse_error": True,
            "is_correct": False,
            "citation_grounding": 0.0,
            "confidence": 0.0,
            "fabricated_claim": True,
            "issues": [f"http_error: {exc}"],
        }
    content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "{}")
    return _parse_json(content)
