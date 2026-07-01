from typing import List

def bell_pair_state() -> List[float]:
    """Return the Bell state |Phi+> amplitudes as a length-4 list."""
    amp = 2 ** -0.5
    return [amp, 0.0, 0.0, amp]
