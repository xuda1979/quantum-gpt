#!/usr/bin/env python3
"""Prepare format-only DPO pairs from existing SFT rows.

Reformat each assistant turn that contains a code block into the canonical
form required by `docs/task-design-conventions.md`:

    <one-line natural-language summary>
    ```python
    #!/usr/bin/env python3
    import sys, json
    def main(): ...
    if __name__ == "__main__": main()
    ```

Synthesize negatives by perturbing the canonical form: (a) strip the code
block (prose-only), (b) drop `def main()`, (c) drop the
`if __name__ == "__main__"` guard. Each chosen/rejected pair differs in
exactly one of these axes, so the DPO signal is format-only and cannot
degrade reasoning.

Inputs
------
--input  : JSONL of ChatML rows (e.g. data/generated/glm52_soft_distill_sft_iter2/train_chatml.jsonl)
--output : JSONL of DPO pairs {"prompt": [...], "chosen": [...], "rejected": [...]}

The script is deterministic and side-effect-free; no tokenizer required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

CANONICAL_HEADER = "#!/usr/bin/env python3"
MAIN_GUARD = 'if __name__ == "__main__":\n    main()'

CODE_FENCE_RE = re.compile(r"```python\n(.*?)```", re.DOTALL)
DEF_MAIN_RE = re.compile(r"^\s*def\s+main\s*\(", re.MULTILINE)
MAIN_GUARD_RE = re.compile(r'^if\s+__name__\s*==\s*"__main__"\s*:', re.MULTILINE)


def has_canonical_python_block(text: str) -> bool:
    m = CODE_FENCE_RE.search(text)
    return bool(m)


def has_def_main(text: str) -> bool:
    m = CODE_FENCE_RE.search(text)
    if not m:
        return False
    return bool(DEF_MAIN_RE.search(m.group(1)))


def has_main_guard(text: str) -> bool:
    m = CODE_FENCE_RE.search(text)
    if not m:
        return False
    return bool(MAIN_GUARD_RE.search(m.group(1)))


def canonicalize_assistant(text: str) -> str | None:
    """Return a canonical-form version of the assistant text, or None if
    the text has no python code block at all (cannot canonicalize)."""
    m = CODE_FENCE_RE.search(text)
    if not m:
        return None
    code = m.group(1)
    # Ensure header
    if not code.lstrip().startswith("#!"):
        code = CANONICAL_HEADER + "\n" + code
    # Ensure def main exists — if not, wrap the code in a main()
    if not DEF_MAIN_RE.search(code):
        # Strip the header, wrap the rest, re-add header
        lines = code.splitlines()
        if lines and lines[0].startswith("#!"):
            header = lines[0]
            body = "\n".join(lines[1:])
        else:
            header = CANONICAL_HEADER
            body = code
        code = (
            header
            + "\n\ndef main():\n"
            + "\n".join("    " + ln if ln else ln for ln in body.splitlines())
            + "\n"
        )
    # Ensure main guard
    if not MAIN_GUARD_RE.search(code):
        code = code.rstrip() + "\n\n" + MAIN_GUARD + "\n"
    # Rebuild assistant text: keep prose before the fence, replace the code
    # block with the canonical one, drop anything after the fence.
    prose = text[: m.start()].rstrip()
    summary = prose.splitlines()[0] if prose else "Here is the solution."
    return f"{summary}\n\n```python\n{code}```\n"


def make_negative_prose_only(canonical: str) -> str:
    """Negative: strip the code block entirely, leaving only prose."""
    return re.sub(r"```python\n.*?```\n?", "", canonical, flags=re.DOTALL).strip() or "See above."


def make_negative_no_main(canonical: str) -> str:
    """Negative: keep the code but rename main() to _run()."""
    return canonical.replace("def main(", "def _run(").replace("main()", "_run()")


def make_negative_no_guard(canonical: str) -> str:
    """Negative: drop the `if __name__ == "__main__"` guard."""
    return MAIN_GUARD_RE.sub("if False:  # dropped guard", canonical)


def row_to_dpo_pairs(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert one ChatML row into up to 3 DPO pairs (one per negative type)."""
    messages = row.get("messages", [])
    # Find the last assistant message
    assistant_text = None
    for m in reversed(messages):
        if m.get("role") == "assistant":
            assistant_text = m.get("content", "")
            break
    if not assistant_text:
        return []
    canonical = canonicalize_assistant(assistant_text)
    if canonical is None or canonical == assistant_text:
        # Already canonical OR no code block — skip; we only want rows where
        # canonicalization actually changed something, so the DPO signal is
        # informative.
        if canonical is None:
            return []
        # If already canonical, we can still synthesize negatives.
        canonical = canonical
    # Prompt = everything except the last assistant message
    # Rebuild prompt as the conversation up to (not including) the last assistant turn
    last_assistant_idx = max(
        (i for i, m in enumerate(messages) if m.get("role") == "assistant"), default=-1
    )
    if last_assistant_idx < 0:
        return []
    prompt_messages = messages[:last_assistant_idx]
    if not prompt_messages:
        return []

    pairs = []
    chosen_messages = prompt_messages + [{"role": "assistant", "content": canonical}]
    for neg_fn, neg_name in [
        (make_negative_prose_only, "prose_only"),
        (make_negative_no_main, "no_main"),
        (make_negative_no_guard, "no_guard"),
    ]:
        neg_text = neg_fn(canonical)
        # Skip if the negative accidentally passes canonicalization
        if neg_name == "prose_only" and has_canonical_python_block(neg_text):
            continue
        if neg_name == "no_main" and has_def_main(neg_text):
            continue
        if neg_name == "no_guard" and has_main_guard(neg_text):
            continue
        rejected_messages = prompt_messages + [{"role": "assistant", "content": neg_text}]
        pairs.append(
            {
                "prompt": prompt_messages,
                "chosen": chosen_messages,
                "rejected": rejected_messages,
                "negative_type": neg_name,
                "pair_id": hashlib.sha256((canonical + neg_name).encode()).hexdigest()[:16],
            }
        )
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Input JSONL of ChatML rows")
    ap.add_argument("--output", required=True, help="Output JSONL of DPO pairs")
    ap.add_argument("--max-rows", type=int, default=0, help="Limit input rows (0 = all)")
    ap.add_argument("--check", action="store_true", help="Validate output after writing")
    args = ap.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    n_in = 0
    n_out = 0
    with inp.open() as fin, out.open("w") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            n_in += 1
            if args.max_rows and n_in > args.max_rows:
                break
            row = json.loads(line)
            for pair in row_to_dpo_pairs(row):
                fout.write(json.dumps(pair, ensure_ascii=False) + "\n")
                n_out += 1
    print(f"read {n_in} rows, wrote {n_out} DPO pairs to {out}", file=sys.stderr)

    if args.check:
        failures = []
        with out.open() as f:
            for i, line in enumerate(f):
                pair = json.loads(line)
                chosen = pair["chosen"][-1]["content"]
                rejected = pair["rejected"][-1]["content"]
                if not has_def_main(chosen):
                    failures.append(f"pair {i} chosen has no def main")
                if not has_main_guard(chosen):
                    failures.append(f"pair {i} chosen has no main guard")
                if not has_canonical_python_block(chosen):
                    failures.append(f"pair {i} chosen has no python block")
                nt = pair["negative_type"]
                if nt == "prose_only" and has_canonical_python_block(rejected):
                    failures.append(f"pair {i} prose_only negative still has code block")
                if nt == "no_main" and has_def_main(rejected):
                    failures.append(f"pair {i} no_main negative still has def main")
                if nt == "no_guard" and has_main_guard(rejected):
                    failures.append(f"pair {i} no_guard negative still has guard")
        if failures:
            print(f"CHECK FAILED: {len(failures)} issues", file=sys.stderr)
            for f in failures[:10]:
                print("  " + f, file=sys.stderr)
            sys.exit(1)
        print(f"CHECK PASSED: {n_out} pairs validated", file=sys.stderr)


if __name__ == "__main__":
    main()
