#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from transformers import AutoTokenizer


def main() -> int:
    model_path = sys.argv[1]
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    print(f"tokenizer_class={tokenizer.__class__.__name__}")
    rendered = tokenizer.apply_chat_template(
        [{"role": "user", "content": "hi"}],
        tokenize=False,
        add_generation_prompt=True,
    )
    print(f"rendered_prefix={rendered[:120]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
