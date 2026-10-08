#!/usr/bin/env python3
"""Unit tests for scripts/self_correcting_distill_27b_iter5.py."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import self_correcting_distill_27b_iter5 as scd  # noqa: E402


def test_extract_python_code_fenced():
    text = 'Critique.\n\n```python\nprint("hi")\n```'
    assert scd.extract_python_code(text) == 'print("hi")'


def test_extract_python_code_bare():
    text = "import os\ndef main():\n    pass\n"
    assert scd.extract_python_code(text) == text.strip()


def test_has_def_main():
    assert scd.has_def_main('def main():\n    pass\n\nif __name__ == "__main__":\n    main()\n')
    assert not scd.has_def_main('print("no main")\n')


def test_pass1_marker_contract():
    code = 'def main():\n    print("MARKER")\n\nif __name__ == "__main__":\n    main()\n'
    ok, _ = scd.pass1_marker_contract(code, "MARKER")
    assert ok


def test_pass3_beautiful_with_docstring():
    code = '"""Module doc."""\ndef main():\n    """Main."""\n    print("hi")\n\nif __name__ == "__main__":\n    main()\n'
    ok, _ = scd.pass3_beautiful(code)
    assert ok


def test_pass3_beautiful_no_docstring():
    code = 'def main():\n    print("hi")\n\nif __name__ == "__main__":\n    main()\n'
    ok, _ = scd.pass3_beautiful(code)
    assert not ok
