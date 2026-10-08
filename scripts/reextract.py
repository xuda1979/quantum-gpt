#!/usr/bin/env python3
"""reextract.py — re-run robust extraction + exec on existing emission JSONLs.

Usage: reextract.py <in.jsonl> <out.jsonl> [more in/out pairs...]
Re-extracts code from the stored responses (fixes indented-fence recovery
without regenerating anything) and re-executes.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_100_reeval import extract_code_robust, run_code  # noqa: E402


def main():
    pairs = sys.argv[1:]
    assert len(pairs) % 2 == 0 and pairs, "need in/out pairs"
    for i in range(0, len(pairs), 2):
        src, dst = pairs[i], pairs[i + 1]
        n = passed = 0
        with open(src, encoding="utf-8") as fh, open(dst, "w", encoding="utf-8") as out:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                code, method = extract_code_robust(r.get("response") or "")
                res = run_code(code)
                r["extracted_code"] = code
                r["extract_method"] = method
                r["exec"] = res
                out.write(json.dumps(r) + "\n")
                n += 1
                passed += 1 if res.get("passed") else 0
        print(f"{src} -> {dst}: n={n} pass={passed}")


if __name__ == "__main__":
    main()
