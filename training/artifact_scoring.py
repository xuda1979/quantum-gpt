#!/usr/bin/env python3
"""Per-artifact reward scoring for the RL + soft-distillation loop.

The reward rubric (``configs/rl/reward_rubric_v1.json`` and
``docs/quantum-coding-reward-rubric-2026-07-07.md``) defines seven
decomposed reward components. The RL+distill pipeline currently captures
only a single blended ``metadata.reward`` scalar; this module decomposes
the teacher's free-form ``issues`` strings into the rubric's categories
and produces a per-artifact score vector that the trainer can use for
reward-weighted distillation.

The classifier is intentionally rule-based (keyword table), not a separate
neural reward model. It reuses the GLM5.2 teacher signal we already pay
for and stays conservative: any unrecognised issue string falls into the
``"logic"`` category (affects ``r_partial``) rather than being ignored,
so unrecognised teacher criticism still hurts partial credit.

Score vector contract (all in [0, 1]):
    r_pass                   1.0 if teacher says is_correct else 0.0
    r_partial                1.0 - severity-weighted issue density
    r_runnable               0.0 if any syntax/import/name issue else 1.0
    r_api_correct            0.0 if any deprecated/wrong/hallucinated API
    r_style                  0.0 if any style issue else 1.0
    r_length_penalty         piecewise-linear on len(correct_answer)
    r_hallucination_penalty  fraction of issues that are hallucinated imports
    r_teacher_confidence     teacher_eval_result.confidence, clamped
    r_first_pass             1.0 if resample_attempts <= 1 else 0.0
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

# ---------------------------------------------------------------------------
# Issue categories
# ---------------------------------------------------------------------------

# Each category maps to a list of (regex, weight) pairs. The regex is matched
# case-insensitively against the issue string. The first match wins per issue.
# Weights are severity weights in [0, 1] used for r_partial: a weight of 1.0
# means "this issue alone can drop r_partial to 0", 0.5 means "contributes
# half". r_partial is 1 - max(weight of matched issues), floored at 0.

_CATEGORIES: dict[str, list[tuple[re.Pattern[str], float]]] = {
    "syntax": [
        (re.compile(r"\bsyntax error\b", re.I), 1.0),
        (re.compile(r"\bindentation\b", re.I), 0.8),
        (re.compile(r"\bunterminated\b", re.I), 1.0),
        (re.compile(r"\bunexpected (token|eof|indent)\b", re.I), 1.0),
        (re.compile(r"\bparse error\b", re.I), 1.0),
    ],
    "import_error": [
        (re.compile(r"\b(import|module) (error|not found|missing)\b", re.I), 1.0),
        (re.compile(r"\bno module named\b", re.I), 1.0),
        (re.compile(r"\bcannot import\b", re.I), 1.0),
        (re.compile(r"\bimport could not be resolved\b", re.I), 1.0),
    ],
    "name_error": [
        (re.compile(r"\bname ?error\b", re.I), 1.0),
        (re.compile(r"\bundefined (name|variable|function)\b", re.I), 0.9),
        (re.compile(r"\bnot defined\b", re.I), 0.9),
        (re.compile(r"\battribute ?error\b", re.I), 0.8),
        (re.compile(r"\btype ?error\b", re.I), 0.7),
        (re.compile(r"\bkey ?error\b", re.I), 0.5),
    ],
    "deprecated_api": [
        (re.compile(r"\bdeprecated\b", re.I), 0.7),
        (re.compile(r"\bqiskit\.aer\b", re.I), 0.9),
        (re.compile(r"\bqiskit\.execute\b", re.I), 0.9),
        (re.compile(r"\bqiskit\.tools\.monitor\b", re.I), 0.9),
        (re.compile(r"\bcirq\.google\.xmondevice\b", re.I), 0.9),
        (re.compile(r"\bpennylane\.defaultqubit\b", re.I), 0.9),
        (re.compile(r"\boutdated api\b", re.I), 0.8),
        (re.compile(r"\blegacy api\b", re.I), 0.8),
    ],
    "wrong_api": [
        (re.compile(r"\bwrong api\b", re.I), 0.8),
        (re.compile(r"\bincorrect (api|usage|function|method)\b", re.I), 0.8),
        (re.compile(r"\bshould use\b", re.I), 0.6),
        (re.compile(r"\binstead of\b", re.I), 0.5),
        (re.compile(r"\bmisuse[ds]?\b", re.I), 0.8),
        (re.compile(r"\bdoes not (exist|match) (the )?api\b", re.I), 0.8),
    ],
    "hallucinated_import": [
        (re.compile(r"\bhallucinat", re.I), 1.0),
        (re.compile(r"\bnonexistent (module|import|package|attribute)\b", re.I), 1.0),
        (re.compile(r"\bfabricated (module|import|api)\b", re.I), 1.0),
        (re.compile(r"\binvented (module|import|api)\b", re.I), 1.0),
        (re.compile(r"\bdoes not exist in\b", re.I), 0.9),
    ],
    "style": [
        (re.compile(r"\bstyle\b", re.I), 0.3),
        (re.compile(r"\bpyflakes\b", re.I), 0.3),
        (re.compile(r"\blint(er|ing)?\b", re.I), 0.3),
        (re.compile(r"\bnaming convention\b", re.I), 0.3),
        (re.compile(r"\bpep8\b", re.I), 0.3),
        (re.compile(r"\bformatting\b", re.I), 0.2),
        (re.compile(r"\bwhitespace\b", re.I), 0.2),
        (re.compile(r"\bunused (import|variable)\b", re.I), 0.4),
    ],
}

# ---------------------------------------------------------------------------
# Science-domain issue categories (rule_science_v1). Parallel to the coding
# _CATEGORIES above. Used when task_domain == "science" and the config sets
# per_artifact_scoring.issue_classifier = "rule_science_v1".
# ---------------------------------------------------------------------------
_SCIENCE_CATEGORIES: dict[str, list[tuple[re.Pattern[str], float]]] = {
    "incorrect_math": [
        (re.compile(r"\bequation\b", re.I), 0.8),
        (re.compile(r"\bderivation\b", re.I), 0.9),
        (re.compile(r"\bmissing term\b", re.I), 0.8),
        (re.compile(r"\bwrong sign\b", re.I), 0.9),
        (re.compile(r"\bnormalization\b", re.I), 0.7),
        (re.compile(r"\balgebra\b", re.I), 0.7),
        (re.compile(r"\bcalculus\b", re.I), 0.7),
        (re.compile(r"\bdifferentiat", re.I), 0.7),
        (re.compile(r"\bintegrat", re.I), 0.7),
        (re.compile(r"\bmatrix (product|multiplication)\b", re.I), 0.8),
        (re.compile(r"\beigen", re.I), 0.7),
        (re.compile(r"\bphase factor\b", re.I), 0.7),
    ],
    "unsupported_claim": [
        (re.compile(r"\bunsupported\b", re.I), 0.9),
        (re.compile(r"\bno citation\b", re.I), 0.9),
        (re.compile(r"\bfabricat", re.I), 1.0),
        (re.compile(r"\bnot in source\b", re.I), 0.9),
        (re.compile(r"\binvented\b", re.I), 1.0),
        (re.compile(r"\bunsubstantiat", re.I), 0.9),
        (re.compile(r"\bwithout (proof|justification)\b", re.I), 0.8),
    ],
    "conceptual_error": [
        (re.compile(r"\bmisunderstand", re.I), 0.9),
        (re.compile(r"\bconfuses?\b", re.I), 0.9),
        (re.compile(r"\bwrong definition\b", re.I), 0.9),
        (re.compile(r"\bcategory error\b", re.I), 0.9),
        (re.compile(r"\bconceptual\b", re.I), 0.8),
        (re.compile(r"\bincorrectly (states|claims|assumes)\b", re.I), 0.8),
    ],
    "incomplete": [
        (re.compile(r"\bincomplete\b", re.I), 0.7),
        (re.compile(r"\bmissing step\b", re.I), 0.8),
        (re.compile(r"\bhand-?wav", re.I), 0.8),
        (re.compile(r"\bglosses over\b", re.I), 0.7),
        (re.compile(r"\bdoes not (show|derive|prove)\b", re.I), 0.7),
        (re.compile(r"\bskips?\b", re.I), 0.6),
    ],
    "ungrounded_comparison": [
        (re.compile(r"\bcomparison\b", re.I), 0.6),
        (re.compile(r"\bcompares? to\b", re.I), 0.6),
        (re.compile(r"\bthreshold\b", re.I), 0.6),
        (re.compile(r"\bvs\.?\b", re.I), 0.5),
        (re.compile(r"\brelative to\b", re.I), 0.5),
        (re.compile(r"\bbetter than\b", re.I), 0.5),
        (re.compile(r"\bworse than\b", re.I), 0.5),
    ],
    "notation": [
        (re.compile(r"\bnotation\b", re.I), 0.4),
        (re.compile(r"\bambiguous symbol\b", re.I), 0.5),
        (re.compile(r"\binconsistent convention\b", re.I), 0.5),
        (re.compile(r"\bwrong (index|subscript|superscript)\b", re.I), 0.5),
        (re.compile(r"\bbra-?ket\b", re.I), 0.4),
    ],
    "other": [],
}

# Science category -> score fields it affects. Mirrors _CATEGORY_IMPACT but
# for the science rubric. The science score vector reuses the same field
# names as the coding rubric (r_pass, r_partial, r_runnable, r_api_correct,
# r_style, r_length_penalty, r_hallucination_penalty, r_teacher_confidence,
# r_first_pass) so the trainer-side code is unchanged. The semantics shift:
# r_runnable -> "derivation is sound", r_api_correct -> "notation/conventions
# correct", r_style -> "exposition clear".
_SCIENCE_CATEGORY_IMPACT: dict[str, list[tuple[str, bool]]] = {
    "incorrect_math": [("r_runnable", True), ("r_partial", True)],
    "unsupported_claim": [("r_hallucination_penalty", True), ("r_partial", True)],
    "conceptual_error": [("r_api_correct", True), ("r_partial", True)],
    "incomplete": [("r_partial", True)],
    "ungrounded_comparison": [("r_style", True), ("r_partial", True)],
    "notation": [("r_api_correct", True)],
    "other": [("r_partial", True)],
}


# Category -> which score fields it affects (with a flag for "negative").
# A negative field means "the score is 1.0 minus penalty" (e.g. r_runnable
# is 1.0 unless a runnable-category issue is present).
_CATEGORY_IMPACT: dict[str, list[tuple[str, bool]]] = {
    "syntax": [("r_runnable", True)],
    "import_error": [("r_runnable", True), ("r_api_correct", True)],
    "name_error": [("r_runnable", True)],
    "deprecated_api": [("r_api_correct", True)],
    "wrong_api": [("r_api_correct", True)],
    "hallucinated_import": [("r_api_correct", True), ("r_hallucination_penalty", False)],
    "style": [("r_style", True)],
    # "logic" is the catch-all for correctness issues; it only affects
    # r_partial via the max-severity computation below.
    "logic": [],
}

# Length-penalty piecewise-linear parameters (mirror the rubric).
_LENGTH_THRESHOLD_CHARS = 4000
_LENGTH_SATURATION_CHARS = 8000

# Confidence floor for the KL gate (so KL never vanishes entirely).
CONFIDENCE_FLOOR_FOR_KL_GATE = 0.3


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------


def classify_issue(issue: str) -> str:
    """Classify a single teacher-issue string into one rubric category.

    Returns one of: syntax, import_error, name_error, deprecated_api,
    wrong_api, hallucinated_import, style, logic, other.

    "logic" is the catch-all for any non-empty string that doesn't match
    a known category (conservative: unrecognised criticism hurts partial
    credit). "other" is reserved for empty/whitespace strings.
    """
    if not issue or not issue.strip():
        return "other"
    for category, patterns in _CATEGORIES.items():
        for pat, _weight in patterns:
            if pat.search(issue):
                return category
    return "logic"


def classify_issues(issues: Iterable[str]) -> list[str]:
    """Classify a list of issue strings. Returns one category per issue."""
    return [classify_issue(s) for s in issues]


def classify_issue_science(issue: str) -> str:
    """Classify a single teacher-issue string into one science-rubric category.

    Returns one of: incorrect_math, unsupported_claim, conceptual_error,
    incomplete, ungrounded_comparison, notation, other.

    "other" is the catch-all for any non-empty string that matches no pattern.
    """
    if not issue or not issue.strip():
        return "other"
    for category, patterns in _SCIENCE_CATEGORIES.items():
        if not patterns:
            continue
        for pat, _weight in patterns:
            if pat.search(issue):
                return category
    return "other"


def classify_issues_science(issues: Iterable[str]) -> list[str]:
    """Classify a list of issue strings using the science rubric."""
    return [classify_issue_science(s) for s in issues]


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------


def _length_penalty(correct_answer: str) -> float:
    """Piecewise-linear length penalty in [0, 1].

    0 chars  -> 0.0
    4000     -> 0.0  (threshold: no penalty up to here)
    8000     -> 1.0  (saturation: full penalty at/above here)
    linear in between.
    """
    n = len(correct_answer or "")
    if n <= _LENGTH_THRESHOLD_CHARS:
        return 0.0
    if n >= _LENGTH_SATURATION_CHARS:
        return 1.0
    return (n - _LENGTH_THRESHOLD_CHARS) / (_LENGTH_SATURATION_CHARS - _LENGTH_THRESHOLD_CHARS)


def _r_partial(
    issues: list[str], categories: list[str], *, category_table: dict | None = None
) -> float:
    """Partial-credit score in [0, 1].

    1.0 if no issues. Otherwise 1.0 - max(severity weight of matched issues),
    floored at 0.0. The max (not sum) is intentional: one severe issue is
    enough to drop partial credit; multiple mild issues don't compound to
    a total drop.
    """
    if not issues:
        return 1.0
    table = category_table if category_table is not None else _CATEGORIES
    max_severity = 0.0
    for issue, cat in zip(issues, categories, strict=False):
        if cat == "other":
            continue
        # Look up the severity weight for the matched pattern.
        weight = 0.5  # default for catch-all categories
        if cat in table:
            for pat, w in table[cat]:
                if pat.search(issue):
                    weight = w
                    break
        if weight > max_severity:
            max_severity = weight
    return max(0.0, 1.0 - max_severity)


def _binary_field(
    categories: list[str], affecting: str, default: float = 1.0, *, impact_table: dict | None = None
) -> float:
    """Return default unless any category matches `affecting`, then 0.0."""
    table = impact_table if impact_table is not None else _CATEGORY_IMPACT
    for cat in categories:
        impacts = table.get(cat, [])
        for field, _is_negative in impacts:
            if field == affecting:
                return 0.0
    return default


def _hallucination_fraction(
    categories: list[str], *, hallucination_category: str = "hallucinated_import"
) -> float:
    """Fraction of issues in the hallucination category. 0.0 if no issues."""
    if not categories:
        return 0.0
    n_halluc = sum(1 for c in categories if c == hallucination_category)
    return n_halluc / max(1, len(categories))


def score_artifact(
    teacher_eval_result: dict[str, Any],
    correct_answer: str,
    resample_attempts: int,
    *,
    issue_classifier: str = "rule_v1",
) -> dict[str, float]:
    """Compute the full per-artifact score vector.

    Args:
        teacher_eval_result: The dict returned by the GLM5.2 teacher eval
            call. Must contain ``is_correct`` (bool) and ``confidence``
            (float in [0, 1]); ``issues`` (list[str]) is optional.
        issue_classifier: ``"rule_v1"`` (coding, default) or
            ``"rule_science_v1"`` (science mode). Selects the category
            table and impact map.
        correct_answer: The corrected answer text (used for length penalty).
        resample_attempts: How many resamples the student needed to produce
            a valid question (1 = first pass).

    Returns:
        Dict with keys r_pass, r_partial, r_runnable, r_api_correct,
        r_style, r_length_penalty, r_hallucination_penalty,
        r_teacher_confidence, r_first_pass — all floats in [0, 1].
    """
    issues: list[str] = list(teacher_eval_result.get("issues", []) or [])
    # Dispatch on classifier. Science mode uses a parallel category table
    # and impact map; the score-field names are shared with the coding
    # rubric so the trainer side is unchanged.
    if issue_classifier == "rule_science_v1":
        categories = [classify_issue_science(s) for s in issues]
        category_table = _SCIENCE_CATEGORIES
        impact_table = _SCIENCE_CATEGORY_IMPACT
        hallucination_category = "unsupported_claim"
    else:
        categories = [classify_issue(s) for s in issues]
        category_table = _CATEGORIES
        impact_table = _CATEGORY_IMPACT
        hallucination_category = "hallucinated_import"

    is_correct = bool(teacher_eval_result.get("is_correct", False))
    confidence = float(teacher_eval_result.get("confidence", 0.5) or 0.5)
    confidence = max(0.0, min(1.0, confidence))

    r_pass = 1.0 if is_correct else 0.0
    r_partial = _r_partial(issues, categories, category_table=category_table)
    # If the teacher says correct, pin r_partial to 1.0 regardless of issues.
    if is_correct:
        r_partial = 1.0
    r_runnable = _binary_field(categories, "r_runnable", default=1.0, impact_table=impact_table)
    r_api_correct = _binary_field(
        categories, "r_api_correct", default=1.0, impact_table=impact_table
    )
    r_style = _binary_field(categories, "r_style", default=1.0, impact_table=impact_table)
    r_length_penalty = _length_penalty(correct_answer)
    r_hallucination_penalty = _hallucination_fraction(
        categories, hallucination_category=hallucination_category
    )
    r_teacher_confidence = confidence
    r_first_pass = 1.0 if int(resample_attempts or 1) <= 1 else 0.0

    return {
        "r_pass": r_pass,
        "r_partial": r_partial,
        "r_runnable": r_runnable,
        "r_api_correct": r_api_correct,
        "r_style": r_style,
        "r_length_penalty": r_length_penalty,
        "r_hallucination_penalty": r_hallucination_penalty,
        "r_teacher_confidence": r_teacher_confidence,
        "r_first_pass": r_first_pass,
    }


def kl_gate_weight(
    artifact_scores: dict[str, float], *, floor: float = CONFIDENCE_FLOOR_FOR_KL_GATE
) -> float:
    """Scale factor for the KL term based on teacher confidence.

    Returns ``max(floor, r_teacher_confidence)`` so the KL term never
    vanishes entirely even when the teacher is uncertain.
    """
    conf = float(artifact_scores.get("r_teacher_confidence", 1.0))
    return max(float(floor), conf)


def reward_weighted_nll_weight(
    reward: float,
    reward_floor: float,
    *,
    r_partial: float = 0.0,
    partial_credit_upweight: float = 0.0,
) -> float:
    """Sample weight for the NLL term under reward-weighted distillation.

    Args:
        reward: The scalar reward in [0, 1] (existing ``metadata.reward``).
        reward_floor: Samples below this are dropped by the dataset; for
            surviving samples, the weight is rescaled so floor -> 0 and
            1.0 -> 1.0.
        r_partial: The per-artifact partial-credit score.
        partial_credit_upweight: Extra NLL weight for near-miss samples
            (H1 knob). 0.0 disables.

    Returns:
        Float weight ``>= 0``. At reward=floor the weight is 0 (no NLL
        gradient); at reward=1 the weight is 1 + partial_credit_upweight*r_partial.
    """
    span = max(1e-6, 1.0 - float(reward_floor))
    base = (float(reward) - float(reward_floor)) / span
    base = max(0.0, min(1.0, base))
    return base + float(partial_credit_upweight) * max(0.0, float(r_partial))
