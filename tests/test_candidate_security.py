from __future__ import annotations

import pytest

from evals.runner.candidate_security import candidate_security_violations


@pytest.mark.parametrize(
    "source",
    [
        "import sys\nframe = getattr(sys, '_' + 'getframe')()\n",
        "from pathlib import Path\nprint(list(Path('.').rglob('*')))\n",
        "import builtins\nprint(getattr(builtins, 'open'))\n",
    ],
)
def test_candidate_security_rejects_computed_introspection_and_file_discovery(
    source: str,
) -> None:
    assert candidate_security_violations(source)


def test_candidate_security_accepts_targeted_quantum_helpers() -> None:
    source = "from collections import Counter\nimport itertools\n"

    assert candidate_security_violations(source) == []
