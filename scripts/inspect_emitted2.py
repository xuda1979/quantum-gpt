#!/usr/bin/env python3
"""Compact per-sample stats of emitted answers — feeds extractor design."""

import json
import re
import sys

FENCE_RE = re.compile(r"```([a-zA-Z0-9_+-]*)\s*\n(.*?)```", re.DOTALL)
IMPORTS = (
    "import qiskit",
    "from qiskit",
    "import cirq",
    "from cirq",
    "import pennylane",
    "from pennylane",
    "import minqs",
    "from minqs",
    "mindspore_quantum",
    "import mindspore",
)


def fence_stats(resp):
    fences = FENCE_RE.findall(resp or "")
    langs = {}
    lengths = []
    for lang, body in fences:
        langs[lang or "(none)"] = langs.get(lang or "(none)", 0) + 1
        lengths.append(len(body.strip()))
    return langs, lengths


def main():
    for f in sys.argv[1:]:
        print(f"######## {f}")
        for i, line in enumerate(open(f, encoding="utf-8")):
            r = json.loads(line)
            resp = r.get("response") or ""
            langs, lengths = fence_stats(resp)
            imports = [k for k in IMPORTS if k in resp]
            print(
                f"s{i} id={r['example_id']} resp_len={len(resp)} "
                f"fences={sum(lengths)} langs={langs} max_fence={max(lengths) if lengths else 0} "
                f"imports={imports} "
                f"def={('def ' in resp)} print={('print(' in resp)} "
                f"exec_reason={r['exec'].get('reason')} extract_len={len(r.get('extracted_code') or '')}"
            )


if __name__ == "__main__":
    main()
