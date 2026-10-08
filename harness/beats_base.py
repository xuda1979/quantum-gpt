# Pinned beats_base comparison metric (card C-0013).
# Decision record: harness/state/beats_base_metric.md.
# Consumer: the C-0012 verdict composer. Do NOT re-implement the comparison.
BEATS_PASS_COUNT = "pass-count"
BEATS_COMPOSITE = "composite-tiebreak"
FULL_TIE = "full-tie-deadlock"


class BeatsBaseError(ValueError):
    """Fail-closed: missing/malformed evidence, or a tie with no tiebreak."""


def _parse(score):
    # Accept "k/n" strings or bare int counts (denominator then unknown).
    if isinstance(score, str):
        parts = score.split("/")
        if len(parts) != 2:
            raise BeatsBaseError(f"malformed score: {score!r}")
        try:
            k, n = int(parts[0]), int(parts[1])
        except ValueError:
            raise BeatsBaseError(f"malformed score: {score!r}")
        if n <= 0 or k < 0 or k > n:
            raise BeatsBaseError(f"out-of-range score: {score!r}")
        return k, n
    if isinstance(score, int) and not isinstance(score, bool):
        if score < 0:
            raise BeatsBaseError(f"out-of-range count: {score!r}")
        return score, None
    raise BeatsBaseError(f"unsupported score: {score!r}")


def beats_base(pass_adapter, pass_base, composite_adapter=None, composite_base=None):
    """Return (verdict, rule) for the pinned metric; raise on bad evidence.

    pass-count primary; composite tiebreak on equal pass-counts; a tie
    without composite inputs raises (fail-closed guard).
    """
    ka, na = _parse(pass_adapter)
    kb, nb = _parse(pass_base)
    if na is not None and nb is not None and na != nb:
        raise BeatsBaseError(f"mismatched denominators: {na} vs {nb}")
    # Supplied-but-garbage composite fails closed even when the outcome is
    # already decided on pass-count (never compare past bad evidence).
    for name, c in (("adapter", composite_adapter), ("base", composite_base)):
        if c is not None and c < 0:
            raise BeatsBaseError(f"negative {name} composite")
    if ka != kb:
        return ka > kb, BEATS_PASS_COUNT
    if composite_adapter is None or composite_base is None:
        raise BeatsBaseError(f"tie {ka}/{na or 18} needs composite tiebreak inputs")
    if composite_adapter != composite_base:
        return composite_adapter > composite_base, BEATS_COMPOSITE
    return False, FULL_TIE
