#!/usr/bin/env python3
"""Per-file summary of emitted answers."""

import json
import re
import sys

FENCE_RE = re.compile(r"```([a-zA-Z0-9_+-]*)\s*\n(.*?)```", re.DOTALL)


def main():
    for f in sys.argv[1:]:
        n = 0
        n_fence = 0
        n_import = 0
        n_def = 0
        n_print = 0
        n_trunc = 0
        max_fence_len = 0
        total_resp_len = 0
        langs = {}
        for line in open(f, encoding="utf-8"):
            r = json.loads(line)
            resp = r.get("response") or ""
            n += 1
            total_resp_len += len(resp)
            if resp.rstrip().endswith((".", ":", ",", "-", "`")) or len(resp) > 1200:
                n_trunc += 1
            fences = FENCE_RE.findall(resp)
            if fences:
                n_fence += 1
                for lang, body in fences:
                    langs[lang or "(none)"] = langs.get(lang or "(none)", 0) + 1
                    max_fence_len = max(max_fence_len, len(body.strip()))
            if any(
                k in resp
                for k in (
                    "import qiskit",
                    "from qiskit",
                    "import cirq",
                    "from cirq",
                    "import pennylane",
                    "from pennylane",
                    "import mindspore",
                    "mindspore_quantum",
                )
            ):
                n_import += 1
            if "def " in resp:
                n_def += 1
            if "print(" in resp:
                n_print += 1
        print(
            f"{f}: n={n} fence_resp={n_fence} langs={langs} max_fence_len={max_fence_len} "
            f"import_resp={n_import} def_resp={n_def} print_resp={n_print} "
            f"likely_truncated={n_trunc} mean_resp_len={total_resp_len // max(1, n)}"
        )


if __name__ == "__main__":
    main()
